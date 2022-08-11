#!/usr/bin/env python3
#
# clean-db-deep-space-nine.py
# Clean a database of Deep Space Nine titles.
#
# Some cleaning is done whilst parsing the AO3 webpages into the
# database with parse-pages-into-db.py. But that program has no
# knowledge of the content, other than it being a AO3 webpage.
#
# This program brims with specific knowledge about Deep Space Nine and
# cleans the database accordingly.
# (eg: Mirror Kira Nerys is a different character to Kira Nerys for the
# purposes of this study, as their sex changes, but that isn't the case
# for other Mirror characters, who merely adopt a different personality)
#
# Run as follows:
#
#  cd ao3-tagging
#  src/collect/clean-db-deep-space-nine.py -i data/database/20220612.yaml -o data/database/20220612-clean.yaml > data/database/20220612-unseen.txt
#
# This program can usefully use
#  src/explore/histogram-table/histogram-table.py
# to judge the effects of changes.
#
# Copyright © Wey Turner, 2022.
# SPDX-License-Identifier: GPL-2.0-only

import argparse
import datetime
import functools
import re
import yaml
import sys

# Clean up names.
#
# For accurate statistics we want all of these normalised to one
# 'canonical' name, say "Alpha Bravo" in this example:
#   - "Alpha Bravo (mentioned)"  -- normalised via the delete_list
#   - "A Bravo"                  -- normalised via the synonym_dict
#   - "Mirror Alpha Bravo"       -- normalised via the delete_list or the
#                                   synonym_dict, avoiding false corrections.
# To help build these tables the cast_set contains all the canonical names:
# normalised names not found there are printed.
#
# How these tables work:
#   - if a phrase in the zap_dict is found within a name, then replace
#     the name with its dictionary value.
#   - every phrase in the delete_list is removed from names
#   - the names have Australian English spacing restored
#   - the name is searched for in synonym_dict, a synonym name which is found
#     in the dictionary is replaced by its canonical name
#   - the cast_set is checked, if the name is not found it is printed
#     for further investigation.
#
# The number of alterations is tracked, as that is useful for statistical
# measures of error (if we assume all the changes are wrong, that sets an
# upper bound on the bias introduced by this data cleaning).
#
# Future enhancement: read the tables in from configuration files,
# which would make this program generic rather than particular to Deep
# Space Nine.


