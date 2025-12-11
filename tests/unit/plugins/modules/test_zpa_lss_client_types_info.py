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


class TestZPALSSClientTypesInfoModule(ModuleTestCase):
    """Unit tests for zpa_lss_client_types_info module."""

    SAMPLE_CLIENT_TYPES = {
        "zpn_client_type_exporter": "Web Browser",
        "zpn_client_type_browser_isolation": "Cloud Browser Isolation",
        "zpn_client_type_machine_tunnel": "Machine Tunnel",
        "zpn_client_type_ip_anchoring": "ZIA Service Edge",
        "zpn_client_type_edge_connector": "Cloud Connector",
        "zpn_client_type_zapp": "Client Connector",
        "zpn_client_type_slogger": "ZPA LSS",
    }

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_lss_client_types_info.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_get_all_client_types(self, mock_client):
        # Module uses: result = client.lss.get_client_types(client_type)
        # Returns data directly, not a tuple
        mock_client.lss.get_client_types.return_value = self.SAMPLE_CLIENT_TYPES

        set_module_args(provider=DEFAULT_PROVIDER)

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_lss_client_types_info

        with pytest.raises(AnsibleExitJson) as result:
            zpa_lss_client_types_info.main()

        assert result.value.result["changed"] is False
        assert "data" in result.value.result
        assert result.value.result["data"] == self.SAMPLE_CLIENT_TYPES

    def test_get_specific_client_type(self, mock_client):
        mock_client.lss.get_client_types.return_value = {"zpn_client_type_zapp": "Client Connector"}

        set_module_args(
            provider=DEFAULT_PROVIDER,
            client_type="zpn_client_type_zapp",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_lss_client_types_info

        with pytest.raises(AnsibleExitJson) as result:
            zpa_lss_client_types_info.main()

        assert result.value.result["changed"] is False
        assert "data" in result.value.result

    def test_api_error_returns_none(self, mock_client):
        mock_client.lss.get_client_types.return_value = None

        set_module_args(provider=DEFAULT_PROVIDER)

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_lss_client_types_info

        with pytest.raises(AnsibleFailJson) as result:
            zpa_lss_client_types_info.main()

        assert "Failed to retrieve LSS client types" in result.value.result["msg"]
