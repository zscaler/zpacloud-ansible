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


class TestZPAApplicationSegmentInfoModule(ModuleTestCase):
    """Unit tests for zpa_application_segment_info module."""

    SAMPLE_SEGMENT = {
        "id": "216199618143441990",
        "name": "Test_App_Segment",
        "description": "Test Application Segment",
        "enabled": True,
        "domain_names": ["test.example.com"],
        "segment_group_id": "216199618143441991",
        "tcp_port_ranges": ["443", "443"],
        "health_reporting": "ON_ACCESS",
        "bypass_type": "NEVER",
    }

    SAMPLE_SEGMENT_2 = {
        "id": "216199618143441992",
        "name": "Test_App_Segment_2",
        "description": "Test Application Segment 2",
        "enabled": True,
        "domain_names": ["test2.example.com"],
        "segment_group_id": "216199618143441991",
        "tcp_port_ranges": ["8080", "8080"],
        "health_reporting": "CONTINUOUS",
        "bypass_type": "NEVER",
    }

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_application_segment_info.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_get_segment_by_id(self, mock_client):
        mock_segment = MockBox(self.SAMPLE_SEGMENT)
        mock_client.application_segment.get_segment.return_value = (mock_segment, None, None)

        set_module_args(provider=DEFAULT_PROVIDER, id="216199618143441990")

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_application_segment_info

        with pytest.raises(AnsibleExitJson) as result:
            zpa_application_segment_info.main()

        assert result.value.result["changed"] is False
        assert len(result.value.result["groups"]) == 1
        assert result.value.result["groups"][0]["id"] == "216199618143441990"

    def test_get_segment_by_name(self, mock_client, mocker):
        mock_segments = [MockBox(self.SAMPLE_SEGMENT), MockBox(self.SAMPLE_SEGMENT_2)]

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_application_segment_info.collect_all_items",
            return_value=(mock_segments, None),
        )

        set_module_args(provider=DEFAULT_PROVIDER, name="Test_App_Segment")

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_application_segment_info

        with pytest.raises(AnsibleExitJson) as result:
            zpa_application_segment_info.main()

        assert result.value.result["changed"] is False
        assert len(result.value.result["app_segments"]) == 1
        assert result.value.result["app_segments"][0]["name"] == "Test_App_Segment"

    def test_get_all_segments(self, mock_client, mocker):
        mock_segments = [MockBox(self.SAMPLE_SEGMENT), MockBox(self.SAMPLE_SEGMENT_2)]

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_application_segment_info.collect_all_items",
            return_value=(mock_segments, None),
        )

        set_module_args(provider=DEFAULT_PROVIDER)

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_application_segment_info

        with pytest.raises(AnsibleExitJson) as result:
            zpa_application_segment_info.main()

        assert result.value.result["changed"] is False
        assert len(result.value.result["app_segments"]) == 2

    def test_segment_not_found_by_id(self, mock_client):
        mock_client.application_segment.get_segment.return_value = (None, None, "Not Found")

        set_module_args(provider=DEFAULT_PROVIDER, id="999999999999999999")

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_application_segment_info

        with pytest.raises(AnsibleFailJson) as result:
            zpa_application_segment_info.main()

        assert "Failed to retrieve Application Segment ID" in result.value.result["msg"]

    def test_segment_not_found_by_name(self, mock_client, mocker):
        mock_segments = [MockBox(self.SAMPLE_SEGMENT)]

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_application_segment_info.collect_all_items",
            return_value=(mock_segments, None),
        )

        set_module_args(provider=DEFAULT_PROVIDER, name="NonExistent_Segment")

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_application_segment_info

        with pytest.raises(AnsibleFailJson) as result:
            zpa_application_segment_info.main()

        assert "not found" in result.value.result["msg"]

    def test_api_error_on_list(self, mock_client, mocker):
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_application_segment_info.collect_all_items",
            return_value=(None, "API Error"),
        )

        set_module_args(provider=DEFAULT_PROVIDER)

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_application_segment_info

        with pytest.raises(AnsibleFailJson) as result:
            zpa_application_segment_info.main()

        assert "Error retrieving Application Segments" in result.value.result["msg"]

