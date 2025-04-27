import tkinter as tk
from tkinter import ttk
import sv_ttk

def get_dark_theme_colors():
    """Get color definitions for dark theme"""
    colors = {}
    
    # Modern dark theme with green/teal accent colors
    colors["accent"] = "#00BFA5"  # Teal accent
    colors["secondary_accent"] = "#4DB6AC"  # Lighter teal
    colors["accent_hover"] = "#009688"  # Deeper teal
    
    colors["background"] = "#1E1E1E"  # Dark background
    colors["card_bg"] = "#2D2D2D"  # Slightly lighter than background
    colors["surface"] = "#333333"  # Surface elements
    
    colors["foreground"] = "#E0F2F1"  # Very light teal for text
    colors["label"] = "#B2DFDB"  # Light teal text for secondary elements
    colors["inactive"] = "#80CBC4"  # Medium teal for disabled text
    
    colors["success"] = "#4CAF50"  # Green
    colors["error"] = "#FF5252"  # Red
    colors["warning"] = "#FFD740"  # Amber
    colors["info"] = "#26A69A"  # Teal for info
    
    colors["separator"] = "#444444"  # Subtle separator
    colors["selection_bg"] = "#00897B33"  # Selection with transparency
    
    colors["glass_bg"] = "#263238"  # Dark teal-tinted background
    colors["glass_frame"] = "#212121"  # Very dark gray
    colors["glass_highlight"] = "#37474F"  # Slightly lighter for highlights
    
    # Input colors
    colors["input_bg"] = "#212121"
    colors["input_fg"] = colors["foreground"]
    colors["border"] = "#455A64"
    
    # UI element colors
    colors["highlight"] = "#37474F"
    colors["shadow"] = "#00000077"
    
    # Button colors
    colors["button_bg"] = colors["accent"]
    colors["button_fg"] = "#FFFFFF"  # White text on buttons
    colors["button_hover"] = colors["accent_hover"]
    
    # Aliases for compatibility
    colors["bg"] = colors["background"]
    colors["text"] = colors["foreground"]
    colors["secondary"] = colors["label"]
    colors["light_text"] = colors["inactive"]
    colors["card_shadow"] = colors["shadow"]
    
    # Apply Sun Valley theme-specific adjustments if available
    try:
        # Refine colors to better match Sun Valley dark theme
        colors["glass_bg"] = "#263238"
        colors["glass_frame"] = "#212121"
        colors["glass_highlight"] = "#37474F"
        colors["input_bg"] = "#333333"
        colors["button_hover"] = "#00897B"
        colors["accent_hover"] = "#00897B"
    except:
        pass
    
    return colors

