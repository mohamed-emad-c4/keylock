import tkinter as tk
from tkinter import ttk
import platform
from settings import get_theme_colors
from functools import partial

class ThemedFrame(ttk.Frame):
    """A frame with theme support and responsive layout"""
    def __init__(self, parent, theme="light", padding=(10, 10), **kwargs):
        self.colors = get_theme_colors(theme)
        
        style = ttk.Style()
        style_name = f"Themed.TFrame.{id(self)}"
        style.configure(style_name, background=self.colors["background"])
        
        super().__init__(parent, style=style_name, padding=padding, **kwargs)
        
    def update_theme(self, theme):
        """Update the frame's theme"""
        self.colors = get_theme_colors(theme)
        style = ttk.Style()
        style_name = f"Themed.TFrame.{id(self)}"
        style.configure(style_name, background=self.colors["background"])

class ThemedButton(ttk.Button):
    """Modern themed button with hover effects"""
    def __init__(self, parent, text, command=None, theme="light", width=None, **kwargs):
        self.colors = get_theme_colors(theme)
        self.parent = parent
        self.is_primary = kwargs.pop('primary', True)
        
        style = ttk.Style()
        style_name = f"Themed.TButton.{id(self)}"
        
        # Primary vs Secondary button styling
        if self.is_primary:
            bg_color = self.colors["button_bg"]
            fg_color = self.colors["button_fg"]
            hover_color = self.colors["button_hover"]
        else:
            bg_color = self.colors["background"]
            fg_color = self.colors["foreground"]
            hover_color = self.colors["selection_bg"]
            
        style.configure(
            style_name,
            background=bg_color,
            foreground=fg_color,
            borderwidth=1,
            focusthickness=3,
            focuscolor=self.colors["accent"]
        )
        
        # Configure hover style
        style.map(
            style_name,
            background=[('active', hover_color)],
            relief=[('pressed', 'sunken'), ('!pressed', 'raised')]
        )
        
        super().__init__(parent, text=text, command=command, style=style_name, width=width, **kwargs)
        
    def update_theme(self, theme):
        """Update the button's theme"""
        self.colors = get_theme_colors(theme)
        style = ttk.Style()
        style_name = f"Themed.TButton.{id(self)}"
        
        if self.is_primary:
            bg_color = self.colors["button_bg"]
            fg_color = self.colors["button_fg"]
            hover_color = self.colors["button_hover"]
        else:
            bg_color = self.colors["background"]
            fg_color = self.colors["foreground"]
            hover_color = self.colors["selection_bg"]
            
        style.configure(
            style_name,
            background=bg_color,
            foreground=fg_color,
            borderwidth=1,
            focusthickness=3,
            focuscolor=self.colors["accent"]
        )
        
        style.map(
            style_name,
            background=[('active', hover_color)],
            relief=[('pressed', 'sunken'), ('!pressed', 'raised')]
        )

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

