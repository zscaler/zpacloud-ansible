from __future__ import absolute_import, division, print_function


__metaclass__ = type

import unittest
from unittest.mock import MagicMock
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_policy_access_rule import (
    PolicyAccessRuleService,
)


class TestPolicyAccessRuleService(unittest.TestCase):
    def test_get_by_id_when_ok(self):
        module = MagicMock()
        rest = MagicMock()
        rest.get = MagicMock()
        rest.get.return_value.status_code = 200
        rest.get.return_value.json = {
            "name": "bar",
            "id": "test",
            "app_connector_groups": [],
            "conditions": [],
            "app_server_groups": [],
        }
        k = PolicyAccessRuleService(module, "", rest)
        self.assertEqual(
            k.getByID("test", "1"),
            {
                "name": "bar",
                "id": "test",
                "app_connector_groups": [],
                "conditions": [],
                "app_server_groups": [],
            },
        )

    def test_get_by_id_when_nok(self):
        module = MagicMock()
        rest = MagicMock()
        rest.get = MagicMock()
        rest.get.return_value.status_code = 400
        k = PolicyAccessRuleService(module, "", rest)
        self.assertIsNone(k.getByID("test", "1"))

    def test_get_by_name_when_ok(self):
        module = MagicMock()
        rest = MagicMock()
        rest.get_paginated_data = MagicMock()
        rest.get_paginated_data.return_value = [
            {
                "name": "bar1",
                "id": "test1",
                "app_connector_groups": [],
                "conditions": [],
                "app_server_groups": [],
            },
            {
                "name": "bar2",
                "id": "test2",
                "app_connector_groups": [],
                "conditions": [],
                "app_server_groups": [],
            },
        ]
        k = PolicyAccessRuleService(module, "", rest)
        self.assertEqual(
            k.getByNameAndType("bar2", ""),
            {
                "name": "bar2",
                "id": "test2",
                "app_connector_groups": [],
                "conditions": [],
                "app_server_groups": [],
            },
        )

    def test_get_by_name_when_nok(self):
        module = MagicMock()
        rest = MagicMock()
        rest.get = MagicMock()
        rest.get.return_value.status_code = 400
        k = PolicyAccessRuleService(module, "", rest)
        self.assertIsNone(k.getByNameAndType("test", ""))

    def test_create_when_ok(self):
        jsonObj = {
            "name": "bar",
            "id": "test",
            "appConnectorGroups": [],
            "conditions": [],
            "appServerGroups": [],
        }
        obj = {
            "name": "bar",
            "id": "test",
            "app_connector_groups": [],
            "conditions": [],
            "app_server_groups": [],
        }
        module = MagicMock()
        rest = MagicMock()
        rest.post = MagicMock()
        rest.post.return_value.status_code = 200
        rest.post.return_value.json = jsonObj
        # For getById(...)
        rest.get = MagicMock()
        rest.get.return_value.status_code = 200
        rest.get.return_value.json = jsonObj
        k = PolicyAccessRuleService(module, "", rest)
        self.assertEqual(k.create(obj, ""), obj)

    def test_create_when_nok(self):
        module = MagicMock()
        rest = MagicMock()
        rest.post = MagicMock()
        rest.post.return_value.status_code = 400
        k = PolicyAccessRuleService(module, "", rest)
        self.assertIsNone(
            k.create(
                {
                    "name": "bar",
                    "id": "test",
                    "app_connector_groups": [],
                    "conditions": [],
                    "app_server_groups": [],
                },
                "",
            )
        )

    def test_update_when_ok(self):
        jsonObj = {
            "name": "bar",
            "id": "test",
            "appConnectorGroups": [],
            "conditions": [],
            "appServerGroups": [],
        }
        obj = {
            "name": "bar",
            "id": "test",
            "app_connector_groups": [],
            "conditions": [],
            "app_server_groups": [],
        }
        module = MagicMock()
        rest = MagicMock()
        rest.put = MagicMock()
        rest.put.return_value.status_code = 200
        # For getById(...)
        rest.get = MagicMock()
        rest.get.return_value.status_code = 200
        rest.get.return_value.json = jsonObj
        k = PolicyAccessRuleService(module, "", rest)
        self.assertEqual(k.update(obj, "1"), obj)

    def test_update_when_nok(self):
        module = MagicMock()
        rest = MagicMock()
        rest.put = MagicMock()
        rest.put.return_value.status_code = 400
        k = PolicyAccessRuleService(module, "", rest)
        self.assertIsNone(k.update({"name": "bar", "id": "test"}, "1"))
