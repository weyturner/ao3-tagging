#!/usr/bin/env python3
#
# Collect web pages containing index of stories from Archive of Our Own.
# These are a series of numbered web pages in response to a search for a
# tag.
#
# Copyright © Wey Turner, 2022.
# SPDX-License-Identifier: GPL-2.0-only

import argparse
from bs4 import BeautifulSoup
import datetime
import requests
import sys
import time
import yaml

# Headers to supply with a HTTP GET.
http_headers = { 'User-Agent':
                 'data collection for honours thesis <ao3@gdt.id.au>/1.0.0' }

# Convert a tag to a AO3 URL.
#   This does AO3 escaping, replacing / with *s*.
#   This does not do URL escaping, that's left to the 'requests' module.
def ao3_tag_to_url(tag):
    return 'https://archiveofourown.org/tags/{}/works'.format(tag.replace('/', '*s*'))

def ao3_tag_page_num_to_url(tag, page_num):
    return ao3_tag_to_url(tag) + '?page={}'.format(page_num)

# From this phrase within a naviagation bar of pages
#   <li>
#     <a href="/tags/Star%20Trek:%20Deep%20Space%20Nine/works?page=515">
#       515
#     </a>
#   </li>
# return the page number in that item in the navigation bar.
# If no page number if found, return 0.
def parse_pagenav(pagenav):
    try:
        page_num = int(pagenav.a.contents[0])
    except AttributeError:
        # No <a></a> tags.
        page_num = 0
    except ValueError:
        # No number within the <a>...</a> tags.
        page_num = 0
    return page_num


# Find the highest page mentioned in the page navination bar.
# If there's no number, return 1 (there's at least the page we were given
# to parse).
# The page navigation bar looks like this HTML:
# <ol aria-label="Pagination"
#     class="pagination actions"
#     role="navigation"
#     title="pagination">
#   <li class="previous"
#       title="previous">
#     <span class="disabled">
#       ← Previous
#     </span>
#   </li>
#   <li>
#     <span class="current">
#       1
#     </span>
#   </li>
#   <li>
#     <a href="/tags/Star%20Trek:%20Deep%20Space%20Nine/works?page=2"
#        rel="next">
#       2
#     </a>
#   </li>
#   <li>
#     <a href="/tags/Star%20Trek:%20Deep%20Space%20Nine/works?page=3">
#       3
#     </a>
#   </li>
#   <!-- ... -->
#   <li class="gap">
#     …
#   </li>
#   <li>
#     <a href="/tags/Star%20Trek:%20Deep%20Space%20Nine/works?page=515">
#       515
#     </a>
#   </li>
#   <li>
#     <a href="/tags/Star%20Trek:%20Deep%20Space%20Nine/works?page=516">
#       516
#     </a>
#   </li>
#   <li class="next" title="next">
#     <a href="/tags/Star%20Trek:%20Deep%20Space%20Nine/works?page=2"
#        rel="next">
#       Next →
#     </a>
#   </li>
# </ol>
def parse_highest_pagenav(pagenavs):
    highest = 1
    for pagenav in pagenavs.find_all('li'):
        highest = max(parse_pagenav(pagenav),
                      highest)
    return highest


# Alter a AO3 tag enough to be part of a filename without causing dramas
# (eg, not using the directory separator '/' or the matching character '*').
def file_name_safe_tag(tag):
    tag = tag.lower()
    tag = tag.replace('/', '-')
    tag = tag.replace(' ', '-')
    tag = tag.replace('*', '-')
    tag = tag.replace('?', '-')
    tag = tag.replace(':', '-')
    tag = tag.replace('--', '-')
    tag = tag.strip('-')
    return tag


# The majority of the output filename.
def file_name_base(out_prefix, tag, time_stamp, page_num):
    return out_prefix + file_name_safe_tag(tag) + '-' + time_stamp.strftime('%Y%m%d-%H%M%S-') + str(page_num).zfill(4)


