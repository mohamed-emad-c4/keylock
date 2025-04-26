import os
import sys
import re
import json
import platform
import ctypes
import tempfile

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def is_admin():
    """Check if the application is running with administrator privileges"""
    try:
        if platform.system() == 'Windows':
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            # On Unix systems, check if UID is 0 (root)
            return os.geteuid() == 0
    except:
        return False

def create_temp_file(content, suffix='.txt'):
    """Create a temporary file with the given content and return its path"""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    temp_file.write(content.encode('utf-8'))
    temp_file.close()
    return temp_file.name

def sanitize_filename(filename):
    """Remove invalid characters from filename"""
    # Replace invalid characters with underscore
    return re.sub(r'[\\/*?:"<>|]', '_', filename)

def format_time(seconds):
    """Format seconds into readable time string (HH:MM:SS)"""
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if hours > 0:
        return f"{int(hours)}:{int(minutes):02d}:{int(seconds):02d}"
    else:
        return f"{int(minutes):02d}:{int(seconds):02d}"

def get_system_info():
    """Get basic system information"""
    return {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor()
    }

def to_snake_case(text):
    """Convert text to snake_case"""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def to_camel_case(text):
    """Convert text to camelCase"""
    components = text.split('_')
    return components[0] + ''.join(x.title() for x in components[1:]) 