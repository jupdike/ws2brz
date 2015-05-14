# ws2brz - Wikispecies to .BRZ

To use, first get the latest big xml dump (DATE-pages-articles.xml.bz2) from here:

- [https://dumps.wikimedia.org/specieswiki/20150426/][1]

For example,

- [https://dumps.wikimedia.org/specieswiki/20150426/specieswiki-20150426-pages-articles.xml.bz2][2]

Next put the file in this folder and run <tt>species.sh</tt>

This will execute the wikispecies-filter.py script and then the wikispecies-uniquer.py
to do the final cleanup, finally creating a .brz zip file with those .json text files.

Simply import the .brz file to use.


  [1]: https://dumps.wikimedia.org/specieswiki/20150426/
  [2]: https://dumps.wikimedia.org/specieswiki/20150426/specieswiki-20150426-pages-articles.xml.bz2
  
