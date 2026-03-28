
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
from nautilus_trader.test_kit.providers import TestInstrumentProvider


_TEST_TIMEOUT = 5.0
_AUDUSD_SIM = TestInstrumentProvider.default_fx_ccy("AUD/USD")


@pytest.mark.xdist_group(name="postgres_integration")
class TestPostgresInstruments:
    """Test PostgreSQL instrument operations."""

    @pytest.mark.asyncio
    async def test_add_instrument_betting(self, postgres_database_adapter):
        # Arrange
        instrument = TestInstrumentProvider.betting_instrument()

        # Act
        postgres_database_adapter.add_instrument(instrument)

        # Allow time for insertion
        await eventually(lambda: postgres_database_adapter.load_instrument(instrument.id), timeout=_TEST_TIMEOUT)

        # Assert
        assert postgres_database_adapter.load_instrument(instrument.id) == instrument

    @pytest.mark.asyncio
    async def test_add_instrument_binary_option(self, postgres_database_adapter):
        # Arrange
        instrument = TestInstrumentProvider.binary_option_instrument()

        # Act
        postgres_database_adapter.add_instrument(instrument)

        # Allow time for insertion
        await eventually(lambda: postgres_database_adapter.load_instrument(instrument.id), timeout=_TEST_TIMEOUT)

        # Assert
        assert postgres_database_adapter.load_instrument(instrument.id) == instrument

    @pytest.mark.asyncio
    async def test_add_instrument_crypto_future(self, postgres_database_adapter):
        # Arrange
        instrument = TestInstrumentProvider.btcusdt_future_binance()

        # Act
        postgres_database_adapter.add_instrument(instrument)

        # Allow time for insertion
        await eventually(lambda: postgres_database_adapter.load_instrument(instrument.id), timeout=_TEST_TIMEOUT)

        # Assert
        assert postgres_database_adapter.load_instrument(instrument.id) == instrument

    @pytest.mark.asyncio
    async def test_add_instrument_crypto_perpetual(self, postgres_database_adapter):
        # Arrange
        instrument = TestInstrumentProvider.btcusdt_perp_binance()

        # Act
        postgres_database_adapter.add_instrument(instrument)

        # Allow time for insertion
        await eventually(lambda: postgres_database_adapter.load_instrument(instrument.id), timeout=_TEST_TIMEOUT)

        # Assert
        assert postgres_database_adapter.load_instrument(instrument.id) == instrument

    @pytest.mark.asyncio
    async def test_add_instrument_currency_pair(self, postgres_database_adapter):
        # Arrange
        instrument = _AUDUSD_SIM

        # Act
        postgres_database_adapter.add_instrument(instrument)

        # Allow time for insertion
        await eventually(lambda: postgres_database_adapter.load_instrument(instrument.id), timeout=_TEST_TIMEOUT)

        # Assert
        assert postgres_database_adapter.load_instrument(instrument.id) == instrument

    @pytest.mark.asyncio
    async def test_add_instrument_equity(self, postgres_database_adapter):
        # Arrange
        instrument = TestInstrumentProvider.equity()

        # Act
        postgres_database_adapter.add_instrument(instrument)

        # Allow time for insertion
        await eventually(lambda: postgres_database_adapter.load_instrument(instrument.id), timeout=_TEST_TIMEOUT)

        # Assert
        assert postgres_database_adapter.load_instrument(instrument.id) == instrument

    @pytest.mark.asyncio
    async def test_add_instrument_futures_contract(self, postgres_database_adapter):
        # Arrange
        instrument = TestInstrumentProvider.es_future()

        # Act
        postgres_database_adapter.add_instrument(instrument)

        # Allow time for insertion
        await eventually(lambda: postgres_database_adapter.load_instrument(instrument.id), timeout=_TEST_TIMEOUT)

        # Assert
        assert postgres_database_adapter.load_instrument(instrument.id) == instrument

    @pytest.mark.asyncio
    async def test_add_instrument_option_contract(self, postgres_database_adapter):
        # Arrange
        instrument = TestInstrumentProvider.aapl_option()

        # Act
        postgres_database_adapter.add_instrument(instrument)

        # Allow time for insertion
        await eventually(lambda: postgres_database_adapter.load_instrument(instrument.id), timeout=_TEST_TIMEOUT)

        # Assert
        assert postgres_database_adapter.load_instrument(instrument.id) == instrument
