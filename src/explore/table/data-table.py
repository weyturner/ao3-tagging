#!/usr/bin/env python3
#
# Table containing variables from the data
#
# Run with
#   src/explore/table/data-table.py  \
#     -i data/database/20220612.yaml  \
#     title author
# where the fields can be pretty much any field in the YAML database
# (type "less data/database/20220612.yaml" to see the database)
#
# If the analysis software likes or doesn't like headers with the variable
# names in the first line of the CSV file, see the --header or --no-header
# option.
#
# Bugs:
#  - variables which are lists are written in an unhelpful format
#
# Copyright © Wey Turner, 2022.
# SPDX-License-Identifier: GPL-2.0-only

import argparse
import collections
import csv
import yaml

def command_line_args():
    ap = argparse.ArgumentParser(description='Create data table',
                                 epilog='Copyright © Wey Turner, 2022. ' +
                                        'License <https://spdx.org/licenses/' +
                                        'GPL-2.0-only.html>')
    ap.add_argument('-i',
                    '--input-database',
                    type=str,
                    required=True,
                    help='Database to load')
    ap.add_argument('--header',
                    default=True,
                    action=argparse.BooleanOptionalAction,
                    help='Header line with variable names')
    ap.add_argument('-o',
                    '--output-csv',
                    type=str,
                    help='Save as CSV file for other tools to use')

    ap.add_argument('fields',
                    type=str,
                    nargs='+',
                    help='Field name')

    return ap.parse_args()



if __name__ == "__main__":
    args = command_line_args()

    with open(args.input_database) as database_f:
        works_list = yaml.load(database_f,
                               Loader=yaml.SafeLoader)

    # Collect the fields from each work.
    rows = list()
    for work in works_list:
        d = list()
        for field in args.fields:
            try:
                d.append(work[field])
            except:
                d.append(None)
        rows.append(d)

    # Sort by first field
    rows.sort(key = lambda x:x[0])

    if args.output_csv:
        with open(args.output_csv, 'w', newline='', encoding='utf-8') as csv_f:
            csv_w = csv.writer(csv_f)
            if args.header:
                csv_w.writerow(args.fields)
            csv_w.writerows(rows)
    else:
        if args.header:
            print(args.fields)
        for r in rows:
            print(r)
