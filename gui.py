from PyQt5 import uic, QtWidgets, QtCore, QtGui
import sys
from utils import *
import corelib
from plot import build


class AppBundle:
    def __init__(self):
        self._app = QtWidgets.QApplication(sys.argv)
        self._window = uic.loadUi("suntime2.ui")
        self._locales = load_locale()
        self.combobox_items = [
            locale("Dawn/Dusk", self._locales),
            locale("Sunrise/Sunset", self._locales),
            locale("Noon/Midnight", self._locales),
            locale("Daylength/Nightlength", self._locales)
        ]

        self.combobox_2_items = [
            locale("Civil", self._locales),
            locale("Nautical", self._locales),
            locale("Astronomical", self._locales),
        ]
        self.window.setWindowIcon(QtGui.QIcon('icon.png'))
        self._setupWindow()

    def calendar_view(self):
        if self.window.calendar.isVisible():
            self.window.calendar.setVisible(False)
        else:
            self.window.calendar.setVisible(True)

    def plot(self):
        location = corelib.get_location(*self.get_coords())
        build(location, self.get_date(), self.combobox_2_items.index(self.window.comboBox_2.currentText()), self.combobox_items.index(self.window.comboBox.currentText()))

    def get_date(self):
        return self.window.calendar.dateTime().toPyDateTime()

    def get_coords(self):
        return float(self.window.lineEdit.text()), float(self.window.lineEdit_2.text())

    def push(self):
        location = corelib.get_location(*self.get_coords())
        self._window.textarea.setText(corelib.get_string(self._locales, self.combobox_2_items.index(self.window.comboBox_2.currentText()), self.get_date(), location))

    def _setupWindow(self):
        found = lookup_location()
        self.window.lineEdit.setText(str(found[0]))
        self.window.lineEdit_2.setText(str(found[1]))
        self.window.pushButton_2.setText(locale(self.window.pushButton_2.text(), self._locales))
        self.window.pushButton.setText(locale(self.window.pushButton.text(), self._locales))
        self.window.pushButton_3.setText(locale(self.window.pushButton_3.text(), self._locales))
        self.window.pushButton_2.clicked.connect(self.calendar_view)
        self.window.pushButton.clicked.connect(self.push)
        self.window.pushButton_3.clicked.connect(self.plot)
        self.window.textarea = QtWidgets.QTextEdit()
        self.window.textarea.setReadOnly(True)
        self.window.textarea.setLineWrapMode(QtWidgets.QTextEdit.WidgetWidth)
        self.window.scrollArea.setWidget(self.window.textarea)
        self.window.comboBox.addItems(self.combobox_items)
        self.window.comboBox_2.addItems(self.combobox_2_items)
        self.window.setWindowTitle("Suntime 2")
        self._window.calendar = QtWidgets.QDateTimeEdit(parent=self.window)
        self._window.calendar.setVisible(False)
        self._window.calendar.setCalendarPopup(True)
        self._window.calendar.setCalendarWidget(QtWidgets.QCalendarWidget())
        self._window.calendar.setDateTime(QtCore.QDateTime.currentDateTime())
        self.window.label.setText(locale(self.window.label.text(), self._locales))
        self.window.label_2.setText(locale(self.window.label_2.text(), self._locales))
        self.window.label_3.setText(locale(self.window.label_3.text(), self._locales))
        self.window.label_4.setText(locale(self.window.label_4.text(), self._locales))
        # fix calendar width

    @property
    def window(self):
        return self._window

    @property
    def application(self):
        return self._app


if __name__ == '__main__':
    app = AppBundle()
    app.window.show()
    sys.exit(app.application.exec_())
