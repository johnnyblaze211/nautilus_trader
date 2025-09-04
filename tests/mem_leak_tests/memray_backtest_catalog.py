#!/usr/bin/env python3
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
Memory leak test for backtest node using catalog streaming.

This test runs multiple backtest iterations using catalog-based data streaming
to detect memory leaks in the backtest node, catalog system, and streaming
data processing components.
"""

from nautilus_trader.backtest.node import BacktestNode
from tests.mem_leak_tests.memory_utils import run_memory_test
from tests.mem_leak_tests.test_fixtures import DEFAULT_TOTAL_RUNS
from tests.mem_leak_tests.test_fixtures import cleanup_catalog
from tests.mem_leak_tests.test_fixtures import get_catalog_backtest_config
from tests.mem_leak_tests.test_fixtures import setup_catalog_with_data


def run_single_catalog_backtest():
    """Run a single catalog-based backtest iteration for memory leak testing."""
    # Set up catalog with data for each run
    catalog_path, instrument, provider = setup_catalog_with_data()
    
    try:
        # Get backtest configuration using shared utilities
        config = get_catalog_backtest_config(catalog_path, instrument, provider)
        
        # Build and run backtest node
        node = BacktestNode(configs=[config])
        
        try:
            results = node.run()
            
            # Clean up results and node
            del results
            del node
            
        except Exception as e:
            print(f"Backtest failed with error: {e}")
            del node
            raise
            
    finally:
        # Clean up temporary catalog directory
        cleanup_catalog(catalog_path)


if __name__ == "__main__":
    # Run memory leak test
    run_memory_test(
        test_func=run_single_catalog_backtest,
        runs=DEFAULT_TOTAL_RUNS,
        test_name="Catalog Backtest Memory Leak Test"
    )
