# -*- coding: utf-8 -*-
#
# Copyright (c) 2023 Zscaler Inc, <devrel@zscaler.com>
#
#                             MIT License
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys
import os

# Add the collection root to path for imports
COLLECTION_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
)
if COLLECTION_ROOT not in sys.path:
    sys.path.insert(0, COLLECTION_ROOT)

import pytest
from unittest.mock import MagicMock, patch

from tests.unit.plugins.modules.common.utils import (
    set_module_args,
    AnsibleExitJson,
    AnsibleFailJson,
    ModuleTestCase,
    DEFAULT_PROVIDER,
)

# Import the real argument_spec function before mocking
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)

# Get the real argument_spec to use in tests
REAL_ARGUMENT_SPEC = ZPAClientHelper.zpa_argument_spec()


class MockBox:
    """Mock Box object to simulate SDK responses"""

    def __init__(self, data):
        self._data = data

    def as_dict(self):
        return self._data

    def __getattr__(self, name):
        return self._data.get(name)


class TestZPAApplicationServerInfoModule(ModuleTestCase):
    """Unit tests for zpa_application_server_info module."""

    # Sample data representing an Application Server from the API
    SAMPLE_SERVER = {
        "id": "216199618143442003",
        "name": "server1.acme.com",
        "description": "server1.acme.com",
        "address": "server1.acme.com",
        "enabled": True,
        "config_space": "DEFAULT",
        "creation_time": "1724114751",
        "modified_time": "1724114751",
        "modified_by": "216199618143191041",
    }

    SAMPLE_SERVER_2 = {
        "id": "216199618143442004",
        "name": "server2.acme.com",
        "description": "server2.acme.com",
        "address": "server2.acme.com",
        "enabled": True,
        "config_space": "DEFAULT",
        "creation_time": "1724114752",
        "modified_time": "1724114752",
        "modified_by": "216199618143191041",
    }

    @pytest.fixture
    def mock_client(self, mocker):
        """Create a mock ZPA client that preserves argument_spec"""
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_application_server_info.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_get_server_by_id(self, mock_client):
        """Test fetching an Application Server by ID."""
        mock_server = MockBox(self.SAMPLE_SERVER)
        mock_client.servers.get_server.return_value = (
            mock_server,
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            id="216199618143442003",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_application_server_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_application_server_info.main()

        mock_client.servers.get_server.assert_called_once()
        assert result.value.result["changed"] is False
        assert len(result.value.result["servers"]) == 1
        assert result.value.result["servers"][0]["id"] == "216199618143442003"
        assert result.value.result["servers"][0]["name"] == "server1.acme.com"

    def test_get_server_by_name(self, mock_client, mocker):
        """Test fetching an Application Server by name."""
        mock_servers = [MockBox(self.SAMPLE_SERVER), MockBox(self.SAMPLE_SERVER_2)]

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_application_server_info.collect_all_items",
            return_value=(mock_servers, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="server1.acme.com",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_application_server_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_application_server_info.main()

        assert result.value.result["changed"] is False
        assert len(result.value.result["servers"]) == 1
        assert result.value.result["servers"][0]["name"] == "server1.acme.com"

    def test_get_all_servers(self, mock_client, mocker):
        """Test fetching all Application Servers."""
        mock_servers = [MockBox(self.SAMPLE_SERVER), MockBox(self.SAMPLE_SERVER_2)]

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_application_server_info.collect_all_items",
            return_value=(mock_servers, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_application_server_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_application_server_info.main()

        assert result.value.result["changed"] is False
        assert len(result.value.result["servers"]) == 2

    def test_get_server_by_id_not_found(self, mock_client):
        """Test fetching a non-existent Application Server by ID."""
        mock_client.servers.get_server.return_value = (
            None,
            None,
            "Not Found",
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            id="999999999999999999",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_application_server_info,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_application_server_info.main()

        assert "Failed to retrieve Application Server ID" in result.value.result["msg"]

    def test_get_server_by_name_not_found(self, mock_client, mocker):
        """Test fetching a non-existent Application Server by name."""
        mock_servers = [MockBox(self.SAMPLE_SERVER)]

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_application_server_info.collect_all_items",
            return_value=(mock_servers, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="nonexistent.server.com",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_application_server_info,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_application_server_info.main()

        assert "not found" in result.value.result["msg"]

    def test_get_server_with_microtenant_id(self, mock_client):
        """Test fetching an Application Server with microtenant_id."""
        mock_server = MockBox(self.SAMPLE_SERVER)
        mock_client.servers.get_server.return_value = (
            mock_server,
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            id="216199618143442003",
            microtenant_id="123456789",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_application_server_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_application_server_info.main()

        mock_client.servers.get_server.assert_called_once()
        call_args = mock_client.servers.get_server.call_args
        assert "microtenant_id" in call_args[0][1]

    def test_api_error_on_list(self, mock_client, mocker):
        """Test handling API error when listing servers."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_application_server_info.collect_all_items",
            return_value=(None, "API Error"),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_application_server_info,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_application_server_info.main()

        assert "Error retrieving Application Servers" in result.value.result["msg"]