class ResponsiveGrid(ttk.Frame):
    """A grid container that automatically adjusts its layout based on width"""
    def __init__(self, parent, columns=2, padding=10, min_column_width=200, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.columns = columns
        self.padding = padding
        self.min_column_width = min_column_width
        self.widgets = []
        
        # Configure the single column to expand
        self.columnconfigure(0, weight=1)
        
        # Bind to resize events
        self.bind("<Configure>", self._on_resize)
        
    def add_widget(self, widget, sticky="ew", padx=5, pady=5):
        """Add a widget to the responsive grid"""
        self.widgets.append({
            "widget": widget,
            "sticky": sticky,
            "padx": padx,
            "pady": pady
        })
        self._reflow_layout()
        
    def _on_resize(self, event):
        """Handle resize events"""
        self._reflow_layout()
        
    def _reflow_layout(self):
        """Reflow the layout based on the current width"""
        width = self.winfo_width()
        
        # Don't reflow if width is 1 (initial state)
        if width <= 1:
            return
            
        # Calculate how many columns can fit
        available_cols = max(1, min(self.columns, width // self.min_column_width))
        
        # Remove all widgets first
        for widget_info in self.widgets:
            widget_info["widget"].grid_forget()
            
        # Re-add widgets in the new layout
        for i, widget_info in enumerate(self.widgets):
            row = i // available_cols
            col = i % available_cols
            
            # Configure column weight if needed
            if col >= self.grid_size()[0]:
                self.columnconfigure(col, weight=1)
                
            widget_info["widget"].grid(
                row=row, 
                column=col, 
                sticky=widget_info["sticky"],
                padx=widget_info["padx"],
                pady=widget_info["pady"]
            )

class Card(ttk.Frame):
    """A card-like container with title and content sections"""
    def __init__(self, parent, title=None, theme="light", padding=(15, 15), **kwargs):
        self.colors = get_theme_colors(theme)
        
        # Configure card style
        style = ttk.Style()
        style_name = f"Card.TFrame.{id(self)}"
        style.configure(
            style_name,
            background=self.colors["card_bg"],
            relief="raised",
            borderwidth=1
        )
        
        super().__init__(parent, style=style_name, padding=padding, **kwargs)
        
        # Configure layout
        self.columnconfigure(0, weight=1)
        
        # Add title if provided
        self.title_label = None
        row = 0
        
        if title:
            # Title style
            title_style_name = f"CardTitle.TLabel.{id(self)}"
            style.configure(
                title_style_name,
                foreground=self.colors["foreground"],
                background=self.colors["card_bg"],
                font=("TkDefaultFont", 12, "bold")
            )
            
            self.title_label = ttk.Label(self, text=title, style=title_style_name)
            self.title_label.grid(row=row, column=0, sticky="w", pady=(0, 10))
            row += 1
            
            # Add separator
            separator_style = f"Card.TSeparator.{id(self)}"
            style.configure(separator_style, background=self.colors["separator"])
            
            self.separator = ttk.Separator(self, orient="horizontal", style=separator_style)
            self.separator.grid(row=row, column=0, sticky="ew", pady=(0, 15))
            row += 1
            
        # Content frame
        content_style = f"CardContent.TFrame.{id(self)}"
        style.configure(content_style, background=self.colors["card_bg"])
        
        self.content = ttk.Frame(self, style=content_style)
        self.content.grid(row=row, column=0, sticky="nsew")
        self.content.columnconfigure(0, weight=1)
        
    def update_theme(self, theme):
        """Update the card's theme"""
        self.colors = get_theme_colors(theme)
        
        style = ttk.Style()
        
        # Update card style
        style_name = f"Card.TFrame.{id(self)}"
        style.configure(
            style_name,
            background=self.colors["card_bg"],
            relief="raised",
            borderwidth=1
        )
        
        # Update title style if exists
        if self.title_label:
            title_style_name = f"CardTitle.TLabel.{id(self)}"
            style.configure(
                title_style_name,
                foreground=self.colors["foreground"],
                background=self.colors["card_bg"],
                font=("TkDefaultFont", 12, "bold")
            )
            
            # Update separator
            separator_style = f"Card.TSeparator.{id(self)}"
            style.configure(separator_style, background=self.colors["separator"])
            
        # Update content style
        content_style = f"CardContent.TFrame.{id(self)}"
        style.configure(content_style, background=self.colors["card_bg"])

class Tooltip:
    """Display a tooltip when hovering over a widget"""
    def __init__(self, widget, text, theme="light", delay=500, wrap_length=200):
        self.widget = widget
        self.text = text
        self.colors = get_theme_colors(theme)
        self.delay = delay
        self.wrap_length = wrap_length
        self.tooltip_window = None
        self.id = None
        
        self.widget.bind("<Enter>", self.schedule)
        self.widget.bind("<Leave>", self.hide)
        self.widget.bind("<ButtonPress>", self.hide)
        
    def schedule(self, event=None):
        """Schedule the tooltip to appear after delay"""
        self.hide()
        self.id = self.widget.after(self.delay, self.show)
        
    def show(self):
        """Show the tooltip"""
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        # Create tooltip window
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        
        # Create tooltip content
        label = tk.Label(
            self.tooltip_window, 
            text=self.text, 
            background=self.colors["card_bg"],
            foreground=self.colors["foreground"],
            wraplength=self.wrap_length,
            justify="left",
            relief="solid",
            borderwidth=1,
            padx=5,
            pady=5
        )
        label.pack()
        
    def hide(self, event=None):
        """Hide the tooltip"""
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
            
    def update_theme(self, theme):
        """Update the tooltip's theme"""
        self.colors = get_theme_colors(theme)

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