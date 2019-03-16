#!/usr/bin/env python3
import sys
import os
sys.path.append(os.getcwd())  # noqa: E402
from cards.id import load_id_json_file
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from pathlib import Path
import json
# typehints imports {{{
from typing import Optional, Dict
# }}}


class client():
    def get(self, _url: str, _json: Optional[Dict] = None,
            follow_redirects: bool = False, headers: Optional[Dict] = None)\
            -> Optional[Dict]:
        default_headers = {"Content-Type": "application/json"}
        if headers:
            default_headers.update(headers)
        json_data = json.dumps(_json).encode("utf-8") if _json else None

        url = f'http://localhost:8888{_url}'
        request = Request(url, data=json_data,
                          headers=default_headers, method='GET')
        try:
            response = urlopen(request)
        except HTTPError as e:
            print(e.read().decode(), file=sys.stderr)
            sys.exit(-1)
        else:
            response_body = response.read().decode("utf-8")
            response.close()
            return json.loads(response_body)

    def post(self, _url: str, _json: Optional[Dict] = None,
             follow_redirects: bool = False, headers: Optional[Dict] = None) \
            -> Optional[Dict]:
        default_headers = {"Content-Type": "application/json"}
        if headers:
            default_headers.update(headers)
        json_data = json.dumps(_json).encode("utf-8") if _json else None
        url = f'http://localhost:8888{_url}'
        request = Request(url, data=json_data,
                          headers=default_headers, method='POST')

        try:
            response = urlopen(request)
        except HTTPError as e:
            print(e.read().decode(), file=sys.stderr)
            sys.exit(-1)
        else:
            response_body = response.read().decode("utf-8")
            response.close()
            return json.loads(response_body)


def login(client: client, secret_id: int, rresp: str) -> Optional[Dict]:
    return client.post('/auth', _json={
        "id": secret_id,
        "g-recaptcha-response": rresp
    }, follow_redirects=True)


client = client()


id_list = load_id_json_file(Path(__file__).parent.parent /
                            Path('cards/test_users.json'))
admin = next(i for i in id_list if i['authority'] == 'admin')

token = login(client, admin["secret_id"], '')["token"]
client.post('/draw_all', headers={"Authorization": f'Bearer {token}'})
