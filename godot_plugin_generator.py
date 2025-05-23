import os
import shutil
import argparse

def get_plugin_metadata(cli_args=None):
    """Prompts the user for plugin metadata or uses CLI args, and returns it as a dictionary."""
    metadata = {}

    # Plugin Name (required)
    if cli_args and cli_args.plugin_name:
        metadata["plugin_name"] = cli_args.plugin_name
    else:
        while True:
            plugin_name_input = input("Enter Plugin Name: ").strip()
            if plugin_name_input:
                metadata["plugin_name"] = plugin_name_input
                break
            print("Plugin Name cannot be empty.")
    
    plugin_name_for_suggestions = metadata["plugin_name"] # Used for suggesting subfolder and script name

    # Subfolder name
    if cli_args and cli_args.subfolder:
        metadata["subfolder"] = cli_args.subfolder
    else:
        suggested_subfolder = plugin_name_for_suggestions.lower().replace(" ", "_")
        while True:
            subfolder_input = input(f"Enter Subfolder name (default: {suggested_subfolder}): ").strip()
            if not subfolder_input:
                subfolder_input = suggested_subfolder
            if subfolder_input:
                metadata["subfolder"] = subfolder_input
                break
            print("Subfolder name cannot be empty.")

    # Description
    if cli_args and cli_args.description is not None: # Check for None because description can be empty string
        metadata["description"] = cli_args.description
    else:
        metadata["description"] = input("Enter Description (optional): ").strip()

    # Author
    if cli_args and cli_args.author is not None: # Check for None because author can be empty string
        metadata["author"] = cli_args.author
    else:
        metadata["author"] = input("Enter Author (optional): ").strip()

    # Version
    if cli_args and cli_args.version:
        metadata["version"] = cli_args.version
    else:
        version_input = input("Enter Version (default: 0.1.0): ").strip()
        if not version_input:
            version_input = "0.1.0"
        metadata["version"] = version_input

    # Main EditorPlugin script name
    if cli_args and cli_args.script_name:
        script_name_val = cli_args.script_name
        if not script_name_val.endswith(".gd"):
            script_name_val += ".gd"
        metadata["script_name"] = script_name_val
    else:
        suggested_script_name = f"{metadata['subfolder']}.gd"
        while True:
            script_name_input = input(f"Enter Main EditorPlugin script name (default: {suggested_script_name}): ").strip()
            if not script_name_input:
                script_name_input = suggested_script_name
            if script_name_input:
                if not script_name_input.endswith(".gd"):
                    script_name_input += ".gd"
                metadata["script_name"] = script_name_input
                break
            print("Main EditorPlugin script name cannot be empty.")
            
    return metadata

def generate_plugin_structure(metadata):
    """Generates the plugin directory structure and plugin.cfg file."""
    plugin_dir = os.path.join("addons", metadata["subfolder"])
    os.makedirs(plugin_dir, exist_ok=True)

    plugin_cfg_path = os.path.join(plugin_dir, "plugin.cfg")
    
    # Ensure the key for the script name matches what's in metadata
    # It was stored as "script_name" in get_plugin_metadata
    main_script_name = metadata["script_name"] 

    plugin_cfg_content = f"""[plugin]

name="{metadata['plugin_name']}"
description="{metadata['description']}"
author="{metadata['author']}"
version="{metadata['version']}"
script="{main_script_name}"
"""
    with open(plugin_cfg_path, "w") as f:
        f.write(plugin_cfg_content)

    print(f"\nSuccessfully created plugin directory: {plugin_dir}")
    print(f"Successfully created plugin configuration: {plugin_cfg_path}")

    # Copy the default icon
    default_icon_src = "default_icon.png"
    if os.path.exists(default_icon_src):
        icon_dst_path = os.path.join(plugin_dir, "icon.png")
        shutil.copy2(default_icon_src, icon_dst_path)
        print(f"Successfully copied default icon to: {icon_dst_path}")
    else:
        print(f"Warning: default_icon.png not found. Please create or add one to the script's directory.")


def get_custom_node_metadata():
    """Prompts the user for custom node metadata and returns it as a dictionary."""
    metadata = {}

    # Custom Node Name (required)
    while True:
        custom_node_name = input("Enter Custom Node Name (e.g., MyCoolButton): ").strip()
        if custom_node_name:
            metadata["custom_node_name"] = custom_node_name
            break
        print("Custom Node Name cannot be empty.")

    # Base Node Type (default: "Node")
    base_node_type = input("Enter Base Node Type (default: Node, e.g., Button, Node2D): ").strip()
    if not base_node_type:
        base_node_type = "Node"
    metadata["base_node_type"] = base_node_type
    
    # Custom Node Script Name (suggest default based on custom_node_name)
    suggested_script_name = f"{custom_node_name.lower().replace(' ', '_')}.gd"
    while True:
        custom_node_script_name = input(f"Enter Custom Node Script Name (default: {suggested_script_name}): ").strip()
        if not custom_node_script_name:
            custom_node_script_name = suggested_script_name
        if custom_node_script_name:
            # Ensure it ends with .gd
            if not custom_node_script_name.endswith(".gd"):
                custom_node_script_name += ".gd"
            metadata["custom_node_script_name"] = custom_node_script_name
            break
        print("Custom Node Script Name cannot be empty.")
        
    return metadata

