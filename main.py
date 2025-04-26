import os
import sys
import core
import threading
import tkinter as tk
import traceback
import datetime
from tkinter import ttk, font, messagebox
from core import lock_keyboard, lock_mouse
from settings import open_config, save_config, get_theme_colors
import scheduler
from PIL import Image, ImageTk
import webbrowser
import sv_ttk
from ui_components import (
    ThemedFrame, ThemedButton, ThemedLabel, ThemedEntry, 
    ThemedCheckbutton, ResponsiveGrid, Card, Tooltip, 
    TabView, setup_theme, create_window, center_window
)

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
schedule_manager = None
app_icon = None


def initialize_app():
    """Initialize the application with configuration and error handling"""
    global config, current_theme, refresh_rate, COLORS, schedule_manager, root, app_icon, shortcut
    
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
        
        # Get theme colors and add necessary aliases
        COLORS = get_theme_colors(current_theme)
        # Add aliases for backward compatibility
        COLORS["bg"] = COLORS["background"]
        COLORS["text"] = COLORS["foreground"]
        COLORS["secondary"] = COLORS["label"]
        COLORS["light_text"] = COLORS["inactive"]
        COLORS["accent"] = COLORS.get("accent", "#4A6BFF")
        
        # Create the main window
        root = tk.Tk()
        root.title("KeyLock")
        
        # Initialize shortcut as StringVar
        shortcut = tk.StringVar(value=config.get("unlock", "ctrl+q"))
        
        # Load app icon
        try:
            app_icon_path = load_asset("lock_icon.png")
            app_icon = tk.PhotoImage(file=app_icon_path)
            root.iconphoto(True, app_icon)
        except Exception as e:
            print(f"Could not load application icon: {e}")
            app_icon = None
        
        # Initialize the scheduler
        schedule_manager = scheduler.ScheduleManager(
            lock_callback=lock_devices_by_type,
            unlock_callback=unlock_all_devices
        )
        schedule_manager.start()
        
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
    """Create the application UI elements"""
    global app_icon, root, key_lock_btn, mouse_lock_btn, key_block_on_min, window_transparency_var, status_var, footer, shortcut
    
    # Configure all styles
    configure_styles()
    
    # Create main container as a notebook with tabs
    main_frame = ttk.Notebook(root)
    main_frame.grid(row=0, column=0, sticky="nsew")
    
    # Make the root window responsive
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    
    # Create main tab
    main_tab = ttk.Frame(main_frame, padding="10")
    main_frame.add(main_tab, text="Main")
    main_tab.columnconfigure(0, weight=1)
    
    # Bind resize event to window
    root.bind("<Configure>", on_window_resize)
    
    # Title frame
    title_frame = ttk.Frame(main_tab)
    title_frame.grid(row=0, column=0, pady=(0, 10), sticky="ew")
    title_frame.columnconfigure(0, weight=1)
    
    # Application icon and title
    title_label = ttk.Label(
        title_frame, 
        text="KeyLock", 
        font=("Segoe UI", 16, "bold"),
        image=app_icon, 
        compound=tk.LEFT
    )
    title_label.grid(row=0, column=0, sticky="w", padx=5)
    
    # Buttons frame with responsive layout
    button_frame = ttk.Frame(main_tab)
    button_frame.grid(row=1, column=0, pady=10, sticky="ew")
    button_frame.columnconfigure(0, weight=1)
    button_frame.columnconfigure(1, weight=1)
    
    # Keyboard Lock button
    key_lock_btn = ttk.Button(
        button_frame,
        text="Lock Keyboard",
        command=toggle_keyboard_lock,
        style="LockButton.TButton",
        width=15
    )
    key_lock_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
    
    # Mouse Lock button
    mouse_lock_btn = ttk.Button(
        button_frame,
        text="Lock Mouse",
        command=toggle_mouse_lock,
        style="LockButton.TButton",
        width=15
    )
    mouse_lock_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
    
    # Options frame
    options_frame = ttk.LabelFrame(main_tab, text="Options", padding=10)
    options_frame.grid(row=2, column=0, pady=10, sticky="ew")
    options_frame.columnconfigure(0, weight=1)
    
    # Create status section on main tab
    status_frame = create_status_section(main_tab)
    
    # Create buttons section on main tab
    create_buttons_section(main_tab)
    
    # Create settings section on main tab
    create_settings_section(main_tab)
    
    # Create scheduler UI on scheduler tab
    scheduler_frame = tk.Frame(main_frame, bg=COLORS["bg"])
    main_frame.add(scheduler_frame, text="Scheduler")
    
    # Populate the scheduler tab
    create_scheduler_section(scheduler_frame)
    
    # Create footer
    footer = tk.Label(
        main_tab, 
        text="Press " + shortcut.get() + " to unlock", 
        bg=COLORS["bg"], 
        fg=COLORS["light_text"],
        pady=10
    )
    footer.grid(row=3, column=0, sticky="ew", pady=(0, 10))
    
    # Apply initial config settings
    apply_config_settings()
    
    # Make window resizable
    root.resizable(True, True)
    
    # Set minimum window size to prevent UI breaking on small sizes
    root.minsize(650, 550)
    
    # Center window on screen
    center_window(root, 800, 650)
    
    return True


def on_window_resize(event):
    """Handle window resize events to adjust UI components"""
    # Only respond if this is the root window being resized
    if event.widget == root:
        try:
            # Adjust font sizes based on window width
            window_width = event.width
            window_height = event.height
            
            # Scale font sizes based on window dimensions
            if window_width < 700:
                font_scale = 0.9
            elif window_width < 1000:
                font_scale = 1.0
            elif window_width < 1200:
                font_scale = 1.1
            else:
                font_scale = 1.2
                
            # Update styles with new scale
            update_font_sizes(font_scale)
            
            # Adjust padding and spacing based on window size
            if window_width < 800:
                compact_layout()
            else:
                spacious_layout()
                
        except Exception as e:
            print(f"Error handling resize: {e}")


def update_font_sizes(scale):
    """Update UI font sizes based on scale factor"""
    try:
        # Update default font
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(size=int(10 * scale))
        
        # Update text font
        text_font = font.nametofont("TkTextFont")
        text_font.configure(size=int(10 * scale))
        
        # Update fixed font
        fixed_font = font.nametofont("TkFixedFont")
        fixed_font.configure(size=int(9 * scale))
        
        # Update styles that need to be responsive
        style = ttk.Style()
        style.configure("TNotebook.Tab", font=("Segoe UI", int(10 * scale)))
        style.configure("TButton", font=("Segoe UI", int(10 * scale)))
        style.configure("Treeview.Heading", font=("Segoe UI", int(9 * scale), "bold"))
        style.configure("TLabelframe.Label", font=("Segoe UI", int(10 * scale), "bold"))
        
        # Update custom labels
        for widget in root.winfo_children():
            update_widget_fonts(widget, scale)
    except Exception as e:
        print(f"Error updating font sizes: {e}")


