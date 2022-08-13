src/explore/notebooks/ -- Jupyter notebooks for data analysis
=============================================================

The notebook is started from this directory. That's most easily done
by starting Jupyter, then navigating to this directory and
double-clicking on the .ipynb notebook file.

By following this convention the path to the .CSV file which is loaded
into the dataframe is `../../../data/database/20220612.csv`.

If a notebook writes a .CSV file then those files start with the name
of the notebook. Then an analysis error evident in the .CSV is easily
traced back to the notebook.  For convenience those .CSV files are
also contained in the directory `src/explore/notebooks/`.


Utility notebooks
=================


base.ipynb
----------

This contains a program to load the dataframe `df` from the main .CSV
file, adjust the datatypes on the dataframe, and narrow the dataframe
to completed works after 2010.


character-attributes.ipynb
--------------------------

This creates a dataframe with the `sex` and `species` of many of the
characters, using the character's `characterclean` names.  This can be
merged with a dataframe for analysis.


Notebooks which produce tables
==============================

As well as producing a table, these notebooks create a .CSV for each
table.


crosstab.ipynb
--------------

This cross-tabulates slash relationship pairs against non-list
categorical variables such as `rating`.


frequency.ipynb
---------------

Calculates the frequency of some categorical variables which are
lists, such as `relationshipspairsslash`.


sum-comments-hits-kudos.ipynb
-----------------------------

Calculates the summed works, comments, hits and kudos for all
`charactersclean` and all `relationshipspairslash`.


Notebooks which are used interactively
======================================


freeform-explorer.ipynb
-----------------------

This explores the open-ended `freeforms` story tags which authors
apply to their works.

It loads the dataframe and provides functions for tabular
exploration. These currently are:

 * `freeform()` to list the freeforms (open-ended story tags)
   associated with a character pair doing slash

 * `mentions()` to search a column, and the report the frequences in
   another column of those matching rows.  This is a generalisation of
   `freeforms()`.