def generate_custom_node_files(plugin_metadata, custom_node_metadata):
    """Generates the main EditorPlugin script and the custom node script."""
    plugin_subfolder = plugin_metadata["subfolder"]
    main_plugin_script_name = plugin_metadata["script_name"] # This was "script_name" in get_plugin_metadata
    
    # Path for the main EditorPlugin script
    editor_plugin_script_path = os.path.join("addons", plugin_subfolder, main_plugin_script_name)

    # Content for the main EditorPlugin script
    # Note: Godot uses "icon.svg" by default if not specified, or "icon.png"
    # For now, let's assume icon.png might be added later or is a common choice.
    editor_plugin_script_content = f"""@tool
extends EditorPlugin

func _enter_tree():
    add_custom_type("{custom_node_metadata['custom_node_name']}", "{custom_node_metadata['base_node_type']}", preload("res://addons/{plugin_subfolder}/{custom_node_metadata['custom_node_script_name']}"), preload("res://addons/{plugin_subfolder}/icon.png"))

func _exit_tree():
    remove_custom_type("{custom_node_metadata['custom_node_name']}")
"""
    with open(editor_plugin_script_path, "w") as f:
        f.write(editor_plugin_script_content)
    print(f"Successfully created main EditorPlugin script: {editor_plugin_script_path}")

    # Path for the custom node script
    custom_node_script_path = os.path.join("addons", plugin_subfolder, custom_node_metadata['custom_node_script_name'])

    # Content for the custom node script
    base_type = custom_node_metadata['base_node_type']
    custom_node_name = custom_node_metadata['custom_node_name']
    
    custom_node_script_content = f"""@tool
extends {base_type}

func _init():
    # You can add initialization logic here if needed.
    pass

func _ready():
    # Called when the node is ready in the scene tree.
"""
    if base_type == "Button":
        custom_node_script_content += f"""
    # For Button example:
    # if not Engine.is_editor_hint():
    #     self.pressed.connect(_on_button_pressed)
    pass

# For Button example:
# func _on_button_pressed():
#     print("{custom_node_name} was pressed!")
"""
    else:
        custom_node_script_content += """
    pass

# Add other custom methods and properties below.
"""
    # Ensure the script ends with a newline
    if not custom_node_script_content.endswith("\n"):
        custom_node_script_content += "\n"
        
    with open(custom_node_script_path, "w") as f:
        f.write(custom_node_script_content)
    print(f"Successfully created custom node script: {custom_node_script_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Godot Engine Plugin Structure")
    parser.add_argument("--plugin_name", help="The name of the plugin")
    parser.add_argument("--subfolder", help="The subfolder name for the plugin in the 'addons' directory")
    parser.add_argument("--description", help="A short description of the plugin")
    parser.add_argument("--author", help="The author's name")
    parser.add_argument("--version", help="The plugin version", default=None) # Default handled in get_plugin_metadata if None
    parser.add_argument("--script_name", help="The main EditorPlugin script name (e.g., plugin.gd)")
    
    args = parser.parse_args()

    plugin_data = get_plugin_metadata(args)
    generate_plugin_structure(plugin_data)

    # If CLI args are used, we might not want to interactively ask for custom node creation,
    # or we might want specific CLI args for that too. For now, keep interactive.
    create_custom_node = input("\nDo you want to create a Custom Node for this plugin? (y/N): ").strip().lower()
    if create_custom_node == 'y':
        custom_node_data = get_custom_node_metadata()
        generate_custom_node_files(plugin_data, custom_node_data)
    else:
        # If no custom node, we still need to create the main plugin script,
        # but it will be simpler, without add_custom_type.
        # For now, the task implies custom node is the primary flow.
        # Let's create a placeholder main script if no custom node.
        main_plugin_script_path = os.path.join("addons", plugin_data["subfolder"], plugin_data["script_name"])
        if not os.path.exists(main_plugin_script_path):
            placeholder_script_content = f"""@tool
extends EditorPlugin

func _enter_tree():
    # Plugin '{plugin_data['plugin_name']}' loaded. Add custom docks, UIs, etc. here.
    pass

func _exit_tree():
    # Plugin '{plugin_data['plugin_name']}' unloaded. Clean up here.
    pass
"""
            with open(main_plugin_script_path, "w") as f:
                f.write(placeholder_script_content)
            print(f"Successfully created placeholder main EditorPlugin script: {main_plugin_script_path}")
