
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
from nautilus_trader.test_kit.stubs.data import TestDataStubs


_TEST_TIMEOUT = 5.0


@pytest.mark.xdist_group(name="postgres_integration")
class TestPostgresGeneralOperations:
    """Test general PostgreSQL cache operations."""

    @pytest.mark.asyncio
    async def test_load_general_objects_when_nothing_in_cache_returns_empty_dict(self, postgres_database_adapter):
        # Arrange, Act
        result = postgres_database_adapter.load()

        # Assert
        assert result == {}

    @pytest.mark.asyncio
    async def test_add_general_object_adds_to_cache(self, postgres_database_adapter):
        # Arrange
        bar = TestDataStubs.bar_5decimal()
        key = str(bar.bar_type) + "-" + str(bar.ts_event)

        # Act
        postgres_database_adapter.add(key, str(bar).encode())

        # Allow time for insertion
        await eventually(lambda: postgres_database_adapter.load(), timeout=_TEST_TIMEOUT)

        # Assert
        assert postgres_database_adapter.load() == {key: str(bar).encode()}

    @pytest.mark.asyncio
    async def test_add_currency(self, postgres_database_adapter):
        # Arrange
        currency = Currency(
            code="1INCH",
            precision=8,
            iso4217=0,
            name="1INCH",
            currency_type=CurrencyType.CRYPTO,
        )

        # Act
        postgres_database_adapter.add_currency(currency)

        # Allow time for insertion
        await eventually(lambda: postgres_database_adapter.load_currency(currency.code), timeout=_TEST_TIMEOUT)

        # Assert
        assert postgres_database_adapter.load_currency(currency.code) == currency
