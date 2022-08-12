
Pandas cheatsheet
=================


Starting Jupyter
----------------

See the start of ~/src/ao3-tagging/src/misc/apple-m1-setup.md for how
to set up the conda environment and start Jupyter. In summary:

```
cd src/ao3-tagging
conda activate ao3-tagging
jupyter notebook
```

The notebook ~/src/ao3-tagging/src/explore/notebooks/base.ipynb has
the clean data from ~/src/ao3-tagging/data/database/20220612.csv
already loaded and narrowed with the code:

```
# Convert to pandas datetime
# Only publications after 2010
df['publicationdate'] = pd.to_datetime(df['publicationdate'])
dawn = pd.Timestamp('2010-01-01')
df = df[df['publicationdate'] >= dawn]

# Only English
df = df[df['language'] == 'en']

# Complete works
df = df[df['complete'] == True]
```

Open base.ipynb by navigating Jupyter to the src/explore/notebooks/
directory and then clicking on base.ipynb to load it. Doing that has
the path to src/data/datbase/*.csv correct.

When you open base.ipynb then right away do File | Save As a different
filename so that your changes are saved elsewhere.

If you want to load the .CSV data into Jupyter from scratch then the
code for that can be coppied from
~/src/ao3-tagging/src/explore/pandas/load_data_table.py.

Both this code and the base.ipynb put the .CSV data in a Pandas
dataframe named `df`.

To run a Jupyter program you fill in the cell and press [Run]. The
[Run] command will run all previously un-run cells. If you want to run
the entire page of the notebook from the start then press [Kernel]
[Restart and run all].

If you want to create a whole new program then press [New] and select
[Python3].


Narrowing data by rows
----------------------

If the field is not a list then narrowing is straightforward.

You do need to get the Python syntax right.

```
# Syntax to compare numbers
#   equals -- note the two equals signs
new_df = df[df['kudos'] == 0]
#   not equals
new_df = df[df['kudos'] != 0]
#   greater than, greater than or equal to
new_df = df[df['kudos'] > 0]
new_df = df[df['kudos'] >= 0]
#   less than, less than or equal to
new_df = df[df['kudos'] < 0]
new_df = df[df['kudos'] <= 0]

# Syntax to compare a string
#   strings are the same (equal)
new_df = df[df['language'] == 'en']
#   strings are not the same (not equal)
new_df = df[df['language'] != 'en']

# Syntax to compare a boolean
#   equals true
new_df = df[df['complete'] == True]
#   equals false
new_df = df[df['complete'] == False]
```

Remember to press [Run].


Narrowing data by rows -- fields which are lists
------------------------------------------------

If the field is a list, and a lot of the data from an Archive of Our
Own is lists of strings, then here's how to make a narrower dataframe
`new_df` containing the rows which have a matching value in the
list. We're using `charactersclean` containing `Elim Garak` for this
example, but the same code with the names changed can be used for the
relationships.

Hint: use the Find+Replace function in your text editor to change all
`charactersclean` to the field you want to match and `Elim Garak` to
the value you want to match. Similarly for `new_df` if you want a
different name for the narrowed dataset. Then you don't have to worry
too much about Python's abundant use of parenthesis and brackets.

```
# New and empty dataframe
new_df = pd.DataFrame()
# Walk through the dataframe 'df' looking for matches in, say, charactersclean
for index, charactersclean in zip(df.index, df['charactersclean']):
    if 'Elim Garak' in charactersclean:
        # Match found, copy the whole row to the bottom of the new dataframe
        row = df[df.index == index]
        new_df = pd.concat([new_df, row])
# new_df now contains the rows in df with a match in the list
```

The indentation (leading spaces) matters in Python. Comments start
with a `#` and you can leave those out.

Remember to use the clean-up variables for this: `charactersclean`,
`relationshipspairslash` and so on. If you don't get a match for
`relationshipspairslash` then try the relationship `'A/B'` as
`'B/A'`. The normalised relationship values have the alphabetically
lowest name first.

This code takes a long time to run and produce the new dataframe
`new_df`. You can tell it's still running because the prompt to the
left of the cell says `In: [*]`, the `*` meaning it's busy.

Once the cell has finished computing then you can have a quick peek at
the results by asking Python what is in the variable:

```
new_df
```

and if you want to see the whote thing:

```
print(new_df)
```

Reference: This page discusses the technical handling of list data values in Pandas:
https://towardsdatascience.com/dealing-with-list-values-in-pandas-dataframes-a177e534f173


Narrowing data by columns
-------------------------

Sometimes you don't care for particular columns. They're easily
dropped using the column name.

```
new_df = df.drop(['cleandate'], axis=1)
```

or mutiple column names:

```
new_df = df.drop(['cleandate', 'summary'], axis=1)
```

If you want to narrow to just one column, say `charactersclean`, then
do this:

```
new_df = df[['charactersclean']]
```


Looking at a dataframe
----------------------

If you want to have a idea of what the dataframe looks like, then
simply entering the name of the dataframe and pressing [Run] will show
it:

```
new_df
```

If you want to see the whole thing:

```
print(new_df)
```

Sometimes showing only part of the dataframe is annoying. Set the
maximum number of rows displayed to a value which suits you:

```
pd.options.display.max_rows = 999
print(new_df)
```


Exporting to CSV
----------------

Once you have the new dataframe `new_df` looking how you want it:

```
new_df.to_csv('name-of-file.csv')
```

which will save the dataframe `new_df` to the CSV file `name-of-file.csv`.

If you want to save it to a particular place then Unix filenames use
`/` between the folder names. Unix uses `~` to mean your home
folder. So if you want to save it to your home folder then say
`~/name-of-file.csv`. Or even a folder you made for this project, say,
`~/ao3-tagging/name-of-file.csv`.

If you don't want the first row to be a heading with the variable
names then:

```
new_df.to_csv('new_df.csv', header=None)
```


Exploding list fields
---------------------

Sometimes it's useful to turn one row like this

```
['Elim Garak', 'Julian Bashir', 'Quark']
```

into three rows like this

```
'Elim Garak',
'Julian Bashir'
'Quark'
```

with all the other data in the row copied.

That might be a lot of memory, so maybe drop the columns and narrow
the rows you don't need before doing this:

```
new_df = pd.DataFrame()
for index, charactersclean in zip(df.index, df['charactersclean']):
    for i in charactersclean:
        row = df[df.index == index].copy()
        row['charactersclean'] = i
        new_df = pd.concat([new_df, row], ignore_index=True)
```

Excel is likely to be much happier with this format, but you'll
probably need to create a .CSV per field which is expanded (you can
imagine the size if we expanded every field all at one).


Frequency counting
------------------

Pandas makes frequency counts simple. Here's a new dataframe `freq`
containing the frequency counts of the values in the column
`kudos` in the dataframe `new_df`.

```
freq = new_df['kudos'].value_counts()
```

If you want the frequencies of fields which contain lists, then
explode that field, as in the section done above.

Reference: https://stackoverflow.com/questions/36004976/count-frequency-of-values-in-pandas-dataframe-column


Some reminders
--------------

`characters` is the original data, `charactersclean` is the comparable
data with the names cleaned up.

You can always assign an variable "to itself". In the variable
assignment `variable = expression` the right hand side `expression` of
the assignment is fully evaluated before the assignment happens to the
left hand side `variable` . So this is a common way and safe way of
working:

```
new_df = df
new_df = new_df.drop(['cleandate'], axis=1)
new_df = new_df.drop(['summary'], axis=1)
new_df = new_df[new_df['kudos'] > 0]
new_df.to_csv('name-of-file.csv')
```

Then if your processing comes off the rails, start over again with
`new_df = df`. `df` hasn't changed and has the original unmodified
data.
