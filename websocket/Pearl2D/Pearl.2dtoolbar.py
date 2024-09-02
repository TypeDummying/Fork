
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk # type: ignore
import json
import os
from PIL import Image, ImageTk # type: ignore

class Pearl2DToolbar:
    def __init__(self, master):
        self.master = master
        self.toolbar_frame = None
        self.tools = {}
        self.custom_tools = {}
        self.addons = {}
        self.config_file = "2d_toolbar_config.json"
        
        self.create_toolbar()
        self.load_config()
        self.load_default_tools()
        self.load_custom_tools()
        self.load_addons()

    def create_toolbar(self):
        """Create the main toolbar frame"""
        self.toolbar_frame = ttk.Frame(self.master)
        self.toolbar_frame.pack(side=tk.LEFT, fill=tk.Y)

    def load_config(self):
        """Load toolbar configuration from JSON file"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "default_tools": ["select", "move", "rotate", "scale"],
                "custom_tools": [],
                "addons": []
            }
            self.save_config()

    def save_config(self):
        """Save toolbar configuration to JSON file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)

    def load_default_tools(self):
        """Load and create buttons for default tools"""
        for tool in self.config["default_tools"]:
            self.add_tool(tool, getattr(self, f"{tool}_tool"))

    def load_custom_tools(self):
        """Load and create buttons for custom tools"""
        for tool in self.config["custom_tools"]:
            self.add_custom_tool(tool["name"], tool["icon"], tool["action"])

    def load_addons(self):
        """Load and create buttons for addons"""
        for addon in self.config["addons"]:
            self.add_addon(addon["name"], addon["icon"], addon["action"])

    def add_tool(self, name, action):
        """Add a default tool to the toolbar"""
        icon = self.load_icon(f"{name}_icon.png")
        button = ttk.Button(self.toolbar_frame, image=icon, command=action)
        button.pack(pady=2)
        self.tools[name] = button

    def add_custom_tool(self, name, icon_path, action):
        """Add a custom tool to the toolbar"""
        icon = self.load_icon(icon_path)
        button = ttk.Button(self.toolbar_frame, image=icon, command=action)
        button.pack(pady=2)
        self.custom_tools[name] = button

    def add_addon(self, name, icon_path, action):
        """Add an addon to the toolbar"""
        icon = self.load_icon(icon_path)
        button = ttk.Button(self.toolbar_frame, image=icon, command=action)
        button.pack(pady=2)
        self.addons[name] = button

    def load_icon(self, icon_path):
        """Load and resize icon for toolbar buttons"""
        img = Image.open(icon_path)
        img = img.resize((24, 24), Image.ANTIALIAS)
        return ImageTk.PhotoImage(img)

    # Default tool actions
    def select_tool(self):
        print("Select tool activated")

    def move_tool(self):
        print("Move tool activated")

    def rotate_tool(self):
        print("Rotate tool activated")

    def scale_tool(self):
        print("Scale tool activated")

    # Custom tool and addon management
    def create_custom_tool(self, name, icon_path, action):
        """Create a new custom tool and add it to the toolbar"""
        self.add_custom_tool(name, icon_path, action)
        self.config["custom_tools"].append({
            "name": name,
            "icon": icon_path,
            "action": action.__name__
        })
        self.save_config()

    def remove_custom_tool(self, name):
        """Remove a custom tool from the toolbar"""
        if name in self.custom_tools:
            self.custom_tools[name].destroy()
            del self.custom_tools[name]
            self.config["custom_tools"] = [tool for tool in self.config["custom_tools"] if tool["name"] != name]
            self.save_config()

    def create_addon(self, name, icon_path, action):
        """Create a new addon and add it to the toolbar"""
        self.add_addon(name, icon_path, action)
        self.config["addons"].append({
            "name": name,
            "icon": icon_path,
            "action": action.__name__
        })
        self.save_config()

    def remove_addon(self, name):
        """Remove an addon from the toolbar"""
        if name in self.addons:
            self.addons[name].destroy()
            del self.addons[name]
            self.config["addons"] = [addon for addon in self.config["addons"] if addon["name"] != name]
            self.save_config()

    def rearrange_toolbar(self, new_order):
        """Rearrange the order of tools, custom tools, and addons in the toolbar"""
        for widget in self.toolbar_frame.winfo_children():
            widget.pack_forget()

        for item in new_order:
            if item in self.tools:
                self.tools[item].pack(pady=2)
            elif item in self.custom_tools:
                self.custom_tools[item].pack(pady=2)
            elif item in self.addons:
                self.addons[item].pack(pady=2)

        self.config["default_tools"] = [item for item in new_order if item in self.tools]
        self.config["custom_tools"] = [tool for tool in self.config["custom_tools"] if tool["name"] in new_order]
        self.config["addons"] = [addon for addon in self.config["addons"] if addon["name"] in new_order]
        self.save_config()

