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
import time
import ctypes
from ctypes import wintypes

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
countdown_active = False
main_content = None


def initialize_app():
    """Initialize the application with configuration and error handling"""
    global config, current_theme, refresh_rate, COLORS, schedule_manager, root, app_icon, shortcut
    
    try:
        config = open_config("keylock.config")
        # Always use dark theme regardless of configuration
        current_theme = "dark" 
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


def initialize_colors():
    """Initialize the COLORS dictionary with all necessary UI colors and enhanced palette"""
    global COLORS
    
    # Always use dark theme colors
    # Modern dark theme with green/teal accent colors
    accent_primary = "#00BFA5"  # Teal accent
    accent_secondary = "#4DB6AC"  # Lighter teal
    accent_hover = "#009688"  # Deeper teal
    
    background = "#1E1E1E"  # Dark background
    card_bg = "#2D2D2D"  # Slightly lighter than background
    surface = "#333333"  # Surface elements
    
    text_primary = "#E0F2F1"  # Very light teal for text
    text_secondary = "#B2DFDB"  # Light teal text for secondary elements
    text_disabled = "#80CBC4"  # Medium teal for disabled text
    
    success = "#4CAF50"  # Green
    error = "#FF5252"  # Red
    warning = "#FFD740"  # Amber
    info = "#26A69A"  # Teal for info
    
    separator = "#444444"  # Subtle separator
    selection = "#00897B33"  # Selection with transparency
    
    glass_bg = "#263238"  # Dark teal-tinted background
    glass_frame = "#212121"  # Very dark gray
    glass_highlight = "#37474F"  # Slightly lighter for highlights
    
    # Set core colors
    COLORS["background"] = background
    COLORS["foreground"] = text_primary
    COLORS["accent"] = accent_primary
    COLORS["secondary_accent"] = accent_secondary
    COLORS["accent_hover"] = accent_hover
    
    # Background variations
    COLORS["card_bg"] = card_bg
    COLORS["surface"] = surface
    COLORS["glass_bg"] = glass_bg
    COLORS["glass_frame"] = glass_frame
    COLORS["glass_highlight"] = glass_highlight
    
    # Text variations
    COLORS["text"] = text_primary  # Alias for foreground
    COLORS["label"] = text_secondary
    COLORS["inactive"] = text_disabled
    COLORS["light_text"] = text_disabled
    
    # Button colors
    COLORS["button_bg"] = accent_primary
    COLORS["button_fg"] = "#FFFFFF"  # White text on buttons
    COLORS["button_hover"] = accent_hover
    
    # Input colors
    COLORS["input_bg"] = "#212121"
    COLORS["input_fg"] = text_primary
    COLORS["border"] = "#455A64"
    
    # Status colors
    COLORS["success"] = success
    COLORS["error"] = error
    COLORS["warning"] = warning
    COLORS["info"] = info
    
    # UI element colors
    COLORS["separator"] = separator
    COLORS["selection_bg"] = selection
    COLORS["highlight"] = "#37474F"
    COLORS["shadow"] = "#00000077"
    
    # Aliases for backward compatibility
    COLORS["bg"] = background
    COLORS["secondary"] = text_secondary
    COLORS["card_shadow"] = COLORS["shadow"]
    
    # Apply Sun Valley theme-specific adjustments if available
    try:
        if sv_ttk:
            # Refine colors to better match Sun Valley dark theme
            COLORS["glass_bg"] = "#263238"
            COLORS["glass_frame"] = "#212121"
            COLORS["glass_highlight"] = "#37474F"
            COLORS["input_bg"] = "#333333"
            COLORS["button_hover"] = "#00897B"
            COLORS["accent_hover"] = "#00897B"
    except:
        pass
    
    return COLORS


def configure_styles():
    """Configure the styles for the application with a modern glass-like appearance and enhanced colors"""
    try:
        style = ttk.Style()
        
        # Always apply Sun Valley dark theme
        try:
            sv_ttk.set_theme("dark")
        except Exception as e:
            print(f"Could not apply Sun Valley theme: {e}")
            style.theme_use('clam')  # Fallback to clam theme
        
        # Ensure we have all necessary colors in the COLORS dictionary
        initialize_colors()
        
        # Configure styles for various UI elements with glass-like appearance
        style.configure(
            "Glass.TFrame", 
            background=COLORS["glass_bg"]
        )
        
        style.configure(
            "TLabel", 
            background=COLORS["background"], 
            foreground=COLORS["foreground"],
            font=("Segoe UI", 10)
        )
        
        style.configure(
            "Glass.TLabel",
            background=COLORS["glass_bg"], 
            foreground=COLORS["foreground"],
            font=("Segoe UI", 10)
        )
        
        style.configure(
            "Glass.Header.TLabel",
            background=COLORS["glass_bg"], 
            foreground=COLORS["foreground"],
            font=("Segoe UI", 18, "bold")
        )
        
        style.configure(
            "Glass.Subheader.TLabel",
            background=COLORS["glass_bg"], 
            foreground=COLORS["foreground"],
            font=("Segoe UI", 14, "bold")
        )
        
        style.configure(
            "Glass.Footer.TLabel",
            background=COLORS["glass_bg"], 
            foreground=COLORS["light_text"],
            font=("Segoe UI", 9)
        )
        
        # Improved button styles with better contrast
        style.configure(
            "Glass.TButton",
            background=COLORS["accent"],
            foreground="#FFFFFF",  # Always white for better readability
            font=("Segoe UI", 10, "bold"),
            padding=(10, 5),
            borderwidth=1,
            focusthickness=0
        )
        
        style.map(
            "Glass.TButton",
            background=[('active', COLORS["accent_hover"]), ('pressed', COLORS["accent_hover"])],
            relief=[('pressed', 'sunken'), ('!pressed', 'raised')]
        )
        
        style.configure(
            "TCheckbutton",
            background=COLORS["background"],
            foreground=COLORS["foreground"],
            font=("Segoe UI", 10)
        )
        
        style.configure(
            "Glass.TCheckbutton",
            background=COLORS["glass_bg"],
            foreground=COLORS["foreground"],
            font=("Segoe UI", 10)
        )
        
        style.configure(
            "Vertical.TScrollbar",
            background=COLORS["glass_bg"],
            arrowcolor=COLORS["foreground"],
            bordercolor=COLORS["glass_bg"],
            troughcolor=COLORS["glass_bg"],
            gripcount=0
        )
        
        style.map(
            "Vertical.TScrollbar",
            background=[('active', COLORS["accent_hover"]), ('pressed', COLORS["accent"])],
            troughcolor=[('!active', COLORS["glass_bg"])]
        )

        # Card style with shadow effect
        style.configure(
            "Card.TFrame",
            background=COLORS["card_bg"],
            borderwidth=0,
            relief="flat",
            padding=15
        )
        
        # Modern rounded button style with high contrast
        style.configure(
            "Rounded.TButton",
            background=COLORS["accent"],
            foreground="#FFFFFF",  # Always white text
            borderwidth=1,
            focusthickness=0,
            padding=(15, 8),
            font=("Segoe UI", 10, "bold")
        )
        
        style.map(
            "Rounded.TButton",
            background=[('active', COLORS["accent_hover"]), ('pressed', COLORS["accent_hover"])],
            relief=[('pressed', 'sunken'), ('!pressed', 'raised')]
        )
        
        # Primary action button with high contrast
        style.configure(
            "Action.TButton",
            background=COLORS["accent"],
            foreground="#FFFFFF",  # Always white text
            borderwidth=1,
            focusthickness=0,
            padding=(15, 8),
            font=("Segoe UI", 11, "bold")
        )
        
        style.map(
            "Action.TButton",
            background=[('active', COLORS["accent_hover"]), ('pressed', COLORS["accent_hover"])],
            relief=[('pressed', 'sunken'), ('!pressed', 'raised')]
        )
        
        # Secondary/ghost button
        style.configure(
            "Ghost.TButton",
            background=COLORS["glass_bg"],
            foreground=COLORS["foreground"],
            borderwidth=1,
            bordercolor=COLORS["border"],
            focusthickness=0,
            padding=(10, 5),
            font=("Segoe UI", 10)
        )
        
        style.map(
            "Ghost.TButton",
            background=[('active', COLORS["selection_bg"]), ('pressed', COLORS["selection_bg"])],
            foreground=[('active', COLORS["accent"]), ('pressed', COLORS["accent"])],
            relief=[('pressed', 'flat'), ('!pressed', 'flat')]
        )
        
        # Success button
        style.configure(
            "Success.TButton",
            background=COLORS["success"],
            foreground=COLORS["button_fg"],
            borderwidth=0,
            focusthickness=0,
            padding=(15, 8),
            font=("Segoe UI", 10, "bold")
        )
        
        style.map(
            "Success.TButton",
            background=[('active', '#3D9140'), ('pressed', '#3D9140')],
            relief=[('pressed', 'flat'), ('!pressed', 'flat')]
        )
        
        # Warning button
        style.configure(
            "Warning.TButton",
            background=COLORS["warning"],
            foreground="#333333",
            borderwidth=0,
            focusthickness=0,
            padding=(15, 8),
            font=("Segoe UI", 10, "bold")
        )
        
        style.map(
            "Warning.TButton",
            background=[('active', '#E59400'), ('pressed', '#E59400')],
            relief=[('pressed', 'flat'), ('!pressed', 'flat')]
        )
        
        # Danger button
        style.configure(
            "Danger.TButton",
            background=COLORS["error"],
            foreground=COLORS["button_fg"],
            borderwidth=0,
            focusthickness=0,
            padding=(15, 8),
            font=("Segoe UI", 10, "bold")
        )
        
        style.map(
            "Danger.TButton",
            background=[('active', '#D32F2F'), ('pressed', '#D32F2F')],
            relief=[('pressed', 'flat'), ('!pressed', 'flat')]
        )
        
        # Notebook/tab styling
        style.configure(
            "TNotebook",
            background=COLORS["background"],
            borderwidth=0,
            tabmargins=[0, 0, 0, 0],
            tabposition="n"
        )
        
        style.configure(
            "TNotebook.Tab",
            background=COLORS["glass_bg"],
            foreground=COLORS["foreground"],
            padding=[15, 5],
            font=("Segoe UI", 10)
        )
        
        style.map(
            "TNotebook.Tab",
            background=[('selected', COLORS["accent"]), ('active', COLORS["selection_bg"])],
            foreground=[('selected', "white"), ('active', COLORS["accent"])],
            expand=[('selected', [1, 1, 1, 0])]
        )
        
        return style
        
    except Exception as e:
        print(f"Error configuring styles: {e}")
        return None


