import os
import json
import argparse
from multiprocessing import Pool
from tqdm import tqdm

from model import Model
from util import generate_recipe_description, general_description
from evaluator import Evaluator
from prompt_examples import get_prompt_example


class PlanSolveAgent:
    def __init__(self, model, recipes, args):
        self.model = model
        self.recipes = recipes
        self.args = args
        self.prompt_generator = PlanSolvePromptGenerator(self.recipes, args.domain, self.args)
        self.history = {}
        self.evaluator = Evaluator(self.recipes, domain=args.domain, heuristic_correction=True)

    def save_history(self, path):
        key = '_'.join([recipe['recipe'] for recipe in self.recipes])
        file_path = os.path.join(path, f'{key}.json')
        with open(file_path, 'w') as f:
            json.dump(self.history, f, indent=4)

    def load_history(self, path):
        key = '_'.join([recipe['recipe'] for recipe in self.recipes])
        file_path = os.path.join(path, f'{key}.json')
        if os.path.exists(file_path) and not self.args.force_generate:
            print(f'{key} already exists in log, skipping...')
            self.history = json.load(open(file_path, 'r'))
            return self.history['response']
        return None

    def generate_response(self):
        prompt = self.prompt_generator.generate_prompt()
        success, response = self.model.generate('You are a helpful assistant.', prompt)
        if not success:
            print('Failed to generate a valid response')
            return None
        self.history = {'prompt': prompt, 'response': response}
        return response

    def evaluate_response(self, response):
        complete, msg = self.evaluator.evaluate_execution(response)
        self.history.update({
            'progress_rate': self.evaluator.evaluate_progress(),
            'complete_speed': self.evaluator.evaluate_complete_speed(),
            'complete': complete,
            'msg': msg,
            'actions': self.evaluator.parsed_actions,
            'goal_ratio': self.evaluator.evaluate_complete_goal_ratio()
        })

    def run(self):
        response = self.load_history(self.args.output_path)
        if not response:
            response = self.generate_response()
            if not response:
                return
            self.save_history(self.args.output_path)

        self.evaluate_response(response)
        self.save_history(self.args.output_path)

        if self.args.verbose:
            self.print_verbose_logs(response)

    def print_verbose_logs(self, response):
        key = '_'.join([recipe['recipe'] for recipe in self.recipes])
        print(response)
        print(f'Parsed response: {self.history["actions"]}')
        print(f'{key} evaluation: {self.history["complete"]}, {self.history["msg"]}')
        print(f'Goal ratio: {self.history["goal_ratio"]}')
        print(f'Progress rate: {self.history["progress_rate"]}')
        print(f'Complete speed: {self.history["complete_speed"]}')


class PlanSolvePromptGenerator:
    def __init__(self, recipes, domain, args):
        self.recipes = recipes
        self.args = args
        self.recipe_descriptions = self.generate_recipe_descriptions()
        self.task_description = self.generate_task_description(args.oracle)
        self.example = get_prompt_example('plan_solve', args.level, args.oracle)

    def generate_recipe_descriptions(self):
        return '\n\n'.join(
            [f'## Recipe {i + 1}:' + generate_recipe_description(recipe, self.args) for i, recipe in enumerate(self.recipes)]
        )

    def generate_task_description(self, oracle):
        base_description = '''## Task
Your task is to complete all of the recipes as quickly as possible while following the recipe. The key to success is to follow the recipe and constraints, then complete the steps in the correct order while minimizing the execution time by executing the autonomous actions concurrently.'''
        if oracle:
            return base_description + ''' First, let's analyze the recipe and create a concise plan on how to perform actions simultaneously to reduce the total execution time. Then write your action sequence following the plan. Your action should be a list of 'Step(step_num, recipe_name, time, timestamp)' which indicates performing the given step for the given time at timestamp. Your time and timestamp should be written as HH:MM:SS.'''
        return base_description + ''' First, let's analyze the recipe and give your thoughts on the recipe, then write a concise plan on how to perform actions simultaneously to reduce the total execution time. Then write your action sequence following the plan. Your action should be a list of 'Step(step_num, recipe_name, time, timestamp)' which indicates performing the given step for the given time at timestamp. Your time and timestamp should be written as HH:MM:SS.'''

    def generate_prompt(self):
        return f'''{general_description}
{self.task_description}
/*
{self.example}
*/

Please follow the example shown above to generate the action sequence for the following recipes.

/*
{self.recipe_descriptions}

## Plan'''


def process_recipe(recipe):
    agent = PlanSolveAgent(model, recipe, args)
    agent.run()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--log_path', type=str, default='logs')
    parser.add_argument('--domain', type=str, default='cooking')
    parser.add_argument('--model_name', type=str, required=True)
    parser.add_argument('--recipe_path', type=str, default='../data')
    parser.add_argument('--belief_path', type=str, default='logs/belief')
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('--dry_run', action='store_true')
    parser.add_argument('--force_generate', action='store_true')
    parser.add_argument('--oracle', action='store_true')
    parser.add_argument('--level', type=str, default='medium')
    parser.add_argument('--small', action='store_true')

    global args
    args = parser.parse_args()

    if not args.dry_run:
        global model
        model = Model({'engine': args.model_name})

    args.model_name = args.model_name.rstrip('/').split('/')[-1]
    args.output_path = os.path.join(
        args.log_path, args.model_name, args.level,
        'plan_solve_oracle' if args.oracle else 'plan_solve', args.domain
    )
    os.makedirs(args.output_path, exist_ok=True)

    args.recipe_path = os.path.join(args.recipe_path, f'{args.domain}.json')
    recipes = json.load(open(args.recipe_path, 'r'))

    if args.dry_run:
        prompt_generator = PlanSolvePromptGenerator(recipes[0], args.domain, args)
        print(prompt_generator.generate_prompt())
        return

    with Pool(processes=16) as pool:
        list(tqdm(pool.imap_unordered(process_recipe, recipes), total=len(recipes)))


if __name__ == '__main__':
    main()
