# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\python\spider\setting.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DlgSetting(object):
    def setupUi(self, DlgSetting):
        DlgSetting.setObjectName("DlgSetting")
        DlgSetting.resize(400, 200)
        DlgSetting.setSizeGripEnabled(True)
        self.gridLayout = QtWidgets.QGridLayout(DlgSetting)
        self.gridLayout.setObjectName("gridLayout")
        self.groupBox_2 = QtWidgets.QGroupBox(DlgSetting)
        self.groupBox_2.setMaximumSize(QtCore.QSize(16777215, 40))
        self.groupBox_2.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.groupBox_2.setStyleSheet("QGroupBox{\n"
"    border:none;\n"
"}")
        self.groupBox_2.setTitle("")
        self.groupBox_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.groupBox_2.setFlat(False)
        self.groupBox_2.setObjectName("groupBox_2")
        self.formLayout = QtWidgets.QFormLayout(self.groupBox_2)
        self.formLayout.setObjectName("formLayout")
        self.btn_cancel = QtWidgets.QPushButton(self.groupBox_2)
        self.btn_cancel.setMinimumSize(QtCore.QSize(100, 0))
        self.btn_cancel.setMaximumSize(QtCore.QSize(100, 16777215))
        self.btn_cancel.setAutoFillBackground(False)
        self.btn_cancel.setObjectName("btn_cancel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.btn_cancel)
        self.btn_ok = QtWidgets.QPushButton(self.groupBox_2)
        self.btn_ok.setMinimumSize(QtCore.QSize(100, 0))
        self.btn_ok.setMaximumSize(QtCore.QSize(100, 16777215))
        self.btn_ok.setAutoFillBackground(False)
        self.btn_ok.setObjectName("btn_ok")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.btn_ok)
        self.gridLayout.addWidget(self.groupBox_2, 1, 0, 1, 1)
        self.tabWidget = QtWidgets.QTabWidget(DlgSetting)
        self.tabWidget.setTabsClosable(False)
        self.tabWidget.setObjectName("tabWidget")
        self.tab_common = QtWidgets.QWidget()
        self.tab_common.setObjectName("tab_common")
        self.formLayout_3 = QtWidgets.QFormLayout(self.tab_common)
        self.formLayout_3.setObjectName("formLayout_3")
        self.chk_min_tray = QtWidgets.QCheckBox(self.tab_common)
        self.chk_min_tray.setChecked(True)
        self.chk_min_tray.setObjectName("chk_min_tray")
        self.formLayout_3.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.chk_min_tray)
        self.tabWidget.addTab(self.tab_common, "")
        self.tab_auto = QtWidgets.QWidget()
        self.tab_auto.setObjectName("tab_auto")
        self.formLayout_2 = QtWidgets.QFormLayout(self.tab_auto)
        self.formLayout_2.setObjectName("formLayout_2")
        self.chk_start = QtWidgets.QCheckBox(self.tab_auto)
        self.chk_start.setObjectName("chk_start")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.chk_start)
        self.time_start = QtWidgets.QTimeEdit(self.tab_auto)
        self.time_start.setEnabled(False)
        self.time_start.setTime(QtCore.QTime(9, 30, 0))
        self.time_start.setObjectName("time_start")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.time_start)
        self.chk_end = QtWidgets.QCheckBox(self.tab_auto)
        self.chk_end.setObjectName("chk_end")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.chk_end)
        self.time_end = QtWidgets.QTimeEdit(self.tab_auto)
        self.time_end.setEnabled(False)
        self.time_end.setTime(QtCore.QTime(16, 30, 0))
        self.time_end.setObjectName("time_end")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.time_end)
        self.tabWidget.addTab(self.tab_auto, "")
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)

        self.retranslateUi(DlgSetting)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(DlgSetting)

    def retranslateUi(self, DlgSetting):
        _translate = QtCore.QCoreApplication.translate
        DlgSetting.setWindowTitle(_translate("DlgSetting", "Dialog"))
        self.btn_cancel.setText(_translate("DlgSetting", "取消"))
        self.btn_ok.setText(_translate("DlgSetting", "确定"))
        self.chk_min_tray.setText(_translate("DlgSetting", "最小化至托盘"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_common), _translate("DlgSetting", "常用设置"))
        self.chk_start.setText(_translate("DlgSetting", "开始时间"))
        self.time_start.setDisplayFormat(_translate("DlgSetting", "hh:mm:ss"))
        self.chk_end.setText(_translate("DlgSetting", "结束时间"))
        self.time_end.setDisplayFormat(_translate("DlgSetting", "hh:mm:ss"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_auto), _translate("DlgSetting", "自动运行"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    DlgSetting = QtWidgets.QDialog()
    ui = Ui_DlgSetting()
    ui.setupUi(DlgSetting)
    DlgSetting.show()
    sys.exit(app.exec_())

