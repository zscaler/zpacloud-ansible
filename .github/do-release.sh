#!/usr/bin/env bash

ansible-galaxy collection build
ansible-galaxy collection publish zscaler-zpacloud-* --server release_galaxy
ansible-galaxy collection publish zscaler-zpacloud-* --server automation_hub
