import os
import platform
import argparse
import PyInstaller.__main__ as build

from rfidtools.core import gui_loop

PATH = os.path.dirname(os.path.realpath(__file__))

# Run from command line using the build option (-b, --build) to build an exe.
# WARNING: Windows will for some reason flag any built .exe using pyInstaller as a virus, this is a false positive, please allow
parser = argparse.ArgumentParser(
    prog='rfidtools',
    description='Tool for RFID tag production at CIOT.',
    epilog='Use "python -m rfidtools" to run from the command line.')

parser.add_argument('-b', '--build-exe',
                    nargs=1,
                    required=False,
                    help='Build the program into an exe to be placed on the desktop.\nRequires an argument passing the relative path to a config.yaml')

args = vars(parser.parse_args())
BUILD = args['build_exe']

# if build option is not selected then run main GUI loop
if BUILD is None:
    gui_loop()

else:
    if platform.system() == 'Windows':
        desktop = os.environ['USERPROFILE'] + '\\Desktop'
        build.run([
            f'{PATH}\\__main__.py',
            '-F',
            f'--distpath={desktop}',
            f'--add-data={BUILD[0]};rfidtools',
            '--name=RFID_Tools',
            '--windowed',
            f'--icon={PATH}\\RFID_Icon.ico'])

    else:
        print('Building to .exe is only supported on Windows.')
        raise SystemError
