import concurrent.futures
import logging
import os
import socket
import yaml

from django.conf import settings
from .models import Inventory


def process_files(inventoryfile):
    """
    アップロードされたCSVデータをディクショナリー配列に
    """
    data = inventoryfile.read().decode("utf-8")
    lines = data.split("\r\n")
    dict = []
    lincnt = 0
    for line in lines:
        if lincnt == 0:
            # Header skip
            lincnt += 1
            continue
        else:
            logging.debug("row data = %s" % line)
            if line:
                fields = line.split(",")
                tmp = {
                    'orderno': fields[0],
                    'hostname': fields[1],
                    'username': fields[2],
                    'password': fields[3]
                }
                dict.append(tmp.copy())

    return dict


def get_ipaddreess_from_hostname(prow: dict) -> str:
    """
    CSVファイルから読み込んだホスト名を使用して、IPv4アドレスを取得する
    """
    _ipaddress = ""
    try:
        _ipaddress = socket.gethostbyname(prow["hostname"])
    except:
        _ipaddress = prow["hostname"]
        logging.exception("get host by %s error." % prow["hostname"])
    return _ipaddress


def write_into_csv(csv_data):
    """
    SQLite3のpolls_inventoryテーブルへDELETE、INSERTします
    """
    # 全部策徐
    Inventory.objects.all().delete()

    # 並列処理
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for hdict, _ipaddress in zip(csv_data, executor.map(get_ipaddreess_from_hostname, csv_data)):    
            new_row = Inventory(hostname=hdict['hostname'], ipaddress=_ipaddress, username=hdict['username'], password=hdict['password'], order_no=hdict['orderno'])
            new_row.save()

    # for row in csv_data:
    #     _ipaddress = ""
    #     try:
    #         _ipaddress = socket.gethostbyname(row['hostname'])
    #     except:
    #         _ipaddress = row['hostname']
    #         logging.exception("get host by %s error." % row['hostname'])

    return 'polls:InventoryList'


def load_yaml_file(filename: str) -> dict:
    with open(filename, "r") as yf:
        data = yaml.load(yf, Loader=yaml.SafeLoader)
    return data


def write_yaml_file(filename: str, data: dict) -> None:
    with open(filename, "w") as yf:
        yaml.dump(data, yf, default_flow_style=False)


def generate_individual_inventory(p_data: list, p_cmd_key_name="maintenance_command", p_flag_netbios=1) -> None:
    """
    メンテナンスコマンドを発行するためのInventoryキーワードを追加する
    args[0]:
    [
        {
            "hostname": hostname,
            "ipaddress": ipaddress
        },
        ...
    ]
    return value: None
    """
    inventory_data: dict = load_yaml_file(settings.ANSIBLE_HOSTS_FILE_PATH)
    # remove host from maintenance_command:hosts key.
    dict_hosts: dict = inventory_data["all"]["children"][p_cmd_key_name]["hosts"]
    for delkey in list(dict_hosts.keys()):
        removed_value = dict_hosts.pop(delkey)
    # add new host
    new_host: dict = {}
    for el in p_data:
        if p_flag_netbios == 1:
            new_host.update({el["hostname"]: None})
        else:
            new_host.update({el["ipaddress"]: None})
    inventory_data["all"]["children"][p_cmd_key_name]["hosts"] = new_host
    # write inventory file.
    write_yaml_file(settings.ANSIBLE_HOSTS_FILE_PATH, inventory_data)


def generate_kitting_inventory(p_kitting_key_name="win10_client_kitting", p_flag_netbios=1) -> None:
    """
    Inventoryテーブルからキッティング用ターゲット端末のInventoryファイルを作成する
    """
    inventory_data: dict = load_yaml_file(settings.ANSIBLE_HOSTS_FILE_PATH)
    # remove host from maintenance_command:hosts key.
    dict_hosts: dict = inventory_data["all"]["children"][p_kitting_key_name]["hosts"]
    for delkey in list(dict_hosts.keys()):
        removed_value = dict_hosts.pop(delkey)
    # add new host
    inventory_rows = Inventory.objects.all()
    new_host: dict = {}
    for row in inventory_rows:
        if p_flag_netbios == 1:
            new_host.update({row.hostname: None})
        else:
            new_host.update({row.ipaddress: None})
    inventory_data["all"]["children"][p_kitting_key_name]["hosts"] = new_host
    # write inventory file.
    write_yaml_file(settings.ANSIBLE_HOSTS_FILE_PATH, inventory_data)


def purge_host_variable_files() -> None:
    """
    ansible host 変数ファイルをすべて削除する
    """
    for filename in os.scandir(settings.ANSIBLE_HOST_VARS_FILE_DIR):
        if filename.name.endswith('.yml'):
            os.unlink(filename)


def generate_host_variable_files(p_flag_netbios=1) -> None:
    """
    host 変数ファイルを作成する
    """
    const_vars = """---
  ansible_user: %s
  ansible_password: %s
...
"""

    rows = Inventory.objects.all()
    for row in rows:
        if p_flag_netbios == 0:
            # host値にipaddressを使用したhost変数ファイルの出力
            with open(f'{settings.ANSIBLE_HOST_VARS_FILE_DIR}/{row.ipaddress}.yml', 'w') as fhv:
                fhv.write(const_vars % (row.username, row.password))
        else:
            # host値にhostnameを使用したhost変数ファイルの出力
            with open(f'{settings.ANSIBLE_HOST_VARS_FILE_DIR}/{row.hostname}.yml', 'w') as fhv:
                fhv.write(const_vars % (row.username, row.password))