class Ds9cast:
    NON_CAST = 'non-cast'

    # Statistics
    names_altered_count = 0

    # Any occurance of this phrase in the name results in the name being
    # replaced entirely.
    zap_dict = {
        '(OC)': NON_CAST,
        'OC': NON_CAST,
        'Original Character': NON_CAST
    }

    # Attributes which can be safely deleted from names.
    #
    # Future enhancement, this could be a list of regular expressions, but
    # that would likely to be confusing to some readers of the code:
    #  eg: '(past-relationship)'            -- simple string
    #      r' *\(past\-relationship\) *$'   -- regular expression
    # So let's keep it simple until it needs to become more complex.
    delete_list = [
        ' (Changeling)',
        ' (implied/referenced)',
        ' (nebulously one-sided)',
        ' (past)',
        ' (relevant)',
        ' - Character',
        ' - Relationship',
        ' briefly mentioned',
        ' is discussed',
        '(  )',
        '()',
        '(?)',
        '(ACoTaR)',
        '(Background)',
        '(DS9)',
        '(Deceased)',
        '(Deep Space Nine)',
        '(Implied',
        '(Implied)',
        '(Implied-Past)',
        '(Keiko mentioned)',
        '(Mentioned)',
        '(One-Sided)',
        '(Past)'
        '(Ro Laren mentioned)',
        '(ST DS9)',
        '(Star Trek DS9)',
        '(Star Trek Deep Space Nine)',
        '(Star Trek)',
        '(Star Trek: DS9)',
        '(Star Trek:DS9)',
        '(Trill symbiont)',
        '(alluded to)',
        '(alluded)',
        '(alternate)',
        '(appears via PADD)',
        '(background)',
        '(both)',
        '(briefly)',
        '(but not really though)',
        '(cameo)',
        '(exes)',
        '(flashbacks)',
        '(flashbacks)',
        '(hinted at)',
        '(holographic)',
        '(implied',
        '(implied/referenced)',
        '(in absentia)',
        '(looming presence) - Character',
        '(looming presence)',
        '(mention)',
        '(mentioned) past ',
        '(mentioned)',
        '(mentionned)',  # typo
        '(mentionné)',
        '(minor)',
        '(mirror)',
        '(multiple hosts)',
        '(not really)',
        '(ocs mentioned)',
        '(ofcs mentioned)',
        '(offscreen)',
        '(one night stand)',
        '(one scene)',
        '(one sided)',
        '(one-sided)'
        '(one-sided?)',
        '(past relationship)'
        '(pre relationship)',
        '(pre-relationship)',
        '(reference)',
        '(referenced)',
        '(relationship)',
        '(side)',
        '(tragic)',
        '(voice)',
        '- relationship',
        'A  mention of',
        'AU ',
        'Background ',
        'Changeling ',
        'Changeling!',
        'Dr.',
        'Former ',
        'If you squint ',
        'Implied ',
        'Light ',
        'Mentioned ',
        'Mentioned Past ',
        'Mentions of ',
        'Minor ',
        'Mirror ',
        'One-sided ',
        'Past ',
        'Slight',
        'Smuggler ',
        'The Idea of ',
        'background ',
        'cameo',
        'casual ',
        'fem!',
        'mentioned',
        'mentions of ',
        'mildly implied',
        'minor ',
        'one sided',
        'one-sided',
        'onesided',
        'past ',
        'possibly onesided',
        'pre ',
        'pre-',
        'side ',
        'slight'
    ]

    # List of fanfic characters in canonical names
    known_set = {
        "Boq'ta",
        "Ch'Targh",
        "Cing'ta",
        "Darhe'el",
        "Dukat's Children",
        "Dukat's Mother",
        "Ee'char",
        "Goran'Agar",
        "Ikat'ika",
        "K'Ehleyr",
        "Keiko O’Brien",
        "Kirayoshi O'Brien",
        "Kotan Pa'Dar",
        "M'Pella",
        "Maihar'du",
        "Miles O'Brien",
        "Molly O'Brien",
        "N’garen",
        "Omet'iklan",
        "Remata'Klan",
        "Rotan'talag",
        "Rugal Pa'Dar",
        "T'Rul",
        "Taran'atar",
        "Vilix'pran",
        'Aamin Marritza',
        'Admiral Whatley',
        'Agent Cole',
        'Akellen Macet',
        'Akorem Laan',
        'Alexander Rozhenko',
        'Alon Ghemor',
        'Altovar',
        'Aluura',
        'Alynna Nechayev',
        'Amaro',
        'Ambassador Lojal',
        'Amsha Bashir',
        'Arandis',
        'Arissa',
        'Arjin',
        'Athra Dukat',
        'Audrid Dax',
        'Baby Changeling',
        'Bandee',
        'Bareil Antos',
        'Barin Troi',
        'Barkan Lokar',
        'Basso Tromac',
        'Bejal Otner',
        'Benjamin Sisko',
        'Benteen',
        'Boday',
        'Boheeka',
        'Borath',
        'Broca',
        'Broik',
        'Brunt',
        'Buck Bokai',
        'Cal Hudson',
        'Captain Solok',
        'Chalan Aroya',
        'Chester',
        'Corat Damar',
        'Corbin Entek',
        'Cox',
        'Curzon Dax',
        'Dax',
        'Dejar',
        'Deral',
        'Deyos',
        'Drex',
        'Dulath',
        'Dulmur',
        'Elias Vaughn',
        'Elim Garak',
        'Ellis Gareth',
        'Emergency Medical Hologram Mark II',
        'Emony Dax',
        'Enabran Tain',
        'Enina Tandro',
        'Entek',
        'Eris',
        'Erit',
        'Ezri Dax',
        'Fala Trentin',
        'Felix',
        'Female Changeling',
        'Furel',
        'Gaila',
        'Gariff Lucsly',
        'Gelnon',
        'Gilora Rejal',
        'Girani',
        'Glenon',
        'Gor',
        'Gowron',
        'Grilka',
        'Grimp',
        'Gul Jasad',
        'Gul Marratt',
        'Gul Revok',
        'Gul Rusot',
        'Gul Russol',
        'Gul Zarale',
        'Hagath',
        'Hanok',
        'Hanor Pren',
        'Iliana Ghemor',
        'Iloja of Prim',
        'Ishka',
        'Jabara',
        'Jack',
        'Jadzia Dax',
        'Jake Sisko',
        'Janel Tigan',
        'Jaro Essa',
        'Jas Holza',
        'Jennifer Sisko',
        'Joran Dax',
        'Joseph Sisko',
        'Judith Sisko',
        'Julian Bashir',
        'Kabo',
        'Kaga',
        'Kai Winn',
        'Kalandra',
        'Kalita',
        'Kang',
        'Karen Loews',
        'Kasidy Yates',
        'Keevan',
        'Kel Lokar',
        'Kela Idaris',
        'Kelas Parmak',
        'Keldar',
        'Kesha',
        'Kilana',
        'Kimara Cretak',
        'Kira Meru',
        'Kira Nerys',
        'Kira Pohl',
        'Kira Reon',
        'Kira Taban',
        'Koloth',
        'Kor',
        'Koval',
        'Kukalaka',
        'Kurn',
        'Laas',
        'Laira',
        'Lauren',
        'Leeta',
        'Legate Kell',
        'Lela Dax',
        'Lenara Kahn',
        'Letant',
        'Lewis Zimmerman',
        'Leyton',
        'Li Nalas',
        'Lieutenant Watley',
        'Lisa Cusak',
        'Lorit Akrem',
        'Luaran',
        'Lupaza',
        'Lursa',
        'Luther Sloan',
        'Lwaxana Troi',
        'Lysia Arlin',
        'Mardah',
        'Mareel',
        'Martok',
        'Mavek',
        'Mekor Dukat',
        'Melora Pazlar',
        'Meya Rejal',
        'Michael Eddington',
        'Mila Garak',
        'Mora Pol',
        'Morn',
        'Mullibok',
        'Nal Dejar',
        'Nareeya',
        'Natima Lang',
        'Neral',
        'Niala Damar',
        'Nilani Kahn',
        'Nilva',
        'Nog',
        'Norvo Tigan',
        'Odo',
        'Onara',
        'Opaka',
        'Ornak',
        'Palandine',
        'Palis Delon',
        'Parn',
        'Patrick',
        'Pel',
        'Prinadora',
        'Procal Dukat',
        'Pythas Lok',
        'Q',
        'Quark',
        'Raymer',
        'Rebecca Sisko',
        'Rebecca Sullivan',
        'Reese',
        'Renhol',
        'Richard Bashir',
        'Rionoj',
        'Rom',
        'Sakal Damar',
        'Sarah Sisko',
        'Sarina Douglas',
        'Shakaar Edon',
        'Sirella',
        'Skrain Dukat',
        'Solbor',
        'Tagana',
        'Tahna Los',
        'Tamal',
        'Tekeny Ghemor',
        'Telnorri',
        'Thomas Riker',
        'Thrax',
        'Tobin Dax',
        'Tora Naprem',
        'Tora Ziyal',
        'Torias Dax',
        'Trevean',
        'Vaatrik Pallra',
        'Vance',
        'Vash',
        'Vedek Nane',
        'Verad',
        'Vic Fontaine',
        'Vreenak',
        'Weyoun',
        'William Ross',
        'Winn Adami',
        'Worf',
        'Wykoff',
        'Yanas Tigan',
        'Yareth',
        'Yedrin Dax',
        'Yelgrun',
        'Zarale',
        'Zek',
        'Ziranne Idaris'
    }

    # Cast members known by other names
    synonym_dict = {
        "Athra Dukat's wife": 'Athra Dukat',
        "Benjamin Sisko's Authoritative Voice": 'Benjamin Sisko',
        "Ch’targh": "Ch'Targh",
        "Clone!Miles O'Brien": "Miles O'Brien",
        "Cäpt'n Sisko": 'Benjamin Sisko',
        "Damar's Son": 'Sakal Damar',
        "Damar's Wife": 'Niala Damar',
        "Dukat's Father | Procal Dukat": 'Procal Dukat',
        "Dukat's Wife | Athra Dukat": 'Athra Dukat',
        "Dukat's ex Wife | Athra Dukat": 'Athra Dukat',
        "Dukat's kids": "Dukat's Children",
        "Dukat's wife": "Athra Dukat's wife",
        "Enabran Tain's ghost": 'Enabran Tain',
        "Ezri Dax's ""Far Beyond the Stars"" Universe Character": 'Ezri Dax',
        "Ikat'ika | Jem'Hadar First": "Ikat'ika",
        "Keiko O' Brien ()": "Keiko O'Brien",
        "Keiko O' Brien": "Keiko O’Brien",
        "Keiko O'Brien": "Keiko O'Brien",
        "Keiko o'brien": "Keiko O’Brien",
        "Keyko O'Brien": "Keiko O’Brien",
        "Mentioning's of Dukat's Wife": 'Athra Dukat',
        "Mile O'Brien (One sided)": "Miles O'Brien",
        "Miles O'Brian": "Miles O’Brien",
        "Miles O'Brien ()": "Miles O'Brien",
        "Miles O'Brien (friendship)": "Miles O'Brien",
        "Miles O'Brien by mention only": "Miles O'Brien",
        "Miles O'Brien's voice": "Miles O'Brien",
        "Miles O’Brien": "Miles O'Brien",
        "Mirror Miles O'Brien": "Miles O'Brien",
        "O'Brien": "Miles O'Brien",
        "Odo'Ital": 'Odo',
        "Odo’iTal": 'Odo',
        "Quark (in the back of Quark's mind)": 'Quark',
        "Quark's Mother": 'Ishka',
        "Remata 'Klan": "Remata'Klan",
        "Smiley O'brien": "Miles O'Brien",
        "Sub-Commander T'Rul": "T'Rul",
        "Tschief O'Brien": "Miles O'Brien",
        "dukat's children": "Dukat's Children",
        "mention o'brian": "Miles O'Brien",
        "miles O'Brien": "Miles O'Brien",
        "miles o'brien": "Miles O'Brien",
        "sort of dukat but really he's just around to be murdered": 'Skrain Dukat',
        ' Kasidy Yates': 'Kasidy Yates',
        '(the idea of) Elim Garak': 'Elim Garak',
        '-Bashir': 'Julian Bashir',
        'A  mention of Julian Bashir': 'Julian Bashir',
        'Admiral Nechayev (Star Trek)': 'Alynna Nechayev',
        'Admiral Ross': 'William Ross',
        'Agent Cole (Star Trek)': 'Agent Cole',
        'Agent Julian Bashir of MI6': 'Julian Bashir',
        'Alexander': 'Alexander Rozhenko',
        'Alternate Odo': 'Odo',
        'Alternate Timeline Odo (Children Of Time)': 'Odo',
        'Altovar (Star Trek)': 'Altovar',
        'Altovar (reference)': 'Altovar',
        'Amaro (Star Trek)': 'Amaro',
        'Ambassador Worf': 'Worf',
        'Anastasia Komananov': 'Kira Nerys',
        'Anjohl Tennan': 'Skrain Dukat',
        'Arandis (Star Trek)': 'Arandis',
        'Arissa (Star Trek)': 'Arissa',
        'Arjin (Star Trek)': 'Arjin',
        'Bareil': 'Bareil Antos',
        'Bariel': 'Bareil Antos',
        'Barin': 'Barin Troi',
        'Barkan': 'Barkan Lokar',
        'Bashir': 'Julian Bashir',
        'Ben Sisko': 'Benjamin Sisko',
        'Ben': 'Benjamin Sisko',
        'Benjamin': 'Benjamin Sisko',
        'Benjamine Sisko': 'Benjamin Sisko',
        'Benny Russell': 'Benjamin Sisko',
        'Bi Julian Bashir': 'Julian Bashir',
        'Calvin Hudson': 'Cal Hudson',
        'Captain Bashir': 'Julian Bashir',
        'Captain Benteen': 'Benteen',
        'Captain Boday': 'Boday',
        'Captain Cusak': 'Lisa Cusak',
        'Captain Julian Bashir': 'Julian Bashir',
        'Captain Raymer': 'Raymer',
        'Captain Sisko': 'Benjamin Sisko',
        'Captain Solok': 'Captain Solok',
        'Chalon Aroya': 'Chalan Aroya',
        'Chancellor Martok': 'Martok',
        'Changeling Julian Bashir': 'Julian Bashir',
        'Chester the Cat': 'Chester',
        'Commander Hudson': 'Cal Hudson',
        'Commander Sisko': 'Benjamin Sisko',
        'Constable Odo': 'Odo',
        'Constable Quark': 'Quark',
        'Constäbbel Odo': 'Odo',
        'Counselor Telnorri': 'Telnorri',
        'Cousin Gaila': 'Gaila',
        'Curson': 'Curzon Dax',
        'Curzon': 'Curzon Dax',
        'DR cox-': 'Cox',
        'Damar': 'Corat Damar',
        'Darlene Kursky': 'Jadzia Dax',
        'Dax (Trill symbiot)': 'Dax',
        'Dax Symbiont': 'Dax',
        'Dax symbiont': 'Dax',
        'Doctor Girani': 'Girani',
        'Doctor Julian Bashir': 'Julian Bashir',
        'Doctor Lenara Kahn': 'Lenara Kahn',
        'Doctor Mora Pol': 'Mora Pol',
        'Doctor Mora Pol': 'Mora Pol',
        'Doctor Mora': 'Mora Pol',
        'Dr Bashir': 'Julian Bashir',
        'Dr. Cox': 'Cox',
        'Dr. Girani': 'Girani',
        'Dr. Hippocrates Noah': 'Benjamin Sisko',
        'Dr. Kalandra': 'Kalandra',
        'Dr. Karen Loews': 'Karen Loews',
        'Dr. Lewis Zimmerman': 'Lewis Zimmerman',
        'Dr. Mora Pel': 'Mora Pol',
        'Dr. Mora': 'Mora Pol',
        'Dr. Noah': 'Benjamin Sisko',
        'Dr. Wykoff': 'Wykoff',
        'Dr.Cox': 'Cox',
        'Dragon!Garak': 'Elim Garak',
        'Dukat (Star Trek)': 'Skrain Dukat',
        'Dukat (implied': 'Skrain Dukat',
        'Dukat': 'Skrain Dukat',
        'Dukats wife': 'Athra Dukat',
        'EMH Julian Bashir': 'Emergency Medical Hologram Mark II',
        'Edon Shaakar': 'Shaakar Edon',
        'Eim Garak': 'Elim Garak',
        'Elim Garrik': 'Elim Garak',
        'Enabran Tain (reference)': 'Enabran Tain',
        'Enabran Tain and non-canon characters': 'Enabran Tain',
        'Eomony Dax': 'Emony Dax',
        'Ezri Tigan': 'Ezri Dax',
        'Ezri': 'Ezri Dax',
        'FOC': NON_CAST,
        'Fake Bashir': 'Julian Bashir',
        'Falcon': "Miles O'Brien",
        'Fem!Gul Zarale': 'Gul Zarale',
        'Fem!Li Nalas': 'Li Nalas',
        'Female Founder': 'Female Changeling',
        'Future Odo': 'Odo',
        'Future Quark': 'Quark',
        'Gabriel Bell': 'Benjamin Sisko',
        'Gaia Odo': 'Odo',
        'Garak (relationship)': 'Elim Garak',
        'Garak is only': 'Elim Garak',
        'Garak': 'Elim Garak',
        'General Martok': 'Martok',
        'Glinn Damar': 'Corat Damar',
        'Grand Nagus Rom': 'Rom',
        'Guhl Dukat': 'Skrain Dukat',
        'Gul Damar': 'Corat Damar',
        'Gul Dukat': 'Skrain Dukat',
        'Gul Parn': 'Parn',
        'Gul Zarale but girl': 'Zarale',
        'High Nagus Rom': 'Rom',
        'Hippocrates Noah': 'Benjamin Sisko',
        'Honey Bare': 'Jadzia Dax',
        'Human!Garak': 'Elim Garak',
        'Iliana': 'Iliana Ghemor',
        'Illiana Ghemor': 'Iliana Ghemor',
        'Iloja of Prime': 'Iloja of Prim',
        'Iloja': 'Iloja of Prim',
        'Imaginary Elim Garak': 'Elim Garak',
        'Infant Changeling': 'Baby Changeling',
        'Intendant': 'Kira Nerys',
        'Jadzea Dax': 'Jadzia Dax',
        'Jadzia Daz': 'Jadzia Dax',
        'Jadzia Idaris': 'Jadzia Dax',
        'Jadzia briefly': 'Jadzia Dax',
        'Jadzia is  literally one time': 'Jadzia Dax',
        'Jadzia': 'Jadzia Dax',
        'Jake': 'Jake Sisko',
        'Jasad': 'Gul Jasad',
        'Jennifer': 'Jennifer Sisko',
        'Joran Dax (memories)': 'Joran Dax',
        'Juilan Bashir': 'Julian Bashir',
        'Julain Bashir': 'Julian Bashir',
        'Julan Bashir': 'Julian Bashir',
        'Jules Bashir': 'Julian Bashir',
        'Julian Bashier': 'Julian Bashir',
        'Julian Bashir (2371)': 'Julian Bashir',
        'Julian Bashir (Just for plot convenience)': 'Julian Bashir',
        'Julian Bashir (comatose)': 'Julian Bashir',
        'Julian Bashir EMH': 'Emergency Medical Hologram Mark II',
        'Julian Bashir and Mirror-Bashir': 'Julian Bashir',
        'Julian Bashri': 'Julian Bashir',
        'Julian bashir': 'Julian Bashir',
        'Julian': 'Julian Bashir',
        'Julius Eaton': 'Julian Bashir',
        'Kahn': 'Lenara Kahn',
        'Kai Opaka': 'Opaka',
        'Kasidy Yates-Sisko': 'Kasidy Yates',
        'Kasidy': 'Kasidy Yates',
        'Kassidy Yates':  'Kasidy Yates',
        'Kay Eaton': 'Kira Nerys',
        'Keevan 2': 'Keevan',
        'Keiko': "Keiko O’Brien",
        'Kia Winn': 'Winn Adami',
        'Kira Nerys ()': 'Kira Nerys',
        'Kira Neyrs': 'Kira Nerys',
        'Kira': 'Kira Nerys',
        'Kiry Nerys': 'Kira Nerys',
        'Klingon Chef': 'Kaga',
        'Komahnder Worf': 'Worf',
        'Kukalaka (Stark Trek)': 'Kukalaka',
        'Leela Dax': 'Lela Dax',
        'Leeta (Leeta )': 'Leeta',
        'Legate Damar': 'Corat Damar',
        'Lenara Kahn but its just  in passing': 'Lenara Kahn',
        'Li Nalas but girl': 'Li Nalas',
        'Lieutenant Commander Jadzia Dax': 'Jadzia Dax',
        'Lupasa': 'Lupaza',
        'Lwaxana': 'Lwaxana Troi',
        'MOC': NON_CAST,
        'Major Kira': 'Kira Nerys',
        'Martok (emails)': 'Martok',
        'Mavik': 'Mavek',
        'Meru': 'Kira Meru',
        'Miles Obrien': "Miles O'Brien",
        'Miles': "Miles O'Brien",
        'Minor rom': NON_CAST,  # "minor" as in small role
        'Mirror Bariel Antos': 'Bariel Antos',
        'Mirror Benjamin Sisko': 'Benjamin Sisko',
        'Mirror Brunt': 'Brunt',
        'Mirror Elim Garak': 'Elim Garak',
        'Mirror Jadzia Dax': 'Jadzia Dax',
        'Mirror Julian Bashir': 'Julian Bashir',
        'Mirror Kira Nerys': 'Kira Nerys',
        'Mirror Odo': 'Odo',
        'Mirror Quark': 'Quark',
        'Mirror Worf': 'Work',
        'Mirror-Bashir': 'Julian Bashir',
        'Molly (DS9: Children of Time)': "Molly O'Brien",
        'Molly O’Brien': "Molly O'Brien",  # Unicode character
        'Molly': "Molly O'Brien",
        'Mora Pel': 'Mora Pol',
        'Mora': 'Mora Pol',
        'Morn only has a cameo fitting of his character': 'Morn',
        'Mäytscher Kira': 'Kira Nerys',
        'Nagus Rom': 'Rom',
        'Naprem': 'Tora Naprem',
        'Natima': 'Natima Lang',
        'Nerys': 'Kira Nerys',
        'Noah': 'Benjamin Sisko',
        'Nurse Jabara': 'Jabara',
        'OC': NON_CAST,
        'OFC': NON_CAST,
        'OMC': NON_CAST,
        'Odo ()': 'Odo',
        'Odo Ital': 'Odo',
        'Odo Mentioned': 'Odo',
        'Odo relationship': 'Odo',
        'Oldo': 'Odo',
        'One-Sided Julian Bashir': 'Julian Bashir',
        'Onesided Pythas Lok': 'Pythas Lok',
        'Opaka Sulan': 'Opaka',
        'Original Bajoran Character': NON_CAST,
        'Original Bajoran Female Character': NON_CAST,
        'Original Bajoran Male Character': NON_CAST,
        'Original Cardassian Character': NON_CAST,
        'Original Character(s)': NON_CAST,
        'Original Female Character': NON_CAST,
        'Original Female Character(s)': NON_CAST,
        'Original Male Character': NON_CAST,
        'Original Male Character(s)': NON_CAST,
        'Other(s)': NON_CAST,
        'Others': NON_CAST,
        'Owner of the Klingon Restaurant': 'Kaga',
        'Pel (Star Trek: Deep Space Nine)': 'Pel',
        'Pel (past... possibly future?)': 'Pel',
        'Possible Dukat': 'Skrain Dukat',
        'Prophet Damar': 'Corat Damar',
        'Prophet Dukat': 'Skrain Dukat',
        'Prophet Odo': 'Odo',
        'Quar': 'Quark',   # typo
        'Quark (  )': 'Quark',
        'Quark ()': 'Quark',
        'Quark (?)': 'Quark',
        'Quark (Star Trek)': 'Quark',
        'Quark (in a sense)': 'Quark',
        'Quark (in spirit)': 'Quark',
        'Quark (you can feel his spirit lingering there)': 'Quark',
        'Quark Math Program': 'Quark',
        'Quark flirting': 'Quark',
        'Reader': NON_CAST,
        'Reese (Deep Space Nine The Siege of AR-558)': 'Reese',
        'Rugal': "Rugal Pa'Dar",
        'Rusot': 'Gul Rusot',
        'Shaakar Edon': 'Shakaar Edon',
        'Shakaar': 'Shakaar Edon',
        'Sisco': 'Benjamin Sisko',
        'Sisko ( )': 'Benjamin Sisko',
        'Sisko the Emissary': 'Benjamin Sisko',
        'Sisko': 'Benjamin Sisko',
        'Sloan': 'Luther Sloan',
        'Sloane': 'Luther Sloan',
        'Smuggler Odo': 'Odo',
        'Tain': 'Enabran Tain',
        'Tentacle Monster': NON_CAST,
        'The Diabolical Mr. Garak': 'Elim Garak',
        'The Emissary': 'Benjamin Sisko',
        'The Female Changeling': 'Female Changeling',
        'The Female Founder': 'Female Changeling',
        'The Grand Nagus': 'Zek',
        'The Intendant': 'Kira Nerys',
        'Tora Ziyal (One-Sided)': 'Tora Ziyal',
        'Tora Ziyal (one night stand)': 'Tora Ziyal',
        'Tora Ziyal (only)': 'Tora Ziyal',
        'Torah Naprem': 'Tora Naprem',
        'Toran': 'Tora Naprem',
        'Tschatzia Däcks': 'Jadzia Dax',
        'Tschulien Bäschier': 'Julian Bashir',
        'Vampire!Garak': 'Elim Garak',
        'Vampire!Julian': 'Julian Bashir',
        'Vedek Antos Bareil': 'Bareil Antos',
        'Vedek Bariel': 'Bariel Antos',
        'Vedik Bariel': 'Bariel Antos',    # typo
        'Verad Dax': 'Verad',
        'Weyoun 1': 'Weyoun',
        'Weyoun 10': 'Weyoun',
        'Weyoun 2': 'Weyoun',
        'Weyoun 3': 'Weyoun',
        'Weyoun 4': 'Weyoun',
        'Weyoun 5': 'Weyoun',
        'Weyoun 6': 'Weyoun',
        'Weyoun 7': 'Weyoun',
        'Weyoun 8': 'Weyoun',
        'Weyoun 9': 'Weyoun',
        'Weyoun Seven': 'Weyoun',
        'Weyoun6': 'Weyoun',
        'Weyoun7': 'Weyoun',
        'Winn': 'Winn Adami',
        'Worf (In Spirit)': 'Worf',
        'Worf (Star Trek: TNG': 'Worf',
        'Worf (Star Trek:TNG': 'Worf',
        'Worf (Star Trek:TNG/DS9)': 'Worf',
        'Worf (short apparition)': 'Worf',
        'Work': 'Worf',
        'Yates': 'Kasidy Yates',
        'You': NON_CAST,
        'Zarale': 'Gul Zarale',
        'Ziyal': 'Tora Ziyal',
        'benjamin sisko': 'Benjamin Sisko',
        'brief mirror!opaka': 'Opaka',
        'dragon!Dukat': 'Skrain Dukat',
        'dragon!Dukat': 'Skrain Dukat',
        'elim garak': 'Elim Garak',
        'female characters': NON_CAST,
        'female founder': 'Female Changeling',
        'female': NON_CAST,
        'his wife': NON_CAST,
        'implied Bashir': 'Julian Bashir',
        'implied Elim Garak': 'Elim Garak',
        'implied Jadzia Dax': 'Jadzia Dax',
        'implied Jadzia': 'Jadzia Dax',
        'implied Julian Bashir': 'Julian Bashir',
        'intendent kira': 'Kira Nerys',
        'jadzia dax': 'Jadzia Dax',
        'julian bashir': 'Julian Bashir',
        'just Garak really': 'Elim Garak',
        'kelas parmak': 'Kelas Parmak',
        'kilana': 'Kilana',
        'kira nerys': 'Kira Nerys',
        'kukkalakka': 'Kukalaka',
        'male': NON_CAST,
        'menion of Rom': 'Rom',
        'mention odo': 'Odo',
        'mention of Julian Bashir': 'Julian Bashir',
        'mirror Jack': 'Jack',
        'mirror Sloan': 'Luther Sloan',
        'mirror!winn because i have A Problem': 'Winn Adami',
        'morn': 'Morn',
        'neurodivergent Julian': 'Julian Bashir',
        'odo solid': 'Odo',
        'odo': 'Odo',
        'other females': NON_CAST,
        'other males': NON_CAST,
        'possibly  Julian': 'Julian Bashir',
        'pregnant Julian Bashir': 'Julian Bashir',
        'technically Keiko Ishikawa': "Keiko O'Brien",
        'the (figurative) ghost of Jennifer Sisko': 'Jennifer Sisko',
        'two-sided Julian Bashir': 'Julian Bashir',
        'unknown character': NON_CAST,
        'unknown female character': NON_CAST,
        'unknown male character': NON_CAST,
        'various ocs': NON_CAST,
        'various ofcs': NON_CAST,
        'vedek bariel': 'Bariel Antos',
        'weyoun 6': 'Weyoun',
        'weyoun': 'Weyoun',
        'with a dash of Garak': 'Elim Garak',
        'with a guest appearance by Elim Garak': 'Elim Garak',
        'zek': 'Zek'
    }


    def __init__(self):
        self.unseen_set = set()


    def normal_name(self, text):
        # If there is any phrase in the zap dict then replace the entire name.
        for s in self.zap_dict:
            if s in text:
                return self.zap_dict[s]

        # Substrings which can be deleted.
        for d in self.delete_list:
            text = text.replace(d, '')
            text = text.strip()

        # Normalise to canonical name.
        if text in self.synonym_dict:
            text = self.synonym_dict[text]

        # Record the name if not a cast member then replace
        # the name with the non-cast phrase.
        if not text in self.known_set:
            self.unseen_set.add(text)
            text = self.NON_CAST

        return text


    def normal_list(self, name_list):
        normal_s = set()
        for name in name_list:
            normal_s.add(self.normal_name(name))
        normal_l = list(normal_s)
        normal_l.sort()
        return normal_l

    def normal_pair(self, pair):
        if pair.find('&') > -1:
            style = 'amp'
        elif pair.find('/') > -1:
            style = 'slash'
        else:
            style = 'other'

        # Normalise relationship
        pair_l = [s.strip() for s in re.split('[/&]', pair)]
        pair_l[0] = self.normal_name(pair_l[0])
        pair_l[1] = self.normal_name(pair_l[1])
        pair_l.sort()

        if style == 'amp':
            pair = '{} & {}'.format(pair_l[0], pair_l[1])
        elif style == 'slash':
            pair = '{}/{}'.format(pair_l[0], pair_l[1])
        return pair


    def normal_pair_list(self, pair_list):
        normal_s = set()
        for pair in pair_list:
            normal_s.add(self.normal_pair(pair))
        normal_l = list(normal_s)
        normal_l.sort()
        return normal_l


    def unseen(self):
        return self.unseen_set


