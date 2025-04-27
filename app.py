import tkinter as tk
from tkinter import ttk, font
import sys
import threading
import json
import time
from ui_components import create_status_section, create_buttons_section
from settings import get_theme_colors
from device_manager import lock_keyboard, unlock_keyboard, lock_mouse, unlock_mouse

class KeyLockApp:
    def __init__(self, root):
        self.root = root
        self.root.title("KeyLock")
        self.root.minsize(400, 350)
        
        # Set app icon
        # self.root.iconbitmap("assets/icon.ico")
        
        # Get theme colors
        self.colors = get_theme_colors()
        
        # Configure ttk styles
        self.configure_styles()
        
        # Create main container
        self.main_frame = ttk.Frame(root, padding=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create the status section with device indicators
        self.status_frame, self.keyboard_canvas, self.mouse_canvas, self.keyboard_status, self.mouse_status = create_status_section(self.main_frame, self.colors)
        self.status_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create Quick Controls section with buttons
        self.controls_frame, self.lock_kb_btn, self.unlock_kb_btn, self.lock_mouse_btn, self.unlock_mouse_btn, self.lock_all_btn, self.unlock_all_btn = create_buttons_section(
            self.main_frame, 
            self.colors, 
            self.toggle_keyboard_lock,
            self.toggle_mouse_lock
        )
        self.controls_frame.pack(fill=tk.BOTH, expand=True)
        
        # Initialize state
        self.keyboard_locked = False
        self.mouse_locked = False
        
        # Start the monitoring thread
        self.device_monitor_thread = threading.Thread(target=self.monitor_device_status, daemon=True)
        self.device_monitor_thread.start()
    
    def configure_styles(self):
        """Configure ttk styles for the application"""
        style = ttk.Style()
        
        # Configure label frame style
        style.configure("TLabelframe", borderwidth=1, relief="solid")
        style.configure("TLabelframe.Label", font=("Segoe UI", 11, "bold"), foreground=self.colors.get("accent", "#1976D2"))
        
        # Configure button styles
        style.configure("TButton", font=("Segoe UI", 10))
        
        # Create accent button style
        style.configure("AccentButton.TButton", 
                       background=self.colors.get("accent", "#1976D2"),
                       foreground="white")
        
        # Create switch style for checkbuttons
        style.configure("Switch.TCheckbutton", font=("Segoe UI", 10))
    
    def toggle_keyboard_lock(self):
        """Toggle the keyboard lock state"""
        if self.keyboard_locked:
            # Unlock the keyboard
            unlock_keyboard()
            self.keyboard_locked = False
            self.keyboard_status.config(text="Unlocked", foreground=self.colors.get("accent_positive", "#4CAF50"))
        else:
            # Lock the keyboard
            lock_keyboard()
            self.keyboard_locked = True
            self.keyboard_status.config(text="Locked", foreground=self.colors.get("accent_negative", "#F44336"))
        
        # Redraw the keyboard indicator
        self.redraw_keyboard_indicator()
    
    def toggle_mouse_lock(self):
        """Toggle the mouse lock state"""
        if self.mouse_locked:
            # Unlock the mouse
            unlock_mouse()
            self.mouse_locked = False
            self.mouse_status.config(text="Unlocked", foreground=self.colors.get("accent_positive", "#4CAF50"))
        else:
            # Lock the mouse
            lock_mouse()
            self.mouse_locked = True
            self.mouse_status.config(text="Locked", foreground=self.colors.get("accent_negative", "#F44336"))
        
        # Redraw the mouse indicator
        self.redraw_mouse_indicator()
    
    def redraw_keyboard_indicator(self):
        """Redraw the keyboard indicator based on current state"""
        from indicators import draw_keyboard_indicator
        self.keyboard_canvas.delete("all")
        draw_keyboard_indicator(self.keyboard_canvas, self.colors, self.keyboard_locked)
    
    def redraw_mouse_indicator(self):
        """Redraw the mouse indicator based on current state"""
        from indicators import draw_mouse_indicator
        self.mouse_canvas.delete("all")
        draw_mouse_indicator(self.mouse_canvas, self.colors, self.mouse_locked)
    
    def monitor_device_status(self):
        """Monitor the device status in a background thread"""
        while True:
            # In a real application, we would check the actual device status here
            # For now, just sleep and continue
            time.sleep(1)

def main():
    root = tk.Tk()
    app = KeyLockApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 