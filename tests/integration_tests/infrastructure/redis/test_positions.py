
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

from nautilus_trader.model.enums import OrderSide
from nautilus_trader.model.identifiers import PositionId
from nautilus_trader.model.identifiers import TradeId
from nautilus_trader.model.objects import Price
from nautilus_trader.model.objects import Quantity
from nautilus_trader.model.position import Position
from nautilus_trader.test_kit.functions import eventually
from nautilus_trader.test_kit.providers import TestInstrumentProvider
from nautilus_trader.test_kit.stubs.events import TestEventStubs


_AUDUSD_SIM = TestInstrumentProvider.default_fx_ccy("AUD/USD")


@pytest.mark.xdist_group(name="redis_integration")
class TestRedisPositions:
    """Test Redis position operations."""

    @pytest.mark.asyncio
    async def test_add_position(self, redis_database_adapter):
        # Arrange
        strategy = redis_database_adapter._test_components['strategy']
        order = strategy.order_factory.market(
            _AUDUSD_SIM.id,
            OrderSide.BUY,
            Quantity.from_int(100_000),
        )

        redis_database_adapter.add_instrument(_AUDUSD_SIM)
        redis_database_adapter.add_order(order)

        # Allow MPSC thread to insert
        await eventually(lambda: redis_database_adapter.load_order(order.client_order_id))

        position_id = PositionId("P-1")
        fill = TestEventStubs.order_filled(
            order,
            instrument=_AUDUSD_SIM,
            position_id=position_id,
            last_px=Price.from_str("1.00000"),
        )

        position = Position(instrument=_AUDUSD_SIM, fill=fill)

        # Act
        redis_database_adapter.add_position(position)

        # Allow MPSC thread to insert
        await eventually(lambda: redis_database_adapter.load_position(position.id))

        # Assert
        assert redis_database_adapter.load_position(position.id) == position

    @pytest.mark.asyncio
    async def test_update_position_for_closed_position(self, redis_database_adapter):
        # Arrange
        strategy = redis_database_adapter._test_components['strategy']
        redis_database_adapter.add_instrument(_AUDUSD_SIM)

        # Allow MPSC thread to insert
        await eventually(lambda: redis_database_adapter.load_instrument(_AUDUSD_SIM.id))

        order1 = strategy.order_factory.market(
            _AUDUSD_SIM.id,
            OrderSide.BUY,
            Quantity.from_int(100_000),
        )

        position_id = PositionId("P-1")
        redis_database_adapter.add_order(order1)

        # Allow MPSC thread to insert
        await eventually(lambda: redis_database_adapter.load_order(order1.client_order_id))

        order1.apply(TestEventStubs.order_submitted(order1))
        redis_database_adapter.update_order(order1)

        order1.apply(TestEventStubs.order_accepted(order1))
        redis_database_adapter.update_order(order1)

        order1.apply(
            TestEventStubs.order_filled(
                order1,
                instrument=_AUDUSD_SIM,
                position_id=position_id,
                last_px=Price.from_str("1.00001"),
                trade_id=TradeId("1"),
            ),
        )
        redis_database_adapter.update_order(order1)

        # Allow MPSC thread to update
        await eventually(lambda: redis_database_adapter.load_order(order1.client_order_id))

        # Act
        position = Position(instrument=_AUDUSD_SIM, fill=order1.last_event)
        redis_database_adapter.add_position(position)

        # Allow MPSC thread to insert
        await eventually(lambda: redis_database_adapter.load_position(position.id))

        order2 = strategy.order_factory.market(
            _AUDUSD_SIM.id,
            OrderSide.SELL,
            Quantity.from_int(100_000),
        )

        redis_database_adapter.add_order(order2)

        # Allow MPSC thread to insert
        await eventually(lambda: redis_database_adapter.load_order(order2.client_order_id))

        order2.apply(TestEventStubs.order_submitted(order2))
        redis_database_adapter.update_order(order2)

        order2.apply(TestEventStubs.order_accepted(order2))
        redis_database_adapter.update_order(order2)

        filled = TestEventStubs.order_filled(
            order2,
            instrument=_AUDUSD_SIM,
            position_id=position_id,
            last_px=Price.from_str("1.00001"),
            trade_id=TradeId("2"),
        )

        order2.apply(filled)
        redis_database_adapter.update_order(order2)

        position.apply(filled)

        # Act
        redis_database_adapter.update_position(position)

        # Allow MPSC thread to update
        await eventually(lambda: redis_database_adapter.load_position(position.id))

        # Assert
        assert redis_database_adapter.load_position(position.id) == position

    @pytest.mark.asyncio
    async def test_update_position_when_not_already_exists_logs(self, redis_database_adapter):
        # Arrange
        strategy = redis_database_adapter._test_components['strategy']
        order = strategy.order_factory.market(
            _AUDUSD_SIM.id,
            OrderSide.BUY,
            Quantity.from_int(100_000),
        )

        redis_database_adapter.add_order(order)

        # Allow MPSC thread to insert
        await eventually(lambda: redis_database_adapter.load_order(order.client_order_id))

        position_id = PositionId("P-1")
        fill = TestEventStubs.order_filled(
            order,
            instrument=_AUDUSD_SIM,
            position_id=position_id,
            last_px=Price.from_str("1.00000"),
        )

        position = Position(instrument=_AUDUSD_SIM, fill=fill)

        # Act
        redis_database_adapter.update_position(position)

        # Assert
        assert True  # No exception raised

    @pytest.mark.asyncio
    async def test_load_position_when_no_position_in_database_returns_none(self, redis_database_adapter):
        # Arrange
        position_id = PositionId("P-1")

        # Act
        result = redis_database_adapter.load_position(position_id)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_load_position_when_no_instrument_in_database_returns_none(self, redis_database_adapter):
        # Arrange
        strategy = redis_database_adapter._test_components['strategy']
        order = strategy.order_factory.market(
            _AUDUSD_SIM.id,
            OrderSide.BUY,
            Quantity.from_int(100_000),
        )

        redis_database_adapter.add_order(order)

        # Allow MPSC thread to insert
        await eventually(lambda: redis_database_adapter.load_order(order.client_order_id))

        position_id = PositionId("P-1")
        fill = TestEventStubs.order_filled(
            order,
            instrument=_AUDUSD_SIM,
            position_id=position_id,
            last_px=Price.from_str("1.00000"),
        )

        position = Position(instrument=_AUDUSD_SIM, fill=fill)
        redis_database_adapter.add_position(position)

        # Allow MPSC thread to insert
        await eventually(lambda: redis_database_adapter.load_position(position.id))

        # Act
        result = redis_database_adapter.load_position(position.id)

        # Assert
        assert result is None  # No instrument in database

    @pytest.mark.asyncio
    async def test_load_position_when_position_in_database_returns_position(self, redis_database_adapter):
        # Arrange
        strategy = redis_database_adapter._test_components['strategy']
        redis_database_adapter.add_instrument(_AUDUSD_SIM)

        # Allow MPSC thread to insert
        await eventually(lambda: redis_database_adapter.load_instrument(_AUDUSD_SIM.id))

        order = strategy.order_factory.market(
            _AUDUSD_SIM.id,
            OrderSide.BUY,
            Quantity.from_int(100_000),
        )

        redis_database_adapter.add_order(order)

        # Allow MPSC thread to insert
        await eventually(lambda: redis_database_adapter.load_order(order.client_order_id))

        position_id = PositionId("P-1")
        fill = TestEventStubs.order_filled(
            order,
            instrument=_AUDUSD_SIM,
            position_id=position_id,
            last_px=Price.from_str("1.00000"),
        )

        position = Position(instrument=_AUDUSD_SIM, fill=fill)
        redis_database_adapter.add_position(position)

        # Allow MPSC thread to insert
        await eventually(lambda: redis_database_adapter.load_position(position.id))

        # Act
        result = redis_database_adapter.load_position(position.id)

        # Assert
        assert result == position

    @pytest.mark.asyncio
    async def test_load_positions_cache_when_no_positions(self, redis_database_adapter):
        # Arrange, Act
        result = redis_database_adapter.load_positions()

        # Assert
        assert result == {}

    @pytest.mark.asyncio
    async def test_load_positions_cache_when_one_position_in_database(self, redis_database_adapter):
        # Arrange
        strategy = redis_database_adapter._test_components['strategy']
        redis_database_adapter.add_instrument(_AUDUSD_SIM)

        # Allow MPSC thread to insert
        await eventually(lambda: redis_database_adapter.load_instrument(_AUDUSD_SIM.id))

        order = strategy.order_factory.market(
            _AUDUSD_SIM.id,
            OrderSide.BUY,
            Quantity.from_int(100_000),
        )

        redis_database_adapter.add_order(order)

        # Allow MPSC thread to insert
        await eventually(lambda: redis_database_adapter.load_order(order.client_order_id))

        position_id = PositionId("P-1")
        fill = TestEventStubs.order_filled(
            order,
            instrument=_AUDUSD_SIM,
            position_id=position_id,
            last_px=Price.from_str("1.00000"),
        )

        position = Position(instrument=_AUDUSD_SIM, fill=fill)
        redis_database_adapter.add_position(position)

        # Allow MPSC thread to insert
        await eventually(lambda: redis_database_adapter.load_position(position.id))

        # Act
        result = redis_database_adapter.load_positions()

        # Assert
        assert result == {position.id: position}
