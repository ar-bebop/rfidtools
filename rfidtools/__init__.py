from os import path

import yaml


global DB_SERVER
global DB_TABLE
global DB_USER
global DB_PASS

global SSH_SERVER
global SSH_USER
global SSH_PASS
global SSH_LOGS_PATH
global SSH_ARCHIVES_PATH

config_path = path.abspath(path.join(path.dirname(__file__), 'config.yaml'))
with open(config_path) as config_file:
    config = yaml.load(config_file, Loader=yaml.Loader)

    DB_SERVER = config['db']['server']
    DB_TABLE = config['db']['table']
    DB_USER = config['db']['user']
    DB_PASS = config['db']['pass']

    SSH_SERVER = config['ssh']['server']
    SSH_USER = config['ssh']['user']
    SSH_PASS = config['ssh']['pass']
    SSH_LOGS_PATH = config['ssh']['logs-path']
    SSH_ARCHIVES_PATH = config['ssh']['archives-path']
