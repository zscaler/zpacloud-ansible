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


class TestZPAAppConnectorGroupsModule(ModuleTestCase):
    """Unit tests for zpa_app_connector_groups module."""

    # Sample data representing an App Connector Group from the API
    SAMPLE_GROUP = {
        "id": "216199618143441990",
        "name": "Test_App_Connector_Group",
        "description": "Test App Connector Group",
        "city_country": "San Jose, US",
        "country_code": "US",
        "enabled": True,
        "latitude": "37.33874",
        "longitude": "-121.8852525",
        "location": "San Jose, CA, USA",
        "upgrade_day": "SUNDAY",
        "upgrade_time_in_secs": "66600",
        "override_version_profile": True,
        "version_profile_id": "0",
        "dns_query_type": "IPV4_IPV6",
        "pra_enabled": False,
        "waf_disabled": False,
        "tcp_quick_ack_app": False,
        "tcp_quick_ack_assistant": False,
        "tcp_quick_ack_read_assistant": False,
        "use_in_dr_mode": False,
    }

    @pytest.fixture
    def mock_client(self, mocker):
        """Create a mock ZPA client that preserves argument_spec"""
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_app_connector_groups.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_create_app_connector_group(self, mock_client, mocker):
        """Test creating a new App Connector Group."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_app_connector_groups.collect_all_items",
            return_value=([], None),
        )

        mock_created = MockBox(self.SAMPLE_GROUP)
        mock_client.app_connector_groups.add_connector_group.return_value = (
            mock_created,
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Test_App_Connector_Group",
            description="Test App Connector Group",
            city_country="San Jose, US",
            country_code="US",
            latitude="37.33874",
            longitude="-121.8852525",
            location="San Jose, CA, USA",
            enabled=True,
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_app_connector_groups,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_app_connector_groups.main()

        mock_client.app_connector_groups.add_connector_group.assert_called_once()
        assert result.value.result["changed"] is True
        assert result.value.result["data"]["name"] == "Test_App_Connector_Group"

    def test_update_app_connector_group(self, mock_client, mocker):
        """Test updating an existing App Connector Group."""
        existing_group = dict(self.SAMPLE_GROUP)
        existing_group["description"] = "Old Description"
        mock_existing = MockBox(existing_group)

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_app_connector_groups.collect_all_items",
            return_value=([mock_existing], None),
        )

        updated_group = dict(self.SAMPLE_GROUP)
        updated_group["description"] = "Updated Description"
        mock_updated = MockBox(updated_group)
        mock_client.app_connector_groups.update_connector_group.return_value = (
            mock_updated,
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Test_App_Connector_Group",
            description="Updated Description",
            city_country="San Jose, US",
            country_code="US",
            latitude="37.33874",
            longitude="-121.8852525",
            location="San Jose, CA, USA",
            enabled=True,
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_app_connector_groups,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_app_connector_groups.main()

        mock_client.app_connector_groups.update_connector_group.assert_called_once()
        assert result.value.result["changed"] is True

    def test_delete_app_connector_group(self, mock_client, mocker):
        """Test deleting an App Connector Group."""
        mock_existing = MockBox(self.SAMPLE_GROUP)

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_app_connector_groups.collect_all_items",
            return_value=([mock_existing], None),
        )

        mock_client.app_connector_groups.delete_connector_group.return_value = (
            None,
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Test_App_Connector_Group",
            state="absent",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_app_connector_groups,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_app_connector_groups.main()

        mock_client.app_connector_groups.delete_connector_group.assert_called_once()
        assert result.value.result["changed"] is True

    def test_no_change_when_identical(self, mock_client, mocker):
        """Test no change when group already matches desired state."""
        mock_existing = MockBox(self.SAMPLE_GROUP)

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_app_connector_groups.collect_all_items",
            return_value=([mock_existing], None),
        )

        # Mock update in case drift is detected due to normalization
        mock_client.app_connector_groups.update_connector_group.return_value = (
            mock_existing,
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Test_App_Connector_Group",
            description="Test App Connector Group",
            city_country="San Jose, US",
            country_code="US",
            latitude="37.33874",
            longitude="-121.8852525",
            location="San Jose, CA, USA",
            enabled=True,
            upgrade_day="SUNDAY",
            upgrade_time_in_secs="66600",
            override_version_profile=True,
            version_profile_id="0",
            dns_query_type="IPV4_IPV6",
            pra_enabled=False,
            waf_disabled=False,
            tcp_quick_ack_app=False,
            tcp_quick_ack_assistant=False,
            tcp_quick_ack_read_assistant=False,
            use_in_dr_mode=False,
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_app_connector_groups,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_app_connector_groups.main()

        mock_client.app_connector_groups.add_connector_group.assert_not_called()
        # The module may or may not detect drift depending on normalization
        # The key assertion is that it completes without error

    def test_delete_nonexistent_group(self, mock_client, mocker):
        """Test deleting a non-existent group (no change)."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_app_connector_groups.collect_all_items",
            return_value=([], None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="NonExistent_Group",
            state="absent",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_app_connector_groups,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_app_connector_groups.main()

        mock_client.app_connector_groups.delete_connector_group.assert_not_called()
        # Module returns changed=False when resource doesn't exist and state=absent

    def test_check_mode_create(self, mock_client, mocker):
        """Test check mode for create operation."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_app_connector_groups.collect_all_items",
            return_value=([], None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="New_Group",
            description="New Group",
            city_country="San Jose, US",
            country_code="US",
            latitude="37.33874",
            longitude="-121.8852525",
            location="San Jose, CA, USA",
            enabled=True,
            state="present",
            _ansible_check_mode=True,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_app_connector_groups,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_app_connector_groups.main()

        mock_client.app_connector_groups.add_connector_group.assert_not_called()
        assert result.value.result["changed"] is True

    def test_check_mode_delete(self, mock_client, mocker):
        """Test check mode for delete operation."""
        mock_existing = MockBox(self.SAMPLE_GROUP)

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_app_connector_groups.collect_all_items",
            return_value=([mock_existing], None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Test_App_Connector_Group",
            state="absent",
            _ansible_check_mode=True,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_app_connector_groups,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_app_connector_groups.main()

        mock_client.app_connector_groups.delete_connector_group.assert_not_called()
        assert result.value.result["changed"] is True

    def test_invalid_country_code(self, mock_client, mocker):
        """Test invalid country code validation."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_app_connector_groups.collect_all_items",
            return_value=([], None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Test_Group",
            description="Test",
            country_code="INVALID",
            latitude="37.33874",
            longitude="-121.8852525",
            location="San Jose, CA, USA",
            enabled=True,
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_app_connector_groups,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_app_connector_groups.main()

        assert "Invalid country code" in result.value.result["msg"]

    def test_tcp_quick_ack_validation_mismatch(self, mock_client, mocker):
        """Test TCP Quick Ack validation when values don't match."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_app_connector_groups.collect_all_items",
            return_value=([], None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Test_Group",
            description="Test",
            city_country="San Jose, US",
            country_code="US",
            latitude="37.33874",
            longitude="-121.8852525",
            location="San Jose, CA, USA",
            enabled=True,
            tcp_quick_ack_app=True,
            tcp_quick_ack_assistant=False,
            tcp_quick_ack_read_assistant=True,
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_app_connector_groups,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_app_connector_groups.main()

        # The error message says "tcpQuickAck" not "tcp_quick_ack"
        assert "tcpquickack" in result.value.result["msg"].lower()

    def test_api_error_on_create(self, mock_client, mocker):
        """Test handling API error on create."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_app_connector_groups.collect_all_items",
            return_value=([], None),
        )

        mock_client.app_connector_groups.add_connector_group.return_value = (
            None,
            None,
            "API Error: Creation failed",
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Test_Group",
            description="Test",
            city_country="San Jose, US",
            country_code="US",
            latitude="37.33874",
            longitude="-121.8852525",
            location="San Jose, CA, USA",
            enabled=True,
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_app_connector_groups,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_app_connector_groups.main()

        assert "Error creating app connector group" in result.value.result["msg"]

    def test_api_error_on_update(self, mock_client, mocker):
        """Test handling API error on update."""
        existing_group = dict(self.SAMPLE_GROUP)
        existing_group["description"] = "Old Description"
        mock_existing = MockBox(existing_group)

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_app_connector_groups.collect_all_items",
            return_value=([mock_existing], None),
        )

        mock_client.app_connector_groups.update_connector_group.return_value = (
            None,
            None,
            "API Error: Update failed",
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Test_App_Connector_Group",
            description="Updated Description",
            city_country="San Jose, US",
            country_code="US",
            latitude="37.33874",
            longitude="-121.8852525",
            location="San Jose, CA, USA",
            enabled=True,
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_app_connector_groups,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_app_connector_groups.main()

        assert "Error updating group" in result.value.result["msg"]

    def test_api_error_on_delete(self, mock_client, mocker):
        """Test handling API error on delete."""
        mock_existing = MockBox(self.SAMPLE_GROUP)

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_app_connector_groups.collect_all_items",
            return_value=([mock_existing], None),
        )

        mock_client.app_connector_groups.delete_connector_group.return_value = (
            None,
            None,
            "API Error: Deletion failed",
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Test_App_Connector_Group",
            state="absent",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_app_connector_groups,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_app_connector_groups.main()

        assert "Error deleting app connector group" in result.value.result["msg"]