def create_ui():
    """Create the application UI elements with modern glass effect and scrollability"""
    global app_icon, root, key_lock_btn, mouse_lock_btn, key_block_on_min, window_transparency_var, status_var, footer, shortcut, main_content
    
    # Configure all styles
    configure_styles()
    
    # Set window properties
    root.geometry("850x650")
    root.minsize(750, 550)
    center_window(root)
    
    # Set window transparency if supported
    apply_transparency(85)
    
    # Set dark background for root window
    root.configure(bg=COLORS["background"])
    
    # Create main container as a notebook with tabs
    main_frame = ttk.Notebook(root)
    main_frame.grid(row=0, column=0, sticky="nsew")
    
    # Make the root window responsive
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    
    # Create main tab with scrollability
    main_tab = ttk.Frame(main_frame, style="TFrame")
    
    # Create a canvas and scrollbar for scrollability
    main_canvas = tk.Canvas(main_tab, bg=COLORS["bg"], highlightthickness=0)
    main_scrollbar = ttk.Scrollbar(main_tab, orient="vertical", command=main_canvas.yview, style="Vertical.TScrollbar")
    
    # Create frame inside canvas for content
    main_content = ttk.Frame(main_canvas, style="TFrame")
    
    # Configure scrolling
    main_canvas.configure(yscrollcommand=main_scrollbar.set)
    main_canvas.pack(side="left", fill="both", expand=True)
    main_scrollbar.pack(side="right", fill="y")
    
    # Create window in canvas for content
    main_canvas_window = main_canvas.create_window((0, 0), window=main_content, anchor="nw", tags="main_content")
    
    # Configure canvas scrolling
    def on_canvas_configure(event):
        main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        width = event.width
        main_canvas.itemconfig(main_canvas_window, width=width)
    
    main_canvas.bind("<Configure>", on_canvas_configure)
    
    # Add mouse wheel scrolling
    def on_mousewheel(event):
        main_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    main_canvas.bind_all("<MouseWheel>", on_mousewheel)
    
    # Configure main_content for responsiveness
    main_content.columnconfigure(0, weight=1)
    
    # Add the main_tab to the notebook
    main_frame.add(main_tab, text="Dashboard")
    
    # Add "Settings" and "Scheduler" tabs
    settings_tab = ttk.Frame(main_frame, style="TFrame")
    scheduler_tab = ttk.Frame(main_frame, style="TFrame")
    
    main_frame.add(settings_tab, text="Settings")
    main_frame.add(scheduler_tab, text="Scheduler")
    
    # Setup content in tabs
    create_settings_section(settings_tab)
    create_scheduler_section_enhanced(scheduler_tab)
    
    # Bind resize event to window
    root.bind("<Configure>", on_window_resize)
    
    # Title frame with glass effect
    title_frame = ttk.Frame(main_content, style="Glass.TFrame")
    title_frame.grid(row=0, column=0, pady=(0, 15), sticky="ew", padx=15)
    title_frame.columnconfigure(0, weight=1)
    
    # Draw a custom app icon on canvas with improved style
    icon_size = 36
    icon_canvas = tk.Canvas(
        title_frame,
        width=icon_size,
        height=icon_size,
        bg=COLORS["glass_bg"],
        highlightthickness=0
    )
    
    # Draw a lock icon with improved appearance
    center_x = icon_size / 2
    center_y = icon_size / 2
    
    # Lock body
    lock_width = 22
    lock_height = 18
    lock_left = center_x - lock_width / 2
    lock_top = center_y - lock_height / 2 + 4
    lock_right = center_x + lock_width / 2
    lock_bottom = lock_top + lock_height
    
    # Draw rounded rectangle for lock body
    draw_rounded_rectangle(
        icon_canvas,
        lock_left, lock_top, lock_right, lock_bottom,
        radius=4,
        outline=COLORS["text"],
        width=2,
        fill=COLORS["accent"]
    )
    
    # Lock shackle with smoother arc
    shackle_width = 14
    shackle_height = 12
    shackle_left = center_x - shackle_width / 2
    shackle_bottom = lock_top
    shackle_right = center_x + shackle_width / 2
    shackle_top = shackle_bottom - shackle_height
    
    icon_canvas.create_arc(
        shackle_left, shackle_top,
        shackle_right, shackle_bottom + shackle_height/2,
        start=0, extent=180,
        outline=COLORS["text"],
        width=2,
        style="arc"
    )
    
    # Add a slight highlight to give 3D effect
    icon_canvas.create_arc(
        shackle_left+1, shackle_top+1,
        shackle_right-1, shackle_bottom + shackle_height/2-1,
        start=0, extent=180,
        outline=COLORS["accent_hover"],
        width=1,
        style="arc"
    )
    
    icon_canvas.grid(row=0, column=0, sticky="w", padx=5)
    
    # Store the canvas as app_icon
    app_icon = icon_canvas
    
    # Application title with improved styling
    title_label = ttk.Label(
        title_frame, 
        text="KeyLock", 
        style="Glass.Header.TLabel"
    )
    title_label.grid(row=0, column=1, sticky="w")
    
    # Add a version label and about button
    version_frame = ttk.Frame(title_frame, style="Glass.TFrame")
    version_frame.grid(row=0, column=2, sticky="e", padx=10)
    
    version_label = ttk.Label(
        version_frame,
        text="v1.0",
        style="Glass.TLabel",
        font=("Segoe UI", 8)
    )
    version_label.pack(side="left", padx=(0, 10))
    
    # Button with a question mark icon - improved styling
    help_button = ttk.Button(
        version_frame,
        text="?",
        width=2,
        style="Ghost.TButton",
        command=lambda: tk.messagebox.showinfo(
            "About KeyLock",
            "KeyLock is a utility for locking your keyboard and mouse.\n\n"
            "Press the configured hotkey to unlock devices.\n\n"
            "© 2023 KeyLock Team"
        )
    )
    help_button.pack(side="right")
    
    # Modern card layout for main controls
    control_card = ttk.Frame(main_content, style="Card.TFrame")
    control_card.grid(row=1, column=0, pady=15, sticky="ew", padx=20)
    control_card.columnconfigure(0, weight=1)
    control_card.columnconfigure(1, weight=1)
    control_card.columnconfigure(2, weight=1)
    
    # Add shadow effect to card
    if current_theme == "light":
        control_card.configure(padding=(15, 15, 15, 20))  # Extra padding at bottom for shadow
    
    # Card header with icon
    header_frame = ttk.Frame(control_card, style="Card.TFrame")
    header_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 15))
    
    header_label = ttk.Label(
        header_frame,
        text="Quick Controls",
        style="Glass.Subheader.TLabel",
        font=("Segoe UI", 14, "bold")
    )
    header_label.pack(side="left")
    
    # Button frame with improved visibility
    button_frame = ttk.Frame(control_card, style="Card.TFrame")
    button_frame.grid(row=1, column=0, columnspan=3, pady=5, sticky="ew")
    button_frame.columnconfigure(0, weight=1)
    button_frame.columnconfigure(1, weight=1)
    button_frame.columnconfigure(2, weight=1)
    
    # Lock Keyboard button - enhanced visibility
    key_lock_btn = ttk.Button(
        button_frame,
        text="Lock Keyboard",
        command=toggle_keyboard_lock,
        style="Rounded.TButton",
        width=15
    )
    key_lock_btn.grid(row=0, column=0, padx=8, pady=8, sticky="ew")
    
    # Lock Mouse button - enhanced visibility
    mouse_lock_btn = ttk.Button(
        button_frame,
        text="Lock Mouse",
        command=toggle_mouse_lock,
        style="Rounded.TButton",
        width=15
    )
    mouse_lock_btn.grid(row=0, column=1, padx=8, pady=8, sticky="ew")
    
    # Lock Both button - enhanced with primary action style
    both_lock_btn = ttk.Button(
        button_frame,
        text="Lock Both",
        command=safe_lock_both,
        style="Action.TButton",
        width=15
    )
    both_lock_btn.grid(row=0, column=2, padx=8, pady=8, sticky="ew")
    
    # Add tooltips for buttons
    tooltip_timer = None
    tooltip_label = None
    
    def show_tooltip(widget, text, event=None):
        nonlocal tooltip_timer, tooltip_label
        x, y, _, _ = widget.bbox("insert")
        x += widget.winfo_rootx() + 25
        y += widget.winfo_rooty() + 25
        
        # Create tooltip
        tooltip_label = tk.Toplevel(widget)
        tooltip_label.wm_overrideredirect(True)
        tooltip_label.wm_geometry(f"+{x}+{y}")
        
        frame = ttk.Frame(tooltip_label, style="Glass.TFrame", padding=5)
        frame.pack(fill="both", expand=True)
        
        label = ttk.Label(frame, text=text, style="Glass.TLabel", 
                         justify=tk.LEFT, wraplength=200)
        label.pack()
    
    def hide_tooltip(event=None):
        nonlocal tooltip_timer, tooltip_label
        if tooltip_timer is not None:
            root.after_cancel(tooltip_timer)
            tooltip_timer = None
        if tooltip_label:
            tooltip_label.destroy()
            tooltip_label = None
    
    def schedule_tooltip(widget, text, event=None):
        nonlocal tooltip_timer
        if tooltip_timer is not None:
            root.after_cancel(tooltip_timer)
        tooltip_timer = root.after(500, lambda: show_tooltip(widget, text))
    
    # Add tooltips to buttons
    key_lock_btn.bind("<Enter>", lambda e: schedule_tooltip(key_lock_btn, "Locks only the keyboard, mouse will remain functional"))
    key_lock_btn.bind("<Leave>", hide_tooltip)
    
    mouse_lock_btn.bind("<Enter>", lambda e: schedule_tooltip(mouse_lock_btn, "Locks only the mouse, keyboard will remain functional"))
    mouse_lock_btn.bind("<Leave>", hide_tooltip)
    
    both_lock_btn.bind("<Enter>", lambda e: schedule_tooltip(both_lock_btn, "Locks both keyboard and mouse simultaneously"))
    both_lock_btn.bind("<Leave>", hide_tooltip)
    
    # Create status section
    status_frame = create_status_section(main_content)
    
    # Create options section with card-like appearance
    options_card = ttk.LabelFrame(main_content, text="Options", padding=15, style="Glass.TFrame")
    options_card.grid(row=3, column=0, sticky="ew", padx=20)
    options_card.columnconfigure(0, weight=1)
    
    # Add the lock on minimize option
    min_frame = ttk.Frame(options_card, style="Glass.TFrame")
    min_frame.grid(row=0, column=0, sticky="w", pady=5)
    
    key_block_on_min = tk.BooleanVar(value=config.get("lock_on_minimize", False))
    lock_on_min_check = ttk.Checkbutton(
        min_frame,
        text="Lock keyboard when minimized",
        variable=key_block_on_min,
        style="Glass.TCheckbutton"
    )
    lock_on_min_check.pack(side="left")
    lock_on_min_check.bind("<Enter>", lambda e: schedule_tooltip(lock_on_min_check, "Automatically locks the keyboard when the application window is minimized"))
    lock_on_min_check.bind("<Leave>", hide_tooltip)
    
    # Add transparency slider with a more modern appearance
    transparency_frame = ttk.Frame(options_card, style="Glass.TFrame")
    transparency_frame.grid(row=1, column=0, sticky="ew", pady=10)
    transparency_frame.columnconfigure(1, weight=1)
    
    transparency_label = ttk.Label(
        transparency_frame,
        text="Window Transparency:",
        style="Glass.TLabel"
    )
    transparency_label.grid(row=0, column=0, sticky="w", padx=(0, 10))
    
    window_transparency_var = tk.IntVar(value=config.get("transparency", 255))
    transparency_slider = ttk.Scale(
        transparency_frame,
        from_=100,
        to=255,
        orient="horizontal",
        variable=window_transparency_var,
        command=lambda v: apply_transparency(int(float(v)))
    )
    transparency_slider.grid(row=0, column=1, sticky="ew")
    transparency_slider.bind("<Enter>", lambda e: schedule_tooltip(transparency_slider, "Adjust the transparency of the application window"))
    transparency_slider.bind("<Leave>", hide_tooltip)
    
    # Add shortcut configuration
    shortcut_frame = ttk.Frame(options_card, style="Glass.TFrame")
    shortcut_frame.grid(row=2, column=0, sticky="ew", pady=5)
    shortcut_frame.columnconfigure(1, weight=1)
    
    shortcut_label = ttk.Label(
        shortcut_frame,
        text="Unlock Shortcut:",
        style="Glass.TLabel"
    )
    shortcut_label.grid(row=0, column=0, sticky="w", padx=(0, 10))
    
    shortcut = tk.StringVar(value=config.get("shortcut", "Ctrl+Alt+U"))
    shortcut_entry = ttk.Entry(
        shortcut_frame,
        textvariable=shortcut,
        style="Glass.TEntry",
        width=15
    )
    shortcut_entry.grid(row=0, column=1, sticky="w")
    shortcut_entry.bind("<KeyRelease>", lambda e: debounce_shortcut_change())
    shortcut_entry.bind("<Enter>", lambda e: schedule_tooltip(shortcut_entry, "Enter a keyboard shortcut to use for unlocking (e.g., Ctrl+Alt+U)"))
    shortcut_entry.bind("<Leave>", hide_tooltip)
    
    # Create scheduler section
    create_scheduler_section_enhanced(main_content)
    
    # Create footer with glass effect
    footer = ttk.Label(
        main_content, 
        text="Press " + shortcut.get() + " to unlock", 
        style="Glass.TLabel",
        padding=10
    )
    footer.grid(row=5, column=0, sticky="ew", pady=(0, 10))
    
    # Apply initial config settings
    apply_config_settings()
    
    # Make window resizable
    root.resizable(True, True)
    
    # Set minimum window size to prevent UI breaking on small sizes
    root.minsize(650, 550)
    
    # Center window on screen
    center_window(root, 800, 650)
    
    # Apply initial transparency
    apply_transparency(window_transparency_var.get())
    
    return True


