import tkinter as tk
from tkinter import ttk
import platform
from settings import get_theme_colors
from functools import partial
import math

class ThemedFrame(tk.Frame):
    """A themed frame that adapts to the current theme"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(borderwidth=0, highlightthickness=0)

class ThemedButton(tk.Button):
    """A themed button with hover effects"""
    def __init__(self, parent, **kwargs):
        # Extract colors or use defaults
        bg_color = kwargs.pop('bg', '#0078D7')
        fg_color = kwargs.pop('fg', 'white')
        hover_bg = kwargs.pop('hover_bg', self._darken_color(bg_color, 0.1))
        hover_fg = kwargs.pop('hover_fg', fg_color)
        
        super().__init__(
            parent,
            bg=bg_color,
            fg=fg_color,
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            font=("Segoe UI", 10),
            cursor="hand2",
            **kwargs
        )
        
        # Store colors for hover state
        self._bg = bg_color
        self._fg = fg_color
        self._hover_bg = hover_bg
        self._hover_fg = hover_fg
        
        # Bind hover events
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
    
    def _on_enter(self, event):
        """Change colors on hover"""
        self.configure(bg=self._hover_bg, fg=self._hover_fg)
    
    def _on_leave(self, event):
        """Restore original colors"""
        self.configure(bg=self._bg, fg=self._fg)
    
    def _darken_color(self, hex_color, factor=0.1):
        """Darken a hex color by a factor"""
        # Convert hex to RGB
        if hex_color.startswith('#'):
            hex_color = hex_color[1:]
        
        # Get RGB components
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        # Darken
        r = max(0, int(r * (1 - factor)))
        g = max(0, int(g * (1 - factor)))
        b = max(0, int(b * (1 - factor)))
        
        # Convert back to hex
        return f"#{r:02x}{g:02x}{b:02x}"

class ThemedLabel(ttk.Label):
    """Themed label with customizable styling"""
    def __init__(self, parent, text="", theme="light", font_size=None, font_weight="normal", **kwargs):
        self.colors = get_theme_colors(theme)
        
        # Determine font based on system
        if platform.system() == "Windows":
            base_font = "Segoe UI"
        elif platform.system() == "Darwin":  # macOS
            base_font = "Helvetica Neue"
        else:  # Linux and others
            base_font = "Noto Sans"
            
        # Set font size
        if font_size is None:
            font_size = 10
        elif font_size == "small":
            font_size = 9
        elif font_size == "medium":
            font_size = 10
        elif font_size == "large":
            font_size = 12
            
        # Create font tuple
        font = (base_font, font_size, font_weight)
        
        style = ttk.Style()
        style_name = f"Themed.TLabel.{id(self)}"
        style.configure(style_name, foreground=self.colors["foreground"], background=self.colors["background"], font=font)
        
        super().__init__(parent, text=text, style=style_name, **kwargs)
        
    def update_theme(self, theme):
        """Update the label's theme"""
        self.colors = get_theme_colors(theme)
        style = ttk.Style()
        style_name = f"Themed.TLabel.{id(self)}"
        style.configure(style_name, foreground=self.colors["foreground"], background=self.colors["background"])

