import openai
import os
import json
from collections import defaultdict
import tiktoken
from model import Model
import re
from util import generate_recipe_description, general_description, load_belief
import argparse
from evaluator import Evaluator
from prompt_examples import get_prompt_example 


class ReActAgent():
    def __init__(self, model, recipes, args) -> None:
        self.model = model
        self.recipes = recipes
        self.memory = ''
        self.prompt_generator = ReActPromptGenerator(args, recipes=recipes)
        self.history = []
        self.successful_actions = ''
        self.args = args
        self.error_source = ''
        self.max_revise = args.max_revise
        self.ignore_time_constraints = True if args.level == 'easy' else False

        if not args.max_turns:
            self.max_turns = sum([len(recipe['steps']) for recipe in recipes]) + self.max_revise
        else:
            self.max_turns = args.max_turns
        self.evaluator = Evaluator(self.recipes, domain=args.domain, heuristic_correction = False, ignore_time_constraints = self.ignore_time_constraints)

    def update_success_actions(self, action):
        self.successful_actions += action + '\n'

    def load_history(self, path):
        key = '_'.join([recipe['recipe'] for recipe in self.recipes])
        path = os.path.join(path, f'{key}.json')
        if os.path.exists(path):
            self.history = json.load(open(path, 'r'))
            self.memory = self.history[-1]['memory']
            self.successful_actions = self.history[-1]['successful_actions']

    def save_history(self, path):
        key = '_'.join([recipe['recipe'] for recipe in self.recipes])
        path = os.path.join(path, f'{key}.json')
        with open(path, 'w') as f:
            json.dump(self.history, f, indent=4)

    def stuck_detector(self):
        ## if the msg from last 3 steps are the same, quit
        if len(self.history) < 3:
            return False
        last_three_steps = [h['msg'] for h in self.history[-3:]]
        ## check if they all failed 
        if all([not h['success'] for h in self.history[-3:]]) and len(set(last_three_steps)) == 1:
            return True
        return False
        
        


    def run(self):
        success, executed = True, True
        msg = ''
        if not self.args.force_generate:
            self.load_history(self.args.output_path)
            try:
                _, msg = self.evaluator.evaluate_execution(self.history[-1]['successful_actions'])
                print(msg)
                success = self.history[-1]['success']
                msg = self.history[-1]['msg']
                if self.args.verbose:
                    print('Loaded from checkpoint')
                    print(msg)
                    print(self.evaluator.environment.observation())
                self.max_turns = self.max_turns - len(self.history)
                self.max_revise = self.max_revise - len([1 for h in self.history if not h['success']])
                last_response = self.history[-1]['response']
                if 'action: finish' in last_response.lower() or '*/' in last_response:
                    print('The agent has chosen to finish the task')
                    return
            except:
                print('No history found')
        if self.args.dry_run:
            print(self.prompt_generator.generate_prompt('Memory\n',self.evaluator.environment.observation()))
            exit()

        while self.max_turns > 0 and self.max_revise > 0:
            observation = self.evaluator.environment.observation()
            if not executed or 'time constraint' in msg.lower() or self.stuck_detector():
                break
            if success:
                if args.hint:
                    prompt = self.prompt_generator.generate_prompt(self.memory, observation = 'Observation: ' + msg + observation + '\nHint: ' + self.evaluator.environment.detect_executable_actions())
                else:
                    prompt = self.prompt_generator.generate_prompt(self.memory, observation = 'Observation: ' + msg + observation)
            else:
                prompt = self.prompt_generator.generate_prompt(self.memory, observation = 'Observation:' + msg + observation)
                self.max_revise -= 1
            executed, response = self.model.generate('You are a helpful assistant', prompt)
            
            ## detect numbers of Action:, if more than 1, only take the first one
            response = 'Action: '.join(response.split('Action: ')[:2])
            if 'Thought:' in response:
                response = 'Thought:' + response.split('Thought:')[1]
            success, msg = self.evaluator.evaluate_execution(response)
            progress_rate = self.evaluator.evaluate_progress()
            complete_speed = self.evaluator.evaluate_complete_speed()
            if success:
                self.update_success_actions(response)
            self.memory += '\nObservation:' + msg + observation
            self.memory += '\nThought:' + response
            self.history.append({'prompt': prompt, 
                                 'memory': self.memory,
                                 'successful_actions':self.successful_actions, 
                                 'success': success,
                                 'response': response,
                                 'msg': msg,
                                 'progress_rate': progress_rate,
                                 'complete_speed': complete_speed})

            self.save_history(self.args.output_path)
            if self.args.verbose:
                print('====Observation====')
                print(observation)
                print('====Response====')
                print(response)
                print('====Feedback====')
                print(msg)

            if 'action: finish' in response.lower() or '*/' in response:
                print('The agent has chosen to finish the task')
                break
            self.max_turns -= 1
    




