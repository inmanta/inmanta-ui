"""
    :copyright: 2019 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
import pytest
from tornado.httpclient import AsyncHTTPClient, HTTPClientError

from inmanta.server import config


@pytest.mark.asyncio
async def test_web_console_handler(server, inmanta_ui_config):
    base_url = f"http://127.0.0.1:{config.get_bind_port()}/console"
    client = AsyncHTTPClient()
    response = await client.fetch(base_url)
    assert response.code == 200

    response = await client.fetch(base_url + "/assets/asset.txt")
    assert response.code == 200

    with pytest.raises(HTTPClientError) as exc:
        await client.fetch(base_url + "/assets/not_existing_asset.json")
    assert 404 == exc.value.code

    response = await client.fetch(base_url + "/lsm/catalog")
    assert response.code == 200
    assert "Should be served by default" in response.body.decode("UTF-8")

    # The app should handle the missing view
    response = await client.fetch(base_url + "/lsm/abc")
    assert response.code == 200
    assert "Should be served by default" in response.body.decode("UTF-8")
