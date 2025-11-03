import json
from collections import defaultdict
import os
import re
import argparse
def parse_belief(belief_type, prediction):
    if '## Recipe' in prediction:
        prediction = prediction.split('## Recipe')[0]
    if belief_type == 'parallel':
        return parse_parallel(prediction)
    elif belief_type == 'physical_constraints':
        return parse_physical_constraints(prediction)
    elif belief_type == 'dependency':
        return parse_dependency(prediction)

def parse_parallel(prediction):
    ## input:1, 2, 4, 6, 8, 9, 11, 12]\nContinuous Actions: [0, 3, 5, 7, 10]
    ## output: [0, 3, 5, 7, 10]
    prediction = prediction.split('Continuous')[0]
    continuous_actions = re.findall(r'\d+', prediction)
    continuous_actions = [int(action) for action in continuous_actions]
    return continuous_actions

def parse_physical_constraints(prediction):
    ## input: Oven: []\nMicrowave: [1,2]\nStove: [3]
    ## output: [('Microwave', 1), ('Microwave', 2), ('Stove', 3)]
    physical_constraints = []
    for line in prediction.split('\n'):
        if line:
            try:
                object, steps = line.split(':')
            except:
                continue
            steps = re.findall(r'\d+', steps)
            object = object.replace('-', '').strip().lower()
            if 'gami' in object:
                object = 'origami'
            elif 'clever' in object:
                object = 'v60_clever_cup'
            elif 'v60' in object:
                object = 'v60'
            elif 'kettle' in object:
                object = 'kettle'
            for step in steps:
                physical_constraints.append((object.lower(), int(step)))
    return physical_constraints
def parse_dependency(prediction):
    ## Input: [0->1, 1->2, 2->3, 3->4, 4->5, 5->6, 6->7, 7->8, 8->9, 9->10, 10->11, 11->12]
    ## Output:
    dependency = []
    ## extract the dependency
    prediction = prediction.strip()
    prediction = prediction.replace('\n', '')
    prediction = prediction.replace(' ', '')
    dependency = re.findall(r'\d+->\d+', prediction)
    ## convert to tuple
    dependency = [tuple([int(step) for step in dep.split('->')]) for dep in dependency]
    ## 去重
    dependency = list(set(dependency))
    return dependency

def generate_recipe_description(recipe, args):
    if not args.oracle and not args.model_name:
        raise ValueError('Model name is required for dynamic setting to load the generated thoughts on the recipe.')
    title = f"{recipe['recipe']}"
    action_description = ['Step {0} ({1}): {2}'.format(step['step'], step['time'], step['text']) for step in recipe['steps']]
    action_description = '\n'.join(action_description)



    ### Add constraint description
    #### Add action id of actions that are interrruptiable
    interruptable_actions = [str(step['step']) for step in recipe['steps'] if step['interrupt']]
    #interrupt_description = f"You can stop step {', '.join(interruptable_actions)} during execution to perform other actions to speed up the process while other actions must be finished without any interruption.\n"
    interrupt_description = f"You can execute part of the action duration to pause steps {', '.join(interruptable_actions)} for more efficient multitasking. But other actions must be finished without interruption."

    #### Add the time constraint. Time constraint means that the next action must be performed within a certain time frame after the previous action.
    time_restrictions = []
    for step in recipe['steps']:
        if step['time_constraint']:
            for previous_index, time_frame in step['time_constraint'].items():
                if time_frame == 0 or time_frame == '0 min':
                    time_restrictions.append('Step {0} must be performed within 0 seconds after Step {1} is finished'.format(step['step'], previous_index))
                else:
                    time_restrictions.append('Step {0} must be performed within {1} after Step {2} is finished'.format(step['step'], time_frame, previous_index))
    time_description = '.'.join(time_restrictions)

    if args.oracle:
        ## parallel actions
        parallel_actions = [str(step['step']) for step in recipe['steps'] if step['parallel']]
        parallel_action_description = f"I can perform autonomous actions step {', '.join(parallel_actions)} in parallel with other actions to speed up the process."

        ## dependency relation
        dependency = []
        for step in recipe['steps']:
            if step['prequisites']:
                for prev in step['prequisites']:
                    dependency.append('{0}->{1}'.format(prev, step['step']))
        dependency = ', '.join(dependency)
        dependency_description = f"The action before the arrow must be completed before the action after the arrow can be started: {dependency}"

        ## Objects
        physical_objects = {}
        for step in recipe['steps']:
            if step['physical']:
                for key in step['physical']:
                    if key not in physical_objects:
                        physical_objects[key] = []
                    physical_objects[key].append(step['step'])
        ## step xx requires object yy
        physical_objects = [(key, ', '.join([str(step) for step in physical_objects[key]])) for key in physical_objects]
        physical_objects = ', '.join([f"Steps {steps} requires {object}" for object, steps in physical_objects])
        physical_objects = f"The following actions would occupy the corresponding physical objects. I can not perform the action if the object is occupied. The property such as volume and temperature of the object should also match the requirement of the recipe: {physical_objects}"

        #### Return the description
        #return '\n'.join([title, action_description,'\n- You can minimize the execution time based on the following properties:' ,parallel_action_description, interrupt_description,'\n- Do not violate any following constraints when executing this recipe:', time_description, dependency_description, physical_objects])
    else:
        belief_path = os.path.join(args.log_path, 'belief', args.model_name)
        belief = load_belief([recipe], belief_path, oracle = False)

        parallel_action_description = belief['parallel']
        dependency_description = belief['dependency']
        physical_objects = belief['physical_constraints']
    if time_description and args.level == 'medium':
        return '\n'.join([title, action_description,'\n- You can minimize the execution time based on the following properties:', interrupt_description,'\n- Do not violate any following constraints when executing this recipe:', time_description, '\nThoughts on the recipe:', parallel_action_description, dependency_description, physical_objects])
    else:
        return '\n'.join([title, action_description,'\n- You can minimize the execution time based on the following properties:', interrupt_description, '\nThoughts on the recipe:', parallel_action_description, dependency_description, physical_objects]) 
