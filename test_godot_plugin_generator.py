import unittest
import os
import shutil
import argparse
from unittest import mock

# Ensure the main script can be imported
import godot_plugin_generator

# Helper function to remove the addons directory
def remove_addons_dir():
    if os.path.exists("addons"):
        shutil.rmtree("addons")

class TestPluginGenerator(unittest.TestCase):

    def setUp(self):
        """Prepare for tests. Ensure no addons directory exists from previous runs."""
        remove_addons_dir()
        # Create a dummy default_icon.png for tests that require it,
        # as it's expected by generate_plugin_structure
        if not os.path.exists("default_icon.png"):
            with open("default_icon.png", "w") as f:
                f.write("dummy icon content")


    def tearDown(self):
        """Clean up after tests. Remove any created addons directory."""
        remove_addons_dir()
        # Remove the dummy icon if it was created by setUp
        # For safety, only remove if it contains "dummy icon content"
        # In a real scenario, you might have a more robust way to track test-generated files
        try:
            with open("default_icon.png", "r") as f:
                content = f.read()
            if content == "dummy icon content":
                 os.remove("default_icon.png")
        except FileNotFoundError:
            pass # If the file doesn't exist, no need to remove it

    # Test methods will be added here
    @mock.patch('builtins.input')
    def test_get_plugin_metadata_interactive(self, mock_input):
        # Simulate user inputs
        # Order of inputs: Plugin Name, Subfolder, Description, Author, Version, Script Name
        mock_input.side_effect = [
            "My Test Plugin",  # Plugin Name
            "",                # Subfolder (use default)
            "A test plugin.",  # Description
            "Test Author",     # Author
            "1.0.0",           # Version
            "my_custom_script.gd" # Script Name
        ]

        expected_metadata = {
            "plugin_name": "My Test Plugin",
            "subfolder": "my_test_plugin", # Default derived from plugin name
            "description": "A test plugin.",
            "author": "Test Author",
            "version": "1.0.0",
            "script_name": "my_custom_script.gd"
        }

        # We are testing the interactive mode, so no cli_args are passed
        result_metadata = godot_plugin_generator.get_plugin_metadata()
        self.assertEqual(result_metadata, expected_metadata)

    @mock.patch('builtins.input')
    def test_get_plugin_metadata_interactive_defaults(self, mock_input):
        # Simulate user inputs, relying more on defaults
        # Order of inputs: Plugin Name, Subfolder, Description, Author, Version, Script Name
        mock_input.side_effect = [
            "Another Plugin", # Plugin Name
            "",               # Subfolder (use default)
            "",               # Description (empty)
            "",               # Author (empty)
            "",               # Version (use default "0.1.0")
            ""                # Script Name (use default based on subfolder)
        ]

        expected_metadata = {
            "plugin_name": "Another Plugin",
            "subfolder": "another_plugin",
            "description": "",
            "author": "",
            "version": "0.1.0",
            "script_name": "another_plugin.gd" # Default derived from subfolder
        }
        
        result_metadata = godot_plugin_generator.get_plugin_metadata()
        self.assertEqual(result_metadata, expected_metadata)

    def test_get_plugin_metadata_cli(self):
        # Simulate command-line arguments using argparse.Namespace
        mock_args = argparse.Namespace(
            plugin_name="CLI Plugin",
            subfolder="cli_subfolder",
            description="CLI Description",
            author="CLI Author",
            version="2.0.0",
            script_name="cli_script.gd"
        )
        
        expected_metadata = {
            "plugin_name": "CLI Plugin",
            "subfolder": "cli_subfolder",
            "description": "CLI Description",
            "author": "CLI Author",
            "version": "2.0.0",
            "script_name": "cli_script.gd"
        }
        
        result_metadata = godot_plugin_generator.get_plugin_metadata(cli_args=mock_args)
        self.assertEqual(result_metadata, expected_metadata)

    def test_get_plugin_metadata_cli_mixed_defaults(self):
        # Simulate CLI args with some values missing to test default logic
        # Note: 'version' has a default of None in argparse, handled by get_plugin_metadata
        # 'script_name' also needs to be tested for default generation if not provided
        mock_args = argparse.Namespace(
            plugin_name="CLI Mixed",
            subfolder=None,       # Should be derived from plugin_name
            description="Mixed CLI desc",
            author=None,          # Should be prompted or empty if interactive disabled (it's empty)
            version=None,         # Should use default "0.1.0"
            script_name=None      # Should be derived from subfolder
        )
        
        # With CLI args, fields not provided are typically None or their argparse default.
        # The function get_plugin_metadata then applies its own defaults or derivations.
        expected_metadata = {
            "plugin_name": "CLI Mixed",
            "subfolder": "cli_mixed", # Derived
            "description": "Mixed CLI desc", # Provided
            "author": "", # Falls back to input, which if not mocked would be empty string for optional. If CLI, it's empty.
            "version": "0.1.0", # Default
            "script_name": "cli_mixed.gd" # Derived
        }
        
        # Mock input for optional fields that would be prompted if not for CLI args
        # For Author, if cli_args.author is None, it falls to input()
        with mock.patch('builtins.input', side_effect=['']): # Mock input for author if it falls through
            result_metadata = godot_plugin_generator.get_plugin_metadata(cli_args=mock_args)
        
        # Author will be an empty string if input is mocked to return empty for it.
        # If author was not in mock_args (i.e. mock_args.author does not exist), it would prompt.
        # Since it *is* in mock_args as None, it means the CLI arg was there but perhaps empty,
        # or we are directly passing None. The function logic is:
        # if cli_args and cli_args.author is not None -> use cli_args.author
        # else -> use input()
        # So, if cli_args.author is None, it uses input().
        self.assertEqual(result_metadata, expected_metadata)

    def test_generate_plugin_structure(self):
        sample_metadata = {
            "plugin_name": "Structure Test Plugin",
            "subfolder": "structure_test",
            "description": "Testing structure generation.",
            "author": "Structure Author",
            "version": "0.5.0",
            "script_name": "structure_script.gd"
        }
        
        godot_plugin_generator.generate_plugin_structure(sample_metadata)
        
        plugin_dir = os.path.join("addons", sample_metadata["subfolder"])
        self.assertTrue(os.path.isdir(plugin_dir), "Plugin directory was not created.")
        
        plugin_cfg_path = os.path.join(plugin_dir, "plugin.cfg")
        self.assertTrue(os.path.isfile(plugin_cfg_path), "plugin.cfg was not created.")
        
        icon_path = os.path.join(plugin_dir, "icon.png")
        self.assertTrue(os.path.isfile(icon_path), "icon.png was not copied.")

        with open(plugin_cfg_path, "r") as f:
            content = f.read()
            
        expected_cfg_content = f"""[plugin]

name="{sample_metadata['plugin_name']}"
description="{sample_metadata['description']}"
author="{sample_metadata['author']}"
version="{sample_metadata['version']}"
script="{sample_metadata['script_name']}"
"""
        self.assertEqual(content, expected_cfg_content, "plugin.cfg content is incorrect.")

    def test_generate_custom_node_files(self):
        plugin_meta = {
            "plugin_name": "Custom Node Test Plugin",
            "subfolder": "custom_node_test",
            "description": "Testing custom node file generation.",
            "author": "Custom Node Author",
            "version": "0.8.0",
            "script_name": "main_plugin_script.gd"
        }
        custom_node_meta = {
            "custom_node_name": "MySpecialNode",
            "base_node_type": "Control",
            "custom_node_script_name": "my_special_node.gd"
        }

        # First, generate the basic plugin structure
        godot_plugin_generator.generate_plugin_structure(plugin_meta)
        
        # Now, generate the custom node files
        godot_plugin_generator.generate_custom_node_files(plugin_meta, custom_node_meta)

        plugin_dir = os.path.join("addons", plugin_meta["subfolder"])
        
        # Check main EditorPlugin script
        editor_plugin_script_path = os.path.join(plugin_dir, plugin_meta["script_name"])
        self.assertTrue(os.path.isfile(editor_plugin_script_path), "EditorPlugin script was not created.")
        
        with open(editor_plugin_script_path, "r") as f:
            editor_content = f.read()
        
        expected_add_custom_type = f'add_custom_type("{custom_node_meta["custom_node_name"]}", "{custom_node_meta["base_node_type"]}", preload("res://addons/{plugin_meta["subfolder"]}/{custom_node_meta["custom_node_script_name"]}"), preload("res://addons/{plugin_meta["subfolder"]}/icon.png"))'
        self.assertIn(expected_add_custom_type, editor_content, "add_custom_type call is incorrect or missing.")
        
        expected_remove_custom_type = f'remove_custom_type("{custom_node_meta["custom_node_name"]}")'
        self.assertIn(expected_remove_custom_type, editor_content, "remove_custom_type call is incorrect or missing.")

        # Check custom node script
        custom_node_script_path = os.path.join(plugin_dir, custom_node_meta["custom_node_script_name"])
        self.assertTrue(os.path.isfile(custom_node_script_path), "Custom node script was not created.")
        
        with open(custom_node_script_path, "r") as f:
            custom_node_content = f.read()
            
        self.assertIn(f"extends {custom_node_meta['base_node_type']}", custom_node_content, "Custom node script does not extend the correct base type.")
        self.assertIn("@tool", custom_node_content, "Custom node script is missing @tool annotation.")

    def test_generate_custom_node_files_button_case(self):
        plugin_meta = {
            "plugin_name": "Button Test Plugin",
            "subfolder": "button_test",
            "script_name": "btn_plugin.gd",
            "description": "", "author": "", "version": "" # Not relevant for this part of test
        }
        custom_node_meta = {
            "custom_node_name": "MyButtonNode",
            "base_node_type": "Button",
            "custom_node_script_name": "my_button_node.gd"
        }
        godot_plugin_generator.generate_plugin_structure(plugin_meta)
        godot_plugin_generator.generate_custom_node_files(plugin_meta, custom_node_meta)
        
        plugin_dir = os.path.join("addons", plugin_meta["subfolder"])
        custom_node_script_path = os.path.join(plugin_dir, custom_node_meta["custom_node_script_name"])
        with open(custom_node_script_path, "r") as f:
            custom_node_content = f.read()
        
        self.assertIn("extends Button", custom_node_content)
        self.assertIn("# func _on_button_pressed():", custom_node_content, "Button specific example code is missing.")
        self.assertIn(f'#     print("{custom_node_meta["custom_node_name"]} was pressed!")', custom_node_content)


if __name__ == "__main__":
    unittest.main()
