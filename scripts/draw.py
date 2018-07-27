#
# draw script
#
# This script is standalone, which is not depends on
# any other modules in this project
# Also this is intended to be run not in virtualenv
# but in systemd-timer or cron, etc...

import json
import argparse
from urllib.request import Request, urlopen

parser = argparse.ArgumentParser(
    description='Draw currently available lotteries')
parser.add_argument("-l", "--list", type=str,
                    required=True, help="ID list json file path")
parser.add_argument("-h", "--host", type=str,
                    default="localhost", help="API hostname")
args = parser.parse_args()

with open(args.list, 'r') as f:
    id_list = json.load(f)

# Take one 'admin' user from list
admin_cred = next(cred for cred in id_list if cred['authority'] == 'admin')

# exclude 'authority' key & value from credential
admin_cred = {k: v for k, v in admin_cred.items() if k != 'authority'}


def post_json(url, data=None, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    json_data = json.dumps(data).encode("utf-8") if data else None
    request = Request(f'{args.host}/{url}', data=json_data,
                      headers=headers, method='POST')
    with urlopen(request) as response:
        response_body = response.read().decode("utf-8")
    return json.loads(response_body)


# Login as admin
response = post_json('/auth', admin_cred)
token = response['token']

# POST /draw_all
response_draw = post_json('/draw_all', None, token)

# Print the result
print(response_draw)