def update_widget_fonts(widget, scale):
    """Recursively update fonts for all widgets"""
    try:
        widget_class = widget.winfo_class()
        
        if widget_class in ("Label", "Button", "Checkbutton", "Radiobutton"):
            current_font = font.Font(font=widget["font"])
            new_size = int(current_font.actual()["size"] * scale / 10)
            if new_size < 8:
                new_size = 8  # Minimum readable size
            widget.configure(font=(current_font.actual()["family"], new_size, current_font.actual()["weight"]))
            
        # Process all children widgets
        for child in widget.winfo_children():
            update_widget_fonts(child, scale)
    except Exception as e:
        print(f"Error updating widget fonts: {e}")


def compact_layout():
    """Apply compact layout for smaller window sizes"""
    try:
        # Adjust padding for main container
        for widget in root.winfo_children():
            if widget.winfo_class() == "Frame":
                widget.grid_configure(padx=5, pady=5)
                
        # More compact button padding
        style = ttk.Style()
        style.configure("TButton", padding=5)
        
        # Adjust other widgets as needed
        for btn in root.winfo_children():
            if isinstance(btn, tk.Button):
                btn.configure(padx=5, pady=3)
    except Exception as e:
        print(f"Error applying compact layout: {e}")


def spacious_layout():
    """Apply spacious layout for larger window sizes"""
    try:
        # Adjust padding for main container
        for widget in root.winfo_children():
            if widget.winfo_class() == "Frame":
                widget.grid_configure(padx=10, pady=10)
                
        # More spacious button padding
        style = ttk.Style()
        style.configure("TButton", padding=10)
        
        # Adjust other widgets as needed
        for btn in root.winfo_children():
            if isinstance(btn, tk.Button):
                btn.configure(padx=10, pady=8)
    except Exception as e:
        print(f"Error applying spacious layout: {e}")


def configure_styles():
    """Configure the UI styles"""
    try:
        # Create custom styles
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(family="Segoe UI", size=10)
        root.option_add("*Font", default_font)
        
        # Configure ttk styles
        style = ttk.Style()
        
        # Configure the notebook tabs with modern styling
        style.configure("TNotebook", background=COLORS["bg"], borderwidth=0)
        style.configure("TNotebook.Tab", 
            background=COLORS["highlight"], 
            foreground=COLORS["text"],
            padding=(12, 6),
            borderwidth=0,
            font=("Segoe UI", 10)
        )
        style.map("TNotebook.Tab",
            background=[("selected", COLORS["accent"])],
            foreground=[("selected", "white")]
        )
        
        # Configure buttons
        style.configure("TButton", 
            background=COLORS["accent"], 
            foreground="white", 
            borderwidth=0,
            focuscolor=COLORS["accent"],
            padding=10,
            font=("Segoe UI", 10)
        )
        style.map("TButton",
            background=[("active", "#0069d9")],
            relief=[("pressed", "flat"), ("!pressed", "flat")]
        )
        
        # Configure entry fields
        style.configure("TEntry", 
            padding=8,
            fieldbackground=COLORS["highlight"],
            borderwidth=1,
        )
        
        # Configure treeview with enhanced styling
        style.configure("Treeview",
            background=COLORS["bg"],
            foreground=COLORS["text"],
            fieldbackground=COLORS["bg"],
            borderwidth=1,
            rowheight=28
        )
        style.map("Treeview",
            background=[("selected", COLORS["accent"])],
            foreground=[("selected", "white")]
        )
        style.configure("Treeview.Heading",
            background=COLORS["highlight"],
            foreground=COLORS["text"],
            padding=6,
            font=("Segoe UI", 9, "bold")
        )
        
        # Configure scrollbars
        style.configure("TScrollbar",
            background=COLORS["bg"],
            troughcolor=COLORS["highlight"],
            borderwidth=0,
            arrowcolor=COLORS["text"]
        )
        
        # Configure frames
        style.configure("TFrame",
            background=COLORS["bg"],
            borderwidth=0
        )
        
        # Configure labelframes
        style.configure("TLabelframe",
            background=COLORS["bg"],
            foreground=COLORS["text"],
            bordercolor=COLORS["border"],
            labeloutside="true",
            borderwidth=1
        )
        style.configure("TLabelframe.Label",
            background=COLORS["bg"],
            foreground=COLORS["text"],
            font=("Segoe UI", 10, "bold")
        )
        
        # Configure checkbuttons
        style.configure("TCheckbutton",
            background=COLORS["bg"],
            foreground=COLORS["text"]
        )
        style.map("TCheckbutton",
            background=[("active", COLORS["bg"])],
            foreground=[("active", COLORS["accent"])]
        )
        
    except Exception as e:
        print(f"Error configuring styles: {e}")


def create_header_section(parent):
    """Create the header section of the UI"""
    try:
        # Headers container
        header_frame = tk.Frame(parent, bg=COLORS["bg"], pady=15)
        header_frame.grid(row=0, column=0, sticky="ew")
        
        # Headers
        title_label = tk.Label(
            header_frame, 
            text="Keylock", 
            font=("Segoe UI", 18, "bold"), 
            bg=COLORS["bg"], 
            fg=COLORS["text"]
        )
        title_label.pack(pady=(0, 5))
        
        subtitle_label = tk.Label(
            header_frame, 
            text="Lock your keyboard and mouse with ease", 
            bg=COLORS["bg"], 
            fg=COLORS["light_text"],
            font=("Segoe UI", 10)
        )
        subtitle_label.pack()
    except Exception as e:
        print(f"Error creating header section: {e}")


def create_status_section(parent):
    """Create the status section of the UI with device status indicators"""
    global keyboard_img, mouse_img, keyboard_img_label, mouse_img_label, keyboard_status, mouse_status
    
    try:
        # Status frames
        status_frame = tk.Frame(parent, bg=COLORS["bg"], padx=20, pady=10)
        status_frame.grid(row=1, column=0, sticky="ew")
        
        # Configure status frame for responsive design
        status_frame.columnconfigure(0, weight=1)
        status_frame.columnconfigure(1, weight=1)
        
        # Device status displays
        keyboard_status_frame = tk.Frame(status_frame, bg=COLORS["bg"], padx=10, pady=10, 
                                         highlightbackground=COLORS["border"], highlightthickness=1)
        keyboard_status_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        mouse_status_frame = tk.Frame(status_frame, bg=COLORS["bg"], padx=10, pady=10,
                                      highlightbackground=COLORS["border"], highlightthickness=1)
        mouse_status_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        
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
        keyboard_label = tk.Label(keyboard_status_frame, text="Keyboard", 
                                 font=("Segoe UI", 11, "bold"),
                                 bg=COLORS["bg"], fg=COLORS["text"])
        keyboard_label.pack(pady=(0, 5))
        
        keyboard_img = keyboard_unlocked_image
        keyboard_img_label = tk.Label(keyboard_status_frame, image=keyboard_img, bg=COLORS["bg"])
        keyboard_img_label.pack(pady=5)
        
        keyboard_status = tk.Label(keyboard_status_frame, text="Unlocked", 
                                  bg=COLORS["highlight"], fg=COLORS["secondary"],
                                  width=15, pady=3)
        keyboard_status.pack(pady=(5, 0))
        
        # Mouse status
        mouse_label = tk.Label(mouse_status_frame, text="Mouse", 
                              font=("Segoe UI", 11, "bold"),
                              bg=COLORS["bg"], fg=COLORS["text"])
        mouse_label.pack(pady=(0, 5))
        
        mouse_img = mouse_unlocked_image
        mouse_img_label = tk.Label(mouse_status_frame, image=mouse_img, bg=COLORS["bg"])
        mouse_img_label.pack(pady=5)
        
        mouse_status = tk.Label(mouse_status_frame, text="Unlocked", 
                               bg=COLORS["highlight"], fg=COLORS["secondary"],
                               width=15, pady=3)
        mouse_status.pack(pady=(5, 0))
        
        return status_frame
    except Exception as e:
        print(f"Error creating status section: {e}")
        return None


