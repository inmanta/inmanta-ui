"""
    Copyright 2019 Inmanta

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

from typing import List, cast

from inmanta.protocol import method
from inmanta.server import SLICE_SERVER, SLICE_TRANSPORT
from inmanta.server import config as opt
from inmanta.server import protocol
from inmanta.server.protocol import ServerSlice
from inmanta.server.server import Server
from inmanta.types import Apireturn

from .config import web_console_enabled, web_console_path


@method(path="/hello-world", operation="GET", client_types=["api"])
def hello_world():
    """
        Basic hello-world API endpoint.
    """


class UISlice(ServerSlice):
    def __init__(self) -> None:
        super().__init__("inmanta_ui.ui")

    async def prestart(self, server: protocol.Server) -> None:
        _server = cast(Server, server.get_slice(SLICE_SERVER))
        self.add_web_console_handler(_server)
        await super(UISlice, self).prestart(server)

    async def start(self) -> None:
        await super(UISlice, self).start()

    async def prestop(self) -> None:
        await super(UISlice, self).prestop()

    async def stop(self) -> None:
        await super(UISlice, self).stop()

    def get_dependencies(self) -> List[str]:
        return []

    def get_depended_by(self) -> List[str]:
        # Ensure we are started before the HTTP endpoint becomes available
        return [SLICE_TRANSPORT]

    @protocol.handle(hello_world)
    async def hello_world_handle(self) -> Apireturn:
        """
            Handle for the hello_world API endpoint.
        """
        return 200, {"data": "hello-world"}

    def add_web_console_handler(self, server: Server) -> None:
        if not web_console_enabled.get():
            return

        path = web_console_path.get()
        if path is None:
            return

        if opt.server_enable_auth.get():
            auth = f"""
        window.auth = {{
            'realm': '{opt.dash_realm.get()}',
            'url': '{opt.dash_auth_url.get()}',
            'clientId': '{opt.dash_client_id.get()}'
        }};"""  # Use the same client-id as the dashboard
        else:
            auth = ""
        server.add_static_content("/web-console/config.js", content=auth)
        server.add_static_handler("/web-console", path, start=True)