class ThemedEntry(ttk.Entry):
    """Themed entry field with placeholder text support"""
    def __init__(self, parent, theme="light", placeholder=None, width=None, **kwargs):
        self.colors = get_theme_colors(theme)
        self.placeholder = placeholder
        self.placeholder_color = self.colors["inactive"]
        self.default_fg_color = self.colors["input_fg"]
        self.has_placeholder = False
        
        style = ttk.Style()
        style_name = f"Themed.TEntry.{id(self)}"
        style.configure(
            style_name,
            foreground=self.colors["input_fg"],
            fieldbackground=self.colors["input_bg"],
            bordercolor=self.colors["border"],
            lightcolor=self.colors["input_bg"],
            darkcolor=self.colors["input_bg"],
            borderwidth=1,
            padding=5
        )
        
        super().__init__(parent, style=style_name, width=width, **kwargs)
        
        # Set up placeholder if provided
        if placeholder:
            self.insert(0, placeholder)
            self.configure(foreground=self.placeholder_color)
            self.has_placeholder = True
            
            self.bind("<FocusIn>", self._on_focus_in)
            self.bind("<FocusOut>", self._on_focus_out)
            
    def _on_focus_in(self, event):
        if self.has_placeholder:
            self.delete(0, tk.END)
            self.configure(foreground=self.default_fg_color)
            self.has_placeholder = False
            
    def _on_focus_out(self, event):
        if not self.get():
            self.insert(0, self.placeholder)
            self.configure(foreground=self.placeholder_color)
            self.has_placeholder = True
            
    def update_theme(self, theme):
        """Update the entry's theme"""
        self.colors = get_theme_colors(theme)
        self.placeholder_color = self.colors["inactive"]
        self.default_fg_color = self.colors["input_fg"]
        
        style = ttk.Style()
        style_name = f"Themed.TEntry.{id(self)}"
        style.configure(
            style_name,
            foreground=self.colors["input_fg"],
            fieldbackground=self.colors["input_bg"],
            bordercolor=self.colors["border"],
            lightcolor=self.colors["input_bg"],
            darkcolor=self.colors["input_bg"],
            borderwidth=1,
            padding=5
        )
        
        # Update text color based on whether placeholder is showing
        if self.has_placeholder:
            self.configure(foreground=self.placeholder_color)
        else:
            self.configure(foreground=self.default_fg_color)

class ThemedCheckbutton(ttk.Checkbutton):
    """Themed checkbutton with modern styling"""
    def __init__(self, parent, text="", command=None, theme="light", variable=None, **kwargs):
        self.colors = get_theme_colors(theme)
        
        style = ttk.Style()
        style_name = f"Themed.TCheckbutton.{id(self)}"
        
        style.configure(
            style_name,
            background=self.colors["background"],
            foreground=self.colors["foreground"],
            indicatorcolor=self.colors["input_bg"],
            indicatorbackground=self.colors["input_bg"],
            indicatorrelief="flat"
        )
        
        style.map(
            style_name,
            background=[('active', self.colors["background"])],
            foreground=[('disabled', self.colors["inactive"])],
            indicatorcolor=[('selected', self.colors["accent"])]
        )
        
        super().__init__(parent, text=text, command=command, style=style_name, variable=variable, **kwargs)
        
    def update_theme(self, theme):
        """Update the checkbutton's theme"""
        self.colors = get_theme_colors(theme)
        
        style = ttk.Style()
        style_name = f"Themed.TCheckbutton.{id(self)}"
        
        style.configure(
            style_name,
            background=self.colors["background"],
            foreground=self.colors["foreground"],
            indicatorcolor=self.colors["input_bg"],
            indicatorbackground=self.colors["input_bg"]
        )
        
        style.map(
            style_name,
            background=[('active', self.colors["background"])],
            foreground=[('disabled', self.colors["inactive"])],
            indicatorcolor=[('selected', self.colors["accent"])]
        )

class ResponsiveGrid(ThemedFrame):
    """A responsive grid layout that adjusts to window size"""
    
    def __init__(self, parent, columns=2, padding=10, **kwargs):
        super().__init__(parent, **kwargs)
        self.columns = columns
        self.padding = padding
        self.widgets = []
        
        # Bind resize event
        self.bind("<Configure>", self._on_resize)
        
    def add_widget(self, widget, row, col, rowspan=1, colspan=1):
        """Add a widget to the grid at the specified position"""
        self.widgets.append({
            'widget': widget,
            'row': row,
            'col': col,
            'rowspan': rowspan,
            'colspan': colspan
        })
        
        # Position the widget
        self._position_widgets()
        
    def _on_resize(self, event):
        """Reposition widgets when the grid is resized"""
        self._position_widgets()
        
    def _position_widgets(self):
        """Position all widgets in the grid"""
        width = self.winfo_width()
        if width <= 1:  # Not yet realized
            return
            
        # Calculate cell dimensions
        col_width = width / self.columns
        
        # Position each widget
        for item in self.widgets:
            widget = item['widget']
            row = item['row']
            col = item['col']
            rowspan = item['rowspan']
            colspan = item['colspan']
            
            # Calculate widget dimensions
            widget_width = col_width * colspan - self.padding * 2
            
            # Calculate position
            x = col * col_width + self.padding
            y = row * col_width + self.padding
            
            # Place the widget
            widget.place(
                x=x,
                y=y,
                width=widget_width,
                height=col_width * rowspan - self.padding * 2
            )

