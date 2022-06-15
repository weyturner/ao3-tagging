src/collect
===========

Collect data from An Archive of Our Own and store it in a database in
data/.

The following are notes used during the development of these programs.


collect-pages.py
----------------

Retrieves webpages from Archive of Our Own for a particular tag.

Install these packages for Debian with `sudo apt-get install`:

 * python3-bs4

 * python3-yaml

or these packages for Fedora with `sudo dnf install`:

 * python3-beautifulsoup4

 * python3-pyyaml


parse-pages-into-db.py
----------------------

Parses retreived webpages into a YAML file.

Install these packages for Debian with `sudo apt-get install`:

 * python3-bs4

 * python3-yaml

or these packages for Fedora with `sudo dnf install`:

 * python3-beautifulsoup4

 * python3-pyyaml


clean-db-deep-space-nine.py
---------------------------

Uses knowledge of Deep Space Nine to clean the database.


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

For a real-time sumary see:

https://github.com/topics/archive-of-our-own

And in particular

https://github.com/nianeyna/ao3downloader

Also looking interesting is

https://github.com/fandomstats/toastystats

which is the work of

https://github.com/annathecrow

This looks handy

https://gitlab.com/antarcticite/ao3-bulk-downloader/
