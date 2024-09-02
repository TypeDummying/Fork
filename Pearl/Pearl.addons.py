
import os
import sys
import importlib
import inspect
import json
import logging
from typing import Dict, List, Any, Callable

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AddonManager:
    """
    Manages the loading, activation, and deactivation of addons for the Fork 3D modeling software.
    """

    def __init__(self, addon_directory: str):
        """
        Initialize the AddonManager.

        :param addon_directory: The directory where addons are stored.
        """
        self.addon_directory = addon_directory
        self.loaded_addons: Dict[str, Any] = {}
        self.active_addons: Dict[str, Any] = {}
        self.addon_metadata: Dict[str, Dict[str, Any]] = {}

    def discover_addons(self) -> List[str]:
        """
        Discover available addons in the addon directory.

        :return: A list of addon names (without the .py extension).
        """
        addon_files = [f[:-3] for f in os.listdir(self.addon_directory) if f.endswith('.py') and f != '__init__.py']
        logger.info(f"Discovered {len(addon_files)} potential addons.")
        return addon_files

    def load_addon(self, addon_name: str) -> bool:
        """
        Load an addon by name.

        :param addon_name: The name of the addon to load.
        :return: True if the addon was loaded successfully, False otherwise.
        """
        if addon_name in self.loaded_addons:
            logger.warning(f"Addon '{addon_name}' is already loaded.")
            return False

        try:
            # Construct the full path to the addon file
            addon_path = os.path.join(self.addon_directory, f"{addon_name}.py")
            
            # Add the addon directory to sys.path temporarily
            sys.path.insert(0, self.addon_directory)
            
            # Import the addon module
            addon_module = importlib.import_module(addon_name)
            
            # Remove the addon directory from sys.path
            sys.path.pop(0)

            # Check if the addon has the required attributes and methods
            if not hasattr(addon_module, 'initialize') or not callable(getattr(addon_module, 'initialize')):
                raise AttributeError("Addon must have an 'initialize' function.")

            if not hasattr(addon_module, 'shutdown') or not callable(getattr(addon_module, 'shutdown')):
                raise AttributeError("Addon must have a 'shutdown' function.")

            # Load metadata if available
            metadata = self._load_addon_metadata(addon_name, addon_module)
            self.addon_metadata[addon_name] = metadata

            # Store the loaded addon
            self.loaded_addons[addon_name] = addon_module
            logger.info(f"Successfully loaded addon: {addon_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to load addon '{addon_name}': {str(e)}")
            return False

    def _load_addon_metadata(self, addon_name: str, addon_module: Any) -> Dict[str, Any]:
        """
        Load metadata for an addon.

        :param addon_name: The name of the addon.
        :param addon_module: The imported addon module.
        :return: A dictionary containing the addon's metadata.
        """
        metadata = {
            "name": addon_name,
            "version": getattr(addon_module, "__version__", "Unknown"),
            "author": getattr(addon_module, "__author__", "Unknown"),
            "description": getattr(addon_module, "__doc__", "No description provided."),
            "dependencies": getattr(addon_module, "__dependencies__", []),
        }

        # Look for a metadata.json file
        metadata_file = os.path.join(self.addon_directory, f"{addon_name}_metadata.json")
        if os.path.exists(metadata_file):
            try:
                with open(metadata_file, 'r') as f:
                    file_metadata = json.load(f)
                metadata.update(file_metadata)
            except json.JSONDecodeError:
                logger.warning(f"Invalid metadata file for addon '{addon_name}'.")

        return metadata

    def activate_addon(self, addon_name: str) -> bool:
        """
        Activate a loaded addon.

        :param addon_name: The name of the addon to activate.
        :return: True if the addon was activated successfully, False otherwise.
        """
        if addon_name not in self.loaded_addons:
            logger.error(f"Cannot activate '{addon_name}'. Addon is not loaded.")
            return False

        if addon_name in self.active_addons:
            logger.warning(f"Addon '{addon_name}' is already active.")
            return False

        addon_module = self.loaded_addons[addon_name]

        try:
            # Check dependencies
            self._check_dependencies(addon_name)

            # Call the initialize function
            addon_module.initialize()

            # Add to active addons
            self.active_addons[addon_name] = addon_module
            logger.info(f"Activated addon: {addon_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to activate addon '{addon_name}': {str(e)}")
            return False

    def _check_dependencies(self, addon_name: str):
        """
        Check if all dependencies for an addon are satisfied.

        :param addon_name: The name of the addon to check dependencies for.
        :raises ImportError: If a dependency is not satisfied.
        """
        dependencies = self.addon_metadata[addon_name].get("dependencies", [])
        for dep in dependencies:
            if dep not in self.active_addons:
                raise ImportError(f"Dependency '{dep}' is not active. Please activate it first.")

    def deactivate_addon(self, addon_name: str) -> bool:
        """
        Deactivate an active addon.

        :param addon_name: The name of the addon to deactivate.
        :return: True if the addon was deactivated successfully, False otherwise.
        """
        if addon_name not in self.active_addons:
            logger.warning(f"Addon '{addon_name}' is not active.")
            return False

        addon_module = self.active_addons[addon_name]

        try:
            # Call the shutdown function
            addon_module.shutdown()

            # Remove from active addons
            del self.active_addons[addon_name]
            logger.info(f"Deactivated addon: {addon_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to deactivate addon '{addon_name}': {str(e)}")
            return False

    def get_addon_info(self, addon_name: str) -> Dict[str, Any]:
        """
        Get information about a specific addon.

        :param addon_name: The name of the addon.
        :return: A dictionary containing information about the addon.
        """
        if addon_name not in self.loaded_addons:
            raise ValueError(f"Addon '{addon_name}' is not loaded.")

        addon_module = self.loaded_addons[addon_name]
        metadata = self.addon_metadata.get(addon_name, {})

        info = {
            "name": addon_name,
            "version": metadata.get("version", "Unknown"),
            "author": metadata.get("author", "Unknown"),
            "description": metadata.get("description", "No description provided."),
            "status": "Active" if addon_name in self.active_addons else "Inactive",
            "dependencies": metadata.get("dependencies", []),
        }

        # Get all public functions and classes
        public_items = inspect.getmembers(addon_module, lambda x: not x.__name__.startswith('_'))
        info["functions"] = [name for name, obj in public_items if inspect.isfunction(obj)]
        info["classes"] = [name for name, obj in public_items if inspect.isclass(obj)]

        return info

    def reload_addon(self, addon_name: str) -> bool:
        """
        Reload an addon. If the addon is active, it will be deactivated and then reactivated.

        :param addon_name: The name of the addon to reload.
        :return: True if the addon was reloaded successfully, False otherwise.
        """
        if addon_name not in self.loaded_addons:
            logger.error(f"Cannot reload '{addon_name}'. Addon is not loaded.")
            return False

        was_active = addon_name in self.active_addons

        # Deactivate if active
        if was_active:
            self.deactivate_addon(addon_name)

        # Unload the addon
        del self.loaded_addons[addon_name]
        del self.addon_metadata[addon_name]

        # Reload the addon
        if self.load_addon(addon_name):
            # Reactivate if it was active before
            if was_active:
                return self.activate_addon(addon_name)
            return True
        return False

    def get_active_addons(self) -> List[str]:
        """
        Get a list of all currently active addons.

        :return: A list of active addon names.
        """
        return list(self.active_addons.keys())

    def get_loaded_addons(self) -> List[str]:
        """
        Get a list of all currently loaded addons.

        :return: A list of loaded addon names.
        """
        return list(self.loaded_addons.keys())

    def execute_addon_function(self, addon_name: str, function_name: str, *args, **kwargs) -> Any:
        """
        Execute a function from an active addon.

        :param addon_name: The name of the addon.
        :param function_name: The name of the function to execute.
        :param args: Positional arguments to pass to the function.
        :param kwargs: Keyword arguments to pass to the function.
        :return: The result of the function execution.
        """
        if addon_name not in self.active_addons:
            raise ValueError(f"Addon '{addon_name}' is not active.")

        addon_module = self.active_addons[addon_name]

        if not hasattr(addon_module, function_name):
            raise AttributeError(f"Function '{function_name}' not found in addon '{addon_name}'.")

        function = getattr(addon_module, function_name)
        return function(*args, **kwargs)

