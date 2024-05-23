# Zscaler Private Access (ZPA) Ansible Collection

[![Galaxy version](https://img.shields.io/badge/dynamic/json?style=flat&label=Galaxy&prefix=v&url=https://galaxy.ansible.com/api/v3/plugin/ansible/content/published/collections/index/zscaler/zpacloud/versions/?is_highest=true&query=data[0].version)](https://galaxy.ansible.com/ui/repo/published/zscaler/zpacloud/)
[![Ansible Lint](https://github.com/zscaler/zpacloud-ansible/actions/workflows/ansible-test-lint.yml/badge.svg?branch=master)](https://github.com/zscaler/zpacloud-ansible/actions/workflows/ansible-test-lint.yml)
[![sanity](https://github.com/zscaler/zpacloud-ansible/actions/workflows/ansible-test-sanity.yml/badge.svg?branch=master)](https://github.com/zscaler/zpacloud-ansible/actions/workflows/ansible-test-sanity.yml)
[![Documentation Status](https://readthedocs.org/projects/zpacloud-ansible/badge/?version=latest)](https://zpacloud-ansible.readthedocs.io/en/latest/?badge=latest)
[![License](https://img.shields.io/github/license/zscaler/zpacloud-ansible?color=blue)](https://github.com/zscaler/zpacloud-ansible/v2/blob/master/LICENSE)
[![Zscaler Community](https://img.shields.io/badge/zscaler-community-blue)](https://community.zscaler.com/)

<div style="display: flex; align-items: center;">
    <a href="https://catalog.redhat.com/software/search?p=1&type=Ansible%20collection&partnerName=Zscaler">
        <img src="https://catalog.redhat.com/img/svg/logo.svg" alt="RedHat logo" title="RedHat Ecosystem Catalog" height="40" />
    </a>
    <a href="https://www.zscaler.com/">
        <img src="https://www.zscaler.com/themes/custom/zscaler/logo.svg" alt="Zscaler logo" title="Zscaler" height="30" style="margin-left: 30px;" />
    </a>
</div>

## Zscaler Support

-> **Disclaimer:** Please refer to our [General Support Statement](https://zscaler.github.io/zpacloud-ansible/support.html) before proceeding with the use of this collection. You can also refer to our [troubleshooting guide](https://zscaler.github.io/zpacloud-ansible/troubleshooting.html) for guidance on typical problems.

This collection contains modules and plugins to assist in automating the configuration and operational tasks on Zscaler Private Access cloud, and API interactions with Ansible.

- Free software: MIT License
- [Documentation](https://zscaler.github.io/zpacloud-ansible)
- [Repository](https://github.com/zscaler/zpacloud-ansible)
- [Example Playbooks](https://github.com/zscaler/zpacloud-playbooks)

## Tested Ansible Versions

This collection is tested with the most current Ansible releases.  Ansible versions
before 2.15 are **not supported**.

## Python Version

The minimum python version for this collection is python `3.9`.

## Installation

Install this collection using the Ansible Galaxy CLI:

```bash
ansible-galaxy collection install zscaler.zpacloud
```

You can also include it in a `requirements.yml` file and install it via `ansible-galaxy collection install -r requirements.yml`, using the format:

```yaml
  collections:
    - zscaler.zpacloud
```

## Using modules from the zpacloud Collection in your playbooks

It's preferable to use content in this collection using their [Fully Qualified Collection Namespace (FQCN)](https://ansible.readthedocs.io/projects/lint/rules/fqcn/), for example `zscaler.zpacloud.zpa_app_connector_groups`:

```yaml
- name: ZPA App Connector Group
  hosts: localhost

  vars:
    zpa_cloud:
      client_id: "{{ lookup('env', 'ZPA_CLIENT_ID') }}"
      client_secret: "{{ lookup('env', 'ZPA_CLIENT_SECRET') }}"
      customer_id: "{{ lookup('env', 'ZPA_CUSTOMER_ID') }}"
      cloud: "{{ lookup('env', 'ZPA_CLOUD') | default(omit) }}"

  tasks:
    - name: Get Information Details of All Customer Version Profiles
      zscaler.zpacloud.zpa_customer_version_profile_facts:
      register: version_profile_id

    - name: Create App Connector Group Example
      zscaler.zpacloud.zpa_app_connector_groups:
        provider: '{{ zpa_cloud }}'
        name: "Example"
        description: "Example"
        enabled: true
        city_country: "California, US"
        country_code: "US"
        latitude: "37.3382082"
        longitude: "-121.8863286"
        location: "San Jose, CA, USA"
        upgrade_day: "SUNDAY"
        upgrade_time_in_secs: "66600"
        override_version_profile: true
        version_profile_id: "{{ version_profile_id.data[0].id }}"
        dns_query_type: "IPV4"
```

(Note that [use of the `collections` key is now discouraged](https://ansible-lint.readthedocs.io/rules/fqcn/))

## Releasing, changelogs, versioning and deprecation

The intended release frequency for major and minor versions are performed whenever there is a need for fixing issues or to address security concerns.

Changelog details are created automatically and more recently can be found [here](./CHANGELOG.md), but also the full history is [here](https://github.com/zscaler/zpacloud-ansible/releases).

[Semantic versioning](https://semver.org/) is adhered to for this project.

Deprecations are done by version number, not by date or by age of release. Breaking change deprecations will only be made with major versions.

## Support

The Zscaler Private Access (ZPA) Collection of Ansible Modules is [certified on Ansible Automation Hub](https://console.redhat.com/ansible/automation-hub/repo/published/zscaler/zpacloud) and officially supported for Ansible subscribers. Ansible subscribers can engage for support through their usual route towards Red Hat.

For those who are not Ansible subscribers, this Collection of Ansible Modules is also [published on Ansible Galaxy](https://galaxy.ansible.com/ui/repo/published/zscaler/zpacloud) and also supported via the formal Zscaler suppport process. Please refer to our [General Support Statement](https://zscaler.github.io/zpacloud-ansible/support.html)

## MIT License

Copyright (c) 2023 [Zscaler](https://github.com/zscaler)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
