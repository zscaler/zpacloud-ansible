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


class TestZPAApplicationServerModule(ModuleTestCase):
    """Unit tests for zpa_application_server module."""

    # Sample data representing an Application Server from the API
    SAMPLE_SERVER = {
        "id": "216199618143442003",
        "name": "server1.acme.com",
        "description": "server1.acme.com",
        "address": "server1.acme.com",
        "enabled": True,
        "app_server_group_ids": [],
    }

    @pytest.fixture
    def mock_client(self, mocker):
        """Create a mock ZPA client that preserves argument_spec"""
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_application_server.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_create_application_server(self, mock_client):
        """Test creating a new Application Server."""
        mock_client.servers.list_servers.return_value = ([], None, None)

        mock_created = MockBox(self.SAMPLE_SERVER)
        mock_client.servers.add_server.return_value = (
            mock_created,
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="server1.acme.com",
            description="server1.acme.com",
            address="server1.acme.com",
            enabled=True,
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_application_server,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_application_server.main()

        mock_client.servers.add_server.assert_called_once()
        assert result.value.result["changed"] is True
        assert result.value.result["data"]["name"] == "server1.acme.com"

    def test_update_application_server(self, mock_client):
        """Test updating an existing Application Server."""
        existing_server = dict(self.SAMPLE_SERVER)
        existing_server["description"] = "Old Description"
        mock_existing = MockBox(existing_server)

        mock_client.servers.list_servers.return_value = ([mock_existing], None, None)

        updated_server = dict(self.SAMPLE_SERVER)
        updated_server["description"] = "Updated Description"
        mock_updated = MockBox(updated_server)
        mock_client.servers.update_server.return_value = (
            mock_updated,
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="server1.acme.com",
            description="Updated Description",
            address="server1.acme.com",
            enabled=True,
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_application_server,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_application_server.main()

        mock_client.servers.update_server.assert_called_once()
        assert result.value.result["changed"] is True

    def test_delete_application_server(self, mock_client):
        """Test deleting an Application Server."""
        mock_existing = MockBox(self.SAMPLE_SERVER)

        mock_client.servers.list_servers.return_value = ([mock_existing], None, None)
        mock_client.servers.delete_server.return_value = (
            None,
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="server1.acme.com",
            state="absent",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_application_server,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_application_server.main()

        mock_client.servers.delete_server.assert_called_once()
        assert result.value.result["changed"] is True

    def test_no_change_when_identical(self, mock_client):
        """Test no change when server already matches desired state."""
        mock_existing = MockBox(self.SAMPLE_SERVER)

        mock_client.servers.list_servers.return_value = ([mock_existing], None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="server1.acme.com",
            description="server1.acme.com",
            address="server1.acme.com",
            enabled=True,
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_application_server,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_application_server.main()

        mock_client.servers.add_server.assert_not_called()
        mock_client.servers.update_server.assert_not_called()
        assert result.value.result["changed"] is False

    def test_delete_nonexistent_server(self, mock_client):
        """Test deleting a non-existent server (no change)."""
        mock_client.servers.list_servers.return_value = ([], None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="nonexistent.server.com",
            state="absent",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_application_server,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_application_server.main()

        mock_client.servers.delete_server.assert_not_called()
        assert result.value.result["changed"] is False

    def test_check_mode_create(self, mock_client):
        """Test check mode for create operation."""
        mock_client.servers.list_servers.return_value = ([], None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="new.server.com",
            description="New Server",
            address="new.server.com",
            enabled=True,
            state="present",
            _ansible_check_mode=True,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_application_server,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_application_server.main()

        mock_client.servers.add_server.assert_not_called()
        assert result.value.result["changed"] is True

    def test_check_mode_delete(self, mock_client):
        """Test check mode for delete operation."""
        mock_existing = MockBox(self.SAMPLE_SERVER)

        mock_client.servers.list_servers.return_value = ([mock_existing], None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="server1.acme.com",
            state="absent",
            _ansible_check_mode=True,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_application_server,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_application_server.main()

        mock_client.servers.delete_server.assert_not_called()
        assert result.value.result["changed"] is True

    def test_create_with_app_server_group_ids(self, mock_client):
        """Test creating an Application Server with app_server_group_ids."""
        mock_client.servers.list_servers.return_value = ([], None, None)

        server_with_groups = dict(self.SAMPLE_SERVER)
        server_with_groups["app_server_group_ids"] = ["123456", "789012"]
        mock_created = MockBox(server_with_groups)
        mock_client.servers.add_server.return_value = (
            mock_created,
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="server1.acme.com",
            description="server1.acme.com",
            address="server1.acme.com",
            enabled=True,
            app_server_group_ids=["123456", "789012"],
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_application_server,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_application_server.main()

        mock_client.servers.add_server.assert_called_once()
        call_kwargs = mock_client.servers.add_server.call_args[1]
        assert call_kwargs.get("app_server_group_ids") == ["123456", "789012"]

    def test_api_error_on_create(self, mock_client):
        """Test handling API error on create."""
        mock_client.servers.list_servers.return_value = ([], None, None)

        mock_client.servers.add_server.return_value = (
            None,
            None,
            "API Error: Creation failed",
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="server1.acme.com",
            description="server1.acme.com",
            address="server1.acme.com",
            enabled=True,
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_application_server,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_application_server.main()

        assert "Error creating server" in result.value.result["msg"]

    def test_api_error_on_update(self, mock_client):
        """Test handling API error on update."""
        existing_server = dict(self.SAMPLE_SERVER)
        existing_server["description"] = "Old Description"
        mock_existing = MockBox(existing_server)

        mock_client.servers.list_servers.return_value = ([mock_existing], None, None)

        mock_client.servers.update_server.return_value = (
            None,
            None,
            "API Error: Update failed",
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="server1.acme.com",
            description="Updated Description",
            address="server1.acme.com",
            enabled=True,
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_application_server,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_application_server.main()

        assert "Error updating server" in result.value.result["msg"]

    def test_api_error_on_delete(self, mock_client):
        """Test handling API error on delete."""
        mock_existing = MockBox(self.SAMPLE_SERVER)

        mock_client.servers.list_servers.return_value = ([mock_existing], None, None)

        mock_client.servers.delete_server.return_value = (
            None,
            None,
            "API Error: Deletion failed",
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="server1.acme.com",
            state="absent",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_application_server,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_application_server.main()

        assert "Error deleting server" in result.value.result["msg"]
