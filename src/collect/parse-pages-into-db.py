#!/usr/bin/env python3
#
# Parse downloaded web pages from An Archive of Our Own into
# a YAML file which acts as a data base.
#
# This can be pretty slow, here's a run for 10324 works in 517 web pages
# on a computer running at 4400 BogoMIPS:
#   $ /usr/bin/time -v parse-pages-into-db.py ...
#   User time (seconds): 117.58
#   System time (seconds): 0.38
#   Percent of CPU this job got: 99%
#   Elapsed (wall clock) time (h:mm:ss or m:ss): 1:58.69
#   Maximum resident set size (kbytes): 250620
#   Major (requiring I/O) page faults: 6
#   Minor (reclaiming a frame) page faults: 164155
#   Voluntary context switches: 64
#   Involuntary context switches: 3888
#   Swaps: 0
#   File system inputs: 1864
#   File system outputs: 16632
#   Socket messages sent: 0
#   Socket messages received: 0
#   Signals delivered: 0
#   Page size (bytes): 4096
#   Exit status: 0
# If speed matters then there are abundant opportunities to improve that,
# this programmer chose clarity and simplcity of expression over speed to allow
# a tighter data science process.
#
# One of the tasks of this program is to make data normal and canonical.
#
# Normal. For example, "B,A" is transformed into Python lists of ['B',
# 'A'] rather than a 'list' of ['B,A']. Normalised formats allow the
# tools to work with the data without sophisticated mangling.
# Obviously the preferred 'normal form' varies by the programming
# tools used, although EF 'Ted' Codd set some general rules in 1970.
#
# Canonical. For example "B,A" transformed into a Python list of ['B',
# 'A'] is regular, but there is different list ['A', 'B'] with the
# same members. This ambiguity can lead to miscalculation; for
# example, imagine that half of the data is categoried as ['B', 'A']
# and half the data is categorised as ['A', 'B'], then statistics will
# miscalcuate membership of the set (A, B) by half.  By requiring a
# 'canonical form' we can ensure that the data "A,B" is expressed in
# only one way -- canonically. Mostly this program does that by
# sorting; in our example, the canonical form is the sorted list of
# ['A', 'B']; the form ['B', 'A'] is non-canonical, not permitted, and
# is corrected by altering the form to be in sorted order.
#
# Run as follows:
#
# cd ao3-tagging
# src/collect/parse-pages-into-db.py -o data/database/20220612.yaml data/raw/star-trek-deep-space-nine-20220601/*.html
#
# Copyright © Wey Turner, 2022.
# SPDX-License-Identifier: GPL-2.0-only

import argparse
from bs4 import BeautifulSoup
import datetime
import functools
import re
import yaml


# Table of AO3 language codes to ISO 639 language codes.
# Some of the AO3 language codes are right-to-left, some are complex
# scripts -- plenty of analysis tools won't cope with either.
# Where we can, use ISO 639-1; where we must, use the longer 639-2 then 639-3.
# As required Use dialet extensions (shown as lowercase) and script
# extensions (shown as Titlecase).
lang_ao3_to_iso = {
    '한국어':                'ko',
    'Čeština':              'cs',
    'Cymraeg':              'cy',
    'Deutsch':              'de',
    'English':              'en',
    'Español':              'es',
    'Français':             'fr',
    'Italiano':             'it',
    'Nederlands':           'nl',
    'Polski':               'pl',
    'Português brasileiro': 'pt-br',     # Brazilian dialect of Portugese.
    'tlhIngan-Hol':         'tlh-Latn',  # Klingon using Latin characters.
    'Русский':              'ru',
    'עברית':                 'he',        # RtL text, take care when changing.
    '中文-普通话 國語':        'zh-Hans',   # Mainland China Mandarin.
    '日本語':                'ja'
}


# https://stackoverflow.com/questions/5920643/add-an-item-between-each-item-already-in-the-list
def tween(seq, sep):
    return functools.reduce(lambda r,v: r+[sep,v], seq[1:], seq[:1])


# Collect command line arguments.
def command_line_args():
    ap = argparse.ArgumentParser(description='Parse index pages from ' +
                                             'An Archive of Our Own ' +
                                 '<https://archiveofourown.org/>',
                                 epilog='Copyright © Wey Turner, 2022. ' +
                                        'License <https://spdx.org/licenses/' +
                                        'GPL-2.0-only.html>')
    ap.add_argument('-i',
                    '--input-database',
                    type=str,
                    default='',
                    help='Database to load')
    ap.add_argument('-o',
                    '--output-database',
                    type=str,
                    required=True,
                    help='Database to create (required)')
    ap.add_argument('filename',
                    nargs='+',
                    help='Filenames of index pages from AO3 to load into ' +
                         'output database')
    return ap.parse_args()