def create_scheduler_section_enhanced(parent):
    """Create an enhanced scheduler UI section with glass effect"""
    try:
        # Create a card-like container for scheduler
        scheduler_card = ttk.Frame(parent, style="Glass.TFrame")
        scheduler_card.grid(row=4, column=0, sticky="ew", padx=20, pady=10)
        scheduler_card.columnconfigure(0, weight=1)
        
        # Header with improved visual hierarchy and glass effect
        scheduler_header = ttk.Label(
            scheduler_card, 
            text="Quick Scheduler", 
            style="Glass.Header.TLabel"
        )
        scheduler_header.grid(row=0, column=0, sticky="w", pady=(10, 5))
        
        # Add a descriptive subheader with glass effect
        scheduler_subheader = ttk.Label(
            scheduler_card,
            text="Set up a quick countdown timer or create a schedule", 
            style="Glass.TLabel"
        )
        scheduler_subheader.grid(row=1, column=0, sticky="w", pady=(0, 15))
        
        # Timer controls in a row
        timer_frame = ttk.Frame(scheduler_card, style="Glass.TFrame")
        timer_frame.grid(row=2, column=0, sticky="ew", pady=5)
        timer_frame.columnconfigure(0, weight=1)
        timer_frame.columnconfigure(1, weight=1)
        timer_frame.columnconfigure(2, weight=1)
        timer_frame.columnconfigure(3, weight=1)
        
        # Minutes entry with glass styling
        minutes_frame = ttk.Frame(timer_frame, style="Glass.TFrame")
        minutes_frame.grid(row=0, column=0, sticky="w", padx=5)
        
        minutes_label = ttk.Label(
            minutes_frame, 
            text="Minutes:", 
            style="Glass.TLabel"
        )
        minutes_label.pack(side="left", padx=(0, 5))
        
        minutes_var = tk.StringVar(value="5")
        minutes_entry = tk.Spinbox(
            minutes_frame,
            from_=1,
            to=60,
            width=3,
            textvariable=minutes_var,
            bg=COLORS["glass_highlight"],
            fg=COLORS["text"],
            font=("Segoe UI", 10, "bold"),
            buttonbackground=COLORS["glass_highlight"],
            relief="flat",
            bd=0
        )
        minutes_entry.pack(side="left")
        
        # Lock type selection with radio buttons
        lock_type_frame = ttk.Frame(timer_frame, style="Glass.TFrame")
        lock_type_frame.grid(row=0, column=1, sticky="w", padx=5)
        
        lock_type_var = tk.StringVar(value="both")
        
        keyboard_radio = ttk.Radiobutton(
            lock_type_frame,
            text="Keyboard",
            variable=lock_type_var,
            value="keyboard",
            style="Glass.TRadiobutton"
        )
        keyboard_radio.pack(side="left", padx=(0, 10))
        
        mouse_radio = ttk.Radiobutton(
            lock_type_frame,
            text="Mouse",
            variable=lock_type_var,
            value="mouse",
            style="Glass.TRadiobutton"
        )
        mouse_radio.pack(side="left", padx=(0, 10))
        
        both_radio = ttk.Radiobutton(
            lock_type_frame,
            text="Both",
            variable=lock_type_var,
            value="both",
            style="Glass.TRadiobutton"
        )
        both_radio.pack(side="left")
        
        # Auto-unlock option
        unlock_frame = ttk.Frame(timer_frame, style="Glass.TFrame")
        unlock_frame.grid(row=0, column=2, sticky="w", padx=5)
        
        auto_unlock_var = tk.BooleanVar(value=True)
        auto_unlock_check = ttk.Checkbutton(
            unlock_frame,
            text="Auto-unlock after",
            variable=auto_unlock_var,
            style="Glass.TCheckbutton"
        )
        auto_unlock_check.pack(side="left", padx=(0, 5))
        
        unlock_minutes_var = tk.StringVar(value="5")
        unlock_minutes_entry = tk.Spinbox(
            unlock_frame,
            from_=1,
            to=120,
            width=3,
            textvariable=unlock_minutes_var,
            bg=COLORS["glass_highlight"],
            fg=COLORS["text"],
            font=("Segoe UI", 10),
            buttonbackground=COLORS["glass_highlight"],
            relief="flat",
            bd=0
        )
        unlock_minutes_entry.pack(side="left", padx=(0, 5))
        
        minutes_text = ttk.Label(
            unlock_frame,
            text="minutes",
            style="Glass.TLabel"
        )
        minutes_text.pack(side="left")
        
        # Start button with glass effect
        start_button = ttk.Button(
            timer_frame,
            text="Start Timer",
            style="Glass.TButton",
            command=lambda: start_enhanced_countdown(
                minutes_var.get(), 
                lock_type_var.get(),
                auto_unlock_var.get(),
                unlock_minutes_var.get(),
                timer_var,
                progress_arc,
                canvas
            )
        )
        start_button.grid(row=0, column=3, sticky="e", padx=5)
        
        # Visual progress indicator
        progress_frame = ttk.Frame(scheduler_card, style="Glass.TFrame")
        progress_frame.grid(row=3, column=0, sticky="ew", pady=10)
        progress_frame.columnconfigure(0, weight=1)
        
        # Create canvas for circular progress
        canvas_size = 80
        canvas = tk.Canvas(
            progress_frame,
            width=canvas_size,
            height=canvas_size,
            bg=COLORS["glass_bg"],
            highlightthickness=0
        )
        canvas.grid(row=0, column=0)
        
        # Create background circle
        center_x = canvas_size // 2
        center_y = canvas_size // 2
        radius = (canvas_size // 2) - 10
        
        # Background circle
        canvas.create_oval(
            center_x - radius, center_y - radius,
            center_x + radius, center_y + radius,
            outline=COLORS["glass_highlight"],
            width=8,
            fill=COLORS["glass_bg"]
        )
        
        # Progress arc (initially empty)
        progress_arc = canvas.create_arc(
            center_x - radius, center_y - radius,
            center_x + radius, center_y + radius,
            start=90, extent=0,
            outline=COLORS["accent"],
            width=8,
            style="arc"
        )
        
        # Add timer text
        timer_var = tk.StringVar(value="Ready")
        timer_text = ttk.Label(
            canvas,
            textvariable=timer_var,
            style="Glass.Timer.TLabel",
            font=("Consolas", 14, "bold")
        )
        canvas.create_window(center_x, center_y, window=timer_text)
        
        # Store references for later use
        parent.timer_var = timer_var
        parent.progress_arc = progress_arc
        parent.timer_canvas = canvas
        
        # Add a "Go to Full Scheduler" button
        full_scheduler_btn = ttk.Button(
            scheduler_card,
            text="Go to Full Scheduler",
            style="Glass.TButton",
            command=lambda: main_frame.select(1)  # Switch to scheduler tab
        )
        full_scheduler_btn.grid(row=4, column=0, sticky="e", pady=10)
        
        return scheduler_card
    except Exception as e:
        print(f"Error creating enhanced scheduler section: {e}")
        return None


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
    """Create the status section with device indicators and modern UI"""
    global keyboard_status, mouse_status, keyboard_img, mouse_img
    
    # Device status card with improved styling
    status_card = ttk.Frame(parent, style="Card.TFrame")
    status_card.grid(row=2, column=0, pady=15, sticky="ew", padx=20)
    status_card.columnconfigure(0, weight=1)
    status_card.columnconfigure(1, weight=1)
    
    # Add shadow effect to card
    if current_theme == "light":
        status_card.configure(padding=(15, 15, 15, 20))  # Extra padding at bottom for shadow
    
    # Card header
    header_frame = ttk.Frame(status_card, style="Card.TFrame")
    header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 15))
    
    header_label = ttk.Label(
        header_frame,
        text="Device Status",
        style="Glass.Subheader.TLabel",
        font=("Segoe UI", 14, "bold")
    )
    header_label.pack(side="left")
    
    # Create a frame for each device with improved layout
    keyboard_frame = ttk.Frame(status_card, style="Card.TFrame", padding=10)
    keyboard_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
    
    mouse_frame = ttk.Frame(status_card, style="Card.TFrame", padding=10)
    mouse_frame.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
    
    # Keyboard status with canvas-based indicator
    keyboard_header = ttk.Label(
        keyboard_frame, 
        text="Keyboard", 
        style="Glass.TLabel", 
        font=("Segoe UI", 12, "bold"),
        foreground=COLORS.get("foreground", "#0D47A1")  # Use foreground with fallback
    )
    keyboard_header.pack(anchor="w", pady=(0, 5))
    
    keyboard_canvas = tk.Canvas(keyboard_frame, width=120, height=80, bg=COLORS["card_bg"], highlightthickness=0)
    keyboard_canvas.pack(fill="both", expand=True)
    
    # Draw keyboard indicator
    draw_keyboard_indicator(keyboard_canvas, locked=False)
    keyboard_img = keyboard_canvas
    
    keyboard_status = ttk.Label(keyboard_frame, text="Unlocked", style="Glass.TLabel", foreground=COLORS["success"])
    keyboard_status.pack(pady=(5, 0))
    
    # Mouse status with canvas-based indicator
    mouse_header = ttk.Label(
        mouse_frame, 
        text="Mouse", 
        style="Glass.TLabel", 
        font=("Segoe UI", 12, "bold"),
        foreground=COLORS.get("foreground", "#0D47A1")  # Use foreground with fallback
    )
    mouse_header.pack(anchor="w", pady=(0, 5))
    
    mouse_canvas = tk.Canvas(mouse_frame, width=120, height=80, bg=COLORS["card_bg"], highlightthickness=0)
    mouse_canvas.pack(fill="both", expand=True)
    
    # Draw mouse indicator
    draw_mouse_indicator(mouse_canvas, locked=False)
    mouse_img = mouse_canvas
    
    mouse_status = ttk.Label(mouse_frame, text="Unlocked", style="Glass.TLabel", foreground=COLORS["success"])
    mouse_status.pack(pady=(5, 0))
    
    return status_card


