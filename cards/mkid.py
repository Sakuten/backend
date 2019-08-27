#!/usr/bin/env python

import argparse

from id import generate_ids, save_id_json_file

parser = argparse.ArgumentParser(description='Generate Id list')
parser.add_argument("-a", "--admin", type=int, default=1,
                    help="The number of IDs for admin")
parser.add_argument("-c", "--checkers", type=int, required=True,
                    help="The number of IDs for checkers")
parser.add_argument("-s", "--students", type=int, required=True,
                    help="The number of IDs for students")
parser.add_argument("-v", "--visitors", type=int, required=True,
                    help="The number of IDs for visitors")
parser.add_argument("-o", "--output", type=str, required=True,
                    help="Output id list path")
args = parser.parse_args()

id_list = generate_ids(args.admin,
                       args.checkers,
                       args.students,
                       args.visitors)
save_id_json_file(args.output, id_list)
