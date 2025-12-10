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


class TestZPAC2CIPRangesInfoModule(ModuleTestCase):
    """Unit tests for zpa_c2c_ip_ranges_info module."""

    SAMPLE_RANGES = [
        {
            "id": "216199618143441990",
            "name": "Corporate_Range",
            "description": "Corporate IP Range",
            "enabled": True,
            "ip_range_begin": "10.0.0.1",
            "ip_range_end": "10.0.0.254",
        },
        {
            "id": "216199618143441991",
            "name": "Branch_Range",
            "description": "Branch Office Range",
            "enabled": True,
            "ip_range_begin": "192.168.1.1",
            "ip_range_end": "192.168.1.254",
        },
    ]

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_c2c_ip_ranges_info.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_get_all_ranges(self, mock_client):
        mock_client.c2c_ip_ranges.list_ip_ranges.return_value = (
            [MockBox(r) for r in self.SAMPLE_RANGES],
            None,
            None,
        )

        set_module_args(provider=DEFAULT_PROVIDER)

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_c2c_ip_ranges_info

        with pytest.raises(AnsibleExitJson) as result:
            zpa_c2c_ip_ranges_info.main()

        assert result.value.result["changed"] is False
        assert len(result.value.result["ranges"]) == 2

    def test_get_range_by_id(self, mock_client):
        mock_client.c2c_ip_ranges.get_ip_range.return_value = (
            MockBox(self.SAMPLE_RANGES[0]),
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            id="216199618143441990",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_c2c_ip_ranges_info

        with pytest.raises(AnsibleExitJson) as result:
            zpa_c2c_ip_ranges_info.main()

        assert result.value.result["changed"] is False
        assert result.value.result["ranges"][0]["name"] == "Corporate_Range"

    def test_get_range_by_name(self, mock_client):
        mock_client.c2c_ip_ranges.list_ip_ranges.return_value = (
            [MockBox(r) for r in self.SAMPLE_RANGES],
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Branch_Range",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_c2c_ip_ranges_info

        with pytest.raises(AnsibleExitJson) as result:
            zpa_c2c_ip_ranges_info.main()

        assert result.value.result["changed"] is False
        assert len(result.value.result["ranges"]) == 1
        assert result.value.result["ranges"][0]["name"] == "Branch_Range"

    def test_range_not_found_by_name(self, mock_client):
        mock_client.c2c_ip_ranges.list_ip_ranges.return_value = (
            [MockBox(r) for r in self.SAMPLE_RANGES],
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="NonExistent_Range",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_c2c_ip_ranges_info

        with pytest.raises(AnsibleFailJson) as result:
            zpa_c2c_ip_ranges_info.main()

        assert "not found" in result.value.result["msg"]

    def test_api_error(self, mock_client):
        mock_client.c2c_ip_ranges.get_ip_range.return_value = (None, None, "API Error")

        set_module_args(
            provider=DEFAULT_PROVIDER,
            id="123",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_c2c_ip_ranges_info

        with pytest.raises(AnsibleFailJson) as result:
            zpa_c2c_ip_ranges_info.main()

        assert "Failed to retrieve" in result.value.result["msg"]