def draw_rounded_rectangle(canvas, x1, y1, x2, y2, radius=10, **kwargs):
    """Draw a rounded rectangle on the canvas"""
    # Draw corner arcs
    canvas.create_arc(x1, y1, x1 + 2*radius, y1 + 2*radius, 
                      start=90, extent=90, style="pieslice", **kwargs)
    canvas.create_arc(x2 - 2*radius, y1, x2, y1 + 2*radius, 
                      start=0, extent=90, style="pieslice", **kwargs)
    canvas.create_arc(x1, y2 - 2*radius, x1 + 2*radius, y2, 
                      start=180, extent=90, style="pieslice", **kwargs)
    canvas.create_arc(x2 - 2*radius, y2 - 2*radius, x2, y2, 
                      start=270, extent=90, style="pieslice", **kwargs)
    
    # Draw connecting rectangles
    canvas.create_rectangle(x1 + radius, y1, x2 - radius, y2, **kwargs)
    canvas.create_rectangle(x1, y1 + radius, x1 + radius, y2 - radius, **kwargs)
    canvas.create_rectangle(x2 - radius, y1 + radius, x2, y2 - radius, **kwargs)


def draw_keyboard_indicator(canvas, locked=False):
    """Draw a keyboard indicator on a canvas"""
    try:
        # Clear existing items
        canvas.delete("all")
        
        width = int(canvas.cget("width"))
        height = int(canvas.cget("height"))
        
        # Calculate dimensions for centered keyboard
        kb_width = width * 0.8
        kb_height = height * 0.6
        key_spacing = kb_width / 12
        
        kb_left = (width - kb_width) / 2
        kb_top = (height - kb_height) / 2
        kb_right = kb_left + kb_width
        kb_bottom = kb_top + kb_height
        
        # Draw keyboard base with rounded corners
        draw_rounded_rectangle(
            canvas,
            kb_left, kb_top, kb_right, kb_bottom,
            radius=5,
            fill=COLORS["glass_highlight"] if not locked else "#263238",
            outline=COLORS["foreground"],
            width=2
        )
        
        # Draw keyboard keys
        key_rows = [10, 12, 9]  # Number of keys in each row
        key_height = kb_height / (len(key_rows) + 1)
        
        for row, num_keys in enumerate(key_rows):
            key_width = (kb_width - ((num_keys + 1) * 2)) / num_keys
            y_top = kb_top + (row + 0.5) * key_height
            y_bottom = y_top + key_height * 0.7
            
            for key in range(num_keys):
                x_left = kb_left + 2 + key * (key_width + 2)
                x_right = x_left + key_width
                
                # Draw individual keys
                draw_rounded_rectangle(
                    canvas,
                    x_left, y_top, x_right, y_bottom,
                    radius=2,
                    fill=COLORS["surface"] if not locked else "#455A64",
                    outline=COLORS["foreground"],
                    width=1
                )
        
        # Draw space bar
        space_width = kb_width * 0.5
        space_left = kb_left + (kb_width - space_width) / 2
        space_right = space_left + space_width
        space_top = kb_top + 3.5 * key_height
        space_bottom = space_top + key_height * 0.7
        
        draw_rounded_rectangle(
            canvas,
            space_left, space_top, space_right, space_bottom,
            radius=2,
            fill=COLORS["surface"] if not locked else "#455A64",
            outline=COLORS["foreground"],
            width=1
        )
        
        # Draw lock indicator
        indicator_size = 20
        indicator_x = kb_right + 5
        indicator_y = kb_top
        
        if locked:
            # Draw locked indicator (closed padlock)
            canvas.create_oval(
                indicator_x - indicator_size/2, 
                indicator_y - indicator_size/2,
                indicator_x + indicator_size/2, 
                indicator_y + indicator_size/2,
                fill="#FF5252",
                outline=COLORS["foreground"],
                width=1
            )
            
            # Draw lock symbol
            icon_size = indicator_size * 0.6
            canvas.create_rectangle(
                indicator_x - icon_size/3,
                indicator_y - icon_size/4,
                indicator_x + icon_size/3,
                indicator_y + icon_size/2,
                fill="#FFFFFF",
                outline=""
            )
            canvas.create_arc(
                indicator_x - icon_size/2,
                indicator_y - icon_size/2,
                indicator_x + icon_size/2,
                indicator_y,
                start=0,
                extent=180,
                style="arc",
                outline="#FFFFFF",
                width=2
            )
            
        else:
            # Draw unlocked indicator (green circle)
            canvas.create_oval(
                indicator_x - indicator_size/2, 
                indicator_y - indicator_size/2,
                indicator_x + indicator_size/2, 
                indicator_y + indicator_size/2,
                fill="#4CAF50",
                outline=COLORS["foreground"],
                width=1
            )
            
            # Draw unlock symbol (checkmark)
            canvas.create_line(
                indicator_x - indicator_size/3,
                indicator_y,
                indicator_x - indicator_size/9,
                indicator_y + indicator_size/3,
                indicator_x + indicator_size/3,
                indicator_y - indicator_size/3,
                fill="#FFFFFF",
                width=2,
                smooth=True,
                capstyle="round",
                joinstyle="round"
            )
            
        return canvas
        
    except Exception as e:
        print(f"Error drawing keyboard indicator: {e}")
        return canvas