class Card(ThemedFrame):
    """A card widget with title and content area"""
    def __init__(self, parent, title=None, **kwargs):
        # Default styling for cards
        bg_color = kwargs.pop('bg', '#FFFFFF')
        border_color = kwargs.pop('border_color', '#E5E5E5')
        title_color = kwargs.pop('title_color', '#333333')
        
        super().__init__(parent, **kwargs)
        self.configure(
            bg=bg_color,
            padx=15,
            pady=15,
            relief="solid",
            borderwidth=1,
            highlightthickness=0
        )
        
        # Add title if provided
        if title:
            title_frame = ThemedFrame(self, bg=bg_color)
            title_frame.pack(fill=tk.X, anchor="nw", pady=(0, 10))
            
            title_label = tk.Label(
                title_frame,
                text=title,
                font=("Segoe UI", 12, "bold"),
                bg=bg_color,
                fg=title_color
            )
            title_label.pack(anchor="w")
            
            # Add separator
            separator = ttk.Separator(self, orient="horizontal")
            separator.pack(fill=tk.X, pady=(0, 10))
        
        # Content area
        self.content_frame = ThemedFrame(self, bg=bg_color)
        self.content_frame.pack(fill=tk.BOTH, expand=True)

class CircularProgressBar(tk.Canvas):
    """A circular progress bar widget"""
    
    def __init__(self, parent, **kwargs):
        # Extract and remove custom parameters
        self.size = kwargs.pop('size', 100)
        self.progress = kwargs.pop('progress', 0)  # 0 to 100
        self.width = kwargs.pop('width', 8)
        self.background_color = kwargs.pop('bg_color', '#E0E0E0')
        self.progress_color = kwargs.pop('progress_color', '#0078D7')
        self.text_color = kwargs.pop('text_color', '#333333')
        
        # Initialize canvas
        super().__init__(
            parent,
            width=self.size,
            height=self.size,
            highlightthickness=0,
            **kwargs
        )
        
        # Draw initial state
        self.update_progress(self.progress)
    
    def update_progress(self, progress):
        """Update the progress bar with new percentage"""
        self.progress = progress
        self.delete("all")
        
        # Calculate angles
        angle = 360 * (progress / 100)
        
        # Draw background circle
        self.create_oval(
            self.width, self.width,
            self.size - self.width, self.size - self.width,
            outline=self.background_color,
            width=self.width
        )
        
        if progress > 0:
            # Draw progress arc
            self.create_arc(
                self.width, self.width,
                self.size - self.width, self.size - self.width,
                start=90, extent=-angle,
                style="arc",
                outline=self.progress_color,
                width=self.width
            )
        
        # Draw text in center
        self.create_text(
            self.size / 2, self.size / 2,
            text=f"{int(progress)}%",
            font=("Segoe UI", int(self.size / 8), "bold"),
            fill=self.text_color
        )

