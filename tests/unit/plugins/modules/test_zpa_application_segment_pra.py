# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

__metaclass__ = type

import pytest
from unittest.mock import MagicMock, patch
from tests.unit.plugins.modules.common.utils import (
    set_module_args, AnsibleExitJson, ModuleTestCase, DEFAULT_PROVIDER,
)
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import ZPAClientHelper

REAL_ARGUMENT_SPEC = ZPAClientHelper.zpa_argument_spec()


class MockBox:
    def __init__(self, data):
        self._data = data
        self.id = data.get("id")

    def as_dict(self):
        return self._data


class TestZPAApplicationSegmentPRAModule(ModuleTestCase):
    SAMPLE_SEGMENT = {
        "id": "123",
        "name": "PRA_App_Segment",
        "enabled": True,
        "segment_group_id": "456",
        "server_group_ids": ["789"],
        "common_apps_dto": {"apps_config": [{"domain": "app1.example.com", "application_port": "3389"}]},
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
                "apps_config": [{"name": "app1", "domain": "app1.example.com", "application_port": "3389",
                                 "application_protocol": "RDP", "app_types": ["SECURE_REMOTE_ACCESS"]}]
            },
        )
        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_application_segment_pra
        with pytest.raises(AnsibleExitJson) as result:
            zpa_application_segment_pra.main()
        assert result.value.result["changed"] is False