def draw_mouse_indicator(canvas, locked=False):
    """Draw a mouse indicator on a canvas"""
    try:
        # Clear existing items
        canvas.delete("all")
        
        width = int(canvas.cget("width"))
        height = int(canvas.cget("height"))
        
        # Calculate dimensions for centered mouse
        mouse_width = width * 0.4
        mouse_height = height * 0.7
        
        mouse_left = (width - mouse_width) / 2
        mouse_top = (height - mouse_height) / 2
        mouse_right = mouse_left + mouse_width
        mouse_bottom = mouse_top + mouse_height
        
        # Draw mouse body with rounded corners
        draw_rounded_rectangle(
            canvas,
            mouse_left, mouse_top, mouse_right, mouse_bottom,
            radius=mouse_width/2,
            fill=COLORS["glass_highlight"] if not locked else "#263238",
            outline=COLORS["foreground"],
            width=2
        )
        
        # Draw mouse wheel
        wheel_width = mouse_width * 0.2
        wheel_height = mouse_height * 0.15
        wheel_left = mouse_left + (mouse_width - wheel_width) / 2
        wheel_top = mouse_top + mouse_height * 0.3
        wheel_right = wheel_left + wheel_width
        wheel_bottom = wheel_top + wheel_height
        
        canvas.create_rectangle(
            wheel_left, wheel_top, wheel_right, wheel_bottom,
            fill=COLORS["surface"] if not locked else "#455A64",
            outline=COLORS["foreground"],
            width=1
        )
        
        # Draw mouse buttons
        btn_height = mouse_height * 0.25
        btn_top = mouse_top + mouse_height * 0.05
        btn_bottom = btn_top + btn_height
        btn_mid = mouse_left + mouse_width / 2
        
        # Left button
        canvas.create_line(
            btn_mid, btn_top, btn_mid, btn_bottom,
            fill=COLORS["foreground"],
            width=1
        )
        
        # Cable
        cable_width = mouse_width * 0.2
        cable_top = mouse_top - mouse_height * 0.1
        
        canvas.create_line(
            mouse_left + mouse_width/2, cable_top,
            mouse_left + mouse_width/2, mouse_top,
            fill=COLORS["foreground"],
            width=2
        )
        
        # Draw lock indicator
        indicator_size = 20
        indicator_x = mouse_right + 5
        indicator_y = mouse_top
        
        if locked:
            # Draw locked indicator (red circle)
            canvas.create_oval(
                indicator_x - indicator_size/2, 
                indicator_y - indicator_size/2,
                indicator_x + indicator_size/2, 
                indicator_y + indicator_size/2,
                fill="#FF5252",
                outline=COLORS["foreground"],
                width=1
            )
            
            # Draw lock symbol
            icon_size = indicator_size * 0.6
            canvas.create_rectangle(
                indicator_x - icon_size/3,
                indicator_y - icon_size/4,
                indicator_x + icon_size/3,
                indicator_y + icon_size/2,
                fill="#FFFFFF",
                outline=""
            )
            canvas.create_arc(
                indicator_x - icon_size/2,
                indicator_y - icon_size/2,
                indicator_x + icon_size/2,
                indicator_y,
                start=0,
                extent=180,
                style="arc",
                outline="#FFFFFF",
                width=2
            )
            
        else:
            # Draw unlocked indicator (green circle)
            canvas.create_oval(
                indicator_x - indicator_size/2, 
                indicator_y - indicator_size/2,
                indicator_x + indicator_size/2, 
                indicator_y + indicator_size/2,
                fill="#4CAF50",
                outline=COLORS["foreground"],
                width=1
            )
            
            # Draw unlock symbol (checkmark)
            canvas.create_line(
                indicator_x - indicator_size/3,
                indicator_y,
                indicator_x - indicator_size/9,
                indicator_y + indicator_size/3,
                indicator_x + indicator_size/3,
                indicator_y - indicator_size/3,
                fill="#FFFFFF",
                width=2,
                smooth=True,
                capstyle="round",
                joinstyle="round"
            )
            
        return canvas
        
    except Exception as e:
        print(f"Error drawing mouse indicator: {e}")
        return canvas


