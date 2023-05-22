"""
    Copyright 2022 Inmanta

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

    Contact: code@inmanta.com
"""

import asyncio
import concurrent
import logging
import os

import pytest

from inmanta import config
from inmanta.server.bootloader import InmantaBootloader

logger = logging.getLogger(__name__)


@pytest.fixture
def inmanta_ui_config(server_config, postgres_db, database_name, web_console_path):
    config.Config.set("server", "enabled_extensions", "ui")
    config.Config.set("web-ui", "console_path", str(web_console_path))
    config.Config.set("web-ui", "features", "A, B, C")


@pytest.fixture
async def server(inmanta_ui_config, server_config):
    """
    Override standard inmanta server to allow more config to be injected
    """
    ibl = InmantaBootloader()
    await ibl.start()

    yield ibl.restserver

    try:
        await asyncio.wait_for(ibl.stop(), 15)
    except concurrent.futures.TimeoutError:
        logger.exception("Timeout during stop of the server in teardown")

    logger.info("Server clean up done")


@pytest.fixture
def web_console_path(tmpdir):
    with open(os.path.join(tmpdir, "index.html"), "w") as index:
        index.write(
            """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Should be served by default</title>
</head>
<body>

</body>
</html>"""
        )
    with open(os.path.join(tmpdir, "asset.js"), "w") as asset_file:
        asset_file.write("// Additional javascript file")

    return tmpdir
