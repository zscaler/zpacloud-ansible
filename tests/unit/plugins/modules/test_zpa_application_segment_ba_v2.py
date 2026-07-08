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


class MockBox:
    def __init__(self, data):
        self._data = data
        self.id = data.get("id")

    def as_dict(self):
        return self._data


class TestZPAApplicationSegmentBAV2Module(ModuleTestCase):
    SAMPLE_SEGMENT = {
        "id": "123",
        "name": "BA_App_Segment",
        "enabled": True,
        "segment_group_id": "456",
        "server_group_ids": ["789"],
        "common_apps_dto": {
            "apps_config": [{"domain": "app1.example.com", "application_port": "443"}]
        },
    }

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_application_segment_ba_v2.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_delete_nonexistent_segment(self, mock_client, mocker):
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_application_segment_ba_v2.collect_all_items",
            return_value=([], None),
        )
        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="absent",
            name="NonExistent_Segment",
            segment_group_id="456",
            server_group_ids=["789"],
            common_apps_dto={
                "apps_config": [
                    {
                        "name": "app1",
                        "domain": "app1.example.com",
                        "application_port": "443",
                        "application_protocol": "HTTPS",
                        "app_types": ["BROWSER_ACCESS"],
                    }
                ]
            },
        )
        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_application_segment_ba_v2,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_application_segment_ba_v2.main()
        assert result.value.result["changed"] is False

    def test_create_segment_with_managed_certificate(self, mock_client, mocker):
        """A BA segment using a Zscaler-managed certificate forwards the
        ext_domain / ext_label fields (and no certificate_id) to the SDK."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_application_segment_ba_v2.collect_all_items",
            return_value=([], None),
        )

        created = MockBox({"id": "999", "name": "BA_Managed_Cert"})
        mock_client.app_segments_ba_v2.add_segment_ba.return_value = (
            created,
            None,
            None,
        )
        mock_client.app_segments_ba_v2.get_segment_ba.return_value = (
            MockBox({"id": "999", "name": "BA_Managed_Cert"}),
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            name="BA_Managed_Cert",
            enabled=True,
            segment_group_id="456",
            server_group_ids=["789"],
            tcp_port_range=[{"from": "80", "to": "80"}],
            domain_names=["app1.example.com"],
            common_apps_dto={
                "apps_config": [
                    {
                        "name": "app1",
                        "enabled": True,
                        "domain": "app1.example.com",
                        "application_port": "80",
                        "application_protocol": "HTTP",
                        "app_types": ["BROWSER_ACCESS"],
                        "ext_domain": "example.zslogin.net",
                        "ext_label": "app1label",
                    }
                ]
            },
        )
        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_application_segment_ba_v2,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_application_segment_ba_v2.main()

        assert result.value.result["changed"] is True

        assert mock_client.app_segments_ba_v2.add_segment_ba.called
        _args, kwargs = mock_client.app_segments_ba_v2.add_segment_ba.call_args
        apps_config = kwargs["common_apps_dto"]["apps_config"]
        assert apps_config[0]["ext_domain"] == "example.zslogin.net"
        assert apps_config[0]["ext_label"] == "app1label"
        # A Zscaler-managed certificate app should not carry a certificate_id.
        assert apps_config[0].get("certificate_id") is None