def update_keyboard():
    """Update the keyboard status indicators"""
    try:
        global keyboard_status, keyboard_img_label
        if keyboard_manager.is_locked():
            keyboard_status.config(text="Locked")
            
            # Update canvas indicator if it exists
            if hasattr(root, 'keyboard_canvas'):
                draw_keyboard_indicator(root.keyboard_canvas, True)
        else:
            keyboard_status.config(text="Unlocked")
            
            # Update canvas indicator if it exists
            if hasattr(root, 'keyboard_canvas'):
                draw_keyboard_indicator(root.keyboard_canvas, False)
    except Exception as e:
        print(f"Error updating keyboard status: {e}")


def update_mouse():
    """Update the mouse status indicators"""
    try:
        global mouse_status, mouse_img_label
        if mouse_manager.is_locked():
            mouse_status.config(text="Locked")
            
            # Update canvas indicator if it exists
            if hasattr(root, 'mouse_canvas'):
                draw_mouse_indicator(root.mouse_canvas, True)
        else:
            mouse_status.config(text="Unlocked")
            
            # Update canvas indicator if it exists
            if hasattr(root, 'mouse_canvas'):
                draw_mouse_indicator(root.mouse_canvas, False)
    except Exception as e:
        print(f"Error updating mouse status: {e}")


def create_buttons_section(parent):
    """Create the buttons section with improved UI and visibility"""
    global key_lock_btn, mouse_lock_btn
    
    # Modern card layout for main controls
    control_card = ttk.Frame(parent, style="Card.TFrame")
    control_card.grid(row=1, column=0, pady=15, sticky="ew", padx=20)
    control_card.columnconfigure(0, weight=1)
    control_card.columnconfigure(1, weight=1)
    control_card.columnconfigure(2, weight=1)
    
    # Add shadow effect to card
    if current_theme == "light":
        control_card.configure(padding=(15, 15, 15, 20))  # Extra padding at bottom for shadow
    
    # Card header with icon
    header_frame = ttk.Frame(control_card, style="Card.TFrame")
    header_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 15))
    
    header_label = ttk.Label(
        header_frame,
        text="Quick Controls",
        style="Glass.Subheader.TLabel",
        font=("Segoe UI", 14, "bold")
    )
    header_label.pack(side="left")
    
    # Button frame with improved visibility
    button_frame = ttk.Frame(control_card, style="Card.TFrame")
    button_frame.grid(row=1, column=0, columnspan=3, pady=5, sticky="ew")
    button_frame.columnconfigure(0, weight=1)
    button_frame.columnconfigure(1, weight=1)
    button_frame.columnconfigure(2, weight=1)
    
    # Lock Keyboard button - enhanced visibility
    key_lock_btn = ttk.Button(
        button_frame,
        text="Lock Keyboard",
        command=toggle_keyboard_lock,
        style="Rounded.TButton",
        width=15
    )
    key_lock_btn.grid(row=0, column=0, padx=8, pady=8, sticky="ew")
    
    # Lock Mouse button - modernized
    mouse_lock_btn = ttk.Button(
        button_frame,
        text="Lock Mouse",
        command=toggle_mouse_lock,
        style="Rounded.TButton",
        width=15
    )
    mouse_lock_btn.grid(row=0, column=1, padx=8, pady=8, sticky="ew")
    
    # Lock Both button - modernized with primary action style
    both_lock_btn = ttk.Button(
        button_frame,
        text="Lock Both",
        command=safe_lock_both,
        style="Action.TButton",
        width=15
    )
    both_lock_btn.grid(row=0, column=2, padx=8, pady=8, sticky="ew")
    
    return control_card


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
    """Apply the dark theme regardless of selection"""
    global current_theme, COLORS
    
    try:
        # Always set dark theme
        current_theme = "dark"
        
        # Initialize enhanced colors
        initialize_colors()
        
        # Apply Sun Valley theme (dark mode)
        sv_ttk.set_theme("dark")
        
        # Configure styles with new colors
        configure_styles()
        
        # Update the colors for all widgets
        for widget in root.winfo_children():
            update_widget_themes(widget, current_theme)
        
        # Update config
        save_config(theme=current_theme)
        
    except Exception as e:
        print(f"Error applying theme: {e}")