# Example usage and documentation

def main():
    """
    Example usage of the AddonManager class.
    """
    # Initialize the AddonManager
    addon_manager = AddonManager("path/to/addons")

    # Discover available addons
    available_addons = addon_manager.discover_addons()
    print(f"Available addons: {available_addons}")

    # Load an addon
    addon_name = "example_addon"
    if addon_manager.load_addon(addon_name):
        print(f"Successfully loaded {addon_name}")

        # Activate the addon
        if addon_manager.activate_addon(addon_name):
            print(f"Successfully activated {addon_name}")

            # Get information about the addon
            addon_info = addon_manager.get_addon_info(addon_name)
            print(f"Addon info: {addon_info}")

            # Execute a function from the addon
            try:
                result = addon_manager.execute_addon_function(addon_name, "some_function", arg1="value1")
                print(f"Function result: {result}")
            except Exception as e:
                print(f"Error executing addon function: {str(e)}")

            # Deactivate the addon
            if addon_manager.deactivate_addon(addon_name):
                print(f"Successfully deactivated {addon_name}")

    # Get lists of loaded and active addons
    print(f"Loaded addons: {addon_manager.get_loaded_addons()}")
    print(f"Active addons: {addon_manager.get_active_addons()}")

if __name__ == "__main__":
    main()

