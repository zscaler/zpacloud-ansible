from __future__ import absolute_import, division, print_function


__metaclass__ = type

import unittest
from unittest.mock import MagicMock
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_application_segment import (
    ApplicationSegmentService,
)


class TestApplicationSegmentService(unittest.TestCase):
    def test_get_by_id_when_ok(self):
        module = MagicMock()
        rest = MagicMock()
        rest.get = MagicMock()
        rest.get.return_value.status_code = 200
        rest.get.return_value.json = {
            "name": "bar",
            "id": "test",
            "server_groups": [],
            "clientless_apps": [],
        }
        k = ApplicationSegmentService(module, "", rest)
        self.assertEqual(
            k.getByID("test"),
            {"name": "bar", "id": "test", "server_groups": [], "clientless_apps": []},
        )

    def test_get_by_id_when_nok(self):
        module = MagicMock()
        rest = MagicMock()
        rest.get = MagicMock()
        rest.get.return_value.status_code = 400
        k = ApplicationSegmentService(module, "", rest)
        self.assertIsNone(k.getByID("test"))

    def test_get_by_name_when_ok(self):
        module = MagicMock()
        rest = MagicMock()
        rest.get_paginated_data = MagicMock()
        rest.get_paginated_data.return_value = [
            {"name": "bar1", "id": "test1", "server_groups": [], "clientless_apps": []},
            {"name": "bar2", "id": "test2", "server_groups": [], "clientless_apps": []},
        ]
        k = ApplicationSegmentService(module, "", rest)
        self.assertEqual(
            k.getByName("bar2"),
            {"name": "bar2", "id": "test2", "server_groups": [], "clientless_apps": []},
        )

    def test_get_by_name_when_nok(self):
        module = MagicMock()
        rest = MagicMock()
        rest.get = MagicMock()
        rest.get.return_value.status_code = 400
        k = ApplicationSegmentService(module, "", rest)
        self.assertIsNone(k.getByName("test"))

    def test_create_when_ok(self):
        jsonObj = {
            "name": "bar",
            "id": "test",
            "serverGroups": [],
            "clientlessApps": [],
        }
        obj = {"name": "bar", "id": "test", "server_groups": [], "clientless_apps": []}
        module = MagicMock()
        rest = MagicMock()
        rest.post = MagicMock()
        rest.post.return_value.status_code = 200
        rest.post.return_value.json = jsonObj
        # For getById(...)
        rest.get = MagicMock()
        rest.get.return_value.status_code = 200
        rest.get.return_value.json = jsonObj
        k = ApplicationSegmentService(module, "", rest)
        self.assertEqual(k.create(obj), obj)

    def test_create_when_nok(self):
        module = MagicMock()
        rest = MagicMock()
        rest.post = MagicMock()
        rest.post.return_value.status_code = 400
        k = ApplicationSegmentService(module, "", rest)
        self.assertIsNone(
            k.create(
                {
                    "name": "bar",
                    "id": "test",
                    "server_groups": [],
                    "clientless_apps": [],
                }
            )
        )

    def test_update_when_ok(self):
        jsonObj = {
            "name": "bar",
            "id": "test",
            "serverGroups": [],
            "clientlessApps": [],
        }
        obj = {"name": "bar", "id": "test", "server_groups": [], "clientless_apps": []}
        module = MagicMock()
        rest = MagicMock()
        rest.put = MagicMock()
        rest.put.return_value.status_code = 200
        # For getById(...)
        rest.get = MagicMock()
        rest.get.return_value.status_code = 200
        rest.get.return_value.json = jsonObj
        k = ApplicationSegmentService(module, "", rest)
        self.assertEqual(k.update(obj), obj)

    def test_update_when_nok(self):
        module = MagicMock()
        rest = MagicMock()
        rest.put = MagicMock()
        rest.put.return_value.status_code = 400
        k = ApplicationSegmentService(module, "", rest)
        self.assertIsNone(k.update({"name": "bar", "id": "test"}))