def update_widget_themes(widget, theme):
    """Recursively update theme for all widgets"""
    try:
        if hasattr(widget, 'update_theme'):
            widget.update_theme(theme)
            
        for child in widget.winfo_children():
            update_widget_themes(child, theme)
            
    except Exception as e:
        print(f"Error updating widget theme: {e}")


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
    """Create the scheduler UI section with glass effect"""
    try:
        # Header with improved visual hierarchy and glass effect
        scheduler_header = ttk.Label(
            parent, 
            text="Scheduled Locking", 
            style="Glass.Header.TLabel"
        )
        scheduler_header.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 15))
        
        # Add a descriptive subheader with glass effect
        scheduler_subheader = ttk.Label(
            parent,
            text="Create and manage scheduled device locks and automatic unlocks", 
            style="Glass.Subheader.TLabel"
        )
        scheduler_subheader.grid(row=1, column=0, sticky="w", padx=20, pady=(0, 15))
        
        # Schedules list frame with glass effect
        schedules_frame = ttk.Frame(
            parent, 
            style="Glass.TFrame",
            padding=5
        )
        schedules_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=5)
        
        # Configure for responsive layout
        schedules_frame.columnconfigure(0, weight=1)
        schedules_frame.rowconfigure(0, weight=1)
        
        # Create a treeview for schedules with glass styling
        columns = ("name", "type", "action", "time", "duration", "enabled")
        schedule_tree = ttk.Treeview(
            schedules_frame, 
            columns=columns, 
            show="headings", 
            height=6,
            style="Glass.Treeview"
        )
        
        # Define headings
        schedule_tree.heading("name", text="Name")
        schedule_tree.heading("type", text="Schedule Type")
        schedule_tree.heading("action", text="Action")
        schedule_tree.heading("time", text="Time")
        schedule_tree.heading("duration", text="Duration")
        schedule_tree.heading("enabled", text="Status")
        
        # Define columns with improved proportions
        schedule_tree.column("name", width=130, minwidth=100)
        schedule_tree.column("type", width=120, minwidth=80)
        schedule_tree.column("action", width=90, minwidth=60)
        schedule_tree.column("time", width=110, minwidth=80)
        schedule_tree.column("duration", width=100, minwidth=60)
        schedule_tree.column("enabled", width=80, minwidth=50)
        
        # Add schedules to the treeview
        for schedule in schedule_manager.get_schedules():
            add_schedule_to_tree(schedule_tree, schedule)
        
        # Add scrollbar with glass styling
        scrollbar = ttk.Scrollbar(
            schedules_frame, 
            orient="vertical", 
            command=schedule_tree.yview, 
            style="Glass.Vertical.TScrollbar"
        )
        schedule_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")
        schedule_tree.grid(row=0, column=0, sticky="nsew", padx=1, pady=1)
        
        # Buttons frame with responsive layout and glass effect
        buttons_frame = ttk.Frame(parent, style="Glass.TFrame", padding=5)
        buttons_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=10)
        
        # Configure for responsive design
        buttons_frame.columnconfigure(0, weight=1)
        buttons_frame.columnconfigure(1, weight=1)
        buttons_frame.columnconfigure(2, weight=1)
        
        # Buttons with glass styling
        add_button = ttk.Button(
            buttons_frame,
            text="Add Schedule",
            command=lambda: show_add_schedule_dialog(schedule_tree),
            style="Glass.TButton"
        )
        add_button.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        edit_button = ttk.Button(
            buttons_frame,
            text="Edit",
            command=lambda: edit_selected_schedule(schedule_tree),
            style="Glass.TButton"
        )
        edit_button.grid(row=0, column=1, sticky="ew", padx=5)
        
        delete_button = ttk.Button(
            buttons_frame,
            text="Delete",
            command=lambda: delete_selected_schedule(schedule_tree),
            style="Glass.TButton"
        )
        delete_button.grid(row=0, column=2, sticky="ew", padx=(5, 0))
        
        # Add visual separator with glass effect
        separator = ttk.Separator(parent, orient="horizontal")
        separator.grid(row=4, column=0, sticky="ew", padx=20, pady=15)
        
        # Add a countdown timer section with glass effect
        countdown_frame = ttk.LabelFrame(
            parent, 
            text="Quick Countdown Timer", 
            style="Glass.TFrame",
            padding=15
        )
        countdown_frame.grid(row=5, column=0, sticky="ew", padx=20, pady=10)
        
        # Add helpful information text with glass effect
        info_text = ttk.Label(
            countdown_frame,
            text="Lock your devices after a countdown, or set a timed auto-unlock duration",
            style="Glass.TLabel",
            wraplength=500
        )
        info_text.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 15))
        
        # Make countdown frame responsive
        countdown_frame.columnconfigure(0, weight=2)
        countdown_frame.columnconfigure(1, weight=3)
        countdown_frame.columnconfigure(2, weight=5)
        
        # Minutes entry with glass styling
        minutes_frame = ttk.Frame(countdown_frame, style="Glass.TFrame")
        minutes_frame.grid(row=1, column=0, sticky="w")
        
        minutes_label = ttk.Label(
            minutes_frame, 
            text="Minutes:", 
            style="Glass.TLabel"
        )
        minutes_label.pack(side="left", padx=(0, 5))
        
        minutes_var = tk.StringVar(value="5")
        minutes_entry = tk.Spinbox(
            minutes_frame,
            from_=1,
            to=60,
            width=3,
            textvariable=minutes_var,
            bg=COLORS["glass_highlight"],
            fg=COLORS["text"],
            font=("Segoe UI", 10, "bold"),
            buttonbackground=COLORS["glass_highlight"],
            relief="flat",
            bd=0
        )
        minutes_entry.pack(side="left")
        
        # Visual countdown display with circular progress bar and glass effect
        countdown_display_frame = ttk.Frame(countdown_frame, style="Glass.TFrame", padding=5)
        countdown_display_frame.grid(row=1, column=1, sticky="ew")
        
        # Create a canvas for the circular progress bar with glass effect
        canvas_size = 120
        canvas = tk.Canvas(
            countdown_display_frame, 
            width=canvas_size, 
            height=canvas_size, 
            bg=COLORS["glass_bg"], 
            highlightthickness=0
        )
        canvas.pack(side="right")
        
        # Draw the progress background (full circle)
        bar_width = 8
        outer_radius = (canvas_size // 2) - 5
        inner_radius = outer_radius - bar_width
        
        # Background circle with glass effect
        canvas.create_oval(
            (canvas_size // 2) - outer_radius,
            (canvas_size // 2) - outer_radius,
            (canvas_size // 2) + outer_radius,
            (canvas_size // 2) + outer_radius,
            outline=COLORS["glass_highlight"],
            width=bar_width,
            fill=COLORS["glass_bg"]
        )
        
        # Progress arc (initially empty)
        progress_arc = canvas.create_arc(
            (canvas_size // 2) - outer_radius,
            (canvas_size // 2) - outer_radius,
            (canvas_size // 2) + outer_radius,
            (canvas_size // 2) + outer_radius,
            start=90,
            extent=0,  # Initially 0 degrees
            outline=COLORS["accent"],
            width=bar_width,
            style="arc"
        )
        
        # Create timer display with glass effect
        timer_var = tk.StringVar(value="Ready")
        timer_display = tk.Label(
            canvas,
            textvariable=timer_var,
            bg=COLORS["glass_bg"],
            fg=COLORS.get("timer_text", COLORS["accent"]),
            font=("Consolas", 14, "bold")
        )
        
        # Position the timer text in the center of the canvas
        canvas.create_window(canvas_size // 2, canvas_size // 2, window=timer_display)
        
        # Store the canvas and progress arc for later use
        parent.timer_canvas = canvas
        parent.progress_arc = progress_arc
        parent.canvas_size = canvas_size
        
        # Store the display variables as attributes for later use
        parent.timer_var = timer_var
        parent.timer_display = timer_display
        
        # Lock type options with glass effect
        lock_type_frame = ttk.Frame(countdown_frame, style="Glass.TFrame")
        lock_type_frame.grid(row=2, column=0, columnspan=2, sticky="w", pady=15)
        
        lock_type_var = tk.StringVar(value="both")
        
        # Add a subtitle for options with glass effect
        lock_type_label = ttk.Label(
            lock_type_frame,
            text="What to lock:",
            style="Glass.TLabel"
        )
        lock_type_label.pack(side="left", padx=(0, 15))
        
        # Use custom radio button style with glass effect
        keyboard_radio = ttk.Radiobutton(
            lock_type_frame,
            text="Keyboard",
            variable=lock_type_var,
            value="keyboard",
            style="Glass.TRadiobutton"
        )
        keyboard_radio.pack(side="left", padx=(0, 10))
        
        mouse_radio = ttk.Radiobutton(
            lock_type_frame,
            text="Mouse",
            variable=lock_type_var,
            value="mouse",
            style="Glass.TRadiobutton"
        )
        mouse_radio.pack(side="left", padx=(0, 10))
        
        both_radio = ttk.Radiobutton(
            lock_type_frame,
            text="Both",
            variable=lock_type_var,
            value="both",
            style="Glass.TRadiobutton"
        )
        both_radio.pack(side="left")
        
        # Duration option for auto-unlock with glass effect
        duration_frame = ttk.Frame(countdown_frame, style="Glass.TFrame")
        duration_frame.grid(row=3, column=0, columnspan=2, sticky="w", pady=(0, 15))
        
        # Create an auto-unlock option with glass effect
        auto_unlock_var = tk.BooleanVar(value=True)
        auto_unlock_check = ttk.Checkbutton(
            duration_frame,
            text="Auto-unlock after",
            variable=auto_unlock_var,
            style="Glass.TCheckbutton"
        )
        auto_unlock_check.pack(side="left", padx=(0, 5))
        
        unlock_minutes_var = tk.StringVar(value="5")
        unlock_minutes_entry = tk.Spinbox(
            duration_frame,
            from_=1,
            to=120,
            width=3,
            textvariable=unlock_minutes_var,
            bg=COLORS["glass_highlight"],
            fg=COLORS["text"],
            font=("Segoe UI", 10),
            buttonbackground=COLORS["glass_highlight"],
            relief="flat",
            bd=0
        )
        unlock_minutes_entry.pack(side="left", padx=(0, 5))
        
        minutes_text = ttk.Label(
            duration_frame,
            text="minutes",
            style="Glass.TLabel"
        )
        minutes_text.pack(side="left")
        
        # Store the auto unlock variables for later use
        parent.auto_unlock_var = auto_unlock_var
        parent.unlock_minutes_var = unlock_minutes_var
        
        # Start button with glass effect
        buttons_container = ttk.Frame(countdown_frame, style="Glass.TFrame")
        buttons_container.grid(row=4, column=0, columnspan=3, sticky="e")
        
        start_button = ttk.Button(
            buttons_container,
            text="Start Countdown",
            command=lambda: start_enhanced_countdown(
                minutes_var.get(), 
                lock_type_var.get(),
                auto_unlock_var.get(),
                unlock_minutes_var.get(),
                timer_var,
                progress_arc,
                canvas
            ),
            style="Glass.TButton"
        )
        start_button.pack(side="right")
        
        # Refresh schedule list periodically
        def refresh_schedule_list():
            update_schedule_tree(schedule_tree)
            parent.after(5000, refresh_schedule_list)
            
        parent.after(5000, refresh_schedule_list)
        
        return schedule_tree
        
    except Exception as e:
        print(f"Error creating scheduler section: {e}\n{traceback.format_exc()}")
        return None


# Enhanced countdown function with visual feedback
def start_enhanced_countdown(minutes_str, lock_type, auto_unlock=True, unlock_minutes="5", timer_var=None, progress_arc=None, canvas=None):
    """
    Start an enhanced countdown timer
    
    Args:
        minutes_str: String representation of minutes
        lock_type: Type of lock ('keyboard', 'mouse', or 'both')
        auto_unlock: Boolean indicating if auto-unlock is enabled
        unlock_minutes: String representation of unlock duration
        timer_var: StringVar to update with countdown information
        progress_arc: ID of the progress arc on canvas
        canvas: Canvas containing the progress arc
    """
    global countdown_active
    
    try:
        # Validate input
        minutes = int(minutes_str)
        if minutes <= 0:
            messagebox.showerror("Error", "Please enter a valid number of minutes")
            return
            
        # Convert to seconds
        seconds = minutes * 60
        countdown_seconds = seconds
        total_seconds = seconds  # Keep track of total seconds for progress calculation
        
        # Update timer display
        if timer_var:
            timer_var.set(f"Countdown: {minutes:02d}:00")
            
        # Reset progress bar
        if progress_arc and canvas:
            canvas.itemconfig(progress_arc, extent=0)
        
        # Create a countdown schedule
        schedule_id = scheduler.generate_id()
        schedule_name = f"Countdown ({minutes} min)"
        
        # Set up auto-unlock if enabled
        duration = None
        if auto_unlock:
            try:
                unlock_minutes_val = int(unlock_minutes)
                if unlock_minutes_val > 0:
                    duration = unlock_minutes_val * 60
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid unlock duration")
                return
        
        # Create the schedule
        schedule = scheduler.Schedule(
            id=schedule_id,
            name=schedule_name,
            action=lock_type,
            time_type="countdown",
            start_time=seconds,
            duration=duration,
            enabled=True
        )
        
        # Add and start the schedule
        if schedule_manager.add_schedule(schedule):
            # Show success message
            device_type = "keyboard and mouse" if lock_type == "both" else lock_type
            
            unlock_msg = ""
            if auto_unlock and duration:
                unlock_duration = int(unlock_minutes)
                unlock_msg = f" and will automatically unlock after {unlock_duration} minute{'s' if unlock_duration != 1 else ''}"
            
            messagebox.showinfo(
                "Countdown Started", 
                f"The {device_type} will be locked in {minutes} minute{'s' if minutes != 1 else ''}{unlock_msg}."
            )
            
            # Set up visual countdown
            def update_countdown():
                nonlocal countdown_seconds
                countdown_seconds -= 1
                
                minutes_left = countdown_seconds // 60
                seconds_left = countdown_seconds % 60
                
                # Update circular progress bar
                if progress_arc and canvas and total_seconds > 0:
                    progress_percentage = 1 - (countdown_seconds / total_seconds)
                    # Convert percentage to degrees (360 degrees = full circle)
                    extent = progress_percentage * -360
                    canvas.itemconfig(progress_arc, extent=extent)
                
                if countdown_seconds >= 0 and timer_var:
                    timer_var.set(f"Countdown: {minutes_left:02d}:{seconds_left:02d}")
                    root.after(1000, update_countdown)
                else:
                    if timer_var:
                        if auto_unlock and duration:
                            # Start the unlock countdown after locking
                            unlock_seconds = duration
                            total_unlock_seconds = duration  # For progress calculation
                            timer_var.set(f"Locked: {unlock_minutes:02d}:00")
                            
                            # Reset progress bar for unlock countdown
                            if progress_arc and canvas:
                                canvas.itemconfig(progress_arc, extent=0, outline="#28a745")  # Green for unlocking
                            
                            def update_unlock_countdown():
                                nonlocal unlock_seconds
                                unlock_seconds -= 1
                                
                                unlock_mins = unlock_seconds // 60
                                unlock_secs = unlock_seconds % 60
                                
                                # Update circular progress bar for unlock countdown
                                if progress_arc and canvas and total_unlock_seconds > 0:
                                    unlock_progress = 1 - (unlock_seconds / total_unlock_seconds)
                                    unlock_extent = unlock_progress * -360
                                    canvas.itemconfig(progress_arc, extent=unlock_extent)
                                
                                if unlock_seconds >= 0 and timer_var:
                                    timer_var.set(f"Unlocks in: {unlock_mins:02d}:{unlock_secs:02d}")
                                    root.after(1000, update_unlock_countdown)
                                else:
                                    timer_var.set("Unlocked")
                                    # Reset progress bar color
                                    if progress_arc and canvas:
                                        canvas.itemconfig(progress_arc, extent=0, outline=COLORS["accent"])
                                    root.after(3000, lambda: timer_var.set("Ready"))
                            
                            root.after(1000, update_unlock_countdown)
                        else:
                            timer_var.set("Locked")
                            # Reset progress bar
                            if progress_arc and canvas:
                                canvas.itemconfig(progress_arc, extent=0)
            
            root.after(1000, update_countdown)
        else:
            messagebox.showerror("Error", "Failed to start countdown")
        
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid number of minutes")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start countdown: {e}")
        print(f"Error starting countdown: {e}\n{traceback.format_exc()}")


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


def cleanup():
    """Cleanup resources when exiting"""
    try:
        if schedule_manager:
            schedule_manager.stop()
    except Exception as e:
        print(f"Error during cleanup: {e}")


def main():
    """Main entry point of the application"""
    global root, keyboard_status, mouse_status, config, shortcut, main_content
    
    try:
        # Initialize application
        if not initialize_app():
            return
        
        # Create the UI
        create_ui()
        
        # Apply transparency based on settings
        transparency_value = int(config.get("transparency", "85"))
        apply_transparency(transparency_value)
        
        # Create remaining UI sections
        if main_content:
            create_status_section(main_content)
            
            # Footer with credits
            footer_frame = ttk.Frame(main_content, style="Glass.TFrame")
            footer_frame.grid(row=99, column=0, sticky="ew", pady=(15, 5), padx=15)
            
            footer = ttk.Label(
                footer_frame,
                text="Press '" + shortcut.get() + "' to unlock",
                style="Glass.Footer.TLabel"
            )
            footer.pack(side="left")
            
            version_text = ttk.Label(
                footer_frame,
                text="KeyLock v1.0",
                style="Glass.Footer.TLabel"
            )
            version_text.pack(side="right")
        
        # Set up auto-lock based on config
        if config.get("onstart_lock_keyboard", "false").lower() == "true":
            safe_lock_keyboard()
            
        if config.get("onstart_lock_mouse", "false").lower() == "true":
            safe_lock_mouse()
        
        # Set up scheduled checks
        root.after(refresh_rate, check_change)
        
        # Update footer
        update_footer()
        
        # The ScheduleManager already loads schedules in its _scheduler_loop method
        # We don't need to call load_schedules() explicitly
        # schedule_manager.load_schedules()  # <- This caused the AttributeError
        
        # Center window and apply theme
        center_window(root)
        
        # Start the main loop
        root.mainloop()
        
    except Exception as e:
        error_msg = f"Error in main function: {e}\n{traceback.format_exc()}"
        print(error_msg)
        try:
            messagebox.showerror("Application Error", f"An error occurred: {e}")
        except:
            pass
        return


def apply_transparency(transparency_value):
    """Apply transparency effect to the main window with blur if supported"""
    try:
        # Convert percentage to alpha value (0-1)
        alpha = transparency_value / 100
        
        # Windows-specific transparency with blur
        if os.name == "nt":
            try:
                from ctypes import windll, c_int, byref, sizeof
                
                # Try to apply acrylic/blur effect (Windows 10/11)
                try:
                    # Windows 10 1903+ supports Acrylic blur
                    ACCENT_ENABLE_BLURBEHIND = 3
                    ACCENT_ENABLE_ACRYLICBLURBEHIND = 4
                    
                    class ACCENTPOLICY(ctypes.Structure):
                        _fields_ = [
                            ("AccentState", ctypes.c_uint),
                            ("AccentFlags", ctypes.c_uint),
                            ("GradientColor", ctypes.c_uint),
                            ("AnimationId", ctypes.c_uint)
                        ]
                    
                    class WINDOWCOMPOSITIONATTRIBDATA(ctypes.Structure):
                        _fields_ = [
                            ("Attribute", ctypes.c_int),
                            ("Data", ctypes.POINTER(ctypes.c_int)),
                            ("SizeOfData", ctypes.c_size_t)
                        ]
                    
                    # First try Acrylic blur (more modern)
                    accent = ACCENTPOLICY()
                    accent.AccentState = ACCENT_ENABLE_ACRYLICBLURBEHIND
                    accent.GradientColor = (int(alpha * 255) << 24) | (0x990000 & 0xFFFFFF)  # AABBGGRR format
                    
                    data = WINDOWCOMPOSITIONATTRIBDATA()
                    data.Attribute = 19  # WCA_ACCENT_POLICY
                    data.SizeOfData = ctypes.sizeof(accent)
                    data.Data = ctypes.cast(ctypes.pointer(accent), ctypes.POINTER(ctypes.c_int))
                    
                    SetWindowCompositionAttribute = windll.user32.SetWindowCompositionAttribute
                    SetWindowCompositionAttribute.argtypes = [ctypes.c_int, ctypes.POINTER(WINDOWCOMPOSITIONATTRIBDATA)]
                    SetWindowCompositionAttribute.restype = ctypes.c_int
                    
                    hwnd = windll.user32.GetParent(root.winfo_id())
                    
                    # Try acrylic first, fall back to regular blur if not supported
                    if not SetWindowCompositionAttribute(hwnd, byref(data)):
                        accent.AccentState = ACCENT_ENABLE_BLURBEHIND
                        if not SetWindowCompositionAttribute(hwnd, byref(data)):
                            # If both fail, use basic transparency
                            root.attributes("-alpha", alpha)
                    
                except Exception as blur_error:
                    print(f"Could not apply blur effect: {blur_error}")
                    # Fall back to basic transparency
                    root.attributes("-alpha", alpha)
                
            except Exception as e:
                print(f"Error setting Windows transparency: {e}")
                # Fallback to basic transparency
                root.attributes("-alpha", alpha)
                
        # macOS transparency
        elif sys.platform == "darwin":
            try:
                root.attributes("-alpha", alpha)
                # macOS doesn't support window blur via Tkinter,
                # but the alpha transparency looks nice with system styles
            except Exception as e:
                print(f"Error setting macOS transparency: {e}")
                
        # Linux transparency - may differ based on window manager
        else:
            try:
                root.attributes("-alpha", alpha)
            except Exception as e:
                print(f"Error setting transparency: {e}")
                
    except Exception as e:
        print(f"Could not apply transparency: {e}")


if __name__ == "__main__":
    sys.exit(main())
