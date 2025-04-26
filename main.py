import os
import sys
import core
import threading
import tkinter as tk
import traceback
from tkinter import ttk, font, messagebox
from core import lock_keyboard, lock_mouse
from settings import open_config, save_config, get_theme_colors

# Global variables
config = None
refresh_rate = 1500
current_theme = "light"
root = None
keyboard_img = None
mouse_img = None
keyboard_img_label = None
mouse_img_label = None
keyboard_status = None
mouse_status = None
shortcut = None
footer = None
debounce_timer = None
COLORS = {}


def initialize_app():
    """Initialize the application with configuration and error handling"""
    global config, current_theme, refresh_rate, COLORS
    
    try:
        config = open_config("keylock.config")
        current_theme = config.get("theme", "light")
        refresh_rate = int(config.get("refresh_rate", "1500"))
        
        if os.name == "nt":
            try:
                from ctypes import windll
                windll.shcore.SetProcessDpiAwareness(1)
            except Exception as e:
                print(f"Could not set DPI awareness: {e}")
        
        # Get theme colors
        COLORS = get_theme_colors(current_theme)
        return True
    except Exception as e:
        error_msg = f"Error initializing application: {e}\n{traceback.format_exc()}"
        print(error_msg)
        try:
            messagebox.showerror("Initialization Error", f"Failed to initialize: {e}")
        except:
            pass  # If messagebox fails (no GUI yet), just continue
        return False


def load_asset(path):
    """Load asset files with proper error handling"""
    try:
        base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
        assets = os.path.join(base, "assets")
        return os.path.join(assets, path)
    except Exception as e:
        print(f"Error loading asset {path}: {e}")
        # Return a fallback path that should exist
        return path


