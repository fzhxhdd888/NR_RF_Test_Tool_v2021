# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'win_newdut.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_NewDUT(object):
    def setupUi(self, NewDUT):
        NewDUT.setObjectName("NewDUT")
        NewDUT.resize(529, 110)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/actionicons/dut_64px.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        NewDUT.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(NewDUT)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.lineEdit_dutname = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_dutname.setObjectName("lineEdit_dutname")
        self.horizontalLayout.addWidget(self.lineEdit_dutname)
        self.pushButton_ok = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_ok.setObjectName("pushButton_ok")
        self.horizontalLayout.addWidget(self.pushButton_ok)
        self.pushButton_cancel = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_cancel.setObjectName("pushButton_cancel")
        self.horizontalLayout.addWidget(self.pushButton_cancel)
        self.verticalLayout.addLayout(self.horizontalLayout)
        NewDUT.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(NewDUT)
        self.statusbar.setObjectName("statusbar")
        NewDUT.setStatusBar(self.statusbar)

        self.retranslateUi(NewDUT)
        QtCore.QMetaObject.connectSlotsByName(NewDUT)

    def retranslateUi(self, NewDUT):
        _translate = QtCore.QCoreApplication.translate
        NewDUT.setWindowTitle(_translate("NewDUT", "New DUT"))
        self.label.setText(_translate("NewDUT", "New DUT Name:"))
        self.pushButton_ok.setText(_translate("NewDUT", "OK"))
        self.pushButton_cancel.setText(_translate("NewDUT", "Cancel"))
from image import icons_rc