def create_buttons_section(parent):
    """Create the buttons section of the UI"""
    try:
        # Buttons container
        buttons_container = tk.Frame(parent, bg=COLORS["bg"], pady=10)
        buttons_container.grid(row=2, column=0, sticky="ew", padx=20)
        
        # Configure for responsive design
        buttons_container.columnconfigure(0, weight=1)
        buttons_container.columnconfigure(1, weight=1)
        buttons_container.rowconfigure(0, weight=1)
        buttons_container.rowconfigure(1, weight=1)
        
        # Individual lock buttons in a row
        lock_keyboard_btn = tk.Button(
            buttons_container,
            text="Lock Keyboard",
            bg=COLORS["accent"],
            fg="white",
            relief="flat",
            borderwidth=0,
            pady=12,
            padx=10,
            cursor="hand2",
            font=("Segoe UI", 10, "bold"),
            activebackground="#0069d9",
            activeforeground="white",
            command=lambda: safe_lock_keyboard()
        )
        lock_keyboard_btn.grid(row=0, column=0, sticky="ew", padx=(0, 5), pady=(0, 5))
        
        lock_mouse_btn = tk.Button(
            buttons_container,
            text="Lock Mouse",
            bg=COLORS["accent"],
            fg="white",
            relief="flat",
            borderwidth=0,
            pady=12,
            padx=10,
            cursor="hand2",
            font=("Segoe UI", 10, "bold"),
            activebackground="#0069d9",
            activeforeground="white",
            command=lambda: safe_lock_mouse()
        )
        lock_mouse_btn.grid(row=0, column=1, sticky="ew", padx=(5, 0), pady=(0, 5))
        
        # Lock both button - spans both columns
        lock_both_btn = tk.Button(
            buttons_container,
            text="Lock Both",
            bg="#dc3545", # Red for emphasis
            fg="white",
            relief="flat",
            borderwidth=0,
            pady=12,
            cursor="hand2",
            font=("Segoe UI", 11, "bold"),
            activebackground="#c82333",
            activeforeground="white",
            command=lambda: safe_lock_both()
        )
        lock_both_btn.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(5, 0))
        
        # Add hover effect
        def on_enter(e, button, orig_color, hover_color):
            button['background'] = hover_color
            
        def on_leave(e, button, orig_color):
            button['background'] = orig_color
            
        lock_keyboard_btn.bind("<Enter>", lambda e: on_enter(e, lock_keyboard_btn, COLORS["accent"], "#0069d9"))
        lock_keyboard_btn.bind("<Leave>", lambda e: on_leave(e, lock_keyboard_btn, COLORS["accent"]))
        
        lock_mouse_btn.bind("<Enter>", lambda e: on_enter(e, lock_mouse_btn, COLORS["accent"], "#0069d9"))
        lock_mouse_btn.bind("<Leave>", lambda e: on_leave(e, lock_mouse_btn, COLORS["accent"]))
        
        lock_both_btn.bind("<Enter>", lambda e: on_enter(e, lock_both_btn, "#dc3545", "#c82333"))
        lock_both_btn.bind("<Leave>", lambda e: on_leave(e, lock_both_btn, "#dc3545"))
        
    except Exception as e:
        print(f"Error creating buttons section: {e}")


