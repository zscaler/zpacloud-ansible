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


class TestZPAServiceEdgeAssistantScheduleInfoModule(ModuleTestCase):
    """Unit tests for zpa_service_edge_assistant_schedule_info module."""

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
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_service_edge_assistant_schedule_info.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_get_schedule_by_id(self, mock_client):
        mock_schedule = MockBox(self.SAMPLE_SCHEDULE)
        mock_client.service_edge_schedule.get_service_edge_schedule.return_value = (
            mock_schedule,
            None,
            None,
        )

        set_module_args(provider=DEFAULT_PROVIDER, id="216199618143441990")

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_service_edge_assistant_schedule_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_service_edge_assistant_schedule_info.main()

        assert result.value.result["changed"] is False

    def test_get_schedule_by_customer_id(self, mock_client):
        mock_schedule = MockBox(self.SAMPLE_SCHEDULE)
        mock_client.service_edge_schedule.get_service_edge_schedule.return_value = (
            mock_schedule,
            None,
            None,
        )

        set_module_args(provider=DEFAULT_PROVIDER, customer_id="216199618143191041")

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_service_edge_assistant_schedule_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_service_edge_assistant_schedule_info.main()

        assert result.value.result["changed"] is False

    def test_schedule_not_found(self, mock_client):
        mock_client.service_edge_schedule.get_service_edge_schedule.return_value = (
            None,
            None,
            "Not Found",
        )

        set_module_args(provider=DEFAULT_PROVIDER, id="999999999999999999")

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_service_edge_assistant_schedule_info,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_service_edge_assistant_schedule_info.main()

        assert (
            "Failed" in result.value.result["msg"]
            or "not found" in result.value.result["msg"].lower()
            or "Error" in result.value.result["msg"]
        )
