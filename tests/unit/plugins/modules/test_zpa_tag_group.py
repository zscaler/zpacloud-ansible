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


class TestZpaTagGroup(ModuleTestCase):
    @pytest.fixture
    def mock_client(self):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_tag_group.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_create_tag_group(self, mock_client, mocker):
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_tag_group.collect_all_items",
            return_value=([], None),
        )
        mock_client.tag_group.create_tag_group.return_value = (
            MockBox({"id": "group-1", "name": "Prod-Workloads"}),
            None,
            None,
        )
        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            name="Prod-Workloads",
            description="Production workload tags",
            tags=[{"tagValue": {"name": "prod"}}],
        )
        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_tag_group

        with pytest.raises(AnsibleExitJson) as result:
            zpa_tag_group.main()

        assert result.value.result["changed"] is True
        mock_client.tag_group.create_tag_group.assert_called_once()

    def test_delete_tag_group(self, mock_client):
        mock_client.tag_group.get_tag_group.return_value = (
            MockBox({"id": "group-1", "name": "Prod-Workloads"}),
            None,
            None,
        )
        mock_client.tag_group.delete_tag_group.return_value = (None, None, None)
        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="absent",
            id="group-1",
            name="Prod-Workloads",
        )
        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_tag_group

        with pytest.raises(AnsibleExitJson) as result:
            zpa_tag_group.main()

        assert result.value.result["changed"] is True
        mock_client.tag_group.delete_tag_group.assert_called_once()

    def test_no_drift_when_tags_not_set_and_api_returns_empty_tags(
        self, mock_client, mocker
    ):
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_tag_group.collect_all_items",
            return_value=(
                [
                    MockBox(
                        {
                            "id": "group-1",
                            "name": "Dummy tag group",
                            "description": "Test tag group",
                            "tags": [],
                        }
                    )
                ],
                None,
            ),
        )
        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            name="Dummy tag group",
            description="Test tag group",
        )
        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_tag_group

        with pytest.raises(AnsibleExitJson) as result:
            zpa_tag_group.main()

        assert result.value.result["changed"] is False
        mock_client.tag_group.update_tag_group.assert_not_called()