def configure_styles(colors):
    """Configure the ttk styles with the given colors"""
    try:
        style = ttk.Style()
        
        # Apply Sun Valley dark theme
        try:
            sv_ttk.set_theme("dark")
        except Exception as e:
            print(f"Could not apply Sun Valley theme: {e}")
            style.theme_use('clam')  # Fallback to clam theme
        
        # Configure styles for various UI elements with glass-like appearance
        style.configure(
            "Glass.TFrame", 
            background=colors["glass_bg"]
        )
        
        style.configure(
            "TLabel", 
            background=colors["background"], 
            foreground=colors["foreground"],
            font=("Segoe UI", 10)
        )
        
        style.configure(
            "Glass.TLabel",
            background=colors["glass_bg"], 
            foreground=colors["foreground"],
            font=("Segoe UI", 10)
        )
        
        style.configure(
            "Glass.Header.TLabel",
            background=colors["glass_bg"], 
            foreground=colors["foreground"],
            font=("Segoe UI", 18, "bold")
        )
        
        style.configure(
            "Glass.Subheader.TLabel",
            background=colors["glass_bg"], 
            foreground=colors["foreground"],
            font=("Segoe UI", 14, "bold")
        )
        
        style.configure(
            "Glass.Footer.TLabel",
            background=colors["glass_bg"], 
            foreground=colors["light_text"],
            font=("Segoe UI", 9)
        )
        
        # Improved button styles with better contrast
        style.configure(
            "Glass.TButton",
            background=colors["accent"],
            foreground="#FFFFFF",  # Always white for better readability
            font=("Segoe UI", 10, "bold"),
            padding=(10, 5),
            borderwidth=1,
            focusthickness=0
        )
        
        style.map(
            "Glass.TButton",
            background=[('active', colors["accent_hover"]), ('pressed', colors["accent_hover"])],
            relief=[('pressed', 'sunken'), ('!pressed', 'raised')]
        )
        
        style.configure(
            "TCheckbutton",
            background=colors["background"],
            foreground=colors["foreground"],
            font=("Segoe UI", 10)
        )
        
        style.configure(
            "Glass.TCheckbutton",
            background=colors["glass_bg"],
            foreground=colors["foreground"],
            font=("Segoe UI", 10)
        )
        
        style.configure(
            "Vertical.TScrollbar",
            background=colors["glass_bg"],
            arrowcolor=colors["foreground"],
            bordercolor=colors["glass_bg"],
            troughcolor=colors["glass_bg"],
            gripcount=0
        )
        
        style.map(
            "Vertical.TScrollbar",
            background=[('active', colors["accent_hover"]), ('pressed', colors["accent"])],
            troughcolor=[('!active', colors["glass_bg"])]
        )

        # Card style with shadow effect
        style.configure(
            "Card.TFrame",
            background=colors["card_bg"],
            borderwidth=0,
            relief="flat",
            padding=15
        )
        
        # Modern rounded button style with high contrast
        style.configure(
            "Rounded.TButton",
            background=colors["accent"],
            foreground="#FFFFFF",  # Always white text
            borderwidth=1,
            focusthickness=0,
            padding=(15, 8),
            font=("Segoe UI", 10, "bold")
        )
        
        style.map(
            "Rounded.TButton",
            background=[('active', colors["accent_hover"]), ('pressed', colors["accent_hover"])],
            relief=[('pressed', 'sunken'), ('!pressed', 'raised')]
        )
        
        # Primary action button with high contrast
        style.configure(
            "Action.TButton",
            background=colors["accent"],
            foreground="#FFFFFF",  # Always white text
            borderwidth=1,
            focusthickness=0,
            padding=(15, 8),
            font=("Segoe UI", 11, "bold")
        )
        
        style.map(
            "Action.TButton",
            background=[('active', colors["accent_hover"]), ('pressed', colors["accent_hover"])],
            relief=[('pressed', 'sunken'), ('!pressed', 'raised')]
        )
        
        # Secondary/ghost button
        style.configure(
            "Ghost.TButton",
            background=colors["glass_bg"],
            foreground=colors["foreground"],
            borderwidth=1,
            bordercolor=colors["border"],
            focusthickness=0,
            padding=(10, 5),
            font=("Segoe UI", 10)
        )
        
        style.map(
            "Ghost.TButton",
            background=[('active', colors["selection_bg"]), ('pressed', colors["selection_bg"])],
            foreground=[('active', colors["accent"]), ('pressed', colors["accent"])],
            relief=[('pressed', 'flat'), ('!pressed', 'flat')]
        )
        
        # Success button
        style.configure(
            "Success.TButton",
            background=colors["success"],
            foreground=colors["button_fg"],
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
            background=colors["warning"],
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
            background=colors["error"],
            foreground=colors["button_fg"],
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
            background=colors["background"],
            borderwidth=0,
            tabmargins=[0, 0, 0, 0],
            tabposition="n"
        )
        
        style.configure(
            "TNotebook.Tab",
            background=colors["glass_bg"],
            foreground=colors["foreground"],
            padding=[15, 5],
            font=("Segoe UI", 10)
        )
        
        style.map(
            "TNotebook.Tab",
            background=[('selected', colors["accent"]), ('active', colors["selection_bg"])],
            foreground=[('selected', "white"), ('active', colors["accent"])],
            expand=[('selected', [1, 1, 1, 0])]
        )
        
        return style
        
    except Exception as e:
        print(f"Error configuring styles: {e}")
        return None

def update_widget_themes(widget, colors):
    """Recursively update theme for all widgets"""
    try:
        if hasattr(widget, 'update_theme'):
            widget.update_theme(colors)
            
        for child in widget.winfo_children():
            update_widget_themes(child, colors)
            
    except Exception as e:
        print(f"Error updating widget theme: {e}") 