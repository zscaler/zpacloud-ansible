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


class TestZPAApplicationSegmentPRAModule(ModuleTestCase):
    SAMPLE_SEGMENT = {
        "id": "123",
        "name": "PRA_App_Segment",
        "enabled": True,
        "segment_group_id": "456",
        "server_group_ids": ["789"],
        "common_apps_dto": {
            "apps_config": [{"domain": "app1.example.com", "application_port": "3389"}]
        },
        "pra_apps": [],
    }

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_application_segment_pra.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_delete_nonexistent_segment(self, mock_client, mocker):
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_application_segment_pra.collect_all_items",
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
                        "application_port": "3389",
                        "application_protocol": "RDP",
                        "app_types": ["SECURE_REMOTE_ACCESS"],
                    }
                ]
            },
        )
        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_application_segment_pra,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_application_segment_pra.main()
        assert result.value.result["changed"] is False

    def test_create_does_not_adopt_foreign_pra_app_id(self, mock_client, mocker):
        """A new segment sharing a domain with another segment's PRA app must not
        send that praAppId, which would move the sub-app off its owner."""
        foreign_pra_app = MockSegment(
            {
                "id": "ssh-pra-app-id",
                "name": "PRA_SSH_Segment",
                "app_id": "ssh-segment-id",
                "domain": "pra-test.example.com",
            }
        )
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_application_segment_pra.collect_all_items",
            return_value=([foreign_pra_app], None),
        )

        created = MockSegment({"id": "rdp-segment-id", "name": "PRA_RDP_Segment"})
        mock_client.app_segments_pra.add_segment_pra.return_value = (
            created,
            None,
            None,
        )
        mock_client.app_segments_pra.get_segment_pra.return_value = (
            MockSegment({"id": "rdp-segment-id", "name": "PRA_RDP_Segment"}),
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            name="PRA_RDP_Segment",
            enabled=True,
            segment_group_id="456",
            server_group_ids=["789"],
            tcp_port_range=[{"from": "3389", "to": "3389"}],
            domain_names=["pra-test.example.com"],
            common_apps_dto={
                "apps_config": [
                    {
                        "name": "rdp_pra",
                        "domain": "pra-test.example.com",
                        "application_port": "3389",
                        "application_protocol": "RDP",
                        "connection_security": "ANY",
                        "app_types": ["SECURE_REMOTE_ACCESS"],
                    }
                ]
            },
        )
        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_application_segment_pra,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_application_segment_pra.main()

        assert result.value.result["changed"] is True
        _args, kwargs = mock_client.app_segments_pra.add_segment_pra.call_args
        common_apps_dto = kwargs["common_apps_dto"]
        assert common_apps_dto["apps_config"][0]["pra_app_id"] == ""
        assert common_apps_dto["apps_config"][0]["app_id"] == ""
        assert "deleted_pra_apps" not in common_apps_dto

    def test_update_resolves_pra_app_id_from_own_sub_apps(self, mock_client, mocker):
        """On update the praAppId comes from the segment's own pra_apps, and a
        sub-app whose domain is no longer declared is marked for deletion."""
        existing = MockSegment(
            {
                "id": "123",
                "name": "PRA_App_Segment",
                "description": "old description",
                "enabled": True,
                "segment_group_id": "456",
                "server_groups": [{"id": "789"}],
                "domain_names": ["app1.example.com", "stale.example.com"],
                "pra_apps": [
                    {
                        "id": "own-pra-app-id",
                        "app_id": "123",
                        "domain": "app1.example.com",
                    },
                    {
                        "id": "stale-pra-app-id",
                        "app_id": "123",
                        "domain": "stale.example.com",
                    },
                ],
            }
        )
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_application_segment_pra.collect_all_items",
            return_value=([existing], None),
        )

        mock_client.app_segments_pra.update_segment_pra.return_value = (
            MockSegment({"id": "123", "name": "PRA_App_Segment"}),
            None,
            None,
        )
        mock_client.app_segments_pra.get_segment_pra.return_value = (
            MockSegment({"id": "123", "name": "PRA_App_Segment"}),
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            name="PRA_App_Segment",
            description="new description",
            enabled=True,
            segment_group_id="456",
            server_group_ids=["789"],
            tcp_port_range=[{"from": "3389", "to": "3389"}],
            domain_names=["app1.example.com"],
            common_apps_dto={
                "apps_config": [
                    {
                        "name": "app1",
                        "domain": "app1.example.com",
                        "application_port": "3389",
                        "application_protocol": "RDP",
                        "connection_security": "ANY",
                        "app_types": ["SECURE_REMOTE_ACCESS"],
                    }
                ]
            },
        )
        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_application_segment_pra,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_application_segment_pra.main()

        assert result.value.result["changed"] is True
        _args, kwargs = mock_client.app_segments_pra.update_segment_pra.call_args
        common_apps_dto = kwargs["common_apps_dto"]
        assert common_apps_dto["apps_config"][0]["pra_app_id"] == "own-pra-app-id"
        assert common_apps_dto["apps_config"][0]["app_id"] == "123"
        assert common_apps_dto["deleted_pra_apps"] == ["stale-pra-app-id"]

    IN_SYNC_SEGMENT = {
        "id": "123",
        "name": "PRA_App_Segment",
        "enabled": True,
        "bypass_type": "NEVER",
        "health_reporting": "NONE",
        "segment_group_id": "456",
        "server_groups": [{"id": "789"}],
        "domain_names": ["app1.example.com"],
        "tcp_port_range": [{"from": "3389", "to": "3389"}],
        "tcp_port_ranges": ["3389", "3389"],
        "pra_apps": [
            {"id": "own-pra-app-id", "app_id": "123", "domain": "app1.example.com"}
        ],
    }

    IN_SYNC_ARGS = dict(
        state="present",
        name="PRA_App_Segment",
        enabled=True,
        segment_group_id="456",
        server_group_ids=["789"],
        tcp_port_range=[{"from": "3389", "to": "3389"}],
        domain_names=["app1.example.com"],
        common_apps_dto={
            "apps_config": [
                {
                    "name": "app1",
                    "domain": "app1.example.com",
                    "application_port": "3389",
                    "application_protocol": "RDP",
                    "app_types": ["SECURE_REMOTE_ACCESS"],
                }
            ]
        },
    )

    def _run_in_sync(self, mock_client, mocker, pra_apps):
        segment = dict(self.IN_SYNC_SEGMENT, pra_apps=pra_apps)
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_application_segment_pra.collect_all_items",
            return_value=([MockSegment(segment)], None),
        )
        mock_client.app_segments_pra.update_segment_pra.return_value = (
            MockSegment({"id": "123", "name": "PRA_App_Segment"}),
            None,
            None,
        )
        mock_client.app_segments_pra.get_segment_pra.return_value = (
            MockSegment({"id": "123", "name": "PRA_App_Segment"}),
            None,
            None,
        )
        set_module_args(provider=DEFAULT_PROVIDER, **self.IN_SYNC_ARGS)
        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_application_segment_pra,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_application_segment_pra.main()
        return result.value.result

    def test_orphaned_pra_app_triggers_update(self, mock_client, mocker):
        """A sub-app deleted outside Ansible leaves domain_names intact, so the
        declared apps_config domain is the only evidence the segment drifted."""
        result = self._run_in_sync(mock_client, mocker, pra_apps=[])

        assert result["changed"] is True
        assert mock_client.app_segments_pra.update_segment_pra.called

        # An empty pra_app_id is what makes the API recreate the sub-app rather
        # than try to reference the one that was deleted.
        _args, kwargs = mock_client.app_segments_pra.update_segment_pra.call_args
        assert kwargs["common_apps_dto"]["apps_config"][0]["pra_app_id"] == ""

    def test_live_pra_app_stays_idempotent(self, mock_client, mocker):
        """Guards the fix against the opposite failure: a segment whose sub-apps
        are all present must not report drift on every run."""
        result = self._run_in_sync(
            mock_client,
            mocker,
            pra_apps=self.IN_SYNC_SEGMENT["pra_apps"],
        )

        assert result["changed"] is False
        assert not mock_client.app_segments_pra.update_segment_pra.called
