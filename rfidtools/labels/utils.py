import re
import csv
import os
from datetime import datetime

import pyodbc as db

from rfidtools import DB_SERVER, DB_TABLE, DB_USER, DB_PASS

PRINT_LOGS_PATH = 'C:\\Print_Logs\\'
PRINT_ARCHIVES_PATH = 'C:\\Print_Archives\\'

# SQL connection
sql_connection = f'Driver={{ODBC Driver 18 for SQL Server}};Server={DB_SERVER};Database={DB_TABLE};UID={DB_USER};PWD={DB_PASS};Encrypt=no'


def listlogs(type) -> list:
    if type not in {'porcelain', 'slabs'}:
        print('Something went very wrong.\nInvalid type argument, object has impossible name.')
        raise TypeError

    os.chdir(PRINT_LOGS_PATH)
    logs = os.listdir()

    return [log for log in logs if re.search(f'^{type}_[0-9]*.txt', log) or re.search(f'^{type}_nf_[0-9]*.txt', log)]


def rmlog(log) -> bool:
    try:
        os.remove(PRINT_LOGS_PATH + log)
        return True

    except Exception as e:
        print('File may not be found, or connection is bad.\n' + str(e))
        return False


def parse_log(type, log, bin) -> list[tuple]:
    data = list()

    if type == 'porcelain':
        def label(row) -> tuple:
            return (
                row['rfid'],  # ProductTagID
                211,  # WarehouseCode
                'Recieved',  # Status
                datetimestamp,  # ReceivedDateTimeStamp
                'script',  # CreatedBy
                bin,  # Bin
                bytearray.fromhex(row['rfid']).decode(),  # ProductTagName
                row['code'])  # ProductCode

    elif type == 'slabs':
        def label(row) -> tuple:
            return (
                row['code'] + '-' + row['lot'] + row['serial'],  # Barcode
                row['rfid'],  # TagID
                row['code'],  # ProductCode
                row['lot'],  # BlockNumber
                row['serial'].strip('-'),  # SlabNumber
                row['dim_x'],  # Length
                row['dim_y'],  # Width
                211,  # WarehouseCode
                bin,  # LocationCode
                2,  # StatusID
                datetimestamp)  # ReceivedDateTimeStamp

    else:
        print('Something went very wrong.\nInvalid type argument, object has impossible name.')
        raise TypeError

    datetimestamp = datetime.fromtimestamp(os.path.getctime(PRINT_LOGS_PATH + log))
    with os.open(PRINT_LOGS_PATH + log, mode='r') as csvfile:
        rows = csv.DictReader(csvfile, dialect='unix')
        for row in rows:
            data.append(label(row))

    return data


def read_log(log) -> list:
    with os.open(PRINT_LOGS_PATH + log, mode='r') as csvfile:
        csvfile.prefetch()
        reader = csv.reader(csvfile)
        data = list(reader)

    return data


def query(data, query) -> bool:
    connection = db.connect(sql_connection)
    cursor = connection.cursor()
    try:
        connection.autocommit = False
        cursor.fast_executemany = True
        cursor.executemany(query, data)

    except db.DatabaseError as err:
        print('Database Error: ' + str(err))
        connection.rollback()
        return False

    else:
        connection.commit()
        return True
    connection.close()


def archive(log) -> bool:
    try:
        os.rename(PRINT_LOGS_PATH + log, PRINT_ARCHIVES_PATH + log)

    except Exception as e:
        print('Something went wrong, logs were not archived.\n' + str(e))
        return False

    else:
        return True
