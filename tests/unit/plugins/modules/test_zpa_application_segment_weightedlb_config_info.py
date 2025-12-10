# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

__metaclass__ = type

import pytest
from unittest.mock import MagicMock, patch
from tests.unit.plugins.modules.common.utils import (
    set_module_args, AnsibleExitJson, AnsibleFailJson, ModuleTestCase, DEFAULT_PROVIDER,
)
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import ZPAClientHelper

REAL_ARGUMENT_SPEC = ZPAClientHelper.zpa_argument_spec()


class MockBox:
    def __init__(self, data):
        self._data = data

    def as_dict(self):
        return self._data


class TestZPAAppSegmentWeightedLBConfigInfoModule(ModuleTestCase):
    SAMPLE_CONFIG = {"weighted_load_balancing": True, "application_to_server_group_mappings": []}
    SAMPLE_SEGMENTS = [
        {"id": "123", "name": "MyAppSegment"},
        {"id": "456", "name": "OtherSegment"},
    ]

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_application_segment_weightedlb_config_info.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_get_config_by_id(self, mock_client):
        mock_client.application_segment.get_weighted_lb_config.return_value = (MockBox(self.SAMPLE_CONFIG), None, None)
        set_module_args(provider=DEFAULT_PROVIDER, application_id="123")
        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_application_segment_weightedlb_config_info
        with pytest.raises(AnsibleExitJson) as result:
            zpa_application_segment_weightedlb_config_info.main()
        assert result.value.result["changed"] is False
        assert "config" in result.value.result

    def test_get_config_by_name(self, mock_client, mocker):
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_application_segment_weightedlb_config_info.collect_all_items",
            return_value=([MockBox(s) for s in self.SAMPLE_SEGMENTS], None),
        )
        mock_client.application_segment.get_weighted_lb_config.return_value = (MockBox(self.SAMPLE_CONFIG), None, None)
        set_module_args(provider=DEFAULT_PROVIDER, application_name="MyAppSegment")
        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_application_segment_weightedlb_config_info
        with pytest.raises(AnsibleExitJson) as result:
            zpa_application_segment_weightedlb_config_info.main()
        assert result.value.result["config"]["application_name"] == "MyAppSegment"

    def test_segment_not_found(self, mock_client, mocker):
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_application_segment_weightedlb_config_info.collect_all_items",
            return_value=([MockBox(s) for s in self.SAMPLE_SEGMENTS], None),
        )
        set_module_args(provider=DEFAULT_PROVIDER, application_name="NonExistent")
        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_application_segment_weightedlb_config_info
        with pytest.raises(AnsibleFailJson) as result:
            zpa_application_segment_weightedlb_config_info.main()
        assert "not found" in result.value.result["msg"]
