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


class TestZPAExtranetResourcePartnerInfoModule(ModuleTestCase):
    SAMPLE_PARTNERS = [
        {"id": "123", "name": "Partner_ER_01", "enabled": True},
        {"id": "456", "name": "Partner_ER_02", "enabled": True},
    ]

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_extranet_resource_partner_info.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_get_all_partners(self, mock_client, mocker):
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_extranet_resource_partner_info.collect_all_items",
            return_value=([MockBox(p) for p in self.SAMPLE_PARTNERS], None),
        )
        set_module_args(provider=DEFAULT_PROVIDER)
        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_extranet_resource_partner_info
        with pytest.raises(AnsibleExitJson) as result:
            zpa_extranet_resource_partner_info.main()
        assert result.value.result["changed"] is False
        assert len(result.value.result["partners"]) == 2

    def test_get_partner_by_id(self, mock_client, mocker):
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_extranet_resource_partner_info.collect_all_items",
            return_value=([MockBox(p) for p in self.SAMPLE_PARTNERS], None),
        )
        set_module_args(provider=DEFAULT_PROVIDER, id="123")
        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_extranet_resource_partner_info
        with pytest.raises(AnsibleExitJson) as result:
            zpa_extranet_resource_partner_info.main()
        assert result.value.result["partners"][0]["name"] == "Partner_ER_01"

    def test_partner_not_found(self, mock_client, mocker):
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_extranet_resource_partner_info.collect_all_items",
            return_value=([MockBox(p) for p in self.SAMPLE_PARTNERS], None),
        )
        set_module_args(provider=DEFAULT_PROVIDER, name="NonExistent")
        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_extranet_resource_partner_info
        with pytest.raises(AnsibleFailJson) as result:
            zpa_extranet_resource_partner_info.main()
        assert "not found" in result.value.result["msg"]
