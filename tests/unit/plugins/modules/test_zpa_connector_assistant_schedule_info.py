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


class TestZPAConnectorAssistantScheduleInfoModule(ModuleTestCase):
    """Unit tests for zpa_connector_assistant_schedule_info module."""

    SAMPLE_SCHEDULE = {
        "id": "5",
        "customer_id": "216199618143191040",
        "enabled": True,
        "delete_disabled": False,
        "frequency": "days",
        "frequency_interval": "7",
    }

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_connector_assistant_schedule_info.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_get_schedule(self, mock_client):
        mock_client.app_connector_schedule.get_connector_schedule.return_value = (
            MockBox(self.SAMPLE_SCHEDULE),
            None,
            None,
        )

        set_module_args(provider=DEFAULT_PROVIDER)

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_connector_assistant_schedule_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_connector_assistant_schedule_info.main()

        assert result.value.result["changed"] is False
        assert "data" in result.value.result
        assert len(result.value.result["data"]) == 1

    def test_get_schedule_by_id(self, mock_client):
        mock_client.app_connector_schedule.get_connector_schedule.return_value = (
            MockBox(self.SAMPLE_SCHEDULE),
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            id="5",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_connector_assistant_schedule_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_connector_assistant_schedule_info.main()

        assert result.value.result["changed"] is False
        assert result.value.result["data"][0]["id"] == "5"

    def test_get_schedule_id_mismatch(self, mock_client):
        mock_client.app_connector_schedule.get_connector_schedule.return_value = (
            MockBox(self.SAMPLE_SCHEDULE),
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            id="999",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_connector_assistant_schedule_info,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_connector_assistant_schedule_info.main()

        assert (
            "No App Connector Schedule found with ID '999'"
            in result.value.result["msg"]
        )

    def test_api_error(self, mock_client):
        mock_client.app_connector_schedule.get_connector_schedule.return_value = (
            None,
            None,
            "API Error",
        )

        set_module_args(provider=DEFAULT_PROVIDER)

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_connector_assistant_schedule_info,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_connector_assistant_schedule_info.main()

        assert "Failed to retrieve App Connector Schedule" in result.value.result["msg"]
