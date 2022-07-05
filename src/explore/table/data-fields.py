#!/usr/bin/env python3
#
# List all the fieldnames in the database
#
# Run with
#
#   src/explore/table/data-fields.py -i data/database/20220612.yaml
#
# This can also be used in conjunction to export everything
#
#   src/explore/table/data-table.py -i data/database/20220612.yaml  \
#   `src/explore/table/data-fields.py -i data/database/20220612.yaml`
#
# Copyright © Wey Turner, 2022.
# SPDX-License-Identifier: GPL-2.0-only

import argparse
import collections
import csv
import yaml


def command_line_args():
    ap = argparse.ArgumentParser(description='Collect field names',
                                 epilog='Copyright © Wey Turner, 2022. ' +
                                        'License <https://spdx.org/licenses/' +
                                        'GPL-2.0-only.html>')
    ap.add_argument('-i',
                    '--input-database',
                    type=str,
                    required=True,
                    help='Database to load')
    return ap.parse_args()


if __name__ == "__main__":
    args = command_line_args()

    with open(args.input_database) as database_f:
        works_list = yaml.load(database_f,
                               Loader=yaml.SafeLoader)

    # Collect the fields from each work.
    fields = set()
    for work in works_list:
        for fieldname in work:
            fields.add(fieldname)
    print(*sorted(fields), sep=' ')
