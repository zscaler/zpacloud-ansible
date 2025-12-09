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


class TestZPAServiceEdgeGroupsInfoModule(ModuleTestCase):
    """Unit tests for zpa_service_edge_groups_info module."""

    # Sample data representing a Service Edge Group from the API
    SAMPLE_GROUP = {
        "id": "216199618143442002",
        "name": "Test_Service_Edge_Group",
        "description": "Test Service Edge Group",
        "city_country": "San Jose, US",
        "country_code": "US",
        "enabled": True,
        "latitude": "37.33874",
        "longitude": "-121.8852525",
        "location": "San Jose, CA, USA",
        "upgrade_day": "SUNDAY",
        "upgrade_time_in_secs": "66600",
        "override_version_profile": False,
        "version_profile_id": "0",
        "version_profile_name": "Default",
        "use_in_dr_mode": False,
        "is_public": "FALSE",
        "grace_distance_enabled": False,
        "grace_distance_value_unit": "MILES",
        "microtenant_name": "Default",
    }

    SAMPLE_GROUP_2 = {
        "id": "216199618143442003",
        "name": "Test_Service_Edge_Group_2",
        "description": "Test Service Edge Group 2",
        "city_country": "New York, US",
        "country_code": "US",
        "enabled": True,
        "latitude": "40.7128",
        "longitude": "-74.0060",
        "location": "New York, NY, USA",
        "upgrade_day": "MONDAY",
        "upgrade_time_in_secs": "25200",
        "override_version_profile": False,
        "version_profile_id": "0",
        "version_profile_name": "Default",
        "use_in_dr_mode": False,
        "is_public": "TRUE",
        "grace_distance_enabled": False,
        "grace_distance_value_unit": "MILES",
        "microtenant_name": "Default",
    }

    @pytest.fixture
    def mock_client(self, mocker):
        """Create a mock ZPA client that preserves argument_spec"""
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_service_edge_groups_info.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_get_group_by_id(self, mock_client):
        """Test fetching a Service Edge Group by ID."""
        mock_group = MockBox(self.SAMPLE_GROUP)
        mock_client.service_edge_group.get_service_edge_group.return_value = (
            mock_group,
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            id="216199618143442002",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_service_edge_groups_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_service_edge_groups_info.main()

        mock_client.service_edge_group.get_service_edge_group.assert_called_once()
        assert result.value.result["changed"] is False
        assert len(result.value.result["groups"]) == 1
        assert result.value.result["groups"][0]["id"] == "216199618143442002"
        assert result.value.result["groups"][0]["name"] == "Test_Service_Edge_Group"

    def test_get_group_by_name(self, mock_client, mocker):
        """Test fetching a Service Edge Group by name."""
        mock_groups = [MockBox(self.SAMPLE_GROUP), MockBox(self.SAMPLE_GROUP_2)]

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_service_edge_groups_info.collect_all_items",
            return_value=(mock_groups, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Test_Service_Edge_Group",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_service_edge_groups_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_service_edge_groups_info.main()

        assert result.value.result["changed"] is False
        assert len(result.value.result["groups"]) == 1
        assert result.value.result["groups"][0]["name"] == "Test_Service_Edge_Group"

    def test_get_all_groups(self, mock_client, mocker):
        """Test fetching all Service Edge Groups."""
        mock_groups = [MockBox(self.SAMPLE_GROUP), MockBox(self.SAMPLE_GROUP_2)]

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_service_edge_groups_info.collect_all_items",
            return_value=(mock_groups, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_service_edge_groups_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_service_edge_groups_info.main()

        assert result.value.result["changed"] is False
        assert len(result.value.result["groups"]) == 2

    def test_get_group_by_id_not_found(self, mock_client):
        """Test fetching a non-existent Service Edge Group by ID."""
        mock_client.service_edge_group.get_service_edge_group.return_value = (
            None,
            None,
            "Not Found",
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            id="999999999999999999",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_service_edge_groups_info,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_service_edge_groups_info.main()

        assert "Failed to retrieve Service Edge Group ID" in result.value.result["msg"]

    def test_get_group_by_name_not_found(self, mock_client, mocker):
        """Test fetching a non-existent Service Edge Group by name."""
        mock_groups = [MockBox(self.SAMPLE_GROUP)]

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_service_edge_groups_info.collect_all_items",
            return_value=(mock_groups, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="NonExistent_Group",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_service_edge_groups_info,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_service_edge_groups_info.main()

        assert "not found" in result.value.result["msg"]

    def test_get_group_with_microtenant_id(self, mock_client):
        """Test fetching a Service Edge Group with microtenant_id."""
        mock_group = MockBox(self.SAMPLE_GROUP)
        mock_client.service_edge_group.get_service_edge_group.return_value = (
            mock_group,
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            id="216199618143442002",
            microtenant_id="123456789",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_service_edge_groups_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_service_edge_groups_info.main()

        mock_client.service_edge_group.get_service_edge_group.assert_called_once()
        call_args = mock_client.service_edge_group.get_service_edge_group.call_args
        assert "microtenant_id" in call_args[0][1]

    def test_api_error_on_list(self, mock_client, mocker):
        """Test handling API error when listing groups."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_service_edge_groups_info.collect_all_items",
            return_value=(None, "API Error"),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_service_edge_groups_info,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_service_edge_groups_info.main()

        assert "Error retrieving Service Edge Groups" in result.value.result["msg"]
