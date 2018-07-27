#!/usr/bin/env python

import argparse

from id import generate_ids, save_id_json_file

parser = argparse.ArgumentParser(description='Generate Id list')
parser.add_argument("-n", "--number", type=int,
                    required=True, help="The number of ids to generate (actually +1 output with admin)")
parser.add_argument("-o", "--output", type=str,
                    required=True, help="Output id list path")
args = parser.parse_args()

id_list = generate_ids(args.number + 1)
id_list[-1]['authority'] = 'admin'
save_id_json_file(args.output, id_list)
