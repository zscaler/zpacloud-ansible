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


class TestZPAAppSegmentMultimatchBulkInfoModule(ModuleTestCase):
    SAMPLE_REFERENCES = [
        {"id": "123", "app_segment_name": "Segment01", "domains": ["app1.example.com"]},
    ]

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_application_segment_multimatch_bulk_info.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_get_unsupported_references(self, mock_client):
        mock_client.application_segment.get_multimatch_unsupported_references.return_value = (
            [MockBox(r) for r in self.SAMPLE_REFERENCES], None, None
        )
        set_module_args(provider=DEFAULT_PROVIDER, domain_names=["app1.example.com"])
        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_application_segment_multimatch_bulk_info
        with pytest.raises(AnsibleExitJson) as result:
            zpa_application_segment_multimatch_bulk_info.main()
        assert result.value.result["changed"] is False
        assert "unsupported_references" in result.value.result

    def test_empty_references(self, mock_client):
        mock_client.application_segment.get_multimatch_unsupported_references.return_value = ([], None, None)
        set_module_args(provider=DEFAULT_PROVIDER, domain_names=["app1.example.com"])
        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_application_segment_multimatch_bulk_info
        with pytest.raises(AnsibleExitJson) as result:
            zpa_application_segment_multimatch_bulk_info.main()
        assert result.value.result["unsupported_references"] == []

    def test_api_error(self, mock_client):
        mock_client.application_segment.get_multimatch_unsupported_references.return_value = (None, None, "API Error")
        set_module_args(provider=DEFAULT_PROVIDER, domain_names=["app1.example.com"])
        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_application_segment_multimatch_bulk_info
        with pytest.raises(AnsibleFailJson) as result:
            zpa_application_segment_multimatch_bulk_info.main()
        assert "Failed to retrieve" in result.value.result["msg"]
