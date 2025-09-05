
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

import sys
import time

import msgspec
import pytest

from nautilus_trader.cache.database import CacheDatabaseAdapter
from nautilus_trader.common.component import MessageBus
from nautilus_trader.common.component import TestClock
from nautilus_trader.config import CacheConfig
from nautilus_trader.config import DatabaseConfig
from nautilus_trader.core.uuid import UUID4
from nautilus_trader.data.engine import DataEngine
from nautilus_trader.execution.engine import ExecutionEngine
from nautilus_trader.portfolio.portfolio import Portfolio
from nautilus_trader.risk.engine import RiskEngine
from nautilus_trader.serialization.serializer import MsgSpecSerializer
from nautilus_trader.test_kit.providers import TestInstrumentProvider
from nautilus_trader.test_kit.stubs.component import TestComponentStubs
from nautilus_trader.test_kit.stubs.identifiers import TestIdStubs
from nautilus_trader.trading.strategy import Strategy


_AUDUSD_SIM = TestInstrumentProvider.default_fx_ccy("AUD/USD")

# Requirements:
# - A Redis service listening on the default port 6379

pytestmark = pytest.mark.skipif(
    sys.platform != "linux",
    reason="databases only supported on Linux",
)


@pytest.fixture
def redis_database_adapter():
    """Fixture providing a configured Redis database adapter."""
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

    data_engine = DataEngine(
        msgbus=msgbus,
        cache=cache,
        clock=clock,
    )

    exec_engine = ExecutionEngine(
        msgbus=msgbus,
        cache=cache,
        clock=clock,
    )

    risk_engine = RiskEngine(
        portfolio=portfolio,
        msgbus=msgbus,
        cache=cache,
        clock=clock,
    )

    strategy = Strategy()
    strategy.register(
        trader_id=trader_id,
        portfolio=portfolio,
        msgbus=msgbus,
        cache=cache,
        clock=clock,
    )

    database = CacheDatabaseAdapter(
        trader_id=trader_id,
        instance_id=UUID4(),
        serializer=MsgSpecSerializer(encoding=msgspec.msgpack, timestamps_as_str=True),
        config=CacheConfig(database=DatabaseConfig()),
    )

    # Store components for test access
    database._test_components = {
        'clock': clock,
        'trader_id': trader_id,
        'msgbus': msgbus,
        'cache': cache,
        'portfolio': portfolio,
        'data_engine': data_engine,
        'exec_engine': exec_engine,
        'risk_engine': risk_engine,
        'strategy': strategy,
    }

    yield database

    # Cleanup
    time.sleep(0.2)
    database.flush()
    time.sleep(0.5)
