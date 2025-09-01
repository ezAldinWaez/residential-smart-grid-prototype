"""Status monitoring and logging for Raspberry Pi controller."""

from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Any
import threading
import time
import json
from datetime import datetime

if TYPE_CHECKING:
    from .gpio_controller import GPIOController
    from ..rsgp.houses_sim.simulator import HousesSimulator


class StatusMonitor:
    """Monitor and log system status for debugging and analysis.
    
    Provides real-time status monitoring, logging capabilities, and system health checks
    for the Raspberry Pi hardware controller.
    
    Args:
        gpio_controller (GPIOController): GPIO controller instance.
        rsgp_hs (HousesSimulator): Houses simulator instance.
    """
    
    def __init__(self, gpio_controller: 'GPIOController', rsgp_hs: 'HousesSimulator') -> None:
        self._gpio_controller = gpio_controller
        self._rsgp_hs = rsgp_hs
        
        self._running = False
        self._monitor_thread: threading.Thread = None
        
        self._status_history: list[Dict[str, Any]] = []
        self._max_history_size = 100
    
    def start(self, monitor_interval: float = 5.0) -> None:
        """Start status monitoring.
        
        Args:
            monitor_interval (float): Monitoring interval in seconds.
        """
        if self._running:
            return
            
        self._running = True
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(monitor_interval,),
            daemon=True
        )
        self._monitor_thread.start()
        print("Status monitor started")
    
    def stop(self) -> None:
        """Stop status monitoring."""
        self._running = False
        
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=1.0)
        
        print("Status monitor stopped")
    
    def _monitor_loop(self, monitor_interval: float) -> None:
        """Main monitoring loop."""
        while self._running:
            try:
                status = self._collect_status()
                self._log_status(status)
                self._update_history(status)
                time.sleep(monitor_interval)
            except Exception as e:
                print(f"Error in status monitoring: {e}")
                time.sleep(monitor_interval)
    
    def _collect_status(self) -> Dict[str, Any]:
        """Collect current system status."""
        timestamp = datetime.now().isoformat()
        
        try:
            hardware_status = self._gpio_controller.get_status()
        except Exception as e:
            hardware_status = {"error": str(e)}
        
        try:
            simulation_status = {
                "simulation_running": self._rsgp_hs.is_running(),
                "system_load": self._rsgp_hs.get_system_load(),
                "houses": [
                    {
                        "house_id": i + 1,
                        "load": self._rsgp_hs.get_house(i).get_load(),
                        "utility_line": self._rsgp_hs.get_house(i).get_utility_line(),
                        "load_line": self._rsgp_hs.get_house(i).get_load_line(),
                    }
                    for i in range(self._rsgp_hs.get_num_houses())
                ]
            }
        except Exception as e:
            simulation_status = {"error": str(e)}
        
        return {
            "timestamp": timestamp,
            "hardware": hardware_status,
            "simulation": simulation_status
        }
    
    def _log_status(self, status: Dict[str, Any]) -> None:
        """Log status information."""
        if "error" in status.get("hardware", {}):
            print(f"Hardware error: {status['hardware']['error']}")
        
        if "error" in status.get("simulation", {}):
            print(f"Simulation error: {status['simulation']['error']}")
    
    def _update_history(self, status: Dict[str, Any]) -> None:
        """Update status history."""
        self._status_history.append(status)
        
        if len(self._status_history) > self._max_history_size:
            self._status_history.pop(0)
    
    def get_current_status(self) -> Dict[str, Any]:
        """Get current system status."""
        return self._collect_status()
    
    def get_status_history(self) -> list[Dict[str, Any]]:
        """Get status history."""
        return self._status_history.copy()
    
    def export_status_log(self, file_path: str) -> None:
        """Export status history to JSON file.
        
        Args:
            file_path (str): Path to export file.
        """
        try:
            with open(file_path, 'w') as f:
                json.dump(self._status_history, f, indent=2)
            print(f"Status log exported to {file_path}")
        except Exception as e:
            print(f"Error exporting status log: {e}")