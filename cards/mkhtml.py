#!/usr/bin/env python

import argparse

from jinja2 import Environment, FileSystemLoader
import json

from mkqr import gen_qr_code
from cards import card
from pathlib import Path

parser = argparse.ArgumentParser(description='Generate HTML from template')
parser.add_argument("-i", "--input", type=str,
                    required=True, help="Input json file path")
parser.add_argument("-b", "--base-url", type=str,
                    required=True, help="Base URL in the QR code")
parser.add_argument("-t", "--template", type=str,
                    default="./template/cards.html.j2",
                    help="Template file path")
parser.add_argument("--horizontal", type=int, default=2,
                    help="How many cards listed in horizontal line")
parser.add_argument("-o", "--output", type=str,
                    required=True, help="Output html file directory")
parser.add_argument("-m", "--max-num", type=int, default=1000,
                    help="How many cards to print in one html files")
args = parser.parse_args()

# 1. Loads list of ids(secret_id, public_id) from json file
# 2. each 'ids', generate QR code using 'secret_id' and make a 'card' object
# 3. write HTML file using Jinja2 template

with open(args.input, 'r') as f:
    id_pairs = json.load(f)

cards = []
for id_pair in id_pairs:
    qr = gen_qr_code(args.base_url, id_pair['secret_id'])

    newcard = card(qr, id_pair['public_id'])
    cards.append(newcard)


def print_cards(cards, path):
    empty_card = card('', '')
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template(args.template)

    html = template.render({
        'cards': cards,
        'empty_card': empty_card,
        'horizontal': args.horizontal
    })
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)


def chunks(l, n):
    """
    This function is taken from Stack Overflow:
    https://stackoverflow.com/questions/312443
    Asked by jespern (https://stackoverflow.com/users/112415
    Answered by Ned Batchelder (https://stackoverflow.com/users/14343)

    Yield successive n-sized chunks from l.
    """
    for i in range(0, len(l), n):
        yield l[i:i + n]


outdir = Path(args.output)
for i, chunk in enumerate(chunks(cards, args.max_num)):
    print_cards(chunk, outdir / f"cards{i}.html")