# Collect command line arguments.
def command_line_args():
    ap = argparse.ArgumentParser(description='Clean database',
                                 epilog='Copyright © Wey Turner, 2022. ' +
                                        'License <https://spdx.org/licenses/' +
                                        'GPL-2.0-only.html>')
    ap.add_argument('-i',
                    '--input-database',
                    type=str,
                    default='',
                    required=True,
                    help='Input database to clean')
    ap.add_argument('-o',
                    '--output-database',
                    type=str,
                    required=True,
                    help='Output database of cleaned data')
    return ap.parse_args()


# Key field to the database.
# It looks like AO3 maintain a work identifier, let's assume that's unique.
def database_key(d):
    return int(d['id'])



if __name__ == "__main__":

    args = command_line_args()
    cleandate = str(datetime.datetime.now())
    database_out = list()

    with open(args.input_database, 'r') as in_f:
        database_in = yaml.load(in_f, Loader=yaml.SafeLoader)

    ds9cast = Ds9cast()

    for work in database_in:
        # Normalise names in characters
        if 'characters' in work:
            work['charactersclean'] = ds9cast.normal_list(work['characters'])
        # Normalise names in relationships
        # We leave 'relationships' alone as that's exactly as in AO3.
        # Update the other variables if they exist in the database.
        if 'relationshipspax' in work:
            work['relationshipspax'] = ds9cast.normal_list(work['relationshipspax'])
        if 'relationshipspaxslash' in work:
            work['relationshipspaxslash'] = ds9cast.normal_list(work['relationshipspaxslash'])
        if 'relationshipspaxamp' in work:
            work['relationshipspaxamp'] = ds9cast.normal_list(work['relationshipspaxamp'])
        if 'relationshipspair' in work:
            work['relationshipspair'] = ds9cast.normal_pair_list(work['relationshipspair'])
        if 'relationshipspairamp' in work:
            work['relationshipspairamp'] = ds9cast.normal_pair_list(work['relationshipspairamp'])
        if 'relationshipspairslash' in work:
            work['relationshipspairslash'] = ds9cast.normal_pair_list(work['relationshipspairslash'])
        work['cleandate'] = cleandate
        database_out.append(work)

    # Write output database
    database_out.sort(key=database_key)
    with open(args.output_database, 'w') as out_f:
        yaml.dump(database_out,
                  out_f,
                  allow_unicode=True,
                  width=79)

    # Characters we have classified yet
    for u in ds9cast.unseen():
        print(u)
