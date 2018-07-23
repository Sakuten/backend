#!/usr/bin/env python

from jinja2 import Environment, FileSystemLoader
import json

from mkqr import gen_qr_code
from cards import card
from config import *


# 1. Loads list of ids(secret_id, public_id) from json file
# 2. each 'ids', generate QR code using 'secret_id' and make a 'card' object
# 3. write HTML file using Jinja2 template

with open(target_path, 'r') as f:
    id_pairs = json.load(f)


qr_pathes = []
cards = []
for id_pair in id_pairs:
    qr = gen_qr_code(base_url, id_pair['secret_id'])
    qr_pathes.append(qr)

    newcard = card(qr, id_pair['public_id'])
    cards.append(newcard)


empty_card = card('','')
env = Environment(loader=FileSystemLoader('./template'))
template = env.get_template('cards.html.j2')

html = template.render({'cards':cards, 'empty_card': empty_card, 'horizontal': horizontal})
with open('cards.html', 'w') as f:
    f.write(html)
