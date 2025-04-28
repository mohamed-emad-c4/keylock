import pynput
import traceback
import logging
from pynput.keyboard import Key, KeyCode

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("keylock.log"),
        logging.StreamHandler()
    ]  
)
logger = logging.getLogger("keylock-core")

# Global state
keyboard_listener = None
mouse_listener = None
shortcut_listener = None
pressed_keys = set()
shortcut_keys = []
keyboard_locked = False
mouse_locked = False
changed = False

# Key mapping constants
VK_MAP = {
    48: "0", 49: "1", 50: "2", 51: "3", 52: "4",
    53: "5", 54: "6", 55: "7", 56: "8", 57: "9",
}

CONTROL_CHAR_MAP = {
    "\x01": "a", "\x02": "b", "\x03": "c", "\x04": "d", "\x05": "e",
    "\x06": "f", "\x07": "g", "\x08": "h", "\x09": "i", "\x0a": "j",
    "\x0b": "k", "\x0c": "l", "\x0d": "m", "\x0e": "n", "\x0f": "o",
    "\x10": "p", "\x11": "q", "\x12": "r", "\x13": "s", "\x14": "t",
    "\x15": "u", "\x16": "v", "\x17": "w", "\x18": "x", "\x19": "y",
    "\x1a": "z",
}


class KeylockError(Exception):
    """Base exception for Keylock errors"""
    pass


class KeyboardLockError(KeylockError):
    """Exception raised for keyboard locking errors"""
    pass


class MouseLockError(KeylockError):
    """Exception raised for mouse locking errors"""
    pass


class ShortcutError(KeylockError):
    """Exception raised for shortcut-related errors"""
    pass


def parse_shortcut(shortcut_str):
    """
    Parse a shortcut string like 'ctrl+q' into keyboard key objects
    
    Args:
        shortcut_str (str): String representation of the shortcut
        
    Returns:
        list: List of pynput key objects
    """
    try:
        if shortcut_str is None:
            shortcut_str = "ctrl+q"
            
        shortcut_parts = shortcut_str.lower().split("+")
        keys = []
        
        for part in shortcut_parts:
            if part == "ctrl":
                keys.append(pynput.keyboard.Key.ctrl_l)
            elif part == "shift":
                keys.append(pynput.keyboard.Key.shift)
            elif part == "alt":
                keys.append(pynput.keyboard.Key.alt_l)
            else:
                keys.append(pynput.keyboard.KeyCode.from_char(part))
                
        return keys
    except Exception as e:
        error_msg = f"Failed to parse shortcut '{shortcut_str}': {e}"
        logger.error(error_msg)
        raise ShortcutError(error_msg) from e


def stop_keyboard():
    """Stop keyboard listener and unlock keyboard"""
    global keyboard_listener, keyboard_locked, changed
    try:
        if keyboard_listener:
            keyboard_listener.stop()
            keyboard_listener = None
        keyboard_locked = False
        changed = True
        logger.info("Keyboard unlocked")
    except Exception as e:
        error_msg = f"Error unlocking keyboard: {e}"
        logger.error(f"{error_msg}\n{traceback.format_exc()}")
        raise KeyboardLockError(error_msg) from e


def start_keyboard():
    """Start keyboard listener and lock keyboard"""
    global keyboard_listener, keyboard_locked, changed
    try:
        keyboard_listener = pynput.keyboard.Listener(suppress=True)
        keyboard_listener.start()
        keyboard_locked = True
        changed = True
        logger.info("Keyboard locked")
    except Exception as e:
        error_msg = f"Error locking keyboard: {e}"
        logger.error(f"{error_msg}\n{traceback.format_exc()}")
        raise KeyboardLockError(error_msg) from e


def stop_mouse():
    """Stop mouse listener and unlock mouse"""
    global mouse_listener, mouse_locked, changed
    try:
        if mouse_listener:
            mouse_listener.stop()
            mouse_listener = None
        mouse_locked = False
        changed = True
        logger.info("Mouse unlocked")
    except Exception as e:
        error_msg = f"Error unlocking mouse: {e}"
        logger.error(f"{error_msg}\n{traceback.format_exc()}")
        raise MouseLockError(error_msg) from e


def start_mouse():
    """Start mouse listener and lock mouse"""
    global mouse_listener, mouse_locked, changed
    try:
        mouse_listener = pynput.mouse.Listener(suppress=True)
        mouse_listener.start()
        mouse_locked = True
        changed = True
        logger.info("Mouse locked")
    except Exception as e:
        error_msg = f"Error locking mouse: {e}"
        logger.error(f"{error_msg}\n{traceback.format_exc()}")
        raise MouseLockError(error_msg) from e


def start_shortcut_listener(shortcut):
    """
    Start the shortcut listener
    
    Args:
        shortcut (str): Shortcut to listen for (e.g. 'ctrl+q')
    """
    global shortcut_listener, shortcut_keys
    try:
        if not shortcut_listener:
            shortcut_keys = parse_shortcut(shortcut)
            shortcut_listener = pynput.keyboard.Listener(
                on_press=on_press, on_release=on_release
            )
            shortcut_listener.start()
            logger.info(f"Shortcut listener started for: {shortcut}")
    except Exception as e:
        error_msg = f"Error starting shortcut listener: {e}"
        logger.error(f"{error_msg}\n{traceback.format_exc()}")
        raise ShortcutError(error_msg) from e