def create_settings_section(parent):
    """Create the settings section of the UI"""
    global shortcut
    
    try:
        # Settings container
        settings_container = tk.LabelFrame(
            parent, 
            text="Settings", 
            bg=COLORS["bg"], 
            fg=COLORS["text"], 
            font=("Segoe UI", 11, "bold"),
            padx=10, 
            pady=10
        )
        settings_container.grid(row=3, column=0, sticky="ew", padx=20, pady=10)
        
        # Configure for responsive design
        settings_container.columnconfigure(0, weight=3)
        settings_container.columnconfigure(1, weight=7)
        
        # Shortcut settings
        shortcut_label = tk.Label(
            settings_container, 
            text="Unlock Shortcut:", 
            bg=COLORS["bg"], 
            fg=COLORS["text"],
            anchor="w"
        )
        shortcut_label.grid(row=0, column=0, sticky="w", pady=(0, 10))
        
        shortcut_frame = tk.Frame(settings_container, bg=COLORS["bg"])
        shortcut_frame.grid(row=0, column=1, sticky="ew", pady=(0, 10))
        shortcut_frame.columnconfigure(0, weight=1)
        
        # Shortcut entry with modern styling
        shortcut = tk.Entry(
            shortcut_frame,
            bg=COLORS["highlight"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief="solid",
            borderwidth=1,
            highlightthickness=0,
            font=("Segoe UI", 10)
        )
        shortcut.grid(row=0, column=0, sticky="ew", ipady=5)
        
        # Theme label
        theme_label = tk.Label(
            settings_container, 
            text="UI Theme:", 
            bg=COLORS["bg"], 
            fg=COLORS["text"],
            anchor="w"
        )
        theme_label.grid(row=1, column=0, sticky="w")
        
        # Theme selection frame
        theme_frame = tk.Frame(settings_container, bg=COLORS["bg"])
        theme_frame.grid(row=1, column=1, sticky="ew")
        theme_frame.columnconfigure(0, weight=1)
        theme_frame.columnconfigure(1, weight=1)
        theme_frame.columnconfigure(2, weight=1)
        
        # Theme selection
        theme_var = tk.StringVar(value=current_theme)
        
        # Custom radio button style
        light_frame = tk.Frame(theme_frame, bg=COLORS["bg"], padx=5, pady=5)
        light_frame.grid(row=0, column=0, sticky="w")
        
        light_radio = tk.Radiobutton(
            light_frame, 
            text="Light", 
            variable=theme_var, 
            value="light", 
            bg=COLORS["bg"],
            fg=COLORS["text"],
            selectcolor=COLORS["highlight"],
            activebackground=COLORS["bg"],
            activeforeground=COLORS["text"],
            font=("Segoe UI", 10)
        )
        light_radio.pack()
        
        dark_frame = tk.Frame(theme_frame, bg=COLORS["bg"], padx=5, pady=5)
        dark_frame.grid(row=0, column=1, sticky="w")
        
        dark_radio = tk.Radiobutton(
            dark_frame, 
            text="Dark", 
            variable=theme_var, 
            value="dark", 
            bg=COLORS["bg"],
            fg=COLORS["text"],
            selectcolor=COLORS["highlight"],
            activebackground=COLORS["bg"],
            activeforeground=COLORS["text"],
            font=("Segoe UI", 10)
        )
        dark_radio.pack()
        
        apply_theme_btn = tk.Button(
            theme_frame,
            text="Apply",
            bg=COLORS["accent"],
            fg="white",
            relief="flat",
            borderwidth=0,
            padx=15,
            pady=2,
            cursor="hand2",
            font=("Segoe UI", 9),
            activebackground="#0069d9",
            activeforeground="white",
            command=lambda: apply_theme(theme_var.get())
        )
        apply_theme_btn.grid(row=0, column=2, sticky="e")
        
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
            keyboard_status.configure(text="Locked", fg="white", bg="#dc3545")
        else:
            keyboard_img = tk.PhotoImage(file=load_asset("keyboard_unlocked.png"))
            keyboard_img_label.configure(image=keyboard_img)
            keyboard_status.configure(text="Unlocked", fg=COLORS["secondary"], bg=COLORS["highlight"])
    except Exception as e:
        print(f"Error updating keyboard status: {e}")


def update_mouse():
    """Update mouse lock status display"""
    try:
        global mouse_img
        if core.mouse_locked:
            mouse_img = tk.PhotoImage(file=load_asset("mouse_locked.png"))
            mouse_img_label.configure(image=mouse_img)
            mouse_status.configure(text="Locked", fg="white", bg="#dc3545")
        else:
            mouse_img = tk.PhotoImage(file=load_asset("mouse_unlocked.png"))
            mouse_img_label.configure(image=mouse_img)
            mouse_status.configure(text="Unlocked", fg=COLORS["secondary"], bg=COLORS["highlight"])
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


def toggle_keyboard_lock():
    """Toggle keyboard lock state"""
    try:
        if core.keyboard_locked:
            core.stop_keyboard()
        else:
            lock_keyboard(shortcut.get())
        update_keyboard()
    except Exception as e:
        messagebox.showerror("Lock Error", f"Failed to toggle keyboard lock: {e}")


def toggle_mouse_lock():
    """Toggle mouse lock state"""
    try:
        if core.mouse_locked:
            core.stop_mouse()
        else:
            lock_mouse(shortcut.get())
        update_mouse()
    except Exception as e:
        messagebox.showerror("Lock Error", f"Failed to toggle mouse lock: {e}")


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
    global footer
    try:
        if footer is not None:
            footer.configure(text="Press " + shortcut.get() + " to unlock")
        root.after(1000, update_footer)
    except Exception as e:
        print(f"Error updating footer: {e}")
        # Try to reschedule
        try:
            root.after(1000, update_footer)
        except:
            pass


def lock_devices_by_type(action_type):
    """
    Lock devices based on action type for scheduler
    
    Args:
        action_type (str): 'keyboard', 'mouse', or 'both'
    """
    try:
        shortcut_val = shortcut.get() if shortcut else "ctrl+q"
        
        if action_type == "keyboard":
            lock_keyboard(shortcut_val)
            update_keyboard()
        elif action_type == "mouse":
            lock_mouse(shortcut_val)
            update_mouse()
        elif action_type == "both":
            lock_keyboard(shortcut_val)
            lock_mouse(shortcut_val)
            update_keyboard()
            update_mouse()
    except Exception as e:
        print(f"Error in lock_devices_by_type: {e}")


def unlock_all_devices():
    """Unlock all devices for scheduler"""
    try:
        if core.keyboard_locked:
            core.stop_keyboard()
            update_keyboard()
        
        if core.mouse_locked:
            core.stop_mouse()
            update_mouse()
    except Exception as e:
        print(f"Error in unlock_all_devices: {e}")


def create_scheduler_section(parent):
    """Create the scheduler UI section"""
    try:
        # Header
        scheduler_header = tk.Label(
            parent, 
            text="Scheduled Locking", 
            font=("Segoe UI", 16, "bold"), 
            bg=COLORS["bg"], 
            fg=COLORS["text"]
        )
        scheduler_header.grid(row=0, column=0, sticky="w", padx=20, pady=(15, 10))
        
        # Schedules list frame
        schedules_frame = tk.Frame(parent, bg=COLORS["bg"])
        schedules_frame.grid(row=1, column=0, sticky="nsew", padx=20)
        
        # Configure for responsive layout
        schedules_frame.columnconfigure(0, weight=1)
        schedules_frame.rowconfigure(0, weight=1)
        
        # Create a treeview for schedules with modern styling
        columns = ("name", "type", "action", "time", "duration", "enabled")
        schedule_tree = ttk.Treeview(
            schedules_frame, 
            columns=columns, 
            show="headings", 
            height=6,
            style="Treeview"
        )
        
        # Define headings
        schedule_tree.heading("name", text="Name")
        schedule_tree.heading("type", text="Schedule Type")
        schedule_tree.heading("action", text="Action")
        schedule_tree.heading("time", text="Time")
        schedule_tree.heading("duration", text="Duration")
        schedule_tree.heading("enabled", text="Status")
        
        # Define columns
        schedule_tree.column("name", width=120, minwidth=100)
        schedule_tree.column("type", width=100, minwidth=80)
        schedule_tree.column("action", width=80, minwidth=60)
        schedule_tree.column("time", width=100, minwidth=80)
        schedule_tree.column("duration", width=80, minwidth=60)
        schedule_tree.column("enabled", width=60, minwidth=50)
        
        # Add schedules to the treeview
        for schedule in schedule_manager.get_schedules():
            add_schedule_to_tree(schedule_tree, schedule)
        
        # Add scrollbar with modern styling
        scrollbar = ttk.Scrollbar(schedules_frame, orient="vertical", command=schedule_tree.yview)
        schedule_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")
        schedule_tree.grid(row=0, column=0, sticky="nsew")
        
        # Buttons frame with responsive layout
        buttons_frame = tk.Frame(parent, bg=COLORS["bg"])
        buttons_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        
        # Configure for responsive design
        buttons_frame.columnconfigure(0, weight=1)
        buttons_frame.columnconfigure(1, weight=1)
        buttons_frame.columnconfigure(2, weight=1)
        
        # Buttons with enhanced styling
        add_button = tk.Button(
            buttons_frame,
            text="Add Schedule",
            bg=COLORS["accent"],
            fg="white",
            relief="flat",
            borderwidth=0,
            padx=15,
            pady=8,
            font=("Segoe UI", 10),
            cursor="hand2",
            activebackground="#0069d9",
            activeforeground="white",
            command=lambda: show_add_schedule_dialog(schedule_tree)
        )
        add_button.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        edit_button = tk.Button(
            buttons_frame,
            text="Edit",
            bg=COLORS["accent"],
            fg="white",
            relief="flat",
            borderwidth=0,
            padx=15,
            pady=8,
            font=("Segoe UI", 10),
            cursor="hand2",
            activebackground="#0069d9",
            activeforeground="white",
            command=lambda: edit_selected_schedule(schedule_tree)
        )
        edit_button.grid(row=0, column=1, sticky="ew", padx=5)
        
        delete_button = tk.Button(
            buttons_frame,
            text="Delete",
            bg="#dc3545",
            fg="white",
            relief="flat",
            borderwidth=0,
            padx=15,
            pady=8,
            font=("Segoe UI", 10),
            cursor="hand2",
            activebackground="#c82333",
            activeforeground="white",
            command=lambda: delete_selected_schedule(schedule_tree)
        )
        delete_button.grid(row=0, column=2, sticky="ew", padx=(5, 0))
        
        # Add hover effects for buttons
        def on_enter(e, button, orig_color, hover_color):
            button['background'] = hover_color
            
        def on_leave(e, button, orig_color):
            button['background'] = orig_color
            
        add_button.bind("<Enter>", lambda e: on_enter(e, add_button, COLORS["accent"], "#0069d9"))
        add_button.bind("<Leave>", lambda e: on_leave(e, add_button, COLORS["accent"]))
        
        edit_button.bind("<Enter>", lambda e: on_enter(e, edit_button, COLORS["accent"], "#0069d9"))
        edit_button.bind("<Leave>", lambda e: on_leave(e, edit_button, COLORS["accent"]))
        
        delete_button.bind("<Enter>", lambda e: on_enter(e, delete_button, "#dc3545", "#c82333"))
        delete_button.bind("<Leave>", lambda e: on_leave(e, delete_button, "#dc3545"))
        
        # Add a countdown timer section with enhanced styling
        countdown_frame = tk.LabelFrame(
            parent, 
            text="Quick Countdown Timer", 
            bg=COLORS["bg"], 
            fg=COLORS["text"],
            font=("Segoe UI", 11, "bold"),
            padx=15, 
            pady=15
        )
        countdown_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=10)
        
        # Make countdown frame responsive
        countdown_frame.columnconfigure(0, weight=1)
        countdown_frame.columnconfigure(1, weight=2)
        countdown_frame.columnconfigure(2, weight=3)
        
        # Minutes entry with better styling
        minutes_frame = tk.Frame(countdown_frame, bg=COLORS["bg"])
        minutes_frame.grid(row=0, column=0, sticky="w")
        
        minutes_label = tk.Label(
            minutes_frame, 
            text="Minutes:", 
            bg=COLORS["bg"], 
            fg=COLORS["text"],
            font=("Segoe UI", 10)
        )
        minutes_label.pack(side="left", padx=(0, 5))
        
        minutes_var = tk.StringVar(value="5")
        minutes_entry = tk.Spinbox(
            minutes_frame,
            from_=1,
            to=60,
            width=3,
            textvariable=minutes_var,
            bg=COLORS["highlight"],
            fg=COLORS["text"],
            font=("Segoe UI", 10),
            buttonbackground=COLORS["highlight"]
        )
        minutes_entry.pack(side="left")
        
        # Lock type options with improved layout
        lock_type_frame = tk.Frame(countdown_frame, bg=COLORS["bg"])
        lock_type_frame.grid(row=0, column=1, sticky="w", padx=15)
        
        lock_type_var = tk.StringVar(value="both")
        
        # Use custom radio button style
        keyboard_radio = tk.Radiobutton(
            lock_type_frame,
            text="Keyboard",
            variable=lock_type_var,
            value="keyboard",
            bg=COLORS["bg"],
            fg=COLORS["text"],
            selectcolor=COLORS["highlight"],
            font=("Segoe UI", 10)
        )
        keyboard_radio.pack(side="left", padx=(0, 10))
        
        mouse_radio = tk.Radiobutton(
            lock_type_frame,
            text="Mouse",
            variable=lock_type_var,
            value="mouse",
            bg=COLORS["bg"],
            fg=COLORS["text"],
            selectcolor=COLORS["highlight"],
            font=("Segoe UI", 10)
        )
        mouse_radio.pack(side="left", padx=(0, 10))
        
        both_radio = tk.Radiobutton(
            lock_type_frame,
            text="Both",
            variable=lock_type_var,
            value="both",
            bg=COLORS["bg"],
            fg=COLORS["text"],
            selectcolor=COLORS["highlight"],
            font=("Segoe UI", 10)
        )
        both_radio.pack(side="left")
        
        # Start button with enhanced styling
        start_button = tk.Button(
            countdown_frame,
            text="Start Countdown",
            bg=COLORS["accent"],
            fg="white",
            relief="flat",
            borderwidth=0,
            padx=15,
            pady=8,
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
            activebackground="#0069d9",
            activeforeground="white",
            command=lambda: start_countdown(minutes_var.get(), lock_type_var.get())
        )
        start_button.grid(row=0, column=2, sticky="e")
        
        # Add hover effect
        start_button.bind("<Enter>", lambda e: on_enter(e, start_button, COLORS["accent"], "#0069d9"))
        start_button.bind("<Leave>", lambda e: on_leave(e, start_button, COLORS["accent"]))
        
        # Refresh schedule list periodically
        def refresh_schedule_list():
            update_schedule_tree(schedule_tree)
            parent.after(5000, refresh_schedule_list)
            
        parent.after(5000, refresh_schedule_list)
        
    except Exception as e:
        print(f"Error creating scheduler section: {e}\n{traceback.format_exc()}")