def create_ui():
    """Create the main UI with components properly separated"""
    global root, keyboard_img, mouse_img, keyboard_img_label, mouse_img_label
    global keyboard_status, mouse_status, shortcut, footer, COLORS
    
    try:
        # Initialize main window
        root = tk.Tk()
        root.geometry("400x440")
        root.configure(bg=COLORS["bg"])
        root.title("Keylock")
        
        try:
            root.iconbitmap(load_asset("icon.ico"))
        except Exception as e:
            print(f"Could not load icon: {e}")
        
        # Configure styles
        configure_styles()
        
        # Create main frame
        main_frame = tk.Frame(root, bg=COLORS["bg"], padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Create header section
        create_header_section(main_frame)
        
        # Create status section
        status_frame = create_status_section(main_frame)
        
        # Create buttons section
        create_buttons_section(main_frame)
        
        # Create settings section
        create_settings_section(main_frame)
        
        # Create footer
        footer = tk.Label(
            main_frame, 
            text="Press " + shortcut.get() + " to unlock", 
            bg=COLORS["bg"], 
            fg=COLORS["light_text"],
            pady=10
        )
        footer.pack(side="bottom", fill="x")
        
        # Apply initial config settings
        apply_config_settings()
        
        # Make window non-resizable
        root.resizable(False, False)
        
        return True
    except Exception as e:
        error_message = f"Error creating UI: {e}\n{traceback.format_exc()}"
        print(error_message)
        try:
            messagebox.showerror("UI Error", f"Failed to create user interface: {e}")
        except:
            pass  # If messagebox fails, just continue
        return False


def configure_styles():
    """Configure the UI styles"""
    try:
        # Create custom styles
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(family="Segoe UI", size=10)
        root.option_add("*Font", default_font)
        
        style = ttk.Style()
        style.configure("TButton", 
            background=COLORS["accent"], 
            foreground="white", 
            borderwidth=0,
            focuscolor=COLORS["accent"],
            padding=10
        )
        style.map("TButton",
            background=[("active", "#0069d9")],
            relief=[("pressed", "flat"), ("!pressed", "flat")]
        )
        
        style.configure("TEntry", 
            padding=8,
            fieldbackground=COLORS["highlight"],
            borderwidth=1,
        )
    except Exception as e:
        print(f"Error configuring styles: {e}")


def create_header_section(parent):
    """Create the header section of the UI"""
    try:
        # Headers
        title_label = tk.Label(parent, text="Keylock", font=("Segoe UI", 18, "bold"), 
                              bg=COLORS["bg"], fg=COLORS["text"])
        title_label.pack(pady=(0, 10))
        
        subtitle_label = tk.Label(parent, text="Lock your keyboard and mouse with ease", 
                                bg=COLORS["bg"], fg=COLORS["light_text"])
        subtitle_label.pack(pady=(0, 20))
    except Exception as e:
        print(f"Error creating header section: {e}")


def create_status_section(parent):
    """Create the status section of the UI with device status indicators"""
    global keyboard_img, mouse_img, keyboard_img_label, mouse_img_label, keyboard_status, mouse_status
    
    try:
        # Status frames
        status_frame = tk.Frame(parent, bg=COLORS["bg"])
        status_frame.pack(fill="x", pady=10)
        
        # Device status displays
        keyboard_status_frame = tk.Frame(status_frame, bg=COLORS["bg"], padx=10, pady=10)
        keyboard_status_frame.pack(side="left", fill="both", expand=True)
        
        mouse_status_frame = tk.Frame(status_frame, bg=COLORS["bg"], padx=10, pady=10)
        mouse_status_frame.pack(side="right", fill="both", expand=True)
        
        try:
            keyboard_locked_image = tk.PhotoImage(file=load_asset("keyboard_locked.png"))
            keyboard_unlocked_image = tk.PhotoImage(file=load_asset("keyboard_unlocked.png"))
            mouse_locked_image = tk.PhotoImage(file=load_asset("mouse_locked.png"))
            mouse_unlocked_image = tk.PhotoImage(file=load_asset("mouse_unlocked.png"))
        except Exception as e:
            print(f"Error loading status images: {e}")
            # Create empty images as fallback
            keyboard_locked_image = tk.PhotoImage(width=32, height=32)
            keyboard_unlocked_image = tk.PhotoImage(width=32, height=32)
            mouse_locked_image = tk.PhotoImage(width=32, height=32)
            mouse_unlocked_image = tk.PhotoImage(width=32, height=32)
        
        # Keyboard status
        keyboard_label = tk.Label(keyboard_status_frame, text="Keyboard", bg=COLORS["bg"], fg=COLORS["text"])
        keyboard_label.pack()
        
        keyboard_img = keyboard_unlocked_image
        keyboard_img_label = tk.Label(keyboard_status_frame, image=keyboard_img, bg=COLORS["bg"])
        keyboard_img_label.pack(pady=5)
        
        keyboard_status = tk.Label(keyboard_status_frame, text="Unlocked", bg=COLORS["bg"], 
                                 fg=COLORS["secondary"])
        keyboard_status.pack()
        
        # Mouse status
        mouse_label = tk.Label(mouse_status_frame, text="Mouse", bg=COLORS["bg"], fg=COLORS["text"])
        mouse_label.pack()
        
        mouse_img = mouse_unlocked_image
        mouse_img_label = tk.Label(mouse_status_frame, image=mouse_img, bg=COLORS["bg"])
        mouse_img_label.pack(pady=5)
        
        mouse_status = tk.Label(mouse_status_frame, text="Unlocked", bg=COLORS["bg"], 
                              fg=COLORS["secondary"])
        mouse_status.pack()
        
        return status_frame
    except Exception as e:
        print(f"Error creating status section: {e}")
        return None


def create_buttons_section(parent):
    """Create the buttons section of the UI"""
    try:
        # Buttons frame
        buttons_frame = tk.Frame(parent, bg=COLORS["bg"], pady=10)
        buttons_frame.pack(fill="x")
        
        # Individual lock buttons in a row
        lock_keyboard_btn = tk.Button(
            buttons_frame,
            text="Lock Keyboard",
            bg=COLORS["accent"],
            fg="white",
            relief="flat",
            borderwidth=0,
            pady=10,
            padx=10,
            cursor="hand2",
            activebackground="#0069d9",
            activeforeground="white",
            command=lambda: safe_lock_keyboard()
        )
        lock_keyboard_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        lock_mouse_btn = tk.Button(
            buttons_frame,
            text="Lock Mouse",
            bg=COLORS["accent"],
            fg="white",
            relief="flat",
            borderwidth=0,
            pady=10,
            padx=10,
            cursor="hand2",
            activebackground="#0069d9",
            activeforeground="white",
            command=lambda: safe_lock_mouse()
        )
        lock_mouse_btn.pack(side="right", fill="x", expand=True, padx=(5, 0))
        
        # Lock both button
        lock_both_btn = tk.Button(
            parent,
            text="Lock Both",
            bg="#dc3545", # Red for emphasis
            fg="white",
            relief="flat",
            borderwidth=0,
            pady=12,
            cursor="hand2",
            activebackground="#c82333",
            activeforeground="white",
            command=lambda: safe_lock_both()
        )
        lock_both_btn.pack(fill="x", pady=10)
    except Exception as e:
        print(f"Error creating buttons section: {e}")


def create_settings_section(parent):
    """Create the settings section of the UI"""
    global shortcut
    
    try:
        # Settings section
        settings_section = tk.Frame(parent, bg=COLORS["bg"], pady=10)
        settings_section.pack(fill="x", pady=(10, 0))
        
        # Settings header
        settings_header = tk.Label(settings_section, text="Settings", font=("Segoe UI", 12, "bold"), 
                                  bg=COLORS["bg"], fg=COLORS["text"])
        settings_header.pack(anchor="w", pady=(0, 10))
        
        # Shortcut settings frame
        settings_frame = tk.Frame(settings_section, bg=COLORS["bg"], padx=5, pady=5)
        settings_frame.pack(fill="x")
        
        # Shortcut label
        shortcut_label = tk.Label(settings_frame, text="Unlock Shortcut:", bg=COLORS["bg"], fg=COLORS["text"])
        shortcut_label.pack(side="left", padx=(0, 10))
        
        # Shortcut entry with modern styling
        shortcut = tk.Entry(
            settings_frame,
            bg=COLORS["highlight"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief="solid",
            borderwidth=1,
            highlightthickness=0
        )
        shortcut.pack(side="left", fill="x", expand=True, ipady=3)
        
        # Theme settings frame
        theme_frame = tk.Frame(settings_section, bg=COLORS["bg"], padx=5, pady=5)
        theme_frame.pack(fill="x", pady=(10, 0))
        
        # Theme label
        theme_label = tk.Label(theme_frame, text="UI Theme:", bg=COLORS["bg"], fg=COLORS["text"])
        theme_label.pack(side="left", padx=(0, 10))
        
        # Theme selection
        theme_var = tk.StringVar(value=current_theme)
        
        # Theme radio buttons
        light_radio = tk.Radiobutton(
            theme_frame, 
            text="Light", 
            variable=theme_var, 
            value="light", 
            bg=COLORS["bg"],
            fg=COLORS["text"],
            selectcolor=COLORS["highlight"],
            activebackground=COLORS["bg"],
            activeforeground=COLORS["text"]
        )
        light_radio.pack(side="left", padx=(0, 10))
        
        dark_radio = tk.Radiobutton(
            theme_frame, 
            text="Dark", 
            variable=theme_var, 
            value="dark", 
            bg=COLORS["bg"],
            fg=COLORS["text"],
            selectcolor=COLORS["highlight"],
            activebackground=COLORS["bg"],
            activeforeground=COLORS["text"]
        )
        dark_radio.pack(side="left", padx=(0, 10))
        
        apply_theme_btn = tk.Button(
            theme_frame,
            text="Apply",
            bg=COLORS["accent"],
            fg="white",
            relief="flat",
            borderwidth=0,
            padx=10,
            pady=2,
            cursor="hand2",
            activebackground="#0069d9",
            activeforeground="white",
            command=lambda: apply_theme(theme_var.get())
        )
        apply_theme_btn.pack(side="left", padx=(10, 0))
        
        # Set initial shortcut value from config
        if config:
            shortcut.insert(0, config.get("unlock", "ctrl+q"))
        else:
            shortcut.insert(0, "ctrl+q")
        
        # Bind shortcut change event
        shortcut.bind("<KeyRelease>", lambda e: debounce_shortcut_change())
    except Exception as e:
        print(f"Error creating settings section: {e}")


def apply_config_settings():
    """Apply settings from the config file"""
    try:
        if config:
            if config.get("onstart_lock_keyboard", "").lower() == "true":
                safe_lock_keyboard()
            if config.get("onstart_lock_mouse", "").lower() == "true":
                safe_lock_mouse()
            if config.get("quit_after", "never").lower() != "never":
                try:
                    quit_after = int(config["quit_after"])
                    root.after(quit_after, safe_exit)
                except ValueError:
                    print(f"Invalid quit_after value: {config['quit_after']}")
    except Exception as e:
        print(f"Error applying config settings: {e}")


def safe_exit():
    """Safely exit the application"""
    try:
        sys.exit()
    except Exception as e:
        print(f"Error during exit: {e}")
        os._exit(0)  # Force exit if sys.exit() fails


def update_keyboard():
    """Update keyboard lock status display"""
    try:
        global keyboard_img
        if core.keyboard_locked:
            keyboard_img = tk.PhotoImage(file=load_asset("keyboard_locked.png"))
            keyboard_img_label.configure(image=keyboard_img)
            keyboard_status.configure(text="Locked", fg="red")
        else:
            keyboard_img = tk.PhotoImage(file=load_asset("keyboard_unlocked.png"))
            keyboard_img_label.configure(image=keyboard_img)
            keyboard_status.configure(text="Unlocked", fg=COLORS["secondary"])
    except Exception as e:
        print(f"Error updating keyboard status: {e}")


def update_mouse():
    """Update mouse lock status display"""
    try:
        global mouse_img
        if core.mouse_locked:
            mouse_img = tk.PhotoImage(file=load_asset("mouse_locked.png"))
            mouse_img_label.configure(image=mouse_img)
            mouse_status.configure(text="Locked", fg="red")
        else:
            mouse_img = tk.PhotoImage(file=load_asset("mouse_unlocked.png"))
            mouse_img_label.configure(image=mouse_img)
            mouse_status.configure(text="Unlocked", fg=COLORS["secondary"])
    except Exception as e:
        print(f"Error updating mouse status: {e}")


def debounce_shortcut_change():
    """Debounce function for shortcut changes"""
    try:
        global debounce_timer
        if debounce_timer is not None:
            root.after_cancel(debounce_timer)
        debounce_timer = root.after(500, lambda: save_config(shortcut.get()))
    except Exception as e:
        print(f"Error in debounce: {e}")


def apply_theme(selected_theme):
    """Apply selected theme and show restart dialog"""
    try:
        save_config(shortcut=shortcut.get(), theme=selected_theme)
        
        # Restart application message
        restart_dialog = tk.Toplevel(root)
        restart_dialog.title("Theme Changed")
        restart_dialog.geometry("300x150")
        restart_dialog.configure(bg=COLORS["bg"])
        restart_dialog.transient(root)
        restart_dialog.grab_set()
        
        msg = tk.Label(
            restart_dialog, 
            text="Theme will be applied when you restart the application.", 
            wraplength=250,
            bg=COLORS["bg"],
            fg=COLORS["text"],
            pady=15
        )
        msg.pack(fill="both", expand=True)
        
        ok_btn = tk.Button(
            restart_dialog, 
            text="OK", 
            bg=COLORS["accent"],
            fg="white",
            relief="flat",
            borderwidth=0,
            command=restart_dialog.destroy
        )
        ok_btn.pack(pady=10)
    except Exception as e:
        messagebox.showerror("Theme Error", f"Could not apply theme: {e}")


def safe_lock_keyboard():
    """Safely lock keyboard with error handling"""
    try:
        lock_keyboard(shortcut.get())
        update_keyboard()
    except Exception as e:
        messagebox.showerror("Lock Error", f"Failed to lock keyboard: {e}")


def safe_lock_mouse():
    """Safely lock mouse with error handling"""
    try:
        lock_mouse(shortcut.get())
        update_mouse()
    except Exception as e:
        messagebox.showerror("Lock Error", f"Failed to lock mouse: {e}")


def safe_lock_both():
    """Safely lock both keyboard and mouse with error handling"""
    try:
        lock_keyboard(shortcut.get())
        lock_mouse(shortcut.get())
    except Exception as e:
        messagebox.showerror("Lock Error", f"Failed to lock devices: {e}")


def check_change():
    """Check for lock status changes and update UI"""
    try:
        if core.changed:
            update_keyboard()
            update_mouse()
            core.changed = False
        root.after(refresh_rate, check_change)
    except Exception as e:
        print(f"Error checking changes: {e}")
        # Attempt to reschedule despite error
        try:
            root.after(refresh_rate, check_change)
        except:
            pass


def update_footer():
    """Update footer text with current shortcut"""
    try:
        footer.configure(text="Press " + shortcut.get() + " to unlock")
        root.after(1000, update_footer)
    except Exception as e:
        print(f"Error updating footer: {e}")
        # Try to reschedule
        try:
            root.after(1000, update_footer)
        except:
            pass


def main():
    """Main application entry point with error handling"""
    try:
        # Initialize the application
        if not initialize_app():
            print("Failed to initialize application, exiting.")
            return 1
        
        # Create the UI
        if not create_ui():
            print("Failed to create UI, exiting.")
            return 1
        
        # Start background threads and timers
        threading.Thread(target=check_change, daemon=True).start()
        update_footer()
        
        # Start the main loop
        root.mainloop()
        return 0
    except Exception as e:
        error_msg = f"Unhandled exception in main: {e}\n{traceback.format_exc()}"
        print(error_msg)
        try:
            messagebox.showerror("Fatal Error", f"An unrecoverable error occurred: {e}")
        except:
            pass
        return 1


if __name__ == "__main__":
    sys.exit(main())