def stop_shortcut_listener():
    """Stop the shortcut listener"""
    global shortcut_listener
    try:
        if shortcut_listener:
            shortcut_listener.stop()
            shortcut_listener = None
            logger.info("Shortcut listener stopped")
    except Exception as e:
        error_msg = f"Error stopping shortcut listener: {e}"
        logger.error(f"{error_msg}\n{traceback.format_exc()}")
        raise ShortcutError(error_msg) from e


def lock_keyboard(shortcut="ctrl+q"):
    """
    Toggle keyboard lock state
    
    Args:
        shortcut (str): Shortcut to use for unlocking
    """
    try:
        global keyboard_locked
        if keyboard_locked:
            stop_keyboard()
        else:
            start_keyboard()
        start_shortcut_listener(shortcut)
    except Exception as e:
        logger.error(f"Error in lock_keyboard: {e}\n{traceback.format_exc()}")
        raise


def lock_mouse(shortcut="ctrl+q"):
    """
    Toggle mouse lock state
    
    Args:
        shortcut (str): Shortcut to use for unlocking
    """
    try:
        global mouse_locked
        if mouse_locked:
            stop_mouse()
        else:
            start_mouse()
        start_shortcut_listener(shortcut)
    except Exception as e:
        logger.error(f"Error in lock_mouse: {e}\n{traceback.format_exc()}")
        raise


def string_to_key(string):
    """
    Convert a string representation to a pynput Key object
    
    Args:
        string (str): String representation of key
        
    Returns:
        Key or KeyCode or None: Corresponding key object
    """
    try:
        if string is None:
            return None
        if isinstance(string, str) and string.startswith("Key."):
            special_key_name = string[4:]
            try:
                return getattr(Key, special_key_name)
            except AttributeError:
                logger.warning(f"Unknown special key: {special_key_name}")
                return None
        elif len(string) == 1:
            return KeyCode.from_char(string)
        else:
            return None
    except Exception as e:
        logger.error(f"Error in string_to_key: {e}")
        return None


def on_press(key):
    """
    Handle key press events
    
    Args:
        key: The key that was pressed
    """
    try:
        global pressed_keys, changed
        readable_key = None
        
        # Get the readable representation of the key
        if hasattr(key, "char"):
            readable_key = key.char
        elif isinstance(key, Key):
            readable_key = str(key)
            
        # Map control characters to readable letters
        if readable_key in CONTROL_CHAR_MAP:
            readable_key = CONTROL_CHAR_MAP[readable_key]
            
        # Convert to key object and add to pressed keys
        key_object = string_to_key(readable_key)
        if key_object is not None:
            pressed_keys.add(key_object)
            
        logger.debug(f"Pressed key: {key}, Readable key: {readable_key}")
        
        # Check if shortcut is pressed
        if shortcut_keys and all(
            (k in pressed_keys) or 
            (isinstance(k, str) and k.startswith("\\x") and ord(k) in pressed_keys)
            for k in shortcut_keys
        ):
            logger.info("Shortcut pressed, unlocking all...")
            stop_keyboard()
            stop_mouse()
            stop_shortcut_listener()
            pressed_keys = set()
            changed = True
    except Exception as e:
        logger.error(f"Error in on_press: {e}\n{traceback.format_exc()}")


def on_release(key):
    """
    Handle key release events
    
    Args:
        key: The key that was released
    """
    try:
        global pressed_keys
        if key in pressed_keys:
            pressed_keys.remove(key)
    except Exception as e:
        logger.error(f"Error in on_release: {e}")


def is_keyboard_locked():
    """
    Check if keyboard is currently locked
    
    Returns:
        bool: True if keyboard is locked, False otherwise
    """
    global keyboard_locked
    return keyboard_locked


def is_mouse_locked():
    """
    Check if mouse is currently locked
    
    Returns:
        bool: True if mouse is locked, False otherwise
    """
    global mouse_locked
    return mouse_locked


def unlock_keyboard():
    """
    Unlock the keyboard
    
    Returns:
        bool: True if keyboard was unlocked successfully, False otherwise
    """
    try:
        if keyboard_locked:
            stop_keyboard()
        return True
    except Exception as e:
        logger.error(f"Error unlocking keyboard: {e}")
        return False


def unlock_mouse():
    """
    Unlock the mouse
    
    Returns:
        bool: True if mouse was unlocked successfully, False otherwise
    """
    try:
        if mouse_locked:
            stop_mouse()
        return True
    except Exception as e:
        logger.error(f"Error unlocking mouse: {e}")
        return False


def unlock_all():
    """
    Unlock both keyboard and mouse
    
    Returns:
        bool: True if both were unlocked successfully, False otherwise
    """
    kb_result = unlock_keyboard()
    mouse_result = unlock_mouse()
    return kb_result and mouse_result


def get_status():
    """
    Get the current status of keyboard and mouse
    
    Returns:
        tuple: (keyboard_locked, mouse_locked, changed)
    """
    global keyboard_locked, mouse_locked, changed
    was_changed = changed
    changed = False
    return keyboard_locked, mouse_locked, was_changed
