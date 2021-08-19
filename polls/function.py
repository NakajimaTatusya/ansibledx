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
                    'hostname': fields[0],
                    'username': fields[1],
                    'password': fields[2]
                }
                dict.append(tmp.copy())

    return dict


def write_into_csv(csv_data):
    """
    SQLite3のテーブルへDELETE、INSERTします
    """
    icnt = 1
    Inventory.objects.all().delete()
    for row in csv_data:
        _ipaddress = ""
        try:
            _ipaddress = socket.gethostbyname(row['hostname'])
        except:
            _ipaddress = row['hostname']
            logging.exception("get host by %s error." % row['hostname'])
        new_row = Inventory(hostname=row['hostname'], ipaddress=_ipaddress, username=row['username'], password=row['password'], order_no=icnt)
        new_row.save()
        icnt += 1

    return 'polls:InventoryList'
