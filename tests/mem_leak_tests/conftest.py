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
Pytest configuration and fixtures for memory leak tests.

This module provides shared fixtures and utilities for memory leak testing.
The main memory monitoring functionality has been moved to memory_utils.py
for better organization and reusability.
"""

# Import the memory monitoring utilities for backward compatibility
from tests.mem_leak_tests.memory_utils import MemoryMonitor
from tests.mem_leak_tests.memory_utils import run_memory_test
from tests.mem_leak_tests.memory_utils import snapshot_memory

# Re-export for backward compatibility
__all__ = [
    "MemoryMonitor",
    "run_memory_test", 
    "snapshot_memory",
]


# Legacy function for backward compatibility
def snapshot_memory(runs):
    """
    Legacy decorator function - use memory_utils.snapshot_memory instead.
    
    This function is kept for backward compatibility with existing tests.
    New tests should use the memory_utils module directly.
    """
    from tests.mem_leak_tests.memory_utils import snapshot_memory as new_snapshot_memory
    return new_snapshot_memory(runs)
