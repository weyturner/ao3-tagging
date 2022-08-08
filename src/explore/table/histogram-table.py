#!/usr/bin/env python3
#
# Create frequency table from database.
#
# Run with
#   src/explore/table/histogram-table.py  \
#     -i data/database/20220612.yaml  \
#     relationshipspaxslash
# where the field can be pretty much any field in the YAML database
# (type "less data/database/20220612.yaml" to see the database)
#
# If the analysis software likes or doesn't like headers with the variable
# names in the first line of the CSV file, see the --header or --no-header
# option.
#
# Unlike data-table.py, this program handles lists within fields well.
#
# Copyright © Wey Turner, 2022.
# SPDX-License-Identifier: GPL-2.0-only

import argparse
import collections
import csv
import yaml

def command_line_args():
    ap = argparse.ArgumentParser(description='Create frequency table for histograms',
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
                    help='Header line with variable names')
    ap.add_argument('-o',
                    '--output-csv',
                    type=str,
                    help='Save as CSV file for other tools to use')
    ap.add_argument('field',
                    type=str,
                    help='Field name')
    return ap.parse_args()



if __name__ == "__main__":
    args = command_line_args()

    with open(args.input_database) as database_f:
        works_list = yaml.load(database_f,
                               Loader=yaml.SafeLoader)

    # Compute frequency of each pairing using the
    # very handy Counter type.
    count = collections.Counter()
    for works in works_list:
        try:
            # Work as expected with singleton fields
            # and list fields.
            if type(works[args.field]) is list:
                count.update(works[args.field])
            elif type(works[args.field]) is dict:
                count.update(works[args.field])
            else:
                # Count the works, not the glyphs within the work name.
                count.update({works[args.field]: 1})
        except KeyError:
            pass

    if args.output_csv:
        with open(args.output_csv, 'w', newline='', encoding='utf-8') as csv_f:
            csv_w = csv.writer(csv_f)
            # Title line with variable name
            if args.header:
                csv_w.writerow([args.field, 'Frequency'])
            # Dump the category and its frequency
            d = list()
            for p in count.most_common():
                d.append([p[0], p[1]])
            csv_w.writerows(d)
    else:
        if args.header:
            print('{:>6}  {}'.format('Freq', args.field))
        for p in count.most_common():
            print('{:>6}  {}'.format(p[1], p[0]))
