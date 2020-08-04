"""
    :copyright: 2019 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""

from inmanta.server.extensions import ApplicationContext
from inmanta_ui.ui import UISlice


def setup(application: ApplicationContext) -> None:
    application.register_slice(UISlice())