# Example usage and documentation

"""
Pearl2DToolbar - 2D Toolbar for Fork 3D/2D Modeling Software

This script provides a customizable 2D toolbar for the Fork 3D/2D modeling software.
It allows users to add default tools, custom tools, and addons to the toolbar.

Usage:
1. Create an instance of Pearl2DToolbar, passing the master widget (usually the main window or a frame).
2. Customize the toolbar by adding custom tools and addons.
3. Rearrange the toolbar as needed.

Example:
    root = tk.Tk()
    toolbar = Pearl2DToolbar(root)

    # Add a custom tool
    def custom_action():
        print("Custom tool activated")

    toolbar.create_custom_tool("Custom Tool", "custom_icon.png", custom_action)

    # Add an addon
    def addon_action():
        print("Addon activated")

    toolbar.create_addon("My Addon", "addon_icon.png", addon_action)

    # Rearrange the toolbar
    new_order = ["select", "move", "Custom Tool", "My Addon", "rotate", "scale"]
    toolbar.rearrange_toolbar(new_order)

    root.mainloop()

Customization:
- To add a custom tool, use the create_custom_tool() method.
- To add an addon, use the create_addon() method.
- To remove a custom tool or addon, use the remove_custom_tool() or remove_addon() method.
- To rearrange the toolbar, use the rearrange_toolbar() method with a new order list.

Configuration:
The toolbar configuration is saved in a JSON file (2d_toolbar_config.json) for persistence across sessions.

Icons:
Place your icon files (PNG format) in the same directory as this script or provide the full path when adding custom tools or addons.

Note: This toolbar is designed for 2D tools and addons. For 3D functionality, create a separate 3D toolbar or extend this class.
"""

# Additional comments for users

# User Customization Guide:
# 1. Adding a custom tool:
#    - Create a function that defines the tool's action
#    - Use create_custom_tool(name, icon_path, action) to add the tool
#    - Example: toolbar.create_custom_tool("My Tool", "my_tool_icon.png", my_tool_action)

# 2. Adding an addon:
#    - Create a function that defines the addon's action
#    - Use create_addon(name, icon_path, action) to add the addon
#    - Example: toolbar.create_addon("My Addon", "my_addon_icon.png", my_addon_action)

# 3. Removing a custom tool or addon:
#    - Use remove_custom_tool(name) or remove_addon(name) to remove the item
#    - Example: toolbar.remove_custom_tool("My Tool")

# 4. Rearranging the toolbar:
#    - Create a list with the desired order of tools and addons
#    - Use rearrange_toolbar(new_order) to apply the new arrangement
#    - Example: toolbar.rearrange_toolbar(["select", "My Tool", "move", "My Addon", "rotate", "scale"])

# 5. Extending functionality:
#    - To add new features, create new methods in the Pearl2DToolbar class
#    - You can override existing methods to change their behavior
#    - Consider creating a subclass for major modifications

# 6. Styling:
#    - This toolbar uses ttk for a native look and feel
#    - To change the style, you can create and apply a ttk.Style() to the buttons
#    - Example:
#      style = ttk.Style()
#      style.configure("TButton", padding=6, relief="flat", background="#ccc")

# 7. Icon management:
#    - Icons should be 24x24 pixels for consistency
#    - Use PNG format for icons to support transparency
#    - Store icons in a dedicated folder for better organization

# Remember to handle exceptions and provide user feedback for a better experience.
# Happy customizing!
