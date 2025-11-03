# environment.py
"""Simulated execution environment."""

from typing import List, Dict, Any, Tuple, Union
from collections import defaultdict
from execution_error import ExecutionError
from physical_objects import Physical_Objects
from goal import Goal
from time_utils import format_time_stamp, format_execution_time

Action = Tuple[int, str, float, float] # (step_id, target_goal, time, global_time)

class Environment:
    """Execution environment managing goals, time, physical objects, and history."""

    def __init__(self, goals: List[Dict[str, Any]], domain: str = 'cooking', ignore_time_constraints: bool = False):
        self.recipes = goals
        self.goals: Dict[str, Goal] = self._create_goals(goals, ignore_time_constraints)
        self.ignore_time_constraints = ignore_time_constraints
        self.occupied_time: List[List[float]] = [] # [[start, end], ...]
        self.occupied_id: List[str] = []
        self.domain = domain
        self.history: List[Action] = []
        self.time_stamp: float = 0.0
        self.progress: List[float] = []
        self.tool_dict: Physical_Objects = self._initialize_physical_objects()

    def get_progress_rate(self) -> float:
        """Get overall progress rate."""
        completed, total = 0, 0
        for goal in self.goals.values():
            completed += goal.progress_record()
            total += len(goal.current_state)
        return completed / total if total > 0 else 0.0

    def _initialize_physical_objects(self) -> Physical_Objects:
        """Initialize physical objects."""
        return Physical_Objects(self.domain)

    def _create_goals(self, goals_data: List[Dict[str, Any]], ignore_time_constraints: bool) -> Dict[str, Goal]:
        """Create Goal objects from data."""
        goal_dict = {}
        for goal_recipe in goals_data:
            goal_name = goal_recipe['recipe']
            goal_dict[goal_name] = Goal(goal_name, goal_recipe['steps'], ignore_time_constraints)
        return goal_dict

    def check_goals_complete(self) -> bool:
        """Check whether all goals are complete."""
        return all(goal.is_complete() for goal in self.goals.values())

    def _time_interval_overlap(self, interval1: List[float], interval2: List[float]) -> bool:
        """Check whether two time intervals overlap."""
        start1, end1 = interval1
        start2, end2 = interval2
        if start1 == end1:
            return start2 < start1 < end2
        if start2 == end2:
            return start1 < start2 < end1
        return max(start1, start2) < min(end1, end2)

    def execute_step(self, action: Action):
        """
        Execute an action.

        Args:
            action: A tuple containing (step_id, target_goal, time, global_time).

        Returns:
            The result of execution.
        """
        step_id, target_goal_name, time, global_time = action
        # 1. Check if the goal exists
        if target_goal_name not in self.goals:
            available_goals = ", ".join(self.goals.keys())
            raise ExecutionError(
                f'Recipe {target_goal_name} is not one of our goals. '
                f'You should choose actions from the given recipes: {available_goals}'
            )

        target_goal = self.goals[target_goal_name]

        # 2. Check if the step exists
        if step_id < 0 or step_id >= len(target_goal.current_state):
            raise ExecutionError(
                f'The step {step_id} does not exist in {target_goal_name}. '
                f'You should choose a valid step from 0 to {len(target_goal.current_state) - 1}.'
            )

        # 3. Handle default time value
        if time == -1:
            time = target_goal.current_state[step_id]['time']

        # 4. Check all constraints
        self._check_constraint(step_id, target_goal_name, time, global_time)

        # 5. If constraints pass, execute the action and update goal state
        executed = target_goal.act(step_id, time, global_time)

        # 6. Update physical object state and environment time
        step_parallel = target_goal.recipe[step_id]['parallel']
        if not step_parallel: # continuous actions
            self.occupied_time.append([global_time, global_time + time])
            self.occupied_id.append(f'step {step_id} of {target_goal_name}')
            self.time_stamp = global_time + time 


        try:
            self.tool_dict.update_status(time, global_time, target_goal.recipe[step_id]['physical'])
        except Exception as e:
            raise ExecutionError(
                f'Error in updating the physical objects for step {step_id} in {target_goal_name}: {e}'
            ) from e

        # 7. Record history and progress
        self.history.append(action)
        self.progress.append(self.get_progress_rate())
        
        # Update the timestamp to the action end time so subsequent actions can be ordered correctly
        #self.time_stamp = max(self.time_stamp, global_time + time)

        return executed

    def _check_constraint(self, step_id: int, target_goal_name: str, time: float, global_time: float):
        """
        Check constraints for executing an action.

        Args:
            step_id: Step ID.
            target_goal_name: Goal name.
            time: Execution time.
            global_time: Global timestamp.
        """
        target_goal = self.goals[target_goal_name]

        # 1. Check timestamp
        if global_time < self.time_stamp:
            raise ExecutionError(
                f'The current timestamp is {format_time_stamp(self.time_stamp)}. '
                f'You cannot perform step {step_id} in {target_goal_name} at {format_time_stamp(global_time)} '
                f'since it is in the past. Choose a valid timestamp that is not earlier than the current timestamp.'
            )

        elif global_time > self.time_stamp:
             self.time_stamp = global_time

        # 2. Handle default time value (already handled in execute_step; redundant here)
        if time == -1:
            time = target_goal.current_state[step_id]['time']

        # 3. Check parallelism constraints
        step_parallel = target_goal.recipe[step_id]['parallel']
        if not step_parallel:
            for i, interval in enumerate(self.occupied_time):
                if self._time_interval_overlap(interval, [global_time, global_time + time]):
                    raise ExecutionError(
                        f'You cannot perform step {step_id} in {target_goal_name} at {format_time_stamp(global_time)} '
                        f'simultaneously with {self.occupied_id[i]} since they are all continuous actions.'
                    )

        # 4. Check physical object constraints
        try:
            self.tool_dict.check_constraint(
                time, global_time, target_goal.recipe[step_id]['physical'], recipe_name=target_goal_name
            )
        except Exception as e:
            raise ExecutionError(
                f'You cannot perform step {step_id} in {target_goal_name} at {format_time_stamp(global_time)}: {e}'
            ) from e

        # 5. Check internal goal constraints (interruptions, dependencies, time constraints, action duration)
        target_goal.check_constraint(step_id, time, global_time, self.tool_dict)

    def detect_active_autonomous_actions(self) -> List[Dict[str, float]]:
        """
        Detect all started but not finished autonomous actions.

        Returns:
            A list of active actions; each element is a dict {action_description: finish_time}.
        """
        active_actions = []
        for goal_name, goal in self.goals.items():
            for i, step in enumerate(goal.current_state):
                if step['finished_time_stamp'] and step['finished_time_stamp'] > self.time_stamp:
                    action_desc = f'step {i} of {goal_name}'
                    active_actions.append({action_desc: step['finished_time_stamp']})
        return active_actions

    def detect_executable_actions(self) -> str:
        """
        Detect executable actions.

        Returns:
            A descriptive string of executable actions.
        """
        current_time_stamp = self.time_stamp
        possible_time_stamps = {current_time_stamp} # Use a set to avoid duplicates
        for goal in self.goals.values():
            for step in goal.current_state:
                if step['finished_time_stamp'] and step['finished_time_stamp'] > self.time_stamp:
                    possible_time_stamps.add(step['finished_time_stamp'])

        # Group executable actions by timestamp
        executable_action_dict = defaultdict(list)
        for goal_name, goal in self.goals.items():
            for i, step in enumerate(goal.current_state):
                if step['time_left'] == 0:
                    continue
                for time_stamp in sorted(possible_time_stamps):
                    # Temporarily set timestamp for checking
                    original_time_stamp = self.time_stamp
                    self.time_stamp = time_stamp
                    try:
                        self._check_constraint(i, goal_name, step['time_left'], time_stamp)
                        executable_action_dict[time_stamp].append((goal_name, i))
                        break # found a feasible timestamp
                    except ExecutionError as e:
                        # If it's a time constraint error, consider the action relevant at this timestamp
                        if 'time constraint' in str(e).lower():
                            executable_action_dict[time_stamp].append((goal_name, i))
                            break
                    except Exception:
                        # Other errors (e.g., physical object occupied) -> try next timestamp
                        pass
                    finally:
                        # Restore original timestamp
                        self.time_stamp = original_time_stamp

        # Format the results
        executable_action_strings = []
        for time_stamp in sorted(executable_action_dict.keys()):
            actions = executable_action_dict[time_stamp]
            if actions:
                action_str = f'The following actions are ready to be executed after {format_time_stamp(time_stamp)}: '
                action_str += ', '.join([f'step {action_id} of {goal_name}' for goal_name, action_id in actions])
                executable_action_strings.append(action_str)

        if not executable_action_strings:
            result = 'There are no actions that can be executed.'
        else:
            result = '; '.join(executable_action_strings) + '.'
            if not self.ignore_time_constraints:
                result += ' Please make sure your plan is consistent with the time restrictions.'

        return result

    def observation(self) -> str:
        """
        Generate the current environment observation.

        Returns:
            Observation string.
        """
        observation_parts = [f'The current timestamp is {format_time_stamp(self.time_stamp)}.']

        # Add physical object status
        observation_parts.append(f'Status of physical objects: {self.tool_dict.get_status(self.time_stamp)}')

        # Add active autonomous actions
        active_actions = self.detect_active_autonomous_actions()
        if active_actions:
            active_action_strs = [
                f'{action_desc} (will finish at {format_time_stamp(finish_time)})'
                for action_dict in active_actions
                for action_desc, finish_time in action_dict.items()
            ]
            observation_parts.append(
                f'You are currently executing the following autonomous actions: {", ".join(active_action_strs)}'
            )

        return ' '.join(observation_parts)
