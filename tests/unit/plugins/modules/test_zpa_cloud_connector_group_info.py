# -*- coding: utf-8 -*-
#
# Copyright (c) 2023 Zscaler Inc, <devrel@zscaler.com>
# MIT License

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys
import os

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
    def __init__(self, data):
        self._data = data

    def as_dict(self):
        return self._data

    def __getattr__(self, name):
        return self._data.get(name)


class TestZPACloudConnectorGroupInfoModule(ModuleTestCase):
    """Unit tests for zpa_cloud_connector_group_info module."""

    SAMPLE_GROUP = {
        "id": "216196257331292017",
        "name": "zs-cc-vpc-096108eb5d9e68d71-ca-central-1a",
        "description": "Cloud Connector Group",
        "enabled": True,
    }

    SAMPLE_GROUP_2 = {
        "id": "216196257331292018",
        "name": "zs-cc-vpc-096108eb5d9e68d71-us-east-1a",
        "description": "Cloud Connector Group US East",
        "enabled": True,
    }

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_cloud_connector_group_info.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_get_group_by_id(self, mock_client):
        """Test fetching a Cloud Connector Group by ID."""
        mock_group = MockBox(self.SAMPLE_GROUP)
        mock_client.cloud_connector_groups.get_cloud_connector_groups.return_value = (
            mock_group,
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            id="216196257331292017",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_cloud_connector_group_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_cloud_connector_group_info.main()

        mock_client.cloud_connector_groups.get_cloud_connector_groups.assert_called_once()
        assert result.value.result["changed"] is False
        assert len(result.value.result["groups"]) == 1

    def test_get_group_by_name(self, mock_client, mocker):
        """Test fetching a Cloud Connector Group by name."""
        mock_groups = [MockBox(self.SAMPLE_GROUP), MockBox(self.SAMPLE_GROUP_2)]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_cloud_connector_group_info.collect_all_items",
            return_value=(mock_groups, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="zs-cc-vpc-096108eb5d9e68d71-ca-central-1a",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_cloud_connector_group_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_cloud_connector_group_info.main()

        assert result.value.result["changed"] is False
        assert len(result.value.result["groups"]) == 1

    def test_get_all_groups(self, mock_client, mocker):
        """Test fetching all Cloud Connector Groups."""
        mock_groups = [MockBox(self.SAMPLE_GROUP), MockBox(self.SAMPLE_GROUP_2)]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_cloud_connector_group_info.collect_all_items",
            return_value=(mock_groups, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_cloud_connector_group_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_cloud_connector_group_info.main()

        assert result.value.result["changed"] is False
        assert len(result.value.result["groups"]) == 2

    def test_group_not_found_by_name(self, mock_client, mocker):
        """Test fetching a non-existent Cloud Connector Group by name."""
        mock_groups = [MockBox(self.SAMPLE_GROUP)]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_cloud_connector_group_info.collect_all_items",
            return_value=(mock_groups, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="NonExistent_Group",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_cloud_connector_group_info,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_cloud_connector_group_info.main()

        assert "not found" in result.value.result["msg"]

