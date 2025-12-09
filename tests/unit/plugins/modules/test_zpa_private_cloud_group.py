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


class TestZPAPrivateCloudGroupModule(ModuleTestCase):
    """Unit tests for zpa_private_cloud_group module."""

    SAMPLE_GROUP = {
        "id": "216199618143442000",
        "name": "US East Private Cloud",
        "description": "Private Cloud Group for US East region",
        "enabled": True,
        "city_country": "San Jose, US",
        "country_code": "US",
        "latitude": "37.3382082",
        "longitude": "-121.8863286",
        "location": "San Jose, CA, USA",
        "upgrade_day": "SUNDAY",
    }

    @pytest.fixture
    def mock_client(self, mocker):
        """Create a mock ZPA client that preserves argument_spec"""
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_private_cloud_group.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_create_private_cloud_group(self, mock_client, mocker):
        """Test creating a new Private Cloud Group."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_private_cloud_group.collect_all_items",
            return_value=([], None),
        )

        mock_created = MockBox(self.SAMPLE_GROUP)
        mock_client.private_cloud_group.add_cloud_group.return_value = (
            mock_created,
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="US East Private Cloud",
            description="Private Cloud Group for US East region",
            enabled=True,
            city_country="San Jose, US",
            country_code="US",
            latitude="37.3382082",
            longitude="-121.8863286",
            location="San Jose, CA, USA",
            upgrade_day="SUNDAY",
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_private_cloud_group,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_private_cloud_group.main()

        mock_client.private_cloud_group.add_cloud_group.assert_called_once()
        assert result.value.result["changed"] is True
        assert result.value.result["data"]["name"] == "US East Private Cloud"

    def test_update_private_cloud_group(self, mock_client, mocker):
        """Test updating an existing Private Cloud Group."""
        existing_group = dict(self.SAMPLE_GROUP)
        existing_group["description"] = "Old Description"
        mock_existing = MockBox(existing_group)

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_private_cloud_group.collect_all_items",
            return_value=([mock_existing], None),
        )

        updated_group = dict(self.SAMPLE_GROUP)
        updated_group["description"] = "Updated Description"
        mock_updated = MockBox(updated_group)
        mock_client.private_cloud_group.update_cloud_group.return_value = (
            mock_updated,
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="US East Private Cloud",
            description="Updated Description",
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_private_cloud_group,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_private_cloud_group.main()

        mock_client.private_cloud_group.update_cloud_group.assert_called_once()
        assert result.value.result["changed"] is True

    def test_delete_private_cloud_group(self, mock_client, mocker):
        """Test deleting a Private Cloud Group."""
        mock_existing = MockBox(self.SAMPLE_GROUP)

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_private_cloud_group.collect_all_items",
            return_value=([mock_existing], None),
        )

        mock_client.private_cloud_group.delete_cloud_group.return_value = (
            None,
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="US East Private Cloud",
            state="absent",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_private_cloud_group,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_private_cloud_group.main()

        mock_client.private_cloud_group.delete_cloud_group.assert_called_once()
        assert result.value.result["changed"] is True

    def test_no_change_when_identical(self, mock_client, mocker):
        """Test no change when group already matches desired state."""
        mock_existing = MockBox(self.SAMPLE_GROUP)

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_private_cloud_group.collect_all_items",
            return_value=([mock_existing], None),
        )

        # Mock update in case drift is detected
        mock_client.private_cloud_group.update_cloud_group.return_value = (
            mock_existing,
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="US East Private Cloud",
            description="Private Cloud Group for US East region",
            enabled=True,
            city_country="San Jose, US",
            country_code="US",
            latitude="37.3382082",
            longitude="-121.8863286",
            location="San Jose, CA, USA",
            upgrade_day="SUNDAY",
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_private_cloud_group,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_private_cloud_group.main()

        mock_client.private_cloud_group.add_cloud_group.assert_not_called()

    def test_delete_nonexistent_group(self, mock_client, mocker):
        """Test deleting a non-existent group (no change)."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_private_cloud_group.collect_all_items",
            return_value=([], None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="NonExistent_Group",
            state="absent",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_private_cloud_group,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_private_cloud_group.main()

        mock_client.private_cloud_group.delete_cloud_group.assert_not_called()

    def test_check_mode_create(self, mock_client, mocker):
        """Test check mode for create operation."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_private_cloud_group.collect_all_items",
            return_value=([], None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="New_Group",
            description="New Group",
            state="present",
            _ansible_check_mode=True,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_private_cloud_group,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_private_cloud_group.main()

        mock_client.private_cloud_group.add_cloud_group.assert_not_called()
        assert result.value.result["changed"] is True

    def test_api_error_on_create(self, mock_client, mocker):
        """Test handling API error on create."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_private_cloud_group.collect_all_items",
            return_value=([], None),
        )

        mock_client.private_cloud_group.add_cloud_group.return_value = (
            None,
            None,
            "API Error: Creation failed",
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Test_Group",
            description="Test",
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_private_cloud_group,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_private_cloud_group.main()

        assert "Error creating Private Cloud Group" in result.value.result["msg"]

    def test_api_error_on_delete(self, mock_client, mocker):
        """Test handling API error on delete."""
        mock_existing = MockBox(self.SAMPLE_GROUP)

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_private_cloud_group.collect_all_items",
            return_value=([mock_existing], None),
        )

        mock_client.private_cloud_group.delete_cloud_group.return_value = (
            None,
            None,
            "API Error: Deletion failed",
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="US East Private Cloud",
            state="absent",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_private_cloud_group,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_private_cloud_group.main()

        assert "Error deleting Private Cloud Group" in result.value.result["msg"]

