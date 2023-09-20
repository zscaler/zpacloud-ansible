=========================================
Zscaler Private Access Ansible Collection
=========================================

Version: 1.2.0

The Zscaler Private Access Ansible collection is a collection of modules that
automate configuration and operational tasks on Zscaler Private Access Cloud. The
underlying protocol uses API calls that are wrapped within the Ansible
framework.

This is a **community supported project**; hence, this project or the software module is not affiliated or supported by Zscaler engineering teams in any way.

Installation
============

Ansible 2.9 is **required** for using collections.

Install the collection using `ansible-galaxy`:

.. code-block:: bash

    ansible-galaxy collection install zscaler.zpacloud

Then in your playbooks you can specify that you want to use the
`zpacloud` collection like so:

.. code-block:: yaml

    collections:
        - zscaler.zpacloud

* Ansible Galaxy: https://galaxy.ansible.com/zscaler/zpacloud
* GitHub repo:  https://github.com/zscaler/zpacloud-ansible


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   examples
   modules
   history
   authors
   license


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
