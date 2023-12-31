import re
import csv
from datetime import datetime

import pyodbc as db
from fabric import Connection
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from rfidtools import DB_SERVER, DB_TABLE, DB_USER, DB_PASS
from rfidtools import SSH_SERVER, SSH_USER, SSH_PASS, SSH_LOGS_PATH, SSH_ARCHIVES_PATH

PRINT_LOGS_PATH = SSH_LOGS_PATH
PRINT_ARCHIVES_PATH = SSH_ARCHIVES_PATH

# SQL connection
sql_connection = f'Driver={{ODBC Driver 18 for SQL Server}};Server={DB_SERVER};Database={DB_TABLE};UID={DB_USER};PWD={DB_PASS};Encrypt=no'

# SSH connection
ssh_kwargs = {'host': SSH_SERVER, 'user': SSH_USER, 'connect_timeout': 10, 'connect_kwargs': {'password': SSH_PASS}}


def listlogs(type) -> list:
    """
    get the logs found for specific type

    :param type: type of logs. Porcelain OR Slabs. Type is passed from object.
    :return: list of strings, each string is the file name of a log.
    """
    if type not in {'porcelain', 'slabs'}:
        print('Something went very wrong.\nInvalid type argument, object has impossible name.')
        raise TypeError

    with Connection(**ssh_kwargs) as c, c.sftp() as sftp:
        sftp.chdir(PRINT_LOGS_PATH)
        logs = sftp.listdir()

    return [log for log in logs if re.search(f'^{type}_[0-9]*.txt', log) or re.search(f'^{type}_nf_[0-9]*.txt', log)]


def rmlog(log) -> bool:
    """
    remove specific log

    :param log: string of file name for log to be removed.
    :return: whether operation was succesful or not, true for success, false for error.
    """
    try:
        with Connection(**ssh_kwargs) as c, c.sftp() as sftp:
            sftp.remove(PRINT_LOGS_PATH + log)
        return True

    except Exception as e:
        print('File may not be found, or connection is bad.\n' + str(e))
        return False


def parse_log(type, log, bin) -> list[tuple]:
    """
    parse log based on type, list of rows as tuple is returned

    :param type: type of log, Porcelain OR Slabs.
    :param log: file name of log to parse.
    :param bin: bin to be assigned to labels in log.
    :return: list of tuples, each tuple is one row of data to insert into DB.
    """
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

    with Connection(**ssh_kwargs) as c, c.sftp() as sftp:
        datetimestamp = datetime.fromtimestamp(sftp.stat(PRINT_LOGS_PATH + log).st_mtime)
        with sftp.open(PRINT_LOGS_PATH + log, mode='r') as csvfile:
            csvfile.prefetch()
            rows = csv.DictReader(csvfile, dialect='unix')
            for row in rows:
                data.append(label(row))

    return data


def read_log(log) -> list:
    """
    read log for viewing

    :param log: file name of log to read.
    :return: list of data from csv file to be read.
    """
    with Connection(**ssh_kwargs) as c, c.sftp() as sftp:
        with sftp.open(PRINT_LOGS_PATH + log, mode='r') as csvfile:
            csvfile.prefetch()
            reader = csv.reader(csvfile)
            data = list(reader)

    return data


def send_print(type, payload) -> bool:
    """
    send print request through headless browser. (This was very hacky)

    :param type: type of print to be sent
    :param payload: data to be printed on label
    :return: exit status, true for success, false for error.
    """
    if type == 'porcelain':
        url = 'http://192.168.2.67:8080/bartender/print/rfid_templates/porcelain_nf.btw?'
        for key, value in payload.items():
            if isinstance(value, str) is str:
                value = value.replace(' ', '%20')

            url += f'{key}={value}&'
        url = url[:-1]

    elif type == 'slabs':
        url = 'http://192.168.2.67:8080/bartender/print/rfid_templates/slabs_nf.btw?'
        for key, value in payload.items():
            if isinstance(value, str) is str:
                value = value.replace(' ', '%20')

            url += f'{key}={value}&'
        url = url[:-1]

    else:
        print('Something went very wrong.\nInvalid type argument, object has impossible name.')
        raise TypeError
        return False

    opts = Options()
    opts.add_argument('--headless')
    driver = webdriver.Chrome(options=opts)
    try:
        driver.get(url)

    except Exception as e:
        print('Something went wrong with the browser automation.\nMaybe chrome isn\'t installed?\n' + str(e))
        return False
    driver.close()

    return True


def query(data, query) -> bool:
    """
    send SQL query to DB, currently only used for inserts

    :param data: data to be sent with query.
    :param query: SQL query to be used.
    :return: exit status, true for success, false for error.
    """
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
    """
    move log to archive folder

    :param log: file name of log to be archived.
    :return: exit status, true for success, false for error.
    """
    try:
        with Connection(**ssh_kwargs) as c:
            c.run(f'mv {PRINT_LOGS_PATH}{log} {PRINT_ARCHIVES_PATH}{log}')

    except Exception as e:
        print('Something went wrong, logs were not archived.\n' + str(e))
        return False

    else:
        return True
