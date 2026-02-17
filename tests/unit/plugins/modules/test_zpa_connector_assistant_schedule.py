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
    ModuleTestCase,
    DEFAULT_PROVIDER,
)

from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)

REAL_ARGUMENT_SPEC = ZPAClientHelper.zpa_argument_spec()


class MockSchedule:
    def __init__(self, data):
        self._data = data

    def to_dict(self):
        return self._data

    def get(self, key, default=None):
        return self._data.get(key, default)


class TestZPAConnectorAssistantScheduleModule(ModuleTestCase):
    """Unit tests for zpa_connector_assistant_schedule module."""

    SAMPLE_SCHEDULE = {
        "id": "216199618143441990",
        "customer_id": "216199618143191041",
        "enabled": True,
        "delete_disabled": False,
        "frequency": "days",
        "frequency_interval": "7",
    }

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_connector_assistant_schedule.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_create_schedule_when_none_exists(self, mock_client):
        # No existing schedule
        mock_client.connectors.get_connector_schedule.return_value = None
        mock_client.connectors.add_connector_schedule.return_value = MockSchedule(
            self.SAMPLE_SCHEDULE
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            customer_id="216199618143191041",
            enabled=True,
            delete_disabled=False,
            frequency="days",
            frequency_interval="7",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_connector_assistant_schedule,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_connector_assistant_schedule.main()

        assert result.value.result["changed"] is True
        assert "Schedule created successfully" in result.value.result["message"]

    def test_update_schedule_when_exists(self, mock_client):
        # Existing schedule with different values
        mock_client.connectors.get_connector_schedule.return_value = {
            "id": "216199618143441990",
            "enabled": False,
            "delete_disabled": True,
            "frequency": "days",
            "frequency_interval": "5",
        }
        mock_client.connectors.update_connector_schedule.return_value = True

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            customer_id="216199618143191041",
            enabled=True,
            delete_disabled=False,
            frequency="days",
            frequency_interval="7",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_connector_assistant_schedule,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_connector_assistant_schedule.main()

        assert result.value.result["changed"] is True
        assert "Schedule updated successfully" in result.value.result["message"]

    def test_no_change_when_schedule_identical(self, mock_client):
        # Schedule exists with same values
        mock_client.connectors.get_connector_schedule.return_value = {
            "id": "216199618143441990",
            "enabled": True,
            "delete_disabled": False,
            "frequency": "days",
            "frequency_interval": "7",
        }

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            customer_id="216199618143191041",
            enabled=True,
            delete_disabled=False,
            frequency="days",
            frequency_interval="7",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_connector_assistant_schedule,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_connector_assistant_schedule.main()

        assert result.value.result["changed"] is False
        assert "No updates required" in result.value.result["message"]

    def test_no_schedule_enabled_false(self, mock_client):
        # No schedule, enabled is False - should not create
        mock_client.connectors.get_connector_schedule.return_value = None

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            customer_id="216199618143191041",
            enabled=False,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_connector_assistant_schedule,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_connector_assistant_schedule.main()

        assert result.value.result["changed"] is False
        assert (
            "No schedule exists and creation is not enabled"
            in result.value.result["message"]
        )
