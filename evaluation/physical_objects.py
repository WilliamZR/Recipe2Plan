# physical_objects.py
import logging
from typing import Dict, List, Any, Optional, Tuple, Union

# Configure logging (adjust level and format as needed)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define custom exception
class ExecutionError(Exception):
    """Custom exception to represent errors during execution."""
    pass

# Define constants
DOMAIN_COOKING = 'cooking'
OVEN_NAME = 'oven'
MICROWAVE_NAME = 'microwave'
STOVE_NAME = 'stove'
TEMPERATURE_PROPERTY = 'temperature'
VOLUME_PROPERTY = 'volume'
RESERVE_KEY = 'reserve'
REQUIRE_KEY = 'require'
UPDATE_KEY = 'update'


class ObjectTracker:
    """
    Tracks the state of a single physical object (e.g., oven, microwave).
    """

    def __init__(self, name: str, properties: Optional[List[str]] = None, num: int = 1):
        """
        Initialize the object tracker.

        Args:
            name: Name of the object.
            properties: List of properties the object has (e.g., ['temperature']).
            num: Number of instances of the object (e.g., multiple stoves).
        """
        self.name = name
        self.properties: Dict[str, Any] = {prop: None for prop in (properties or [])}
        self.occupied_time: List[Tuple[float, float]] = []
        self.num = num
        self.reserved: str = ''  # Reserved for specific recipe use

    def _time_interval_overlap(self, interval1: Tuple[float, float], interval2: Tuple[float, float]) -> bool:
        """
        Check if two time intervals overlap.

        Args:
            interval1: First time interval (start, end).
            interval2: Second time interval (start, end).

        Returns:
            True if intervals overlap, otherwise False.
        """
        start1, end1 = interval1
        start2, end2 = interval2

        # Case where a point overlaps with an interval
        if start1 == end1:
            return start2 < start1 < end2
        if start2 == end2:
            return start1 < start2 < end1

        # Case where two intervals overlap
        return max(start1, start2) < min(end1, end2)

    def _is_available(self, time: float, time_stamp: float, argument: Dict[str, Any], recipe_name: str) -> bool:
        """
        Check if the object is available at the given time.

        Args:
            time: Execution time.
            time_stamp: Global timestamp.
            argument: Dictionary of action parameters.
            recipe_name: Current recipe name.

        Returns:
            True if available, otherwise raises ExecutionError.
        """
        current_time_interval = (time_stamp, time_stamp + time)
        overlapping_count = 0

        # Check if reserved by another recipe
        if self.reserved and self.reserved != recipe_name:
            raise ExecutionError(f"Object {self.name} is reserved for recipe '{self.reserved}'")

        for interval in self.occupied_time:
            if self._time_interval_overlap(interval, current_time_interval):
                # Allow operations with identical time and property updates (e.g., preheating the oven for different recipes simultaneously)
                time_match = interval == current_time_interval
                property_identical = (
                    UPDATE_KEY in argument and
                    all(self.properties.get(k) == v for k, v in argument[UPDATE_KEY].items())
                )
                if time_match and property_identical:
                    continue
                overlapping_count += 1

        if overlapping_count >= self.num:
            raise ExecutionError(f"Object {self.name} is occupied")

        # Check if required properties are satisfied
        if REQUIRE_KEY in argument:
            required_properties = argument[REQUIRE_KEY]
            for key, required_value in required_properties.items():
                current_value = self.properties.get(key)
                if key != VOLUME_PROPERTY and current_value != required_value:
                    raise ExecutionError(
                        f"The {key} of {self.name} is {current_value} but the action needs {required_value}"
                    )
                elif key == VOLUME_PROPERTY and (current_value is None or current_value < required_value):
                    raise ExecutionError(
                        f"{self.name} volume is {current_value} but the action needs {required_value}. "
                        f"The volume is not enough"
                    )

        return True  # If no exception is raised, the object is considered available

    def check_constraint(self, time: float, time_stamp: float, argument: Dict[str, Any], recipe_name: str) -> None:
        """
        Check object constraints.

        Args:
            time: Execution time.
            time_stamp: Global timestamp.
            argument: Dictionary of action parameters.
            recipe_name: Current recipe name.
        """
        self._is_available(time, time_stamp, argument, recipe_name)

    def update_status(self, time: float, time_stamp: float, argument: Dict[str, Any]) -> None:
        """
        Update the object's status.

        Args:
            time: Execution time.
            time_stamp: Global timestamp.
            argument: Dictionary of action parameters.
        """
        current_time_interval = (time_stamp, time_stamp + time)
        self.occupied_time.append(current_time_interval)

        # Update object properties
        if UPDATE_KEY in argument:
            update_properties = argument[UPDATE_KEY]
            for key, value in update_properties.items():
                self.properties[key] = value
                logger.debug(f"Updated {self.name}.{key} to {value}")

        # Handle reservation
        if RESERVE_KEY in argument:
            self.reserved = argument[RESERVE_KEY]
            logger.debug(f"Reserved {self.name} for recipe '{self.reserved}'")

        # Update volume (if applicable)
        if (REQUIRE_KEY in argument and VOLUME_PROPERTY in argument[REQUIRE_KEY]):
            required_volume = argument[REQUIRE_KEY][VOLUME_PROPERTY]
            if self.properties.get(VOLUME_PROPERTY) is not None:
                self.properties[VOLUME_PROPERTY] -= required_volume
                logger.debug(f"Reduced {self.name} volume by {required_volume}. New volume: {self.properties[VOLUME_PROPERTY]}")

    def get_status(self, time_stamp: float) -> str:
        """
        Get the object's status description at the given timestamp.

        Args:
            time_stamp: Global timestamp.

        Returns:
            String description of the object's status.
        """
        status_parts = []

        # Check if occupied
        is_occupied = False
        for interval in self.occupied_time:
            if interval[0] <= time_stamp < interval[1]:
                is_occupied = True
                break
        if self.reserved:  # If reserved, also considered occupied
            is_occupied = True

        if is_occupied:
            status_parts.append("is occupied")
        else:
            status_parts.append("is not occupied")

        # Add property status
        for key, value in self.properties.items():
            if key in [TEMPERATURE_PROPERTY, VOLUME_PROPERTY]:
                if value is None:
                    status_parts.append(f"is not preheated")  # Assume temperature is related to preheating
                else:
                    status_parts.append(f"{key} is {value}")
            else:
                status_parts.append(f"{key} is {value}")

        return ", ".join(status_parts)

    def __str__(self) -> str:
        """Return the string representation of the object."""
        return f"{self.name}: {self.properties}"