# Parse a work from HTML into Python dict.
#
# For convenience here is some nicely-reformatted HTML for a work so
# that the excellently-described structure of the page can be plainly
# seen:
#
# <li class="work blurb group work-39026430 user-8795776"
#     id="work_39026430"
#     role="article">
#   <!--title, author, fandom-->
#   <div class="header module">
#     <h4 class="heading">
#       <a href="/works/39026430">
#         Gods in Ruins
#       </a>
#       by
#       <!-- do not cache -->
#       <a href="/users/Arati_Mhevet/pseuds/Arati_Mhevet" rel="author">
#         Arati_Mhevet
#       </a>
#     </h4>
#     <h5 class="fandoms heading">
#       <span class="landmark">
#         Fandoms:
#       </span>
#       <a class="tag"
#          href="/tags/Star%20Trek:%20Deep%20Space%20Nine/works">
#         Star Trek: Deep Space Nine
#       </a>
#     </h5>
#     <!--required tags-->
#     <ul class="required-tags">
#       <li>
#         <a aria-controls="#modal"
#            class="help symbol question modal"
#            href="/help/symbols-key.html" title="Symbols key">
#           <span class="rating-general-audience rating"
#                 title="General Audiences">
#             <span class="text">
#               General Audiences
#             </span>
#           </span>
#         </a>
#       </li>
#       <li>
#         <a aria-controls="#modal"
#            class="help symbol question modal"
#            href="/help/symbols-key.html" title="Symbols key">
#           <span class="warning-no warnings"
#                 title="No Archive Warnings Apply">
#             <span class="text">
#               No Archive Warnings Apply
#             </span>
#           </span>
#         </a>
#       </li>
#       <li>
#         <a aria-controls="#modal" class="help symbol question modal"
#            href="/help/symbols-key.html"
#            title="Symbols key">
#           <span class="category-gen category"
#                 title="Gen">
#             <span class="text">
#               Gen
#             </span>
#           </span>
#         </a>
#       </li>
#       <li>
#         <a aria-controls="#modal"
#            class="help symbol question modal"
#            href="/help/symbols-key.html"
#            title="Symbols key">
#           <span class="complete-yes iswip"
#                 title="Complete Work">
#             <span class="text">
#               Complete Work
#             </span>
#           </span>
#         </a>
#       </li>
#     </ul>
#     <p class="datetime">
#       17 May 2022
#     </p>
#   </div>
#   <!--warnings again, cast, freeform tags-->
#   <h6 class="landmark heading">
#     Tags
#   </h6>
#   <ul class="tags commas">
#     <li class="warnings">
#       <strong>
#         <a class="tag"
#            href="/tags/No%20Archive%20Warnings%20Apply/works">
#           No Archive Warnings Apply
#         </a>
#       </strong>
#     </li>
#     <li class="relationships">
#       <a class="tag"
#          href="/tags/Julian%20Bashir*s*Elim%20Garak/works">
#         Julian Bashir/Elim Garak
#       </a>
#     </li>
#     <li class="relationships">
#       <a class="tag"
#          href="/tags/Elim%20Garak*s*Cardassia/works">
#         Elim Garak/Cardassia
#       </a>
#     </li>
#     <li class="relationships">
#       <a class="tag"
#          href="/tags/Elim%20Garak%20*a*%20Enabran%20Tain/works">
#         Elim Garak &amp; Enabran Tain
#       </a>
#     </li>
#     <li class="characters">
#       <a class="tag"
#          href="/tags/Elim%20Garak/works">
#         Elim Garak
#       </a>
#     </li>
#     <li class="characters">
#       <a class="tag"
#          href="/tags/Martok%20(Star%20Trek)/works">
#         Martok (Star Trek)
#       </a>
#     </li>
#     <li class="characters">
#       <a class="tag"
#          href="/tags/Enabran%20Tain/works">
#         Enabran Tain
#       </a>
#     </li>
#     <li class="characters">
#       <a class="tag"
#          href="/tags/Worf%20(Star%20Trek:TNG*s*DS9)/works">
#         Worf (Star Trek:TNG/DS9)
#       </a>
#     </li>
#     <li class="characters">
#       <a class="tag"
#          href="/tags/Julian%20Bashir/works">
#         Julian Bashir
#       </a>
#     </li>
#   </ul>
#   <!--summary-->
#   <h6 class="landmark heading">
#     Summary
#   </h6>
#   <blockquote class="userstuff summary">
#     <p>'A man is a god in ruins.' Martok and Garak, after ‘By
#       Inferno’s Light’.</p>
#   </blockquote>
#   <!--stats-->
#   <dl class="stats">
#     <dt class="language">
#       Language:
#     </dt>
#     <dd class="language">
#       English
#     </dd>
#     <dt class="words">
#       Words:
#     </dt>
#     <dd class="words">
#       1,297
#     </dd>
#     <dt class="chapters">
#       Chapters:
#     </dt>
#     <dd class="chapters">
#       <a href="/works/39026430/chapters/97673250">
#         2
#       </a>
#       /2
#     </dd>
#     <dt class="comments">
#       Comments:
#     </dt>
#     <dd class="comments">
#       <a href="/works/39026430?show_comments=true&amp;view_full_work=true#comments">
#         9
#       </a>
#     </dd>
#     <dt class="kudos">
#       Kudos:
#     </dt>
#     <dd class="kudos">
#       <a href="/works/39026430?view_full_work=true#kudos">
#         49
#       </a>
#     </dd>
#     <dt class="bookmarks">
#       Bookmarks:
#     </dt>
#     <dd class="bookmarks">
#       <a href="/works/39026430/bookmarks">
#         5
#       </a>
#     </dd>
#     <dt class="hits">
#       Hits:
#     </dt>
#     <dd class="hits">
#       146
#     </dd>
#   </dl>
# </li>
def parse_work(work):
    data = dict()

    # Extract work_id and user_id from
    # <li class="work blurb group work-39340149 user-1320663">
    for c in work.get_attribute_list('class'):
        if c.startswith('work-'):
            data['id'] = int(c.replace('work-', ''))
        elif c.startswith('user-'):
            data['userid'] = int(c.replace('user-', ''))

    # Extract work_title from
    # <div class="header module">
    #   <h4 class="heading">
    #     <a href="/works/39340149">
    #       How they all Find Out
    #     </a>
    head = work.find('h4', class_='heading')
    a_list = head.find_all('a')
    data['title'] = a_list[0].text

    # Extract work_author from
    # <div class="header module">
    #  by
    #  <!-- do not cache -->
    #  <a rel="author" href="/users/tomfics/pseuds/lovemelizards">
    #   lovemelizards (tomfics)
    #  </a>
    # Some works are anonymous, these don't have a <a> tag
    # <div class="header module">
    #  by
    #  <!-- do not cache -->
    #  Anonymous
    try:
        data['author'] = a_list[1].text
    except:
        data['author'] = None

    # Extract fandoms tags from
    # <h5 class="fandoms heading">
    #  <span class="landmark">
    #   Fandoms:
    #  </span>
    #  <a class="tag" href="/tags/Star%20Trek:%20Deep%20Space%20Nine/works">
    #   Star Trek: Deep Space Nine
    #  </a>
    # </h5>
    data['fandoms'] = list()
    for a in work.find('h5', class_='fandoms').find_all('a'):
        data['fandoms'].append(a.text)
    data['fandoms'].sort()

    # Extract rating from
    # <ul class="required-tags">
    #  <li>
    #   <a aria-controls="#modal"
    #      class="help symbol question modal"
    #      href="/help/symbols-key.html" title="Symbols key">
    #    <span class="rating-general-audience rating"
    #          title="General Audiences">
    #     <span class="text">
    #      General Audiences
    #     </span>
    #    </span>
    #  </a>
    # </li>
    data['rating'] = work.find('span', class_='rating').span.text

    # Extract warnings from
    # <ul class="required-tags">
    #  <li>
    #   <a aria-controls="#modal"
    #      class="help symbol question modal"
    #      href="/help/symbols-key.html" title="Symbols key">
    #     <span class="warning-no warnings"
    #           title="No Archive Warnings Apply">
    #      <span class="text">
    #       No Archive Warnings Apply
    #      </span>
    #     </span>
    #    </a>
    #   </li>
    # Annoyingly multiple warnings are separated by commas, not by
    # HTML markup.
    data['warnings'] = [s.strip()
                        for s in
                        work.find('span',
                                  class_='warnings').span.text.split(',')]
    data['warnings'].sort()

    # Extract categories (of sexual behaviour) from
    # <ul class="required-tags">
    #  <li>
    #   <a aria-controls="#modal" class="help symbol question modal"
    #      href="/help/symbols-key.html"
    #      title="Symbols key">
    #    <span class="category-gen category"
    #          title="Gen">
    #     <span class="text">
    #      Gen
    #     </span>
    #    </span>
    #   </a>
    #  </li>
    # Annoyingly multiple categories are separated by commas, not by
    # HTML markup.
    data['categories'] = [s.strip()
                          for s in
                          work.find('span',
                                    class_='category').span.text.split(',')]
    data['categories'].sort()

    # Extract iswip ("is work in progress") from
    # <ul class="required-tags">
    #  <li>
    #   <a aria-controls="#modal"
    #      class="help symbol question modal"
    #      href="/help/symbols-key.html"
    #      title="Symbols key">
    #    <span class="complete-yes iswip"
    #          title="Complete Work">
    #     <span class="text">
    #      Complete Work
    #     </span>
    #    </span>
    #   </a>
    #  </li>
    iswip = work.find('span', class_='iswip').span.text
    # Record iswip as a Boolean value to make extracting data simpler.
    data['complete'] = (iswip == 'Complete Work')

    # Extract date from
    # <div class="header module">
    #  <p class="datetime">
    #   17 May 2022
    #  </p>
    data['publicationdate'] = work.find('p', class_='datetime').text

    # Extract optional relationships from
    # <ul class="tags commas">
    #  <li class="relationships">
    #   <a class="tag"
    #      href="/tags/Julian%20Bashir*s*Elim%20Garak/works">
    #    Julian Bashir/Elim Garak
    #   </a>
    #  </li>
    # *Do not* normalise a relationship of A/B and A&B, these have
    # different meanings.
    relationships = list()
    try:
        for li in work.find_all('li', class_='relationships'):
            relationships.append(li.a.text)
    except (AttributeError, KeyError) as err:
        pass
    if relationships:
        relationships.sort()
        data['relationships'] = relationships

        # The relationships values are computationally complex, far
        # too sophisticated for many analysis tools.  Do let's
        # disassemble those in various ways to made it easy to
        # use analysis tools.
        #
        # Explode B/A and D&C into easier to analyse variables.
        # relationshippax:
        # - A
        # - B
        # - C
        # - D
        # relationshippaxslash:
        # - A
        # - B
        # relationshippaxamp:
        # - C
        # - D
        # relationshippair:        # relationship, but canonical order of pair
        # - A/B
        # - C & D
        # relationshippairslash:   # relationship, but canonical order of pair
        # - A/B
        # relationshippairamp:     # relationship, but canonical order of pair
        # - C & D
        relationshipspax = set()
        relationshipspaxamp = set()
        relationshipspaxslash = set()
        relationshipspair = set()
        relationshipspairamp = set()
        relationshipspairslash = set()
        for r in relationships:
            # Split the characters in the relationships
            r = r.replace('(implied)', '')
            r = r.replace('(unrequited)', '')
            # The first & or / defines the type of relationship
            if r.find('&') > -1:
                style = 'amp'
            elif r.find('/') > -1:
                style = 'slash'
            else:
                style = 'other'
            # Convert string to list of strings at / or &
            pair = [s.strip() for s in re.split('[/&]', r)]
            # Remove empty strings, caused by leading or trailing / or &
            pair = list(filter(None, pair))
            # Normlise order
            pair.sort()

            # Make lists of people involved.
            # We use sets rather than lists as that handles duplicate
            # names without special handling.
            if len(pair) > 1:
                # Lists of people
                for p in pair:
                    relationshipspax.add(p)
                    if style == 'amp':
                        relationshipspaxamp.add(p)
                    elif style == 'slash':
                        relationshipspaxslash.add(p)
                # Lists of pairings
                if style == 'amp':
                    pair_s = ' '.join(tween(pair, '&'))
                    relationshipspairamp.add(pair_s)
                    relationshipspair.add(pair_s)
                elif style == 'slash':
                    pair_s = ''.join(tween(pair, '/'))
                    relationshipspairslash.add(pair_s)
                    relationshipspair.add(pair_s)

        if relationshipspax:
            data['relationshipspax'] = sorted(relationshipspax)
        if relationshipspaxamp:
            data['relationshipspaxamp'] = sorted(relationshipspaxamp)
        if relationshipspaxslash:
            data['relationshipspaxslash'] = sorted(relationshipspaxslash)
        if relationshipspair:
            data['relationshipspair'] = sorted(relationshipspair)
        if relationshipspairamp:
            data['relationshipspairamp'] = sorted(relationshipspairamp)
        if relationshipspairslash:
            data['relationshipspairslash'] = sorted(relationshipspairslash)

    # Extract optional characters from
    # <ul class="tags commas">
    #  <li class="characters">
    #   <a class="tag"
    #      href="/tags/Elim%20Garak/works">
    #    Elim Garak
    #   </a>
    #  </li>
    l = list()
    try:
        for li in work.find_all('li', class_='characters'):
            l.append(li.a.text)
    except (AttributeError, KeyError) as err:
        pass
    if l:
        l.sort()
        data['characters'] = l

    # Extract optional freeforms from
    # <ul class="tags commas">
    #  <li class='freeforms'>
    #   <a class="tag" href="/tags/Crossdressing/works">
    #    Crossdressing
    #   </a>
    #  </li>
    l = list()
    try:
        for li in work.find_all('li', class_='freeforms'):
            l.append(li.a.text)
    except (AttributeError, KeyError) as err:
        pass
    if l:
        l.sort()
        data['freeforms'] = l

    # Extract summary.
    # <blockquote class="userstuff summary">
    #  <p>'A man is a god in ruins.' Martok and Garak, after ‘By
    #   Inferno’s Light’.</p>
    # </blockquote>
    try:
        data['summary'] = work.find('blockquote', class_='summary').p.text
    except AttributeError:
        pass

    # Extract a heap of statistics, all of the form
    # <dl class="stats">
    #  <dt class="language">
    #   Language:
    #  </dt>
    #  <dd class="language">
    #   English
    #  </dd>
    data['language'] = lang_ao3_to_iso[work.find('dd',
                                                 class_='language').text]

    words_text = work.find('dd', class_='words').text.replace(',', '')
    if words_text == '':
        data['words'] = int(0)
    else:
        data['words'] = int(words_text)

    # Count of comments
    try:
        data['comments'] = int(work.find('dd', class_='comments').a.text.replace(',', ''))
    except AttributeError:
        data['comments'] = int(0)

    # Count of kudos
    try:
        data['kudos'] = int(work.find('dd', class_='kudos').a.text.replace(',', ''))
    except AttributeError:
        data['kudos'] = int(0)

    # Count of bookmarks
    try:
        data['bookmarks'] = int(work.find('dd', class_='bookmarks').a.text.replace(',', ''))
    except AttributeError:
        data['bookmarks'] = int(0)

    # Extract chapters
    # <dd class="chapters">
    #  <a href="/works/39026430/chapters/97673250">
    #   2
    #  </a>
    #   /2
    #  </dd>
    # Form can be
    #  1/2 or 1/?
    l = work.find('dd', class_='chapters').text.split('/')
    data['chapter'] = int(l[0])
    if l[1] != '?':
        data['chapters'] = int(l[1])

    # Count of downloads.
    data['hits'] = int(work.find('dd', class_='hits').text.replace(',', ''))

    return data


