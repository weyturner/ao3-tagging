src/explore
===========

Exploratory data analysis and visualisation of the database. This
includes exporting subsets of the database to comma-separated-values
CSV format for use by analysis tools.


src/explore/table/
------------------

These programs create tables from the YANG database. The table can be
displayed or saved as a CSV file for use by analytical software.

 - data-table.py: create a square table

 - histogram-table.py: create a frequency table


src/explore/pandas/
-------------------

These programs contain pandas utility code:

 - load_data_table.py: load the .CSV data table into a Pandas
   dataframe and apply Pandas types to the columns.

 - character-attributes.py: create a `character_attributes` dataframe
   indexed by `characterclean` with columns of `species` and `sex`.


src/explore/notebooks/
----------------------

Jupyter notebooks used for data analysis, tables and graphs.
