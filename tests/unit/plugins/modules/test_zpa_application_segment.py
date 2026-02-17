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
        self.id = data.get("id")

    def as_dict(self):
        return self._data

    def __getattr__(self, name):
        return self._data.get(name)


class TestZPAApplicationSegmentModule(ModuleTestCase):
    """Unit tests for zpa_application_segment module."""

    SAMPLE_SEGMENT = {
        "id": "216199618143442010",
        "name": "Example Application Segment",
        "description": "Example Application Segment",
        "enabled": True,
        "bypass_type": "NEVER",
        "health_reporting": "ON_ACCESS",
        "is_cname_enabled": True,
        "tcp_port_ranges": ["80", "80"],
        "domain_names": ["crm.example.com"],
        "segment_group_id": "216196257331291896",
        "server_groups": [
            {
                "id": "216196257331291969",
                "name": "server_group_1",
            }
        ],
        "health_check_type": "DEFAULT",
        "match_style": "EXCLUSIVE",
        "passive_health_enabled": True,
    }

    @pytest.fixture
    def mock_client(self, mocker):
        """Create a mock ZPA client that preserves argument_spec"""
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_application_segment.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_create_application_segment(self, mock_client, mocker):
        """Test creating a new Application Segment."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_application_segment.collect_all_items",
            return_value=([], None),
        )

        mock_created = MockBox(self.SAMPLE_SEGMENT)
        mock_client.application_segment.add_segment.return_value = (
            mock_created,
            None,
            None,
        )
        mock_client.application_segment.get_segment.return_value = (
            mock_created,
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Example Application Segment",
            description="Example Application Segment",
            enabled=True,
            health_reporting="ON_ACCESS",
            bypass_type="NEVER",
            is_cname_enabled=True,
            tcp_port_range=[{"from": "80", "to": "80"}],
            domain_names=["crm.example.com"],
            segment_group_id="216196257331291896",
            server_group_ids=["216196257331291969"],
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_application_segment,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_application_segment.main()

        mock_client.application_segment.add_segment.assert_called_once()
        assert result.value.result["changed"] is True
        assert result.value.result["data"]["name"] == "Example Application Segment"

    def test_update_application_segment(self, mock_client, mocker):
        """Test updating an existing Application Segment."""
        existing_segment = dict(self.SAMPLE_SEGMENT)
        existing_segment["description"] = "Old Description"
        mock_existing = MockBox(existing_segment)

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_application_segment.collect_all_items",
            return_value=([mock_existing], None),
        )

        updated_segment = dict(self.SAMPLE_SEGMENT)
        updated_segment["description"] = "Updated Description"
        mock_updated = MockBox(updated_segment)
        mock_client.application_segment.update_segment.return_value = (
            mock_updated,
            None,
            None,
        )
        mock_client.application_segment.get_segment.return_value = (
            mock_updated,
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Example Application Segment",
            description="Updated Description",
            enabled=True,
            health_reporting="ON_ACCESS",
            bypass_type="NEVER",
            is_cname_enabled=True,
            tcp_port_range=[{"from": "80", "to": "80"}],
            domain_names=["crm.example.com"],
            segment_group_id="216196257331291896",
            server_group_ids=["216196257331291969"],
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_application_segment,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_application_segment.main()

        mock_client.application_segment.update_segment.assert_called_once()
        assert result.value.result["changed"] is True

    def test_delete_application_segment(self, mock_client, mocker):
        """Test deleting an Application Segment."""
        mock_existing = MockBox(self.SAMPLE_SEGMENT)

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_application_segment.collect_all_items",
            return_value=([mock_existing], None),
        )

        mock_client.application_segment.delete_segment.return_value = (
            None,
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Example Application Segment",
            state="absent",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_application_segment,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_application_segment.main()

        mock_client.application_segment.delete_segment.assert_called_once()
        assert result.value.result["changed"] is True

    def test_no_change_when_identical(self, mock_client, mocker):
        """Test no change when segment already matches desired state."""
        mock_existing = MockBox(self.SAMPLE_SEGMENT)

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_application_segment.collect_all_items",
            return_value=([mock_existing], None),
        )

        # Mock update in case drift is detected
        mock_client.application_segment.update_segment.return_value = (
            mock_existing,
            None,
            None,
        )
        mock_client.application_segment.get_segment.return_value = (
            mock_existing,
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Example Application Segment",
            description="Example Application Segment",
            enabled=True,
            health_reporting="ON_ACCESS",
            bypass_type="NEVER",
            is_cname_enabled=True,
            tcp_port_range=[{"from": "80", "to": "80"}],
            domain_names=["crm.example.com"],
            segment_group_id="216196257331291896",
            server_group_ids=["216196257331291969"],
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_application_segment,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_application_segment.main()

        mock_client.application_segment.add_segment.assert_not_called()

    def test_delete_nonexistent_segment(self, mock_client, mocker):
        """Test deleting a non-existent segment (no change)."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_application_segment.collect_all_items",
            return_value=([], None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="NonExistent_Segment",
            state="absent",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_application_segment,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_application_segment.main()

        mock_client.application_segment.delete_segment.assert_not_called()
        assert result.value.result["changed"] is False

    def test_check_mode_create(self, mock_client, mocker):
        """Test check mode for create operation."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_application_segment.collect_all_items",
            return_value=([], None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="New_Segment",
            description="New Segment",
            enabled=True,
            domain_names=["new.example.com"],
            segment_group_id="216196257331291896",
            server_group_ids=["216196257331291969"],
            state="present",
            _ansible_check_mode=True,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_application_segment,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_application_segment.main()

        mock_client.application_segment.add_segment.assert_not_called()
        assert result.value.result["changed"] is True

    def test_check_mode_delete(self, mock_client, mocker):
        """Test check mode for delete operation."""
        mock_existing = MockBox(self.SAMPLE_SEGMENT)

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_application_segment.collect_all_items",
            return_value=([mock_existing], None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Example Application Segment",
            state="absent",
            _ansible_check_mode=True,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_application_segment,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_application_segment.main()

        mock_client.application_segment.delete_segment.assert_not_called()
        assert result.value.result["changed"] is True

    def test_create_with_udp_ports(self, mock_client, mocker):
        """Test creating an Application Segment with UDP ports."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_application_segment.collect_all_items",
            return_value=([], None),
        )

        segment_with_udp = dict(self.SAMPLE_SEGMENT)
        segment_with_udp["udp_port_ranges"] = ["53", "53"]
        mock_created = MockBox(segment_with_udp)
        mock_client.application_segment.add_segment.return_value = (
            mock_created,
            None,
            None,
        )
        mock_client.application_segment.get_segment.return_value = (
            mock_created,
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Example Application Segment",
            description="Example Application Segment",
            enabled=True,
            tcp_port_range=[{"from": "80", "to": "80"}],
            udp_port_range=[{"from": "53", "to": "53"}],
            domain_names=["crm.example.com"],
            segment_group_id="216196257331291896",
            server_group_ids=["216196257331291969"],
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_application_segment,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_application_segment.main()

        mock_client.application_segment.add_segment.assert_called_once()

    def test_create_with_multiple_domains(self, mock_client, mocker):
        """Test creating an Application Segment with multiple domain names."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_application_segment.collect_all_items",
            return_value=([], None),
        )

        segment_multi_domain = dict(self.SAMPLE_SEGMENT)
        segment_multi_domain["domain_names"] = [
            "app1.example.com",
            "app2.example.com",
            "app3.example.com",
        ]
        mock_created = MockBox(segment_multi_domain)
        mock_client.application_segment.add_segment.return_value = (
            mock_created,
            None,
            None,
        )
        mock_client.application_segment.get_segment.return_value = (
            mock_created,
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Example Application Segment",
            description="Example Application Segment",
            enabled=True,
            tcp_port_range=[{"from": "443", "to": "443"}],
            domain_names=["app1.example.com", "app2.example.com", "app3.example.com"],
            segment_group_id="216196257331291896",
            server_group_ids=["216196257331291969"],
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_application_segment,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_application_segment.main()

        mock_client.application_segment.add_segment.assert_called_once()

    def test_icmp_access_type_conversion(self, mock_client, mocker):
        """Test that icmp_access_type bool is converted to PING/NONE."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_application_segment.collect_all_items",
            return_value=([], None),
        )

        segment_with_icmp = dict(self.SAMPLE_SEGMENT)
        segment_with_icmp["icmp_access_type"] = "PING"
        mock_created = MockBox(segment_with_icmp)
        mock_client.application_segment.add_segment.return_value = (
            mock_created,
            None,
            None,
        )
        mock_client.application_segment.get_segment.return_value = (
            mock_created,
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Example Application Segment",
            description="Example Application Segment",
            enabled=True,
            tcp_port_range=[{"from": "80", "to": "80"}],
            domain_names=["crm.example.com"],
            segment_group_id="216196257331291896",
            server_group_ids=["216196257331291969"],
            icmp_access_type=True,  # Should be converted to "PING"
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_application_segment,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_application_segment.main()

        mock_client.application_segment.add_segment.assert_called_once()

    def test_tcp_keep_alive_conversion(self, mock_client, mocker):
        """Test that tcp_keep_alive bool is converted to 0/1."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_application_segment.collect_all_items",
            return_value=([], None),
        )

        segment_with_keepalive = dict(self.SAMPLE_SEGMENT)
        segment_with_keepalive["tcp_keep_alive"] = "1"
        mock_created = MockBox(segment_with_keepalive)
        mock_client.application_segment.add_segment.return_value = (
            mock_created,
            None,
            None,
        )
        mock_client.application_segment.get_segment.return_value = (
            mock_created,
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Example Application Segment",
            description="Example Application Segment",
            enabled=True,
            tcp_port_range=[{"from": "80", "to": "80"}],
            domain_names=["crm.example.com"],
            segment_group_id="216196257331291896",
            server_group_ids=["216196257331291969"],
            tcp_keep_alive=True,  # Should be converted to "1"
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_application_segment,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_application_segment.main()

        mock_client.application_segment.add_segment.assert_called_once()

    def test_api_error_on_create(self, mock_client, mocker):
        """Test handling API error on create."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_application_segment.collect_all_items",
            return_value=([], None),
        )

        mock_client.application_segment.add_segment.return_value = (
            None,
            None,
            "API Error: Creation failed",
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Test_Segment",
            description="Test",
            enabled=True,
            domain_names=["test.example.com"],
            segment_group_id="216196257331291896",
            server_group_ids=["216196257331291969"],
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_application_segment,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_application_segment.main()

        assert "Error creating application segment" in result.value.result["msg"]

    def test_api_error_on_delete(self, mock_client, mocker):
        """Test handling API error on delete."""
        mock_existing = MockBox(self.SAMPLE_SEGMENT)

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_application_segment.collect_all_items",
            return_value=([mock_existing], None),
        )

        mock_client.application_segment.delete_segment.return_value = (
            None,
            None,
            "API Error: Deletion failed",
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Example Application Segment",
            state="absent",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_application_segment,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_application_segment.main()

        assert "Error deleting application segment" in result.value.result["msg"]

    def test_select_connector_close_to_app_with_udp_fails(self, mock_client, mocker):
        """Test that select_connector_close_to_app with UDP ports fails validation."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_application_segment.collect_all_items",
            return_value=([], None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Test_Segment",
            description="Test",
            enabled=True,
            tcp_port_range=[{"from": "80", "to": "80"}],
            udp_port_range=[{"from": "53", "to": "53"}],
            domain_names=["test.example.com"],
            segment_group_id="216196257331291896",
            server_group_ids=["216196257331291969"],
            select_connector_close_to_app=True,
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_application_segment,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_application_segment.main()

        assert "select_connector_close_to_app" in result.value.result["msg"]

    def test_match_style_inclusive(self, mock_client, mocker):
        """Test creating an Application Segment with INCLUSIVE match style."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_application_segment.collect_all_items",
            return_value=([], None),
        )

        segment_inclusive = dict(self.SAMPLE_SEGMENT)
        segment_inclusive["match_style"] = "INCLUSIVE"
        mock_created = MockBox(segment_inclusive)
        mock_client.application_segment.add_segment.return_value = (
            mock_created,
            None,
            None,
        )
        mock_client.application_segment.get_segment.return_value = (
            mock_created,
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Example Application Segment",
            description="Example Application Segment",
            enabled=True,
            tcp_port_range=[{"from": "80", "to": "80"}],
            domain_names=["crm.example.com"],
            segment_group_id="216196257331291896",
            server_group_ids=["216196257331291969"],
            match_style="INCLUSIVE",
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_application_segment,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_application_segment.main()

        mock_client.application_segment.add_segment.assert_called_once()
        call_kwargs = mock_client.application_segment.add_segment.call_args[1]
        assert call_kwargs.get("match_style") == "INCLUSIVE"
