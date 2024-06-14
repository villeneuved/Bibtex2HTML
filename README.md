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

## Sample HTML output

<h1>Attosecond Science Publications</h1>
<div style="clear:both;"><h3>2020</h3></div>
<div style="width:90%;padding:0.5em 0px 0.5em 0px;border-bottom:thin solid #0000ff;"><span>Tomoyuki Endo, Simon P. Neville, Vincent Wanie, Samuel Beaulieu, Chen Qu, Jude Deschamps, Philippe Lassonde, Bruno E. Schmidt, Hikaru Fujise, Mizuho Fushitani, Akiyoshi Hishikawa, Paul L. Houston, Joel M. Bowman, Michael S. Schuurman, François Légaré, Heide Ibrahim, </span><br/><span style="font-style:italic;">Capturing roaming molecular fragments in real time, </span><br/><span>Science 370, 1072--1077 (2020)</span><span style="font-size:small;float:right;">    <a href="http://dx.doi.org/10.1126/science.abc2960" target="_blank">DOI</a> </span></div>
<div style="width:90%;padding:0.5em 0px 0.5em 0px;border-bottom:thin solid #0000ff;"><span>Katherine R. Herperger, Anja Röder, Ryan J. MacDonell, Andrey E. Boguslavskiy, Anders B. Skov, Albert Stolow, Michael S. Schuurman, </span><br/><span style="font-style:italic;">Directing excited state dynamics via chemical substitution: A systematic study of π-donors and π-acceptors at a carbon–carbon double bond, </span><br/><span>The Journal Of Chemical Physics 153, 244307 (2020)</span><span style="font-size:small;float:right;">    <a href="http://dx.doi.org/10.1063/5.0031689" target="_blank">DOI</a> </span></div>
<div style="width:90%;padding:0.5em 0px 0.5em 0px;border-bottom:thin solid #0000ff;"><span>Homin Shin, Xiangyang Liu, Thomas Lacelle, Ryan J. MacDonell, Michael S. Schuurman, Patrick R. L. Malenfant, Chantal Paquet, </span><br/><span style="font-style:italic;">Mechanistic Insight into Bis(amino) Copper Formate Thermochemistry for Conductive Molecular Ink Design, </span><br/><span>\ACS\ Applied Materials & Interfaces 12, 33039--33049 (2020)</span><span style="font-size:small;float:right;">    <a href="http://dx.doi.org/10.1021/acsami.0c08645" target="_blank">DOI</a> </span></div>

