""" GUI interface to MakeHtmlBibtex.py

The GUI user interface is created and edited using QT Designer,
which is included in the Anaconda distribution.
From a DOS prompt with the Anaconda SET definitions, enter "designer".
Designer will save a file bib2html_ui.ui.
At the dos prompt, run pyuic5 bib2html_ui.ui -o bib2html_ui.py .
The latter file is imported into the code below.

"""
import MakeHtmlBibtex   # functions like parsebib

from PyQt5 import QtCore, QtGui, QtWidgets

from Bib2Html_ui import Ui_MainWindow  #Created by QT Designer and pyuic5

import os       #for filename and directory handling

class MainWin(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWin, self).__init__()

        self.setupUi(self) # Set up the user interface from Designer

# Initialize some of the controls

        currdir = os.getcwd()   #current directory path where this file is executing    
        self.q_lineEdit_OutputFile.setText( os.path.join( currdir, 'testbib.html' ) )
        bibfile = MakeHtmlBibtex.get_bibfile_path() #default input file
        self.q_lineEdit_InputFile.setText( bibfile )

# Define actions of controls on form.
# setupUi calls connectSlotsByName which finds function names
# that match control names in the UI, of the form on_controlname_clicked.
        
    @QtCore.pyqtSlot()  #connects to Designer-named signal
    def on_q_pushButton_Exit_clicked(self):
#        print('Exiting')
        sys.exit(0)

    @QtCore.pyqtSlot()
    def on_q_pushButton_Go_clicked(self):
#        print('Go Button')
        bibfile = self.q_lineEdit_InputFile.text() #input bib file
        outfile = self.q_lineEdit_OutputFile.text()    #output html file
        onlyauthor = self.q_author_lineEdit.text()    #single author name
        citations = self.checkBoxCitations.isChecked()      #True if box is checked
        MakeHtmlBibtex.parsebib( bibfile, outfile, onlyauthor, citations )
        
    @QtCore.pyqtSlot()
    def on_q_browse_button_clicked(self):
        currdir = os.getcwd()   #current directory path where this file is executing    
        fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Open Bib file', 
         currdir, "Image files (*.bib)" )
        self.q_lineEdit_InputFile.setText( fname[0] )
        
#######################################################################
# Below runs as a Qt application if this file is invoked as a main file.
        
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = MainWin()
    MainWindow.show()
    sys.exit(app.exec_())

