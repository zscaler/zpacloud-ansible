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


class MockSegment:
    """SDK-like object exposing every payload key as an attribute."""

    def __init__(self, data):
        self._data = data

    def __getattr__(self, name):
        return self._data.get(name)

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

    def test_create_does_not_touch_foreign_ba_apps(self, mock_client, mocker):
        """Creating a new BA segment while another segment's BA app exists in
        the tenant must not mark that app as deleted (which the create API
        rejects with 400 resource.not.found) nor adopt its baAppId."""
        foreign_segment = MockSegment(
            {
                "id": "other-segment-id",
                "name": "Other_BA_Segment",
                "domain_names": ["other.example.com"],
                "clientless_apps": [
                    {
                        "id": "foreign-ba-app-id",
                        "app_id": "other-segment-id",
                        "domain": "other.example.com",
                    }
                ],
            }
        )
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_application_segment_ba_v2.collect_all_items",
            return_value=([foreign_segment], None),
        )

        created = MockSegment({"id": "new-segment-id", "name": "BA_New_Segment"})
        mock_client.app_segments_ba_v2.add_segment_ba.return_value = (
            created,
            None,
            None,
        )
        mock_client.app_segments_ba_v2.get_segment_ba.return_value = (
            MockSegment({"id": "new-segment-id", "name": "BA_New_Segment"}),
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            name="BA_New_Segment",
            enabled=True,
            segment_group_id="456",
            server_group_ids=["789"],
            tcp_port_range=[{"from": "80", "to": "80"}],
            domain_names=["new.example.com"],
            common_apps_dto={
                "apps_config": [
                    {
                        "name": "new.example.com",
                        "enabled": True,
                        "domain": "new.example.com",
                        "application_port": "80",
                        "application_protocol": "HTTP",
                        "app_types": ["BROWSER_ACCESS"],
                        "ext_domain": "example.zslogin.net",
                        "ext_label": "newlabel",
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
        _args, kwargs = mock_client.app_segments_ba_v2.add_segment_ba.call_args
        common_apps_dto = kwargs["common_apps_dto"]
        assert "deleted_ba_apps" not in common_apps_dto
        assert common_apps_dto["apps_config"][0]["ba_app_id"] == ""
        assert common_apps_dto["apps_config"][0]["app_id"] == ""

    def test_update_resolves_ba_app_id_from_own_clientless_apps(
        self, mock_client, mocker
    ):
        """On update the baAppId comes from the segment's own clientless apps,
        and a sub-app whose domain is no longer declared is marked deleted."""
        existing = MockSegment(
            {
                "id": "123",
                "name": "BA_App_Segment",
                "enabled": True,
                "segment_group_id": "456",
                "server_groups": [{"id": "789"}],
                "domain_names": ["app1.example.com", "stale.example.com"],
                "clientless_apps": [
                    {
                        "id": "own-ba-app-id",
                        "app_id": "123",
                        "domain": "app1.example.com",
                    },
                    {
                        "id": "stale-ba-app-id",
                        "app_id": "123",
                        "domain": "stale.example.com",
                    },
                ],
            }
        )
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_application_segment_ba_v2.collect_all_items",
            return_value=([existing], None),
        )

        mock_client.app_segments_ba_v2.update_segment_ba.return_value = (
            MockSegment({"id": "123", "name": "BA_App_Segment"}),
            None,
            None,
        )
        mock_client.app_segments_ba_v2.get_segment_ba.return_value = (
            MockSegment({"id": "123", "name": "BA_App_Segment"}),
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            name="BA_App_Segment",
            enabled=True,
            segment_group_id="456",
            server_group_ids=["789"],
            tcp_port_range=[{"from": "443", "to": "443"}],
            domain_names=["app1.example.com"],
            common_apps_dto={
                "apps_config": [
                    {
                        "name": "app1",
                        "enabled": True,
                        "domain": "app1.example.com",
                        "application_port": "443",
                        "application_protocol": "HTTPS",
                        "app_types": ["BROWSER_ACCESS"],
                        "certificate_id": "999",
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
        _args, kwargs = mock_client.app_segments_ba_v2.update_segment_ba.call_args
        common_apps_dto = kwargs["common_apps_dto"]
        assert common_apps_dto["apps_config"][0]["ba_app_id"] == "own-ba-app-id"
        assert common_apps_dto["apps_config"][0]["app_id"] == "123"
        assert common_apps_dto["deleted_ba_apps"] == ["stale-ba-app-id"]

    def test_remove_last_ba_app_keeps_declared_domains(self, mock_client, mocker):
        """Declaring an empty apps_config deletes the live BA sub-app but must
        keep the declared domain_names instead of wiping them to []."""
        existing = MockSegment(
            {
                "id": "123",
                "name": "BA_App_Segment",
                "enabled": True,
                "segment_group_id": "456",
                "server_groups": [{"id": "789"}],
                "domain_names": ["app1.example.com"],
                "tcp_port_range": [{"from": "443", "to": "443"}],
                "clientless_apps": [
                    {
                        "id": "own-ba-app-id",
                        "app_id": "123",
                        "domain": "app1.example.com",
                    }
                ],
            }
        )
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_application_segment_ba_v2.collect_all_items",
            return_value=([existing], None),
        )

        mock_client.app_segments_ba_v2.update_segment_ba.return_value = (
            MockSegment({"id": "123", "name": "BA_App_Segment"}),
            None,
            None,
        )
        mock_client.app_segments_ba_v2.get_segment_ba.return_value = (
            MockSegment({"id": "123", "name": "BA_App_Segment"}),
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            name="BA_App_Segment",
            enabled=True,
            segment_group_id="456",
            server_group_ids=["789"],
            tcp_port_range=[{"from": "443", "to": "443"}],
            domain_names=["app1.example.com"],
            common_apps_dto={"apps_config": []},
        )
        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_application_segment_ba_v2,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_application_segment_ba_v2.main()

        assert result.value.result["changed"] is True
        _args, kwargs = mock_client.app_segments_ba_v2.update_segment_ba.call_args
        assert kwargs["common_apps_dto"]["deleted_ba_apps"] == ["own-ba-app-id"]
        assert kwargs["common_apps_dto"]["apps_config"] == []
        # The declared domains and ports must survive the sub-app removal.
        assert kwargs["domain_names"] == ["app1.example.com"]

    IN_SYNC_SEGMENT = {
        "id": "123",
        "name": "BA_App_Segment",
        "enabled": True,
        "bypass_type": "NEVER",
        "health_reporting": "NONE",
        "segment_group_id": "456",
        "server_groups": [{"id": "789"}],
        "domain_names": ["app1.example.com"],
        "tcp_port_range": [{"from": "443", "to": "443"}],
        "tcp_port_ranges": ["443", "443"],
        "clientless_apps": [
            {"id": "own-ba-app-id", "app_id": "123", "domain": "app1.example.com"}
        ],
    }

    IN_SYNC_ARGS = dict(
        state="present",
        name="BA_App_Segment",
        enabled=True,
        segment_group_id="456",
        server_group_ids=["789"],
        tcp_port_range=[{"from": "443", "to": "443"}],
        domain_names=["app1.example.com"],
        common_apps_dto={
            "apps_config": [
                {
                    "name": "app1",
                    "enabled": True,
                    "domain": "app1.example.com",
                    "application_port": "443",
                    "application_protocol": "HTTPS",
                    "app_types": ["BROWSER_ACCESS"],
                    "certificate_id": "999",
                }
            ]
        },
    )

    def _run_in_sync(self, mock_client, mocker, clientless_apps):
        segment = dict(self.IN_SYNC_SEGMENT, clientless_apps=clientless_apps)
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_application_segment_ba_v2.collect_all_items",
            return_value=([MockSegment(segment)], None),
        )
        mock_client.app_segments_ba_v2.update_segment_ba.return_value = (
            MockSegment({"id": "123", "name": "BA_App_Segment"}),
            None,
            None,
        )
        mock_client.app_segments_ba_v2.get_segment_ba.return_value = (
            MockSegment({"id": "123", "name": "BA_App_Segment"}),
            None,
            None,
        )
        set_module_args(provider=DEFAULT_PROVIDER, **self.IN_SYNC_ARGS)
        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_application_segment_ba_v2,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_application_segment_ba_v2.main()
        return result.value.result

    def test_orphaned_ba_app_triggers_update(self, mock_client, mocker):
        """A sub-app deleted outside Ansible leaves domain_names intact, so the
        declared apps_config domain is the only evidence the segment drifted."""
        result = self._run_in_sync(mock_client, mocker, clientless_apps=[])

        assert result["changed"] is True
        assert mock_client.app_segments_ba_v2.update_segment_ba.called

        # An empty ba_app_id is what makes the API recreate the sub-app rather
        # than try to reference the one that was deleted.
        _args, kwargs = mock_client.app_segments_ba_v2.update_segment_ba.call_args
        assert kwargs["common_apps_dto"]["apps_config"][0]["ba_app_id"] == ""

    def test_live_ba_app_stays_idempotent(self, mock_client, mocker):
        """Guards the fix against the opposite failure: a segment whose sub-apps
        are all present must not report drift on every run."""
        result = self._run_in_sync(
            mock_client,
            mocker,
            clientless_apps=self.IN_SYNC_SEGMENT["clientless_apps"],
        )

        assert result["changed"] is False
        assert not mock_client.app_segments_ba_v2.update_segment_ba.called