class ToggleSwitch(tk.Frame):
    """A modern toggle switch widget"""
    
    def __init__(self, parent, **kwargs):
        # Extract and remove custom parameters
        self.width = kwargs.pop('width', 60)
        self.height = kwargs.pop('height', 30)
        self.on_color = kwargs.pop('on_color', '#0078D7')
        self.off_color = kwargs.pop('off_color', '#CCCCCC')
        self.on_text = kwargs.pop('on_text', 'ON')
        self.off_text = kwargs.pop('off_text', 'OFF')
        initial_state = kwargs.pop('state', False)
        self.command = kwargs.pop('command', None)
        
        # Initialize frame
        super().__init__(parent, **kwargs)
        self.configure(width=self.width, height=self.height, bg=parent["bg"])
        
        # Create canvas for drawing the switch
        self.canvas = tk.Canvas(
            self,
            width=self.width,
            height=self.height,
            bg=parent["bg"],
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Bind events
        self.canvas.bind("<Button-1>", self._toggle)
        
        # Set initial state
        self.state = initial_state
        self._draw_switch()
    
    def _toggle(self, event=None):
        """Toggle the switch state"""
        self.state = not self.state
        self._draw_switch()
        if self.command:
            self.command(self.state)
    
    def _draw_switch(self):
        """Draw the toggle switch on the canvas"""
        self.canvas.delete("all")
        
        # Determine colors
        bg_color = self.on_color if self.state else self.off_color
        text = self.on_text if self.state else self.off_text
        
        # Draw the track
        radius = self.height / 2
        self.canvas.create_rounded_rect(
            0, 0, self.width, self.height,
            radius=radius, fill=bg_color
        )
        
        # Draw the thumb
        thumb_pos = self.width - self.height + 2 if self.state else 2
        self.canvas.create_oval(
            thumb_pos, 2,
            thumb_pos + self.height - 4, self.height - 2,
            fill="#FFFFFF"
        )
        
        # Draw text
        text_x = self.width - self.height / 2 - 10 if self.state else 15
        self.canvas.create_text(
            text_x, self.height / 2,
            text=text,
            fill="#FFFFFF",
            font=("Segoe UI", 8, "bold")
        )
    
    def get(self):
        """Get the current state"""
        return self.state
    
    def set(self, state):
        """Set the state"""
        if state != self.state:
            self.state = state
            self._draw_switch()

# Extend Canvas to add methods for rounded rectangles
tk.Canvas.create_rounded_rect = lambda self, x1, y1, x2, y2, radius=25, **kwargs: \
    self.create_polygon(
        x1 + radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1,
        smooth=True, **kwargs
    )

def setup_theme(root, theme="light"):
    """Setup the main application theme"""
    colors = get_theme_colors(theme)
    style = ttk.Style()
    
    # Configure ttk theme
    if platform.system() == "Windows":
        style.theme_use("vista")
    elif platform.system() == "Darwin":  # macOS
        style.theme_use("aqua")
    else:  # Linux
        style.theme_use("clam")
    
    # Configure the base styles
    style.configure("TFrame", background=colors["background"])
    style.configure("TLabel", background=colors["background"], foreground=colors["foreground"])
    style.configure("TButton", 
                    background=colors["button_bg"],
                    foreground=colors["button_fg"],
                    borderwidth=1)
    style.map("TButton",
              background=[('active', colors["button_hover"])],
              relief=[('pressed', 'sunken'), ('!pressed', 'raised')])
    
    style.configure("TEntry",
                   foreground=colors["input_fg"],
                   fieldbackground=colors["input_bg"],
                   bordercolor=colors["border"],
                   lightcolor=colors["input_bg"],
                   darkcolor=colors["input_bg"])
    
    style.configure("TCheckbutton", 
                   background=colors["background"],
                   foreground=colors["foreground"])
    style.map("TCheckbutton",
             indicatorcolor=[('selected', colors["accent"])])
    
    # Configure main window
    if isinstance(root, tk.Tk) or isinstance(root, tk.Toplevel):
        root.configure(background=colors["background"])
        
    return style

class TabView(ttk.Notebook):
    """Tabbed interface with themed styling"""
    def __init__(self, parent, theme="light", **kwargs):
        self.colors = get_theme_colors(theme)
        
        style = ttk.Style()
        style_name = f"ThemedTabView.TNotebook.{id(self)}"
        
        # Configure notebook style
        style.configure(
            style_name,
            background=self.colors["background"],
            borderwidth=0
        )
        
        # Configure tab style
        tab_style = f"{style_name}.Tab"
        style.configure(
            tab_style,
            background=self.colors["background"],
            foreground=self.colors["foreground"],
            padding=[10, 5],
            borderwidth=0
        )
        
        style.map(
            tab_style,
            background=[('selected', self.colors["card_bg"]), 
                        ('active', self.colors["background"])],
            foreground=[('selected', self.colors["accent"]), 
                        ('active', self.colors["foreground"])]
        )
        
        super().__init__(parent, style=style_name, **kwargs)
        
    def add_tab(self, title, **kwargs):
        """Create a new frame for a tab and add it to the notebook"""
        frame = ttk.Frame(self)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        
        self.add(frame, text=title, **kwargs)
        return frame
        
    def update_theme(self, theme):
        """Update the tabview's theme"""
        self.colors = get_theme_colors(theme)
        
        style = ttk.Style()
        style_name = f"ThemedTabView.TNotebook.{id(self)}"
        
        # Update notebook style
        style.configure(
            style_name,
            background=self.colors["background"],
            borderwidth=0
        )
        
        # Update tab style
        tab_style = f"{style_name}.Tab"
        style.configure(
            tab_style,
            background=self.colors["background"],
            foreground=self.colors["foreground"],
            padding=[10, 5],
            borderwidth=0
        )
        
        style.map(
            tab_style,
            background=[('selected', self.colors["card_bg"]), 
                        ('active', self.colors["background"])],
            foreground=[('selected', self.colors["accent"]), 
                        ('active', self.colors["foreground"])]
        )

class CollapsibleCard(ThemedFrame):
    """A collapsible card widget with a toggle header"""
    def __init__(self, parent, title="", **kwargs):
        # Extract and store specific parameters
        self.bg_color = kwargs.get('bg', '#FFFFFF')
        self.text_color = kwargs.get('fg', '#333333')
        self.accent_color = kwargs.get('accent', '#0078D7')
        self.expanded = kwargs.pop('expanded', True)
        
        super().__init__(parent, **kwargs)
        self.configure(
            relief="solid",
            borderwidth=1,
            highlightthickness=0
        )
        
        # Create title frame/header
        self.header_frame = ThemedFrame(self, bg=self.bg_color)
        self.header_frame.pack(fill=tk.X, anchor="nw")
        
        # Toggle indicator (+ or -)
        self.toggle_indicator = tk.Label(
            self.header_frame,
            text="▼" if self.expanded else "►",
            font=("Segoe UI", 10),
            bg=self.bg_color,
            fg=self.accent_color
        )
        self.toggle_indicator.pack(side=tk.LEFT, padx=(10, 5), pady=10)
        
        # Title label
        self.title_label = tk.Label(
            self.header_frame,
            text=title,
            font=("Segoe UI", 12, "bold"),
            bg=self.bg_color,
            fg=self.text_color
        )
        self.title_label.pack(side=tk.LEFT, pady=10)
        
        # Make the header clickable
        self.header_frame.bind("<Button-1>", self.toggle)
        self.toggle_indicator.bind("<Button-1>", self.toggle)
        self.title_label.bind("<Button-1>", self.toggle)
        
        # Content frame (holds the collapsible content)
        self.content_frame = ThemedFrame(self, bg=self.bg_color)
        if self.expanded:
            self.content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
    
    def toggle(self, event=None):
        """Toggle the expanded/collapsed state"""
        self.expanded = not self.expanded
        
        # Update the toggle indicator
        self.toggle_indicator.config(text="▼" if self.expanded else "►")
        
        # Show or hide the content
        if self.expanded:
            self.content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        else:
            self.content_frame.pack_forget()
            
    def expand(self):
        """Expand the card"""
        if not self.expanded:
            self.toggle()
            
    def collapse(self):
        """Collapse the card"""
        if self.expanded:
            self.toggle()

def create_window(title, theme="light", icon=None, resizable=(True, True), min_size=(400, 300)):
    """Create a themed tkinter window"""
    root = tk.Tk()
    root.title(title)
    root.minsize(*min_size)
    
    # Set window resizable properties
    root.resizable(resizable[0], resizable[1])
    
    # Set window icon if provided
    if icon:
        root.iconphoto(True, tk.PhotoImage(file=icon))
    
    # Setup theme
    setup_theme(root, theme)
    
    # Configure grid weights for responsive layout
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    
    return root

def create_dialog(parent, title, theme="light", modal=True, resizable=(True, True), min_size=(300, 200)):
    """Create a themed dialog window"""
    dialog = tk.Toplevel(parent)
    dialog.title(title)
    dialog.minsize(*min_size)
    
    # Set modal behavior
    if modal:
        dialog.transient(parent)
        dialog.grab_set()
        
    # Set window resizable properties
    dialog.resizable(resizable[0], resizable[1])
    
    # Setup theme
    setup_theme(dialog, theme)
    
    # Configure grid weights for responsive layout
    dialog.columnconfigure(0, weight=1)
    dialog.rowconfigure(0, weight=1)
    
    return dialog

def center_window(window, width=None, height=None):
    """Center a window on the screen"""
    # Get screen dimensions
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    # Use provided dimensions or current window size
    if width is None:
        width = window.winfo_width()
    if height is None:
        height = window.winfo_height()
        
    # If window hasn't been updated yet, update it to get proper dimensions
    if width == 1:
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        
    # Calculate position
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    
    # Set window position
    window.geometry(f"{width}x{height}+{x}+{y}") 