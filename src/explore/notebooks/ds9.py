#
# ds9.py

# Functions for manipulation of AO3 and DS9 data in notebooks.
# The main one is to load the dataframe, which is done with
#   df = ds9.df()
# If you need to refer to any to of the datatypes then say
#   ds9.categories_type
# and so on.
#
# You'd typicall start a notebook with
#   import pandas as pd
#   import numpy as np
#   import seaborn as sns
#   import matplotlib as plt
#   import ds9
#   df = ds9.df()

import pandas as pd

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
        'Mature',
        'Explicit',
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


# Convert some strings to lists
def strtolist(s):
    if pd.isna(s):
        return list()
    else:
        return eval(s)

# Load the dataframe
# Use with
#   import ds9
#   df = ds9.df()
def df(csv='../../../data/database/20220612.csv',
       narrowing=True):
    # Load data from CSV into Pandas dataframe
    # See https://pbpython.com/pandas_dtypes.html
    df = pd.read_csv(csv, dtype=dtypes)
    df.set_index('id', inplace=True)

    df['categories'] = df['categories'].apply(strtolist)
    df['characters'] = df['characters'].apply(strtolist)
    df['charactersclean'] = df['charactersclean'].apply(strtolist)
    df['fandoms'] = df['fandoms'].apply(strtolist)
    df['freeforms'] = df['freeforms'].apply(strtolist)
    df['relationships'] = df['relationships'].apply(strtolist)
    df['relationshipspair'] = df['relationshipspair'].apply(strtolist)
    df['relationshipspairslash'] = df['relationshipspairslash'].apply(strtolist)
    df['relationshipspairamp'] = df['relationshipspairamp'].apply(strtolist)
    df['relationshipspax'] = df['relationshipspax'].apply(strtolist)
    df['relationshipspaxslash'] = df['relationshipspaxslash'].apply(strtolist)
    df['relationshipspaxamp'] = df['relationshipspaxamp'].apply(strtolist)
    df['warnings'] = df['warnings'].apply(strtolist)
    # Convert to pandas datetime
    df['publicationdate'] = pd.to_datetime(df['publicationdate'])

    # Narrowing common to all analysis,
    # can be disabled with
    #   df = ds9.df(narrowing=False)
    # if needed.
    if narrowing:
        # Only publications after 2010
        dawn = pd.Timestamp('2010-01-01')
        df = df[df['publicationdate'] >= dawn]
        # Only English
        df = df[df['language'] == 'en']
        # Complete works
        df = df[df['complete'] == True]

    # Set the Pandas environment
    # We want to see the full table.
    pd.options.display.max_rows = 10000

    return df
