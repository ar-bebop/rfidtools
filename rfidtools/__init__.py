from pathlib import Path

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

config_path = Path(__file__).parent.joinpath('config.yaml')
with open(config_path) as config_file:
    config = yaml.load(config_file, Loader=yaml.Loader)

    DB_SERVER = config['DB']['server']
    DB_TABLE = config['DB']['table']
    DB_USER = config['DB']['user']
    DB_PASS = config['DB']['pass']

    SSH_SERVER = config['SSH']['server']
    SSH_USER = config['SSH']['user']
    SSH_PASS = config['SSH']['pass']
    SSH_LOGS_PATH = config['SSH']['logs-path']
    SSH_ARCHIVES_PATH = config['SSH']['archives-path']
