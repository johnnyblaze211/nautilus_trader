
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

from nautilus_trader.test_kit.functions import eventually
from nautilus_trader.test_kit.mocks.actors import MockActor
from nautilus_trader.test_kit.mocks.strategies import MockStrategy
from nautilus_trader.test_kit.stubs.data import TestDataStubs


@pytest.mark.xdist_group(name="redis_integration")
class TestRedisActorsStrategies:
    """Test Redis actor and strategy operations."""

    @pytest.mark.asyncio
    async def test_update_actor(self, redis_database_adapter):
        # Arrange
        components = redis_database_adapter._test_components
        actor = MockActor()
        actor.register_base(
            portfolio=components['portfolio'],
            msgbus=components['msgbus'],
            cache=components['cache'],
            clock=components['clock'],
        )

        # Act
        redis_database_adapter.update_actor(actor)

        # Allow MPSC thread to insert
        await eventually(lambda: redis_database_adapter.load_actor(actor.id))

        result = redis_database_adapter.load_actor(actor.id)

        # Assert
        assert result == {"A": 1}

    @pytest.mark.asyncio
    async def test_update_strategy(self, redis_database_adapter):
        # Arrange
        components = redis_database_adapter._test_components
        strategy = MockStrategy(TestDataStubs.bartype_btcusdt_binance_100tick_last())
        strategy.register(
            trader_id=components['trader_id'],
            portfolio=components['portfolio'],
            msgbus=components['msgbus'],
            cache=components['cache'],
            clock=components['clock'],
        )

        # Act
        redis_database_adapter.update_strategy(strategy)

        # Allow MPSC thread to insert
        await eventually(lambda: redis_database_adapter.load_strategy(strategy.id))

        result = redis_database_adapter.load_strategy(strategy.id)

        # Assert
        assert result == {"UserState": b'{"A": 1}'}

    @pytest.mark.asyncio
    async def test_delete_actor(self, redis_database_adapter):
        # Arrange
        components = redis_database_adapter._test_components
        actor = MockActor()
        actor.register_base(
            portfolio=components['portfolio'],
            msgbus=components['msgbus'],
            cache=components['cache'],
            clock=components['clock'],
        )

        redis_database_adapter.update_actor(actor)

        # Allow MPSC thread to insert
        await eventually(lambda: redis_database_adapter.load_actor(actor.id))

        # Act
        redis_database_adapter.delete_actor(actor.id)

        # Allow MPSC thread to delete
        await eventually(lambda: redis_database_adapter.load_actor(actor.id) is None)

        result = redis_database_adapter.load_actor(actor.id)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_strategy(self, redis_database_adapter):
        # Arrange
        components = redis_database_adapter._test_components
        strategy = MockStrategy(TestDataStubs.bartype_btcusdt_binance_100tick_last())
        strategy.register(
            trader_id=components['trader_id'],
            portfolio=components['portfolio'],
            msgbus=components['msgbus'],
            cache=components['cache'],
            clock=components['clock'],
        )

        redis_database_adapter.update_strategy(strategy)

        # Allow MPSC thread to insert
        await eventually(lambda: redis_database_adapter.load_strategy(strategy.id))

        # Act
        redis_database_adapter.delete_strategy(strategy.id)

        # Allow MPSC thread to delete
        await eventually(lambda: redis_database_adapter.load_strategy(strategy.id) is None)

        result = redis_database_adapter.load_strategy(strategy.id)

        # Assert
        assert result is None
