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
Shared test fixtures and utilities for memory leak tests.
"""

import shutil
import tempfile
from decimal import Decimal
from pathlib import Path

from nautilus_trader.backtest.engine import BacktestEngineConfig
from nautilus_trader.backtest.node import BacktestDataConfig
from nautilus_trader.backtest.node import BacktestEngineConfig as NodeBacktestEngineConfig
from nautilus_trader.backtest.node import BacktestRunConfig
from nautilus_trader.backtest.node import BacktestVenueConfig
from nautilus_trader.config import ImportableStrategyConfig
from nautilus_trader.config import LoggingConfig
from nautilus_trader.core.datetime import dt_to_unix_nanos
from nautilus_trader.examples.strategies.ema_cross_twap import EMACrossTWAPConfig
from nautilus_trader.model.currencies import ETH
from nautilus_trader.model.currencies import USDT
from nautilus_trader.model.data import BarType
from nautilus_trader.model.data import QuoteTick
from nautilus_trader.model.enums import AccountType
from nautilus_trader.model.enums import OmsType
from nautilus_trader.model.identifiers import TraderId
from nautilus_trader.model.identifiers import Venue
from nautilus_trader.model.objects import Money
from nautilus_trader.persistence.catalog import ParquetDataCatalog
from nautilus_trader.persistence.wranglers import BarDataWrangler
from nautilus_trader.persistence.wranglers import QuoteTickDataWrangler
from nautilus_trader.persistence.wranglers import TradeTickDataWrangler
from nautilus_trader.test_kit.providers import TestDataProvider
from nautilus_trader.test_kit.providers import TestInstrumentProvider


# Common test constants
DEFAULT_TOTAL_RUNS = 128
DEFAULT_CHUNK_SIZE = 1000


class TestInstruments:
    """Common test instruments used across memory leak tests."""
    
    @staticmethod
    def get_sim_venue():
        return Venue("SIM")
    
    @staticmethod
    def get_binance_venue():
        return Venue("BINANCE")
    
    @staticmethod
    def get_audusd_sim():
        return TestInstrumentProvider.default_fx_ccy("AUD/USD", TestInstruments.get_sim_venue())
    
    @staticmethod
    def get_gbpusd_sim():
        return TestInstrumentProvider.default_fx_ccy("GBP/USD", TestInstruments.get_sim_venue())
    
    @staticmethod
    def get_ethusdt_binance():
        return TestInstrumentProvider.ethusdt_binance()


class TestConfigurations:
    """Common test configurations for memory leak tests."""
    
    @staticmethod
    def get_basic_backtest_engine_config():
        """Get basic backtest engine configuration."""
        return BacktestEngineConfig(
            trader_id=TraderId("BACKTESTER-001"),
            logging=LoggingConfig(bypass_logging=True),
        )
    
    @staticmethod
    def get_binance_venue_config():
        """Get Binance venue configuration for backtests."""
        return {
            "venue": TestInstruments.get_binance_venue(),
            "oms_type": OmsType.NETTING,
            "account_type": AccountType.CASH,  # Spot CASH account (not for perpetuals or futures)
            "base_currency": None,  # Multi-currency account
            "starting_balances": [Money(1_000_000.0, USDT), Money(10.0, ETH)],
        }
    
    @staticmethod
    def get_sim_venue_config():
        """Get SIM venue configuration for backtests."""
        return BacktestVenueConfig(
            name="SIM",
            oms_type="HEDGING",
            account_type="MARGIN",  # Use MARGIN account for FX pairs
            base_currency="USD",
            starting_balances=["1_000_000 USD"],
        )
    
    @staticmethod
    def get_ema_cross_twap_config(instrument):
        """Get EMA Cross TWAP strategy configuration."""
        return EMACrossTWAPConfig(
            instrument_id=instrument.id,
            bar_type=BarType.from_str("ETHUSDT.BINANCE-250-TICK-LAST-INTERNAL"),
            trade_size=Decimal("0.05"),
            fast_ema_period=10,
            slow_ema_period=20,
            twap_horizon_secs=10.0,
            twap_interval_secs=2.5,
        )
    
    @staticmethod
    def get_ema_cross_strategy_config(instrument):
        """Get EMA Cross strategy configuration for catalog tests."""
        return ImportableStrategyConfig(
            strategy_path="nautilus_trader.examples.strategies.ema_cross:EMACross",
            config_path="nautilus_trader.examples.strategies.ema_cross:EMACrossConfig",
            config={
                "instrument_id": instrument.id,
                "bar_type": "AUD/USD.SIM-15-MINUTE-BID-INTERNAL",
                "fast_ema_period": 10,
                "slow_ema_period": 20,
                "trade_size": Decimal("100_000"),
            },
        )


class TestDataWranglers:
    """Common data wranglers for memory leak tests."""
    
    @staticmethod
    def get_trade_tick_wrangler(instrument=None):
        """Get trade tick data wrangler."""
        if instrument is None:
            instrument = TestInstruments.get_ethusdt_binance()
        return TradeTickDataWrangler(instrument=instrument)
    
    @staticmethod
    def get_quote_tick_wrangler(instrument=None):
        """Get quote tick data wrangler."""
        if instrument is None:
            instrument = TestInstruments.get_audusd_sim()
        return QuoteTickDataWrangler(instrument=instrument)
    
    @staticmethod
    def get_bid_bar_wrangler(instrument=None):
        """Get bid bar data wrangler."""
        if instrument is None:
            instrument = TestInstruments.get_gbpusd_sim()
        return BarDataWrangler(
            bar_type=BarType.from_str("GBP/USD.SIM-1-MINUTE-BID-EXTERNAL"),
            instrument=instrument,
        )
    
    @staticmethod
    def get_ask_bar_wrangler(instrument=None):
        """Get ask bar data wrangler."""
        if instrument is None:
            instrument = TestInstruments.get_gbpusd_sim()
        return BarDataWrangler(
            bar_type=BarType.from_str("GBP/USD.SIM-1-MINUTE-ASK-EXTERNAL"),
            instrument=instrument,
        )


def setup_catalog_with_data():
    """
    Set up a temporary catalog with test data.
    
    Returns:
        tuple: (catalog_path, instrument, provider)
    """
    # Create temporary directory for catalog
    catalog_path = Path(tempfile.mkdtemp())
    catalog = ParquetDataCatalog(catalog_path)

    # Set up instrument and data
    instrument = TestInstruments.get_audusd_sim()
    provider = TestDataProvider()
    wrangler = QuoteTickDataWrangler(instrument=instrument)

    # Process test data and write to catalog
    ticks = wrangler.process(provider.read_csv_ticks("truefx/audusd-ticks.csv"))
    ticks.sort(key=lambda x: x.ts_init)

    catalog.write_data([instrument])
    catalog.write_data(ticks)

    return catalog_path, instrument, provider


def cleanup_catalog(catalog_path):
    """Clean up temporary catalog directory."""
    if catalog_path.exists():
        shutil.rmtree(catalog_path)


def get_catalog_backtest_config(catalog_path, instrument, provider):
    """
    Get backtest configuration for catalog-based tests.
    
    Args:
        catalog_path: Path to the catalog
        instrument: Test instrument
        provider: Test data provider
        
    Returns:
        BacktestRunConfig: Configured backtest run
    """
    venues = [TestConfigurations.get_sim_venue_config()]

    # Get data range from test file
    test_data = provider.read_csv_ticks("truefx/audusd-ticks.csv")
    start_time = dt_to_unix_nanos(test_data.index[0])
    end_time = dt_to_unix_nanos(test_data.index[-1])

    data_configs = [
        BacktestDataConfig(
            catalog_path=str(catalog_path),
            data_cls=QuoteTick,
            instrument_id=instrument.id,
            start_time=start_time,
            end_time=end_time,
        ),
    ]

    strategies = [TestConfigurations.get_ema_cross_strategy_config(instrument)]

    # Configure backtest run with streaming (small chunk size for memory testing)
    return BacktestRunConfig(
        engine=NodeBacktestEngineConfig(
            trader_id=TraderId("BACKTESTER-001"),
            strategies=strategies,
            logging=LoggingConfig(bypass_logging=True),
        ),
        data=data_configs,
        venues=venues,
        chunk_size=DEFAULT_CHUNK_SIZE,  # Enable streaming mode with small chunks
        raise_exception=True,  # Raise exceptions to catch errors
    )
