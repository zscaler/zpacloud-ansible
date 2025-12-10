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


class TestZPACustomerVersionProfileInfoModule(ModuleTestCase):
    """Unit tests for zpa_customer_version_profile_info module."""

    SAMPLE_PROFILE = {
        "id": "216199618143441990",
        "name": "Default",
        "customer_id": "216199618143191041",
        "upgrade_priority": "WEEK",
        "visibility_scope": "ALL",
        "creation_time": "1693027293",
        "modified_time": "1693027293",
    }

    SAMPLE_PROFILE_2 = {
        "id": "216199618143441991",
        "name": "Previous Default",
        "customer_id": "216199618143191041",
        "upgrade_priority": "DAY",
        "visibility_scope": "ALL",
        "creation_time": "1693027293",
        "modified_time": "1693027293",
    }

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_customer_version_profile_info.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_get_profile_by_id(self, mock_client, mocker):
        mock_profiles = [MockBox(self.SAMPLE_PROFILE)]

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_customer_version_profile_info.collect_all_items",
            return_value=(mock_profiles, None),
        )

        set_module_args(provider=DEFAULT_PROVIDER, id="216199618143441990")

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_customer_version_profile_info

        with pytest.raises(AnsibleExitJson) as result:
            zpa_customer_version_profile_info.main()

        assert result.value.result["changed"] is False
        assert len(result.value.result["profiles"]) == 1

    def test_get_profile_by_name(self, mock_client, mocker):
        mock_profiles = [MockBox(self.SAMPLE_PROFILE), MockBox(self.SAMPLE_PROFILE_2)]

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_customer_version_profile_info.collect_all_items",
            return_value=(mock_profiles, None),
        )

        set_module_args(provider=DEFAULT_PROVIDER, name="Default")

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_customer_version_profile_info

        with pytest.raises(AnsibleExitJson) as result:
            zpa_customer_version_profile_info.main()

        assert result.value.result["changed"] is False

    def test_get_all_profiles(self, mock_client, mocker):
        mock_profiles = [MockBox(self.SAMPLE_PROFILE), MockBox(self.SAMPLE_PROFILE_2)]

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_customer_version_profile_info.collect_all_items",
            return_value=(mock_profiles, None),
        )

        set_module_args(provider=DEFAULT_PROVIDER)

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_customer_version_profile_info

        with pytest.raises(AnsibleExitJson) as result:
            zpa_customer_version_profile_info.main()

        assert result.value.result["changed"] is False
        assert len(result.value.result["profiles"]) == 2

    def test_profile_not_found(self, mock_client, mocker):
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_customer_version_profile_info.collect_all_items",
            return_value=([], None),
        )

        set_module_args(provider=DEFAULT_PROVIDER, name="NonExistent")

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_customer_version_profile_info

        with pytest.raises(AnsibleFailJson) as result:
            zpa_customer_version_profile_info.main()

        assert "not found" in result.value.result["msg"]

    def test_api_error_on_list(self, mock_client, mocker):
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_customer_version_profile_info.collect_all_items",
            return_value=(None, "API Error"),
        )

        set_module_args(provider=DEFAULT_PROVIDER)

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_customer_version_profile_info

        with pytest.raises(AnsibleFailJson) as result:
            zpa_customer_version_profile_info.main()

        assert "Error retrieving version profiles" in result.value.result["msg"]
