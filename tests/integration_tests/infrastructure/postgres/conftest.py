
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

import os
import sys

import pytest

from nautilus_trader.cache.adapter import CachePostgresAdapter
from nautilus_trader.common.component import MessageBus
from nautilus_trader.common.component import TestClock
from nautilus_trader.portfolio.portfolio import Portfolio
from nautilus_trader.test_kit.providers import TestInstrumentProvider
from nautilus_trader.test_kit.stubs.component import TestComponentStubs
from nautilus_trader.test_kit.stubs.identifiers import TestIdStubs
from nautilus_trader.trading.strategy import Strategy


_TEST_TIMEOUT = 5.0
_AUDUSD_SIM = TestInstrumentProvider.default_fx_ccy("AUD/USD")

# Requirements:
# - A Postgres service listening on the default port 5432

pytestmark = pytest.mark.skipif(
    sys.platform != "linux",
    reason="databases only supported on Linux",
)


@pytest.fixture
def postgres_database_adapter():
    """Fixture providing a configured PostgreSQL database adapter."""
    # Set environment variables
    os.environ["POSTGRES_HOST"] = "localhost"
    os.environ["POSTGRES_PORT"] = "5432"
    os.environ["POSTGRES_USERNAME"] = "nautilus"
    os.environ["POSTGRES_PASSWORD"] = "pass"
    os.environ["POSTGRES_DATABASE"] = "nautilus"
    
    database = CachePostgresAdapter()
    database.flush()  # Reset database
    
    clock = TestClock()
    trader_id = TestIdStubs.trader_id()

    msgbus = MessageBus(
        trader_id=trader_id,
        clock=clock,
    )

    cache = TestComponentStubs.cache()

    portfolio = Portfolio(
        msgbus=msgbus,
        cache=cache,
        clock=clock,
    )

    # Initialize strategy
    strategy = Strategy()
    strategy.register(
        trader_id=trader_id,
        portfolio=portfolio,
        msgbus=msgbus,
        cache=cache,
        clock=clock,
    )

    # Store components for test access
    database._test_components = {
        'clock': clock,
        'trader_id': trader_id,
        'msgbus': msgbus,
        'cache': cache,
        'portfolio': portfolio,
        'strategy': strategy,
    }

    yield database

    # Cleanup
    database.flush()
    database.dispose()
