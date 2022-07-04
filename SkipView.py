import sys
import time
from types import NoneType

from PyQt5 import QtCore, QtGui, QtWidgets
import qdarktheme

import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

#from LogixTEST import PLCRead
from pylogix import PLC

plt.style.use('dark_background')

class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

class PlotView(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(PlotView, self).__init__()

        self.vertical_layout = QtWidgets.QVBoxLayout()
        self.vertical_main_layout = QtWidgets.QVBoxLayout(self)

        self.refresh_button = QtWidgets.QPushButton()
        self.refresh_button.setText('Refresh')

        self.container = QtWidgets.QGroupBox()
        self.containerbox = QtWidgets.QVBoxLayout()
        self.container.setLayout(self.containerbox)
        self.container.setTitle('Trend Preview')

        self.container2 = QtWidgets.QGroupBox()
        self.containerbox2 = QtWidgets.QVBoxLayout()
        self.container2.setLayout(self.containerbox2)
        self.container2.setTitle('Box2')

        #self.vertical_main_layout.addWidget(self.refresh_button)
        self.vertical_main_layout.addLayout(self.vertical_layout)
        self.vertical_layout.addWidget(self.container)
        #self.vertical_layout.addWidget(self.container2)


# READ TAGS THREAD


class WorkerValues(QtCore.QObject):

    # WORKER SIGNALS
    finished = QtCore.pyqtSignal()
    progress = QtCore.pyqtSignal(int)
    returnvalues = QtCore.pyqtSignal(list)

    def __init__(self, plc_ip, tags, stop):
        super().__init__()
        self.driver = PLC()
        self.driver.IPAddress = plc_ip
        self.tags = tags
        self.vals_list = []
        self.stop = stop

    # WORKER RUN - READING FROM PLC
    def run(self):
        while True:
            if self.stop['break']:
                time.sleep(0.05)
                for i in self.driver.Read(self.tags):
                    self.vals_list.append(f"{i.Value}")
                self.returnvalues.emit(self.vals_list)
                self.vals_list.clear()
                time.sleep(0.05)
            else:
                time.sleep(0.05)
                break
        self.finished.emit()


# TAGS DISPLAY


class TagsList(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(TagsList, self).__init__(parent=parent)

        # LAYOUTS
        self.vertical_layout = QtWidgets.QVBoxLayout(self)
        self.horizontal_layout = QtWidgets.QHBoxLayout()

        # PLC ADDRES
        self.ip_addres_line = QtWidgets.QLineEdit()
        self.ip_addres_line.setText('192.168.100.250')

        # FILTER SEARCH
        self.search_edit_line = QtWidgets.QLineEdit(self)
        self.search_edit_line.setText('Write tags to filter')

        # FILTER BUTTON
        self.filter = QtWidgets.QPushButton("Filter Tags", self)
        self.filter.clicked.connect(self.filterClicked)

        # REFRESH BUTTON
        self.tags_search_button = QtWidgets.QPushButton(
            "Refresh Tags List", self)

        # TAG LIST
        self.list = QtWidgets.QListView(self)
        self.model = QtGui.QStandardItemModel(self.list)

        # LAYOUT APPEND
        self.vertical_layout.addWidget(self.ip_addres_line)
        self.vertical_layout.addLayout(self.horizontal_layout)
        self.vertical_layout.addWidget(self.list)
        self.horizontal_layout.addWidget(self.search_edit_line)
        self.horizontal_layout.addWidget(self.filter)
        self.horizontal_layout.addWidget(self.tags_search_button)

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
        filter_text = str(self.search_edit_line.text()).lower()
        for row in range(self.model.rowCount()):
            if filter_text in str(self.model.item(row).text()).lower():
                self.list.setRowHidden(row, False)
            else:
                self.list.setRowHidden(row, True)


# VALUES DISPLAY


class ValuesList(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(ValuesList, self).__init__(parent=parent)

        # LAYOUTS
        self.vertical_layout = QtWidgets.QVBoxLayout(self)
        self.horizontal_layout = QtWidgets.QHBoxLayout()

        # WRITE VALUES BUTTON
        self.write = QtWidgets.QPushButton("Show Tags Names", self)

        # START READ BUTTON
        self.start = QtWidgets.QPushButton("Start Reading", self)

        # STOP READ BUTTON
        self.stop = QtWidgets.QPushButton("Stop Reading", self)

        # TAG LIST
        self.list = QtWidgets.QListView(self)
        self.model = QtGui.QStandardItemModel(self.list)

        # LAYOUT APPEND
        self.vertical_layout.addLayout(self.horizontal_layout)
        self.vertical_layout.addWidget(self.list)
        self.horizontal_layout.addWidget(self.write)
        self.horizontal_layout.addWidget(self.start)
        self.horizontal_layout.addWidget(self.stop)

    # LIST UPDATING
    def listShow(self, List):
        self.model.clear()
        for code in List:
            item = QtGui.QStandardItem(code)
            item.setCheckable(False)
            item.setEditable(False)
            self.model.appendRow(item)
        self.list.setModel(self.model)


# MAIN APPLICATION LOOP


class AppWindow (QtWidgets.QWidget):
    def __init__(self,*args,**kwargs):
        super(AppWindow,self).__init__(*args,**kwargs)

        self._left_layout_width = 500
        self._tags = []
        self._values_names = []
        self._stop = {'break': True}

        self.n_data = 2
        self.xdata = list(range(self.n_data))
        self.ydata = [0 for i in range(self.n_data)]
        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)

        self.initUI()

    def initUI(self):
        # WINDOW
        self.resize(1000, 800)
        self.setWindowTitle('Skip View')

        # TAGS
        self.content_list = TagsList()
        self.content_list.setMaximumWidth(self._left_layout_width)

        # DUMMY
        self.graph_list = PlotView()

        # VALUES
        self.values_list = ValuesList()
        self.values_list.setMaximumWidth(self._left_layout_width)

        # BUTTONS SIGNALS
        self.content_list.tags_search_button.clicked.connect(self.readTags)
        self.content_list.tags_search_button.clicked.connect(self.writeTags)
        self.values_list.write.clicked.connect(self.writeCheckedTags)
        self.values_list.write.clicked.connect(self.writeValues)
        self.values_list.start.clicked.connect(self.runReading)
        self.values_list.stop.setEnabled(False)
        self.values_list.stop.clicked.connect(self.stopReading)

        # LAYOUT
        left_layout = QtWidgets.QVBoxLayout()
        left_layout.setAlignment(QtCore.Qt.AlignRight)
        right_layout = QtWidgets.QVBoxLayout()
        main_layout = QtWidgets.QGridLayout()

        left_layout.addWidget(self.content_list)
        left_layout.addWidget(self.values_list)

        right_layout.addWidget(self.graph_list)

        self.graph_list.containerbox.addWidget(self.canvas)

        main_layout.addItem(left_layout, 1, 1)
        main_layout.addItem(right_layout, 1, 2)

        self.setLayout(main_layout)

        self._plot_ref = None

        self.show()

    def updateValues(self, list):
        self.values_list.listShow(list)

    def runReading(self):
        self._stop['break'] = True

        self.thread = QtCore.QThread()
        self.worker = WorkerValues(
            self.content_list.ip_addres_line.text(), self._values_names, self._stop)

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.returnvalues.connect(self.updateValues)
        self.worker.returnvalues.connect(self.update_plot)

        self.thread.start()

        self.values_list.start.setEnabled(False)
        self.values_list.write.setEnabled(False)
        self.values_list.stop.setEnabled(True)

        self.thread.finished.connect(
            lambda: self.values_list.start.setEnabled(True)
        )
        self.thread.finished.connect(
            lambda: self.values_list.write.setEnabled(True)
        )
        self.thread.finished.connect(
            lambda: self.values_list.stop.setEnabled(False)
        )

    def stopReading(self):
        self._stop['break'] = False

    def writeCheckedTags(self):
        self._values_names.clear()
        for index in range(self.content_list.model.rowCount()):
            item = self.content_list.model.item(index)
            if item.checkState() == QtCore.Qt.Checked:
                self._values_names.append(f"{item.text()}")
        return self._values_names

    def writeTags(self):
        self.content_list.listShow(self._tags)

    def writeValues(self):
        self.values_list.listShow(self._values_names)

    # READ PLC TAGS
    def readTags(self):
        with PLC(self.content_list.ip_addres_line.text()) as self.driver:
            if self.driver.GetTagList().Value is not None:
                if self.driver.GetTagList().Value is not NoneType:
                    self._tags.clear()
                    for t in self.driver.GetTagList().Value:
                        self._tags.append(f"{t.TagName}")
                        self.content_list.tags_search_button.setText(
                            "Refresh Tags List")
                else:
                    self._tags = ['No tags/Failed to load tags']
                    return self._tags
            else:
                self.content_list.tags_search_button.setText(
                    'Search for tags has failed')

    def update_plot(self,list):
        if list:
            self.xdata.append(self.xdata[len(self.xdata)-1]+1)
            self.ydata = self.ydata + [float(list[0])]
        else:
            pass
        self.canvas.axes.cla()
        self.canvas.axes.plot(self.xdata, self.ydata, 'r')
        self.canvas.draw()

    def dummy(self):
        print('dummy')


"""
    # MANUAL READ SELECTED TAGS VALUES
    def ReadTagValue(self):
        with PLC(plcaddress) as self.driver:
            if self.driver.GetTagList().Value is not NoneType:
                for i in self.driver.Read(testtags):
                    print(i.Value)
"""

if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(qdarktheme.load_stylesheet("dark", "rounded"))

    FF = AppWindow()

    sys.exit(app.exec())
