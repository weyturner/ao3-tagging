src/collect
===========

Collect data from An Archive of Our Own and store it in a database in
data/.

Each of the programs used prints it's full command-line parameters if
run with the `--help` option.

The processing steps are as follows:


src/collect/collect-pages.py
----------------------------

Retrieves webpages from Archive of Our Own for a particular tag. The
tag `Star Trek: Deep Space Nine` is used if no other tag is supplied
using the `--tag` parameter.

The retreived web pages are saved where indicated by the `--outprefix`
parameter. Use the directory `data/raw/` when doing a production run.

Each retreived web page is named
`<tag>-<date>-<time>-<count>-index.html`.  These saved web pages are
used for further processing.

Metadata about each retrieved web page is stored into
`<tag>-<date>-<time>-<count>-meta.yaml`. These files are not used for
further processing but are retained for the repeatability of the
experiment.

The AO3 website classifies as misuse client IP addresses which
retrieve large numbers of web pages in a short period. This program
limits itself to retreiving six pages per minute (ie, a page per ten
seconds). That is below what the site administrators say in forum
postings is the trigger for classification as misuse. Different page
retreival rates can be used with the ``--rate-limit`
parameter. Different rates have not been tested: being added to the
AO3 blocklist would impede research so this risk was not taken.

The program depends on the prior installation of these Python
libraries; for Debian with `sudo apt-get install`:

 * python3-bs4

 * python3-yaml

or for Fedora with `sudo dnf install`:

 * python3-beautifulsoup4

 * python3-pyyaml

The program is typically run with

```
src/collect/collect-pages.py --outprefix data/raw/star-trek-deep-space-nine-20220601/
```


src/collect/parse-pages-into-db.py
----------------------------------

Parses the retreived web pages into a YAML file.

Data fields are cleaned. This uses only knowledge of An Archive of Our
Own. For example, AO3 specifies languages using the native text of
that language (English, Français, etc); this is difficult to process
and so is converted to ISO language codes (en, fr, etc). Similarly,
many numerical fields are presented using commas (1,000) and these are
converted to a more usual integer format (1000). Fields with multiple
values are converted to a YAML list.

The program produces a number of fields which do not exist in the web
page. This is to make processing be downstream analsysis much
easier. These fields do not replace fields containing the exact data
from the web page, so the original data is always available to check
for processing errors.

The fields added for works are:

 * `relationshippax` (a list) -- people mentioned in `relationships`.

 * `relationshippaxslash` (a list) -- people mentioned in
   `relationships` in the form "A/B" (that is, the convention to
   indicate a sexual relationship).

 * `relationshippaxamp` (a list) -- people mentioned in
   `relationships` in the form "A & B" (that is, the convention to
   indicate a non-sexual relationship).

 * `relationshippair` (a list) -- `relationships`, but modified so
   that "A/B" and "B/A" always appear in the same order, namely
   "A/B". Similarly, "A & B" and "B & A" always appear in the same
   order, namely "A & B".

 * `relationshippairslash` (a list) -- as for `relationshippair`, but
   only "A/B" (sexual) relationships.

 * `relationshippairamp` (a list) -- as for `relationshippair`, but
   only "A & B" (non-sexual) relationships.

The data is ordered by `id`. That is a unique ascending number for
each work.

Install these packages for Debian with `sudo apt-get install`:

 * python3-bs4

 * python3-yaml

or these packages for Fedora with `sudo dnf install`:

 * python3-beautifulsoup4

 * python3-pyyaml

The program is typically run with:

```
src/collect/parse-pages-into-db.py --output-database data/database/20220612.yaml data/raw/star-trek-deep-space-nine-20220601/*.html
```


src/collect/clean-db-deep-space-nine.py
---------------------------------------

This program uses extensive knowledge of Deep Space Nine to clean the
database.

That cleaning has several goals:

 * Some phrases present in a name always indicate a non-cast
   character. These immediately cause a mapping to `non-cast`. eg:
   "(original character)". See `zap_dict` in the program.

 * Some phrases in names are redundant for identification, but are
   guides for people wanting to select a story to read. These guides
   are often in parenthesis. eg: "(one-sided)" or "(mentioned)". These
   phrases are removed from the name. See `delete_list` in the
   program.

 * Some characters have multiple names. These are mapped to a single
   normalised name. That name is typically "<firstname> <lastname>",
   although in a television series with diverse cultures and species
   that's not always the normalised name. eg: "Doctor Julian Bashir"
   to "Julian Bashir". See `synonym_dict` in the program.

 * Some names have typographical errors, these are corrected by
   mapping them to the normalised name. eg: "Torah Naprem" to "Tora
   Naprem". Again, see `synonym_dict` in the program.

 * Non-cast characters are mapped to the name `non-cast`. This is a
   way to deal with the large number of characters original to a
   particular author, or with out-of-universe cross-over characters
   (eg, Dr Who). A list of all the known cast members was iteratively
   built, and names not in this list are converted to `non-cast`. See
   `known set` in the program.

As a check, the characters encountered which are mapped to `non-cast`
are printed (to the screen, aka `stdout`). This was the basis for the
iterative construction of `known_set`.

Once the names are changed, these fields are added:

 * `charactersclean` (a list) -- originally from `characters`.

 * `cleandate` (a date) -- the time and date the program was run, for
   data traceability.

and these fields are updated:

 * `relationshippax` (a list) -- as above, originally from `relationships`.

 * `relationshippaxslash` (a list) -- as above, originally from
   `relationships`.

 * `relationshippaxamp` (a list) -- as above, originally from
   `relationships`.

 * `relationshippair` (a list) -- as above, originally from
   `relationships`.

 * `relationshippairslash` (a list) -- as above, originally from
   `relationships`.

 * `relationshippairamp` (a list) -- as above, originally from
   `relationships`.

No libraries are required beyond a typical Python3 installation.

Typical command is:

```
src/collect/clean-db-deep-space-nine.py --input-database data/database/20220612.yaml --output-database data/database/20220612-clean.yaml > data/database/20220612-clean-stdout.txt
```


src/explore/table/data-fields.py
--------------------------------

This prints all the field names present in the YAML database.

This is useful if you want to export all the fields to a .CSV file
using the data-table.py utility described below.

Typical command is:

```
src/explore/table/data-fields.py --input-database data/database/20220612-clean.yaml
```

and the output looks like this:

```
author bookmarks categories chapter chapters characters charactersclean cleandate comments complete fandoms filename freeforms hits id kudos language parsedate publicationdate rating relationships relationshipspair relationshipspairamp relationshipspairslash relationshipspax relationshipspaxamp relationshipspaxslash summary title userid warnings words
```


src/explore/table/data-table.py
-------------------------------

This exports fields in the YAML database to a .CSV file.

.CSV files are traditionally the input to statistical processing, so
the .CSV file marks the boundary from the data science steps of
collection and cleaning to the data science steps of visualisation and
statistics.

Different CSV files might need to be generated for different
statistical products:

 * Some don't like multi-valued fields

 * Some don't like headings, some do. See the `--header` and
   `--no-header` command line options to data-table.py.

 * Some are tight on memory, and so irrelevant fields can be not exported.

Here's how to export just the author and title:

```
src/explore/table/data-table.py --input-database data/database/20220612-clean.yaml --output-csv example.csv author title
```

Note that some statistical packages want the uniqiue key in the first
column of the exported data. That is, the `id` field listed as the
first variable to export.

```
src/explore/table/data-table.py --input-database data/database/20220612-clean.yaml --output-csv example.csv id author title
```

In conjuction with data-fields.py to list all the field names, all the
fields of the YAML database can be exported to the CSV file.

Here's how to do that in a single Unix command, including moving `id`
to the front of the list of field names.

 * data-fields.py lists all the field names.

 * the stream editor *sed* deletes `id` (sed's `s` command "substitutes
   ` id ` with ` `"), leaving the other field names alone.

 * *xargs* ("expand arguments") moves the field names printed by
   data-fields.py into command line parameters to data-table.py.

 * data-table.py reads the YAML database, matches all the fields in
   its command line (which is *all* the fields), and exports
   them. `id` is listed as the first parameter to data-table.py, and
   so is the first column in the .CSV file.

```
src/explore/table/data-fields.py  \
  --input-database data/database/20220612-clean.yaml |  \
sed 's/ id / /' |  \
xargs src/explore/table/data-table.py  \
  --input-database data/database/20220612-clean.yaml  \
  --output-csv data/database/20220612.csv \
  id
```

explore/pandas/load_data_table.py
---------------------------------

Use this code in a Jupyter notebook to load the .CSV file in
data/database/ into Jupyter.

As well as loading the data, this assigns the correct Pandas datatypes
and also creates categories for the columns which need those.

After this, the next steps are to do whatever data reduction or
selection is needed, and then to graph the data.


Open issues
-----------

*Multi-value fields* -- like the many relationship fields -- are not
handled well by some statistical languages. So that might require some
additional work so that their individual needs are met.  Many AO3
fields are multi-value fields.


Resolved issues
---------------

*Out of scope records* should be removed at the analysis stage using
Pandas, as the code in Pandas for data reduction is concise. Here's
the typical data reduction:

```
# Only publications after 2010
df['publicationdate'] = pd.to_datetime(df['publicationdate'])
dawn = pd.Timestamp('2010-01-01')
df = df[df['publicationdate'] >= dawn]

# Only English
df = df[df['language'] == 'en']

# Complete works
df = df[df['complete'] == True]
```


Programming notes
=================


Downloading tags
----------------

Download tags from a query subset of
[An Archive of Our Own](https://archiveofourown.org/).

This task is screen-scraping of AO3 using the Python library
[BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)
from the fandom
https://archiveofourown.org/tags/Star%20Trek:%20Deep%20Space%20Nine/works

[Toastystats](https://github.com/fandomstats/toastystats) have wrapped
the generic functions of BeautifulSoup with a porcelain for AO3.


AO3 URL structure
-----------------

Is really nice. Here's all the works for _Star Trek: Deep Space Nine_:

https://archiveofourown.org/tags/Star%20Trek:%20Deep%20Space%20Nine/works

Unfortunately that output is paginated, but driving that is just a page counter:

https://archiveofourown.org/tags/Star%20Trek:%20Deep%20Space%20Nine/works?page=1

Similarly tag names can be transformed into tag URLs really easily:

_Damar (Star Trek)/Original Female Character(s)_

becomes

https://archiveofourown.org/tags/Damar%20(Star%20Trek)*s*Original%20Female%20Character(s)/works

This is great as it means we can re-create URLs from text, rather than
needing to store both the tag value and the tag URL.


Input
-----

Here's what the HTML of a work looks like.

As can be seen there's extensive use of HTML semantic markup, such as `class`.

```
    <ol class="work index group">
      <li id="work_39026430"
          class="work blurb group work-39026430 user-8795776"
          role="article">
        <!--title, author, fandom-->
        <div class="header module">
          <h4 class="heading">
            <a href="/works/39026430">Gods in Ruins</a>
            by
            <a rel="author"
               href="/users/Arati_Mhevet/pseuds/Arati_Mhevet">Arati_Mhevet</a>
          </h4>
          <h5 class="fandoms heading">
            <span class="landmark">Fandoms:</span>
            <a class="tag"
               href="/tags/Star%20Trek:%20Deep%20Space%20Nine/works">Star Trek: Deep Space Nine</a>
            &nbsp;
          </h5>
          <!--required tags-->
          <ul class="required-tags">
            <li>
              <a class="help symbol question modal"
                 title="Symbols key"
                 aria-controls="#modal"
                 href="/help/symbols-key.html"
                 <span class="rating-general-audience rating"
                       title="General Audiences">
                   <span class="text">General Audiences</span>
                 </span>
              </a>
            </li>
            <li>
              <a class="help symbol question modal"
                 title="Symbols key"
                 aria-controls="#modal"
                 href="/help/symbols-key.html">
                 <span class="warning-no warnings"
                       title="No Archive Warnings Apply">
                   <span class="text">No Archive Warnings Apply</span>
                 </span>
              </a>
            </li>
            <li>
              <a class="help symbol question modal"
                 title="Symbols key"
                 aria-controls="#modal"
                 href="/help/symbols-key.html">
                <span class="category-gen category"
                      title="Gen">
                  <span class="text">Gen</span>
                </span>
              </a>
            </li>
            <li>
              <a class="help symbol question modal"
                 title="Symbols key"
                 aria-controls="#modal"
                 href="/help/symbols-key.html">
                <span class="complete-yes iswip"
                      title="Complete Work">
                  <span class="text">Complete Work</span>
                </span>
              </a>
            </li>
          </ul>
          <p class="datetime">17 May 2022</p>
        </div>

        <!--warnings again, cast, freeform tags-->
        <h6 class="landmark heading">Tags</h6>

        <ul class="tags commas">
          <li class='warnings'>
            <strong>
              <a class="tag"
                 href="/tags/No%20Archive%20Warnings%20Apply/works">No Archive Warnings Apply</a>
            </strong>
          </li>
          <li class='relationships'>
            <a class="tag"
               href="/tags/Julian%20Bashir*s*Elim%20Garak/works">Julian Bashir/Elim Garak</a>
          </li>
          <li class='relationships'>
            <a class="tag"
               href="/tags/Elim%20Garak*s*Cardassia/works">Elim Garak/Cardassia</a>
          </li>
          <li class='relationships'>
            <a class="tag"
               href="/tags/Elim%20Garak%20*a*%20Enabran%20Tain/works">Elim Garak & Enabran Tain</a>
          </li>
          <li class='characters'>
            <a class="tag"
               href="/tags/Elim%20Garak/works">Elim Garak</a>
          </li>
          <li class='characters'>
            <a class="tag"
               href="/tags/Martok%20(Star%20Trek)/works">Martok (Star Trek)</a>
          </li>
          <li class='characters'>
            <a class="tag"
               href="/tags/Enabran%20Tain/works">Enabran Tain</a>
          </li>
          <li class='characters'>
            <a class="tag"
               href="/tags/Worf%20(Star%20Trek:TNG*s*DS9)/works">Worf (Star Trek:TNG/DS9)</a>
          </li>
          <li class='characters'>
            <a class="tag"
               href="/tags/Julian%20Bashir/works">Julian Bashir</a>
          </li>
        </ul>
        <!--summary-->
        <h6 class="landmark heading">Summary</h6>
        <blockquote class="userstuff summary">
          <p>'A man is a god in ruins.' Martok and Garak, after ‘By Inferno’s Light’.</p>
        </blockquote>
      </li>
    </ol>
```

Output
------

We want a YAML file like this, which we can use to load the meta-data
of all 10214 works into RAM.

work: 12345
title: "The Casualty"
author: "XindiChick"
pseuds: "XindiChick"
author_page: https://archiveofourown.org/users/XindiChick/pseuds/XindiChick
date: "2022-05-06"
series_name: "The nermal files"
series_id: 789
language: en
words: 118267
chapters: 32
comments: 2
kudos: 3
bookmarks: 1
hits: 113
relationships:
 - Damar (Star Trek)/Original Female Character(s)
 - Dukat (Star Trek) Original Female Character(s)
characters:
 - Original Cardassian Character(s)/Original Female Character(s)
 - Dukat (Star Trek)
 - Damar (Star Trek)
 - Kira Nerys Odo (Star Trek)
 - Elim Garak
 - Original Character(s)
freeforms:
 - Angst
 - Smut
 - War
 - Occupation
 - Dominion War (Star Trek)
 - Cardassians
 - Cardassia
 - Cardassian Culture
 - Cardassian Anatomy
 - Cardassian Rebellion
 - Military
 - Canon-Typical Violence
 - Prisoner of War
 - Friendship
 - Family
 - Psychological Trauma
 - loss of family
 - Destruction of home
 - Lovers To Enemies
 - Friends to Lovers
 - Cardassian-Dominion Alliance
 - Forbidden Love
 - dealing with grief
 - DS9 Takeover
 - Terok Nor (Star Trek)
 - Post-Canon Cardassia
 - Rusot (Star Trek)
 - Freeform Seskal (Star Trek)
 - Tora Ziyal (Star Trek)
 - Weyoun 7-8 (Star Trek)
 - Female Founder (Star Trek) - Freeform
 - War Crimes
 - Bajoran Spirit merged with Cardassian Values
 - Aliens
 - Footnotes
 - no need to be a fan to read
 - did I mention aliens?
 - sexy aliens
 - Alien Sex
 - Alien Romance
 - Alien Biology
 - Alien Culture


Detail of note
--------------

1) In HTML URLs `A/B` tags are transformed to `A*s*B` to avoid
clashing with HTML's use of `/`.


2) There's a unkown "pseuds" feature about user-names: compare these
URLs:

```
<a href="/users/Eitch/pseuds/Lenn" rel="author">Lenn (Eitch)</a>
<a href="/users/Lady_Sci_Fi/pseuds/Lady_Sci_Fi" rel="author">Lady_Sci_Fi</a>
<a href="/users/kas_delafere/pseuds/yeoman_kas" rel="author">yeoman_kas (kas_delafere)</a>
```

3) There is a deeper structure to tags than apparent in the rendered
page. The types seen so far are:

 - `relationships`
 - `characters`
 - `freeforms`

4) Series are assigned an ID, as in /series/2759188.

5) Stats are particularly easy to parse.

 - `language`
 - `words`
 - `chapters`
 - number of `comments`
 - number of `kudos`
 - `hits`


Analysis
--------

Tags are, in statistical jargon, categories.  Statistical languages
are not well-adapted to records with some hundreds of categories, most
of which are empty.

We can analyse the categories: such as presenting the frequency of the
tag in a histogram or word cloud.

Which sort of statistical distribution are the frequencies of the
categories?  What are the likely reasons for this?

Another way of looking at tags is as edges of a graph. That is,
stories with tags connect with stories with the same tag.  That cloud
might give some interesting results.

Tags can also be looked upon as derived values of the work. If we can
train a AI on the existing tags, will it generate further tags for
stories from their text?

Ethics
------

The https://archiveofourown.org/robots.txt file limits which URLs we
should programmatically access. That file contains

```
# See https://www.robotstxt.org/robotstxt.html for documentation on how to use the robots.txt file
#

User-agent:	*
Disallow:	/works? # cruel but efficient
Disallow: /autocomplete/
Disallow: /downloads/
Disallow: /external_works/
# disallow indexing of search results
Disallow: /bookmarks/search?
Disallow: /people/search?
Disallow: /tags/search?
Disallow: /works/search?

User-agent:	Googlebot
Disallow: /autocomplete/
Disallow: /downloads/
Disallow: /external_works/
# Googlebot is smart and knows pattern matching
Disallow: /works/*?
Disallow: /*search?
Disallow:	/*?*query=
Disallow:	/*?*sort_
Disallow:	/*?*selected_tags
Disallow:	/*?*selected_pseuds
Disallow: /*?*use_openid
Disallow: /*?*view_adult
Disallow: /*?*tag_id
Disallow: /*?*pseud_id
Disallow: /*?*user_id
Disallow: /*?*pseud=
Disallow: /people?*show=

User-agent: Slurp
Crawl-delay: 30
```

Our program abides by this request.

It takes 27 hours to download the 10,000 stories and abide by the robots.txt


Prior work
----------

For a real-time summary see:

https://github.com/topics/archive-of-our-own

And in particular

https://github.com/nianeyna/ao3downloader

Also looking interesting is

https://github.com/fandomstats/toastystats

which is the work of

https://github.com/annathecrow

This looks handy

https://gitlab.com/antarcticite/ao3-bulk-downloader/
