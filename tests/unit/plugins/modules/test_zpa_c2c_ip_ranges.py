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


class TestZPAC2CIPRangesModule(ModuleTestCase):
    """Unit tests for zpa_c2c_ip_ranges module."""

    SAMPLE_IP_RANGE = {
        "id": "216199618143441990",
        "name": "Test_C2C_IP_Range",
        "description": "Test C2C IP Range",
        "enabled": True,
        "ip_range_begin": "10.0.0.1",
        "ip_range_end": "10.0.0.254",
    }

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_c2c_ip_ranges.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_create_ip_range(self, mock_client):
        # No existing range
        mock_client.c2c_ip_ranges.list_ip_ranges.return_value = ([], None, None)
        mock_client.c2c_ip_ranges.add_ip_range.return_value = (MockBox(self.SAMPLE_IP_RANGE), None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            name="Test_C2C_IP_Range",
            description="Test C2C IP Range",
            ip_range_begin="10.0.0.1",
            ip_range_end="10.0.0.254",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_c2c_ip_ranges

        with pytest.raises(AnsibleExitJson) as result:
            zpa_c2c_ip_ranges.main()

        assert result.value.result["changed"] is True

    def test_update_ip_range(self, mock_client):
        # Existing range with different description
        existing_range = MockBox({**self.SAMPLE_IP_RANGE, "description": "Old Description"})
        mock_client.c2c_ip_ranges.list_ip_ranges.return_value = ([existing_range], None, None)
        mock_client.c2c_ip_ranges.update_ip_range.return_value = (MockBox(self.SAMPLE_IP_RANGE), None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            name="Test_C2C_IP_Range",
            description="Test C2C IP Range",
            ip_range_begin="10.0.0.1",
            ip_range_end="10.0.0.254",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_c2c_ip_ranges

        with pytest.raises(AnsibleExitJson) as result:
            zpa_c2c_ip_ranges.main()

        assert result.value.result["changed"] is True

    def test_delete_ip_range(self, mock_client):
        existing_range = MockBox(self.SAMPLE_IP_RANGE)
        mock_client.c2c_ip_ranges.list_ip_ranges.return_value = ([existing_range], None, None)
        mock_client.c2c_ip_ranges.delete_ip_range.return_value = (None, None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="absent",
            name="Test_C2C_IP_Range",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_c2c_ip_ranges

        with pytest.raises(AnsibleExitJson) as result:
            zpa_c2c_ip_ranges.main()

        assert result.value.result["changed"] is True

    def test_no_change_when_identical(self, mock_client):
        existing_range = MockBox(self.SAMPLE_IP_RANGE)
        mock_client.c2c_ip_ranges.list_ip_ranges.return_value = ([existing_range], None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            name="Test_C2C_IP_Range",
            description="Test C2C IP Range",
            enabled=True,
            ip_range_begin="10.0.0.1",
            ip_range_end="10.0.0.254",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_c2c_ip_ranges

        with pytest.raises(AnsibleExitJson) as result:
            zpa_c2c_ip_ranges.main()

        assert result.value.result["changed"] is False

    def test_delete_nonexistent_range(self, mock_client):
        mock_client.c2c_ip_ranges.list_ip_ranges.return_value = ([], None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="absent",
            name="NonExistent_IP_Range",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_c2c_ip_ranges

        with pytest.raises(AnsibleExitJson) as result:
            zpa_c2c_ip_ranges.main()

        assert result.value.result["changed"] is False
