# Copyright (c) 2023 Zscaler Inc, <devrel@zscaler.com>
# MIT License

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import os
import sys
from unittest.mock import MagicMock, patch

import pytest

from tests.unit.plugins.modules.common.utils import (
    ModuleTestCase,
    set_module_args,
    AnsibleExitJson,
    DEFAULT_PROVIDER,
)
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)

COLLECTION_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
)
if COLLECTION_ROOT not in sys.path:
    sys.path.insert(0, COLLECTION_ROOT)

REAL_ARGUMENT_SPEC = ZPAClientHelper.zpa_argument_spec()


class MockBox:
    def __init__(self, data):
        self._data = data

    def as_dict(self):
        return self._data


class TestZpaTagKey(ModuleTestCase):
    @pytest.fixture
    def mock_client(self):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_tag_key.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_create_tag_key(self, mock_client, mocker):
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_tag_key.collect_all_items",
            return_value=([], None),
        )
        mock_client.tag_key.create_tag_key.return_value = (
            MockBox({"id": "key-1", "name": "Environment"}),
            None,
            None,
        )
        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            namespace_id="ns-1",
            name="Environment",
            enabled=True,
            tag_values=[{"name": "prod"}],
        )
        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_tag_key

        with pytest.raises(AnsibleExitJson) as result:
            zpa_tag_key.main()

        assert result.value.result["changed"] is True
        mock_client.tag_key.create_tag_key.assert_called_once()

    def test_delete_tag_key(self, mock_client):
        mock_client.tag_key.get_tag_key.return_value = (
            MockBox({"id": "key-1", "name": "Environment", "namespace_id": "ns-1"}),
            None,
            None,
        )
        mock_client.tag_key.delete_tag_key.return_value = (None, None, None)
        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="absent",
            namespace_id="ns-1",
            id="key-1",
            name="Environment",
        )
        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_tag_key

        with pytest.raises(AnsibleExitJson) as result:
            zpa_tag_key.main()

        assert result.value.result["changed"] is True
        mock_client.tag_key.delete_tag_key.assert_called_once()

    def test_no_drift_when_api_returns_empty_tag_values(self, mock_client, mocker):
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_tag_key.collect_all_items",
            return_value=(
                [
                    MockBox(
                        {
                            "id": "key-1",
                            "name": "DevEnvironment",
                            "description": "Environment tag key",
                            "enabled": True,
                            "tag_values": [],
                        }
                    )
                ],
                None,
            ),
        )
        mock_client.tag_key.get_tag_key.return_value = (
            MockBox(
                {
                    "id": "key-1",
                    "name": "DevEnvironment",
                    "description": "Environment tag key",
                    "enabled": True,
                    "tag_values": [],
                }
            ),
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            namespace_id="ns-1",
            name="DevEnvironment",
            description="Environment tag key",
            enabled=True,
            tag_values=[{"name": "dev1"}, {"name": "dev2"}],
        )
        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_tag_key

        with pytest.raises(AnsibleExitJson) as result:
            zpa_tag_key.main()

        assert result.value.result["changed"] is False
        mock_client.tag_key.update_tag_key.assert_not_called()
