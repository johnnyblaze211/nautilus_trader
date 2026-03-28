
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

from nautilus_trader.model.enums import CurrencyType
from nautilus_trader.model.objects import Currency
from nautilus_trader.test_kit.functions import eventually
from nautilus_trader.test_kit.stubs.events import TestEventStubs
from nautilus_trader.test_kit.stubs.execution import TestExecStubs


@pytest.mark.xdist_group(name="redis_integration")
class TestRedisCurrencyAccount:
    """Test Redis currency and account operations."""

    @pytest.mark.asyncio
    async def test_add_currency(self, redis_database_adapter):
        # Arrange
        currency = Currency(
            code="1INCH",
            precision=8,
            iso4217=0,
            name="1INCH",
            currency_type=CurrencyType.CRYPTO,
        )

        # Act
        redis_database_adapter.add_currency(currency)

        # Allow MPSC thread to insert
        await eventually(lambda: redis_database_adapter.load_currency(currency.code))

        # Assert
        assert redis_database_adapter.load_currency(currency.code) == currency

    @pytest.mark.asyncio
    async def test_add_account(self, redis_database_adapter):
        # Arrange
        account = TestExecStubs.cash_account()

        # Act
        redis_database_adapter.add_account(account)

        # Allow MPSC thread to insert
        await eventually(lambda: redis_database_adapter.load_account(account.id))

        # Assert
        assert redis_database_adapter.load_account(account.id) == account

    @pytest.mark.asyncio
    async def test_update_account(self, redis_database_adapter):
        # Arrange
        account = TestExecStubs.cash_account()
        redis_database_adapter.add_account(account)

        # Allow MPSC thread to insert
        await eventually(lambda: redis_database_adapter.load_account(account.id))

        # Act
        account_state = TestEventStubs.cash_account_state()
        redis_database_adapter.update_account(account_state)

        # Allow MPSC thread to update
        await eventually(lambda: redis_database_adapter.load_account(account.id).last_event == account_state)

        # Assert
        assert redis_database_adapter.load_account(account.id).last_event == account_state

    @pytest.mark.asyncio
    async def test_load_currency_when_no_currencies_in_database_returns_none(self, redis_database_adapter):
        # Arrange, Act
        result = redis_database_adapter.load_currency("AUD")

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_load_currency_when_currency_in_database_returns_expected(self, redis_database_adapter):
        # Arrange
        currency = Currency(
            code="1INCH",
            precision=8,
            iso4217=0,
            name="1INCH",
            currency_type=CurrencyType.CRYPTO,
        )

        redis_database_adapter.add_currency(currency)

        # Allow MPSC thread to insert
        await eventually(lambda: redis_database_adapter.load_currency(currency.code))

        # Act
        result = redis_database_adapter.load_currency("1INCH")

        # Assert
        assert result == currency

    @pytest.mark.asyncio
    async def test_load_currencies_when_currencies_in_database_returns_expected(self, redis_database_adapter):
        # Arrange
        currency = Currency(
            code="1INCH",
            precision=8,
            iso4217=0,
            name="1INCH",
            currency_type=CurrencyType.CRYPTO,
        )

        redis_database_adapter.add_currency(currency)

        # Allow MPSC thread to insert
        await eventually(lambda: redis_database_adapter.load_currency(currency.code))

        # Act
        result = redis_database_adapter.load_currencies()

        # Assert
        assert result == {"1INCH": currency}

    @pytest.mark.asyncio
    async def test_load_account_when_no_account_in_database_returns_none(self, redis_database_adapter):
        # Arrange, Act
        result = redis_database_adapter.load_account(TestExecStubs.cash_account().id)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_load_account_when_account_in_database_returns_account(self, redis_database_adapter):
        # Arrange
        account = TestExecStubs.cash_account()
        redis_database_adapter.add_account(account)

        # Allow MPSC thread to insert
        await eventually(lambda: redis_database_adapter.load_account(account.id))

        # Act
        result = redis_database_adapter.load_account(account.id)

        # Assert
        assert result == account

    @pytest.mark.asyncio
    async def test_load_accounts_when_no_accounts_returns_empty_dict(self, redis_database_adapter):
        # Arrange, Act
        result = redis_database_adapter.load_accounts()

        # Assert
        assert result == {}

    @pytest.mark.asyncio
    async def test_load_accounts_cache_when_one_account_in_database(self, redis_database_adapter):
        # Arrange
        account = TestExecStubs.cash_account()
        redis_database_adapter.add_account(account)

        # Allow MPSC thread to insert
        await eventually(lambda: redis_database_adapter.load_account(account.id))

        # Act
        result = redis_database_adapter.load_accounts()

        # Assert
        assert result == {account.id: account}
