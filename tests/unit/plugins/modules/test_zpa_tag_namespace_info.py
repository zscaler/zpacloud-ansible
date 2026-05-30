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


class TestZpaTagNamespaceInfo(ModuleTestCase):
    @pytest.fixture
    def mock_client(self):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_tag_namespace_info.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_get_tag_namespace_by_id(self, mock_client):
        mock_client.tag_namespace.get_namespace.return_value = (
            MockBox({"id": "ns-1", "name": "Environment"}),
            None,
            None,
        )
        set_module_args(provider=DEFAULT_PROVIDER, id="ns-1")
        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_tag_namespace_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_tag_namespace_info.main()

        assert len(result.value.result["namespaces"]) == 1

    def test_get_all_tag_namespaces(self, mock_client, mocker):
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_tag_namespace_info.collect_all_items",
            return_value=(
                [MockBox({"id": "ns-1", "name": "Environment"})],
                None,
            ),
        )
        set_module_args(provider=DEFAULT_PROVIDER)
        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_tag_namespace_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_tag_namespace_info.main()

        assert result.value.result["changed"] is False
        assert result.value.result["namespaces"][0]["name"] == "Environment"
