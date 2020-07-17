#!/usr/bin/python

from ansible.module_utils.basic import *
from distutils.version import LooseVersion

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
      args=dict(type='str', default=None),
      api_host=dict(required=True),
      api_user=dict(required=True),
      api_password=dict(no_log=True),
      validate_certs=dict(type='bool', default='no'),
      node=dict(type='str', default='no')
    )
  )
  api_user = module.params['api_user']
  api_host = module.params['api_host']
  api_password = module.params['api_password']
  validate_certs = module.params['validate_certs']
  node = module.params['node']

  try:
    proxmox = ProxmoxAPI(api_host, user=api_user, password=api_password, verify_ssl=validate_certs)
    global VZ_TYPE
    global PVE_MAJOR_VERSION
    PVE_MAJOR_VERSION = 3 if proxmox_version(proxmox) < LooseVersion('4.0') else 4
  except Exception as e:
    module.fail_json(msg='authorization on proxmox cluster failed with exception: %s' % e)

  node = proxmox.nodes(node)

  vms = node.qemu.get()

  vm_list = []
  vm_dict = {}

  for vm in vms:
    vm_dict[vm['name']] = node.qemu(vm['vmid']).config.get()
    vm_dict[vm['name']]['vmid'] = vm['vmid']

  response = vm_dict
  module.exit_json(changed=False, vm_configs=response)

if __name__ == '__main__':
  main()
