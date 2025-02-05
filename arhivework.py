from pathlib import Path
import os
import subprocess
PATH = os.path.abspath(os.getcwd())

fix_name = []
si = subprocess.STARTUPINFO()
si.wShowWindow = subprocess.SW_HIDE
username = os.getlogin()


def unpack_fix_zip():
    fix_list = Path('FixDir').glob('*.zip')
    for fix in fix_list:
        subprocess.call(
            f'{PATH}/7Zip/7z.exe x -y {fix} -o"{PATH}/FixDir/unpacking"',
            startupinfo=si)


def unpack_fix_ais():
    fix_list = Path('FixDir').glob('*.zip')
    for fix in fix_list:
        subprocess.call(
            f'{PATH}/7Zip/7z.exe x -y {
                fix} -o"C:\Program Files (x86)\Ais3Prom\"',
            startupinfo=si)
    os.popen(
        'start "Indexation" "C:\Program Files (x86)\Ais3Prom\Client\CommonComponents.Catalog.IndexationUtility.exe"')


def create_sfx():
    subprocess.call(
        f'{PATH}/winrar/Rar.exe a -df -ep1 -sfx C:/Users/{
            username}/Desktop/Fix FixDir/unpacking/Client',
        startupinfo=si)
    subprocess.call(
        f'{PATH}/winrar/Rar.exe c C:/Users/{username}/Desktop/Fix.exe -zFixDir/scenario.txt',
        startupinfo=si)


def clean_directory():
    os.popen(f'del {PATH}\FixDir\*.zip')


if __name__ == '__main__':

    unpack_fix_zip()
    create_sfx()
