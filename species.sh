#!/bin/sh

mkdir ws
time  bzcat specieswiki-20150426-pages-articles.xml.bz2 | head -n 100000 | python wikispecies-filter.py
python wikispecies-uniquer.py ws/thoughts.json && mv ws/thoughts.json.uniq ws/thoughts.json
(cd ws && zip ../ws.brz * && cd ..)