class ReActPromptGenerator():
    def __init__(self, args, recipes):
        self.recipes = recipes
        self.recipe_description = self.get_all_recipe_description(recipes)
        self.args = args
        self.examples = get_prompt_example('react', args.level, args.oracle)
        self.task_description = '''## Task Description
You are required to analyze the current status of the environment and decide the next action to take so that you can finish the recipes in the shortest time without violating constraints. Give your thoughts on the given status, action history and observation. If you find your initial thoughts of the recipes does not align with the current status, you can revise your initial thoughts. Your analysis should be within 100 words starting with 'Thought:'. Then you should choose your next action. If you think you have already completed all the recipes, please output 'Action: Finish'. Write your action as 'Action: Step(step_num, recipe_name, time, timestamp)' - Perform the given step for the given time at timestamp. Your time and timestamp should be written as HH:MM:SS. You can only perform one action each time. Do not repeat actions that are already in progress. If you choose to wait for current actions to finish, please state the time you will wait for. Then write your next action as 'I will wait and perform the next action at HH:MM:SS. Action: Step(step_num, recipe_name, time, timestamp).
'''

    def generate_prompt(self, memory, observation):
        prompt = f'''{general_description}
{self.task_description}
/*
{self.examples}\
*/

Please follow the example shown above to complete the task. 

/*
{self.recipe_description}

## Action Sequence
{memory}
{observation}
Thought:'''
        return prompt

    @staticmethod
    def get_all_recipe_description(recipes):
        recipe_descriptions = [f'## Recipe {i + 1}:' + generate_recipe_description(recipe,args) for i, recipe in enumerate(recipes)]
        return '\n\n'.join(recipe_descriptions)
        

    

if __name__ == '__main__':
    import json
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--log_path', type = str, default = 'logs')
    parser.add_argument('--domain', type=str, default='cooking')
    parser.add_argument('--model_name', type=str, required=True)
    parser.add_argument('--recipe_path', type=str, default='../data')
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('--dry_run', action = 'store_true')
    parser.add_argument('--force_generate', action = 'store_true')
    parser.add_argument('--belief_path', type = str, default = 'logs/belief')
    parser.add_argument('--oracle', action = 'store_true')
    parser.add_argument('--max_turns', type=int)
    parser.add_argument('--max_revise', type=int, default=10)
    parser.add_argument('--level', type=str, default='easy')
    parser.add_argument('--small', action='store_true')
    parser.add_argument('--hint', action='store_true')
    args = parser.parse_args()
    if not args.dry_run:
        model = Model({'engine': args.model_name, 'stop': ['\nObservation']})

    if args.model_name.endswith('/'):
        args.model_name = args.model_name.split('/')[-2]
    else:
        args.model_name = args.model_name.split('/')[-1]    
    

    path = os.path.join(args.log_path, args.model_name)
    if not os.path.exists(path):
        os.makedirs(path)
    if args.oracle:
        if args.hint:
            args.output_path = os.path.join(path,args.level, 'react_oracle_hint', args.domain)
        else:
            args.output_path = os.path.join(path,args.level, 'react_oracle', args.domain)
    else:
        assert not args.hint
        args.output_path = os.path.join(path,args.level, 'react', args.domain)

    if not os.path.exists(args.output_path):
        os.makedirs(args.output_path)

    args.recipe_path = os.path.join(args.recipe_path, f'{args.domain}.json')
    recipes = json.load(open(args.recipe_path, 'r'))
 
    if args.dry_run:
        prompt_generator = ReActPromptGenerator(args, recipes=recipes[0])
        print(prompt_generator.generate_prompt('Memory\n', 'Observation\n'))
        exit()
    
    if args.small:
        recipes = recipes[:3]

    for recipe in recipes:
        react_agent = ReActAgent(model, recipe, args)
        react_agent.run()

    print(args.recipe_path)