def add_schedule_to_tree(tree, schedule):
    """Add a schedule to the treeview"""
    try:
        # Format time display
        if schedule.time_type == 'countdown':
            time_str = f"{schedule.start_time} seconds"
        elif schedule.time_type == 'once':
            if isinstance(schedule.start_time, datetime.datetime):
                time_str = schedule.start_time.strftime("%Y-%m-%d %H:%M")
            else:
                time_str = str(schedule.start_time)
        else:
            if isinstance(schedule.start_time, datetime.time):
                time_str = schedule.start_time.strftime("%H:%M")
            else:
                time_str = str(schedule.start_time)
        
        # Format duration
        if schedule.duration is None:
            duration_str = "Indefinite"
        else:
            minutes = schedule.duration // 60
            if minutes < 60:
                duration_str = f"{minutes} min"
            else:
                hours = minutes // 60
                mins = minutes % 60
                duration_str = f"{hours}h {mins}m"
        
        # Format schedule type
        type_map = {
            'once': 'One-time',
            'daily': 'Daily',
            'weekdays': 'Weekdays',
            'weekends': 'Weekends',
            'countdown': 'Countdown'
        }
        type_str = type_map.get(schedule.time_type, schedule.time_type)
        
        # Format action
        action_map = {
            'keyboard': 'Keyboard',
            'mouse': 'Mouse',
            'both': 'Both'
        }
        action_str = action_map.get(schedule.action, schedule.action)
        
        # Format enabled status
        enabled_str = "Enabled" if schedule.enabled else "Disabled"
        
        # Insert into tree
        tree.insert(
            "", 
            "end", 
            iid=schedule.id,
            values=(schedule.name, type_str, action_str, time_str, duration_str, enabled_str)
        )
    except Exception as e:
        print(f"Error adding schedule to tree: {e}")


def update_schedule_tree(tree):
    """Update the schedule treeview with current schedules"""
    try:
        # Clear current items
        for item in tree.get_children():
            tree.delete(item)
        
        # Add all schedules
        for schedule in schedule_manager.get_schedules():
            add_schedule_to_tree(tree, schedule)
    except Exception as e:
        print(f"Error updating schedule tree: {e}")


