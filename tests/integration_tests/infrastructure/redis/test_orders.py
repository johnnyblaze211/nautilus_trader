
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
from nautilus_trader.model.enums import OrderType
from nautilus_trader.model.identifiers import ExecAlgorithmId
from nautilus_trader.model.objects import Price
from nautilus_trader.model.objects import Quantity
from nautilus_trader.model.orders import LimitOrder
from nautilus_trader.model.orders import MarketOrder
from nautilus_trader.test_kit.functions import eventually
from nautilus_trader.test_kit.providers import TestInstrumentProvider
from nautilus_trader.test_kit.stubs.events import TestEventStubs


_AUDUSD_SIM = TestInstrumentProvider.default_fx_ccy("AUD/USD")


@pytest.mark.xdist_group(name="redis_integration")
class TestRedisOrders:
    """Test Redis order operations."""

    @pytest.mark.asyncio
    async def test_add_order(self, redis_database_adapter):
        # Arrange
        strategy = redis_database_adapter._test_components['strategy']
        order = strategy.order_factory.market(
            _AUDUSD_SIM.id,
            OrderSide.BUY,
            Quantity.from_int(100_000),
        )

        # Act
        redis_database_adapter.add_order(order)

        # Allow MPSC thread to insert
        await eventually(lambda: redis_database_adapter.load_order(order.client_order_id))

        # Assert
        assert redis_database_adapter.load_order(order.client_order_id) == order

    @pytest.mark.asyncio
    async def test_update_order_when_not_already_exists_logs(self, redis_database_adapter):
        # Arrange
        strategy = redis_database_adapter._test_components['strategy']
        order = strategy.order_factory.stop_market(
            _AUDUSD_SIM.id,
            OrderSide.BUY,
            Quantity.from_int(100_000),
            Price.from_str("1.00000"),
        )

        # Act
        redis_database_adapter.update_order(order)

        # Assert
        assert True  # No exceptions raised

    @pytest.mark.asyncio
    async def test_update_order_for_open_order(self, redis_database_adapter):
        # Arrange
        strategy = redis_database_adapter._test_components['strategy']
        order = strategy.order_factory.stop_market(
            _AUDUSD_SIM.id,
            OrderSide.BUY,
            Quantity.from_int(100_000),
            Price.from_str("1.00000"),
        )

        redis_database_adapter.add_order(order)

        # Allow MPSC thread to insert
        await eventually(lambda: redis_database_adapter.load_order(order.client_order_id))

        order.apply(TestEventStubs.order_submitted(order))
        redis_database_adapter.update_order(order)

        order.apply(TestEventStubs.order_accepted(order))

        # Act
        redis_database_adapter.update_order(order)

        # Assert
        assert redis_database_adapter.load_order(order.client_order_id) == order

    @pytest.mark.asyncio
    async def test_update_order_for_closed_order(self, redis_database_adapter):
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

        order.apply(TestEventStubs.order_submitted(order))
        redis_database_adapter.update_order(order)

        order.apply(TestEventStubs.order_accepted(order))
        redis_database_adapter.update_order(order)

        fill = TestEventStubs.order_filled(
            order,
            instrument=_AUDUSD_SIM,
            last_px=Price.from_str("1.00001"),
        )

        order.apply(fill)

        # Allow MPSC thread to insert
        await eventually(lambda: redis_database_adapter.load_order(order.client_order_id))

        # Act
        redis_database_adapter.update_order(order)

        # Assert
        assert redis_database_adapter.load_order(order.client_order_id) == order

    @pytest.mark.asyncio
    async def test_load_order_when_no_order_in_database_returns_none(self, redis_database_adapter):
        # Arrange
        strategy = redis_database_adapter._test_components['strategy']
        order = strategy.order_factory.market(
            _AUDUSD_SIM.id,
            OrderSide.BUY,
            Quantity.from_int(100_000),
        )

        # Act
        result = redis_database_adapter.load_order(order.client_order_id)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_load_order_when_market_order_in_database_returns_order(self, redis_database_adapter):
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

        # Act
        result = redis_database_adapter.load_order(order.client_order_id)

        # Assert
        assert result == order

    @pytest.mark.asyncio
    async def test_load_order_with_exec_algorithm_params(self, redis_database_adapter):
        # Arrange
        strategy = redis_database_adapter._test_components['strategy']
        exec_algorithm_params = {"horizon_secs": 20, "interval_secs": 2.5}
        order = strategy.order_factory.market(
            _AUDUSD_SIM.id,
            OrderSide.BUY,
            Quantity.from_int(100_000),
            exec_algorithm_id=ExecAlgorithmId("TWAP"),
            exec_algorithm_params=exec_algorithm_params,
        )

        redis_database_adapter.add_order(order)

        # Allow MPSC thread to insert
        await eventually(lambda: redis_database_adapter.load_order(order.client_order_id))

        # Act
        result = redis_database_adapter.load_order(order.client_order_id)

        # Assert
        assert result == order
        assert result.exec_algorithm_params

    @pytest.mark.asyncio
    async def test_load_order_when_limit_order_in_database_returns_order(self, redis_database_adapter):
        # Arrange
        strategy = redis_database_adapter._test_components['strategy']
        order = strategy.order_factory.limit(
            _AUDUSD_SIM.id,
            OrderSide.BUY,
            Quantity.from_int(100_000),
            Price.from_str("1.00000"),
        )

        redis_database_adapter.add_order(order)

        # Allow MPSC thread to insert
        await eventually(lambda: redis_database_adapter.load_order(order.client_order_id))

        # Act
        result = redis_database_adapter.load_order(order.client_order_id)

        # Assert
        assert result == order

    @pytest.mark.asyncio
    async def test_load_order_when_transformed_to_market_order_in_database_returns_order(self, redis_database_adapter):
        # Arrange
        strategy = redis_database_adapter._test_components['strategy']
        order = strategy.order_factory.limit(
            _AUDUSD_SIM.id,
            OrderSide.BUY,
            Quantity.from_int(100_000),
            Price.from_str("1.00000"),
        )

        order = MarketOrder.transform_py(order, 0)

        redis_database_adapter.add_order(order)

        # Allow MPSC thread to insert
        await eventually(lambda: redis_database_adapter.load_order(order.client_order_id))

        # Act
        result = redis_database_adapter.load_order(order.client_order_id)

        # Assert
        assert result == order
        assert result.order_type == OrderType.MARKET

    @pytest.mark.asyncio
    async def test_load_order_when_transformed_to_limit_order_in_database_returns_order(self, redis_database_adapter):
        # Arrange
        strategy = redis_database_adapter._test_components['strategy']
        order = strategy.order_factory.limit_if_touched(
            _AUDUSD_SIM.id,
            OrderSide.BUY,
            Quantity.from_int(100_000),
            Price.from_str("1.00000"),
            Price.from_str("1.00000"),
        )

        order = LimitOrder.transform_py(order, 0)

        redis_database_adapter.add_order(order)

        # Allow MPSC thread to insert
        await eventually(lambda: redis_database_adapter.load_order(order.client_order_id))

        # Act
        result = redis_database_adapter.load_order(order.client_order_id)

        # Assert
        assert result == order
        assert result.order_type == OrderType.LIMIT

    @pytest.mark.asyncio
    async def test_load_order_when_stop_market_order_in_database_returns_order(self, redis_database_adapter):
        # Arrange
        strategy = redis_database_adapter._test_components['strategy']
        order = strategy.order_factory.stop_market(
            _AUDUSD_SIM.id,
            OrderSide.BUY,
            Quantity.from_int(100_000),
            Price.from_str("1.00000"),
        )

        redis_database_adapter.add_order(order)

        # Allow MPSC thread to insert
        await eventually(lambda: redis_database_adapter.load_order(order.client_order_id))

        # Act
        result = redis_database_adapter.load_order(order.client_order_id)

        # Assert
        assert result == order

    @pytest.mark.asyncio
    async def test_load_order_when_stop_limit_order_in_database_returns_order(self, redis_database_adapter):
        # Arrange
        strategy = redis_database_adapter._test_components['strategy']
        order = strategy.order_factory.stop_limit(
            _AUDUSD_SIM.id,
            OrderSide.BUY,
            Quantity.from_int(100_000),
            Price.from_str("1.00000"),
            Price.from_str("1.00001"),
        )

        redis_database_adapter.add_order(order)

        # Allow MPSC thread to insert
        await eventually(lambda: redis_database_adapter.load_order(order.client_order_id))

        # Act
        result = redis_database_adapter.load_order(order.client_order_id)

        # Assert
        assert result == order

    @pytest.mark.asyncio
    async def test_load_orders_cache_when_no_orders(self, redis_database_adapter):
        # Arrange, Act
        result = redis_database_adapter.load_orders()

        # Assert
        assert result == {}

    @pytest.mark.asyncio
    async def test_load_orders_cache_when_one_order_in_database(self, redis_database_adapter):
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

        # Act
        result = redis_database_adapter.load_orders()

        # Assert
        assert result == {order.client_order_id: order}