# The output filename of the index pages.
def file_name_html(out_prefix, tag, time_stamp, page_num):
    print('File: {}'.format(file_name_base(out_prefix, tag, time_stamp, page_num)))
    return file_name_base(out_prefix, tag, time_stamp, page_num) + '-index.html'


# The output filename of the metadata about how we collected the index pages.
def file_name_meta(out_prefix, tag, time_stamp, page_num):
    return file_name_base(out_prefix, tag, time_stamp, page_num) + '-meta.yaml'


# Don't be blocked by the AO3 servers for over-use.
def rate_limit(pages_per_minute):
    if pages_per_minute > 0:
        wait = (60 / float(pages_per_minute))
        print('wait: {}'.format(wait))
        time.sleep(60 / float(pages_per_minute))


# Collect command line arguments.
def command_line_args():
    ap = argparse.ArgumentParser(description='Collect index pages from ' +
                                             'An Archive of Our Own ' +
                                 '<https://archiveofourown.org/>',
                                 epilog='Copyright © Wey Turner, 2022. ' +
                                        'License <https://spdx.org/licenses/' +
                                        'GPL-2.0-only.html>')
    ap.add_argument('-i',
                    '--infile',
                    type=str,
                    help='Filename of input containing a AO3 HTML page ' +
                         '(handy for testing)')
    ap.add_argument('-o',
                    '--outprefix',
                    type=str,
                    default='',
                    help='Prefix for output filenames')
    ap.add_argument('-r',
                    '--rate-limit',
                    type=int,
                    default=6,
                    help='Maximum number of web pages fetched per minute ' +
                         '(use 0 for no rate-limiting)')
    ap.add_argument('-t',
                    '--tag',
                    type=str,
                    default='Star Trek: Deep Space Nine',
                    help='Tag to present to AO3 website to subset works')
    return ap.parse_args()

if __name__ == "__main__":

    args = command_line_args()

    # Read web page into 'page': from either the AO3 website with
    # topic 'tag'; or from 'infile' with a saved HTML page for
    # testing.
    if args.infile:
        with open(args.infile) as f:
            page = f.read()
    else:
        url = ao3_tag_to_url(args.tag)
        print(url)
        r = requests.get(url,
                         headers=http_headers)
        if r.status_code == 200:
            page = r.text
        else:
            raise Exception('GET {} failed with HTTP status code {}' +
                            ''.format(url,
                                      r.status_code))

    # Parse webpage into normalised HTML.
    page_soup = BeautifulSoup(page,
                              'html.parser')

    # Find page naviation. That looks like:
    #  <ol class="pagination actions">
    pagenavs = page_soup.find('ol', class_='pagination')
    highest_pagenav = parse_highest_pagenav(pagenavs)
    print('{} pages'.format(highest_pagenav))

    # Collect each webpage of the index of works matching a tag.
    run_datetime = datetime.datetime.now()
    for page_num in range(1, highest_pagenav+1):
        meta = {}

        rate_limit(args.rate_limit)

        # Get the web page.
        meta['get_start_datetime'] = datetime.datetime.now()
        url = ao3_tag_page_num_to_url(args.tag,
                                      page_num)
        print('Page {}: {}'.format(page_num, url))
        r = requests.get(url,
                         headers=http_headers)
        if r.status_code == 200:
            page = r.text
        else:
            page = ''
        meta['get_end_datetime'] = datetime.datetime.now()

        # Save the web page.
        with open(file_name_html(args.outprefix,
                                 args.tag,
                                 run_datetime,
                                 page_num),
                  'w') as html_f:
            html_f.write(page)

        # Save the information about the web page.
        meta['tag'] = args.tag
        meta['run_datetime'] = str(run_datetime)
        meta['url'] = url
        meta['status_code'] = r.status_code
        meta['rate_limit'] = args.rate_limit
        with open(file_name_meta(args.outprefix,
                                 args.tag,
                                 run_datetime,
                                 page_num),
                  'w') as meta_f:
            yaml.dump(meta, meta_f)
