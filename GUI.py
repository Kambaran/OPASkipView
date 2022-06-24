import sys

from PyQt5 import QtCore, QtGui, QtWidgets
import qdarktheme

import asyncio
import time


globallist = ["1","2","aaa","bbb","kur"]



class Dialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Dialog, self).__init__(parent=parent)
        vLayout = QtWidgets.QVBoxLayout(self)
        hLayout = QtWidgets.QHBoxLayout()


        self.lineEdit = QtWidgets.QLineEdit(self)
        hLayout.addWidget(self.lineEdit)    

        #filter button
        self.filter = QtWidgets.QPushButton("filter", self)
        hLayout.addWidget(self.filter)
        self.filter.clicked.connect(self.filterClicked)

        self.list = QtWidgets.QListView(self)

        vLayout.addLayout(hLayout)
        vLayout.addWidget(self.list)

        self.model = QtGui.QStandardItemModel(self.list)



        codes = [
            'LOAA-05379',
            'LOAA-04468',
            'LOAA-03553',
            'LOAA-02642',
            'LOAA-05731'
        ]

        for code in codes:
            item = QtGui.QStandardItem(code)
            item.setCheckable(False)
            item.setEditable(False)
            self.model.appendRow(item)
        self.list.setModel(self.model)

    def filterClicked(self):
        filter_text = str(self.lineEdit.text()).lower()
        for row in range(self.model.rowCount()):
            if filter_text in str(self.model.item(row).text()).lower():
                self.list.setRowHidden(row, False)
            else:
                self.list.setRowHidden(row, True)

class AppWindow (QtWidgets.QWidget):
        
    def __init__(self):

        super().__init__()
        self.initUI()
    

    def initUI(self):

        grid_layout = QtWidgets.QHBoxLayout()
        self.setLayout(grid_layout)

        content_list = Dialog()

        grid_layout.addWidget(content_list)
        
        self.setWindowTitle('Skip View')

        self.show()

if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(qdarktheme.load_stylesheet("dark","rounded"))

    FF = AppWindow()
  
    sys.exit(app.exec())
