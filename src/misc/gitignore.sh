#!/bin/bash --
#
# Create .gitignore file with
#   ./gitignore.sh >> ../../.gitignore
# adjusting the path as required.

cat <<EOF
# ao3-tagging/.gitignore
# Made by src/misc/gitignore.sh

# Particular to ao3-tagging.
Untitled*.ipynb

# Remainder of file from <https://www.toptal.com/developers/gitignore>.
EOF

CURLOPTS="--silent --location"

# To see the list of product codes
#   https://www.toptal.com/developers/gitignore/api/list
# List each of the products which manipulate this repository.
PRODUCTS="git"
# Remainder in alphabetical order.
PRODUCTS+=",emacs"
PRODUCTS+=",juypternotebooks"
PRODUCTS+=",linux"
PRODUCTS+=",macos"
PRODUCTS+=",python"
PRODUCTS+=",visualstudiocode"
PRODUCTS+=",windows"

curl $CURLOPTS "https://www.toptal.com/developers/gitignore/api/$PRODUCTS"