# Key field to the database.
# It looks like AO3 maintain a work identifier, let's assume that's unique.
def database_key(d):
    return int(d['id'])


# Main
if __name__ == "__main__":

    args = command_line_args()
    parsedate = str(datetime.datetime.now())

    # Initialise database, from an existing file to update it,
    # otherwise empty.
    database = list()
    if args.input_database:
        with open(args.input_database, 'r') as in_f:
            database = yaml.load(in_f, Loader=SafeLoader)

    # Parse each AO3 index webpage file into database records, one
    # record for each work within the index page.
    for filename in args.filename:
        # Read and parse webpage into normalised HTML.
        with open(filename, 'r') as page_f:
            page = page_f.read()
        page_soup = BeautifulSoup(page, 'html.parser')

        # Discard the page headers and other non-content.
        # The list of works is surrounded by a Ordered List
        # <ol class="work">.
        # tag.
        works = page_soup.find('ol', class_='work')

        # Loop through the works extracting their attributes.
        # Each work is surrounded by a List Item <li class="work">.
        # Add the works' attributes to the database.
        for work in works.find_all('li', class_='work'):
            # Extract data from webpage
            data = parse_work(work)
            # Add metadata about this run
            data['filename'] = filename
            data['parsedate'] = parsedate
            # Add to database
            database.append(data)

    # Write database of works.
    # We do this in a canonical order (ascending work_id) to make
    # comparisons of changes easily possible using the standard Unix
    # diff.
    database.sort(key=database_key)
    with open(args.output_database, 'w') as out_f:
        yaml.dump(database,
                  out_f,
                  allow_unicode=True,
                  width=79)
