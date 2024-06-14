# Bibtex2HTML
 Converts the entries in a Bibtex file into formatted HTML.
 
 Bibtex provides a way to save bibliographic information about journal articles.
 It is part of the TEX/LATEX system.
 This format is supported by a variety of commercial databases of peer-reviewed literature such as scientific journals, books, and conference proceedings.  For example, Scopus, Web of Science.
 Also desktop applications such as JabRef, Zotero.
 
 This Python program reads all Article entries in your Bibtex file, and converts them into an HTML file.
 I chose the HTML formatting to be readable.  The code can be modified to output in a different format if you prefer.
 
## Requirements
 - Python > 3.6, preferably an Anaconda distribution.
 - pip install bibtexparser
 - pip install pyperclip
 - pip install pybliometrics (optional, for Scopus lookup of citations counts).

## Command line
From an Anaconda command prompt:  

python MakeHtmlBibtex.py -i bibfile.bib -o htmlfile.html -a authorname -c

All command line arguments are optional. The input file (-i) should probably be given since the code will look for a particular file on my system, not yours.  The output file (-o) defaults to testbib.html.  
The optional authorname (-a) specifies an author's last name like Smith; then only articles that contain Smith as an author will be included.  
Citation count (-c) is optional, and will look up the number of article citations on Scopus.  It requires the pybliometrics package, a Scopus key, and must be run on a computer with licensed access to Scopus, like a university network.

The output is sorted by year (decreasing), then alphabetically by the last name of the first author.

The produced HTML file can be opened directly in a browser.  In addition, the HTML text, minus the preamble required by a browser, is copied into the clipboard.  This text can be pasted into e.g a Wordpress site.

A convenience program, bib2html.py, is included.  It uses PyQt5 to create a graphical user interface that drives MakeHtmlBibtex.