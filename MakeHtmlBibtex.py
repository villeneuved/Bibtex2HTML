"""
Convert all entries in a bibtex.bib file into HTML format.

Command line:

python MakeHtmlBibtex.py -i inputfilename -o outputfilename -n authorname -c

All command line arguments are optional.
Inputfilename defaults to bibtextmaster.bib in the local or Dropbox directory.
Outputfilename defaults to testbib.html.

Optional command line argument -n is a single word with an author last name (obey capitalization).
If given, only bibtex entries that contain that author name are output.
-c will use Scopus to look up the number of citations (requires Scopus API key and Scopus access).

Reads from a Bibtex file containing article information (only @ARTICLE entries used).
Sorts entries by year and then by author.
Writes a new file testbib.html in current directory that contains html plus preamble/postamble.
Stores html content (no preamble) in Windows clipboard.  This can be pasted into Wordpress in Text mode.

Note regarding encoding:  The bibtexmaster.bib file should have UTF-8 encoding,
to preserve special accents and symbols if copied from a web site.
If you use JabRef to create the bib file, use File/Database Properties to set it to UTF-8.
Bibtexparser will convert Latex special symbols, e.g. {\'e}, to the equivalent UTF-8 symbol.
The output html will have UTF-8 encoding, and Wordpress expects this.

This assumes that you have Python 3.6 or greater installed on your computer:
We use bibtexparser package.  From Anaconda command prompt:
pip install bibtexparser
pip install pyperclip
pip install pybliometrics (optional, for Scopus lookup of citations counts).

I used PyInstaller to create a Windows executable package.
pyinstaller --onefile MakeHtmlBibtex.py

This was one of my early Python programs.
Today I would probably use a class to encapsulate the functions.

David Villeneuve
Sep 2017

2021/02/26  Program failed due to month = jan in BIB files.
Solved by adding common_strings = True to init of parser:
        parser = BibTexParser( common_strings=True )   #common strings like months, must be here

2024/06/12  Added Scopus lookup of citation count.
Using this feature requires:
- The pybliometrics package
- a Scopus access key (free)
- must be run on a computer with licensed access to Scopus, e.g. university network)
The first time you run it with this option, you will get a text prompt to enter your key.
The key is then saved in your root document folder for subsequent use.

"""

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import *
import pyperclip        #to copy text to clipboard
import os               #for user directory
import sys              #for retrieving command line arguments
import argparse         #for parsing command line arguments

# Global variables

onlyauthor = ''     #string containing an author name
currentyear = 0     #integer containing the year for sorting
outfile = ''        #string containing name of output HTML file
bibfile = ''        #string containing name of input BIB file
htmltext = ''       #string containing buffer of html text
foutfile = None     #file handle for outfile

# html_preamble and html_postamble are for the stand-alone html document.
# For Wordpress, they are not copied into the clipboard.

html_preamble = """
<!DOCTYPE html>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>Publication List</title>
</head>
<body style="font-family:Sans-serif;">
<h1>Publications</h1>
"""

html_postamble = """
</body></html>
"""

# html strings for the links to DOI and PDF addresses

pubdoi = '  <a href="{0}" target="_blank"><img src="https://www.attoscience.ca/images/DOI_logo-20x20.png" alt="DOI"></a> '
pubpdf = ' <a href="{0}" target="_blank"><img src="https://www.attoscience.ca/images/pdf-logo-20x20.png" alt="PDF"></a>'

pubdoi = '  <a href="{0}" target="_blank">DOI</a> '
pubpdf = ' <a href="{0}" target="_blank">PDF</a>'

highlycited = ' <img src="https://www.attoscience.ca/images/highlycited.png" alt="Highly Cited" title="Judged by Web of Science to be in the top 1% of papers in physics for that year."> '

###############################################################

def getnames(names):
    """Make people names as firstnames surname
    Converts Latex control sequences to UTF-8 symbol.

    :param names: A list of each author name
    :type names: list
    :returns: list -- Correctly formated names
    """
    
    tidynames = []
    for namestring in names:
        namestring = namestring.strip()
        if len(namestring) < 1:
            continue
        if ',' in namestring:
            namesplit = namestring.split(',', 1)
            last = namesplit[0].strip()
            firsts = [i.strip() for i in namesplit[1].split()]
        else:
            namesplit = namestring.split()
            last = namesplit.pop()
            firsts = [i.replace('.', '. ').strip() for i in namesplit]
        if last in ['jnr', 'jr', 'junior']:
            last = firsts.pop()
        for item in firsts:
            if item in ['ben', 'van', 'der', 'de', 'la', 'le']:
                last = firsts.pop() + ' ' + last
        n = ' '.join(firsts) + ' ' + last   #author name
