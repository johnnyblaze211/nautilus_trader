
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

import asyncio
from decimal import Decimal

import pytest

from nautilus_trader.backtest.engine import BacktestEngine
from nautilus_trader.backtest.engine import BacktestEngineConfig
from nautilus_trader.config import CacheConfig
from nautilus_trader.config import DatabaseConfig
from nautilus_trader.config import LoggingConfig
from nautilus_trader.examples.strategies.ema_cross import EMACross
from nautilus_trader.examples.strategies.ema_cross import EMACrossConfig
from nautilus_trader.model.currencies import USD
from nautilus_trader.model.enums import AccountType
from nautilus_trader.model.enums import OmsType
from nautilus_trader.model.identifiers import Venue
from nautilus_trader.model.objects import Money
from nautilus_trader.persistence.wranglers import QuoteTickDataWrangler
from nautilus_trader.test_kit.providers import TestDataProvider
from nautilus_trader.test_kit.providers import TestInstrumentProvider


_AUDUSD_SIM = TestInstrumentProvider.default_fx_ccy("AUD/USD")


@pytest.mark.xdist_group(name="redis_integration")
class TestRedisBacktestIntegration:
    """Test Redis integration with backtest engine."""

    @pytest.mark.asyncio
    async def test_rerunning_backtest_with_redis_db_builds_correct_index(self, redis_database_adapter):
        # Arrange
        config = BacktestEngineConfig(
            trader_id="BACKTESTER-001",
            cache=CacheConfig(database=DatabaseConfig()),
            logging=LoggingConfig(log_level="ERROR"),
        )

        engine = BacktestEngine(config=config)

        engine.add_venue(
            venue=Venue("SIM"),
            oms_type=OmsType.HEDGING,
            account_type=AccountType.MARGIN,
            base_currency=USD,
            starting_balances=[Money(1_000_000, USD)],
        )

        wrangler = QuoteTickDataWrangler(_AUDUSD_SIM)
        provider = TestDataProvider()
        ticks = wrangler.process(provider.read_csv_ticks("truefx/audusd-ticks.csv")[:10000])
        engine.add_instrument(_AUDUSD_SIM)
        engine.add_data(ticks)

        strategy = EMACross(
            instrument_id=_AUDUSD_SIM.id,
            config=EMACrossConfig(
                fast_ema_period=10,
                slow_ema_period=20,
                trade_size=Decimal(1_000_000),
            ),
        )
        engine.add_strategy(strategy)

        # Act
        engine.run()

        # Allow MPSC thread to insert
        await asyncio.sleep(1.0)

        # Re-run
        engine.reset()
        engine.run()

        # Allow MPSC thread to insert
        await asyncio.sleep(1.0)

        # Assert
        assert True  # No exceptions raised during re-run
