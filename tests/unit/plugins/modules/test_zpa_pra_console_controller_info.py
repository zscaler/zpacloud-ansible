# -*- coding: utf-8 -*-
#
# Copyright (c) 2023 Zscaler Inc, <devrel@zscaler.com>
# MIT License

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys
import os

COLLECTION_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
)
if COLLECTION_ROOT not in sys.path:
    sys.path.insert(0, COLLECTION_ROOT)

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

    def __getattr__(self, name):
        return self._data.get(name)


class TestZPAPRAConsoleControllerInfoModule(ModuleTestCase):
    """Unit tests for zpa_pra_console_controller_info module."""

    SAMPLE_CONSOLE = {
        "id": "216199618143442010",
        "name": "PRA Console",
        "description": "PRA Console",
        "enabled": True,
        "pra_application_id": "216199618143442001",
    }

    SAMPLE_CONSOLE_2 = {
        "id": "216199618143442011",
        "name": "PRA Console 2",
        "description": "PRA Console 2",
        "enabled": True,
        "pra_application_id": "216199618143442002",
    }

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_pra_console_controller_info.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_get_console_by_id(self, mock_client):
        """Test fetching a PRA Console by ID."""
        mock_console = MockBox(self.SAMPLE_CONSOLE)
        mock_client.pra_console.get_console.return_value = (mock_console, None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            id="216199618143442010",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_pra_console_controller_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_pra_console_controller_info.main()

        mock_client.pra_console.get_console.assert_called_once()
        assert result.value.result["changed"] is False
        assert len(result.value.result["groups"]) == 1

    def test_get_console_by_name(self, mock_client, mocker):
        """Test fetching a PRA Console by name."""
        mock_consoles = [MockBox(self.SAMPLE_CONSOLE), MockBox(self.SAMPLE_CONSOLE_2)]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_pra_console_controller_info.collect_all_items",
            return_value=(mock_consoles, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="PRA Console",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_pra_console_controller_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_pra_console_controller_info.main()

        assert result.value.result["changed"] is False
        assert len(result.value.result["groups"]) == 1

    def test_get_all_consoles(self, mock_client, mocker):
        """Test fetching all PRA Consoles."""
        mock_consoles = [MockBox(self.SAMPLE_CONSOLE), MockBox(self.SAMPLE_CONSOLE_2)]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_pra_console_controller_info.collect_all_items",
            return_value=(mock_consoles, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_pra_console_controller_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_pra_console_controller_info.main()

        assert result.value.result["changed"] is False
        assert len(result.value.result["groups"]) == 2

    def test_console_not_found_by_id(self, mock_client):
        """Test fetching a non-existent console by ID."""
        mock_client.pra_console.get_console.return_value = (None, None, "Not Found")

        set_module_args(
            provider=DEFAULT_PROVIDER,
            id="999999",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_pra_console_controller_info,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_pra_console_controller_info.main()

        assert "Failed to retrieve PRA Console ID" in result.value.result["msg"]

    def test_console_not_found_by_name(self, mock_client, mocker):
        """Test fetching a non-existent console by name."""
        mock_consoles = [MockBox(self.SAMPLE_CONSOLE)]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_pra_console_controller_info.collect_all_items",
            return_value=(mock_consoles, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="NonExistent_Console",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_pra_console_controller_info,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_pra_console_controller_info.main()

        assert "not found" in result.value.result["msg"]

