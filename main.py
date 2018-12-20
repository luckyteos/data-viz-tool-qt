import sys
import argparse
import pandas as pd
from PySide2.QtCore import (QAbstractTableModel, QDateTime, QModelIndex,
                            QRect, Qt, QTimeZone, Slot)
from PySide2.QtGui import QColor, QPainter
from PySide2.QtWidgets import (QAction, QApplication, QHBoxLayout, QHeaderView,
                               QMainWindow, QSizePolicy, QTableView, QWidget)
from PySide2.QtCharts import QtCharts

class CustomTableModel(QAbstractTableModel):
    def __init__(self, data=None):
        QAbstractTableModel.__init__(self)
        self.load_data(data)

    def load_data(self, data):
        self.input_dates = data[0].values
        self.input_magnitudes = data[1].values

        self.column_count = 2
        self.row_count = len(self.input_magnitudes)

    def rowCount(self, parent=QModelIndex()):
        return self.row_count

    def columnCount(self, parent=QModelIndex()):
        return self.column_count

    def headerData(self, section, orientation, role):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return ("Date", "Magnitude")[section]
        else:
            return "{}".format(section)

    def data(self, index, role=Qt.DisplayRole):
        column = index.column()
        row = index.row()

        if role == Qt.DisplayRole:
            if column == 0:
                raw_date = self.input_dates[row]
                date = "{}".format(raw_date.toPython())
                return date[:-3]
            elif column == 1:
                return "{:.2f}".format(self.input_magnitudes[row])
        elif role == Qt.BackgroundRole:
            return QColor(Qt.white)
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignRight

        return None


class Widget(QWidget):
    def __init__(self, data):
        QWidget.__init__(self)

        #Getting the Model
        self.model = CustomTableModel(data)

        #Creating a QTableView
        self.table_view = QTableView()
        self.table_view.setModel(self.model)

        #QTableView Headers
        self.horizontal_header = self.table_view.horizontalHeader()
        self.vertical_header = self.table_view.verticalHeader()
        self.horizontal_header.setSectionResizeMode(QHeaderView.ResizeToContents)
        self.vertical_header.setSectionResizeMode(QHeaderView.ResizeToContents)
        self.horizontal_header.setStretchLastSection(True)

        #QWidget Layout
        self.main_layout = QHBoxLayout()
        size = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        #Left Layout
        size.setHorizontalStretch(1)
        self.table_view.setSizePolicy(size)
        self.main_layout.addWidget(self.table_view)

        # Set layout to QWidget
        self.setLayout(self.main_layout)

def transform_date(utc, timezone=None):
    utc_fmt = "yyyy-MM-ddTHH:mm:ss.zzzZ"
    new_date = QDateTime().fromString(utc, utc_fmt)
    if timezone:
        new_date.setTimeZone(timezone)
    return new_date

def read_data(fname):
    i_data = pd.read_csv(fname)

    i_data = i_data.drop(i_data[i_data.mag < 0].index)
    magnitudes = i_data["mag"]

    timezone = QTimeZone(b"Asia/Singapore")

    times = i_data["time"].apply(lambda x: transform_date(x, timezone))

    return times, magnitudes

class MainWindow(QMainWindow):
    def __init__(self, widget):
        QMainWindow.__init__(self)
        self.setWindowTitle("Earthquake Info")

        # Menu
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("File")

        #Exit QAction
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.exit_app)

        self.file_menu.addAction(exit_action)

        # Status Bar
        self.status = self.statusBar()
        self.status.showMessage("Data loaded and plotted")

        # Windows Dimensions
        geom = app.desktop().availableGeometry(self)
        self.setFixedSize(geom.width() * 0.8, geom.height() * 0.7)
        
        self.setCentralWidget(widget)

    @Slot()
    def exit_app(self, checked):
        sys.exit()



if __name__ == "__main__":
    options = argparse.ArgumentParser()
    options.add_argument("-f", "--file", type=str, required=True)
    args = options.parse_args()
    data = read_data(args.file)

    #Qt Application
    app = QApplication([])

    widget = Widget(data)
    #QMainWindow using widget as central widget
    window = MainWindow(widget)
    window.show()

    sys.exit(app.exec_())
    
    
    