class Physical_Objects:
    """
    Manages a collection of all physical objects.
    """

    def __init__(self, domain: str = DOMAIN_COOKING):
        """
        Initialize the physical object manager.

        Args:
            domain: Domain ('cooking', etc.).
        """
        self.domain = domain
        self.objects: Dict[str, ObjectTracker] = self._create_physical_objects(domain)

    def _create_physical_objects(self, domain: str) -> Dict[str, ObjectTracker]:
        """
        Create physical objects based on the domain.

        Args:
            domain: Domain name.

        Returns:
            Dictionary of physical objects.

        Raises:
            ExecutionError: If the domain is invalid.
        """
        if domain == DOMAIN_COOKING:
            return {
                OVEN_NAME: ObjectTracker(OVEN_NAME, properties=[TEMPERATURE_PROPERTY]),
                MICROWAVE_NAME: ObjectTracker(MICROWAVE_NAME),
                STOVE_NAME: ObjectTracker(STOVE_NAME),
            }
        else:
            raise ExecutionError(f"Invalid domain '{domain}', please choose from '{DOMAIN_COOKING}'")

    def check_constraint(self, time: float, global_time: float, action_dict: Dict[str, Any], recipe_name: str) -> None:
        """
        Check constraints for all relevant objects.

        Args:
            time: Execution time.
            global_time: Global timestamp.
            action_dict: Actions involving physical objects and their parameters.
            recipe_name: Current recipe name.
        """
        for obj_name, argument in action_dict.items():
            if obj_name in self.objects:
                self.objects[obj_name].check_constraint(time, global_time, argument, recipe_name)
            else:
                logger.warning(f"Object '{obj_name}' not found in domain '{self.domain}'")

    def update_status(self, time: float, global_time: float, action_dict: Dict[str, Any]) -> None:
        """
        Update the status of all relevant objects.

        Args:
            time: Execution time.
            global_time: Global timestamp.
            action_dict: Actions involving physical objects and their parameters.
        """
        for obj_name, argument in action_dict.items():
            if obj_name in self.objects:
                self.objects[obj_name].update_status(time, global_time, argument)
            else:
                logger.warning(f"Object '{obj_name}' not found in domain '{self.domain}'")

    def get_status(self, time_stamp: float) -> str:
        """
        Get the status description of all objects.

        Args:
            time_stamp: Global timestamp.

        Returns:
            String description of all object statuses.
        """
        status_parts = []
        for obj_name, obj_tracker in self.objects.items():
            status_parts.append(f"{obj_name} {obj_tracker.get_status(time_stamp)}")
        return "; ".join(status_parts)

    def __str__(self) -> str:
        """Return the string representation of all objects."""
        return "\n".join(str(obj) for obj in self.objects.values())
