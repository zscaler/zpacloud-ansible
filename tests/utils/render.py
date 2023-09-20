#!/usr/bin/env python

from __future__ import absolute_import, division, print_function

__metaclass__ = type


import os

# Get environment variables
client_id = os.getenv("ZPA_CLIENT_ID")
client_secret = os.getenv("ZPA_CLIENT_SECRET")
customer_id = os.getenv("ZPA_CUSTOMER_ID")

content = """
---
client_id: %s
client_secret: %s
customer_id: %s

""" % (
    client_id,
    client_secret,
    customer_id,
)

f = open("./tests/integration/integration_config.yml", "w")
f.write(content)
f.close()
