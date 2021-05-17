import re
import subprocess
from json import loads
from urllib import request
import locale
import argparse

ip4_regex = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
ip6_regex = re.compile(r'(\w{0,4}:\w{0,4}:\w{0,4}:\w{0,4}:\w{0,4}:\w{0,4})')


class ASResponse:
    def __init__(self, json: dict):
        self._parse(json)

    def _parse(self, data):
        self.ip = data.get('ip') or '--'
        self.city = data.get('city') or '--'
        self.hostname = data.get('hostname') or '--'
        self.country = data.get('country') or '--'
        if org := data.get('org'):
            self.AS, self.provider = org.split()[0], ' '.join(org.split()[1:])
        else:
            self.AS, self.provider = '--', '--'


class Output:
    _IP_LEN = 20
    _AS_LEN = 10
    _COUNTRY_CITY_LEN = 26

    def __init__(self):
        self._number = 1

    def print(self, ip: str, autonomous_sys: str, country: str, city: str, provider: str):
        if self._number == 1:
            self._print_header()
        country_city = f'{country}/{city}'
        data_string = f'{self._number}' + ' ' * (3 - len(str(self._number))) + \
                      ip + self._spaces(self._IP_LEN, len(ip)) + \
                      autonomous_sys + self._spaces(self._AS_LEN, len(autonomous_sys)) + \
                      country_city + self._spaces(self._COUNTRY_CITY_LEN, len(country_city)) + provider
        self._number += 1
        print(data_string)
        print('-' * 100)

    def _print_header(self):
        print('№  IP' + self._spaces(self._IP_LEN, 2) + 'AS' + self._spaces(self._AS_LEN, 2) +
              'Country/City' + self._spaces(self._COUNTRY_CITY_LEN, 12) + 'Provider')
        print('-' * 100)

    @staticmethod
    def _spaces(expected: int, actual: int) -> str:
        return ' ' * (3 + (expected - actual))


def get_as_number_by_ip(ip) -> ASResponse:
    inf = loads(request.urlopen('https://ipinfo.io/' + ip + '/json').read())
    return ASResponse(inf)


def get_route(address: str, os_lang: dict[str, str]):
    tracert = subprocess.Popen(['tracert', address], stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
    end_ip = ""
    get_as = False
    output = Output()
    for line in iter(tracert.stdout.readline, ""):
        line = line.decode(encoding='cp866')
        if line.find(os_lang['invalid input']) != -1:
            print(line)
            break
        elif line.find(os_lang['tracing']) != -1:
            print(line, end='')
            end_ip = get_ip_from_line(line)
            print(end_ip)

        elif line.find(os_lang['max hops']) != -1:
            get_as = True
        elif line.find(os_lang['host unreachable']) != -1:
            print(line.removeprefix(' '))
            break
        elif line.find(os_lang['trace complete']) != -1:
            print(line)
            break

        try:
            ip = get_ip_from_line(line)
        except IndexError:
            continue
        if get_as:
            response = get_as_number_by_ip(ip)
            output.print(response.ip, response.AS,
                         response.country, response.city, response.provider)
            if ip == end_ip:
                print('Трассировка завершена.')
                break


def get_ip_from_line(line):
    matches = ip4_regex.findall(line)
    if len(matches) != 0:
        return ip4_regex.findall(line)[-1]
    return ip6_regex.findall(line)[-1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Autonomous Systems tracert')
    parser.add_argument('address', type=str,
                        help='Destination to which utility traces route.')
    return parser.parse_args()


EN_STATE_TO_MESSAGE = {
    'invalid input': 'Unable to resolve',
    'tracing': 'Tracing route',
    'host unreachable': 'Destination Host Unreachable',
    'trace complete': 'Trace complete',
    'max hops': 'over a maximum of'
}

RU_STATE_TO_MESSAGE = {
    'invalid input': 'Не удается разрешить системное имя узла',
    'tracing': 'Трассировка маршрута',
    'host unreachable': 'Заданный узел недоступен.',
    'trace complete': 'Трассировка завершена',
    'max hops': 'с максимальным числом прыжков'
}

SYSTEM_MESSAGES = {
    'ru_RU': RU_STATE_TO_MESSAGE,
    'en_EN': EN_STATE_TO_MESSAGE
}

if __name__ == '__main__':
    site = parse_args()
    lang = locale.getdefaultlocale()[0]
    if not SYSTEM_MESSAGES.get(lang):
        print('please enter your cmd lang [ru, en]')
        lang = 'ru_RU' if 'ru' in input() else 'en_EN'
    get_route(site.address, SYSTEM_MESSAGES[lang])
