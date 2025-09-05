
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


_AUDUSD_SIM = TestInstrumentProvider.default_fx_ccy("AUD/USD")


@pytest.mark.xdist_group(name="redis_integration")
class TestRedisInstruments:
    """Test Redis instrument operations."""

    @pytest.mark.asyncio
    async def test_add_instrument(self, redis_database_adapter):
        # Arrange, Act
        redis_database_adapter.add_instrument(_AUDUSD_SIM)

        # Allow MPSC thread to insert
        await eventually(lambda: redis_database_adapter.load_instrument(_AUDUSD_SIM.id))

        # Assert
        assert redis_database_adapter.load_instrument(_AUDUSD_SIM.id) == _AUDUSD_SIM

    @pytest.mark.asyncio
    async def test_load_instrument_when_no_instrument_in_database_returns_none(self, redis_database_adapter):
        # Arrange, Act
        result = redis_database_adapter.load_instrument(_AUDUSD_SIM.id)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_load_instrument_when_instrument_in_database_returns_expected(self, redis_database_adapter):
        # Arrange
        redis_database_adapter.add_instrument(_AUDUSD_SIM)

        # Allow MPSC thread to insert
        await eventually(lambda: redis_database_adapter.load_instrument(_AUDUSD_SIM.id))

        # Act
        result = redis_database_adapter.load_instrument(_AUDUSD_SIM.id)

        # Assert
        assert result == _AUDUSD_SIM

    @pytest.mark.asyncio
    async def test_load_instruments_when_instrument_in_database_returns_expected(self, redis_database_adapter):
        # Arrange
        redis_database_adapter.add_instrument(_AUDUSD_SIM)

        # Allow MPSC thread to insert
        await eventually(lambda: redis_database_adapter.load_instrument(_AUDUSD_SIM.id))

        # Act
        result = redis_database_adapter.load_instruments()

        # Assert
        assert result == {_AUDUSD_SIM.id: _AUDUSD_SIM}

    @pytest.mark.asyncio
    async def test_load_synthetic_when_no_synethic_instrument_in_database_returns_none(self, redis_database_adapter):
        # Arrange, Act
        result = redis_database_adapter.load_synthetic(_AUDUSD_SIM.id)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_load_synthetic_when_synthetic_instrument_in_database_returns_expected(self, redis_database_adapter):
        # Arrange
        synthetic = TestInstrumentProvider.synthetic_instrument()
        redis_database_adapter.add_synthetic(synthetic)

        # Allow MPSC thread to insert
        await eventually(lambda: redis_database_adapter.load_synthetic(synthetic.id))

        # Act
        result = redis_database_adapter.load_synthetic(synthetic.id)

        # Assert
        assert result == synthetic
