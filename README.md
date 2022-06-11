ao3-tagging -- analysis of An Archive of Our Own
================================================


Purpose
-------

Data collection and analysis for Wey Turner's Honours thesis of 2022.

For the actual thesis see the repository ao3-tagging.


Structure of this repository
----------------------------

There are two parts to these programs:

 1. src/collect/ -- Downloading the tags from archiveofourown.org which
    match a query, adding those to a database of works.

 2. src/explore/ -- Exploratory data analysis and visualisation of the
    database. This includes exporting subsets of the database to
    comma-separated-values CSV format for use by analysis tools.

The database of works is a file in YAML format, in the data/database/
directory. YAML was chosen as it is easy to view, and easy to
manipulate in the Python programming language.

The raw data downloaded from AO3 is kept to allow
replication of this work, in the data/raw/
directory.

