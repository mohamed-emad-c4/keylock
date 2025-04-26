import os
import sys
import time
import json
import threading
import logging
from datetime import datetime

from settings import get_theme_colors, save_config, open_config
from utils import resource_path

# Configure logging
log_dir = resource_path("logs")
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(log_dir, "keylock.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

class KeylockController:
    def __init__(self, ui):
        self.ui = ui
        self.running = False
        self.scheduler_running = False
        self.elapsed_time = 0
        self.timer_thread = None
        self.scheduler_thread = None
        self.stop_event = threading.Event()
        
        # Load configuration on startup
        self.load_settings()
        
        # Log startup
        logging.info("Keylock application started")
    
    def load_settings(self):
        """Load settings from config file"""
        try:
            config = open_config()
            
            # Apply theme
            if "theme" in config:
                self.ui.theme = config["theme"]
                self.ui.colors = get_theme_colors(self.ui.theme)
                self.ui.apply_theme()
                self.ui.theme_btn.configure(text="☀️" if self.ui.theme == "dark" else "🌙")
            
            # Apply other settings
            if "block_keyboard" in config:
                self.ui.block_keyboard_var.set(config["block_keyboard"])
            
            if "block_mouse" in config:
                self.ui.block_mouse_var.set(config["block_mouse"])
            
            if "use_password" in config:
                self.ui.use_password_var.set(config["use_password"])
                if config["use_password"]:
                    self.ui.toggle_password_fields()
                    
                    # For security, we don't load the password directly
                    # Just indicate a password is set
                    if "password" in config and config["password"]:
                        self.ui.password_entry.insert(0, "********")
                        self.ui.confirm_password_entry.insert(0, "********")
            
            logging.info("Settings loaded successfully")
            
        except Exception as e:
            logging.error(f"Error loading settings: {str(e)}")
            # If loading fails, we'll use defaults
    
    def save_settings(self):
        """Save current settings to config file"""
        try:
            # Get values from UI
            config = {
                "theme": self.ui.theme,
                "block_keyboard": self.ui.block_keyboard_var.get(),
                "block_mouse": self.ui.block_mouse_var.get(),
                "use_password": self.ui.use_password_var.get(),
            }
            
            # Save password if set and not the placeholder
            if self.ui.use_password_var.get():
                password = self.ui.password_entry.get()
                confirm = self.ui.confirm_password_entry.get()
                
                if password != "********" and confirm != "********":
                    if password == confirm and password:
                        # In a real app, we would hash this password
                        config["password"] = password
                    elif password != confirm:
                        self.ui.root.after(0, lambda: self.ui.show_error(
                            "Password Error", "Passwords don't match"))
                        return False
            
            # Save to file
            save_config(config)
            logging.info("Settings saved successfully")
            
            # Show success message
            self.ui.root.after(0, lambda: self.ui.show_message(
                "Settings Saved", "Your settings have been saved successfully"))
            
            return True
            
        except Exception as e:
            logging.error(f"Error saving settings: {str(e)}")
            self.ui.root.after(0, lambda: self.ui.show_error(
                "Save Error", f"Could not save settings: {str(e)}"))
            return False
    
    def start_keylock(self):
        """Start keylock protection"""
        if self.running:
            return
        
        try:
            # Check password if enabled
            if self.ui.use_password_var.get() and not self._validate_password():
                return
            
            # Update UI
            self.ui.update_status("Starting...", True)
            
            # Set flags
            self.running = True
            self.stop_event.clear()
            
            # Start timer thread
            self.elapsed_time = 0
            self.timer_thread = threading.Thread(target=self._run_timer)
            self.timer_thread.daemon = True
            self.timer_thread.start()
            
            # Start input blocking based on settings
            block_keyboard = self.ui.block_keyboard_var.get()
            block_mouse = self.ui.block_mouse_var.get()
            
            # Log action
            logging.info(f"Keylock started (keyboard: {block_keyboard}, mouse: {block_mouse})")
            
            # In a real implementation, we would initialize the actual
            # keyboard/mouse blocking here
            
            # Update status after successful start
            self.ui.root.after(1000, lambda: self.ui.update_status("Running", True))
            
        except Exception as e:
            self.running = False
            logging.error(f"Error starting keylock: {str(e)}")
            self.ui.root.after(0, lambda: self.ui.show_error(
                "Start Error", f"Could not start keylock: {str(e)}"))
            self.ui.update_status("Error", False)
    
    def stop_keylock(self):
        """Stop keylock protection"""
        if not self.running:
            return
        
        try:
            # Update UI
            self.ui.update_status("Stopping...", True)
            
            # Signal threads to stop
            self.stop_event.set()
            
            # Stop input blocking
            # In a real implementation, we would stop the actual
            # keyboard/mouse blocking here
            
            # Wait for timer thread to finish
            if self.timer_thread and self.timer_thread.is_alive():
                self.timer_thread.join(2.0)  # Wait up to 2 seconds
            
            # Update flags and UI
            self.running = False
            self.ui.update_status("Stopped", False)
            
            # Log action
            logging.info(f"Keylock stopped after {self.elapsed_time} seconds")
            
        except Exception as e:
            logging.error(f"Error stopping keylock: {str(e)}")
            self.ui.root.after(0, lambda: self.ui.show_error(
                "Stop Error", f"Could not stop keylock: {str(e)}"))
    
    def start_scheduler(self):
        """Start the scheduler"""
        if self.scheduler_running:
            return
        
        try:
            # Get schedule items from UI
            schedule_items = []
            for item_id in self.ui.schedule_tree.get_children():
                values = self.ui.schedule_tree.item(item_id, "values")
                # Format: (id, start_time, duration, status)
                
                # Parse duration text to get seconds
                duration_text = values[2]
                if "second" in duration_text:
                    duration = int(duration_text.split()[0])
                elif "minute" in duration_text:
                    duration = int(duration_text.split()[0]) * 60
                elif "hour" in duration_text:
                    duration = int(duration_text.split()[0]) * 3600
                else:
                    duration = 30 * 60  # Default to 30 minutes
                
                schedule_items.append({
                    "id": values[0],
                    "start_time": values[1],
                    "duration": duration,
                    "status": "Pending"
                })
            
            # Check if we have any items
            if not schedule_items:
                self.ui.root.after(0, lambda: self.ui.show_error(
                    "Scheduler Error", "No schedule items to run"))
                return
            
            # Update UI
            self.ui.update_status("Scheduler starting...", None)
            self.scheduler_running = True
            self.ui.start_scheduler_btn.configure(state="disabled")
            self.ui.stop_scheduler_btn.configure(state="normal")
            
            # Start scheduler thread
            self.scheduler_thread = threading.Thread(
                target=self._run_scheduler, 
                args=(schedule_items,)
            )
            self.scheduler_thread.daemon = True
            self.scheduler_thread.start()
            
            # Log action
            logging.info(f"Scheduler started with {len(schedule_items)} items")
            
            # Update status
            self.ui.root.after(1000, lambda: self.ui.update_status("Scheduler running", None))
            
        except Exception as e:
            self.scheduler_running = False
            logging.error(f"Error starting scheduler: {str(e)}")
            self.ui.root.after(0, lambda: self.ui.show_error(
                "Scheduler Error", f"Could not start scheduler: {str(e)}"))
            self.ui.update_status("Error", None)
    
    def stop_scheduler(self):
        """Stop the scheduler"""
        if not self.scheduler_running:
            return
        
        try:
            # Update UI
            self.ui.update_status("Stopping scheduler...", None)
            
            # Signal thread to stop
            self.stop_event.set()
            
            # Wait for thread to finish
            if self.scheduler_thread and self.scheduler_thread.is_alive():
                self.scheduler_thread.join(2.0)  # Wait up to 2 seconds
            
            # Update flags and UI
            self.scheduler_running = False
            self.ui.start_scheduler_btn.configure(state="normal")
            self.ui.stop_scheduler_btn.configure(state="disabled")
            
            # Update tree items to show stopped status
            for item_id in self.ui.schedule_tree.get_children():
                values = self.ui.schedule_tree.item(item_id, "values")
                if values[3] == "Running":
                    self.ui.schedule_tree.item(item_id, values=(
                        values[0], values[1], values[2], "Stopped"
                    ))
            
            # Update status
            self.ui.update_status("Scheduler stopped", None)
            
            # Log action
            logging.info("Scheduler stopped")
            
        except Exception as e:
            logging.error(f"Error stopping scheduler: {str(e)}")
            self.ui.root.after(0, lambda: self.ui.show_error(
                "Scheduler Error", f"Could not stop scheduler: {str(e)}"))
    
    def _run_timer(self):
        """Background thread to update timer display"""
        while not self.stop_event.is_set() and self.running:
            try:
                # Update UI with current time
                self.ui.root.after(0, lambda t=self.elapsed_time: self.ui.update_time(t))
                
                # Sleep for a second
                time.sleep(1)
                
                # Increment elapsed time
                self.elapsed_time += 1
                
            except Exception as e:
                logging.error(f"Error in timer thread: {str(e)}")
                break
    
    def _run_scheduler(self, schedule_items):
        """Background thread to run scheduled items"""
        while not self.stop_event.is_set() and self.scheduler_running:
            try:
                # Check if we have items to process
                if not schedule_items:
                    break
                
                # Get current time
                current_time = datetime.now().strftime("%H:%M:%S")
                
                # Process each item
                for item in schedule_items[:]:  # Copy to avoid modification during iteration
                    if item["status"] == "Running":
                        continue
                    
                    # Check if it's time to start this item
                    if item["start_time"] <= current_time and item["status"] == "Pending":
                        # Update status in the tree
                        self._update_item_status(item["id"], "Running")
                        
                        # Start keylock if not already running
                        if not self.running:
                            self.ui.root.after(0, self.start_keylock)
                        
                        # Schedule stop after duration
                        self.ui.root.after(
                            item["duration"] * 1000,  # Convert to milliseconds
                            lambda i=item["id"]: self._complete_scheduled_item(i)
                        )
                        
                        # Update item status
                        item["status"] = "Running"
                        
                        # Log action
                        logging.info(f"Started scheduled item {item['id']} for {item['duration']} seconds")
                
                # Sleep for a second
                time.sleep(1)
                
            except Exception as e:
                logging.error(f"Error in scheduler thread: {str(e)}")
                break
        
        # Log completion
        logging.info("Scheduler thread completed")
    
    def _update_item_status(self, item_id, status):
        """Update the status of a schedule item in the tree"""
        for tree_id in self.ui.schedule_tree.get_children():
            values = self.ui.schedule_tree.item(tree_id, "values")
            if str(values[0]) == str(item_id):
                self.ui.schedule_tree.item(tree_id, values=(
                    values[0], values[1], values[2], status
                ))
                break
    
    def _complete_scheduled_item(self, item_id):
        """Complete a scheduled item and stop keylock if needed"""
        try:
            # Update item status
            self._update_item_status(item_id, "Completed")
            
            # Check if there are any other running items
            other_running = False
            for tree_id in self.ui.schedule_tree.get_children():
                values = self.ui.schedule_tree.item(tree_id, "values")
                if values[3] == "Running" and str(values[0]) != str(item_id):
                    other_running = True
                    break
            
            # If no other items are running, stop keylock
            if not other_running and self.running:
                self.stop_keylock()
            
            # Log completion
            logging.info(f"Completed scheduled item {item_id}")
            
        except Exception as e:
            logging.error(f"Error completing scheduled item: {str(e)}")
    
    def _validate_password(self):
        """Validate the password if password protection is enabled"""
        # Get saved password from config
        try:
            config = open_config()
            saved_password = config.get("password", "")
            
            if not saved_password:
                # No password set yet, let it pass
                return True
            
            # Ask for password
            password = self.ui.ask_password("Enter Password", "Enter password to unlock:")
            
            if password == saved_password:
                return True
            else:
                self.ui.show_error("Access Denied", "Incorrect password")
                return False
                
        except Exception as e:
            logging.error(f"Error validating password: {str(e)}")
            self.ui.show_error("Authentication Error", str(e))
            return False 