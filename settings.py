import os
import threading
import json

DEFAULT_CONFIG = {
    "unlock": "ctrl+q",
    "onstart_lock_keyboard": "false",
    "onstart_lock_mouse": "false",
    "refresh_rate": "1500",
    "quit_after": "never",
    "theme": "light"
}

config_template = """
&unlock@!@ctrl+q                # Shortcut to unlock (Examples: ctrl+q, alt+s, shift+ctrl+q)
&onstart_lock_keyboard@!@false  # Lock keyboard on start (true or false)
&onstart_lock_mouse@!@false     # Lock mouse on start (true or false)
&refresh_rate@!@1500            # Check for lock every x milliseconds (integer only)
&quit_after@!@never             # Exit app after some time (never or number in milliseconds, examples: 1000, 5000, never)
&theme@!@light                  # UI theme (light or dark)

# 🔴 The "Mouse lock" button is a bit buggy. When you lock only mouse, if exit shortcut has "ctrl" then you can only use a-z characters and nothing else. This is not an issue when you lock only keyboard or both.
"""


def parse(path):
    """Parse config file and return settings dictionary"""
    settings = {}
    try:
        with open(path, "r") as file:
            for line in file:
                line = line.split("#", 1)[0].strip()
                if line:
                    key_value = line.split("@!@", 1)
                    if len(key_value) == 2:
                        settings[key_value[0].lstrip("&")] = key_value[1]
        
        # Set any missing default values
        for key, value in DEFAULT_CONFIG.items():
            if key not in settings:
                settings[key] = value
    except Exception as e:
        print(f"Error parsing config: {e}")
        return DEFAULT_CONFIG.copy()
    
    return settings


def open_config(file_name):
    """Open and parse configuration file"""
    if os.path.exists(file_name):
        settings_dict = parse(file_name)
        return settings_dict
    return DEFAULT_CONFIG.copy()


def save_config(shortcut=None, **kwargs):
    """
    Save configuration to file
    
    Args:
        shortcut: Shortcut key (for backward compatibility)
        **kwargs: Other config options to update
    """
    config_path = "keylock.config"

    def main():
        try:
            current_config = {}
            
            # Create config file if it doesn't exist
            if not os.path.exists(config_path):
                with open(config_path, "w") as file:
                    file.write(config_template)
                current_config = DEFAULT_CONFIG.copy()
            else:
                # Read existing config
                current_config = parse(config_path)
            
            # Update values
            if shortcut is not None:
                current_config["unlock"] = shortcut
                
            # Update with any additional kwargs
            for key, value in kwargs.items():
                current_config[key] = str(value)
            
            # Write updated config
            with open(config_path, "r") as file:
                content = file.read().strip() or config_template

            lines = content.splitlines()
            updated_lines = []
            updated_keys = set()

            # Update existing lines
            for line in lines:
                skip = False
                for key in current_config:
                    if line.startswith(f"&{key}@!@"):
                        updated_lines.append(f"&{key}@!@{current_config[key]}")
                        updated_keys.add(key)
                        skip = True
                        break
                
                if not skip:
                    updated_lines.append(line)
            
            # Add any new keys
            for key, value in current_config.items():
                if key not in updated_keys:
                    updated_lines.append(f"&{key}@!@{value}")

            # Write back to file
            with open(config_path, "w") as file:
                file.write("\n".join(updated_lines))
                
        except Exception as e:
            print(f"Error saving config: {e}")

    thread = threading.Thread(target=main)
    thread.start()
    thread.join()


def get_theme_colors(theme="light"):
    """Get color scheme based on theme"""
    if theme.lower() == "dark":
        return {
            "bg": "#212529",
            "accent": "#0d6efd",
            "secondary": "#6c757d",
            "text": "#f8f9fa",
            "light_text": "#adb5bd",
            "highlight": "#343a40",
            "border": "#495057"
        }
    else:  # Light theme (default)
        return {
            "bg": "#f5f5f7",
            "accent": "#007bff",
            "secondary": "#6c757d",
            "text": "#212529",
            "light_text": "#6c757d",
            "highlight": "#e9ecef",
            "border": "#dee2e6"
        }
