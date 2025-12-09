# -*- coding: utf-8 -*-
#
# Copyright (c) 2023 Zscaler Inc, <devrel@zscaler.com>
# MIT License

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

from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)

REAL_ARGUMENT_SPEC = ZPAClientHelper.zpa_argument_spec()


class MockBox:
    """Mock Box object to simulate SDK responses"""

    def __init__(self, data):
        self._data = data

    def as_dict(self):
        return self._data

    def __getattr__(self, name):
        return self._data.get(name)


class TestZPAServerGroupModule(ModuleTestCase):
    """Unit tests for zpa_server_group module."""

    SAMPLE_GROUP = {
        "id": "216199618143442001",
        "name": "Example_Server_Group",
        "description": "Example Server Group",
        "enabled": True,
        "dynamic_discovery": True,
        "app_connector_groups": [
            {
                "id": "216199618143441990",
                "name": "test_app_connector_group",
            }
        ],
    }

    @pytest.fixture
    def mock_client(self, mocker):
        """Create a mock ZPA client that preserves argument_spec"""
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_server_group.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_create_server_group(self, mock_client, mocker):
        """Test creating a new Server Group."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_server_group.collect_all_items",
            return_value=([], None),
        )

        mock_created = MockBox(self.SAMPLE_GROUP)
        mock_client.server_groups.add_group.return_value = (
            mock_created,
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Example_Server_Group",
            description="Example Server Group",
            enabled=True,
            dynamic_discovery=True,
            app_connector_group_ids=["216199618143441990"],
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_server_group,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_server_group.main()

        mock_client.server_groups.add_group.assert_called_once()
        assert result.value.result["changed"] is True
        assert result.value.result["data"]["name"] == "Example_Server_Group"

    def test_update_server_group(self, mock_client, mocker):
        """Test updating an existing Server Group."""
        existing_group = dict(self.SAMPLE_GROUP)
        existing_group["description"] = "Old Description"
        mock_existing = MockBox(existing_group)

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_server_group.collect_all_items",
            return_value=([mock_existing], None),
        )

        updated_group = dict(self.SAMPLE_GROUP)
        updated_group["description"] = "Updated Description"
        mock_updated = MockBox(updated_group)
        mock_client.server_groups.update_group.return_value = (
            mock_updated,
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Example_Server_Group",
            description="Updated Description",
            enabled=True,
            dynamic_discovery=True,
            app_connector_group_ids=["216199618143441990"],
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_server_group,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_server_group.main()

        mock_client.server_groups.update_group.assert_called_once()
        assert result.value.result["changed"] is True

    def test_delete_server_group(self, mock_client, mocker):
        """Test deleting a Server Group."""
        mock_existing = MockBox(self.SAMPLE_GROUP)

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_server_group.collect_all_items",
            return_value=([mock_existing], None),
        )

        mock_client.server_groups.delete_group.return_value = (
            None,
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Example_Server_Group",
            state="absent",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_server_group,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_server_group.main()

        mock_client.server_groups.delete_group.assert_called_once()
        assert result.value.result["changed"] is True

    def test_no_change_when_identical(self, mock_client, mocker):
        """Test no change when group already matches desired state."""
        mock_existing = MockBox(self.SAMPLE_GROUP)

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_server_group.collect_all_items",
            return_value=([mock_existing], None),
        )

        # Mock update in case drift is detected
        mock_client.server_groups.update_group.return_value = (
            mock_existing,
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Example_Server_Group",
            description="Example Server Group",
            enabled=True,
            dynamic_discovery=True,
            app_connector_group_ids=["216199618143441990"],
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_server_group,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_server_group.main()

        mock_client.server_groups.add_group.assert_not_called()

    def test_delete_nonexistent_group(self, mock_client, mocker):
        """Test deleting a non-existent group (no change)."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_server_group.collect_all_items",
            return_value=([], None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="NonExistent_Group",
            state="absent",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_server_group,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_server_group.main()

        mock_client.server_groups.delete_group.assert_not_called()

    def test_check_mode_create(self, mock_client, mocker):
        """Test check mode for create operation."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_server_group.collect_all_items",
            return_value=([], None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="New_Group",
            description="New Group",
            enabled=True,
            dynamic_discovery=True,
            state="present",
            _ansible_check_mode=True,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_server_group,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_server_group.main()

        mock_client.server_groups.add_group.assert_not_called()
        assert result.value.result["changed"] is True

    def test_create_with_dynamic_discovery_off(self, mock_client, mocker):
        """Test creating a Server Group with dynamic discovery disabled."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_server_group.collect_all_items",
            return_value=([], None),
        )

        group_static = dict(self.SAMPLE_GROUP)
        group_static["dynamic_discovery"] = False
        group_static["server_ids"] = ["123456789"]
        mock_created = MockBox(group_static)
        mock_client.server_groups.add_group.return_value = (
            mock_created,
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Example_Server_Group",
            description="Example Server Group",
            enabled=True,
            dynamic_discovery=False,
            app_connector_group_ids=["216199618143441990"],
            server_ids=["123456789"],
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_server_group,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_server_group.main()

        mock_client.server_groups.add_group.assert_called_once()
        call_kwargs = mock_client.server_groups.add_group.call_args[1]
        assert call_kwargs.get("dynamic_discovery") is False

    def test_api_error_on_create(self, mock_client, mocker):
        """Test handling API error on create."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_server_group.collect_all_items",
            return_value=([], None),
        )

        mock_client.server_groups.add_group.return_value = (
            None,
            None,
            "API Error: Creation failed",
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Test_Group",
            description="Test",
            enabled=True,
            dynamic_discovery=True,
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_server_group,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_server_group.main()

        assert "Error creating group" in result.value.result["msg"]

    def test_api_error_on_delete(self, mock_client, mocker):
        """Test handling API error on delete."""
        mock_existing = MockBox(self.SAMPLE_GROUP)

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_server_group.collect_all_items",
            return_value=([mock_existing], None),
        )

        mock_client.server_groups.delete_group.return_value = (
            None,
            None,
            "API Error: Deletion failed",
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Example_Server_Group",
            state="absent",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_server_group,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_server_group.main()

        assert "Error deleting group" in result.value.result["msg"]

