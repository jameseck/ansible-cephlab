#!/usr/bin/python

from ansible.module_utils.basic import *
from distutils.version import LooseVersion

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'James Eckersall'}

DOCUMENTATION = r'''
---
module: proxmox_get_vm_ip
short_description: Retrieves IP address from Proxmox VM
description:
  - Retrieves IP address from Proxmox VM
version_added: "2.8"
author: "James Eckersall <james.eckersall@gmail.com>"
options:
  api_host:
    description:
      - Specify the target host of the Proxmox VE cluster.
    required: true
  api_user:
    description:
      - Specify the user to authenticate with.
    required: true
  api_password:
    description:
      - Specify the password to authenticate with.
      - You can use C(PROXMOX_PASSWORD) environment variable.
  node:
    description:
      - Proxmox VE node, where the new VM will be created.
      - Only required for C(state=present).
      - For other states, it will be autodiscovered.
  vm_id:
    description:
      - The ID for the VM
  vm_ip_type:
    description:
      - Whether to retrieve ipv4 or ipv6 address
  vm_interface:
    description:
      - The VM interface to query
  validate_certs:
    description:
      - If C(no), SSL certificates will not be validated. This should only be used on personally controlled sites using self-signed certificates.
    type: bool
    default: 'no'
requirements: [ "proxmoxer", "requests" ]
'''

EXAMPLES = '''
# Retrieve ipv4 IP from eth0 on VM with vmid 600
- proxmox_get_vm_ip:
    api_user    : root@pam
    api_password: secret
    api_host    : proxhost
    node        : proxhost
    vm_id       : 600
    vm_ip_type  : ipv4
    vm_interface: eth0
'''

RETURN = '''
ip:
    description: A dict of dicts reflecting VM configs
    returned: success
    type: string
    sample: 192.168.111.12
'''

try:
    from proxmoxer import ProxmoxAPI
    HAS_PROXMOXER = True
except ImportError:
    HAS_PROXMOXER = False

def proxmox_version(proxmox):
    apireturn = proxmox.version.get()
    return LooseVersion(apireturn['version'])

def main():
  module = AnsibleModule(
    argument_spec=dict(
      args           = dict(type='str', default=None),
      api_host       = dict(required=True),
      api_user       = dict(required=True),
      api_password   = dict(no_log=True),
      validate_certs = dict(type='bool', default='no'),
      node           = dict(type='str', default='no'),
      vm_id          = dict(type='int', required=True),
      vm_ip_type     = dict(type='str', default='ipv4'),
      vm_interface   = dict(type='str', default='eth0')
    )
  )
  api_user       = module.params['api_user']
  api_host       = module.params['api_host']
  api_password   = module.params['api_password']
  validate_certs = module.params['validate_certs']
  node           = module.params['node']
  vm_id          = module.params['vm_id']
  vm_ip_type     = module.params['vm_ip_type']
  vm_interface   = module.params['vm_interface']

  try:
    proxmox = ProxmoxAPI(api_host, user=api_user, password=api_password, verify_ssl=validate_certs)
    global VZ_TYPE
    global PVE_MAJOR_VERSION
    PVE_MAJOR_VERSION = 3 if proxmox_version(proxmox) < LooseVersion('4.0') else 4
  except Exception as e:
    module.fail_json(msg='authorization on proxmox cluster failed with exception: %s' % e)

  try:
    vm_ip = proxmox.nodes(node).qemu(vm_id).agent('network-get-interfaces').get()
  except Exception as e:
    module.fail_json(msg='Getting IP for VM with vmid %s failed with exception: %s' % (vm_id, e))

  vm_ip_info = [i for i in vm_ip['result'] if i['name'] == vm_interface]
  vm_ip4_addr = [i for i in vm_ip_info[0]['ip-addresses'] if i['ip-address-type'] == vm_ip_type][0]['ip-address']

  response = vm_ip4_addr
  module.exit_json(changed=False, ip=response)

if __name__ == '__main__':
  main()
