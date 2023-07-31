from os import path

import yaml


global DB_SERVER
global DB_TABLE
global DB_USER
global DB_PASS

config_path = path.abspath(path.join(path.dirname(__file__), 'config.yaml'))
with open(config_path) as config_file:
    config = yaml.load(config_file, Loader=yaml.Loader)

    DB_SERVER = config['db']['server']
    DB_TABLE = config['db']['table']
    DB_USER = config['db']['user']
    DB_PASS = config['db']['pass']
