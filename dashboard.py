import tkinter as tk
from tkinter import ttk
import os
import sys
import core
import controller
import scheduler
from ui_components import ThemedFrame, ThemedButton, ResponsiveGrid, Card, CollapsibleCard
from utils import resource_path

class KeylockDashboard:
    """Modern dashboard UI for KeyLock application"""
    
    def __init__(self, root=None):
        """Initialize the dashboard"""
        self.root = root or tk.Tk()
        self.root.title("KeyLock Dashboard")
        self.root.minsize(800, 600)
        
        # Try to load theme from settings first
        try:
            from settings import open_config
            config = open_config()
            self.theme = config.get("theme", "light")
        except Exception:
            # Default to light theme if there's an error
            self.theme = "light"
            
        # Theme and colors based on the theme
        if self.theme == "dark":
            self.colors = {
                "bg": "#1E1E1E",           # Dark background
                "dark_bg": "#252526",      # Darker background
                "accent": "#0078D7",       # Primary accent color
                "accent_hover": "#106EBE",  # Accent hover state
                "text": "#FFFFFF",         # Main text color
                "secondary_text": "#CCCCCC", # Secondary text color
                "success": "#28a745",      # Success color
                "warning": "#ffc107",      # Warning color
                "error": "#dc3545",        # Error color
                "card_bg": "#2D2D30",      # Card background
                "card_border": "#3E3E42",  # Card border
                "glass_bg": "#2D2D3099"    # Semi-transparent background
            }
        else:
            self.colors = {
                "bg": "#F5F5F5",           # Light background
                "dark_bg": "#2D2D30",      # Dark background
                "accent": "#0078D7",       # Primary accent color
                "accent_hover": "#106EBE",  # Accent hover state
                "text": "#333333",         # Main text color
                "secondary_text": "#777777", # Secondary text color
                "success": "#28a745",      # Success color
                "warning": "#ffc107",      # Warning color
                "error": "#dc3545",        # Error color
                "card_bg": "#FFFFFF",      # Card background
                "card_border": "#E5E5E5",  # Card border
                "glass_bg": "#FFFFFF99"    # Semi-transparent background
            }
        
        # State variables
        self.keyboard_locked = False
        self.mouse_locked = False
        self.timer_running = False
        self.scheduler_running = False
        self.current_view = "dashboard"
        
        # Setup UI
        self._setup_ui()
        
        # Initialize core components
        self._initialize_components()
        
    def _setup_ui(self):
        """Setup the main UI structure"""
        # Configure the window
        self.root.configure(bg=self.colors["bg"])
        
        # Create main frames
        self.sidebar = ThemedFrame(self.root, bg=self.colors["dark_bg"])
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=0, pady=0)
        
        self.main_area = ThemedFrame(self.root, bg=self.colors["bg"])
        self.main_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Create sidebar navigation
        self._create_sidebar()
        
        # Create theme toggle button
        self.theme_btn = tk.Button(
            self.root,
            text="🌙" if self.theme == "light" else "☀️",  # Set icon based on current theme
            font=("Segoe UI", 14),
            bg=self.colors["bg"],
            fg=self.colors["text"],
            bd=0,
            padx=10,
            pady=5,
            cursor="hand2",
            command=self._toggle_theme
        )
        self.theme_btn.place(relx=1.0, y=0, anchor="ne")
        
        # Create main dashboard view
        self._create_dashboard_view()
        
    def _create_sidebar(self):
        """Create the sidebar with navigation links"""
        # App title
        title_frame = ThemedFrame(self.sidebar, bg=self.colors["dark_bg"])
        title_frame.pack(fill=tk.X, padx=15, pady=(20, 15))
        
        title_label = tk.Label(
            title_frame, 
            text="KeyLock",
            font=("Segoe UI", 18, "bold"),
            bg=self.colors["dark_bg"],
            fg="#FFFFFF"
        )
        title_label.pack(anchor=tk.W)
        
        version_label = tk.Label(
            title_frame, 
            text="v2.0",
            font=("Segoe UI", 10),
            bg=self.colors["dark_bg"],
            fg="#AAAAAA"
        )
        version_label.pack(anchor=tk.W)
        
        # Navigation links
        nav_frame = ThemedFrame(self.sidebar, bg=self.colors["dark_bg"])
        nav_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=(20, 0))
        
        self._create_nav_button(nav_frame, "Dashboard", "dashboard", True)
        self._create_nav_button(nav_frame, "Settings", "settings")
        
        # Bottom buttons
        bottom_frame = ThemedFrame(self.sidebar, bg=self.colors["dark_bg"])
        bottom_frame.pack(fill=tk.X, padx=15, pady=15)
        
        help_button = tk.Label(
            bottom_frame,
            text="Help & Support",
            font=("Segoe UI", 10),
            bg=self.colors["dark_bg"],
            fg="#AAAAAA",
            cursor="hand2"
        )
        help_button.pack(anchor=tk.W, pady=(0, 5))
        help_button.bind("<Button-1>", lambda e: self._show_help())
        
        exit_button = tk.Label(
            bottom_frame,
            text="Exit",
            font=("Segoe UI", 10),
            bg=self.colors["dark_bg"],
            fg="#AAAAAA",
            cursor="hand2"
        )
        exit_button.pack(anchor=tk.W)
        exit_button.bind("<Button-1>", lambda e: self._safe_exit())
        
    def _create_nav_button(self, parent, text, view_name, is_active=False):
        """Create a navigation button in the sidebar"""
        bg_color = self.colors["accent"] if is_active else self.colors["dark_bg"]
        fg_color = "#FFFFFF" if is_active else "#CCCCCC"
        
        nav_button = tk.Frame(
            parent,
            bg=bg_color,
            cursor="hand2",
            padx=15,
            pady=10
        )
        nav_button.pack(fill=tk.X, pady=1)
        
        label = tk.Label(
            nav_button,
            text=text,
            font=("Segoe UI", 12),
            bg=bg_color,
            fg=fg_color
        )
        label.pack(anchor=tk.W)
        
        # Bind click event
        nav_button.bind("<Button-1>", lambda e, v=view_name: self._switch_view(v))
        label.bind("<Button-1>", lambda e, v=view_name: self._switch_view(v))
        
        # Hover effects
        def on_enter(e):
            if view_name != self.current_view:
                nav_button.configure(bg=self.colors["accent_hover"])
                label.configure(bg=self.colors["accent_hover"])
        
        def on_leave(e):
            if view_name != self.current_view:
                nav_button.configure(bg=self.colors["dark_bg"])
                label.configure(bg=self.colors["dark_bg"])
        
        nav_button.bind("<Enter>", on_enter)
        nav_button.bind("<Leave>", on_leave)
        label.bind("<Enter>", on_enter)
        label.bind("<Leave>", on_leave)
    
    def _create_dashboard_view(self):
        """Create the main dashboard view"""
        # Clear existing widgets
        for widget in self.main_area.winfo_children():
            widget.destroy()
        
        # Create header
        header = ThemedFrame(self.main_area, bg=self.colors["bg"])
        header.pack(fill=tk.X, padx=20, pady=20)
        
        title = tk.Label(
            header,
            text="Dashboard",
            font=("Segoe UI", 22, "bold"),
            bg=self.colors["bg"],
            fg=self.colors["text"]
        )
        title.pack(side=tk.LEFT)
        
        # Quick action buttons
        btn_frame = ThemedFrame(header, bg=self.colors["bg"])
        btn_frame.pack(side=tk.RIGHT)
        
        countdown_btn = ThemedButton(
            btn_frame,
            text="Start Countdown",
            command=self._start_countdown,
            width=15,
            bg=self.colors["accent"],
            fg="#FFFFFF"
        )
        countdown_btn.pack(side=tk.LEFT, padx=5)
        
        lock_all_btn = ThemedButton(
            btn_frame,
            text="Lock All Devices",
            command=self._lock_all_devices,
            width=15,
            bg=self.colors["accent"],
            fg="#FFFFFF"
        )
        lock_all_btn.pack(side=tk.LEFT, padx=5)
        
        # Status cards
        cards_frame = ResponsiveGrid(self.main_area, columns=2, padding=10)
        cards_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Device status card
        device_card = Card(cards_frame, title="Device Status", bg=self.colors["card_bg"])
        cards_frame.add_widget(device_card, 0, 0, rowspan=1, colspan=1)
        
        # Create keyboard status display
        kb_frame = ThemedFrame(device_card.content_frame, bg=self.colors["card_bg"])
        kb_frame.pack(fill=tk.X, pady=5)
        
        # Load keyboard icon
        try:
            kb_icon_path = resource_path("assets/keyboard.png")
            self.kb_icon = tk.PhotoImage(file=kb_icon_path)
            # Resize icon if needed
            self.kb_icon = self.kb_icon.subsample(9,9)
            
            # Create label with icon
            kb_icon_label = tk.Label(
                kb_frame,
                image=self.kb_icon,
                bg=self.colors["card_bg"]
            )
            kb_icon_label.pack(side=tk.LEFT, padx=(0, 5))
        except Exception as e:
            print(f"Error loading keyboard icon: {str(e)}")
        
        kb_label = tk.Label(
            kb_frame,
            text="Keyboard:",
            font=("Segoe UI", 11),
            bg=self.colors["card_bg"],
            fg=self.colors["text"]
        )
        kb_label.pack(side=tk.LEFT, padx=(0, 10))
        
        kb_status = tk.Label(
            kb_frame,
            text="Unlocked",
            font=("Segoe UI", 11),
            bg=self.colors["success"],
            fg="#FFFFFF",
            padx=8,
            pady=2,
            borderwidth=0
        )
        kb_status.pack(side=tk.LEFT)
        self.kb_status_label = kb_status
        
        kb_toggle = ThemedButton(
            kb_frame,
            text="Lock",
            command=self._toggle_keyboard,
            width=8
        )
        kb_toggle.pack(side=tk.RIGHT)
        self.kb_toggle_btn = kb_toggle
        
        # Create mouse status display
        mouse_frame = ThemedFrame(device_card.content_frame, bg=self.colors["card_bg"])
        mouse_frame.pack(fill=tk.X, pady=5)
        
        # Load mouse icon
        try:
            mouse_icon_path = resource_path("assets/mous.png")
            self.mouse_icon = tk.PhotoImage(file=mouse_icon_path)
            # Resize icon if needed
            self.mouse_icon = self.mouse_icon.subsample(9,9)
            
            # Create label with icon
            mouse_icon_label = tk.Label(
                mouse_frame,
                image=self.mouse_icon,
                bg=self.colors["card_bg"]
            )
            mouse_icon_label.pack(side=tk.LEFT, padx=(0, 5))
        except Exception as e:
            print(f"Error loading mouse icon: {str(e)}")
        
        mouse_label = tk.Label(
            mouse_frame,
            text="Mouse:     ",
            font=("Segoe UI", 11),
            bg=self.colors["card_bg"],
            fg=self.colors["text"]
        )
        mouse_label.pack(side=tk.LEFT, padx=(0, 10))
        
        mouse_status = tk.Label(
            mouse_frame,
            text="Unlocked",
            font=("Segoe UI", 11),
            bg=self.colors["success"],
            fg="#FFFFFF",
            padx=8,
            pady=2,
            borderwidth=0
        )
        mouse_status.pack(side=tk.LEFT)
        self.mouse_status_label = mouse_status
        
        mouse_toggle = ThemedButton(
            mouse_frame,
            text="Lock",
            command=self._toggle_mouse,
            width=8
        )
        mouse_toggle.pack(side=tk.RIGHT)
        self.mouse_toggle_btn = mouse_toggle
        
        # Timer card
        timer_card = Card(cards_frame, title="Timer", bg=self.colors["card_bg"])
        cards_frame.add_widget(timer_card, 0, 1, rowspan=1, colspan=1)
        
        timer_value = tk.Label(
            timer_card.content_frame,
            text="00:00:00",
            font=("Segoe UI", 24, "bold"),
            bg=self.colors["card_bg"],
            fg=self.colors["text"]
        )
        timer_value.pack(pady=10)
        self.timer_label = timer_value
        
        timer_controls = ThemedFrame(timer_card.content_frame, bg=self.colors["card_bg"])
        timer_controls.pack(pady=5)
        
        preset_frame = ThemedFrame(timer_card.content_frame, bg=self.colors["card_bg"])
        preset_frame.pack(pady=5, fill=tk.X)
        
        tk.Label(
            preset_frame,
            text="Quick presets:",
            font=("Segoe UI", 10),
            bg=self.colors["card_bg"],
            fg=self.colors["text"]
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        for minutes in ["5", "10", "30", "60"]:
            preset_btn = ThemedButton(
                preset_frame,
                text=f"{minutes}m",
                command=lambda m=minutes: self._start_preset_timer(m),
                width=4,
                bg=self.colors["bg"],
                fg=self.colors["text"]
            )
            preset_btn.pack(side=tk.LEFT, padx=3)
        
        # Upcoming schedules card
        schedule_card = Card(cards_frame, title="Next Scheduled Events", bg=self.colors["card_bg"])
        cards_frame.add_widget(schedule_card, 1, 0, rowspan=1, colspan=2)
        
        # Create schedule list with a scrollbar
        schedule_frame = ThemedFrame(schedule_card.content_frame, bg=self.colors["card_bg"])
        schedule_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        schedule_list = ttk.Treeview(
            schedule_frame,
            columns=("name", "time", "action", "duration"),
            show="headings",
            height=5
        )
        schedule_list.heading("name", text="Name")
        schedule_list.heading("time", text="Time")
        schedule_list.heading("action", text="Action")
        schedule_list.heading("duration", text="Duration")
        
        schedule_list.column("name", width=150)
        schedule_list.column("time", width=150)
        schedule_list.column("action", width=100)
        schedule_list.column("duration", width=100)
        
        scrollbar = ttk.Scrollbar(schedule_frame, orient="vertical", command=schedule_list.yview)
        schedule_list.configure(yscrollcommand=scrollbar.set)
        
        schedule_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.schedule_list = schedule_list
        
        # Sample data for now
        schedule_list.insert("", tk.END, values=("Work Focus", "14:00", "Both", "60 min"))
        schedule_list.insert("", tk.END, values=("Break Time", "16:30", "Both", "15 min"))
        
        # Footer with status
        footer = ThemedFrame(self.main_area, bg=self.colors["bg"])
        footer.pack(fill=tk.X, padx=20, pady=10)
        
        status_label = tk.Label(
            footer,
            text="Ready",
            font=("Segoe UI", 10),
            bg=self.colors["bg"],
            fg=self.colors["secondary_text"]
        )
        status_label.pack(side=tk.LEFT)
        self.status_label = status_label
        
        # Show success message on initial load
        self.update_status("Application loaded successfully")
    
    def _create_devices_view(self):
        """Create the devices control view"""
        # To be implemented
        pass
    
    def _create_scheduler_view(self):
        """Create the scheduler view"""
        # To be implemented
        pass
        
    def _create_stats_view(self):
        """Create the statistics view"""
        # To be implemented
        pass
        
    def _create_settings_view(self):
        """Create the settings view"""
        # Clear existing widgets
        for widget in self.main_area.winfo_children():
            widget.destroy()
        
        # Create header
        header = ThemedFrame(self.main_area, bg=self.colors["bg"])
        header.pack(fill=tk.X, padx=20, pady=20)
        
        title = tk.Label(
            header,
            text="Settings",
            font=("Segoe UI", 22, "bold"),
            bg=self.colors["bg"],
            fg=self.colors["text"]
        )
        title.pack(side=tk.LEFT)
        
        # Settings container
        settings_frame = ThemedFrame(self.main_area, bg=self.colors["bg"])
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=0)
        
        # Appearance section
        appearance_card = Card(settings_frame, title="Appearance", bg=self.colors["card_bg"])
        appearance_card.pack(fill=tk.X, pady=10)
        
        # Theme selection
        theme_frame = ThemedFrame(appearance_card.content_frame, bg=self.colors["card_bg"])
        theme_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            theme_frame,
            text="Theme:",
            font=("Segoe UI", 11),
            bg=self.colors["card_bg"],
            fg=self.colors["text"]
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        theme_var = tk.StringVar(value="light")  # Default theme
        
        # Update theme_var to current theme if available
        if hasattr(self, 'theme'):
            theme_var.set(self.theme)
        
        theme_options = ttk.Combobox(
            theme_frame,
            textvariable=theme_var,
            values=["light", "dark"],
            width=15,
            state="readonly"
        )
        theme_options.pack(side=tk.LEFT)
        
        # Apply button
        apply_theme_btn = ThemedButton(
            theme_frame,
            text="Apply",
            command=lambda: self._apply_theme_from_settings(theme_var.get()),
            bg=self.colors["accent"],
            fg="#FFFFFF",
            width=8
        )
        apply_theme_btn.pack(side=tk.RIGHT)
        
        # Transparency settings
        transparency_frame = ThemedFrame(appearance_card.content_frame, bg=self.colors["card_bg"])
        transparency_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(
            transparency_frame,
            text="Window Opacity:",
            font=("Segoe UI", 11),
            bg=self.colors["card_bg"],
            fg=self.colors["text"]
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        transparency_var = tk.IntVar(value=100)  # Default 100%
        
        transparency_scale = ttk.Scale(
            transparency_frame,
            from_=50,
            to=100,
            orient=tk.HORIZONTAL,
            variable=transparency_var,
            length=200
        )
        transparency_scale.pack(side=tk.LEFT, padx=(0, 10))
        
        transparency_label = tk.Label(
            transparency_frame,
            text="100%",
            bg=self.colors["card_bg"],
            fg=self.colors["text"]
        )
        transparency_label.pack(side=tk.LEFT)
        
        # Update transparency label when scale changes
        def update_transparency_label(event=None):
            value = transparency_var.get()
            transparency_label.configure(text=f"{value}%")
            # Placeholder for applying transparency
            self.update_status(f"Opacity set to {value}%")
        
        transparency_scale.bind("<Motion>", update_transparency_label)
        transparency_scale.bind("<ButtonRelease-1>", update_transparency_label)
        
        # Behavior Section
        behavior_card = CollapsibleCard(
            settings_frame,
            title="Behavior",
            bg=self.colors["card_bg"],
            fg=self.colors["text"],
            accent=self.colors["accent"]
        )
        behavior_card.pack(fill=tk.X, pady=10, padx=20)
        
        # Keyboard Lock Mode
        keyboard_frame = ThemedFrame(behavior_card.content_frame, bg=self.colors["card_bg"])
        keyboard_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(
            keyboard_frame,
            text="Keyboard Lock Mode:",
            font=("Segoe UI", 11),
            bg=self.colors["card_bg"],
            fg=self.colors["text"]
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        keyboard_mode_var = tk.StringVar(value="Full Lock")
        keyboard_modes = ["Full Lock", "Allow Shortcuts", "Custom"]
        
        keyboard_mode_combo = ttk.Combobox(
            keyboard_frame,
            textvariable=keyboard_mode_var,
            values=keyboard_modes,
            state="readonly",
            width=15
        )
        keyboard_mode_combo.pack(side=tk.LEFT)
        keyboard_mode_combo.bind("<<ComboboxSelected>>", 
                                lambda e: self.update_status(f"Keyboard mode set to {keyboard_mode_var.get()}"))
        
        # Mouse Lock Mode
        mouse_frame = ThemedFrame(behavior_card.content_frame, bg=self.colors["card_bg"])
        mouse_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(
            mouse_frame,
            text="Mouse Lock Mode:",
            font=("Segoe UI", 11),
            bg=self.colors["card_bg"],
            fg=self.colors["text"]
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        mouse_mode_var = tk.StringVar(value="Full Lock")
        mouse_modes = ["Full Lock", "Restrict Area", "Disable Clicks"]
        
        mouse_mode_combo = ttk.Combobox(
            mouse_frame,
            textvariable=mouse_mode_var,
            values=mouse_modes,
            state="readonly",
            width=15
        )
        mouse_mode_combo.pack(side=tk.LEFT)
        mouse_mode_combo.bind("<<ComboboxSelected>>", 
                            lambda e: self.update_status(f"Mouse mode set to {mouse_mode_var.get()}"))
        
        # Save settings button
        save_frame = ThemedFrame(settings_frame, bg=self.colors["bg"])
        save_frame.pack(fill=tk.X, pady=20)
        
        save_btn = ThemedButton(
            save_frame,
            text="Save Settings",
            command=lambda: self._save_settings(theme_var.get()),
            bg=self.colors["accent"],
            fg="#FFFFFF",
            width=15
        )
        save_btn.pack(side=tk.RIGHT)
        
        # Footer with status
        footer = ThemedFrame(self.main_area, bg=self.colors["bg"])
        footer.pack(fill=tk.X, padx=20, pady=10)
        
        status_label = tk.Label(
            footer,
            text="Settings loaded",
            font=("Segoe UI", 10),
            bg=self.colors["bg"],
            fg=self.colors["secondary_text"]
        )
        status_label.pack(side=tk.LEFT)
        self.status_label = status_label
    
    def _switch_view(self, view_name):
        """Switch between different views"""
        if view_name == self.current_view:
            return
            
        self.current_view = view_name
        
        # Rebuild sidebar to update active state
        for widget in self.sidebar.winfo_children():
            widget.destroy()
        self._create_sidebar()
        
        # Show the selected view
        if view_name == "dashboard":
            self._create_dashboard_view()
        elif view_name == "settings":
            self._create_settings_view()
        # Fallback to dashboard for removed views
        elif view_name in ["devices", "scheduler", "stats"]:
            self.current_view = "dashboard"
            self._create_dashboard_view()
            self.update_status("This view is no longer available")
    
    def _initialize_components(self):
        """Initialize core components and timers"""
        # Start a periodic check for updates
        self._check_state()
    
    def _check_state(self):
        """Periodically check state and update UI"""
        try:
            # Check keyboard and mouse status
            self.keyboard_locked = core.is_keyboard_locked()
            self.mouse_locked = core.is_mouse_locked()
            
            # Update status indicators
            self._update_status_indicators()
            
            # Schedule next check
            self.root.after(1000, self._check_state)
        except Exception as e:
            self.update_status(f"Error checking state: {str(e)}")
    
    def _update_status_indicators(self):
        """Update the status indicators in the UI"""
        # Update keyboard status
        if self.keyboard_locked:
            self.kb_status_label.configure(text="Locked", bg=self.colors["error"])
            self.kb_toggle_btn.configure(text="Unlock")
        else:
            self.kb_status_label.configure(text="Unlocked", bg=self.colors["success"])
            self.kb_toggle_btn.configure(text="Lock")
        
        # Update mouse status
        if self.mouse_locked:
            self.mouse_status_label.configure(text="Locked", bg=self.colors["error"])
            self.mouse_toggle_btn.configure(text="Unlock")
        else:
            self.mouse_status_label.configure(text="Unlocked", bg=self.colors["success"])
            self.mouse_toggle_btn.configure(text="Lock")
    
    def _toggle_keyboard(self):
        """Toggle the keyboard lock state"""
        try:
            if self.keyboard_locked:
                core.unlock_keyboard()
                self.update_status("Keyboard unlocked")
            else:
                core.lock_keyboard()
                self.update_status("Keyboard locked")
        except Exception as e:
            self.update_status(f"Error toggling keyboard: {str(e)}")
    
    def _toggle_mouse(self):
        """Toggle the mouse lock state"""
        try:
            if self.mouse_locked:
                core.unlock_mouse()
                self.update_status("Mouse unlocked")
            else:
                core.lock_mouse()
                self.update_status("Mouse locked")
        except Exception as e:
            self.update_status(f"Error toggling mouse: {str(e)}")
    
    def _lock_all_devices(self):
        """Lock both keyboard and mouse"""
        try:
            if not self.keyboard_locked:
                core.lock_keyboard()
            if not self.mouse_locked:
                core.lock_mouse()
            self.update_status("All devices locked")
        except Exception as e:
            self.update_status(f"Error locking devices: {str(e)}")
    
    def _start_countdown(self):
        """Open dialog to start a countdown timer"""
        try:
            # Create countdown dialog
            dialog = tk.Toplevel(self.root)
            dialog.title("Start Countdown")
            dialog.geometry("300x200")
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Center dialog
            dialog.update_idletasks()
            x = self.root.winfo_rootx() + (self.root.winfo_width() - dialog.winfo_width()) // 2
            y = self.root.winfo_rooty() + (self.root.winfo_height() - dialog.winfo_height()) // 2
            dialog.geometry(f"+{x}+{y}")
            
            # Create form
            frame = ThemedFrame(dialog, bg=self.colors["bg"])
            frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # Duration selection
            tk.Label(
                frame, 
                text="Lock Duration (minutes):", 
                bg=self.colors["bg"],
                fg=self.colors["text"]
            ).pack(anchor=tk.W, pady=(0, 5))
            
            minutes_var = tk.StringVar(value="5")
            minutes_entry = tk.Entry(frame, textvariable=minutes_var, width=10)
            minutes_entry.pack(anchor=tk.W, pady=(0, 15))
            
            # Lock type selection
            tk.Label(
                frame, 
                text="Lock Type:", 
                bg=self.colors["bg"],
                fg=self.colors["text"]
            ).pack(anchor=tk.W, pady=(0, 5))
            
            lock_type_var = tk.StringVar(value="both")
            
            rb_frame = ThemedFrame(frame, bg=self.colors["bg"])
            rb_frame.pack(anchor=tk.W, pady=(0, 15))
            
            tk.Radiobutton(
                rb_frame, 
                text="Keyboard Only", 
                variable=lock_type_var, 
                value="keyboard",
                bg=self.colors["bg"],
                fg=self.colors["text"]
            ).pack(side=tk.LEFT, padx=(0, 10))
            
            tk.Radiobutton(
                rb_frame, 
                text="Mouse Only", 
                variable=lock_type_var, 
                value="mouse",
                bg=self.colors["bg"],
                fg=self.colors["text"]
            ).pack(side=tk.LEFT, padx=(0, 10))
            
            tk.Radiobutton(
                rb_frame, 
                text="Both", 
                variable=lock_type_var, 
                value="both",
                bg=self.colors["bg"],
                fg=self.colors["text"]
            ).pack(side=tk.LEFT)
            
            # Auto unlock option
            auto_unlock_var = tk.BooleanVar(value=True)
            tk.Checkbutton(
                frame, 
                text="Auto unlock after timer finishes", 
                variable=auto_unlock_var,
                bg=self.colors["bg"],
                fg=self.colors["text"]
            ).pack(anchor=tk.W, pady=(0, 15))
            
            # Buttons
            btn_frame = ThemedFrame(frame, bg=self.colors["bg"])
            btn_frame.pack(fill=tk.X, pady=(10, 0))
            
            def on_start():
                try:
                    minutes = minutes_var.get()
                    lock_type = lock_type_var.get()
                    auto_unlock = auto_unlock_var.get()
                    
                    # Close dialog
                    dialog.destroy()
                    
                    # Start the timer
                    self._start_timer(minutes, lock_type, auto_unlock)
                except Exception as e:
                    self.update_status(f"Error starting timer: {str(e)}")
                    dialog.destroy()
            
            ThemedButton(
                btn_frame,
                text="Start",
                command=on_start,
                bg=self.colors["accent"],
                fg="#FFFFFF"
            ).pack(side=tk.RIGHT, padx=(5, 0))
            
            ThemedButton(
                btn_frame,
                text="Cancel",
                command=dialog.destroy,
                bg=self.colors["bg"],
                fg=self.colors["text"]
            ).pack(side=tk.RIGHT)
            
        except Exception as e:
            self.update_status(f"Error opening countdown dialog: {str(e)}")
    
    def _start_preset_timer(self, minutes):
        """Start a preset timer"""
        self._start_timer(minutes, "both", True)
    
    def _start_timer(self, minutes, lock_type="both", auto_unlock=True):
        """Start a timer with the specified duration and lock type"""
        try:
            # Convert minutes to integer
            minutes = int(minutes)
            if minutes <= 0:
                raise ValueError("Duration must be positive")
            
            # Start appropriate locks
            if lock_type == "keyboard" or lock_type == "both":
                if not self.keyboard_locked:
                    core.lock_keyboard()
            
            if lock_type == "mouse" or lock_type == "both":
                if not self.mouse_locked:
                    core.lock_mouse()
            
            # Update status
            self.update_status(f"Started {minutes} minute timer with {lock_type} lock")
            
            # Initialize timer variables
            self.timer_running = True
            self.timer_duration = minutes * 60  # Convert to seconds
            self.timer_remaining = self.timer_duration
            self.timer_start_time = self.root.after_idle(self._update_timer)
            
            # Store auto-unlock setting
            self.timer_auto_unlock = auto_unlock
            
        except Exception as e:
            self.update_status(f"Error starting timer: {str(e)}")
    
    def _update_timer(self):
        """Update the timer display"""
        if not self.timer_running or not hasattr(self, 'timer_remaining'):
            # Reset timer display
            self.timer_label.configure(text="00:00:00")
            return
        
        # Update the remaining time
        self.timer_remaining -= 1
        
        # Format time as HH:MM:SS
        hours = self.timer_remaining // 3600
        minutes = (self.timer_remaining % 3600) // 60
        seconds = self.timer_remaining % 60
        time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
        
        # Update the label
        self.timer_label.configure(text=time_str)
        
        # Check if timer has finished
        if self.timer_remaining <= 0:
            self.timer_running = False
            
            # Auto-unlock if enabled
            if hasattr(self, 'timer_auto_unlock') and self.timer_auto_unlock:
                if self.keyboard_locked:
                    core.unlock_keyboard()
                if self.mouse_locked:
                    core.unlock_mouse()
                self.update_status("Timer completed - devices unlocked")
            else:
                self.update_status("Timer completed")
        else:
            # Schedule next update in 1 second
            self.root.after(1000, self._update_timer)
    
    def _show_help(self):
        """Show help and support information"""
        try:
            # Create help dialog
            dialog = tk.Toplevel(self.root)
            dialog.title("KeyLock Help")
            dialog.geometry("500x400")
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Center dialog
            dialog.update_idletasks()
            x = self.root.winfo_rootx() + (self.root.winfo_width() - dialog.winfo_width()) // 2
            y = self.root.winfo_rooty() + (self.root.winfo_height() - dialog.winfo_height()) // 2
            dialog.geometry(f"+{x}+{y}")
            
            # Create content frame
            frame = ThemedFrame(dialog, bg=self.colors["bg"])
            frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # Title
            title = tk.Label(
                frame,
                text="KeyLock Help & Support",
                font=("Segoe UI", 16, "bold"),
                bg=self.colors["bg"],
                fg=self.colors["text"]
            )
            title.pack(anchor=tk.W, pady=(0, 20))
            
            # Create scrollable text area
            text_frame = ThemedFrame(frame, bg=self.colors["bg"])
            text_frame.pack(fill=tk.BOTH, expand=True)
            
            scrollbar = tk.Scrollbar(text_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            help_text = tk.Text(
                text_frame,
                wrap=tk.WORD,
                bg=self.colors["card_bg"],
                fg=self.colors["text"],
                font=("Segoe UI", 10),
                padx=10,
                pady=10,
                bd=1,
                relief=tk.SOLID
            )
            help_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            scrollbar.config(command=help_text.yview)
            help_text.config(yscrollcommand=scrollbar.set)
            
            # Help content
            help_content = """
KeyLock is a powerful application that allows you to lock your keyboard and mouse.

Basic Usage:
- Use the "Lock" buttons in the Dashboard to lock your keyboard or mouse
- Use the "Lock All Devices" button to lock both at once
- Use the hotkey (default: Ctrl+Q) to unlock devices at any time

Timer Features:
- Set a countdown timer to automatically lock your devices
- Choose which devices to lock (keyboard, mouse, or both)
- Set auto-unlock to automatically unlock when the timer expires

Scheduler:
- Schedule recurring device locks
- Configure different lock types and durations
- View upcoming scheduled locks in the Dashboard

Settings:
- Customize the app appearance
- Configure hotkeys
- Set password protection for unlocking

For more help or to report bugs, visit:
https://keylock.example.com/support

Version: 2.0
"""
            help_text.insert(tk.END, help_content)
            help_text.config(state=tk.DISABLED)
            
            # Close button
            button_frame = ThemedFrame(frame, bg=self.colors["bg"])
            button_frame.pack(fill=tk.X, pady=(20, 0))
            
            ThemedButton(
                button_frame,
                text="Close",
                command=dialog.destroy,
                bg=self.colors["accent"],
                fg="#FFFFFF",
                width=10
            ).pack(side=tk.RIGHT)
            
        except Exception as e:
            self.update_status(f"Error showing help: {str(e)}")
    
    def _safe_exit(self):
        """Safely exit the application"""
        try:
            # Release any locks
            if self.keyboard_locked:
                core.unlock_keyboard()
            if self.mouse_locked:
                core.unlock_mouse()
                
            # Clean up
            controller.unregister_hotkeys()
            
            # Exit
            self.root.destroy()
        except Exception as e:
            print(f"Error during exit: {e}")
            self.root.destroy()
    
    def update_status(self, message):
        """Update the status label with a message"""
        if hasattr(self, 'status_label'):
            self.status_label.configure(text=message)
    
    def apply_theme(self):
        """Apply the current theme to all UI components"""
        # Update the colors dictionary based on theme
        if self.theme == "dark":
            self.colors = {
                "bg": "#1E1E1E",           # Dark background
                "dark_bg": "#252526",      # Darker background
                "accent": "#0078D7",       # Primary accent color
                "accent_hover": "#106EBE",  # Accent hover state
                "text": "#FFFFFF",         # Main text color
                "secondary_text": "#CCCCCC", # Secondary text color
                "success": "#28a745",      # Success color
                "warning": "#ffc107",      # Warning color
                "error": "#dc3545",        # Error color
                "card_bg": "#2D2D30",      # Card background
                "card_border": "#3E3E42",  # Card border
                "glass_bg": "#2D2D3099"    # Semi-transparent background
            }
        else:
            # Light theme (default)
            self.colors = {
                "bg": "#F5F5F5",           # Light background
                "dark_bg": "#2D2D30",      # Dark background
                "accent": "#0078D7",       # Primary accent color
                "accent_hover": "#106EBE",  # Accent hover state
                "text": "#333333",         # Main text color
                "secondary_text": "#777777", # Secondary text color
                "success": "#28a745",      # Success color
                "warning": "#ffc107",      # Warning color
                "error": "#dc3545",        # Error color
                "card_bg": "#FFFFFF",      # Card background
                "card_border": "#E5E5E5",  # Card border
                "glass_bg": "#FFFFFF99"    # Semi-transparent background
            }
        
        try:
            # Update root window background
            if hasattr(self, 'root') and self.root.winfo_exists():
                self.root.configure(bg=self.colors["bg"])
            
            # Update main frames (with error handling)
            if hasattr(self, 'sidebar') and self.sidebar.winfo_exists():
                self.sidebar.configure(bg=self.colors["dark_bg"])
            
            if hasattr(self, 'main_area') and self.main_area.winfo_exists():
                self.main_area.configure(bg=self.colors["bg"])
            
            # Update theme toggle button
            if hasattr(self, 'theme_btn') and self.theme_btn.winfo_exists():
                self.theme_btn.configure(bg=self.colors["bg"], fg=self.colors["text"])
            
            # Save theme preference to config
            try:
                from settings import save_config, open_config
                config = open_config()
                config["theme"] = self.theme
                save_config(config)
            except Exception as e:
                print(f"Error saving theme preference: {str(e)}")
            
            # Instead of rebuilding the view immediately, recreate the current view
            # from scratch to avoid reference errors
            current_view = self.current_view
            self.current_view = None  # Force recreation
            
            # Rebuild sidebar to update active state
            for widget in self.sidebar.winfo_children():
                widget.destroy()
            self._create_sidebar()
            
            # Switch to the current view to rebuild it with new theme
            self._switch_view(current_view)
            
            # Update status message
            self.update_status(f"Theme changed to {self.theme}")
        except Exception as e:
            # If there's an error, at least try to update the status
            if hasattr(self, 'status_label') and hasattr(self.status_label, 'winfo_exists') and self.status_label.winfo_exists():
                self.status_label.configure(text=f"Error applying theme: {str(e)}")
            print(f"Error applying theme: {str(e)}")

    def _apply_theme_from_settings(self, theme):
        """Apply the theme from settings"""
        self.theme = theme
        self.apply_theme()

    def _save_settings(self, theme):
        """Save the theme settings"""
        try:
            from settings import save_config, open_config
            
            # Load current config
            config = open_config()
            
            # Update theme
            config["theme"] = theme
            
            # Get other settings from UI
            if hasattr(self, 'block_keyboard_var'):
                config["block_keyboard"] = self.block_keyboard_var.get()
            
            if hasattr(self, 'block_mouse_var'):
                config["block_mouse"] = self.block_mouse_var.get()
                
            if hasattr(self, 'use_password_var'):
                config["use_password"] = self.use_password_var.get()
            
            # Save to config file
            save_config(config)
            
            # Update theme
            self.theme = theme
            self.apply_theme()
            
            # If controller is available, use it to save settings too
            if hasattr(self, 'controller') and hasattr(self.controller, 'save_settings'):
                self.controller.save_settings()
            
            # Show success message
            self.update_status("Settings saved successfully")
        except Exception as e:
            self.update_status(f"Error saving settings: {str(e)}")

    def _toggle_theme(self):
        """Toggle between light and dark theme"""
        try:
            # Toggle the theme
            if self.theme == "dark":
                self.theme = "light"
                if hasattr(self, 'theme_btn') and self.theme_btn.winfo_exists():
                    self.theme_btn.configure(text="🌙")  # Moon icon for light theme
            else:
                self.theme = "dark"
                if hasattr(self, 'theme_btn') and self.theme_btn.winfo_exists():
                    self.theme_btn.configure(text="☀️")  # Sun icon for dark theme
            
            # Apply the theme changes
            self.apply_theme()
            
            # Save the theme preference
            try:
                from settings import save_config, open_config
                config = open_config()
                config["theme"] = self.theme
                save_config(config)
            except Exception as e:
                print(f"Error saving theme preference: {str(e)}")
                
        except Exception as e:
            print(f"Error toggling theme: {str(e)}")

    def run(self):
        """Run the dashboard application"""
        self.root.mainloop()
        
    def set_controller(self, controller):
        """Set the controller reference"""
        self.controller = controller


def main():
    """Main entry point for the dashboard"""
    dashboard = KeylockDashboard()
    dashboard.run()


if __name__ == "__main__":
    main() 