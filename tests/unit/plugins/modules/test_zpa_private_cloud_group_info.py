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


class TestZPAPrivateCloudGroupInfoModule(ModuleTestCase):
    """Unit tests for zpa_private_cloud_group_info module."""

    SAMPLE_GROUP = {
        "id": "216199618143442000",
        "name": "US East",
        "description": "Private Cloud Group for US East region",
        "enabled": True,
        "city_country": "San Jose, US",
        "country_code": "US",
        "latitude": "37.3382082",
        "longitude": "-121.8863286",
        "location": "San Jose, CA, USA",
        "is_public": "true",
        "override_version_profile": False,
        "upgrade_day": "SUNDAY",
        "upgrade_time_in_secs": "66600",
        "microtenant_name": "Default",
    }

    SAMPLE_GROUP_2 = {
        "id": "216199618143442001",
        "name": "US West",
        "description": "Private Cloud Group for US West region",
        "enabled": True,
        "city_country": "Los Angeles, US",
        "country_code": "US",
        "latitude": "34.0522",
        "longitude": "-118.2437",
        "location": "Los Angeles, CA, USA",
        "is_public": "false",
        "override_version_profile": False,
        "upgrade_day": "MONDAY",
        "upgrade_time_in_secs": "66600",
        "microtenant_name": "Default",
    }

    @pytest.fixture
    def mock_client(self, mocker):
        """Create a mock ZPA client that preserves argument_spec"""
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_private_cloud_group_info.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_get_group_by_id(self, mock_client):
        """Test fetching a Private Cloud Group by ID."""
        mock_group = MockBox(self.SAMPLE_GROUP)
        mock_client.private_cloud_group.get_cloud_group.return_value = (
            mock_group,
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            id="216199618143442000",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_private_cloud_group_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_private_cloud_group_info.main()

        mock_client.private_cloud_group.get_cloud_group.assert_called_once()
        assert result.value.result["changed"] is False
        assert len(result.value.result["groups"]) == 1
        assert result.value.result["groups"][0]["name"] == "US East"

    def test_get_group_by_name(self, mock_client, mocker):
        """Test fetching a Private Cloud Group by name."""
        mock_groups = [MockBox(self.SAMPLE_GROUP), MockBox(self.SAMPLE_GROUP_2)]

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_private_cloud_group_info.collect_all_items",
            return_value=(mock_groups, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="US East",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_private_cloud_group_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_private_cloud_group_info.main()

        assert result.value.result["changed"] is False
        assert len(result.value.result["groups"]) == 1
        assert result.value.result["groups"][0]["name"] == "US East"

    def test_get_all_groups(self, mock_client, mocker):
        """Test fetching all Private Cloud Groups."""
        mock_groups = [MockBox(self.SAMPLE_GROUP), MockBox(self.SAMPLE_GROUP_2)]

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_private_cloud_group_info.collect_all_items",
            return_value=(mock_groups, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_private_cloud_group_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_private_cloud_group_info.main()

        assert result.value.result["changed"] is False
        assert len(result.value.result["groups"]) == 2

    def test_get_group_by_id_not_found(self, mock_client):
        """Test fetching a non-existent Private Cloud Group by ID."""
        mock_client.private_cloud_group.get_cloud_group.return_value = (
            None,
            None,
            "Not Found",
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            id="999999999999999999",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_private_cloud_group_info,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_private_cloud_group_info.main()

        assert "Failed to retrieve Private Cloud Group ID" in result.value.result["msg"]

    def test_get_group_by_name_not_found(self, mock_client, mocker):
        """Test fetching a non-existent Private Cloud Group by name."""
        mock_groups = [MockBox(self.SAMPLE_GROUP)]

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_private_cloud_group_info.collect_all_items",
            return_value=(mock_groups, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="NonExistent_Group",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_private_cloud_group_info,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_private_cloud_group_info.main()

        assert "not found" in result.value.result["msg"]

    def test_api_error_on_list(self, mock_client, mocker):
        """Test handling API error when listing groups."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_private_cloud_group_info.collect_all_items",
            return_value=(None, "API Error"),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_private_cloud_group_info,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_private_cloud_group_info.main()

        assert "Error retrieving Private Cloud Groups" in result.value.result["msg"]

