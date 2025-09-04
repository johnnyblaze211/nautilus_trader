# -------------------------------------------------------------------------------------------------
#  Copyright (C) 2015-2025 Nautech Systems Pty Ltd. All rights reserved.
#  https://nautechsystems.io
#
#  Licensed under the GNU Lesser General Public License Version 3.0 (the "License");
#  You may not use this file except in compliance with the License.
#  You may obtain a copy of the License at https://www.gnu.org/licenses/lgpl-3.0.en.html
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
# -------------------------------------------------------------------------------------------------

"""
Memory monitoring utilities for memory leak tests.
"""

import gc
import tracemalloc
from typing import Callable


class MemoryMonitor:
    """Memory monitoring utility for tracking memory usage during test runs."""
    
    def __init__(self):
        self.max_peak_memory = 0
        self.snapshot = None
        self.initial_snapshot = None
    
    def start_monitoring(self):
        """Start memory monitoring."""
        tracemalloc.start()
        self.max_peak_memory = 0
        self.snapshot = None
        self.initial_snapshot = None
    
    def stop_monitoring(self):
        """Stop memory monitoring."""
        tracemalloc.stop()
    
    def take_snapshot(self, run_number: int = 0):
        """
        Take a memory snapshot and update tracking variables.
        
        Args:
            run_number: Current run number for logging
        """
        self.snapshot = tracemalloc.take_snapshot()
        if run_number == 0:
            self.initial_snapshot = self.snapshot

        current_memory, peak = tracemalloc.get_traced_memory()
        current_memory_mb = current_memory / (1024 * 1024)
        peak_mb = peak / (1024 * 1024)

        # Update max_memory if current_memory is greater
        if peak_mb > self.max_peak_memory:
            self.max_peak_memory = current_memory_mb

        # Print memory usage information
        print(f"Memory allocated after run {run_number + 1}: {current_memory_mb:.2f} MB")
        print(f"Max peak memory recorded: {self.max_peak_memory:.2f} MB")
        print()
    
    def reset_peak(self):
        """Reset peak memory tracking and run garbage collection."""
        gc.collect()
        tracemalloc.reset_peak()
    
    def print_memory_diff(self, top_n: int = 10):
        """
        Print memory differences since initial snapshot.
        
        Args:
            top_n: Number of top differences to display
        """
        if self.snapshot is None or self.initial_snapshot is None:
            print("No snapshots available for comparison")
            return
        
        # Find and display largest memory blocks, since initial run
        top_stats = self.snapshot.compare_to(self.initial_snapshot, "lineno")
        print(f"[ Top {top_n} differences ]")
        for stat in top_stats[:top_n]:
            print(stat)

        if top_stats:
            stat = top_stats[0]
            print(f"{stat.count} memory blocks: {stat.size / 1024:.1f} KiB")
            for line in stat.traceback.format():
                print(line)


def snapshot_memory(runs: int):
    """
    Decorator to snapshot memory usage for a function across multiple runs.
    
    Args:
        runs: Number of times to run the function
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            monitor = MemoryMonitor()
            monitor.start_monitoring()

            # Run the function n times and measure memory usage each time
            for i in range(runs):
                print(f"Run {i}...")

                # Run func
                func(*args, **kwargs)

                # Take snapshot and measure memory
                monitor.take_snapshot(i)
                
                # Reset for next run
                monitor.reset_peak()

            # Stop monitoring and print final results
            monitor.stop_monitoring()
            monitor.print_memory_diff()

        return wrapper
    return decorator


def run_memory_test(test_func: Callable, runs: int = 128, test_name: str = "Memory Test"):
    """
    Run a memory leak test with monitoring.
    
    Args:
        test_func: Function to test for memory leaks
        runs: Number of test runs
        test_name: Name of the test for logging
    """
    print(f"Starting {test_name} with {runs} runs")
    print("=" * 50)
    
    monitor = MemoryMonitor()
    monitor.start_monitoring()
    
    try:
        for i in range(runs):
            print(f"Run: {i + 1}/{runs}")
            
            # Run the test function
            test_func()
            
            # Monitor memory usage
            monitor.take_snapshot(i)
            monitor.reset_peak()
            
    except Exception as e:
        print(f"Test failed on run {i + 1} with error: {e}")
        raise
    finally:
        monitor.stop_monitoring()
        print(f"\n{test_name} completed")
        print("=" * 50)
        monitor.print_memory_diff()
