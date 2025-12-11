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


class TestZPAUserPortalLinkInfoModule(ModuleTestCase):
    SAMPLE_LINKS = [
        {"id": "123", "name": "Link01", "link": "https://example.com"},
        {"id": "456", "name": "Link02", "link": "https://test.com"},
    ]

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_user_portal_link_info.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_get_all_links(self, mock_client, mocker):
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_user_portal_link_info.collect_all_items",
            return_value=([MockBox(l) for l in self.SAMPLE_LINKS], None),
        )
        set_module_args(provider=DEFAULT_PROVIDER)
        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_user_portal_link_info
        with pytest.raises(AnsibleExitJson) as result:
            zpa_user_portal_link_info.main()
        assert result.value.result["changed"] is False
        assert len(result.value.result["links"]) == 2

    def test_get_link_by_id(self, mock_client):
        mock_client.user_portal_link.get_portal_link.return_value = (MockBox(self.SAMPLE_LINKS[0]), None, None)
        set_module_args(provider=DEFAULT_PROVIDER, id="123")
        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_user_portal_link_info
        with pytest.raises(AnsibleExitJson) as result:
            zpa_user_portal_link_info.main()
        assert result.value.result["links"][0]["name"] == "Link01"

    def test_link_not_found(self, mock_client, mocker):
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_user_portal_link_info.collect_all_items",
            return_value=([MockBox(l) for l in self.SAMPLE_LINKS], None),
        )
        set_module_args(provider=DEFAULT_PROVIDER, name="NonExistent")
        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_user_portal_link_info
        with pytest.raises(AnsibleFailJson) as result:
            zpa_user_portal_link_info.main()
        assert "not found" in result.value.result["msg"]
