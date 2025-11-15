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
Memory leak test for backtest engine using TWAP strategy.

This test runs multiple backtest iterations to detect memory leaks in the
backtest engine, strategy execution, and data processing components.
"""

from nautilus_trader.backtest.engine import BacktestEngine
from nautilus_trader.examples.algorithms.twap import TWAPExecAlgorithm
from nautilus_trader.examples.strategies.ema_cross_twap import EMACrossTWAP
from tests.mem_leak_tests.memory_utils import run_memory_test
from tests.mem_leak_tests.test_fixtures import DEFAULT_TOTAL_RUNS
from tests.mem_leak_tests.test_fixtures import TestConfigurations
from tests.mem_leak_tests.test_fixtures import TestDataWranglers
from tests.mem_leak_tests.test_fixtures import TestInstruments


def setup_backtest_engine():
    """
    Set up and configure a backtest engine with TWAP strategy.
    
    Returns:
        BacktestEngine: Configured backtest engine
    """
    # Get shared configurations
    config = TestConfigurations.get_basic_backtest_engine_config()
    engine = BacktestEngine(config=config)
    
    # Get test instrument
    instrument = TestInstruments.get_ethusdt_binance()
    
    # Add trading venue using shared configuration
    venue_config = TestConfigurations.get_binance_venue_config()
    engine.add_venue(**venue_config)
    
    # Add instruments
    engine.add_instrument(instrument)
    
    return engine, instrument


def add_test_data(engine, instrument):
    """
    Add test data to the backtest engine.
    
    Args:
        engine: Backtest engine
        instrument: Trading instrument
    """
    from nautilus_trader.test_kit.providers import TestDataProvider
    
    provider = TestDataProvider()
    wrangler = TestDataWranglers.get_trade_tick_wrangler(instrument)
    ticks = wrangler.process(provider.read_csv_ticks("binance/ethusdt-trades.csv"))
    engine.add_data(ticks)


def add_strategy_and_algorithm(engine, instrument):
    """
    Add strategy and execution algorithm to the engine.
    
    Args:
        engine: Backtest engine
        instrument: Trading instrument
    """
    # Configure strategy using shared configuration
    strategy_config = TestConfigurations.get_ema_cross_twap_config(instrument)
    strategy = EMACrossTWAP(config=strategy_config)
    engine.add_strategy(strategy=strategy)
    
    # Add execution algorithm
    exec_algorithm = TWAPExecAlgorithm()
    engine.add_exec_algorithm(exec_algorithm)


def run_single_backtest():
    """Run a single backtest iteration for memory leak testing."""
    # Set up backtest engine
    engine, instrument = setup_backtest_engine()
    
    try:
        # Add test data
        add_test_data(engine, instrument)
        
        # Add strategy and algorithm
        add_strategy_and_algorithm(engine, instrument)
        
        # Run the engine (from start to end of data)
        engine.run()
        
        # For repeated backtest runs make sure to reset the engine
        engine.reset()
        
    finally:
        # Good practice to dispose of the object
        engine.dispose()


if __name__ == "__main__":
    # Run memory leak test
    run_memory_test(
        test_func=run_single_backtest,
        runs=DEFAULT_TOTAL_RUNS,
        test_name="Backtest Engine Memory Leak Test"
    )
