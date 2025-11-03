# evaluator.py
"""Evaluate execution plans."""

import re
import json
from typing import List, Dict, Any, Tuple, Union
from execution_error import ExecutionError
from environment import Environment
from time_utils import format_time_stamp

class Evaluator:
    """Evaluator for parsing and evaluating action plans."""

    def __init__(self, goals: List[Dict[str, Any]], domain: str = 'cooking',
                 heuristic_correction: bool = False, ignore_time_constraints: bool = False):
        self.domain = domain
        self.environment = Environment(goals, domain=domain, ignore_time_constraints=ignore_time_constraints)
        self.end_step = 0
        self.heuristic_correction = heuristic_correction
        self.parsed_actions: List[List[Union[int, str, float]]] = []

    def _parse_time(self, time_str: str) -> float:
        """
        Parse a time string into seconds.

        Args:
            time_str: Time string in the format HH:MM:SS, MM:SS, or SS.

        Returns:
            Time in seconds.
        """
        parts = time_str.split(':')
        try:
            if len(parts) == 3:
                h, m, s = parts
                return 3600 * float(h) + 60 * float(m) + float(s)
            elif len(parts) == 2:
                # Assume MM:SS format
                m, s = parts
                return 60 * float(m) + float(s)
            elif len(parts) == 1:
                s = parts[0]
                # Set default unit based on the domain
                if self.domain == 'cooking':
                    # Default to minutes
                    return 60 * float(s)
                else:  # e.g., 'coffee'
                    # Default to seconds
                    return float(s)
        except ValueError:
            pass # If conversion fails, return default value
        return 0.0

    def parse_actions(self, actions_str: str) -> List[List[Union[int, str, float]]]:
        """
        Parse a list of actions from a string.

        Args:
            actions_str: String containing actions.

        Returns:
            Parsed list of actions.
        """
        # Clean up input
        actions_str = actions_str.replace('"', '').replace("'", '')
        actions_str = re.sub(r'(\d+) min', r'\1:00', actions_str)
        actions_str = re.sub(r'(\d+) sec', r'0:\1', actions_str) # Normalize to MM:SS format
        actions_str = re.sub(r'(\d+) hour', r'\1:00:00', actions_str)

        output = []
        # Match full format: Step(step_id, goal_name, time, time_stamp)
        pattern_full = re.compile(r'Step\((\d+), ([\w-]+), ((?:\d+:)?\d+:\d+), ((?:\d+:)?\d+:\d+)\)')
        matches_full = pattern_full.findall(actions_str)

        for match in matches_full:
            step_id = int(match[0])
            goal_name = match[1]
            time = self._parse_time(match[2])
            time_stamp = self._parse_time(match[3])
            output.append([step_id, goal_name, time, time_stamp])

        # If no full format matches, try simplified format: Step(step_id, goal_name, time_stamp)
        if not output:
            pattern_simple = re.compile(r'Step\((\d+), ([\w-]+), ((?:\d+:)?\d+:\d+)\)')
            matches_simple = pattern_simple.findall(actions_str)
            for match in matches_simple:
                step_id = int(match[0])
                goal_name = match[1]
                # Get default execution time from the environment
                try:
                    default_time = self.environment.goals[goal_name].current_state[step_id]['time']
                except (KeyError, IndexError):
                    default_time = 0 # Default to 0 if not found
                time_stamp = self._parse_time(match[2])
                output.append([step_id, goal_name, default_time, time_stamp])

        # Sort actions
        output.sort(key=lambda x: x[3]) # Sort by time_stamp

        # Heuristic correction
        if self.heuristic_correction and output:
            current_env_time = 0.0
            for i in range(len(output)):
                action = output[i]
                step_id, goal_name, action_time, action_time_stamp = action
                try:
                    is_parallel = self.environment.goals[goal_name].current_state[step_id]['parallel']
                except (KeyError, IndexError):
                    is_parallel = False

                # Correct timestamps if earlier than the environment time
                if action_time_stamp < current_env_time:
                    time_diff = current_env_time - action_time_stamp
                    # Adjust timestamps for current and subsequent actions
                    for j in range(i, len(output)):
                        output[j][3] += time_diff # Adjust time_stamp

                # Update environment time
                if is_parallel:
                    current_env_time = max(current_env_time, action_time_stamp)
                else:
                    current_env_time = max(current_env_time, action_time_stamp + action_time)

        self.parsed_actions = output
        return output

    def evaluate_execution(self, actions_str: str) -> Tuple[bool, str]:
        """
        Evaluate the execution of actions.

        Args:
            actions_str: Action string.

        Returns:
            (Success flag, Message).
        """
        try:
            actions = self.parse_actions(actions_str)
            self.parsed_actions = actions
        except Exception as e:
            return False, f'Error in parsing the plan: {e}'

        if not actions:
            return False, 'No actions to execute. Please provide a valid action.'

        for i, action_data in enumerate(actions):
            action_tuple = tuple(action_data) # Convert to tuple to match Environment expectations
            try:
                self.environment.execute_step(action_tuple)
            except ExecutionError as e:
                self.end_step = i
                if len(actions) > 1:
                    err_msg = f'Successfully executed {i} actions. Action {i} cannot be executed: {e}'
                else: # len(actions) == 1
                    err_msg = f'Action cannot be executed: {e}'
                return False, err_msg
            except Exception as e: # Catch unexpected errors other than ExecutionError
                 self.end_step = i
                 return False, f'Unexpected error during execution of action {i}: {e}'

        # Return success message based on the number and type of actions executed
        if len(actions) == 1:
            step_id, goal_name, _, _ = actions[0]
            try:
                is_parallel = self.environment.goals[goal_name].current_state[step_id]['parallel']
                if is_parallel:
                    return True, 'Autonomous action started successfully.'
                else:
                    return True, 'Continuous action executed successfully.'
            except (KeyError, IndexError):
                # Default to success if parallelism cannot be determined
                pass
        # len(actions) > 1 or failed to determine parallelism
        return True, 'Actions executed successfully.'

    def evaluate_progress(self) -> float:
        """Evaluate execution progress (maximum progress rate)."""
        try:
            return max(self.environment.progress) if self.environment.progress else 0.0
        except ValueError: # max() arg is an empty sequence
            return 0.0

    def evaluate_complete_speed(self) -> float:
        """
        Evaluate the speed of completing the plan.
        """
        plan_dict = json.load(open('../data/plan.json'))
        key = '_'.join([recipe['recipe'] for recipe in self.environment.recipes])
        if self.environment.ignore_time_constraints:
            ref_plan = plan_dict[key]['plan_wo_restriction']
        else:
            ref_plan = plan_dict[key]['plan_w_restriction']
        try:
            ref_plan = ref_plan[:len(self.environment.history)]
            finish_time = max([step[3] + step[2] for step in ref_plan])

            ref_time = sum([step[2] for step in ref_plan])
            
            ref_time = ref_time - finish_time
            ref_parallel_time = 0

            for action in ref_plan:
                if self.environment.goals[action[1]].current_state[action[0]]['parallel']:
                    ref_parallel_time += action[2]        
            ref_speed = ref_time / ref_parallel_time
        except:
            ref_speed = 0
        
        try:
            finish_time = max([step[3] + step[2] for step in self.environment.history])
        except:
            return 0
        total_time = sum([step[2] for step in self.environment.history])
        # Time taken to finish the last step
        try:
            finish_step = self.environment.history[-1]
        except IndexError:
            return 0
        
        saved_time = total_time - finish_time

        # Compute time for all parallel actions
        total_parallel_time = 0
        for recipe in self.environment.goals.values():
            for step in recipe.current_state:
                if step['parallel'] == 1 and step['completed']:
                    total_parallel_time += step['time']

        if saved_time < 0:
            saved_time = 0

        try:
            speed = saved_time / total_parallel_time / ref_speed
            speed = min(speed, 5 * saved_time / total_parallel_time)
        except Exception as e:
            speed = 0
        return speed

    def evaluate_complete_goal_ratio(self) -> float:
        """Evaluate the ratio of completed goals."""
        if not self.environment.goals:
            return 0.0
        completed_count = sum(1 for goal in self.environment.goals.values() if goal.is_complete())
        return completed_count / len(self.environment.goals)