"""
Addon Development Guide for Fork 3D Modeling Software

1. Addon Structure:
   An addon for Fork should be a single Python file with a .py extension.
   The file should contain at least two functions:
   - initialize(): Called when the addon is activated.
   - shutdown(): Called when the addon is deactivated.

2. Metadata:
   Addons can include metadata as module-level variables:
   - __version__: The version of the addon.
   - __author__: The author of the addon.
   - __doc__: A docstring describing the addon's functionality.
   - __dependencies__: A list of other addons that this addon depends on.

   Alternatively, you can provide a separate JSON file named <addon_name>_metadata.json
   in the same directory as the addon file.

3. Addon Functionality:
   - Implement your addon's functionality as functions and classes within the addon file.
   - Use the Fork API (not provided in this example) to interact with the 3D modeling software.
   - Avoid name conflicts with other addons by using unique prefixes for your functions and classes.

4. Error Handling:
   - Handle exceptions within your addon to prevent crashes.
   - Use logging to report errors and important information.

5. Performance:
   - Be mindful of performance, especially for operations that may be called frequently.
   - Use efficient algorithms and data structures.

6. User Interface:
   - If your addon requires a user interface, use the UI toolkit provided by Fork (not shown in this example).
   - Follow Fork's UI guidelines for consistency.

7. Testing:
   - Write unit tests for your addon to ensure its functionality.
   - Test your addon with different versions of Fork to ensure compatibility.

8. Documentation:
   - Provide clear documentation for your addon, including installation instructions and usage examples.
   - Document each public function and class in your addon.

9. Distribution:
   - Package your addon along with any required resources and the metadata file.
   - Provide clear installation instructions for users.

10. Maintenance:
    - Keep your addon updated to work with the latest version of Fork.
    - Respond to user feedback and fix bugs promptly.

Example Addon Structure:


# example_addon.py

__version__ = "1.0.0"
__author__ = "Your Name"
__doc__ = "This addon adds example functionality to Fork."
__dependencies__ = ["some_other_addon"]

import logging

logger = logging.getLogger(__name__)

def initialize():
    logger.info("Example addon initialized")
    # Set up your addon here

def shutdown():
    logger.info("Example addon shut down")
    # Clean up your addon here

def some_function(arg1):
    # Implement your addon functionality here
    return f"Processed {arg1}"

class SomeClass:
    # Implement your addon classes here
    pass


This addon system allows for flexible and powerful extensions to the Fork 3D modeling software
while maintaining a structured and manageable approach to addon development and usage.
"""
