"""
    :copyright: 2019 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
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
    config.Config.set("web-console", "path", str(web_console_path))


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
    assets_dir = os.path.join(tmpdir, "assets")
    os.mkdir(assets_dir)
    with open(os.path.join(assets_dir, "asset.txt"), "w") as asset_file:
        asset_file.write("Additional config file")

    return tmpdir
