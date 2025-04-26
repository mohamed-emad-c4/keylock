import threading
import time
import datetime
import logging
import json
import os
from typing import Dict, List, Optional, Callable, Any, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("keylock.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("keylock-scheduler")

class Schedule:
    """Class representing a scheduled locking task"""
    def __init__(
        self, 
        id: str,
        name: str,
        action: str,  # 'keyboard', 'mouse', or 'both'
        time_type: str,  # 'once', 'daily', 'weekdays', 'weekends', 'countdown'
        start_time: Union[datetime.time, datetime.datetime, int],  # time, full datetime, or seconds for countdown
        days: Optional[List[int]] = None,  # 0-6 for weekdays when time_type is 'weekly'
        duration: Optional[int] = None,  # Duration in seconds, None means indefinite
        enabled: bool = True
    ):
        self.id = id
        self.name = name
        self.action = action
        self.time_type = time_type
        self.start_time = start_time
        self.days = days or []
        self.duration = duration
        self.enabled = enabled
        self.timer: Optional[threading.Timer] = None
        self.unlock_timer: Optional[threading.Timer] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert schedule to dict for serialization"""
        result = {
            "id": self.id,
            "name": self.name,
            "action": self.action,
            "time_type": self.time_type,
            "enabled": self.enabled
        }
        
        # Handle different time formats
        if self.time_type == 'countdown':
            result["start_time"] = self.start_time  # seconds
        elif isinstance(self.start_time, datetime.time):
            result["start_time"] = self.start_time.strftime("%H:%M:%S")
        elif isinstance(self.start_time, datetime.datetime):
            result["start_time"] = self.start_time.strftime("%Y-%m-%d %H:%M:%S")
            
        if self.days:
            result["days"] = self.days
            
        if self.duration is not None:
            result["duration"] = self.duration
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Schedule':
        """Create a Schedule object from a dictionary"""
        # Parse the start_time based on time_type
        start_time = data["start_time"]
        if data["time_type"] == 'countdown':
            start_time = int(start_time)
        elif data["time_type"] == 'once':
            start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        else:
            # Daily, weekdays, weekends
            start_time = datetime.datetime.strptime(start_time, "%H:%M:%S").time()
            
        return cls(
            id=data["id"],
            name=data["name"],
            action=data["action"],
            time_type=data["time_type"],
            start_time=start_time,
            days=data.get("days", []),
            duration=data.get("duration", None),
            enabled=data.get("enabled", True)
        )


class ScheduleManager:
    """Class to manage scheduled locking tasks"""
    def __init__(self, lock_callback: Callable[[str], None], unlock_callback: Callable[[], None]):
        self.schedules: Dict[str, Schedule] = {}
        self.lock_callback = lock_callback
        self.unlock_callback = unlock_callback
        self.scheduler_thread: Optional[threading.Thread] = None
        self.running = False
        self.lock = threading.RLock()
        
    def start(self):
        """Start the scheduler thread"""
        if self.scheduler_thread is None or not self.scheduler_thread.is_alive():
            self.running = True
            self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
            self.scheduler_thread.start()
            logger.info("Scheduler started")
    
    def stop(self):
        """Stop the scheduler thread"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=1.0)
        self._cancel_all_timers()
        logger.info("Scheduler stopped")
    
    def _cancel_all_timers(self):
        """Cancel all active timers"""
        with self.lock:
            for schedule in self.schedules.values():
                if schedule.timer:
                    schedule.timer.cancel()
                    schedule.timer = None
                if schedule.unlock_timer:
                    schedule.unlock_timer.cancel()
                    schedule.unlock_timer = None
    
    def add_schedule(self, schedule: Schedule) -> bool:
        """Add a new schedule"""
        with self.lock:
            if schedule.id in self.schedules:
                logger.warning(f"Schedule with ID {schedule.id} already exists")
                return False
            
            self.schedules[schedule.id] = schedule
            self._schedule_next_run(schedule)
            self._save_schedules()
            logger.info(f"Added schedule: {schedule.name} ({schedule.id})")
            return True
    
    def update_schedule(self, schedule: Schedule) -> bool:
        """Update an existing schedule"""
        with self.lock:
            if schedule.id not in self.schedules:
                logger.warning(f"Schedule with ID {schedule.id} not found")
                return False
            
            # Cancel existing timers
            existing = self.schedules[schedule.id]
            if existing.timer:
                existing.timer.cancel()
            if existing.unlock_timer:
                existing.unlock_timer.cancel()
            
            # Update with new schedule
            self.schedules[schedule.id] = schedule
            self._schedule_next_run(schedule)
            self._save_schedules()
            logger.info(f"Updated schedule: {schedule.name} ({schedule.id})")
            return True
    
    def remove_schedule(self, schedule_id: str) -> bool:
        """Remove a schedule"""
        with self.lock:
            if schedule_id not in self.schedules:
                logger.warning(f"Schedule with ID {schedule_id} not found")
                return False
            
            schedule = self.schedules[schedule_id]
            if schedule.timer:
                schedule.timer.cancel()
            if schedule.unlock_timer:
                schedule.unlock_timer.cancel()
                
            del self.schedules[schedule_id]
            self._save_schedules()
            logger.info(f"Removed schedule: {schedule_id}")
            return True
    
    def get_schedule(self, schedule_id: str) -> Optional[Schedule]:
        """Get a schedule by ID"""
        return self.schedules.get(schedule_id)
    
    def get_schedules(self) -> List[Schedule]:
        """Get all schedules"""
        return list(self.schedules.values())
    
    def _schedule_next_run(self, schedule: Schedule):
        """Schedule the next run of a schedule"""
        if not schedule.enabled:
            return
        
        now = datetime.datetime.now()
        seconds_until_next = 0
        
        if schedule.time_type == 'countdown':
            # Simple countdown timer (in seconds)
            seconds_until_next = schedule.start_time
        
        elif schedule.time_type == 'once':
            # One-time schedule at specific date/time
            if isinstance(schedule.start_time, datetime.datetime):
                if schedule.start_time > now:
                    seconds_until_next = (schedule.start_time - now).total_seconds()
                else:
                    # Already passed, don't schedule
                    schedule.enabled = False
                    return
        
        else:
            # Recurring schedules
            target_time = schedule.start_time
            if not isinstance(target_time, datetime.time):
                logger.error(f"Invalid start_time type for recurring schedule: {type(target_time)}")
                return
                
            # Create a datetime for today at the target time
            target_datetime = datetime.datetime.combine(now.date(), target_time)
            
            if schedule.time_type == 'daily':
                # Schedule runs every day
                if target_datetime > now:
                    # Still today
                    seconds_until_next = (target_datetime - now).total_seconds()
                else:
                    # Tomorrow
                    tomorrow = now + datetime.timedelta(days=1)
                    target_datetime = datetime.datetime.combine(tomorrow.date(), target_time)
                    seconds_until_next = (target_datetime - now).total_seconds()
            
            elif schedule.time_type == 'weekdays':
                # Schedule runs on weekdays (Monday=0 to Friday=4)
                days_ahead = 0
                current_weekday = now.weekday()
                
                if current_weekday < 5:  # It's a weekday
                    if target_datetime > now:
                        # Still today
                        seconds_until_next = (target_datetime - now).total_seconds()
                    else:
                        # Next weekday
                        if current_weekday == 4:  # Friday
                            days_ahead = 3  # Next Monday
                        else:
                            days_ahead = 1  # Next day
                else:  # It's a weekend
                    # Next Monday
                    days_ahead = 7 - current_weekday + 0  # 0 is Monday
                
                if days_ahead > 0:
                    future_date = now + datetime.timedelta(days=days_ahead)
                    target_datetime = datetime.datetime.combine(future_date.date(), target_time)
                    seconds_until_next = (target_datetime - now).total_seconds()
            
            elif schedule.time_type == 'weekends':
                # Schedule runs on weekends (Saturday=5, Sunday=6)
                days_ahead = 0
                current_weekday = now.weekday()
                
                if current_weekday >= 5:  # It's a weekend
                    if target_datetime > now:
                        # Still today
                        seconds_until_next = (target_datetime - now).total_seconds()
                    else:
                        # Next day if Saturday, otherwise next Saturday
                        if current_weekday == 5:  # Saturday
                            days_ahead = 1  # Sunday
                        else:  # Sunday
                            days_ahead = 6  # Next Saturday
                else:  # It's a weekday
                    # Next Saturday
                    days_ahead = 5 - current_weekday
                
                if days_ahead > 0:
                    future_date = now + datetime.timedelta(days=days_ahead)
                    target_datetime = datetime.datetime.combine(future_date.date(), target_time)
                    seconds_until_next = (target_datetime - now).total_seconds()
            
            elif schedule.time_type == 'weekly' and schedule.days:
                # Schedule runs on specific days of the week
                # Find the next occurrence
                current_weekday = now.weekday()
                days = sorted(schedule.days)  # Ensure days are sorted
                
                # Find the next day in the scheduled days
                next_day = None
                for day in days:
                    if day > current_weekday:
                        next_day = day
                        break
                
                if next_day is not None:
                    # Found a day this week
                    days_ahead = next_day - current_weekday
                else:
                    # Needs to be next week
                    days_ahead = 7 - current_weekday + days[0]
                
                if days_ahead == 0:  # Today is a scheduled day
                    if target_datetime > now:
                        # Still today
                        seconds_until_next = (target_datetime - now).total_seconds()
                    else:
                        # Find the next day next week
                        if len(days) > 1:
                            # There are other days this week
                            next_day = days[1]
                            days_ahead = next_day - current_weekday
                        else:
                            # Next week
                            days_ahead = 7
                
                future_date = now + datetime.timedelta(days=days_ahead)
                target_datetime = datetime.datetime.combine(future_date.date(), target_time)
                seconds_until_next = (target_datetime - now).total_seconds()
        
        # Schedule the timer
        if seconds_until_next > 0:
            schedule.timer = threading.Timer(
                seconds_until_next,
                self._execute_schedule,
                args=[schedule.id]
            )
            schedule.timer.daemon = True
            schedule.timer.start()
            
            # Log the scheduled time
            target_time = now + datetime.timedelta(seconds=seconds_until_next)
            logger.info(f"Scheduled {schedule.name} to run at {target_time}")
    
    def _execute_schedule(self, schedule_id: str):
        """Execute a scheduled task"""
        with self.lock:
            if schedule_id not in self.schedules:
                logger.warning(f"Schedule {schedule_id} not found for execution")
                return
                
            schedule = self.schedules[schedule_id]
            
            if not schedule.enabled:
                logger.info(f"Schedule {schedule.name} ({schedule.id}) is disabled, skipping execution")
                return
                
            logger.info(f"Executing schedule: {schedule.name} ({schedule.id})")
            
            try:
                # Call the lock callback with the action type
                self.lock_callback(schedule.action)
                
                # If there's a duration, schedule an unlock
                if schedule.duration is not None:
                    logger.info(f"Scheduling unlock in {schedule.duration} seconds")
                    schedule.unlock_timer = threading.Timer(
                        schedule.duration,
                        self._execute_unlock,
                        args=[schedule.id]
                    )
                    schedule.unlock_timer.daemon = True
                    schedule.unlock_timer.start()
                
                # If it's a one-time schedule, disable it after execution
                if schedule.time_type == 'once' or schedule.time_type == 'countdown':
                    schedule.enabled = False
                    self._save_schedules()
                else:
                    # Schedule the next run for recurring schedules
                    self._schedule_next_run(schedule)
                    
            except Exception as e:
                logger.error(f"Error executing schedule {schedule.name}: {e}")
                # Try to schedule next run despite error
                try:
                    self._schedule_next_run(schedule)
                except Exception as ex:
                    logger.error(f"Failed to reschedule {schedule.name}: {ex}")
    
    def _execute_unlock(self, schedule_id: str):
        """Execute the unlock operation for a schedule"""
        with self.lock:
            if schedule_id not in self.schedules:
                logger.warning(f"Schedule {schedule_id} not found for unlock operation")
                return
                
            schedule = self.schedules[schedule_id]
            logger.info(f"Executing unlock for schedule: {schedule.name} ({schedule.id})")
            
            try:
                # Call the unlock callback
                self.unlock_callback()
                
                # Clear the unlock timer reference
                schedule.unlock_timer = None
                
            except Exception as e:
                logger.error(f"Error executing unlock for schedule {schedule.name}: {e}")
    
    def _scheduler_loop(self):
        """Main scheduler loop for checking and executing schedules"""
        logger.info("Scheduler loop started")
        
        try:
            # First, load any saved schedules
            self._load_schedules()
            
            # Schedule initial runs
            for schedule in self.schedules.values():
                self._schedule_next_run(schedule)
            
            # Keep the thread alive but don't do heavy work
            # The actual scheduling is done with individual timers
            while self.running:
                time.sleep(1)
                
        except Exception as e:
            logger.error(f"Error in scheduler loop: {e}")
        
        logger.info("Scheduler loop ended")
    
    def _save_schedules(self):
        """Save schedules to file"""
        try:
            schedules_data = {
                schedule_id: schedule.to_dict() 
                for schedule_id, schedule in self.schedules.items()
            }
            
            with open("keylock_schedules.json", "w") as f:
                json.dump(schedules_data, f, indent=2)
                
            logger.info("Schedules saved to file")
        except Exception as e:
            logger.error(f"Error saving schedules: {e}")
    
    def _load_schedules(self):
        """Load schedules from file"""
        if not os.path.exists("keylock_schedules.json"):
            logger.info("No schedules file found")
            return
        
        try:
            with open("keylock_schedules.json", "r") as f:
                schedules_data = json.load(f)
            
            for schedule_id, schedule_data in schedules_data.items():
                schedule = Schedule.from_dict(schedule_data)
                self.schedules[schedule_id] = schedule
                
            logger.info(f"Loaded {len(self.schedules)} schedules from file")
        except Exception as e:
            logger.error(f"Error loading schedules: {e}")


# Helper function to create a unique ID
def generate_id() -> str:
    """Generate a unique ID for a schedule"""
    import uuid
    return str(uuid.uuid4())[:8]


# Example usage:
# schedule_manager = ScheduleManager(lock_callback=lock_devices, unlock_callback=unlock_devices)
# schedule_manager.start()
# daily_schedule = Schedule(
#     id=generate_id(),
#     name="Daily Lock",
#     action="both",
#     time_type="daily",
#     start_time=datetime.time(12, 0, 0),  # Noon every day
#     duration=3600  # 1 hour
# )
# schedule_manager.add_schedule(daily_schedule) 