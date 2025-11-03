# goal.py
"""Class representing a single goal (recipe) and its steps."""

import re
from typing import List, Dict, Any, Union
from execution_error import ExecutionError
from time_utils import format_execution_time, format_time_stamp


KEY_TIME = 'time'
KEY_TIME_LEFT = 'time_left'
KEY_FINISHED_TIME_STAMP = 'finished_time_stamp'
KEY_INTERRUPT = 'interrupt'
KEY_PARALLEL = 'parallel'
KEY_COMPLETED = 'completed'
KEY_PREQUISITES = 'prequisites' 
KEY_PHYSICAL = 'physical'
KEY_TIME_CONSTRAINT = 'time_constraint'
KEY_UPDATE = 'update'
KEY_REQUIRE = 'require'

class Goal:
    """Represents a goal or recipe."""

    def __init__(self, name: str, actions: List[Dict[str, Any]], ignore_time_constraints: bool = False):
        self.name = name
        self.recipe = actions
        self.current_state: List[Dict[str, Any]] = []
        self.ignore_time_constraints = ignore_time_constraints

        for i, step in enumerate(actions):
            # Normalize time constraints
            if isinstance(step.get(KEY_TIME_CONSTRAINT, ''), dict) and step[KEY_TIME_CONSTRAINT]:
                for key in step[KEY_TIME_CONSTRAINT]:
                    step[KEY_TIME_CONSTRAINT][key] = self._time_normalize(step[KEY_TIME_CONSTRAINT][key])

            self.current_state.append({
                'recipe': name,
                'index': i,
                KEY_TIME: self._time_normalize(step[KEY_TIME]),
                KEY_TIME_LEFT: self._time_normalize(step[KEY_TIME]),
                KEY_FINISHED_TIME_STAMP: None,
                KEY_INTERRUPT: step[KEY_INTERRUPT],
                KEY_PARALLEL: step[KEY_PARALLEL],
                KEY_COMPLETED: False,
                KEY_PREQUISITES: step[KEY_PREQUISITES],
                KEY_PHYSICAL: step[KEY_PHYSICAL],
                KEY_TIME_CONSTRAINT: step[KEY_TIME_CONSTRAINT]
            })

    def _time_normalize(self, time_input: Union[str, int, float]) -> int:
        """Normalize time input to seconds (integer)."""
        if isinstance(time_input, (int, float)):
            return int(time_input)
        if 'min' in time_input:
            time_value = int(re.search(r'\d+', time_input).group())
            return time_value * 60
        elif 'hour' in time_input:
            time_value = int(re.search(r'\d+', time_input).group())
            return time_value * 3600
        elif 'sec' in time_input:
            time_value = int(re.search(r'\d+', time_input).group())
            return time_value
        else:
            return 0

    def act(self, step_id: int, time: float, time_stamp: float) -> bool:
        """
        Execute a step.

        Args:
            step_id: Step ID.
            time: Execution time (seconds).
            time_stamp: Global timestamp.

        Returns:
            True if execution is successful.
        """
        if step_id < 0 or step_id >= len(self.current_state):
             raise ExecutionError(f"Invalid step ID {step_id} for goal {self.name}")

        current_step = self.current_state[step_id]
        
        if time > current_step[KEY_TIME_LEFT]:
            raise ExecutionError(
                f"Execution time {format_execution_time(time)} exceeds remaining time "
                f"{format_execution_time(current_step[KEY_TIME_LEFT])} for step {step_id} in {self.name}."
            )

        current_step[KEY_TIME_LEFT] -= time
        if current_step[KEY_TIME_LEFT] <= 0: # Use <= to handle floating-point precision issues
            current_step[KEY_TIME_LEFT] = 0
            current_step[KEY_COMPLETED] = True 
            
        current_step[KEY_FINISHED_TIME_STAMP] = time + time_stamp
        
        return True


    def check_constraint(self, step_id: int, time: float, time_stamp: float, physical_objects):
        """
        Check all constraints for executing a step.

        Args:
            step_id: Step ID.
            time: Execution time.
            time_stamp: Global timestamp.
            physical_objects: Physical object manager.
        """
        if step_id < 0 or step_id >= len(self.current_state):
             raise ExecutionError(f"Invalid step ID {step_id} for goal {self.name}")

        current_step = self.current_state[step_id]

        # 1. Check time constraints
        time_constraints = current_step[KEY_TIME_CONSTRAINT]
        for pre_step_str, time_limit in time_constraints.items():
            if self.ignore_time_constraints:
                continue
            try:
                pre_step_id = int(pre_step_str)
                pre_step = self.current_state[pre_step_id]
            except (ValueError, IndexError):
                 raise ExecutionError(f"Invalid prerequisite step ID '{pre_step_str}' in time constraint for step {step_id} in {self.name}")

            if pre_step[KEY_FINISHED_TIME_STAMP] is not None:
                if time_stamp - pre_step[KEY_FINISHED_TIME_STAMP] > time_limit:
                    raise ExecutionError(
                        f'Time constraint violated for Step {step_id} in {self.name}. '
                        f'The time interval between step {pre_step_id} and step {step_id} '
                        f'exceeds the time limit {format_execution_time(time_limit)}. '
                        f'You should restart preparing the ingredients based on the observation.'
                    )

        # 2. Check step status and time
        if time > current_step[KEY_TIME_LEFT]:
            if current_step[KEY_TIME_LEFT] == 0:
                raise ExecutionError(f'Step {step_id} in {self.name} is already executed.')
            elif current_step[KEY_FINISHED_TIME_STAMP] and current_step[KEY_FINISHED_TIME_STAMP] < time_stamp:
                raise ExecutionError(
                    f'Step {step_id} in {self.name} is already executing and will finish at '
                    f'{format_time_stamp(current_step[KEY_FINISHED_TIME_STAMP])}.'
                )
            else:
                raise ExecutionError(
                    f'The execution time {format_execution_time(time)} exceeds the time needed '
                    f'{format_execution_time(current_step[KEY_TIME_LEFT])} for step {step_id} in {self.name}.'
                )

        if current_step[KEY_TIME_LEFT] != time and current_step[KEY_INTERRUPT] == 0:
            raise ExecutionError(
                f'Step {step_id} in {self.name} is not interruptable. '
                f'You should set the execution time as {format_execution_time(current_step[KEY_TIME_LEFT])} '
                f'to finish this step in one go.'
            )

        # 3. Check prerequisites
        for prev_step_id in current_step[KEY_PREQUISITES]:
            prev_step = self.current_state[prev_step_id]

            is_prev_completed = prev_step[KEY_COMPLETED]
            is_prev_finished = prev_step[KEY_FINISHED_TIME_STAMP] is not None and prev_step[KEY_FINISHED_TIME_STAMP] <= time_stamp

            # Prerequisite steps must be completed, or tools must be available
            if not (is_prev_completed and is_prev_finished):
                if not is_prev_completed:
                    raise ExecutionError(
                        f'Step {step_id} cannot be performed because prerequisite step {prev_step_id} '
                        f'is not completed. You should complete step {prev_step_id} for {self.name} first.'
                    )
                elif not is_prev_finished: 
                    raise ExecutionError(
                        f'Step {step_id} cannot be performed because prerequisite step {prev_step_id} '
                        f'is not finished. You should wait for step {prev_step_id} for {self.name} to finish '
                        f'at {format_time_stamp(prev_step[KEY_FINISHED_TIME_STAMP])}.'
                    )



    def is_complete(self) -> bool:
        """Check if the goal is complete."""
        return self.progress_record() == len(self.current_state)

    def progress_record(self) -> int:
        """Record the number of completed steps (including their prerequisites)."""
        complete = set()
        for i, step in enumerate(self.current_state):
            if step[KEY_COMPLETED]:
                complete.add(i)
                for pre in step[KEY_PREQUISITES]:
                    complete.add(pre)
        return len(complete)

