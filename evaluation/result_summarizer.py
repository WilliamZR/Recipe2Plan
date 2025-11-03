## Load actions for each agent and evalute
## then save the results

import os
import json
from evaluator import Evaluator
from collections import defaultdict

error_mapping = {
    'is not one of our goal': 'Action Mismatch',
    'there is no step': 'Action Mismatch',
    'is in the past': 'Action Concurrency',
    'they are all continuous actions': 'Action Concurrency',
    'is not completed': 'Action Dependency',
    'twice': 'Action Mismatch',
    'the execution time': 'Action Mismatch',
    'interrupt constraint': 'Execution Interruptibility',
    'time constraint': 'Time Restriction',
    'object': 'Resource Limitation',
    'temperature': 'Resource Limitation',
    'volume': 'Resource Limitation',
    'not all goals are completed': 'Incomplete Exit',
    'completed all goals': 'Success',
}

def get_error_type(msg):
    for key in error_mapping:
        if key in msg.lower():
            return error_mapping[key]
    return f'Unknown:{msg}'


def get_result(model, domain, agent, level = 'medium', heuristic_correction = False):
    
    log_path = os.path.join('logs', model, level, agent, domain)
    if not os.path.exists(log_path):
        return ''
    recipe_path = os.path.join('../data', f'{domain}.json')
    error_summary = defaultdict(int)
    recipe_data = json.load(open(recipe_path, 'r'))
    pass_rate, goal_ratio, progress_rate, complete_speed = [], [], [], []
    num_of_executable_actions_list = []
    ignore_time_constraint = True if level == 'easy' else False
    for recipe_pair in recipe_data:
        
        key = '_'.join([recipe['recipe'] for recipe in recipe_pair])
        ## load log
        target_path = os.path.join(log_path, f'{key}.json')
        try:
            log = json.load(open(target_path, 'r'))
        except:
            print('error:', target_path)
            continue
        
        max_retries = 10
        if isinstance(log, dict):
        ## Process Reasoning Models
            response = log['response']
            ## evaluate
            if '</think>' in response:
                response = response.split('</think>')[-1]
            evaluator = Evaluator(recipe_pair, domain, heuristic_correction = heuristic_correction, ignore_time_constraints = ignore_time_constraint)
            success, msg = evaluator.evaluate_execution(response)
        else:
        ## Process ReAct Models
            evaluator = Evaluator(recipe_pair, domain, heuristic_correction = False, ignore_time_constraints = ignore_time_constraint)
            for act in log:
                num_executable_actions = evaluator.environment.detect_executable_actions()
                num_executable_actions = len(num_executable_actions.split(','))
                num_of_executable_actions_list.append(num_executable_actions)
                success, msg = evaluator.evaluate_execution(act['response'])
                if not success:
                    max_retries -= 1
                    if max_retries < 0:
                        break
                

        current_goal_ratio = evaluator.evaluate_complete_goal_ratio()
        current_progress_rate = evaluator.evaluate_progress()
        current_complete_speed = evaluator.evaluate_complete_speed()

        if isinstance(log, dict):
            log['goal_ratio'] = current_goal_ratio
            log['progress_rate'] = current_progress_rate
            log['complete_speed'] = current_complete_speed
            log['complete'] = success
            log['msg'] = msg
        else:
            log[-1]['goal_ratio'] = current_goal_ratio
            log[-1]['progress_rate'] = current_progress_rate
            log[-1]['complete_speed'] = current_complete_speed
            log[-1]['complete'] = success
            log[-1]['msg'] = msg
        ## save log
        
        with open(target_path, 'w') as f:
            json.dump(log, f, indent=4)
        pass_rate.append(current_goal_ratio == 1)
        goal_ratio.append(current_goal_ratio)
        progress_rate.append(current_progress_rate)
        complete_speed.append(current_complete_speed)


        error = get_error_type(msg)
        error_summary[error] += 1

    ## multitasking score equals compute speed if progress rate is 1 else 0
    score = [complete_speed[i] if progress_rate[i] == 1 else 0 for i in range(len(progress_rate))]
    #score = [complete_speed[i] * progress_rate[i] for i in range(len(progress_rate))]

    result = {
        'pass_rate': sum(pass_rate) / len(pass_rate) * 100,
        'progress_rate': sum(progress_rate) / len(progress_rate) * 100,
        'complete_speed': sum(complete_speed) / len(complete_speed) * 100,
        'score': sum(score) / len(score) * 100,
    }
    return result, error_summary, complete_speed

def verbalize(result):
    output = []
    for key in result:
        output.append(f'{result[key]:.1f}')
    output = ' & '.join(output)
    return output

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--heuristic_correction', action='store_true')
    parser.add_argument('--level', type = str, default='medium')
    parser.add_argument('--verbose', action = 'store_true')
    args = parser.parse_args()
    print(args)
    models =[ 'gpt-5-mini','gpt-5', 'gemini-2.5-pro', 'gemini-2.5-flash','claude-opus-4-20250514','claude-sonnet-4-20250514', 'deepseek-reasoner']
    agents = [ 'plan_solve_oracle']
    domains = ['cooking']
 
 
    result_dict = {}
    for domain in domains:
        print('====================', domain, '====================')
        for model in models:
            print(model)
            for agent in agents:
                try:
                    result, error_summary, progress_rate = get_result(model, domain, agent, level = args.level, heuristic_correction = args.heuristic_correction)
                    if model == 'gpt-4o-2024-08-06':
                        if agent == 'react':
                            pr_react = progress_rate
                        if agent == 'react_oracle':
                            pr_react_oracle = progress_rate
                except Exception as e:
                    print(e)
                    continue

                result_dict[f'{model}_{agent}_{domain}'] = result
                try:
                    print(f'{agent}:', verbalize(result))
                    if args.verbose:
                        print(error_summary)
                except:
                    continue
    exit()