#               n = codecs.decode( n, 'ulatex+utf8' )   #convert Latex \'e to UTF-8
        n = n.replace( '{', '' )        #remove braces
        n = n.replace( '}', '' )
        n = n.replace( '\,', ' ' )      
        tidynames.append(n)
        
    return tidynames

#----------------------------------------------------------------------------

def get_citation_count( doi ):

# Looks up the DOI on Scopus and returns the number of citations as an integer.
# Requires that the pybliography package be installed.
# pip install pybliometrics
# GitHub - ElsevierDev/pybliometrics: Python-based API-Wrapper to access Scopus
# pybliometrics: Python-based API-Wrapper to access Scopus — pybliometrics documentation
#
# The first time that this is run on a computer, it will prompt for the API key,
# then will create a config file at the user's root.
#
# API key = a5a60ec2046187d43202c4591450cc4d

    import pybliometrics

    pybliometrics.scopus.init()  # read API keys
#    pybliometrics.scopus.init('keys', ['a5a60ec2046187d43202c4591450cc4d'])  # read API keys
    ab = pybliometrics.scopus.AbstractRetrieval(doi)
    print( 'Looking up DOI {} on Scopus, counts {}'.format(doi, ab.citedby_count) )
    return ab.citedby_count
    
#----------------------------------------------------------------------------

def makeentry( ent, onlyauthor, citations ):

# Parse the bib entry ent and output the corresponding html code

    global currentyear
    if onlyauthor != '':
        if onlyauthor not in ent['author']:
            return
        
    if 'year' in ent:
        try:
            entyear = int( ent['year'] )
            if entyear != currentyear:
                output( '<div style="clear:both;"><h3>' + ent['year'] + '</h3></div>\n' )
                currentyear = entyear
        except:
                        pass
        
    output( '<div style="width:90%;padding:0.5em 0px 0.5em 0px;border-bottom:thin solid #0000ff;">' )

    names = getnames( [i.strip() for i in ent["author"].replace('\n', ' ').split(" and ")])
    s = ''
    for n in names:
        s += n + ', '   #s is all names in one string
    output( '<span>' )
    output( s )  #firstname lastname
    output( '</span><br/><span style="font-style:italic;">' )

    t = ent['title']        #remove curly braces from title
    t = t.replace( '{', '' )
    t = t.replace( '}', '' )
    t = t.replace( '$\\mu$', '&mu;' )
    output( t )
    output( ', </span><br/><span>' )
    
    if 'journal' in ent:
        t = ent['journal'].title()
        t = t.replace( 'Ieee', 'IEEE' )
        t = t.replace( 'Acs', 'ACS' )
        t = t.replace( 'Josa', 'JOSA' )
        s = t
    else:
        s = 'JOURNAL'
    s = s + ' '
    
    if 'volume' in ent:
        s += ent['volume']
    else:
        s += 'VOLUME'
    s = s + ', '
    
    if 'pages' in ent:
        s += ent['pages']
    elif 'art_number' in ent:
        s += ent['art_number']
    elif 'article-number' in ent:
        s += ent['article-number']
    else:
        s += 'PAGES'
        
    if 'year' in ent:
        s = s + ' (' + ent['year'] + ')'
        
    s = s + '</span>'
    output(s)
    
    output( '<span style="font-size:small;float:right;">  ' )
    if 'highlycited' in ent:
        output( highlycited )
    if citations:
        num_cit = None
        if 'doi' in ent:    #DOI field is in entry
            num_cit = get_citation_count( ent['doi'] )
        elif 'url_link' in ent:     #url_link is like http://dx.doi.org/DOI
            if 'http://dx.doi.org/' in ent['url_link']:
                doi = ent['url_link'].replace( 'http://dx.doi.org/', '' )
#                print( 'Inferred DOI: {}'.format(doi) )
                num_cit = get_citation_count( doi )
        if num_cit is not None:
            output( '{} '.format(num_cit) )
    if 'doi' in ent:
        output( pubdoi.format( 'http://dx.doi.org/' + ent['doi'] ) )
#        print( 'Entry DOI: {}'.format(ent['doi']) )
    elif 'url_link' in ent:
        output( pubdoi.format( ent['url_link'] ) )
    if 'url_paper' in ent:      #link to PDF
        s1 = ent['url_paper']   #check if base url forgotten
        if '/' not in s1:
            s1 = 'https://www.attoscience.ca/pdf/' + s1
        output( pubpdf.format( s1 ) )
    output( '</span></div>\n' )

#-----------------------------------------------------------------------
        
def output( str ):
        global htmltext
        foutfile.write( str )
        htmltext += str

def getauthor( p ):     #function to help sort by author
        return p['author']

