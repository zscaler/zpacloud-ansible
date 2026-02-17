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


class TestZPARiskScoreValuesInfoModule(ModuleTestCase):
    """Unit tests for zpa_risk_score_values_info module."""

    SAMPLE_RISK_VALUES = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "UNKNOWN"]

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_risk_score_values_info.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_get_all_risk_scores(self, mock_client):
        # Module uses: values, _unused, err = client.policies.get_risk_score_values(...)
        mock_client.policies.get_risk_score_values.return_value = (
            self.SAMPLE_RISK_VALUES,
            None,
            None,
        )

        set_module_args(provider=DEFAULT_PROVIDER)

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_risk_score_values_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_risk_score_values_info.main()

        assert result.value.result["changed"] is False
        assert "values" in result.value.result
        assert result.value.result["values"] == self.SAMPLE_RISK_VALUES

    def test_get_risk_scores_exclude_unknown(self, mock_client):
        filtered_values = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
        mock_client.policies.get_risk_score_values.return_value = (
            filtered_values,
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            exclude_unknown=True,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_risk_score_values_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_risk_score_values_info.main()

        assert result.value.result["changed"] is False
        assert "UNKNOWN" not in result.value.result["values"]

    def test_api_error(self, mock_client):
        mock_client.policies.get_risk_score_values.return_value = (
            None,
            None,
            "API Error",
        )

        set_module_args(provider=DEFAULT_PROVIDER)

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_risk_score_values_info,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_risk_score_values_info.main()

        assert "Error retrieving risk score values" in result.value.result["msg"]

    def test_empty_result(self, mock_client):
        mock_client.policies.get_risk_score_values.return_value = (None, None, None)

        set_module_args(provider=DEFAULT_PROVIDER)

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_risk_score_values_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_risk_score_values_info.main()

        assert result.value.result["changed"] is False
        assert result.value.result["values"] == []
