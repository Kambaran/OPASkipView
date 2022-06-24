import sys
from types import NoneType

from PyQt5 import QtCore, QtGui, QtWidgets
import qdarktheme

#from LogixTEST import PLCRead
from pylogix import PLC

import time

testlist = ['1', '2', '3']
testtags = ['V_DOJAZDOWA_KW','V_JAZDA_WEJ','V_JAZDA_WYJ','S_WYJ']

# READ TAGS THREAD
class WorkerValues(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    progress = QtCore.pyqtSignal(int)

    def run(self):
        for i in range(1):
            time.sleep(1)
            self.progress.emit(i + 1)
        self.finished.emit()

        """with PLC("192.168.100.250") as driver:

            tags = ['V_DOJAZDOWA_KW','V_JAZDA_WEJ','V_JAZDA_WYJ','S_WYJ']

            while True:
                ret = driver.Read(tags)
                time.sleep(0.2)
                for r in ret:
                    """
        
# TAGS DISPLAY
class TagsList(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(TagsList, self).__init__(parent=parent)
        self.vertical_layout = QtWidgets.QVBoxLayout(self)
        self.horizontal_layout = QtWidgets.QHBoxLayout()

        # FILTER SEARCH
        self.lineEdit = QtWidgets.QLineEdit(self)
        self.lineEdit.setText('Search for tags')

        # FILTER BUTTON
        self.filter = QtWidgets.QPushButton("filter", self)
        self.filter.clicked.connect(self.filterClicked)

        # TAG LIST
        self.list = QtWidgets.QListView(self)
        self.model = QtGui.QStandardItemModel(self.list)

        # LAYOUT APPEND
        self.vertical_layout.addLayout(self.horizontal_layout)
        self.vertical_layout.addWidget(self.list)
        self.horizontal_layout.addWidget(self.lineEdit)
        self.horizontal_layout.addWidget(self.filter)

    # LIST UPDATING
    def listShow(self, List):
        self.model.clear()
        for code in List:
            item = QtGui.QStandardItem(code)
            item.setCheckable(True)
            item.setEditable(False)
            self.model.appendRow(item)
        self.list.setModel(self.model)

    # LIST FILTERING
    def filterClicked(self):
        filter_text = str(self.lineEdit.text()).lower()
        for row in range(self.model.rowCount()):
            if filter_text in str(self.model.item(row).text()).lower():
                self.list.setRowHidden(row, False)
            else:
                self.list.setRowHidden(row, True)
        
# MAIN APPLICATION LOOP
class AppWindow (QtWidgets.QWidget):

    def __init__(self):

        super().__init__()

        self._tags = []

        self.initUI()

    def initUI(self):
        self.resize(800, 800)
        grid_layout = QtWidgets.QVBoxLayout()
        self.setLayout(grid_layout)

        self.content_list = TagsList()
        #self.content_list.setMaximumWidth(400)

        self.log = QtWidgets.QTextEdit()

        self.button = QtWidgets.QPushButton('Write')
        self.button.clicked.connect(self.ReadTags)
        self.button.clicked.connect(self.ReadTagValue) #,self.content_list.listShow(self._tags))

        grid_layout.addWidget(self.content_list)
        grid_layout.addWidget(self.log)
        grid_layout.addWidget(self.button)

        self.tags_search_button = QtWidgets.QPushButton("Refresh Tags List")
        self.tags_search_button.clicked.connect(self.runLongTask)

        # grid_layout.addWidget(self.tags_search_button)
        self.content_list.horizontal_layout.addWidget(self.tags_search_button)

        self.setWindowTitle('Skip View')

        self.show()

    def reportProgress(self, n):
        self.tags_search_button.setText(f"Refresing List of Tags: {n} s")
        self.content_list.listShow(self._tags)

    def runLongTask(self):
        # Create a QThread object
        self.thread = QtCore.QThread()
        # Create a worker object
        self.worker = WorkerValues()
        # Move worker to the thread
        self.worker.moveToThread(self.thread)
        # Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.reportProgress)
        # Start the thread
        self.thread.start()
        # Final resets
        self.tags_search_button.setEnabled(False)
        self.thread.finished.connect(
            lambda: self.tags_search_button.setEnabled(True)
        )
        self.thread.finished.connect(
           lambda: self.tags_search_button.setText("Refresh Tags List")
        )

    # READ PLC TAGS
    def ReadTags(self):
        with PLC("192.168.100.250") as self.driver:
            if self.driver.GetTagList().Value is not NoneType:
                for t in self.driver.GetTagList().Value:
                    self._tags.append(f"Nazwa tagu:  {t.TagName} |  Typ zmiennej:  {t.DataType}")
                else:
                    self.tags = ['Failed to load tags']
                return self._tags
    
    # READ SELECTED TAGS VALUES
    def ReadTagValue(self):
        with PLC("192.168.100.250") as self.driver:
            if self.driver.GetTagList().Value is not NoneType:
                for i in self.driver.Read(testtags):
                    print(i.Value)


if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(qdarktheme.load_stylesheet("dark", "rounded"))

    FF = AppWindow()

    sys.exit(app.exec())
