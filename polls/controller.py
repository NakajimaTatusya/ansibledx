import os

from .models import Inventory


class ClearInventoryFiles:
  for filename in os.scandir('/home/ceansible/ce_dx_proj/auto-kitting/host_vars'):
    if filename.name.endswith('.yml'):
      os.unlink(filename)


class OutputInventoryFile:
    const_hosts = """---
  all:
    hosts:
    vars:
      ansible_connection: winrm
      ansible_port: 5985
      ansible_winrm_server_cert_validation: ignore
    children:
      win10_client_kitting:
        hosts:
"""

    const_vars = """---
  ansible_user: %s
  ansible_password: %s
...
"""

    rows = Inventory.objects.all()
    for row in rows:
        # hosts.yml ファイル用
        const_hosts += "          %s:\n" % row.hostname

        # host_varsファイル出力
        with open('/home/ceansible/ce_dx_proj/auto-kitting/host_vars/%s.yml' % row.hostname, 'w') as fhv:
          fhv.write(const_vars % (row.username, row.password))
    const_hosts += "..."

    # hosts.yml 書き出し    
    with open('/home/ceansible/ce_dx_proj/auto-kitting/products/hosts.yml', 'w') as fh:
        fh.write(const_hosts)
