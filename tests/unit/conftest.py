# Copyright (c) 2023 Zscaler Inc, <devrel@zscaler.com>
# MIT License
#
# Pytest configuration for unit tests

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys
import os

import pytest

# Set up the ansible_collections namespace properly
# The collection is at: /path/to/ansible_collections/zscaler/zpacloud
# We need to add /path/to to sys.path so ansible_collections.zscaler.zpacloud works

COLLECTION_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
# This is the zpacloud directory

# Go up to ansible_collections parent (3 levels: zpacloud -> zscaler -> ansible_collections -> parent)
ANSIBLE_COLLECTIONS_PARENT = os.path.abspath(
    os.path.join(COLLECTION_ROOT, "..", "..", "..")
)

# Add to sys.path if not already there
if ANSIBLE_COLLECTIONS_PARENT not in sys.path:
    sys.path.insert(0, ANSIBLE_COLLECTIONS_PARENT)

# Also add collection root for local imports
if COLLECTION_ROOT not in sys.path:
    sys.path.insert(0, COLLECTION_ROOT)


@pytest.fixture(autouse=True)
def reset_module_args():
    """
    Reset Ansible module args between tests.
    This prevents test pollution.
    """
    from ansible.module_utils import basic

    basic._ANSIBLE_ARGS = None
    yield
    basic._ANSIBLE_ARGS = None


@pytest.fixture
def mock_zscaler_sdk(mocker):
    """
    Mock the entire zscaler SDK to prevent any real imports.
    Use this when testing modules that import from zscaler.
    """
    mock_sdk = mocker.MagicMock()
    mocker.patch.dict("sys.modules", {"zscaler": mock_sdk})
    return mock_sdk
