import sys
import os
import logging
import traceback
from dashboard import KeylockDashboard

def print_file_structure_info():
    """Print information about the enhanced file structure"""
    print("\nKeyLock - Enhanced UI Dashboard")
    print("================================")
    print("\nThe application has been enhanced with a modern UI:")
    
    # Core modules
    print("\nCore Modules:")
    print("  - main.py        - Entry point")
    print("  - dashboard.py   - Modern UI dashboard")
    print("  - core.py        - Core keyboard/mouse locking functionality")
    print("  - controller.py  - Input handling and hotkeys")
      
    # UI modules
    print("\nUI Modules:")
    print("  - ui_components.py - Reusable UI widgets")
    
    # Feature modules
    print("\nFeature Modules:")
    print("  - scheduler.py    - Schedule management")
    print("  - settings.py     - Configuration management")
    
    print("\nBenefits:")
    print("  - Modern, responsive UI design")
    print("  - Improved user experience")
    print("  - Better visualization of device status")
    print("  - Enhanced scheduling capabilities")
    print("================================\n")

def setup_logging():
    """Configure logging for the application"""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(log_dir, "keylock.log")),
            logging.StreamHandler()
        ]
    )
    
    # Create application logger
    logger = logging.getLogger("keylock")
    logger.info("KeyLock application starting")
    
    return logger

def main():
    """Main entry point for the application"""
    try:
        # Setup logging
        logger = setup_logging()
        
        # Print info
        print_file_structure_info()
        
        # Initialize and run the dashboard
        dashboard = KeylockDashboard()
        return dashboard.run()
    except Exception as e:
        # Log any unhandled exceptions
        error_msg = f"Unhandled exception: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        logging.error(error_msg)
        return 1

if __name__ == "__main__":
    sys.exit(main())
