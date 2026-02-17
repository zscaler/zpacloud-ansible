# -*- coding: utf-8 -*-
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
        self.name = data.get("name")

    def as_dict(self):
        return self._data


class TestZPAAppSegmentByTypeInfoModule(ModuleTestCase):
    SAMPLE_SEGMENTS = [
        {"id": "123", "name": "ba_app01", "domain": "app1.example.com"},
        {"id": "456", "name": "ba_app02", "domain": "app2.example.com"},
    ]

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_application_segment_by_type_info.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_get_all_segments_by_type(self, mock_client, mocker):
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_application_segment_by_type_info.collect_all_items",
            return_value=([MockBox(s) for s in self.SAMPLE_SEGMENTS], None),
        )
        set_module_args(provider=DEFAULT_PROVIDER, application_type="BROWSER_ACCESS")
        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_application_segment_by_type_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_application_segment_by_type_info.main()
        assert result.value.result["changed"] is False
        assert len(result.value.result["data"]) == 2

    def test_get_segment_by_name(self, mock_client, mocker):
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_application_segment_by_type_info.collect_all_items",
            return_value=([MockBox(s) for s in self.SAMPLE_SEGMENTS], None),
        )
        set_module_args(
            provider=DEFAULT_PROVIDER,
            application_type="BROWSER_ACCESS",
            name="ba_app01",
        )
        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_application_segment_by_type_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_application_segment_by_type_info.main()
        assert len(result.value.result["data"]) == 1
        assert result.value.result["data"][0]["name"] == "ba_app01"

    def test_segment_not_found(self, mock_client, mocker):
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_application_segment_by_type_info.collect_all_items",
            return_value=([MockBox(s) for s in self.SAMPLE_SEGMENTS], None),
        )
        set_module_args(
            provider=DEFAULT_PROVIDER,
            application_type="BROWSER_ACCESS",
            name="NonExistent",
        )
        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_application_segment_by_type_info,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_application_segment_by_type_info.main()
        assert "not found" in result.value.result["msg"]
