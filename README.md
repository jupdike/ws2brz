# ws2brz - Wikispecies to .BRZ

To use, first get the latest big xml dump (DATE-pages-articles.xml.bz2) from here:

- [https://dumps.wikimedia.org/specieswiki/20150426/][1]

For example,

- [https://dumps.wikimedia.org/specieswiki/20150426/specieswiki-20150426-pages-articles.xml.bz2][2]

Next put the file in this folder and run

    sh species.sh

This will execute the wikispecies-filter.py script and then the wikispecies-uniquer.py
to do the final cleanup, finally creating a .brz zip file with those .json text files.

Simply import the ws.brz file to use.

# Development and Testing

To test on a subset of the data, use this:

    mkdir ws
    time  bzcat specieswiki-20150426-pages-articles.xml.bz2 | head -n 100000 | python wikispecies-filter.py
    python wikispecies-uniquer.py ws/thoughts.json && mv ws/thoughts.json.uniq ws/thoughts.json
    cd ws && zip ../ws.brz * && cd ..)

Possibly you might want to remove the big uncompressed ws folder when finished.

  [1]: https://dumps.wikimedia.org/specieswiki/20150426/
  [2]: https://dumps.wikimedia.org/specieswiki/20150426/specieswiki-20150426-pages-articles.xml.bz2