def show_add_schedule_dialog(tree):
    """Show dialog to add a new schedule"""
    try:
        dialog = tk.Toplevel(root)
        dialog.title("Add Schedule")
        dialog.geometry("400x500")
        dialog.configure(bg=COLORS["bg"])
        dialog.transient(root)
        dialog.grab_set()
        
        # Name frame
        name_frame = tk.Frame(dialog, bg=COLORS["bg"], pady=5)
        name_frame.pack(fill="x", padx=20)
        
        name_label = tk.Label(name_frame, text="Schedule Name:", bg=COLORS["bg"], fg=COLORS["text"])
        name_label.pack(side="left")
        
        name_var = tk.StringVar()
        name_entry = tk.Entry(
            name_frame,
            textvariable=name_var,
            bg=COLORS["highlight"],
            fg=COLORS["text"],
            width=25
        )
        name_entry.pack(side="right")
        
        # Schedule type frame
        type_frame = tk.LabelFrame(dialog, text="Schedule Type", bg=COLORS["bg"], fg=COLORS["text"], pady=10)
        type_frame.pack(fill="x", padx=20, pady=10)
        
        type_var = tk.StringVar(value="once")
        
        once_radio = tk.Radiobutton(
            type_frame,
            text="One-time",
            variable=type_var,
            value="once",
            bg=COLORS["bg"],
            fg=COLORS["text"],
            selectcolor=COLORS["highlight"],
            command=lambda: toggle_date_time_fields(type_var.get(), date_frame, weekday_frame)
        )
        once_radio.pack(anchor="w")
        
        daily_radio = tk.Radiobutton(
            type_frame,
            text="Daily",
            variable=type_var,
            value="daily",
            bg=COLORS["bg"],
            fg=COLORS["text"],
            selectcolor=COLORS["highlight"],
            command=lambda: toggle_date_time_fields(type_var.get(), date_frame, weekday_frame)
        )
        daily_radio.pack(anchor="w")
        
        weekdays_radio = tk.Radiobutton(
            type_frame,
            text="Weekdays (Mon-Fri)",
            variable=type_var,
            value="weekdays",
            bg=COLORS["bg"],
            fg=COLORS["text"],
            selectcolor=COLORS["highlight"],
            command=lambda: toggle_date_time_fields(type_var.get(), date_frame, weekday_frame)
        )
        weekdays_radio.pack(anchor="w")
        
        weekends_radio = tk.Radiobutton(
            type_frame,
            text="Weekends (Sat-Sun)",
            variable=type_var,
            value="weekends",
            bg=COLORS["bg"],
            fg=COLORS["text"],
            selectcolor=COLORS["highlight"],
            command=lambda: toggle_date_time_fields(type_var.get(), date_frame, weekday_frame)
        )
        weekends_radio.pack(anchor="w")
        
        # Date frame (for one-time schedule)
        date_frame = tk.Frame(dialog, bg=COLORS["bg"], pady=5)
        date_frame.pack(fill="x", padx=20, pady=5)
        
        date_label = tk.Label(date_frame, text="Date (YYYY-MM-DD):", bg=COLORS["bg"], fg=COLORS["text"])
        date_label.pack(side="left")
        
        date_var = tk.StringVar(value=datetime.datetime.now().strftime("%Y-%m-%d"))
        date_entry = tk.Entry(
            date_frame,
            textvariable=date_var,
            bg=COLORS["highlight"],
            fg=COLORS["text"],
            width=15
        )
        date_entry.pack(side="right")
        
        # Weekday selection frame (hidden initially)
        weekday_frame = tk.Frame(dialog, bg=COLORS["bg"], pady=5)
        # Not packing yet - will be shown/hidden based on schedule type
        
        weekday_label = tk.Label(weekday_frame, text="Select Days:", bg=COLORS["bg"], fg=COLORS["text"])
        weekday_label.pack(side="left")
        
        weekday_vars = [tk.BooleanVar(value=False) for _ in range(7)]
        weekday_checks = []
        weekday_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        
        days_frame = tk.Frame(weekday_frame, bg=COLORS["bg"])
        days_frame.pack(side="right")
        
        for i, day in enumerate(weekday_names):
            check = tk.Checkbutton(
                days_frame,
                text=day,
                variable=weekday_vars[i],
                bg=COLORS["bg"],
                fg=COLORS["text"],
                selectcolor=COLORS["highlight"]
            )
            check.pack(side="left")
            weekday_checks.append(check)
        
        # Time frame
        time_frame = tk.Frame(dialog, bg=COLORS["bg"], pady=5)
        time_frame.pack(fill="x", padx=20, pady=5)
        
        time_label = tk.Label(time_frame, text="Time (HH:MM):", bg=COLORS["bg"], fg=COLORS["text"])
        time_label.pack(side="left")
        
        time_var = tk.StringVar(value=datetime.datetime.now().strftime("%H:%M"))
        time_entry = tk.Entry(
            time_frame,
            textvariable=time_var,
            bg=COLORS["highlight"],
            fg=COLORS["text"],
            width=10
        )
        time_entry.pack(side="right")
        
        # Action frame
        action_frame = tk.LabelFrame(dialog, text="Lock Action", bg=COLORS["bg"], fg=COLORS["text"], pady=10)
        action_frame.pack(fill="x", padx=20, pady=10)
        
        action_var = tk.StringVar(value="both")
        
        keyboard_radio = tk.Radiobutton(
            action_frame,
            text="Keyboard",
            variable=action_var,
            value="keyboard",
            bg=COLORS["bg"],
            fg=COLORS["text"],
            selectcolor=COLORS["highlight"]
        )
        keyboard_radio.pack(anchor="w")
        
        mouse_radio = tk.Radiobutton(
            action_frame,
            text="Mouse",
            variable=action_var,
            value="mouse",
            bg=COLORS["bg"],
            fg=COLORS["text"],
            selectcolor=COLORS["highlight"]
        )
        mouse_radio.pack(anchor="w")
        
        both_radio = tk.Radiobutton(
            action_frame,
            text="Both",
            variable=action_var,
            value="both",
            bg=COLORS["bg"],
            fg=COLORS["text"],
            selectcolor=COLORS["highlight"]
        )
        both_radio.pack(anchor="w")
        
        # Duration frame
        duration_frame = tk.Frame(dialog, bg=COLORS["bg"], pady=5)
        duration_frame.pack(fill="x", padx=20, pady=5)
        
        duration_label = tk.Label(duration_frame, text="Duration (minutes, 0 for indefinite):", bg=COLORS["bg"], fg=COLORS["text"])
        duration_label.pack(side="left")
        
        duration_var = tk.StringVar(value="0")
        duration_entry = tk.Entry(
            duration_frame,
            textvariable=duration_var,
            bg=COLORS["highlight"],
            fg=COLORS["text"],
            width=5
        )
        duration_entry.pack(side="right")
        
        # Buttons frame
        buttons_frame = tk.Frame(dialog, bg=COLORS["bg"], pady=10)
        buttons_frame.pack(fill="x", padx=20, pady=10)
        
        cancel_button = tk.Button(
            buttons_frame,
            text="Cancel",
            bg=COLORS["secondary"],
            fg="white",
            relief="flat",
            borderwidth=0,
            padx=10,
            pady=5,
            command=dialog.destroy
        )
        cancel_button.pack(side="left", padx=(0, 10))
        
        save_button = tk.Button(
            buttons_frame,
            text="Save",
            bg=COLORS["accent"],
            fg="white",
            relief="flat",
            borderwidth=0,
            padx=10,
            pady=5,
            command=lambda: save_schedule(
                dialog, tree, None, name_var.get(), type_var.get(), action_var.get(),
                date_var.get(), time_var.get(), weekday_vars, duration_var.get()
            )
        )
        save_button.pack(side="right")
        
        # Show/hide relevant fields based on initial selection
        toggle_date_time_fields(type_var.get(), date_frame, weekday_frame)
        
    except Exception as e:
        print(f"Error showing add schedule dialog: {e}\n{traceback.format_exc()}")


