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


class TestZPALSSConfigLogTypesFormatsInfoModule(ModuleTestCase):
    SAMPLE_LOG_FORMAT = {
        "csv": "%s{LogTimestamp:time} User Activity zpa-lss: ,%s{Customer}",
        "json": '{"LogTimestamp": %j{LogTimestamp:time},"Customer": %j{Customer}}',
        "tsv": "%s{LogTimestamp:time}\\t%s{Customer}",
    }

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_lss_config_log_types_formats_info.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_get_log_format(self, mock_client):
        mock_client.lss.get_all_log_formats.return_value = self.SAMPLE_LOG_FORMAT
        set_module_args(provider=DEFAULT_PROVIDER, log_type="zpn_trans_log")
        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_lss_config_log_types_formats_info
        with pytest.raises(AnsibleExitJson) as result:
            zpa_lss_config_log_types_formats_info.main()
        assert result.value.result["changed"] is False
        assert "csv" in result.value.result["data"]
        assert "json" in result.value.result["data"]

    def test_log_format_not_found(self, mock_client):
        mock_client.lss.get_all_log_formats.return_value = None
        set_module_args(provider=DEFAULT_PROVIDER, log_type="zpn_trans_log")
        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_lss_config_log_types_formats_info
        with pytest.raises(AnsibleFailJson) as result:
            zpa_lss_config_log_types_formats_info.main()
        assert "Failed to retrieve" in result.value.result["msg"]
