import concurrent.futures
import logging
import socket

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