def toggle_date_time_fields(schedule_type, date_frame, weekday_frame):
    """Show/hide date and weekday fields based on schedule type"""
    try:
        if schedule_type == "once":
            date_frame.pack(fill="x", padx=20, pady=5)
            weekday_frame.pack_forget()
        elif schedule_type == "weekly":
            date_frame.pack_forget()
            weekday_frame.pack(fill="x", padx=20, pady=5)
        else:
            date_frame.pack_forget()
            weekday_frame.pack_forget()
    except Exception as e:
        print(f"Error toggling date/time fields: {e}")


def save_schedule(dialog, tree, schedule_id, name, schedule_type, action_type,
                 date_str, time_str, weekday_vars=None, duration_str="0"):
    """Save a new or edited schedule"""
    try:
        if not name:
            messagebox.showerror("Error", "Please enter a name for the schedule")
            return
        
        # Parse time
        try:
            hour, minute = map(int, time_str.split(":"))
            time_obj = datetime.time(hour, minute)
        except ValueError:
            messagebox.showerror("Error", "Invalid time format. Please use HH:MM")
            return
        
        # Parse duration
        try:
            duration_minutes = int(duration_str)
            duration = duration_minutes * 60 if duration_minutes > 0 else None
        except ValueError:
            messagebox.showerror("Error", "Duration must be a number")
            return
        
        # Create the schedule object
        if schedule_type == "once":
            # Parse date for one-time schedule
            try:
                year, month, day = map(int, date_str.split("-"))
                date_obj = datetime.date(year, month, day)
                # Combine date and time
                start_time = datetime.datetime.combine(date_obj, time_obj)
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD")
                return
        else:
            # For recurring schedules, just use the time
            start_time = time_obj
        
        # Get selected weekdays for weekly schedule
        selected_days = []
        if weekday_vars:
            selected_days = [i for i, var in enumerate(weekday_vars) if var.get()]
        
        # Create or update the schedule
        if schedule_id is None:
            # Create new schedule
            schedule_id = scheduler.generate_id()
            schedule = scheduler.Schedule(
                id=schedule_id,
                name=name,
                action=action_type,
                time_type=schedule_type,
                start_time=start_time,
                days=selected_days,
                duration=duration,
                enabled=True
            )
            schedule_manager.add_schedule(schedule)
        else:
            # Update existing schedule
            schedule = scheduler.Schedule(
                id=schedule_id,
                name=name,
                action=action_type,
                time_type=schedule_type,
                start_time=start_time,
                days=selected_days,
                duration=duration,
                enabled=True
            )
            schedule_manager.update_schedule(schedule)
        
        # Update the treeview
        update_schedule_tree(tree)
        
        # Close the dialog
        dialog.destroy()
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save schedule: {e}")
        print(f"Error saving schedule: {e}\n{traceback.format_exc()}")


def edit_selected_schedule(tree):
    """Edit the selected schedule"""
    try:
        selected = tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select a schedule to edit")
            return
        
        schedule_id = selected[0]
        schedule = schedule_manager.get_schedule(schedule_id)
        
        if not schedule:
            messagebox.showerror("Error", "Schedule not found")
            return
        
        # Show edit dialog
        show_edit_schedule_dialog(tree, schedule)
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to edit schedule: {e}")
        print(f"Error editing schedule: {e}\n{traceback.format_exc()}")


