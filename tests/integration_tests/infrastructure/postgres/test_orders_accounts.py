
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
from nautilus_trader.model.objects import Money
from nautilus_trader.model.objects import Quantity
from nautilus_trader.test_kit.functions import eventually
from nautilus_trader.test_kit.providers import TestInstrumentProvider
from nautilus_trader.test_kit.stubs.events import TestEventStubs
from nautilus_trader.test_kit.stubs.execution import TestExecStubs


_TEST_TIMEOUT = 5.0
_AUDUSD_SIM = TestInstrumentProvider.default_fx_ccy("AUD/USD")


@pytest.mark.xdist_group(name="postgres_integration")
class TestPostgresOrdersAccounts:
    """Test PostgreSQL order and account operations."""

    @pytest.mark.asyncio
    async def test_add_order(self, postgres_database_adapter):
        # Arrange
        strategy = postgres_database_adapter._test_components['strategy']
        order = strategy.order_factory.market(
            _AUDUSD_SIM.id,
            OrderSide.BUY,
            Quantity.from_int(100_000),
        )

        # Act
        postgres_database_adapter.add_order(order)

        # Allow time for insertion
        await eventually(lambda: postgres_database_adapter.load_order(order.client_order_id), timeout=_TEST_TIMEOUT)

        # Assert
        assert postgres_database_adapter.load_order(order.client_order_id) == order

    @pytest.mark.asyncio
    async def test_update_order_for_closed_order(self, postgres_database_adapter):
        # Arrange
        strategy = postgres_database_adapter._test_components['strategy']
        order = strategy.order_factory.market(
            _AUDUSD_SIM.id,
            OrderSide.BUY,
            Quantity.from_int(100_000),
        )

        postgres_database_adapter.add_order(order)

        # Allow time for insertion
        await eventually(lambda: postgres_database_adapter.load_order(order.client_order_id), timeout=_TEST_TIMEOUT)

        order.apply(TestEventStubs.order_submitted(order))
        postgres_database_adapter.update_order(order)

        order.apply(TestEventStubs.order_accepted(order))
        postgres_database_adapter.update_order(order)

        fill = TestEventStubs.order_filled(order, instrument=_AUDUSD_SIM)
        order.apply(fill)

        # Act
        postgres_database_adapter.update_order(order)

        # Allow time for update
        await eventually(lambda: postgres_database_adapter.load_order(order.client_order_id), timeout=_TEST_TIMEOUT)

        # Assert
        assert postgres_database_adapter.load_order(order.client_order_id) == order

    @pytest.mark.asyncio
    async def test_update_order_for_open_order(self, postgres_database_adapter):
        # Arrange
        strategy = postgres_database_adapter._test_components['strategy']
        order = strategy.order_factory.market(
            _AUDUSD_SIM.id,
            OrderSide.BUY,
            Quantity.from_int(100_000),
        )

        postgres_database_adapter.add_order(order)

        # Allow time for insertion
        await eventually(lambda: postgres_database_adapter.load_order(order.client_order_id), timeout=_TEST_TIMEOUT)

        order.apply(TestEventStubs.order_submitted(order))
        postgres_database_adapter.update_order(order)

        order.apply(TestEventStubs.order_accepted(order))

        # Act
        postgres_database_adapter.update_order(order)

        # Allow time for update
        await eventually(lambda: postgres_database_adapter.load_order(order.client_order_id), timeout=_TEST_TIMEOUT)

        # Assert
        assert postgres_database_adapter.load_order(order.client_order_id) == order

    @pytest.mark.asyncio
    async def test_add_order_snapshot(self, postgres_database_adapter):
        # Arrange
        strategy = postgres_database_adapter._test_components['strategy']
        order = strategy.order_factory.market(
            _AUDUSD_SIM.id,
            OrderSide.BUY,
            Quantity.from_int(100_000),
        )

        # Act
        postgres_database_adapter.add_order_snapshot(order)

        # Allow time for insertion
        await eventually(lambda: postgres_database_adapter.load_order(order.client_order_id), timeout=_TEST_TIMEOUT)

        # Assert
        assert postgres_database_adapter.load_order(order.client_order_id) == order

    @pytest.mark.asyncio
    async def test_add_position_snapshot(self, postgres_database_adapter):
        # Arrange
        strategy = postgres_database_adapter._test_components['strategy']
        postgres_database_adapter.add_instrument(_AUDUSD_SIM)

        # Allow time for insertion
        await eventually(lambda: postgres_database_adapter.load_instrument(_AUDUSD_SIM.id), timeout=_TEST_TIMEOUT)

        order = strategy.order_factory.market(
            _AUDUSD_SIM.id,
            OrderSide.BUY,
            Quantity.from_int(100_000),
        )

        fill = TestEventStubs.order_filled(order, instrument=_AUDUSD_SIM)
        from nautilus_trader.model.position import Position
        position = Position(instrument=_AUDUSD_SIM, fill=fill)

        # Act
        postgres_database_adapter.add_position_snapshot(position)

        # Allow time for insertion
        await eventually(lambda: postgres_database_adapter.load_position(position.id), timeout=_TEST_TIMEOUT)

        # Assert
        assert postgres_database_adapter.load_position(position.id) == position

    @pytest.mark.asyncio
    async def test_add_and_update_account(self, postgres_database_adapter):
        # Arrange
        account = TestExecStubs.cash_account()

        # Act
        postgres_database_adapter.add_account(account)

        # Allow time for insertion
        await eventually(lambda: postgres_database_adapter.load_account(account.id), timeout=_TEST_TIMEOUT)

        # Update account
        account_state = TestEventStubs.cash_account_state(
            account_id=account.id,
            balances=[Money(2_000_000, account.base_currency)],
        )
        postgres_database_adapter.update_account(account_state)

        # Allow time for update
        await eventually(lambda: postgres_database_adapter.load_account(account.id), timeout=_TEST_TIMEOUT)

        # Assert
        updated_account = postgres_database_adapter.load_account(account.id)
        assert updated_account.last_event == account_state

    @pytest.mark.asyncio
    async def test_update_account(self, postgres_database_adapter):
        # Arrange
        account = TestExecStubs.cash_account()
        postgres_database_adapter.add_account(account)

        # Allow time for insertion
        await eventually(lambda: postgres_database_adapter.load_account(account.id), timeout=_TEST_TIMEOUT)

        # Act
        account_state = TestEventStubs.cash_account_state(account_id=account.id)
        postgres_database_adapter.update_account(account_state)

        # Allow time for update
        await eventually(lambda: postgres_database_adapter.load_account(account.id), timeout=_TEST_TIMEOUT)

        # Assert
        updated_account = postgres_database_adapter.load_account(account.id)
        assert updated_account.last_event == account_state
