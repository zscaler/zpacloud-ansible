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


class TestZPAServerGroupInfoModule(ModuleTestCase):
    """Unit tests for zpa_server_group_info module."""

    SAMPLE_GROUP = {
        "id": "216199618143442001",
        "name": "Example_Server_Group",
        "description": "Example Server Group",
        "enabled": True,
        "config_space": "DEFAULT",
        "dynamic_discovery": True,
        "ip_anchored": False,
        "microtenant_name": "Default",
        "app_connector_groups": [
            {
                "id": "216199618143441990",
                "name": "test_app_connector_group",
            }
        ],
    }

    SAMPLE_GROUP_2 = {
        "id": "216199618143442002",
        "name": "Example_Server_Group_2",
        "description": "Example Server Group 2",
        "enabled": True,
        "config_space": "DEFAULT",
        "dynamic_discovery": False,
        "ip_anchored": True,
        "microtenant_name": "Default",
        "app_connector_groups": [],
    }

    @pytest.fixture
    def mock_client(self, mocker):
        """Create a mock ZPA client that preserves argument_spec"""
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_server_group_info.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_get_group_by_id(self, mock_client):
        """Test fetching a Server Group by ID."""
        mock_group = MockBox(self.SAMPLE_GROUP)
        mock_client.server_groups.get_group.return_value = (
            mock_group,
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            id="216199618143442001",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_server_group_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_server_group_info.main()

        mock_client.server_groups.get_group.assert_called_once()
        assert result.value.result["changed"] is False
        assert len(result.value.result["groups"]) == 1
        assert result.value.result["groups"][0]["name"] == "Example_Server_Group"

    def test_get_group_by_name(self, mock_client, mocker):
        """Test fetching a Server Group by name."""
        mock_groups = [MockBox(self.SAMPLE_GROUP), MockBox(self.SAMPLE_GROUP_2)]

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_server_group_info.collect_all_items",
            return_value=(mock_groups, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Example_Server_Group",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_server_group_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_server_group_info.main()

        assert result.value.result["changed"] is False
        assert len(result.value.result["groups"]) == 1
        assert result.value.result["groups"][0]["name"] == "Example_Server_Group"

    def test_get_all_groups(self, mock_client, mocker):
        """Test fetching all Server Groups."""
        mock_groups = [MockBox(self.SAMPLE_GROUP), MockBox(self.SAMPLE_GROUP_2)]

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_server_group_info.collect_all_items",
            return_value=(mock_groups, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_server_group_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_server_group_info.main()

        assert result.value.result["changed"] is False
        assert len(result.value.result["groups"]) == 2

    def test_get_group_by_id_not_found(self, mock_client):
        """Test fetching a non-existent Server Group by ID."""
        mock_client.server_groups.get_group.return_value = (
            None,
            None,
            "Not Found",
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            id="999999999999999999",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_server_group_info,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_server_group_info.main()

        assert "Failed to retrieve Server Group ID" in result.value.result["msg"]

    def test_get_group_by_name_not_found(self, mock_client, mocker):
        """Test fetching a non-existent Server Group by name."""
        mock_groups = [MockBox(self.SAMPLE_GROUP)]

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_server_group_info.collect_all_items",
            return_value=(mock_groups, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="NonExistent_Group",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_server_group_info,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_server_group_info.main()

        assert "not found" in result.value.result["msg"]

    def test_api_error_on_list(self, mock_client, mocker):
        """Test handling API error when listing groups."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_server_group_info.collect_all_items",
            return_value=(None, "API Error"),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_server_group_info,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_server_group_info.main()

        assert "Error retrieving Server Groups" in result.value.result["msg"]

