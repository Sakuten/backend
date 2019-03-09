#
# draw script
#
# This script is standalone, which is not depends on
# any other modules in this project
# Also this is intended to be run not in virtualenv
# but in systemd-timer or cron, etc...

import json
import sys
import argparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import hashlib
# typehints imports {{{
from typehint import Dict, Optional
# }}}

parser = argparse.ArgumentParser(
    description='Draw currently available lotteries')
parser.add_argument("-l", "--list", type=str,
                    required=True, help="ID list json file path")
parser.add_argument("-a", "--host", type=str,
                    default="localhost", help="API hostname")
parser.add_argument("-p", "--protocol", type=str,
                    default="http", help="The protocol to use")
parser.add_argument("-y", "--yes", action='store_true',
                    help="Don't confirm before drawing")
args = parser.parse_args()

with open(args.list, 'r') as f:
    id_list = json.load(f)

# Take one 'admin' user from list
admin_ids = next(cred for cred in id_list if cred['authority'] == 'admin')


def post_json(path: str, data: Optional[Dict]=None, token: Optional[str]=None) -> Optional[Dict]:
    headers = {"Content-Type": "application/json"}
    if token:
        headers['Authorization'] = 'Bearer ' + token
    json_data = json.dumps(data).encode("utf-8") if data else None
    url = '{}://{}/{}'.format(args.protocol, args.host, path)
    request = Request(url, data=json_data,
                      headers=headers, method='POST')
    try:
        response = urlopen(request)
    except HTTPError as e:
        print('Error: {}'.format(e.read()), file=sys.stderr)
        sys.exit(-1)
    else:
        response_body = response.read().decode("utf-8")
        response.close()
        return json.loads(response_body)


with open(args.list, 'r') as f:
    local_checksum = hashlib.sha256(f.read().encode()).hexdigest()
    server_checksum = post_json('ids_hash')['sha256']
    if local_checksum != server_checksum:
        print('local ids.json is different from servers', file=sys.stderr)
        sys.exit(70)  # we should decide error code


# Login as admin
admin_cred = {
    'id': admin_ids['secret_id'],
    'g-recaptcha-response': ''
}

response = post_json('auth', admin_cred)
token = response['token']

if not args.yes:
    print('Attempt to draw lotteries.')
    print('Proceed? [ny] >', end='')
    ans = input()
    if ans != 'y':
        print('Abort.', file=sys.stderr)
        sys.exit(-1)

# POST /draw_all
response_draw = post_json('draw_all', None, token)

# Print the result
print(response_draw)
