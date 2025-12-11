# -*- coding: utf-8 -*-
# Copyright (c) 2023 Zscaler Inc, <devrel@zscaler.com>
# MIT License

from __future__ import absolute_import, division, print_function

__metaclass__ = type

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


class TestZPAAppSegmentWeightedLBConfigModule(ModuleTestCase):
    """Unit tests for zpa_application_segment_weightedlb_config module."""

    SAMPLE_CONFIG = {
        "weighted_load_balancing": True,
        "application_to_server_group_mappings": [
            {"id": "123", "weight": "10", "passive": False},
            {"id": "456", "weight": "20", "passive": True},
        ],
    }

    SAMPLE_SEGMENT = {
        "id": "72058304855090129",
        "name": "MyAppSegment",
    }

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_application_segment_weightedlb_config.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_update_weighted_lb_config_by_id(self, mock_client):
        """Test updating weighted LB config by application ID"""
        mock_client.application_segment.get_weighted_lb_config.return_value = (
            MockBox({**self.SAMPLE_CONFIG, "weighted_load_balancing": False}), None, None
        )
        mock_client.application_segment.update_weighted_lb_config.return_value = (
            MockBox(self.SAMPLE_CONFIG), None, None
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            application_id="72058304855090129",
            weighted_load_balancing=True,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_application_segment_weightedlb_config

        with pytest.raises(AnsibleExitJson) as result:
            zpa_application_segment_weightedlb_config.main()

        assert result.value.result["changed"] is True

    def test_update_weighted_lb_config_by_name(self, mock_client, mocker):
        """Test updating weighted LB config by application name"""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_application_segment_weightedlb_config.collect_all_items",
            return_value=([MockBox(self.SAMPLE_SEGMENT)], None),
        )
        mock_client.application_segment.get_weighted_lb_config.return_value = (
            MockBox({**self.SAMPLE_CONFIG, "weighted_load_balancing": False}), None, None
        )
        mock_client.application_segment.update_weighted_lb_config.return_value = (
            MockBox(self.SAMPLE_CONFIG), None, None
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            application_name="MyAppSegment",
            weighted_load_balancing=True,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_application_segment_weightedlb_config

        with pytest.raises(AnsibleExitJson) as result:
            zpa_application_segment_weightedlb_config.main()

        assert result.value.result["changed"] is True

    def test_no_change_when_config_same(self, mock_client):
        """Test no change when config already matches"""
        mock_client.application_segment.get_weighted_lb_config.return_value = (
            MockBox(self.SAMPLE_CONFIG), None, None
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            application_id="72058304855090129",
            weighted_load_balancing=True,
            application_to_server_group_mappings=[
                {"id": "123", "weight": "10", "passive": False},
                {"id": "456", "weight": "20", "passive": True},
            ],
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_application_segment_weightedlb_config

        with pytest.raises(AnsibleExitJson) as result:
            zpa_application_segment_weightedlb_config.main()

        assert result.value.result["changed"] is False

    def test_check_mode(self, mock_client):
        """Test check mode"""
        mock_client.application_segment.get_weighted_lb_config.return_value = (
            MockBox({**self.SAMPLE_CONFIG, "weighted_load_balancing": False}), None, None
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            application_id="72058304855090129",
            weighted_load_balancing=True,
            _ansible_check_mode=True,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_application_segment_weightedlb_config

        with pytest.raises(AnsibleExitJson) as result:
            zpa_application_segment_weightedlb_config.main()

        assert result.value.result["changed"] is True

    def test_get_config_error(self, mock_client):
        """Test error when retrieving current config"""
        mock_client.application_segment.get_weighted_lb_config.return_value = (
            None, None, "Config error"
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            application_id="72058304855090129",
            weighted_load_balancing=True,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_application_segment_weightedlb_config

        with pytest.raises(AnsibleFailJson) as result:
            zpa_application_segment_weightedlb_config.main()

        assert "failed" in result.value.result["msg"].lower()

    def test_update_error(self, mock_client):
        """Test error during update"""
        mock_client.application_segment.get_weighted_lb_config.return_value = (
            MockBox({**self.SAMPLE_CONFIG, "weighted_load_balancing": False}), None, None
        )
        mock_client.application_segment.update_weighted_lb_config.return_value = (
            None, None, "Update error"
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            application_id="72058304855090129",
            weighted_load_balancing=True,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_application_segment_weightedlb_config

        with pytest.raises(AnsibleFailJson) as result:
            zpa_application_segment_weightedlb_config.main()

        assert "error" in result.value.result["msg"].lower()

    def test_app_not_found_by_name(self, mock_client, mocker):
        """Test error when application not found by name"""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_application_segment_weightedlb_config.collect_all_items",
            return_value=([], None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            application_name="NonExistentApp",
            weighted_load_balancing=True,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_application_segment_weightedlb_config

        with pytest.raises(AnsibleFailJson) as result:
            zpa_application_segment_weightedlb_config.main()

        assert "not found" in result.value.result["msg"].lower()

    def test_list_segments_error(self, mock_client, mocker):
        """Test error when listing segments fails"""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_application_segment_weightedlb_config.collect_all_items",
            return_value=(None, "List error"),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            application_name="MyAppSegment",
            weighted_load_balancing=True,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_application_segment_weightedlb_config

        with pytest.raises(AnsibleFailJson) as result:
            zpa_application_segment_weightedlb_config.main()

        assert "error" in result.value.result["msg"].lower()

    def test_mapping_drift_different_length(self, mock_client):
        """Test drift detection with different mapping lengths"""
        mock_client.application_segment.get_weighted_lb_config.return_value = (
            MockBox(self.SAMPLE_CONFIG), None, None
        )
        mock_client.application_segment.update_weighted_lb_config.return_value = (
            MockBox({}), None, None
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            application_id="72058304855090129",
            application_to_server_group_mappings=[
                {"id": "123", "weight": "10", "passive": False},
            ],
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_application_segment_weightedlb_config

        with pytest.raises(AnsibleExitJson) as result:
            zpa_application_segment_weightedlb_config.main()

        assert result.value.result["changed"] is True

    def test_mapping_drift_different_weight(self, mock_client):
        """Test drift detection with different weights"""
        mock_client.application_segment.get_weighted_lb_config.return_value = (
            MockBox(self.SAMPLE_CONFIG), None, None
        )
        mock_client.application_segment.update_weighted_lb_config.return_value = (
            MockBox({}), None, None
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            application_id="72058304855090129",
            application_to_server_group_mappings=[
                {"id": "123", "weight": "50", "passive": False},
                {"id": "456", "weight": "20", "passive": True},
            ],
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_application_segment_weightedlb_config

        with pytest.raises(AnsibleExitJson) as result:
            zpa_application_segment_weightedlb_config.main()

        assert result.value.result["changed"] is True

    def test_mapping_drift_new_server_group(self, mock_client):
        """Test drift detection with new server group ID"""
        mock_client.application_segment.get_weighted_lb_config.return_value = (
            MockBox(self.SAMPLE_CONFIG), None, None
        )
        mock_client.application_segment.update_weighted_lb_config.return_value = (
            MockBox({}), None, None
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            application_id="72058304855090129",
            application_to_server_group_mappings=[
                {"id": "123", "weight": "10", "passive": False},
                {"id": "789", "weight": "20", "passive": True},
            ],
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_application_segment_weightedlb_config

        with pytest.raises(AnsibleExitJson) as result:
            zpa_application_segment_weightedlb_config.main()

        assert result.value.result["changed"] is True
