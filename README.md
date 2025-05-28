# Zscaler Private Access (ZPA) Ansible Collection

[![Galaxy version](https://img.shields.io/badge/dynamic/json?style=flat&label=Galaxy&prefix=v&url=https://galaxy.ansible.com/api/v3/plugin/ansible/content/published/collections/index/zscaler/zpacloud/versions/?is_highest=true&query=data[0].version)](https://galaxy.ansible.com/ui/repo/published/zscaler/zpacloud/)
[![Ansible Lint](https://github.com/zscaler/zpacloud-ansible/actions/workflows/ansible-test-lint.yml/badge.svg?branch=master)](https://github.com/zscaler/zpacloud-ansible/actions/workflows/ansible-test-lint.yml)
[![sanity](https://github.com/zscaler/zpacloud-ansible/actions/workflows/ansible-test-sanity.yml/badge.svg?branch=master)](https://github.com/zscaler/zpacloud-ansible/actions/workflows/ansible-test-sanity.yml)
[![Documentation Status](https://readthedocs.org/projects/zpacloud-ansible/badge/?version=latest)](https://zpacloud-ansible.readthedocs.io/en/latest/?badge=latest)
[![License](https://img.shields.io/github/license/zscaler/zpacloud-ansible?color=blue)](https://github.com/zscaler/zpacloud-ansible/v2/blob/master/LICENSE)
[![Zscaler Community](https://img.shields.io/badge/zscaler-community-blue)](https://community.zscaler.com/)

## Zscaler Support

-> **Disclaimer:** Please refer to our [General Support Statement](https://zscaler.github.io/zpacloud-ansible/support.html) before proceeding with the use of this collection. You can also refer to our [troubleshooting guide](https://zscaler.github.io/zpacloud-ansible/troubleshooting.html) for guidance on typical problems.

This collection contains modules and plugins to assist in automating the configuration and operational tasks on Zscaler Private Access cloud, and API interactions with Ansible.

- Free software: [MIT License](https://github.com/zscaler/zpacloud-ansible/blob/master/LICENSE)
- [Documentation](https://zscaler.github.io/zpacloud-ansible)
- [Repository](https://github.com/zscaler/zpacloud-ansible)
- [Example Playbooks](https://github.com/zscaler/zpacloud-playbooks)

## Tested Ansible Versions

This collection is tested with the most current Ansible releases. Ansible versions
before 2.15 are **not supported**.

## Python dependencies

The minimum python version for this collection is python `3.9`.

The Python module dependencies are not automatically handled by `ansible-galaxy`. To manually install these dependencies, you have the following options:

1. Utilize the `requirements.txt` file located [here](https://github.com/zscaler/zpacloud-ansible/blob/master/requirements.txt) to install all required packages:

  ```sh
    pip install -r requirements.txt
  ```

2. Alternatively, install the [Zscaler SDK Python](https://pypi.org/project/zscaler-sdk-python/) package directly:

  ```sh
    pip install zscaler-sdk-python
  ```

## Installation

Install this collection using the Ansible Galaxy CLI:

```sh
ansible-galaxy collection install zscaler.zpacloud
```

You can also include it in a `requirements.yml` file and install it via `ansible-galaxy collection install -r requirements.yml`, using the format:

```yaml
  collections:
    - zscaler.zpacloud
```

## Zscaler OneAPI New Framework

The ZPA Ansible Collection now offers support for [OneAPI](https://help.zscaler.com/oneapi/understanding-oneapi) OAuth2 authentication through [Zidentity](https://help.zscaler.com/zidentity/what-zidentity).

**NOTE** As of version v2.0.0, this Ansible Collection offers backwards compatibility to the Zscaler legacy API framework. This is the recommended authentication method for organizations whose tenants are still not migrated to [Zidentity](https://help.zscaler.com/zidentity/what-zidentity).

**NOTE** Notice that OneAPI and Zidentity is not currently supported for the following clouds: `GOV` and `GOVUS`. Refer to the [Legacy API Framework](#legacy-api-framework) for more information on how authenticate to these environments

## OneAPI - Using modules from the ziacloud Collection in your playbooks

It's preferable to use content in this collection using their [Fully Qualified Collection Namespace (FQCN)](https://ansible.readthedocs.io/projects/lint/rules/fqcn/), for example `zscaler.zpacloud.zpa_application_segment`:

### Examples Usage - Client Secret Authentication

```yaml
---
- name: ZPA Application Segment
  hosts: localhost

  vars:
    zpa_cloud:
      client_id: "{{ lookup('env', 'ZSCALER_CLIENT_ID') }}"
      client_secret: "{{ lookup('env', 'ZSCALER_CLIENT_SECRET') }}"
      vanity_domain: "{{ lookup('env', 'ZSCALER_VANITY_DOMAIN') }}"
      customer_id: '{{ lookup("env", "ZPA_CUSTOMER_ID") | default(omit) }}'
      cloud: "{{ lookup('env', 'ZSCALER_CLOUD') | default(omit) }}"

  tasks:
    - name: Create an Application Segment
      zscaler.zpacloud.zpa_application_segment:
        provider: "{{ zpa_cloud }}"
        state: present
        name: app_segment_01_ansible
        description: app_segment_01_ansible test
        enabled: true
        is_cname_enabled: true
        tcp_keep_alive: true
        passive_health_enabled: true
        health_check_type: DEFAULT
        health_reporting: ON_ACCESS
        bypass_type: NEVER
        icmp_access_type: true
        tcp_port_range:
          - from: "8000"
            to: "8000"
        udp_port_range:
          - from: "8000"
            to: "8000"
        domain_names:
          - server1.example.com
          - server2.example.com
          - server4.example.com
          - server3.example.com
        segment_group_id: "72058304855114308"
        server_group_ids:
          - "72058304855090128"
      register: created_app
    - debug:
        msg: "{{ created_app }}"
```

(Note that [use of the `collections` key is now discouraged](https://ansible-lint.readthedocs.io/rules/fqcn/))

**NOTE**: The `zscaler_cloud` is optional and only required when authenticating to other environments i.e `beta`

⚠️ **WARNING:** Hard-coding credentials into any Ansible playbook configuration is not recommended, and risks secret leakage should this file be committed to public version controls.

```yaml
---
- name: ZPA Application Segment
  hosts: localhost

  vars:
    zpa_cloud:
      client_id: "{{ client_id | default(omit) }}"
      private_key: "{{ lookup('file', 'private_key.pem') | default(omit) }}"
      vanity_domain: "{{ vanity_domain | default(omit) }}"
      customer_id: "{{ customer_id | default(omit) }}"
      cloud: "{{ cloud | default(omit) }}"

  tasks:
    - name: Create an Application Segment
      zscaler.zpacloud.zpa_application_segment:
        provider: "{{ zpa_cloud }}"
        state: present
        name: app_segment_01_ansible
        description: app_segment_01_ansible test
        enabled: true
        is_cname_enabled: true
        tcp_keep_alive: true
        passive_health_enabled: true
        health_check_type: DEFAULT
        health_reporting: ON_ACCESS
        bypass_type: NEVER
        icmp_access_type: true
        tcp_port_range:
          - from: "8000"
            to: "8000"
        udp_port_range:
          - from: "8000"
            to: "8000"
        domain_names:
          - server1.example.com
          - server2.example.com
          - server4.example.com
          - server3.example.com
        segment_group_id: "72058304855114308"
        server_group_ids:
          - "72058304855090128"
      register: created_app
    - debug:
        msg: "{{ created_app }}"
```

## Authentication - OneAPI New Framework

As of version v2.0.0, this provider supports authentication via the new Zscaler API framework [OneAPI](https://help.zscaler.com/oneapi/understanding-oneapi)

Zscaler OneAPI uses the OAuth 2.0 authorization framework to provide secure access to Zscaler Private Access (ZPA) APIs. OAuth 2.0 allows third-party applications to obtain controlled access to protected resources using access tokens. OneAPI uses the Client Credentials OAuth flow, in which client applications can exchange their credentials with the authorization server for an access token and obtain access to the API resources, without any user authentication involved in the process.

- [ZPA API](https://help.zscaler.com/oneapi/understanding-oneapi#:~:text=Workload%20Groups-,ZPA%20API,-Zscaler%20Private%20Access)

### Default Environment variables

You can provide credentials via the `ZSCALER_CLIENT_ID`, `ZSCALER_CLIENT_SECRET`, `ZSCALER_VANITY_DOMAIN`, `ZSCALER_CLOUD` environment variables, representing your Zidentity OneAPI credentials `clientId`, `clientSecret`, `vanityDomain` and `zscaler_cloud` respectively.

| Argument        | Description                                                                                         | Environment Variable     |
|-----------------|-----------------------------------------------------------------------------------------------------|--------------------------|
| `client_id`     | _(String)_ Zscaler API Client ID, used with `client_secret` or `private_key` OAuth auth mode.         | `ZSCALER_CLIENT_ID`      |
| `client_secret` | _(String)_ Secret key associated with the API Client ID for authentication.                         | `ZSCALER_CLIENT_SECRET`  |
| `private_key`    | _(String)_ A string Private key value.                                                              | `ZSCALER_PRIVATE_KEY`    |
| `vanity_domain` | _(String)_ Refers to the domain name used by your organization.                                     | `ZSCALER_VANITY_DOMAIN`  |
| `customer_id` | _(String)_ A string that contains the ZPA customer ID which identifies the tenant                                      | `ZPA_CUSTOMER_ID`  |
| `zscaler_cloud`         | _(String)_ The name of the Zidentity cloud, e.g., beta.                                             | `ZSCALER_CLOUD`          |

### Alternative OneAPI Cloud Environments

OneAPI supports authentication and can interact with alternative Zscaler enviornments i.e `beta`. To authenticate to these environments you must provide the following values:

| Argument         | Description                                                                                         |   | Environment Variable     |
|------------------|-----------------------------------------------------------------------------------------------------|---|--------------------------|
| `vanity_domain`   | _(String)_ Refers to the domain name used by your organization |   | `ZSCALER_VANITY_DOMAIN`  |
| `zscaler_cloud`          | _(String)_ The name of the Zidentity cloud i.e beta      |   | `ZSCALER_CLOUD`          |

For example: Authenticating to Zscaler Beta environment:

```sh
export ZSCALER_VANITY_DOMAIN="acme"
export ZSCALER_CLOUD="beta"
```

### OneAPI (API Client Scope)

OneAPI Resources are automatically created within the ZIdentity Admin UI based on the RBAC Roles
applicable to APIs within the various products. For example, in ZPA, navigate to `Administration -> Role
Management` and select `Add API Role`.

Once this role has been saved, return to the ZIdentity Admin UI and from the Integration menu
select API Resources. Click the `View` icon to the right of Zscaler APIs and under the ZPA
dropdown you will see the newly created Role. In the event a newly created role is not seen in the
ZIdentity Admin UI a `Sync Now` button is provided in the API Resources menu which will initiate an
on-demand sync of newly created roles.

## Legacy API Framework

### ZPA Native Authentication

- As of version v2.0.0, this Ansible Collection offers backwards compatibility to the Zscaler legacy API framework. This is the recommended authentication method for organizations whose tenants are still **NOT** migrated to [Zidentity](https://help.zscaler.com/zidentity/what-zidentity).

### Examples Usage

```yaml
- name: ZPA App Connector Group
  hosts: localhost

  vars:
    zia_cloud:
      zpa_client_id: "{{ zpa_client_id | default(omit) }}"
      zpa_client_secret: "{{ zpa_client_secret | default(omit) }}"
      zpa_customer_id: "{{ zpa_customer_id | default(omit) }}"
      zpa_cloud: "{{ zpa_cloud | default(omit) }}"
      use_legacy_client: "{{ use_legacy_client | default(omit) }}"

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

The ZPA Cloud is identified by several cloud name prefixes, which determines which API endpoint the requests should be sent to. The following cloud environments are supported:

- `BETA`
- `GOV`
- `GOVUS`
- `ZPATWO`

### Environment variables

You can provide credentials via the `ZPA_CLIENT_ID`, `ZPA_CLIENT_SECRET`, `ZPA_CUSTOMER_ID`, `ZPA_MICROTENANT_ID`,, `ZPA_CLOUD`, `ZSCALER_USE_LEGACY_CLIENT` environment variables, representing your ZPA `zpa_client_id`, `zpa_client_secret`, `zpa_customer_id`, `zpa_microtenant_id`, `zpa_cloud` and `use_legacy_client` respectively.

| Argument     | Description | Environment variable |
|--------------|-------------|-------------------|
| `zpa_client_id`       | _(String)_ The ZPA API client ID generated from the ZPA console.| `ZPA_CLIENT_ID` |
| `zpa_client_secret`       | _(String)_ The ZPA API client secret generated from the ZPA console.| `ZPA_CLIENT_SECRET` |
| `zpa_customer_id`       | _(String)_ The ZPA tenant ID found in the Administration > Company menu in the ZPA console.| `ZPA_CUSTOMER_ID` |
| `zpa_microtenant_id`       | _(String)_ The ZPA microtenant ID found in the respective microtenant instance under Configuration & Control > Public API > API Keys menu in the ZPA console.| `ZPA_MICROTENANT_ID` |
| `zpa_cloud`       | _(String)_ The Zscaler cloud for your tenancy.| `ZPA_CLOUD` |
| `use_legacy_client`       | _(Bool)_ Enable use of the legacy ZPA API Client.| `ZSCALER_USE_LEGACY_CLIENT` |

```sh
# Change place holder values denoted by brackets to real values, including the
# brackets.

$ export ZPA_CLIENT_ID="[ZPA_CLIENT_ID]"
$ export ZPA_CLIENT_SECRET="[ZPA_CLIENT_SECRET]"
$ export ZPA_CUSTOMER_ID="[ZPA_CUSTOMER_ID]"
$ export ZPA_CLOUD="[ZPA_CLOUD]"
$ export ZPA_MICROTENANT_ID="[ZPA_MICROTENANT_ID]" # REQUIRED ONLY IF USING MICROTENANTS
$ export ZSCALER_USE_LEGACY_CLIENT=true
```

⚠️ **WARNING:** Hard-coding credentials into any Ansible playbook configuration is not recommended, and risks secret leakage should this file be committed to public version control

For details about how to retrieve your tenant Base URL and API key/token refer to the Zscaler help portal. <https://help.zscaler.com/zpa/getting-started-zpa-api>

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
