#!/usr/bin/env python3
#
# To convert YAML to a pandas data table, firstly list all the fields in the
# YAML file with
#    src/explore/table/data-fields.py \
#      -i data/database/20220612.yaml
# then hand those fields, id first, into the YAML to CSV exporter:
#   src/explore/table/data-table.py \
#      -i data/database/20220612.yaml \
#      -o data/database/20220612.csv \
#      id \
#      author bookmarks categories chapter chapters characters comments \
#      complete fandoms filename freeforms hits kudos language parsedate \
#      publicationdate rating relationships relationshipspair \
#      relationshipspairamp relationshipspairslash relationshipspax \
#      relationshipspaxamp relationshipspaxslash summary title userid \
#      warnings words
#
# then read that into a Pandas dataframe.

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib as plt

# https://pandas.pydata.org/pandas-docs/stable/user_guide/categorical.html
#
# Categories are ordered by descending frequency in dataset so that
# setting unsorted=True makes graphs come out correctely where
# the category is the primary category of the population.
#
# To get the frequency of, say, 'language', run
# src/explore/table/histogram-table.py -i data/database/20220612.yaml language

categories_type = pd.api.types.CategoricalDtype(
    categories=[
        'M/M',
        'Gen',
        'F/M',
        'F/F',
        'Multi',
        'No category',
        'Other'
    ],
    ordered=True)

# Ordered by frequency in dataset
warnings_type = pd.api.types.CategoricalDtype(
    categories=[
        'No Archive Warnings Apply',
        'Choose Not To Use Archive Warnings',
        'Graphic Depictions Of Violence',
        'Major Character Death',
        'Rape/Non-Con',
        'Underage',
    ],
    ordered=True)

# Ordered by frequency in dataset
rating_type = pd.api.types.CategoricalDtype(
    categories=[
        'General Audiences',
        'Teen And Up Audiences',
        'Explicit',
        'Mature',
        'Not Rated',
    ],
    ordered=True)

language_type = pd.api.types.CategoricalDtype(
    categories=[
        'en',
        'ru',
        'de',
        'zh-Hans',
        'it',
        'pt-br',
        'ko',
        'fr',
        'es',
        'cy',
        'pl',
        'cs',
        'ja',
        'he',
        'tlh-Latn',
        'nl'
    ],
    ordered=True)

dtypes = { 'id': 'int64',
           'author': 'string',
           'chapter': 'Int64',
           'chapters': 'Int64',
           'comments': 'Int64',
           'complete': 'bool',
           'filename': 'string',
           'hits': 'Int64',
           'kudos': 'Int64',
           'language': 'category',
           'summary': 'string',
           'title': 'string',
           'userid': 'Int64',
           'words': 'Int64',
           'rating': rating_type,
           'language': language_type }

# Load data from CSV into Pandas dataframe
# See https://pbpython.com/pandas_dtypes.html
df = pd.read_csv('data/database/20220612.csv', dtype=dtypes)
df.set_index('id', inplace=True)

# Convert to pandas datetime
# Only publications after 2010
df['publicationdate'] = pd.to_datetime(df['publicationdate'])
dawn = pd.Timestamp('2010-01-01')
df = df[df['publicationdate'] >= dawn]

# Only English
df = df[df['language'] == 'en']

# Complete works
df = df[df['complete'] == True]


# Example plot

fig = sns.catplot(x='kudos', kind='count', orient='v', data=df)
fig

# sns.FacetGrid.savefig(fig, 'language.svg', format='svg', transparent=True)
# plt.pyplot.show()