def getyear( p ):       #function to help sort by year
        return p['year']

# This routine is particular to my system.
# It tries to find a particular file, bibtexmaster.bib
# that we use for our publication list.
# Someone else should either put the bib filename on the command line,
# or modify this.
def get_bibfile_path():   #find location of bibtexmaster.bib file on different systems

    print( 'Trying local folder for bibtexmaster.bib' )
    bibfile = 'bibtexmaster.bib'            #try local folder first
    if os.path.isfile( bibfile ):
        bibfile = os.path.abspath( 'bibtexmaster.bib' ) #use local copy instead of Dropbox copy
        return bibfile
    
    bibfile = os.path.expanduser( '~\\Dropbox\\attoscience.ca\\bibtexmaster.bib' )
    print( 'Trying {}'.format( bibfile ) )
    if os.path.isfile( bibfile ):
        return bibfile

    bibfile = os.path.expanduser( '~\\Documents\\Dropbox\\attoscience.ca\\bibtexmaster.bib' )
    print( 'Trying {}'.format( bibfile ) )
    if os.path.isfile( bibfile ):
        return bibfile

    print( 'Failed to find bibtexmaster.bib file.' )
    sys.exit()

   
#-------------------------------------------------------------------------
#
# Main function that does the parsing of the BIB file into HTML.
#
# Input arguments:
#  bibfile = string containing name of input BIB file to read.
#  outfile = string containing name of output HTML file to create.
#  onlyauthor = string with the surname of an author, then only that author's pubs are used
#  citations = true if we are to look up the number of citations on Scopus.

def parsebib( p_bibfile, p_outfile, p_onlyauthor, p_citations ):

    global foutfile
    global htmltext
    htmltext = '<h1>Attosecond Science Publications</h1>\n'      #to contain html text to be copied to clipboard
    currentyear = 0

    print( 'Reading from BIB file ', p_bibfile )
    print( 'Writing to {} in current directory.'.format( p_outfile) )

    foutfile = open( p_outfile, 'w', encoding='utf-8' )   #output file with html text
#    print( type(foutfile) )
    
    with open( p_bibfile, encoding='utf-8' ) as bibtex_file:       #input bibtex file

        bibtex_str = bibtex_file.read()         #read BIB file into string
        parser = BibTexParser( common_strings=True )   #common strings like months, must be here
        parser.customization = convert_to_unicode
        parser.common_strings = True             #doesnt work here
        bib_database = bibtexparser.loads( bibtex_str, parser=parser)

        foutfile.write( html_preamble )

    # Sort the entries first by author, then by reversed year.
    # This results in entries sorted by year, then by author within each year.

        sort1 = sorted( bib_database.entries, key=getauthor, reverse=False )    #sort by author name
        sort2 = sorted( sort1, key=getyear, reverse=True )      #sort by year

    # Read each bibtex entry and emit the html code required to display it

        for ent in sort2:
            if 'ENTRYTYPE' in ent:
                if ent[ 'ENTRYTYPE' ] == 'article':     #we only consider Article entries at this time
                    makeentry( ent, p_onlyauthor, p_citations )
                else:
                    print( 'EntryType {} ignored.'.format( ent[ 'ENTRYTYPE' ] ) )

    foutfile.write( html_postamble )
    foutfile.close()
    pyperclip.copy( htmltext )         #copy html text to clipboard
    print( 'Done.  HTML also copied to clipboard.' )
    #exit()

# ---------------------------------------------------------------------------
# This is run only if the program is invoked from the command line.
# It parses the command line arguments for filenames
# and creates global strings onlyauthor, outfile and bibfile.

def main():

    parser = argparse.ArgumentParser(description='Convert Bibtex to HTML')
    parser.add_argument( '-i', '--input', help='Filename of input Bibtex file' )
    parser.add_argument( '-o', '--output', help='Filename of output HTML file' )
    parser.add_argument( '-n', '--name', help='Author lastname e.g. Staudte' )
    parser.add_argument( '-c', '--citations', action='store_true', help='Include citation counts' )
    args = parser.parse_args()

    onlyauthor = ''
    if args.name is not None:
        onlyauthor = args.name         #first argument is a single author name
        print( 'Selecting for entries containing author ', onlyauthor )

    outfile = 'testbib.html'        #default output file name
    if args.output is not None:
        outfile = args.output

    if args.input is not None:
        bibfile = args.input
    else:        
        bibfile = get_bibfile_path()    #this is unique to my system
        
    citations = args.citations is not None and args.citations   #include number of citations?

    parsebib( bibfile, outfile, onlyauthor, citations )

#####################################
# If this code is initiated from the command line, then run the main code

if __name__ == "__main__":
    main()