def show_edit_schedule_dialog(tree, schedule):
    """Show dialog to edit an existing schedule"""
    try:
        dialog = tk.Toplevel(root)
        dialog.title("Edit Schedule")
        dialog.geometry("400x500")
        dialog.configure(bg=COLORS["bg"])
        dialog.transient(root)
        dialog.grab_set()
        
        # Name frame
        name_frame = tk.Frame(dialog, bg=COLORS["bg"], pady=5)
        name_frame.pack(fill="x", padx=20)
        
        name_label = tk.Label(name_frame, text="Schedule Name:", bg=COLORS["bg"], fg=COLORS["text"])
        name_label.pack(side="left")
        
        name_var = tk.StringVar(value=schedule.name)
        name_entry = tk.Entry(
            name_frame,
            textvariable=name_var,
            bg=COLORS["highlight"],
            fg=COLORS["text"],
            width=25
        )
        name_entry.pack(side="right")
        
        # Schedule type frame
        type_frame = tk.LabelFrame(dialog, text="Schedule Type", bg=COLORS["bg"], fg=COLORS["text"], pady=10)
        type_frame.pack(fill="x", padx=20, pady=10)
        
        type_var = tk.StringVar(value=schedule.time_type)
        
        once_radio = tk.Radiobutton(
            type_frame,
            text="One-time",
            variable=type_var,
            value="once",
            bg=COLORS["bg"],
            fg=COLORS["text"],
            selectcolor=COLORS["highlight"],
            command=lambda: toggle_date_time_fields(type_var.get(), date_frame, weekday_frame)
        )
        once_radio.pack(anchor="w")
        
        daily_radio = tk.Radiobutton(
            type_frame,
            text="Daily",
            variable=type_var,
            value="daily",
            bg=COLORS["bg"],
            fg=COLORS["text"],
            selectcolor=COLORS["highlight"],
            command=lambda: toggle_date_time_fields(type_var.get(), date_frame, weekday_frame)
        )
        daily_radio.pack(anchor="w")
        
        weekdays_radio = tk.Radiobutton(
            type_frame,
            text="Weekdays (Mon-Fri)",
            variable=type_var,
            value="weekdays",
            bg=COLORS["bg"],
            fg=COLORS["text"],
            selectcolor=COLORS["highlight"],
            command=lambda: toggle_date_time_fields(type_var.get(), date_frame, weekday_frame)
        )
        weekdays_radio.pack(anchor="w")
        
        weekends_radio = tk.Radiobutton(
            type_frame,
            text="Weekends (Sat-Sun)",
            variable=type_var,
            value="weekends",
            bg=COLORS["bg"],
            fg=COLORS["text"],
            selectcolor=COLORS["highlight"],
            command=lambda: toggle_date_time_fields(type_var.get(), date_frame, weekday_frame)
        )
        weekends_radio.pack(anchor="w")
        
        # Date frame (for one-time schedule)
        date_frame = tk.Frame(dialog, bg=COLORS["bg"], pady=5)
        
        date_label = tk.Label(date_frame, text="Date (YYYY-MM-DD):", bg=COLORS["bg"], fg=COLORS["text"])
        date_label.pack(side="left")
        
        # Get date string from schedule if it's a datetime
        date_str = ""
        if schedule.time_type == "once" and isinstance(schedule.start_time, datetime.datetime):
            date_str = schedule.start_time.strftime("%Y-%m-%d")
        else:
            date_str = datetime.datetime.now().strftime("%Y-%m-%d")
            
        date_var = tk.StringVar(value=date_str)
        date_entry = tk.Entry(
            date_frame,
            textvariable=date_var,
            bg=COLORS["highlight"],
            fg=COLORS["text"],
            width=15
        )
        date_entry.pack(side="right")
        
        # Weekday selection frame
        weekday_frame = tk.Frame(dialog, bg=COLORS["bg"], pady=5)
        
        weekday_label = tk.Label(weekday_frame, text="Select Days:", bg=COLORS["bg"], fg=COLORS["text"])
        weekday_label.pack(side="left")
        
        weekday_vars = [tk.BooleanVar(value=(i in schedule.days)) for i in range(7)]
        weekday_checks = []
        weekday_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        
        days_frame = tk.Frame(weekday_frame, bg=COLORS["bg"])
        days_frame.pack(side="right")
        
        for i, day in enumerate(weekday_names):
            check = tk.Checkbutton(
                days_frame,
                text=day,
                variable=weekday_vars[i],
                bg=COLORS["bg"],
                fg=COLORS["text"],
                selectcolor=COLORS["highlight"]
            )
            check.pack(side="left")
            weekday_checks.append(check)
        
        # Time frame
        time_frame = tk.Frame(dialog, bg=COLORS["bg"], pady=5)
        time_frame.pack(fill="x", padx=20, pady=5)
        
        time_label = tk.Label(time_frame, text="Time (HH:MM):", bg=COLORS["bg"], fg=COLORS["text"])
        time_label.pack(side="left")
        
        # Get time string from schedule
        time_str = ""
        if isinstance(schedule.start_time, datetime.time):
            time_str = schedule.start_time.strftime("%H:%M")
        elif isinstance(schedule.start_time, datetime.datetime):
            time_str = schedule.start_time.strftime("%H:%M")
        else:
            time_str = datetime.datetime.now().strftime("%H:%M")
            
        time_var = tk.StringVar(value=time_str)
        time_entry = tk.Entry(
            time_frame,
            textvariable=time_var,
            bg=COLORS["highlight"],
            fg=COLORS["text"],
            width=10
        )
        time_entry.pack(side="right")
        
        # Action frame
        action_frame = tk.LabelFrame(dialog, text="Lock Action", bg=COLORS["bg"], fg=COLORS["text"], pady=10)
        action_frame.pack(fill="x", padx=20, pady=10)
        
        action_var = tk.StringVar(value=schedule.action)
        
        keyboard_radio = tk.Radiobutton(
            action_frame,
            text="Keyboard",
            variable=action_var,
            value="keyboard",
            bg=COLORS["bg"],
            fg=COLORS["text"],
            selectcolor=COLORS["highlight"]
        )
        keyboard_radio.pack(anchor="w")
        
        mouse_radio = tk.Radiobutton(
            action_frame,
            text="Mouse",
            variable=action_var,
            value="mouse",
            bg=COLORS["bg"],
            fg=COLORS["text"],
            selectcolor=COLORS["highlight"]
        )
        mouse_radio.pack(anchor="w")
        
        both_radio = tk.Radiobutton(
            action_frame,
            text="Both",
            variable=action_var,
            value="both",
            bg=COLORS["bg"],
            fg=COLORS["text"],
            selectcolor=COLORS["highlight"]
        )
        both_radio.pack(anchor="w")
        
        # Duration frame
        duration_frame = tk.Frame(dialog, bg=COLORS["bg"], pady=5)
        duration_frame.pack(fill="x", padx=20, pady=5)
        
        duration_label = tk.Label(duration_frame, text="Duration (minutes, 0 for indefinite):", bg=COLORS["bg"], fg=COLORS["text"])
        duration_label.pack(side="left")
        
        # Get duration in minutes
        duration_min = 0
        if schedule.duration is not None:
            duration_min = schedule.duration // 60
            
        duration_var = tk.StringVar(value=str(duration_min))
        duration_entry = tk.Entry(
            duration_frame,
            textvariable=duration_var,
            bg=COLORS["highlight"],
            fg=COLORS["text"],
            width=5
        )
        duration_entry.pack(side="right")
        
        # Enabled frame
        enabled_frame = tk.Frame(dialog, bg=COLORS["bg"], pady=5)
        enabled_frame.pack(fill="x", padx=20, pady=5)
        
        enabled_var = tk.BooleanVar(value=schedule.enabled)
        enabled_check = tk.Checkbutton(
            enabled_frame, 
            text="Enabled",
            variable=enabled_var,
            bg=COLORS["bg"],
            fg=COLORS["text"],
            selectcolor=COLORS["highlight"]
        )
        enabled_check.pack(side="left")
        
        # Buttons frame
        buttons_frame = tk.Frame(dialog, bg=COLORS["bg"], pady=10)
        buttons_frame.pack(fill="x", padx=20, pady=10)
        
        cancel_button = tk.Button(
            buttons_frame,
            text="Cancel",
            bg=COLORS["secondary"],
            fg="white",
            relief="flat",
            borderwidth=0,
            padx=10,
            pady=5,
            command=dialog.destroy
        )
        cancel_button.pack(side="left", padx=(0, 10))
        
        save_button = tk.Button(
            buttons_frame,
            text="Save",
            bg=COLORS["accent"],
            fg="white",
            relief="flat",
            borderwidth=0,
            padx=10,
            pady=5,
            command=lambda: save_schedule(
                dialog, tree, schedule.id, name_var.get(), type_var.get(), action_var.get(),
                date_var.get(), time_var.get(), weekday_vars, duration_var.get()
            )
        )
        save_button.pack(side="right")
        
        # Show/hide relevant fields based on initial selection
        toggle_date_time_fields(type_var.get(), date_frame, weekday_frame)
        
    except Exception as e:
        print(f"Error showing edit schedule dialog: {e}\n{traceback.format_exc()}")


def delete_selected_schedule(tree):
    """Delete the selected schedule"""
    try:
        selected = tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select a schedule to delete")
            return
        
        schedule_id = selected[0]
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this schedule?"):
            if schedule_manager.remove_schedule(schedule_id):
                update_schedule_tree(tree)
            else:
                messagebox.showerror("Error", "Failed to delete schedule")
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to delete schedule: {e}")
        print(f"Error deleting schedule: {e}\n{traceback.format_exc()}")


def start_countdown(minutes_str, lock_type):
    """Start a countdown timer"""
    try:
        minutes = int(minutes_str)
        if minutes <= 0:
            messagebox.showerror("Error", "Please enter a valid number of minutes")
            return
        
        seconds = minutes * 60
        
        # Create a countdown schedule
        schedule_id = scheduler.generate_id()
        schedule_name = f"Countdown ({minutes} min)"
        
        schedule = scheduler.Schedule(
            id=schedule_id,
            name=schedule_name,
            action=lock_type,
            time_type="countdown",
            start_time=seconds,
            duration=None,  # Indefinite until manually unlocked
            enabled=True
        )
        
        # Add and start the schedule
        if schedule_manager.add_schedule(schedule):
            messagebox.showinfo(
                "Countdown Started", 
                f"The {lock_type} will be locked in {minutes} minutes"
            )
        else:
            messagebox.showerror("Error", "Failed to start countdown")
        
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid number of minutes")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start countdown: {e}")
        print(f"Error starting countdown: {e}\n{traceback.format_exc()}")


def cleanup():
    """Cleanup resources when exiting"""
    try:
        if schedule_manager:
            schedule_manager.stop()
    except Exception as e:
        print(f"Error during cleanup: {e}")


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
        
        # Register cleanup handler
        root.protocol("WM_DELETE_WINDOW", lambda: (cleanup(), root.destroy()))
        
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
