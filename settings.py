import os
import threading
import json
from utils import resource_path

CONFIG_FILE = resource_path("config.json")

# Theme definitions
LIGHT_THEME = {
    "background": "#F0F0F0",
    "foreground": "#333333",
    "accent": "#4A6BFF",
    "secondary_accent": "#7B8CFE",
    "button_bg": "#4A6BFF",
    "button_fg": "#FFFFFF",
    "button_hover": "#3A5BEF",
    "border": "#CCCCCC",
    "input_bg": "#FFFFFF",
    "input_fg": "#333333",
    "label": "#555555",
    "error": "#FF5252",
    "success": "#4CAF50",
    "warning": "#FFC107",
    "selection_bg": "#4A6BFF22",
    "highlight": "#FFEB3B",
    "separator": "#E0E0E0",
    "scrollbar": "#BBBBBB",
    "inactive": "#9E9E9E",
    "card_bg": "#FFFFFF",
    "card_shadow": "#00000022"
}

DARK_THEME = {
    "background": "#1E1E1E",
    "foreground": "#F0F0F0",
    "accent": "#4A6BFF",
    "secondary_accent": "#7B8CFE",
    "button_bg": "#4A6BFF",
    "button_fg": "#FFFFFF",
    "button_hover": "#5A7BFF",
    "border": "#444444",
    "input_bg": "#2C2C2C",
    "input_fg": "#F0F0F0",
    "label": "#AAAAAA",
    "error": "#FF5252",
    "success": "#4CAF50",
    "warning": "#FFC107",
    "selection_bg": "#4A6BFF44",
    "highlight": "#FFD600",
    "separator": "#383838",
    "scrollbar": "#555555",
    "inactive": "#777777",
    "card_bg": "#2A2A2A",
    "card_shadow": "#00000066"
}

# Default configuration
DEFAULT_CONFIG = {
    "theme": "light",
    "unlock": "ctrl+q",
    "refresh_rate": "1500",
    "quit_after": "never",
    "onstart_lock_keyboard": "false",
    "onstart_lock_mouse": "false"
}

# Template for config file
config_template = """# KeyLock Configuration File
&theme@!@light
&unlock@!@ctrl+q
&refresh_rate@!@1500
&quit_after@!@never
&onstart_lock_keyboard@!@false
&onstart_lock_mouse@!@false
"""

def get_default_config():
    """Return the default configuration"""
    return {
        "theme": "light",
        "auto_start": False,
        "minimize_to_tray": True,
        "check_updates": True,
        "sound_enabled": True,
        "notification_enabled": True,
        "font_size": "medium",  # small, medium, large
        "language": "en",
        "last_window_size": [800, 600],
        "last_window_position": [100, 100],
        "last_tab": 0,
        "recent_files": [],
        "custom_shortcuts": {}
    }

def get_theme_colors(theme="light"):
    """Get color theme based on theme name"""
    if theme.lower() == "dark":
        return DARK_THEME
    return LIGHT_THEME  # Default to light theme

def open_config():
    """Load configuration from file or create default if not exists"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                loaded_config = json.load(f)
                
            # Merge with default to ensure all keys exist
            config = get_default_config()
            for key, value in loaded_config.items():
                config[key] = value
                
            return config
        else:
            # Create default config if it doesn't exist
            config = get_default_config()
            save_config(config)
            return config
            
    except Exception as e:
        print(f"Error loading config: {e}")
        # Return default config on error
        return get_default_config()

def save_config(config):
    """Save configuration to file"""
    try:
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False

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


def update_ui_animation(root, from_colors, to_colors, duration=500):
    """
    Animate UI color changes for smooth transition
    
    Args:
        root: The root window
        from_colors: Starting color dictionary
        to_colors: Target color dictionary
        duration: Animation duration in milliseconds
    """
    import time
    
    start_time = time.time() * 1000
    end_time = start_time + duration
    
    def interpolate_color(color1, color2, ratio):
        """Interpolate between two hex colors"""
        try:
            # Convert hex to RGB
            r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
            r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
            
            # Interpolate
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            
            # Convert back to hex
            return f"#{r:02x}{g:02x}{b:02x}"
        except Exception:
            # Fall back to target color if interpolation fails
            return color2
    
    def update_step():
        """Update colors one step in the animation"""
        current_time = time.time() * 1000
        if current_time >= end_time:
            # Animation complete, use final colors
            return
        
        # Calculate interpolation ratio (0 to 1)
        ratio = (current_time - start_time) / duration
        
        # Create interpolated color map
        current_colors = {}
        for key in to_colors:
            if key in from_colors and key in to_colors:
                if from_colors[key].startswith('#') and to_colors[key].startswith('#'):
                    current_colors[key] = interpolate_color(from_colors[key], to_colors[key], ratio)
                else:
                    current_colors[key] = to_colors[key]
            else:
                current_colors[key] = to_colors[key]
        
        # Schedule next update
        if ratio < 1:
            root.after(16, update_step)  # ~60fps
    
    # Start animation
    update_step()
