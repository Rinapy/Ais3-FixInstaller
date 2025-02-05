import requests
from exceptions import LoginError
from bs4 import BeautifulSoup
import re
import subprocess


def login(
    username: str,
    password: str
) -> tuple[
    requests.Response,
    requests.cookies.RequestsCookieJar
]:
    url = 'https://support.tax.nalog.ru/knowledge_base/?login=yes'
    headers = {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/112.0.0.0 YaBrowser/23.5.2.625 '
            'Yowser/2.5 Safari/537.36'
        )
    }
    session = requests.Session()
    data = {'backurl': '/',
            'AUTH_FORM': 'Y',
            'TYPE': 'AUTH',
            'USER_LOGIN': username,
            'USER_PASSWORD': password,
            'Login': 'Войти'}

    response = session.post(url, headers=headers, data=data, verify=False)
    if get_valid(response.text):
        return response, session.cookies
    raise LoginError


def get_valid(response: str) -> bool:
    soup = BeautifulSoup(response, 'lxml')
    form = soup.find('form', attrs={'name': 'system_auth_form6zOYVN'})
    if form is None:
        return True
    return False


def parse_fix(response: str) -> dict:
    soup = BeautifulSoup(response, 'lxml')
    fix_dict = {}
    version = get_install_version()
    if version == 'отсутствует':
        pattern = re.compile(r"[\w'._+-]+_[\w'._+-]+_")
    else:
        pattern = re.compile(rf"[\w'._+-]+_{version}+_")
    for fix_name in soup.find_all(
        'a',
        class_='list-group-item__link',
        href=True,
        limit=60
    ):
        if pattern.match(fix_name.text.replace('\t', '').replace('\n', '')):
            fix_dict[fix_name.text.replace('\t', '').replace(
                '\n', '')] = 'https://support.tax.nalog.ru' + fix_name['href']
    return fix_dict


def get_install_version() -> str:
    try:
        with open(
            'C:/Program Files (x86)/Ais3Prom/Client/version.txt',
            'r'
        ) as file:
            version = file.readline()
    except Exception:
        return 'отсутствует'
    return version


def kill_ais_process() -> None:
    si = subprocess.STARTUPINFO()
    si.wShowWindow = subprocess.SW_HIDE
    subprocess.call(
        'taskkill /im "CommonComponents.UserAgent.exe"',
        startupinfo=si
    )
    subprocess.call(
        'taskkill /im "CommonComponents.UnifiedClient.exe"',
        startupinfo=si
    )


def download_fixs(fix_name_list, fix_dict, cookies) -> None:
    for fix_name in fix_name_list:
        arhive = requests.get(
            fix_dict[fix_name], verify=False, cookies=cookies)
        with open(f'FixDir/{fix_name}.zip', 'wb') as code:
            code.write(arhive.content)


if __name__ == '__main__':
    pass
