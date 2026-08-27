# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

__metaclass__ = type

import pytest
from unittest.mock import MagicMock, patch
from tests.unit.plugins.modules.common.utils import (
    set_module_args,
    AnsibleExitJson,
    ModuleTestCase,
    DEFAULT_PROVIDER,
)
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)

REAL_ARGUMENT_SPEC = ZPAClientHelper.zpa_argument_spec()


class MockSegment:
    """SDK-like object exposing every payload key as an attribute."""

    def __init__(self, data):
        self._data = data

    def __getattr__(self, name):
        return self._data.get(name)

    def as_dict(self):
        return self._data


class TestZPAApplicationSegmentInspectionModule(ModuleTestCase):
    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_application_segment_inspection.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_create_does_not_touch_foreign_inspection_apps(self, mock_client, mocker):
        """Creating a new inspection segment while another segment's inspection
        app exists in the tenant must not mark that app as deleted (which the
        create API rejects with 400 resource.not.found) nor adopt its id."""
        foreign_app = MockSegment(
            {
                "id": "foreign-inspect-app-id",
                "name": "Other_Inspect_Segment",
                "app_id": "other-segment-id",
                "domain": "other.example.com",
            }
        )
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_application_segment_inspection.collect_all_items",
            return_value=([foreign_app], None),
        )

        created = MockSegment({"id": "new-segment-id", "name": "Inspect_New_Segment"})
        mock_client.app_segments_inspection.add_segment_inspection.return_value = (
            created,
            None,
            None,
        )
        mock_client.app_segments_inspection.get_segment_inspection.return_value = (
            MockSegment({"id": "new-segment-id", "name": "Inspect_New_Segment"}),
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            name="Inspect_New_Segment",
            enabled=True,
            segment_group_id="456",
            server_group_ids=["789"],
            tcp_port_range=[{"from": "443", "to": "443"}],
            domain_names=["new.example.com"],
            common_apps_dto={
                "apps_config": [
                    {
                        "name": "new.example.com",
                        "enabled": True,
                        "domain": "new.example.com",
                        "application_port": "443",
                        "application_protocol": "HTTPS",
                        "app_types": ["INSPECT"],
                        "certificate_id": "999",
                    }
                ]
            },
        )
        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_application_segment_inspection,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_application_segment_inspection.main()

        assert result.value.result["changed"] is True
        _args, kwargs = (
            mock_client.app_segments_inspection.add_segment_inspection.call_args
        )
        common_apps_dto = kwargs["common_apps_dto"]
        assert "deleted_pra_apps" not in common_apps_dto
        assert common_apps_dto["apps_config"][0]["inspect_app_id"] == ""
        assert common_apps_dto["apps_config"][0]["app_id"] == ""

    def test_create_keeps_declared_domains(self, mock_client, mocker):
        """The declared domain_names must be merged with (not replaced by) the
        domains derived from apps_config."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_application_segment_inspection.collect_all_items",
            return_value=([], None),
        )

        created = MockSegment({"id": "new-segment-id", "name": "Inspect_New_Segment"})
        mock_client.app_segments_inspection.add_segment_inspection.return_value = (
            created,
            None,
            None,
        )
        mock_client.app_segments_inspection.get_segment_inspection.return_value = (
            MockSegment({"id": "new-segment-id", "name": "Inspect_New_Segment"}),
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            name="Inspect_New_Segment",
            enabled=True,
            segment_group_id="456",
            server_group_ids=["789"],
            tcp_port_range=[{"from": "443", "to": "443"}],
            domain_names=["extra.example.com", "new.example.com"],
            common_apps_dto={
                "apps_config": [
                    {
                        "name": "new.example.com",
                        "enabled": True,
                        "domain": "new.example.com",
                        "application_port": "443",
                        "application_protocol": "HTTPS",
                        "app_types": ["INSPECT"],
                        "certificate_id": "999",
                    }
                ]
            },
        )
        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_application_segment_inspection,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_application_segment_inspection.main()

        assert result.value.result["changed"] is True
        _args, kwargs = (
            mock_client.app_segments_inspection.add_segment_inspection.call_args
        )
        assert sorted(kwargs["domain_names"]) == [
            "extra.example.com",
            "new.example.com",
        ]
