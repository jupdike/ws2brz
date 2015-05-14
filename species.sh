#!/bin/sh

mkdir -p ws
time  bzcat specieswiki-20150426-pages-articles.xml.bz2 | python wikispecies-filter.py
#time  bzcat specieswiki-20150426-pages-articles.xml.bz2 | head -n 1000000 | python wikispecies-filter.py
time  python wikispecies-uniquer.py ws/thoughts.json && mv ws/thoughts.json.uniq ws/thoughts.json
(cd ws && zip ../ws.brz * && cd ..)