general_description = '''You are a multitask planner. You will plan an action sequence to finish some recipes as quickly as possible without violating any constraints.

## Recipes
Each recipe is a sequence of actions designed to achieve a specific goal. Each action is a textual description companied with the duration to fininsh the action. Each recipe has autonomous actions such as boiling water that lets agent be idle during execution. They can be executed in parallel with other actions to speed up the process  Continuous actions such as pouring water occupies the agent and only one continuous action can be executing at the same time across all recipes.
'''


oracle_description = '''## Belief
The following belief is the property of the recipe. Use it to guide the planning process. Do not revise the belief during interaction with the environment.
'''

non_oracle_description = '''## Belief
The following belief is generated based on the recipe. The belief is used to guide the planning process. Note that belief may not be accurate, you can revise your belief during interaction with the environment.
'''
belief_template = '''
Dependency of Actions
The dependency of actions is as follows. The action before the arrow must be completed before the action after the arrow can be started.
{dependency}

Autonomous Actions
The following actions can be executed in parallel.
{autonomous}
Other actions are autonomous actions and can not be executed in parallel.

Physical Objects
The follow actions would require the following physical objects. And you only have one of each mentioned object at your disposal. The property such as volume and temperature of the object should also match the requirement of the recipe.
{physical_objects}
'''

react_example = '''
Test React Example
'''


def load_plan(recipes, plan_path):
    key = '_'.join([recipe['recipe'] for recipe in recipes])
    plan_path = os.path.join(plan_path, f'{key}.json')
    plan = json.load(open(plan_path, 'r'))
    return plan['plan']

def load_belief(recipes, belief_path, oracle = False):
    belief = defaultdict(list)

    for recipe in recipes:
        recipe_name = recipe['recipe']
        generated_response = json.load(open(os.path.join(belief_path, f'{recipe_name}.json'), 'r'))

        for key in generated_response:
            #print(key)
            response = parse_belief(key, generated_response[key])
            #print(response)
            belief[key].append(verbalize_belief(response, key))
    for key in belief:
        belief[key] = '\n'.join(belief[key])

    #belief = belief_template.format(dependency = belief['dependency'], autonomous = belief['parallel'], physical_objects = belief['physical_constraints'])

    #if oracle:
    #    belief = f"{oracle_description}{belief}"
    #else:
    #    belief = f"{non_oracle_description}{belief}"

    return belief


def verbalize_belief(belief, key):
    if key == 'parallel':
        belief = ', '.join([str(step) for step in belief])
        belief = f'I can perform autonomous actions step {belief} in parallel with other actions to speed up the process.'
        return f"{belief}"
    elif key == 'physical_constraints':
        ## write as object: id, id, id
        output_dict = defaultdict(list)
        for object, step in belief:
            output_dict[object].append(step)
        physical_objects = [(key, ', '.join([str(step) for step in output_dict[key]]) ) for key in output_dict]
        physical_objects = ', '.join([f"Steps {steps} requires {object}" for object, steps in physical_objects])
        belief = f"The following actions would occupy the corresponding physical objects. I can not perform the action if the object is occupied. The property such as volume and temperature of the object should also match the requirement of the recipe: {physical_objects}"

        return f"{belief}"
    elif key == 'dependency':
        ## write as 0->1, 1->2, 2->3, 3->4, 4->5, 5->6, 6->7, 7->8, 8->9, 9->10, 10->11, 11->12
        belief = ', '.join([f"{prev}->{next}" for prev, next in belief])
        belief = f"The action before the arrow must be completed before the action after the arrow can be started: {belief}"
        return f" {belief}"
    else:
        raise ValueError('Invalid key')



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--log_path', type = str, default = '/newdisk/wuzr/planning_actions_with_time/evaluation/logs')
    parser.add_argument('--domain', type=str, default='coffee')
    parser.add_argument('--model_name', type=str, required=True)
    parser.add_argument('--recipe_path', type=str, default='/newdisk/wuzr/planning_actions_with_time/recipe2plan/recipes/small')
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('--dry_run', action = 'store_true')
    parser.add_argument('--force_generate', action = 'store_true')
    parser.add_argument('--oracle', action = 'store_true')
    parser.add_argument('--level', type = str, default= 'easy')
    args = parser.parse_args()
    path = '/newdisk/wuzr/planning_actions_with_time/recipe2plan/recipes/small/coffee.json'
    data = json.load(open(path, 'r'))
    
    print(generate_recipe_description(data[0], args))

    ## test load belief
    #test_input = data[:2]
    #test_model = 'gpt-3.5-turbo-0125'
    #test_belief_path = f'/newdisk/wuzr/planning_actions_with_time/recipe2plan/belief/{test_model}'

    #belief = load_belief(test_model, test_input, test_belief_path)
    #print(belief)