
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

import pytest

from nautilus_trader.common.signal import generate_signal_class
from nautilus_trader.core import nautilus_pyo3
from nautilus_trader.core.nautilus_pyo3 import AggressorSide
from nautilus_trader.model.data import BarAggregation
from nautilus_trader.model.data import BarSpecification
from nautilus_trader.model.data import BarType
from nautilus_trader.model.data import CustomData
from nautilus_trader.model.data import DataType
from nautilus_trader.model.data import QuoteTick
from nautilus_trader.model.data import TradeTick
from nautilus_trader.model.enums import PriceType
from nautilus_trader.model.objects import Price
from nautilus_trader.model.objects import Quantity
from nautilus_trader.test_kit.functions import eventually
from nautilus_trader.test_kit.providers import TestInstrumentProvider
from nautilus_trader.test_kit.stubs.data import TestDataStubs
from nautilus_trader.trading.filters import NewsEvent
from nautilus_trader.trading.filters import NewsImpact


_TEST_TIMEOUT = 5.0
_AUDUSD_SIM = TestInstrumentProvider.default_fx_ccy("AUD/USD")


@pytest.mark.xdist_group(name="postgres_integration")
class TestPostgresDataStorage:
    """Test PostgreSQL data storage operations."""

    @pytest.mark.asyncio
    async def test_add_and_load_trades(self, postgres_database_adapter):
        # Arrange
        trade = TradeTick(
            instrument_id=_AUDUSD_SIM.id,
            price=Price.from_str("1.00001"),
            size=Quantity.from_int(100_000),
            aggressor_side=AggressorSide.BUY,
            trade_id=nautilus_pyo3.TradeId("123456789"),
            ts_event=0,
            ts_init=0,
        )

        # Act
        postgres_database_adapter.add_trade_ticks([trade])

        # Allow time for insertion
        await eventually(lambda: len(postgres_database_adapter.load_trade_ticks(_AUDUSD_SIM.id)) > 0, timeout=_TEST_TIMEOUT)

        # Assert
        result = postgres_database_adapter.load_trade_ticks(_AUDUSD_SIM.id)
        assert len(result) == 1
        assert result[0] == trade

    @pytest.mark.asyncio
    async def test_add_and_load_quotes(self, postgres_database_adapter):
        # Arrange
        quote = QuoteTick(
            instrument_id=_AUDUSD_SIM.id,
            bid_price=Price.from_str("1.00000"),
            ask_price=Price.from_str("1.00001"),
            bid_size=Quantity.from_int(100_000),
            ask_size=Quantity.from_int(100_000),
            ts_event=0,
            ts_init=0,
        )

        # Act
        postgres_database_adapter.add_quote_ticks([quote])

        # Allow time for insertion
        await eventually(lambda: len(postgres_database_adapter.load_quote_ticks(_AUDUSD_SIM.id)) > 0, timeout=_TEST_TIMEOUT)

        # Assert
        result = postgres_database_adapter.load_quote_ticks(_AUDUSD_SIM.id)
        assert len(result) == 1
        assert result[0] == quote

    @pytest.mark.asyncio
    async def test_add_and_load_bars(self, postgres_database_adapter):
        # Arrange
        bar_spec = BarSpecification(1, BarAggregation.MINUTE, PriceType.BID)
        bar_type = BarType(_AUDUSD_SIM.id, bar_spec)
        bar = TestDataStubs.bar_5decimal()

        # Act
        postgres_database_adapter.add_bars([bar])

        # Allow time for insertion
        await eventually(lambda: len(postgres_database_adapter.load_bars(bar_type)) > 0, timeout=_TEST_TIMEOUT)

        # Assert
        result = postgres_database_adapter.load_bars(bar_type)
        assert len(result) == 1
        assert result[0] == bar

    @pytest.mark.asyncio
    async def test_add_and_load_signals(self, postgres_database_adapter):
        # Arrange
        signal_class = generate_signal_class(
            name="MySignal",
            value_type=float,
        )
        signal = signal_class(value=1.0, ts_event=0, ts_init=0)

        # Act
        postgres_database_adapter.add_signals([signal])

        # Allow time for insertion
        await eventually(lambda: len(postgres_database_adapter.load_signals(signal_class)) > 0, timeout=_TEST_TIMEOUT)

        # Assert
        result = postgres_database_adapter.load_signals(signal_class)
        assert len(result) == 1
        assert result[0] == signal

    @pytest.mark.asyncio
    async def test_add_and_load_custom_data(self, postgres_database_adapter):
        # Arrange
        news_event = NewsEvent(
            impact=NewsImpact.HIGH,
            name="Unemployment Rate",
            currency=_AUDUSD_SIM.base_currency,
            ts_event=0,
            ts_init=0,
        )

        data_type = DataType(
            type=NewsEvent,
            metadata={"currency": "USD"},
        )

        custom_data = CustomData(data_type, news_event)

        # Act
        postgres_database_adapter.add_custom_data([custom_data])

        # Allow time for insertion
        await eventually(lambda: len(postgres_database_adapter.load_custom_data(data_type)) > 0, timeout=_TEST_TIMEOUT)

        # Assert
        result = postgres_database_adapter.load_custom_data(data_type)
        assert len(result) == 1
        assert result[0] == custom_data
