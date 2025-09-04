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
Memory leak test for data processing components.

This test runs multiple data processing iterations to detect memory leaks in
data wranglers, tick processing, and bar data processing components.
"""

from nautilus_trader.test_kit.providers import TestDataProvider
from tests.mem_leak_tests.memory_utils import run_memory_test
from tests.mem_leak_tests.test_fixtures import DEFAULT_TOTAL_RUNS
from tests.mem_leak_tests.test_fixtures import TestDataWranglers
from tests.mem_leak_tests.test_fixtures import TestInstruments


def process_quote_ticks():
    """Process quote tick data for memory leak testing."""
    provider = TestDataProvider()
    instrument = TestInstruments.get_audusd_sim()
    wrangler = TestDataWranglers.get_quote_tick_wrangler(instrument)
    
    # Process quote tick data
    ticks = wrangler.process(provider.read_csv_ticks("truefx/audusd-ticks.csv"))
    
    # Clean up references
    del ticks
    del wrangler


def process_trade_ticks():
    """Process trade tick data for memory leak testing."""
    provider = TestDataProvider()
    instrument = TestInstruments.get_ethusdt_binance()
    wrangler = TestDataWranglers.get_trade_tick_wrangler(instrument)
    
    # Process trade tick data
    ticks = wrangler.process(provider.read_csv_ticks("binance/ethusdt-trades.csv"))
    
    # Clean up references
    del ticks
    del wrangler


def process_bar_data():
    """Process bar data for memory leak testing."""
    provider = TestDataProvider()
    instrument = TestInstruments.get_gbpusd_sim()
    
    # Set up bid and ask wranglers using shared utilities
    bid_wrangler = TestDataWranglers.get_bid_bar_wrangler(instrument)
    ask_wrangler = TestDataWranglers.get_ask_bar_wrangler(instrument)
    
    # Process bid and ask bar data (limited to 10k bars for memory testing)
    bid_bars = bid_wrangler.process(
        data=provider.read_csv_bars("fxcm/gbpusd-m1-bid-2012.csv")[:10_000],
    )
    ask_bars = ask_wrangler.process(
        data=provider.read_csv_bars("fxcm/gbpusd-m1-ask-2012.csv")[:10_000],
    )
    
    # Clean up references
    del bid_bars
    del ask_bars
    del bid_wrangler
    del ask_wrangler


def run_single_data_processing():
    """Run a single data processing iteration for memory leak testing."""
    # Process different types of data
    process_quote_ticks()
    process_trade_ticks()
    process_bar_data()


if __name__ == "__main__":
    # Run memory leak test
    run_memory_test(
        test_func=run_single_data_processing,
        runs=DEFAULT_TOTAL_RUNS,
        test_name="Data Processing Memory Leak Test"
    )
