#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/11/10 13:50
# @Author  : Feng Zhaohui
# @Site    :
# @File    : init_ui.py
# @Software: PyCharm

import Start_project
import ctypes
from win32process import SuspendThread, ResumeThread
from win32con import PROCESS_ALL_ACCESS
from gui.main_win import Ui_main_win
from gui.win_testseq import Ui_win_editseq
from gui.win_caseparms import Ui_win_caseparms
from gui.Devices_ui import Ui_MainWindow_device
from gui.win_channel import Ui_win_Channel
from gui.loss_win import Ui_Loss_win
from gui.DUT_ui import Ui_DUT_Win
from gui.win_newdut import Ui_NewDUT
from gui.win_losseditor import Ui_Edit_loss_file_Window
from PyQt5.QtWidgets import QMainWindow, QSplashScreen
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtWidgets import QTreeWidgetItem
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QHeaderView
from PyQt5.QtWidgets import QButtonGroup
from PyQt5.QtWidgets import QMenu
from PyQt5.QtGui import QPixmap, QMovie, QFont, QBrush, QColor, QPainter, QStandardItemModel, QIcon
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtCore import QThread
from PyQt5.QtCore import pyqtSignal
import testseq_handle
import global_elements
from shutil import copy
from datetime import datetime
import os
import re
import time
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Qt5Agg")  # 声明使用QT5
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class MainWin(QMainWindow, Ui_main_win):
    """
        主界面
    """
    def __init__(self, parent=None):
        super(MainWin, self).__init__(parent)
        self.setupUi(self)

        self.movie = QMovie(':/actionicons/timer_62x64.gif')
        self.instance_init()

        self.test_thread = test_Thread()  # 实例化一个线程，用来处理测试过程

        self.cwd = './plan/'
        self.rppath = './result'

        # self.model = QStandardItemModel(0,24)

        self.figure = plt.figure(facecolor='k',  frameon=False)  # 可选参数,facecolor为背景颜色
        self.axes1 = self.figure.add_subplot(211)
        self.axes2 = self.figure.add_subplot(212)
        self.canvas = FigureCanvas(self.figure)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.showtime)

        # 定义信号槽关系
        self.actionRun.triggered.connect(self.startbtn_click)
        self.actionPause.triggered.connect(self.pausebtn_click)
        self.actionStop.triggered.connect(self.stopbtn_click)
        self.actionnew_test_seq.triggered.connect(self.newseq)
        self.actionSave_Test_sequence.triggered.connect(self.saveseq)
        self.actionLoad_test_sequence.triggered.connect(self.loadseq)
        self.actionDevices_Config.triggered.connect(self.device_config)
        self.actionDUT.triggered.connect(self.dut_edit)
        self.tableWidget_plan.itemDoubleClicked.connect(self.parms_btnclicked)
        self.tableWidget_plan.itemChanged.connect(self.parms_clicked)
        self.actionReport_Path.triggered.connect(self.reportmenuclick)
        self.actionPath_Loss.triggered.connect(self.pathlosswin)
        self.actionChannel_Config.triggered.connect(self.channelwin)
        self.actionLast_Config.triggered.connect(self.lastconfig)
        global_elements.emitsingle.updataScpiUI.connect(self.updataScpiUi)
        global_elements.emitsingle.stateupdataSingle.connect(self.stateupdateUi)
        global_elements.emitsingle.thread_exitSingle.connect(self.testthread_exit)
        global_elements.emitsingle.reportupdataSingle.connect(self.reportupdata)
        global_elements.emitsingle.faileditemsupdataSingle.connect(self.faileditemsupdataSingle)
        global_elements.emitsingle.process_rateupdataSingle.connect(self.processrateupdata)
        global_elements.emitsingle.totalStepupdata.connect(self.totalstep)
        # 建立更新主界面summry的信号槽关系
        global_elements.emitsingle.summaryupdataSingle.connect(self.summryupdata)
        global_elements.emitsingle.resultChartclear.connect(self.resultChartClear)
        global_elements.emitsingle.maxOutputPowerChartUpdata.connect(self.maxPowerChartUpdata)
        global_elements.emitsingle.onoffPowerChartUpdata.connect(self.onoffChartUpdata)
        global_elements.emitsingle.freErrorChartUpdata.connect(self.freErrorChartUpdata)
        global_elements.emitsingle.evmChartUpdata.connect(self.evmChartUpdata)
        global_elements.emitsingle.evmflatnessChartUpdata.connect(self.evmflatnessChartUpdata)
        global_elements.emitsingle.inbandemissionChartUpdata.connect(self.inbandemissionChartUpdata)
        global_elements.emitsingle.bwChartUpdata.connect(self.bwChartUpdata)
        global_elements.emitsingle.semChartUpdata.connect(self.semChartUpdata)
        global_elements.emitsingle.aclrChartUpdata.connect(self.aclrChartUpdata)
        global_elements.emitsingle.blerChartUpdata.connect(self.blerChartUpdata)
        global_elements.emitsingle.blerSearchChartUpdata.connect(self.blerSearchChartUpdata)
        global_elements.emitsingle.nsa6_2b_1_3ChartUpdata.connect(self.nsa6_2b_1_3ChartUpdata)

        # test线程运行完成信号槽关系
        self.test_thread.finished.connect(self.testfinish)

    # def paintEvent(self, e):
    #
    #     painter = QPainter(self)
    #     painter.begin(self)
    #     painter.set
    #     painter.setPen(QColor(255, 0, 0))
    #     painter.setFont(QFont('SimSun', 25))
    #     painter.drawText(self.centralWidget().rect(),Qt.AlignCenter, "self.painterText")
    #
    #     painter.end()

    def instance_init(self):
        # 初始化需要使用的配置到字典类型
        global_elements.ChannelConfig_dict = global_elements.xml_to_dict('./config/ParmsConfig/ChannelConfig.xml')
        global_elements.SCSBandwidthConfig_dict = global_elements.xml_to_dict(
            './config/ParmsConfig/SCSBandwidthConfig.xml')
        global_elements.RBConfig_dict = global_elements.xml_to_dict('./config/ParmsConfig/RBConfig.xml')
        global_elements.DlRBConfig_dict = global_elements.xml_to_dict('./config/ParmsConfig/DLRBConfig.xml')
        global_elements.UlRBConfig_dict = global_elements.xml_to_dict('./config/ParmsConfig/ULRBConfig.xml')
        global_elements.DevicesConfig_dict = global_elements.xml_to_dict('./config/DevicesConfig/DevicesConfig.xml')
        global_elements.dutNameList = global_elements.ergodic_dir(global_elements.DUTCONFIGXMLPATH)
        global_elements.MCSindex_dict = global_elements.xml_to_dict('./config/ParmsConfig/MCSindex.xml')
        global_elements.DLlevel_dict = global_elements.xml_to_dict('./config/ParmsConfig/DLLevel.xml')
        global_elements.LTEBW_dict = global_elements.xml_to_dict('./config/ParmsConfig/LTEBandwidthConfig.xml')
        global_elements.LTEChannel_dict = global_elements.xml_to_dict('./config/ParmsConfig/LTEChannelConfig.xml')
        global_elements.LTERBConfig_dict = global_elements.xml_to_dict('./config/ParmsConfig/LTERBConfig.xml')
        # 初始化DUT激活状态都是不激活
        for dut_index in range(len(global_elements.dutNameList)):
            global_elements.dutAcitveStateDict[global_elements.dutNameList[dut_index]] = False

        self.ProgressBar.setStyleSheet('color: #80CE0F;')

        self.setWindowState(Qt.WindowMaximized)
        self.gridLayout_summry.setColumnMinimumWidth(0, 180)
        self.ProgressBar.setValue(0)

        self.actionStop.setEnabled(False)
        self.actionPause.setEnabled(False)

        self.tableWidget_plan.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 自适应水平宽度
        self.tableWidget_result.setColumnCount(24)
        self.tableWidget_result.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)  # 自适应水平宽度
        self.tableWidget_result.setHorizontalHeaderLabels(
            ['Test Type', 'Test Case', 'Test Item', 'Result', 'Low Limit', 'High Limit', 'Unit', 'Judgement', 'Waveform',
             'Test Band', 'BandWidth',
             'SCS', 'Test ID', 'RB Allocation', 'MCS Index', 'Modulation', 'DL_Channel', 'UL_Channel', 'DL_Freq(MHz)',
             'UL_Freq(MHz)', 'Volt.(V)', 'Temp.(℃)',
             'Time', 'Remark'])
        self.tableWidget_faileditems.setColumnCount(24)
        self.tableWidget_faileditems.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)  # 自适应水平宽度
        self.tableWidget_faileditems.setHorizontalHeaderLabels(
            ['Test Type', 'Test Case', 'Test Item', 'Result', 'Low Limit', 'High Limit', 'Unit', 'Judgement',
             'Waveform',
             'Test Band', 'BandWidth',
             'SCS', 'Test ID', 'RB Allocation', 'MCS Index', 'Modulation', 'DL_Channel', 'UL_Channel', 'DL_Freq(MHz)',
             'UL_Freq(MHz)', 'Volt.(V)', 'Temp.(℃)',
             'Time', 'Remark'])
        # self.tableWidget_plan.horizontalHeader().setStyleSheet('QHeaderView::section{background:rgb(170, 170, 225);}')
        # self.tableWidget_plan.verticalHeader().setStyleSheet('QHeaderView::section{background:rgb(200, 200, 200);}')

        self.label_movie.setMovie(self.movie)


    # 主界面 Start按钮槽函数定义************************************************************************
    def startbtn_click(self):
        # 点击start按钮后更新界面控件状态
        self.actionRun.setEnabled(False)
        self.actionPause.setEnabled(True)
        self.actionStop.setEnabled(True)
        self.actionChannel_Config.setEnabled(False)
        self.actionnew_test_seq.setEnabled(False)
        self.actionSave_Test_sequence.setEnabled(False)
        self.actionLoad_test_sequence.setEnabled(False)
        self.actionDevices_Config.setEnabled(False)
        self.actionDUT.setEnabled(False)
        self.actionReport_Path.setEnabled(False)
        self.actionPath_Loss.setEnabled(False)
        self.actionLast_Config.setEnabled(False)

        self.movie.start()

        rowCount = self.tableWidget_plan.rowCount()
        columnCount = self.tableWidget_plan.columnCount()
        for i in range(rowCount):
            for j in range(columnCount):
                self.tableWidget_plan.item(i, j).setFlags(Qt.NoItemFlags)

        self.tableWidget_result.setRowCount(0)
        self.textBrowser_log.clear()
        self.textBrowser_scpi.clear()
        self.tableWidget_faileditems.setRowCount(0)

        # 启动计时
        self.startTime = datetime.now()
        self.timer.start()

        global_elements.maxOutputPowerResutl = []
        global_elements.maxOutputPowerTestid = []
        global_elements.maxOutputPowerLow = []
        global_elements.maxOutputPowerhigh = []

        rr = self.gridLayout_summry.indexOf(self.canvas)
        if rr != -1:
            self.axes2.cla()
            self.axes2.patch.set_alpha(0)
            self.axes1.cla()
            self.axes1.patch.set_alpha(0)
            self.canvas.draw()

        # 开启另一个线程处理测试过程，以防界面在测试过程中卡死
        self.test_thread.start()

    def totalstep(self, content):
        self.label_totalstep.setText('Total Step: ' + content)

    def showtime(self):
        self.stopTime = datetime.now()
        time_delta = self.stopTime - self.startTime
        time_delta_sec = int(time_delta.total_seconds())
        hour_num = int(time_delta_sec / 3600)
        time_sec_remaining = time_delta_sec % 3600
        min_num = int(time_sec_remaining / 60)
        sec_num = time_sec_remaining % 60
        self.label_time.setText(str(hour_num).zfill(2) + ': ' + str(min_num).zfill(2) + ': ' +
                                str(sec_num).zfill(2))

    # 主界面Pause按钮槽函数
    def pausebtn_click(self):
        # global_element.IsPause = True
        # self.actionPause.setEnabled(False)
        # self.actionStop.setEnabled(False)
        # user_choose = win32api.MessageBox(0, '测试已暂停，按OK继续!', '提醒', win32con.MB_OK)
        # if user_choose == 1:
        #     global_element.IsPause = False
        #     self.actionPause.setEnabled(True)
        #     self.actionStop.setEnabled(True)
        if self.test_thread.handle != -1:
            self.actionPause.setEnabled(False)
            self.actionStop.setEnabled(False)
            ret = SuspendThread(self.test_thread.handle)
            user_choose = QMessageBox.information(self, 'Tip', 'Test has been suspended, press Yes to continue!',
                                                  QMessageBox.Yes)
            if user_choose == QMessageBox.Yes:
                self.actionPause.setEnabled(True)
                self.actionStop.setEnabled(True)
                ret = ResumeThread(self.test_thread.handle)

    # 主界面Stop按钮槽函数
    def stopbtn_click(self):
        # user_choose = win32api.MessageBox(0, 'Confirm to stop testing?', 'Tip', win32con.MB_OKCANCEL)
        user_choose = QMessageBox.question(self, 'Tip', 'Are you sure to abort the test?',
                                           QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if user_choose == QMessageBox.Yes:
            # global_elements.IsStop = True  # 此参数用于report tool方法是否还能运行
            time.sleep(3)  # 等待3秒，以防正在处理的report文件损坏
            self.testthread_exit('User abort test！')

    # 弹出创建新的测试序列窗口
    def newseq(self):
        if global_elements.dutActiveDict == {}:
            QMessageBox.warning(self, 'Tip', 'Please active a DUT first!', QMessageBox.Yes)
        else:
            self.newseqWin = TestseqWin()
            self.newseqWin.okSig.connect(self.createTestSeq)
            self.newseqWin.show()

    # 在主界面更新测试序列
    def createTestSeq(self, content):
        band_list = content[0]
        testcase_list = content[2]
        self.tableWidget_plan.setRowCount(len(testcase_list))
        self.tableWidget_plan.setColumnCount(len(band_list))

        self.tableWidget_plan.setHorizontalHeaderLabels(band_list)
        self.tableWidget_plan.setVerticalHeaderLabels(testcase_list)

        # 在主界面plan表格添加配置参数按钮
        for band_index in range(len(band_list)):
            for case_index in range(len(testcase_list)):
                # self.parms_btn = QPushButton()
                # self.parms_btn.setText('Params...')
                # self.parms_btn.clicked.connect(self.parms_btnclicked)
                # self.tableWidget_plan.setCellWidget(case_index, band_index, self.parms_btn)
                self.parms_item = QTableWidgetItem()
                self.parms_item.setCheckState(Qt.Checked)
                self.parms_item.setText('Params...')
                # self.parms_item.setForeground(Qt.white)

                self.tableWidget_plan.setItem(case_index, band_index, self.parms_item)

    # 配置参数按钮槽函数
    def parms_btnclicked(self, index):
        # 获取当前点击按钮的位置，并取得对应测试项的step列表
        self.tableWidget_plan.setCurrentCell(index.row(), index.column())
        global_elements.clicked_colindex = self.tableWidget_plan.currentColumn()
        global_elements.clicked_rowindex = self.tableWidget_plan.currentRow()
        col_index = self.tableWidget_plan.currentColumn()
        row_index = self.tableWidget_plan.currentRow()
        currentSteplist = []
        currentband = ''
        currentcase = ''
        if isinstance(global_elements.testseq_dict['xml']['testseq'], list):
            if isinstance(global_elements.testseq_dict['xml']['testseq'][col_index]['testplan'], list):
                currentband = global_elements.testseq_dict['xml']['testseq'][col_index]['testplan'][row_index]['@band']
                currentcase = global_elements.testseq_dict['xml']['testseq'][col_index]['testplan'][row_index]['@testcase']
                currentSteplist = global_elements.testseq_dict['xml']['testseq'][col_index]['testplan'][row_index]['step']
            elif isinstance(global_elements.testseq_dict['xml']['testseq'][col_index]['testplan'], dict):
                currentband = global_elements.testseq_dict['xml']['testseq'][col_index]['testplan']['@band']
                currentcase = global_elements.testseq_dict['xml']['testseq'][col_index]['testplan']['@testcase']
                currentSteplist = global_elements.testseq_dict['xml']['testseq'][col_index]['testplan']['step']
        elif isinstance(global_elements.testseq_dict['xml']['testseq'], dict):
            if isinstance(global_elements.testseq_dict['xml']['testseq']['testplan'], list):
                currentband = global_elements.testseq_dict['xml']['testseq']['testplan'][row_index]['@band']
                currentcase = global_elements.testseq_dict['xml']['testseq']['testplan'][row_index]['@testcase']
                currentSteplist = global_elements.testseq_dict['xml']['testseq']['testplan'][row_index]['step']
            elif isinstance(global_elements.testseq_dict['xml']['testseq']['testplan'], dict):
                currentband = global_elements.testseq_dict['xml']['testseq']['testplan']['@band']
                currentcase = global_elements.testseq_dict['xml']['testseq']['testplan']['@testcase']
                currentSteplist = global_elements.testseq_dict['xml']['testseq']['testplan']['step']

        self.parms_win = CaseParmsWin(currentSteplist, currentband, currentcase)
        self.parms_win.show()

    # plan表格cell被单击时更新checkstatue到待测试字典
    def parms_clicked(self, index):
        self.tableWidget_plan.setCurrentCell(index.row(), index.column())
        col_index = self.tableWidget_plan.currentColumn()
        row_index = self.tableWidget_plan.currentRow()

        current_checkstate = self.tableWidget_plan.item(row_index, col_index).checkState()
        final_checkstate = 'True' if current_checkstate == Qt.Checked else 'False'

        if isinstance(global_elements.testseq_dict['xml']['testseq'], dict):
            global_elements.testseq_dict['xml']['testseq'] = [global_elements.testseq_dict['xml']['testseq']]

        if isinstance(global_elements.testseq_dict['xml']['testseq'][col_index]['testplan'], dict):
            global_elements.testseq_dict['xml']['testseq'][col_index]['testplan'] = [global_elements.testseq_dict['xml']['testseq'][col_index]['testplan']]

        global_elements.testseq_dict['xml']['testseq'][col_index]['testplan'][row_index]['@enable'] = final_checkstate

    # 保存当前测试序列字典内容到xml 测试序列
    def saveseq(self):
        if len(global_elements.testseq_dict['xml']['testseq']) == 0:
            QMessageBox.warning(self, 'Tip', 'There is nothing to save!', QMessageBox.Yes)
        if len(global_elements.testseq_dict['xml']['testseq']) > 0:
            fileName_choose, filetype = QFileDialog.getSaveFileName(self,
                                                                     'Save test sequences',
                                                                     self.cwd,
                                                                     'TestSeq Files (*.seq);;All Files (*)')

            if fileName_choose != '':
                global_elements.dict_to_xmlstr(global_elements.testseq_dict, fileName_choose)

    def loadseq(self):
        fileName_choose, filetype = QFileDialog.getOpenFileName(self,
                                                                'Selecting Test Sequences',
                                                                self.cwd,
                                                                'TestSeq Files (*.seq);;All Files (*)')
        if fileName_choose != '':
            global_elements.testseq_dict = {'xml': {'testseq': []}}
            self.tableWidget_plan.clear()
            xml_dict = global_elements.xml_to_dict(fileName_choose)
            if isinstance(xml_dict['xml']['testseq'], dict):
                xml_dict['xml']['testseq'] = [xml_dict['xml']['testseq']]

            band_list = []
            case_list = []
            for band_index in range(len(xml_dict['xml']['testseq'])):
                if isinstance(xml_dict['xml']['testseq'][band_index]['testplan'], dict):
                    xml_dict['xml']['testseq'][band_index]['testplan'] = [xml_dict['xml']['testseq'][band_index]['testplan']]
                band_list.append(xml_dict['xml']['testseq'][band_index]['testplan'][0]['@band'])

                for case_index in range(len(xml_dict['xml']['testseq'][band_index]['testplan'])):
                    if isinstance(xml_dict['xml']['testseq'][band_index]['testplan'][case_index]['step'], dict):
                        xml_dict['xml']['testseq'][band_index]['testplan'][case_index]['step'] = [xml_dict['xml']['testseq'][band_index]['testplan'][case_index]['step']]

            for case_index in range(len(xml_dict['xml']['testseq'][0]['testplan'])):
                case_list.append(xml_dict['xml']['testseq'][0]['testplan'][case_index]['@testcase'])

            global_elements.testseq_dict = xml_dict

            self.tableWidget_plan.setColumnCount(len(band_list))
            self.tableWidget_plan.setRowCount(len(case_list))
            self.tableWidget_plan.setHorizontalHeaderLabels(band_list)
            self.tableWidget_plan.setVerticalHeaderLabels(case_list)

            for col in range(len(xml_dict['xml']['testseq'])):
                for row in range(len(xml_dict['xml']['testseq'][col]['testplan'])):
                    self.parms_item = QTableWidgetItem()
                    if xml_dict['xml']['testseq'][col]['testplan'][row]['@enable'] == 'True':
                        self.parms_item.setCheckState(Qt.Checked)
                    else:
                        self.parms_item.setCheckState(Qt.Unchecked)
                    self.parms_item.setText('Params...')
                    # self.parms_item.setForeground(Qt.darkBlue)
                    self.tableWidget_plan.setItem(row, col, self.parms_item)

    def device_config(self):
        """
        打开设备配置窗口
        :return:
        """
        self.device_win = DeviceWin()
        self.device_win.show()

    def dut_edit(self):
        """
        打开DUT配置窗口
        :return:
        """
        self.dut_win = DUTWin()
        self.dut_win.oksig.connect(self.updateActiveDUT)
        self.dut_win.show()

    # 更新主界面激活DUT的内容
    def updateActiveDUT(self, content):
        self.label_dutacitve.setText(content)

    # 定义report工具的槽函数
    def reportmenuclick(self):
        fileName_choose, filetype = QFileDialog.getSaveFileName(self,
                                                                'Report Preservation',
                                                                self.rppath,
                                                                'Excel Files (*.xlsx);;All Files (*)')

        if fileName_choose != '':
            zhmodel = re.compile(u'[\u4e00-\u9fa5]')
            match = zhmodel.search(fileName_choose)
            if match:
                # win32api.MessageBox(0, 'The report path can not contain Chinese!')
                QMessageBox.warning(self, 'Warning', 'The report path can not contain Chinese!', QMessageBox.Yes)
                global_elements.REPORTPATH = ''
            else:
                global_elements.REPORTPATH = fileName_choose
                self.label_report.setText(fileName_choose)

    # 定义点击Path Loss后的编辑窗口
    def pathlosswin(self):
        self.loss_win = PathLossWin()
        self.loss_win.oksig.connect(self.updateLossLable)
        self.loss_win.show()

    # 更新主界面Loss的Lable
    def updateLossLable(self, content):
        str_temp = 'RF1 COM: ' + content[0] + '\nRF2 COM: ' + content[1] + '\nRF3 COM: ' + content[2] + '\nRF4 COM: ' + content[3]
        self.label_loss.setText(str_temp)

    # 打开channel界面
    def channelwin(self):
        self.channelwin_ex = channelWin()
        self.channelwin_ex.show()

    # 更新SCPI UI
    def updataScpiUi(self, content):
        self.textBrowser_scpi.append(content)


    # 更新测试状态界面
    def stateupdateUi(self, content):
        time_now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        self.textBrowser_log.append(time_now + ':        ' + content)
        self.statusBar().showMessage(content)

    # 定义接收到test线程退出信号后的槽函数
    def testthread_exit(self, content):

        global_elements.isStatusError = True
        time_now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        self.textBrowser_log.append(time_now + ':        ' + content)
        self.textBrowser_log.append(time_now + ':        ' + 'Tip:    Program abnormal exit!')
        self.test_thread.terminate()
        # self.test_thread.quit()
        self.test_thread.wait()

    # 定义接收到test线程完成信号后的槽函数
    def testfinish(self):
        self.movie.stop()
        self.timer.stop()
        # 保存log到txt
        try:
            str_text = self.textBrowser_log.toPlainText()
            qS = str(str_text)
            path_file = global_elements.REPORTPATH[:-4] + 'txt'

            f = open(path_file, 'a+')
            f.write('{}'.format(qS))
            f.close()
        except Exception as e:
            pass

        # 保存scpi到txt
        try:
            str_text = self.textBrowser_scpi.toPlainText()
            qS = str(str_text)
            path_file = global_elements.REPORTPATH[:-5] + '_scpi.txt'

            f = open(path_file, 'a+')
            f.write('{}'.format(qS))
            f.close()
        except Exception as e:
            pass

        # painter = QPainter(self)
        # painter.begin(self)
        # painter.setPen(QColor(255, 0, 0))
        # painter.setFont(QFont("SimSun", 40))
        # painter.drawText(self.textBrowser_log.rect(),Qt.AlignCenter, 'FAILED')
        # painter.end()

        if global_elements.isStatusError == False:
            self.statusBar().showMessage('The test is completed!')
            # report_handle.test_finish_rep_handle()
            user_choose = QMessageBox.information(self, 'Tip', 'Test Finished!', QMessageBox.Yes)
        else:
            self.statusBar().showMessage('The test is aborted!')
            # report_handle.test_finish_rep_handle()
            user_choose = QMessageBox.information(self, 'Tip', 'Test aborted!', QMessageBox.Yes)
        if user_choose == QMessageBox.Yes:
            self.actionRun.setEnabled(True)
            self.actionPause.setEnabled(False)
            self.actionStop.setEnabled(False)
            self.actionChannel_Config.setEnabled(True)
            self.actionnew_test_seq.setEnabled(True)
            self.actionSave_Test_sequence.setEnabled(True)
            self.actionLoad_test_sequence.setEnabled(True)
            self.actionDevices_Config.setEnabled(True)
            self.actionDUT.setEnabled(True)
            self.actionReport_Path.setEnabled(True)
            self.actionPath_Loss.setEnabled(True)
            self.actionLast_Config.setEnabled(True)

            rowCount = self.tableWidget_plan.rowCount()
            columnCount = self.tableWidget_plan.columnCount()
            for i in range(rowCount):
                for j in range(columnCount):
                    self.tableWidget_plan.item(i, j).setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)

    def lastconfig(self):
        lastconfig_dict = global_elements.xml_to_dict('./config/Last Config.xml')
        # 更新Report路径
        self.label_report.setText(lastconfig_dict['xml']['lastconfig']['reportpath'])
        global_elements.REPORTPATH = lastconfig_dict['xml']['lastconfig']['reportpath']
        # 更新loss信息
        self.label_loss.setText('RF1 COM: ' + lastconfig_dict['xml']['lastconfig']['lossfilepath1'] + '\nRF2 COM: ' + \
                          lastconfig_dict['xml']['lastconfig']['lossfilepath2'] + '\nRF3 COM: ' + \
                          lastconfig_dict['xml']['lastconfig']['lossfilepath3'] + '\nRF4 COM: ' + \
                          lastconfig_dict['xml']['lastconfig']['lossfilepath4'])
        global_elements.pathLossDict['RF1'] = lastconfig_dict['xml']['lastconfig']['lossfilepath1']
        global_elements.pathLossDict['RF2'] = lastconfig_dict['xml']['lastconfig']['lossfilepath2']
        global_elements.pathLossDict['RF3'] = lastconfig_dict['xml']['lastconfig']['lossfilepath3']
        global_elements.pathLossDict['RF4'] = lastconfig_dict['xml']['lastconfig']['lossfilepath4']
        # 更新DUT信息
        activedutname = lastconfig_dict['xml']['lastconfig']['DUT']
        self.label_dutacitve.setText(activedutname)
        global_elements.dutAcitveStateDict[activedutname] = True
        global_elements.dutActiveDict = global_elements.xml_to_dict('./config/DUTConfig/' + activedutname + '.xml')

    # 定义报告更新槽函数
    def reportupdata(self, content):
        data_list = content
        current_row_count = self.tableWidget_result.rowCount()

        self.tableWidget_result.setRowCount(current_row_count + 1)
        self.tableWidget_result.setRowHeight(current_row_count, 10)
        for i in range(len(data_list)):
            item = QTableWidgetItem()
            item.setText(data_list[i])
            if i in [6, 7]:
                if data_list[i] == 'Passed':
                    item.setForeground(Qt.green)
                elif data_list[i] == 'Failed':
                    item.setForeground(Qt.red)
                elif data_list[i] == 'Inconclusivee':
                    item.setForeground(Qt.yellow)
                else:
                    item.setForeground(Qt.white)
            else:
                item.setForeground(Qt.white)
            self.tableWidget_result.setItem(current_row_count, i, item)
            self.tableWidget_result.item(current_row_count, i).setFlags(Qt.NoItemFlags)
        self.tableWidget_result.scrollToBottom()

    # 定义failed报告更新槽函数
    def faileditemsupdataSingle(self, content):
        data_list = content
        current_row_count = self.tableWidget_faileditems.rowCount()

        self.tableWidget_faileditems.setRowCount(current_row_count + 1)
        self.tableWidget_faileditems.setRowHeight(current_row_count, 10)
        for i in range(len(data_list)):
            item = QTableWidgetItem()
            item.setText(data_list[i])
            if i in [6, 7]:
                if data_list[i] == 'Passed':
                    item.setForeground(Qt.green)
                elif data_list[i] == 'Failed':
                    item.setForeground(Qt.red)
                elif data_list[i] == 'Inconclusivee':
                    item.setForeground(Qt.yellow)
                else:
                    item.setForeground(Qt.white)
            else:
                item.setForeground(Qt.white)
            self.tableWidget_faileditems.setItem(current_row_count, i, item)
            self.tableWidget_result.item(current_row_count, i).setFlags(Qt.NoItemFlags)
        self.tableWidget_faileditems.scrollToBottom()


    # 定义收到更新测试进度的信号后的槽函数
    def processrateupdata(self, content):
        self.ProgressBar.setValue(float(content))

    # 主界面更新summry槽函数
    def summryupdata(self, content_list):
        self.gridLayout_summry.addWidget(self.canvas)
        self.setLayout(self.gridLayout_summry)
        datalist = content_list
        self.axes1.cla()
        lables = ['Passed: ' + str(datalist[0]), 'Failed: ' + str(datalist[1]), 'Inconclusive: ' + str(datalist[2])]
        explode = (0.1, 0, 0)
        colors = ['g', 'r', 'y']

        patches, l_text, p_text = self.axes1.pie(datalist, explode=explode, labels=lables, colors=colors,
                                          autopct='%1.1f%%',
                                          shadow=False, startangle=150)
        self.axes1.set_title('Summary', color='w')
        self.axes1.axis('equal')
        legend = self.axes1.legend(loc='upper left', bbox_to_anchor=(-0.1, 1), frameon=True)
        frame = legend.get_frame()
        frame.set_alpha(0.5)
        frame.set_facecolor('lightcyan')  # 设置图例legend背景透明
        for l_t in l_text:
            l_t.set_color('none')
        # frame.set_edgecolor('none')
        self.axes1.patch.set_alpha(0)
        self.canvas.draw()

    def resultChartClear(self):
        self.axes2.cla()
        # self.axes2.patch.set_facecolor("c")
        self.axes2.patch.set_alpha(0)
        self.canvas.draw()

    def freErrorChartUpdata(self, content):
        self.gridLayout_summry.addWidget(self.canvas)
        self.setLayout(self.gridLayout_summry)
        Presult = content[0]
        Presult_list = [None if i == -999 else i for i in Presult]
        Plow_list = content[1]
        Phigh_list = content[2]
        Ptestid_list = content[3]
        self.axes2.cla()
        ln_resutl = self.axes2.scatter(Ptestid_list, Presult_list, color='blue', linewidth=3.0)
        ln_resutl.set_label('Meas Value')

        if len(Phigh_list) == 1:
            ln_high = self.axes2.axhline(y=Phigh_list[0], xmin=0.1, xmax=0.9, color='red')
            ln_high.set_label('High Limit')
            if global_elements.test_case_name != 'ts138521_1 6.3.1 Minimum output power':
                ln_low = self.axes2.axhline(y=Plow_list[0], xmin=0.1, xmax=0.9, color='red')
                ln_low.set_label('Low Limit')
        else:
            pass
        self.axes2.set_ylabel('Frequency Error(Hz)', color='w')
        self.axes2.set_xlabel('Test ID', color='w')
        self.axes2.set_title('Frequency Error ' +
                             global_elements.NR_SCS_r + ' '
                             + global_elements.NR_bw_r + ' '
                             + global_elements.NR_ch_r, color='w')
        self.axes2.spines['left'].set_visible(False)  # 去掉左边框
        self.axes2.spines['right'].set_visible(False)  # 去掉右边框
        self.axes2.tick_params(axis='x', labelcolor='w')
        self.axes2.tick_params(axis='y', labelcolor='w')
        self.axes2.patch.set_alpha(0)  # 背景透明度
        legend = self.axes2.legend(loc='best', frameon=True)  # 边框
        frame = legend.get_frame()
        frame.set_alpha(0.5)
        frame.set_facecolor('lightcyan')  # 设置图例legend背景透明
        self.canvas.draw()

    def maxPowerChartUpdata(self, content):
        self.gridLayout_summry.addWidget(self.canvas)
        self.setLayout(self.gridLayout_summry)
        Presult = content[0]
        Presult_list = [None if i==-999 else i for i in Presult]
        Plow_list = content[1]
        Phigh_list = content[2]
        Ptestid_list = content[3]
        self.axes2.cla()
        ln_resutl = self.axes2.scatter(Ptestid_list, Presult_list, color='blue', linewidth=3.0)
        ln_resutl.set_label('Meas Value')

        if len(Phigh_list) == 1:
            ln_high = self.axes2.axhline(y=Phigh_list[0], xmin=0.1, xmax=0.9, color='red')
            ln_high.set_label('High Limit')
            if global_elements.test_case_name not in  ['ts138521_1 6.3.1 Minimum output power',
                                                       'ts138521_1 6.4.2.2 Carrier leakage']:
                ln_low = self.axes2.axhline(y=Plow_list[0], xmin=0.1, xmax=0.9, color='red')
                ln_low.set_label('Low Limit')
        else:
            ln_high = self.axes2.plot(Ptestid_list, Phigh_list, color='red', linewidth=1.0, linestyle='-')
            ln_high[0].set_label('High Limit')
            if global_elements.test_case_name != 'ts138521_1 6.3.1 Minimum output power':
                ln_low = self.axes2.plot(Ptestid_list, Plow_list, color='red', linewidth=1.0, linestyle='-')
                ln_low[0].set_label('Low Limit')
        self.axes2.set_ylabel('Power Value(dBm)', color='w')

        if global_elements.test_case_name == 'ts138521_1 6.2.1 UE maximum output power':
            self.axes2.set_xlabel('Test ID', color='w')
            self.axes2.set_title('Max Output Power ' +
                                 global_elements.NR_SCS_r + ' '
                                 + global_elements.NR_bw_r + ' '
                                 + global_elements.NR_ch_r, color='w')
        elif global_elements.test_case_name == 'ts138521_1 6.2.2 UE maximum output power reduction':
            self.axes2.set_xlabel('Test ID', color='w')
            self.axes2.set_title('MPR ' +
                                 global_elements.NR_SCS_r + ' '
                                 + global_elements.NR_bw_r + ' '
                                 + global_elements.NR_ch_r, color='w')
        elif global_elements.test_case_name == 'ts138521_1 6.2.4 Configured transmitted power':
            self.axes2.set_xlabel('Test ID_Test Point', color='w')
            self.axes2.set_title('Configured Power ' +
                                 global_elements.NR_SCS_r + ' '
                                 + global_elements.NR_bw_r + ' '
                                 + global_elements.NR_ch_r, color='w')
        elif global_elements.test_case_name == 'ts138521_1 6.3.1 Minimum output power':
            self.axes2.set_xlabel('Test ID', color='w')
            self.axes2.set_title('Min Output Power ' +
                                 global_elements.NR_SCS_r + ' '
                                 + global_elements.NR_bw_r + ' '
                                 + global_elements.NR_ch_r, color='w')
        elif global_elements.test_case_name == 'ts138521_1 6.4.2.2 Carrier leakage':
            self.axes2.set_xlabel('Exp. Power', color='w')
            self.axes2.set_title('Carrier leakage ' +
                                 global_elements.NR_SCS_r + ' '
                                 + global_elements.NR_bw_r + ' '
                                 + global_elements.NR_ch_r, color='w')
        self.axes2.spines['left'].set_visible(False)  # 去掉左边框
        self.axes2.spines['right'].set_visible(False)  # 去掉右边框
        self.axes2.tick_params(axis='x', labelcolor='w')
        self.axes2.tick_params(axis='y', labelcolor='w')
        self.axes2.patch.set_alpha(0)                      # 背景透明度
        legend = self.axes2.legend(loc='best', frameon=True)   # 边框
        frame = legend.get_frame()
        frame.set_alpha(0.5)
        frame.set_facecolor('lightcyan')  # 设置图例legend背景透明
        self.canvas.draw()

    def inbandemissionChartUpdata(self, content):
        self.gridLayout_summry.addWidget(self.canvas)
        self.setLayout(self.gridLayout_summry)
        Presult = content[0]
        Presult_list = [None if i==-999 else i for i in Presult]
        Plow_list = content[1]
        Phigh_list = content[2]
        Ptestid_list = content[3]
        self.axes2.cla()
        ln_resutl = self.axes2.scatter(Ptestid_list, Presult_list, color='blue', linewidth=3.0)
        ln_resutl.set_label('Meas Value')

        if len(Phigh_list) == 1:
            ln_low = self.axes2.axhline(y=Plow_list[0], xmin=0.1, xmax=0.9, color='red')
            ln_low.set_label('Low Limit')
        else:
            ln_low = self.axes2.plot(Ptestid_list, Plow_list, color='red', linewidth=1.0, linestyle='-')
            ln_low[0].set_label('Low Limit')
        self.axes2.set_ylabel('Inband Emission Margin Value(dB)', color='w')

        self.axes2.set_xlabel('Test ID@Exp. Power', color='w')
        self.axes2.set_title('Inband emission Margin ' +
                             global_elements.NR_SCS_r + ' '
                             + global_elements.NR_bw_r + ' '
                             + global_elements.NR_ch_r, color='w')

        self.axes2.spines['left'].set_visible(False)  # 去掉左边框
        self.axes2.spines['right'].set_visible(False)  # 去掉右边框
        self.axes2.tick_params(axis='x', labelcolor='w', labelrotation=90)
        self.axes2.tick_params(axis='y', labelcolor='w')
        self.axes2.patch.set_alpha(0)                      # 背景透明度
        legend = self.axes2.legend(loc='best', frameon=True)   # 边框
        frame = legend.get_frame()
        frame.set_alpha(0.5)
        frame.set_facecolor('lightcyan')  # 设置图例legend背景透明
        self.canvas.draw()

    def onoffChartUpdata(self, content):
        self.gridLayout_summry.addWidget(self.canvas)
        self.setLayout(self.gridLayout_summry)
        Presult = content[0]
        Presult_list = [None if i == -999 else i for i in Presult]
        Plow_list = content[1]
        Phigh_list = content[2]
        Ptestlabels_list = content[3]
        self.axes2.cla()
        ln_resutl = self.axes2.scatter(Ptestlabels_list, Presult_list, color='blue', linewidth=3.0)
        ln_resutl.set_label('Meas Value')
        ln_high = self.axes2.plot(Ptestlabels_list, Phigh_list, color='red', linewidth=1.0, linestyle='-')
        ln_high[0].set_label('High Limit')

        ln_low = self.axes2.axhline(y=Plow_list[1], xmin=0.45, xmax=0.55, color='red')
        ln_low.set_label('Low Limit')

        self.axes2.set_ylabel('Power Value(dBm)', color='w')
        self.axes2.set_xlabel('ON OFF Power', color='w')
        self.axes2.set_title('ON OFF Power ' +
                             global_elements.NR_SCS_r + ' '
                             + global_elements.NR_bw_r + ' '
                             + global_elements.NR_ch_r, color='w')
        self.axes2.spines['left'].set_visible(False)  # 去掉左边框
        self.axes2.spines['right'].set_visible(False)  # 去掉右边框
        self.axes2.tick_params(axis='x', labelcolor='w')
        self.axes2.tick_params(axis='y', labelcolor='w')
        self.axes2.patch.set_alpha(0)  # 背景透明度
        legend = self.axes2.legend(loc='best', frameon=True)  # 边框
        frame = legend.get_frame()
        frame.set_alpha(0.5)
        frame.set_facecolor('lightcyan')  # 设置图例legend背景透明
        self.canvas.draw()

    def evmChartUpdata(self, content):
        self.gridLayout_summry.addWidget(self.canvas)
        self.setLayout(self.gridLayout_summry)
        evmRMSresult = content[0]
        evmRMSresult_list = [None if i==-999 else i for i in evmRMSresult]
        evmDMRSresult = content[1]
        evmDMRSresult_list = [None if i==-999 else i for i in evmDMRSresult]
        Plow_list = content[2]
        Phigh_list = content[3]
        Ptestid_list = content[4]
        self.axes2.cla()
        ln_resutl1 = self.axes2.scatter(Ptestid_list, evmRMSresult_list, color='blue', linewidth=0.1)
        ln_resutl1.set_label('EVM RMS Meas Value')

        ln_resutl2 = self.axes2.scatter(Ptestid_list, evmDMRSresult_list, color='yellow', linewidth=0.1)
        ln_resutl2.set_label('EVM DMRS Meas Value')

        if len(Phigh_list) == 1:
            ln_high = self.axes2.axhline(y=Phigh_list[0], xmin=0.1, xmax=0.9, color='red')
            ln_high.set_label('High Limit')
        else:
            ln_high = self.axes2.plot(Ptestid_list, Phigh_list, color='red', linewidth=1.0, linestyle='-')
            ln_high[0].set_label('High Limit')

        self.axes2.set_ylabel('EVM Value(%)', color='w')

        self.axes2.set_xlabel('Test ID', color='w')
        self.axes2.set_title('EVM PUSCH ' +
                             global_elements.NR_SCS_r + ' '
                             + global_elements.NR_bw_r + ' '
                             + global_elements.NR_ch_r, color='w')

        self.axes2.spines['left'].set_visible(False)  # 去掉左边框
        self.axes2.spines['right'].set_visible(False)  # 去掉右边框
        self.axes2.tick_params(axis='x', labelcolor='w', labelrotation=90)
        self.axes2.tick_params(axis='y', labelcolor='w')
        self.axes2.patch.set_alpha(0)                      # 背景透明度
        legend = self.axes2.legend(loc='best', frameon=True)   # 边框
        frame = legend.get_frame()
        frame.set_alpha(0.5)
        frame.set_facecolor('lightcyan')  # 设置图例legend背景透明
        self.canvas.draw()

    def evmflatnessChartUpdata(self, content):
        self.gridLayout_summry.addWidget(self.canvas)
        self.setLayout(self.gridLayout_summry)
        Presult = content[0]
        Presult_list = [None if i==-999 else i for i in Presult]
        Plow_list = content[1]
        Phigh_list = content[2]
        Ptestid_list = content[3]
        self.axes2.cla()
        ln_resutl = self.axes2.scatter(Ptestid_list, Presult_list, color='blue', linewidth=3.0)
        ln_resutl.set_label('Meas Value')

        if len(Phigh_list) == 1:
            ln_high = self.axes2.axhline(y=Phigh_list[0], xmin=0.1, xmax=0.9, color='red')
            ln_high.set_label('High Limit')
        else:
            ln_high = self.axes2.plot(Ptestid_list, Phigh_list, color='red', linewidth=1.0, linestyle='-')
            ln_high[0].set_label('High Limit')

        self.axes2.set_ylabel('Meas Value(dB)', color='w')


        self.axes2.set_xlabel('Test ID_Ripple', color='w')
        self.axes2.set_title('EVM Equalizer Spectrum Flatness ' +
                             global_elements.NR_SCS_r + ' '
                             + global_elements.NR_bw_r + ' '
                             + global_elements.NR_ch_r, color='w')

        self.axes2.spines['left'].set_visible(False)  # 去掉左边框
        self.axes2.spines['right'].set_visible(False)  # 去掉右边框
        self.axes2.tick_params(axis='x', labelcolor='w', labelrotation=90)
        self.axes2.tick_params(axis='y', labelcolor='w')
        self.axes2.patch.set_alpha(0)                      # 背景透明度
        legend = self.axes2.legend(loc='best', frameon=True)   # 边框
        frame = legend.get_frame()
        frame.set_alpha(0.5)
        frame.set_facecolor('lightcyan')  # 设置图例legend背景透明
        self.canvas.draw()

    def bwChartUpdata(self, content):
        self.gridLayout_summry.addWidget(self.canvas)
        self.setLayout(self.gridLayout_summry)
        Presult = content[0]
        Presult_list = [None if i==-999 else i for i in Presult]
        Plow_list = content[1]
        Phigh_list = content[2]
        Ptestid_list = content[3]
        self.axes2.cla()
        ln_resutl = self.axes2.scatter(Ptestid_list, Presult_list, color='blue', linewidth=3.0)
        ln_resutl.set_label('Meas Value')

        if len(Phigh_list) == 1:
            ln_high = self.axes2.axhline(y=Phigh_list[0], xmin=0.1, xmax=0.9, color='red')
            ln_high.set_label('High Limit')
        else:
            ln_high = self.axes2.plot(Ptestid_list, Phigh_list, color='red', linewidth=1.0, linestyle='-')
            ln_high[0].set_label('High Limit')
        self.axes2.set_ylabel('BandWidth Value(MHz)', color='w')

        self.axes2.set_xlabel('Test ID', color='w')
        self.axes2.set_title('Occupied Bandwidth ' +
                             global_elements.NR_SCS_r + ' '
                             + global_elements.NR_bw_r + ' '
                             + global_elements.NR_ch_r, color='w')
        self.axes2.spines['left'].set_visible(False)  # 去掉左边框
        self.axes2.spines['right'].set_visible(False)  # 去掉右边框
        self.axes2.tick_params(axis='x', labelcolor='w')
        self.axes2.tick_params(axis='y', labelcolor='w')
        self.axes2.patch.set_alpha(0)                      # 背景透明度
        legend = self.axes2.legend(loc='best', frameon=True)   # 边框
        frame = legend.get_frame()
        frame.set_alpha(0.5)
        frame.set_facecolor('lightcyan')  # 设置图例legend背景透明
        self.canvas.draw()

    def semChartUpdata(self, content):
        self.gridLayout_summry.addWidget(self.canvas)
        self.setLayout(self.gridLayout_summry)
        Presult = content[0]
        Presult_list = [None if i==-999 else i for i in Presult]
        Plow_list = content[1]
        Phigh_list = content[2]
        Ptestid_list = content[3]
        self.axes2.cla()
        ln_resutl = self.axes2.scatter(Ptestid_list, Presult_list, color='blue', linewidth=3.0)
        ln_resutl.set_label('Meas Value')

        if len(Phigh_list) == 1:
            ln_low = self.axes2.axhline(y=Plow_list[0], xmin=0.1, xmax=0.9, color='red')
            ln_low.set_label('Low Limit')
        else:
            ln_low = self.axes2.plot(Ptestid_list, Plow_list, color='red', linewidth=1.0, linestyle='-')
            ln_low[0].set_label('Low Limit')
        self.axes2.set_ylabel('Margin Value(dB)', color='w')

        self.axes2.set_xlabel('Margin', color='w')
        self.axes2.set_title('SEM Margin ' +
                             global_elements.NR_SCS_r + ' '
                             + global_elements.NR_bw_r + ' '
                             + global_elements.NR_ch_r + ' TestID' + global_elements.NR_testid, color='w')

        self.axes2.spines['left'].set_visible(False)  # 去掉左边框
        self.axes2.spines['right'].set_visible(False)  # 去掉右边框
        self.axes2.tick_params(axis='x', labelcolor='w')
        self.axes2.tick_params(axis='y', labelcolor='w')
        self.axes2.patch.set_alpha(0)                      # 背景透明度
        legend = self.axes2.legend(loc='best', frameon=True)   # 边框
        frame = legend.get_frame()
        frame.set_alpha(0.5)
        frame.set_facecolor('lightcyan')  # 设置图例legend背景透明
        self.canvas.draw()

    def aclrChartUpdata(self, content):
        self.gridLayout_summry.addWidget(self.canvas)
        self.setLayout(self.gridLayout_summry)
        Presult = content[0]
        Presult_list = [None if i==-999 else i for i in Presult]
        Plow_list = content[1]
        Phigh_list = content[2]
        Ptestid_list = content[3]
        self.axes2.cla()
        ln_resutl = self.axes2.scatter(Ptestid_list, Presult_list, color='blue', linewidth=3.0)
        ln_resutl.set_label('Meas Value')

        if len(Phigh_list) == 1:
            ln_low = self.axes2.axhline(y=Plow_list[0], xmin=0.1, xmax=0.9, color='red')
            ln_low.set_label('Low Limit')
        else:
            ln_low = self.axes2.plot(Ptestid_list, Plow_list, color='red', linewidth=1.0, linestyle='-')
            ln_low[0].set_label('Low Limit')
        self.axes2.set_ylabel('ACLR Value(dB)', color='w')

        self.axes2.set_xlabel('ACLR', color='w')
        self.axes2.set_title('ACLR ' +
                             global_elements.NR_SCS_r + ' '
                             + global_elements.NR_bw_r + ' '
                             + global_elements.NR_ch_r + ' TestId_' + global_elements.NR_testid, color='w')

        self.axes2.spines['left'].set_visible(False)  # 去掉左边框
        self.axes2.spines['right'].set_visible(False)  # 去掉右边框
        self.axes2.tick_params(axis='x', labelcolor='w', labelrotation=90, labelsize='small')
        self.axes2.tick_params(axis='y', labelcolor='w')
        self.axes2.patch.set_alpha(0)                      # 背景透明度
        legend = self.axes2.legend(loc='best', frameon=True)   # 边框
        frame = legend.get_frame()
        frame.set_alpha(0.5)
        frame.set_facecolor('lightcyan')  # 设置图例legend背景透明
        self.canvas.draw()

    def blerChartUpdata(self, content):
        self.gridLayout_summry.addWidget(self.canvas)
        self.setLayout(self.gridLayout_summry)
        Presult = content[0]
        Presult_list = [None if i==-999 else i for i in Presult]
        Plow_list = content[1]
        Phigh_list = content[2]
        Ptestid_list = content[3]
        self.axes2.cla()
        ln_resutl = self.axes2.scatter(Ptestid_list, Presult_list, color='blue', linewidth=3.0)
        ln_resutl.set_label('Meas Value')

        if len(Phigh_list) == 1:
            ln_high = self.axes2.axhline(y=Phigh_list[0], xmin=0.1, xmax=0.9, color='red')
            ln_high.set_label('High Limit')
        else:
            ln_high = self.axes2.plot(Ptestid_list, Phigh_list, color='red', linewidth=1.0, linestyle='-')
            ln_high[0].set_label('High Limit')

        self.axes2.set_ylabel('BLER Value(%)', color='w')

        if global_elements.test_case_name == 'ts138521_1 7.4 Maximum input level':
            self.axes2.set_xlabel('BW_TestId', color='w')
        else:
            self.axes2.set_xlabel('BW_Channel', color='w')
        self.axes2.set_title('BLER ' + global_elements.NR_SCS_r + ' ', color='w')

        self.axes2.spines['left'].set_visible(False)  # 去掉左边框
        self.axes2.spines['right'].set_visible(False)  # 去掉右边框
        self.axes2.tick_params(axis='x', labelcolor='w', labelrotation=90)
        self.axes2.tick_params(axis='y', labelcolor='w')
        self.axes2.patch.set_alpha(0)                      # 背景透明度
        legend = self.axes2.legend(loc='best', frameon=True)   # 边框
        frame = legend.get_frame()
        frame.set_alpha(0.5)
        frame.set_facecolor('lightcyan')  # 设置图例legend背景透明
        self.canvas.draw()

    def blerSearchChartUpdata(self, content):
        self.gridLayout_summry.addWidget(self.canvas)
        self.setLayout(self.gridLayout_summry)
        Presult = content[0]
        Presult_list = [None if i==-999 else i for i in Presult]
        Plow_list = content[1]
        Phigh_list = content[2]
        Ptestid_list = content[3]
        self.axes2.cla()
        ln_resutl = self.axes2.scatter(Ptestid_list, Presult_list, color='blue', linewidth=3.0)
        ln_resutl.set_label('Meas Value')

        if len(Phigh_list) == 1:
            ln_high = self.axes2.axhline(y=Phigh_list[0], xmin=0.1, xmax=0.9, color='red')
            ln_high.set_label('High Limit')
        else:
            ln_high = self.axes2.plot(Ptestid_list, Phigh_list, color='red', linewidth=1.0, linestyle='-')
            ln_high[0].set_label('High Limit')

        self.axes2.set_ylabel('Search Value(dBm)', color='w')

        self.axes2.set_xlabel('BW_Channel', color='w')
        self.axes2.set_title('Sensitivity Search ' + global_elements.NR_SCS_r + ' ', color='w')

        self.axes2.spines['left'].set_visible(False)  # 去掉左边框
        self.axes2.spines['right'].set_visible(False)  # 去掉右边框
        self.axes2.tick_params(axis='x', labelcolor='w', labelrotation=90)
        self.axes2.tick_params(axis='y', labelcolor='w')
        self.axes2.patch.set_alpha(0)                      # 背景透明度
        legend = self.axes2.legend(loc='best', frameon=True)   # 边框
        frame = legend.get_frame()
        frame.set_alpha(0.5)
        frame.set_facecolor('lightcyan')  # 设置图例legend背景透明
        self.canvas.draw()

    def nsa6_2b_1_3ChartUpdata(self, content):
        self.gridLayout_summry.addWidget(self.canvas)
        self.setLayout(self.gridLayout_summry)
        Presult = content[0]
        Presult_list = [None if i==-999 else i for i in Presult]
        Plow_list = content[1]
        Phigh_list = content[2]
        Ptestid_list = content[3]
        x_list = ['Overall', 'LTE', 'NR']
        self.axes2.cla()
        ln_resutl = self.axes2.scatter(x_list, Presult_list, color='blue', linewidth=3.0)
        ln_resutl.set_label('Meas Value')

        if int(Ptestid_list[0]) in range(1, 7):
            ln_high = self.axes2.axhline(y=Phigh_list[0], xmin=0, xmax=0.3, color='red')
            ln_high.set_label('High Limit')
            ln_low = self.axes2.axhline(y=Plow_list[0], xmin=0, xmax=0.3, color='red')
            ln_low.set_label('Low Limit')
        else:
            ln_high = self.axes2.axhline(y=Phigh_list[0], xmin=0.4, xmax=0.6, color='red')
            ln_high.set_label('High Limit')
            ln_low = self.axes2.axhline(y=Plow_list[0], xmin=0.4, xmax=0.6, color='red')
            ln_low.set_label('Low Limit')

        self.axes2.set_ylabel('Power Value(dBm)', color='w')
        self.axes2.set_xlabel('Output Power', color='w')
        self.axes2.set_title(global_elements.NR_band + ' ' +
                             global_elements.NR_SCS_r + ' '
                             + global_elements.NR_bw + ' '
                             + global_elements.NR_ch + ' TestId:' + global_elements.NR_testid, color='w')

        self.axes2.spines['left'].set_visible(False)  # 去掉左边框
        self.axes2.spines['right'].set_visible(False)  # 去掉右边框
        self.axes2.tick_params(axis='x', labelcolor='w')
        self.axes2.tick_params(axis='y', labelcolor='w')
        self.axes2.patch.set_alpha(0)                      # 背景透明度
        legend = self.axes2.legend(loc='best', frameon=True)   # 边框
        frame = legend.get_frame()
        frame.set_alpha(0.5)
        frame.set_facecolor('lightcyan')  # 设置图例legend背景透明
        self.canvas.draw()


class TestseqWin(QMainWindow, Ui_win_editseq):
    """
        新建测试序列界面
    """
    okSig = pyqtSignal(list)

    def __init__(self, parent=None):
        super(TestseqWin, self).__init__(parent)
        self.setupUi(self)

        self.example_init()

        # 设置为模拟对话框，阻塞上一层窗口
        self.setWindowModality(Qt.ApplicationModal)

        self.listWidget_case.setContextMenuPolicy(Qt.CustomContextMenu)  ######允许右键产生子菜单
        self.listWidget_case.customContextMenuRequested.connect(self.generateMenu)  ####右键菜单

        # 定义信号槽关系
        self.pushButton_cancel.clicked.connect(self.close)
        self.pushButton_ok.clicked.connect(self.okclicked)
        # self.tableWidget_band.cellChanged.connect(self.cellchangedCheck)

    def example_init(self):
        self.tableWidget_band_NSA.horizontalHeader().setVisible(True)
        band_list = []
        for k,v in enumerate(global_elements.ChannelConfig_dict['xml']):
            band_list.append(v)

        # 将不支持的band设置为不可用
        for i in range(self.tableWidget_band.rowCount()):
            if self.tableWidget_band.item(i, 0).text() not in  band_list:
                self.tableWidget_band.item(i, 0).setFlags(Qt.NoItemFlags)
                self.tableWidget_band.item(i, 1).setFlags(Qt.NoItemFlags)

    # def cellchangedCheck(self, content):
    #
    #     current_text = self.tableWidget_band.item(content, 1).text()
    #     scs_list = current_text.split(',')
    #     for scs_item in scs_list:
    #         if scs_item not in ['15', '30', '60']:
    #             self.tableWidget_band.item(content, 1).setForeground(Qt.red)
    #             break
    #
    #         self.tableWidget_band.item(content, 1).setForeground(Qt.white)

    def generateMenu(self, pos):
        """
        右键之后生成右键菜单，并作后续处理
        :param pos: 右键的位置
        :return:
        """

        # 如果有行号，则对相应的DUT生成处理菜单

        menu = QMenu()
        disableAll = menu.addAction(u"Disable All")
        enableAll = menu.addAction(u"Enable All")

        action = menu.exec_(self.listWidget_case.mapToGlobal(pos))
        if action == disableAll:
            self.disableAll()
        elif action == enableAll:
            self.enableAll()


    def disableAll(self):
        rowCount = self.listWidget_case.count()
        for row in range(rowCount):
            self.listWidget_case.item(row).setCheckState(Qt.Unchecked)

    def enableAll(self):
        rowCount = self.listWidget_case.count()
        for row in range(rowCount):
            self.listWidget_case.item(row).setCheckState(Qt.Checked)

    # Ok 按钮点击后槽函数
    def okclicked(self):
        status = True
        band_list = []
        testcase_list = []
        SCS_list = []
        condition_list = []
        tableWidget_band_list = [self.tableWidget_band, self.tableWidget_band_NSA]
        listWidget_case_list = [self.listWidget_case, self.listWidget_case_NSA]
        current_index = self.tabWidget.currentIndex()
        for i in range(tableWidget_band_list[current_index].rowCount()):
            if tableWidget_band_list[current_index].item(i, 0).checkState():
                band_list.append(tableWidget_band_list[current_index].item(i, 0).text())
                SCS_list.append(tableWidget_band_list[current_index].item(i, 1).text())

        for j in range(listWidget_case_list[current_index].count()):
            if listWidget_case_list[current_index].item(j).checkState():
                testcase_list.append(listWidget_case_list[current_index].item(j).text())

        if len(band_list) == 0:
            status = False
            QMessageBox.warning(self, 'Tip', 'Please select at least one band!', QMessageBox.Yes)

        for index in range(len(SCS_list)):
            scs_list = SCS_list[index].split(',')
            for scs_item in scs_list:
                if scs_item not in ['15', '30', '60']:
                    status = False
                    QMessageBox.warning(self, 'Tip', 'The SCS format of ' + band_list[index] + ' is incorrect!', QMessageBox.Yes)

        if len(testcase_list) == 0:
            status = False
            QMessageBox.warning(self, 'Tip', 'Please select at least one test case!', QMessageBox.Yes)

        temperatrue = self.comboBox_temp.currentText()
        voltage = self.comboBox_volt.currentText()
        condition_list = [temperatrue, voltage]

        if status:
            # 更新待测试序列字典
            testseq_handle.new_testseq_dict(band_list, SCS_list, testcase_list, condition_list)

            # 向主窗口传递所需要的信息，用于生成主窗口测试序列界面
            self.okSig.emit([band_list, SCS_list, testcase_list])

            self.close()


class CaseParmsWin(QMainWindow, Ui_win_caseparms):
    def __init__(self, parms_list, band, case, parent=None):
        super(CaseParmsWin, self).__init__(parent)
        self.setupUi(self)

        self.parms_list = parms_list
        self.band = band
        self.case = case

        self.init_example()

        # 设置为模拟对话框，阻塞上一层窗口
        self.setWindowModality(Qt.ApplicationModal)

        # 信号槽关系定义
        self.pushButton_cancel.clicked.connect(self.close)
        self.pushButton_ok.clicked.connect(self.ok_clicked)
        # self.pushButton_cancel.setStyleSheet("border-top-left-radius:5px;border-bottom-right-radius:5px;")
        # self.pushButton_ok.setStyleSheet("border-top-left-radius:5px;border-bottom-right-radius:5px;")

    def init_example(self):
        self.label.setText(self.band + ' ' + self.case)
        # self.setStyleSheet("color:white")
        # self.setStyleSheet("background-color:black")

        # 根据parms_list更新参数配置表
        self.tableWidget.clear()     # 清空
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(0)

        if isinstance(self.parms_list, dict):    # 如果是字典类型，转换成只有一个元素的列表类型
            self.parms_list = [self.parms_list]

        self.tableWidget.setColumnCount(len(self.parms_list))
        self.tableWidget.setRowCount(len(self.parms_list[0]['params']))
        parms_namelist = []

        for p in self.parms_list[0]['params']:
            parms_namelist.append(p['name'])
        self.tableWidget.setVerticalHeaderLabels(parms_namelist)
        self.tableWidget.setHorizontalHeaderLabels('step' + str(x + 1) for x in range(len(self.parms_list)))

        for col_index in range(len(self.parms_list)):
            for row_index in range(len(self.parms_list[col_index]['params'])):
                if row_index == 0:
                    item = QTableWidgetItem()
                    if self.parms_list[col_index]['params'][0]['value'] == 'True':
                        item.setCheckState(Qt.Checked)
                    else:
                        item.setCheckState(not Qt.Checked)
                    self.tableWidget.setItem(row_index, col_index, item)
                else:
                    item = QTableWidgetItem()
                    item.setText(self.parms_list[col_index]['params'][row_index]['value'])
                    self.tableWidget.setItem(row_index, col_index, item)

    def ok_clicked(self):
        # 将界面表格中每行每列的参数更新到待测试字典
        col_count = self.tableWidget.columnCount()
        row_count = self.tableWidget.rowCount()

        for col_index in range(col_count):
            for row_index in range(row_count):
                try:
                    current_item_text = self.tableWidget.item(row_index, col_index).text()
                except:
                    pass
                try:
                    current_item_text = self.tableWidget.cellWidget(row_index, col_index).currentText()
                except:
                    pass

                # 如果是字典，转换成列表
                # print(isinstance(global_elements.testseq_dict['xml']['testseq'], dict))
                if isinstance(global_elements.testseq_dict['xml']['testseq'], dict):
                    global_elements.testseq_dict['xml']['testseq'] = [global_elements.testseq_dict['xml']['testseq']]

                if isinstance(global_elements.testseq_dict['xml']['testseq'][global_elements.clicked_colindex]['testplan'], dict):
                    global_elements.testseq_dict['xml']['testseq'][global_elements.clicked_colindex]['testplan'] = [global_elements.testseq_dict['xml']['testseq'][global_elements.clicked_colindex]['testplan']]

                if row_index == 0:
                    if self.tableWidget.item(row_index, col_index).checkState() == Qt.Checked:
                        global_elements.testseq_dict['xml']['testseq'][global_elements.clicked_colindex]['testplan'][
                            global_elements.clicked_rowindex]['step'][col_index]['params'][row_index]['value'] = 'True'
                    else:
                        global_elements.testseq_dict['xml']['testseq'][global_elements.clicked_colindex]['testplan'][
                            global_elements.clicked_rowindex]['step'][col_index]['params'][row_index]['value'] = 'False'
                else:
                    global_elements.testseq_dict['xml']['testseq'][global_elements.clicked_colindex]['testplan'][global_elements.clicked_rowindex]['step'][col_index]['params'][row_index]['value'] = current_item_text

        self.close()


class DeviceWin(QMainWindow, Ui_MainWindow_device):
    def __init__(self, parent=None):
        super(DeviceWin, self).__init__(parent)
        self.setupUi(self)

        self.intance_init()

        # 设置为模拟对话框，阻塞上一层窗口
        self.setWindowModality(Qt.ApplicationModal)

        # 信号槽关系
        self.pushButton_ok.clicked.connect(self.okclicked)
        self.pushButton_cancel.clicked.connect(self.close)

    def intance_init(self):
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 自适应水平宽度
        # self.tableWidget.horizontalHeader().setStyleSheet('QHeaderView::section{background:rgb(170, 170, 225);}')

        self.item1 = QComboBox()
        self.item1.addItems(['CMX500'])
        self.tableWidget.setCellWidget(0, 0, self.item1)
        self.item2 = QComboBox()
        self.item2.addItems(['GPIB', 'TCPIP'])
        self.tableWidget.setCellWidget(0, 1, self.item2)

        self.item3 = QComboBox()
        self.item3.addItems(['E3632A'])
        self.tableWidget.setCellWidget(1, 0, self.item3)
        self.item4 = QComboBox()
        self.item4.addItems(['GPIB', 'TCPIP'])
        self.tableWidget.setCellWidget(1, 1, self.item4)

        self.item1.setCurrentText(global_elements.DevicesConfig_dict['xml']['CU']['DeviceName'])
        self.item2.setCurrentText(global_elements.DevicesConfig_dict['xml']['CU']['ConnectionType'])
        item1 = QTableWidgetItem()
        item1.setText(global_elements.DevicesConfig_dict['xml']['CU']['Address'])
        self.tableWidget.setItem(0, 2, item1)

        self.item3.setCurrentText(global_elements.DevicesConfig_dict['xml']['PS']['DeviceName'])
        self.item4.setCurrentText(global_elements.DevicesConfig_dict['xml']['PS']['ConnectionType'])
        item2 = QTableWidgetItem()
        item2.setText(global_elements.DevicesConfig_dict['xml']['PS']['Address'])
        self.tableWidget.setItem(1, 2, item2)

    def okclicked(self):
        global_elements.DevicesConfig_dict['xml']['CU']['DeviceName'] = self.item1.currentText()
        global_elements.DevicesConfig_dict['xml']['CU']['ConnectionType'] = self.item2.currentText()
        global_elements.DevicesConfig_dict['xml']['CU']['Address'] = self.tableWidget.item(0, 2).text()
        global_elements.DevicesConfig_dict['xml']['PS']['DeviceName'] = self.item3.currentText()
        global_elements.DevicesConfig_dict['xml']['PS']['ConnectionType'] = self.item4.currentText()
        global_elements.DevicesConfig_dict['xml']['PS']['Address'] = self.tableWidget.item(1, 2).text()


        global_elements.dict_to_xmlstr(global_elements.DevicesConfig_dict, './config/DevicesConfig/DevicesConfig.xml')
        self.close()


class DUTWin(QMainWindow, Ui_DUT_Win):
    oksig = pyqtSignal(str)
    def __init__(self, parent=None):
        super(DUTWin, self).__init__(parent)
        self.setupUi(self)

        self.intance_init()

        # 设置为模拟对话框，阻塞上一层窗口
        self.setWindowModality(Qt.ApplicationModal)

        self.tableWidget.setContextMenuPolicy(Qt.CustomContextMenu)  ######允许右键产生子菜单
        self.tableWidget.customContextMenuRequested.connect(self.generateMenu)  ####右键菜单

        # 信号槽关系
        self.tableWidget.itemClicked.connect(self.itemclicked)
        self.pushButton_savechanged.clicked.connect(self.saveChangedClicked)
        self.pushButton_cancel.clicked.connect(self.close)
        self.pushButton_ok.clicked.connect(self.okclicked)

    def intance_init(self):
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 自适应水平宽度
        self.tableWidget.verticalHeader().setVisible(False)
        # 加载现有的DUT到列表中
        self.tableWidget.setRowCount(len(global_elements.dutNameList))

        for dut_index in range(len(global_elements.dutNameList)):
            item_dutname = QTableWidgetItem()
            item_dutname.setText(global_elements.dutNameList[dut_index])
            item_dutname.setFlags(item_dutname.flags() & (~Qt.ItemIsEditable))      # 设备Item不可编辑但可以选中
            self.tableWidget.setItem(dut_index, 1, item_dutname)

            item_checked = QLabel()
            if global_elements.dutAcitveStateDict[global_elements.dutNameList[dut_index]]:
                item_checked.setPixmap(QPixmap('./image/right_arrow_24px.ico'))
                item_checked.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            else:
                item_checked.setText('')
                # item.setFlags(item.flags() & (~Qt.ItemIsEditable))  # 设备Item不可编辑但可以选中
            self.tableWidget.setCellWidget(dut_index, 0, item_checked)

        self.btngrp = QButtonGroup()
        self.btngrp.addButton(self.radioButton_manual)
        self.btngrp.addButton(self.radioButton_powerc)
        self.btngrp.addButton(self.radioButton_AT)

    def okclicked(self):
        isDUTacitve = False
        for k, v in global_elements.dutAcitveStateDict.items():
            if v:
                isDUTacitve = True
                activedutname = k
                break
        if isDUTacitve:
            self.oksig.emit(activedutname)
            self.close()
        else:
            QMessageBox.warning(self, 'Warning', 'Please activate a DUT!', QMessageBox.Yes)

    def itemclicked(self, index):
        # 当表格中第二列的item被点击时，更新右边界面的参数内容
        if index.column() == 1 and index.row() >= 0:
            self.tableWidget.setCurrentCell(index.row(), index.column())
            currentDUT = self.tableWidget.currentItem().text()
            currentDUTDict = global_elements.xml_to_dict(global_elements.DUTCONFIGXMLPATH + currentDUT + '.xml')

            self.lineEdit_brand.setText(currentDUTDict['xml']['DUTCONFIG']['Brand'])
            self.lineEdit_HW.setText(currentDUTDict['xml']['DUTCONFIG']['HWVersion'])
            self.lineEdit_SW.setText(currentDUTDict['xml']['DUTCONFIG']['SWVersion'])
            self.lineEdit_SN.setText(currentDUTDict['xml']['DUTCONFIG']['SN'])
            self.lineEdit_IMEI.setText(currentDUTDict['xml']['DUTCONFIG']['IMEI'])
            self.lineEdit_2.setText(currentDUTDict['xml']['DUTCONFIG']['MAXREGTIME'])
            if currentDUTDict['xml']['DUTCONFIG']['AUTOMODE'] == '1':
                self.radioButton_manual.setChecked(True)
            elif currentDUTDict['xml']['DUTCONFIG']['AUTOMODE'] == '2':
                self.radioButton_powerc.setChecked(True)
            elif currentDUTDict['xml']['DUTCONFIG']['AUTOMODE'] == '3':
                self.radioButton_AT.setChecked(True)
            else:
                pass
            self.lineEdit_comport.setText(currentDUTDict['xml']['DUTCONFIG']['COMPORT'])
            self.lineEdit_HV.setText(currentDUTDict['xml']['DUTCONFIG']['HV'])
            self.lineEdit_NV.setText(currentDUTDict['xml']['DUTCONFIG']['NV'])
            self.lineEdit_LV.setText(currentDUTDict['xml']['DUTCONFIG']['LV'])
            self.lineEdit_maxCurrent.setText(currentDUTDict['xml']['DUTCONFIG']['MAXC'])
            self.lineEdit_HT.setText(currentDUTDict['xml']['DUTCONFIG']['HT'])
            self.lineEdit_NT.setText(currentDUTDict['xml']['DUTCONFIG']['NT'])
            self.lineEdit_LT.setText(currentDUTDict['xml']['DUTCONFIG']['LT'])
            if currentDUTDict['xml']['DUTCONFIG']['halfpi'] == '1':
                self.checkBox_halfpi.setChecked(True)
            else:
                self.checkBox_halfpi.setChecked(False)
            self.comboBox_PowerClass.setCurrentText(currentDUTDict['xml']['DUTCONFIG']['powerclass'])

        # # 当表格中的第一列item被点击时，激活DUT
        # if index.column() == 0 and index.row() >= 0:
        #     self.active_dut(index.row())

    def generateMenu(self, pos):
        """
        右键之后生成右键菜单，并作后续处理
        :param pos: 右键的位置
        :return:
        """
        # 获取右键的行号，如果没有在行上，返回-1
        row_num = -1
        for i in self.tableWidget.selectionModel().selection().indexes():
            row_num = i.row()

        # 如果没有行号，则只生成新建DUT菜单
        if row_num == -1:
            menu = QMenu()
            item1 = menu.addAction(u"New DUT")
            action1 = menu.exec_(self.tableWidget.mapToGlobal(pos))
            if action1 == item1:
                self.creatNewDUTWin()

        # 如果有行号，则对相应的DUT生成处理菜单
        if row_num >= 0:
            menu = QMenu()
            activeDUT = menu.addAction(u"Active DUT")
            saveAsDUT = menu.addAction(u"Save as DUT")
            deleteDUT = menu.addAction(u"Delete DUT")
            action2 = menu.exec_(self.tableWidget.mapToGlobal(pos))
            if action2 == activeDUT:
                self.active_dut(row_num)
            elif action2 == saveAsDUT:
                self.save_as_DUTwin(row_num)
            elif action2 == deleteDUT:
                self.delete_DUT(row_num)

    def creatNewDUTWin(self):
        """
        创建新DUT的窗口
        :return:
        """
        self.new_dut_win = newDUTWin()
        self.new_dut_win.oksig.connect(self.createNewDUT)
        self.new_dut_win.show()

    def createNewDUT(self, content):
        """
        :param content:  新建 DUT 窗口传回的New DUT Name
        :return:
        """
        if content != 'None':  # 确认返回了可用的DUT NAME
            # 判断DUT是否已经存在
            if content in global_elements.dutNameList:  # 如果存在
                QMessageBox.warning(self, 'Warning', 'DUT already exists!', QMessageBox.Yes)
            else:
                global_elements.dutNameList.append(content)    # 符合条件的DUT Name加入DUT名称列表
                # 符合条件的DUT Name加入界面列表
                current_row_count = self.tableWidget.rowCount()
                self.tableWidget.setRowCount(current_row_count + 1)    # DUT表格增加一行
                item = QTableWidgetItem()
                item.setText(str(content))
                item.setFlags(item.flags() & (~Qt.ItemIsEditable))  # 设备Item不可编辑但可以选中
                self.tableWidget.setItem(current_row_count, 1, item)
                # 将新建 DUT加入激活状态字典
                global_elements.dutAcitveStateDict[content] = False
                # 创建NEW DUT的xml文件
                copy(global_elements.DEFUALTCONFIGXMLPATH + 'NewDUTConfig.xml', global_elements.DUTCONFIGXMLPATH
                            + content + '.xml')


    def active_dut(self, row_index):
        """
        激活选中的DUT,并更新激活DUT的字典
        :param row_index:  当前的行
        :return:
        """
        if row_index >= 0:
            currentDUT = self.tableWidget.item(row_index, 1).text()
            # 更新DUT激活状态的字典
            for k, v in global_elements.dutAcitveStateDict.items():
                if k == currentDUT:
                    global_elements.dutAcitveStateDict[k] = True
                else:
                    global_elements.dutAcitveStateDict[k] = False

            # 更新激活的DUT字典
            global_elements.dutActiveDict = global_elements.xml_to_dict(global_elements.DUTCONFIGXMLPATH + currentDUT + '.xml')

            # 更新界面，将激活的DUT前面作标记
            rowCount = self.tableWidget.rowCount()
            for row in range(rowCount):
                lableItem = QLabel()  # 为了方便图标居中，生成一个lable对象用来装图标
                if self.tableWidget.item(row, 1).text() ==  currentDUT:
                    lableItem.setPixmap(QPixmap("./image/right_arrow_24px.ico"))
                    lableItem.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                else:
                    lableItem.setText('')
                self.tableWidget.setCellWidget(row, 0, lableItem)

    def save_as_DUTwin(self, row_index):
        """
        另存为DUT，更新DUT NAME列表，更新界面，更新xml文件，更新DUT激活状态字典
        :param row_index:
        :return:
        """
        self.newDUTWin = newDUTWin()
        self.newDUTWin.oksig.connect(self.saveAsDUT)
        self.newDUTWin.show()

    def saveAsDUT(self, content):
        """
        另存为DUT，更新DUT NAME列表，更新界面，更新xml文件，更新DUT激活状态字典
        :param content:
        :return:
        """
        currentRow = self.tableWidget.currentRow()
        currentDUT = self.tableWidget.item(currentRow, 1).text()
        if content != 'None':  # 确认返回了可用的DUT NAME
            # 判断DUT是否已经存在
            if content in global_elements.dutNameList:  # 如果存在
                QMessageBox.warning(self, 'Warning', 'DUT already exists!', QMessageBox.Yes)
            else:
                global_elements.dutNameList.append(content)    # 符合条件的DUT Name加入DUT名称列表
                # 符合条件的DUT Name加入界面列表
                current_row_count = self.tableWidget.rowCount()
                self.tableWidget.setRowCount(current_row_count + 1)    # DUT表格增加一行
                item = QTableWidgetItem()
                item.setText(str(content))
                item.setFlags(item.flags() & (~Qt.ItemIsEditable))  # 设备Item不可编辑但可以选中
                self.tableWidget.setItem(current_row_count, 1, item)
                # 将新建 DUT加入激活状态字典
                global_elements.dutAcitveStateDict[content] = False
                # 复制 DUT的xml文件
                copy(global_elements.DUTCONFIGXMLPATH + currentDUT + '.xml', global_elements.DUTCONFIGXMLPATH
                            + content + '.xml')

    def delete_DUT(self, row_index):
        """
        删除当前DUT,更新DUT列表，更新界面，更新DUT激活状态字典，更新xml文件。如果当前DUT是激活状态，更新激活DUT字典
        :param row_index:
        :return:
        """
        currentRow = self.tableWidget.currentRow()
        currentDUT = self.tableWidget.item(currentRow, 1).text()
        global_elements.dutNameList.remove(currentDUT)            # 更新DUT列表
        self.tableWidget.removeRow(currentRow)                    # 更新界面
        if global_elements.dutAcitveStateDict[currentDUT]:        # 如果当前DUT是激活状态，更新激活DUT字典
            global_elements.dutActiveDict = {}
        global_elements.dutAcitveStateDict.pop(currentDUT)        # 更新DUT激活状态字典
        # 删除DUT对应的xml文件
        if os.path.exists(global_elements.DUTCONFIGXMLPATH + currentDUT + '.xml'):
            os.remove(global_elements.DUTCONFIGXMLPATH + currentDUT + '.xml')


    def saveChangedClicked(self):
        """
        保存当前DUT的配置到xml文件，如果当前DUT是已激活的DUT,还需要更新，激活DUT的字典
        :return:
        """
        if len(self.tableWidget.selectedItems()) > 0:     # 判断当前是否有选中DUT,如果有选中，执行下面内容
            currentRow = self.tableWidget.currentRow()
            currentDUT = self.tableWidget.item(currentRow, 1).text()     # 获取当前DUT NAME
            currentDUTDict = {'xml': {'DUTCONFIG': {}}}  # 定义一个字典用于临时存放界面参数，便于转换为XML文件
            currentDUTDict['xml']['DUTCONFIG']['Brand'] = self.lineEdit_brand.text()
            currentDUTDict['xml']['DUTCONFIG']['HWVersion'] = self.lineEdit_HW.text()
            currentDUTDict['xml']['DUTCONFIG']['SWVersion'] = self.lineEdit_SW.text()
            currentDUTDict['xml']['DUTCONFIG']['SN'] = self.lineEdit_SN.text()
            currentDUTDict['xml']['DUTCONFIG']['IMEI'] = self.lineEdit_IMEI.text()
            currentDUTDict['xml']['DUTCONFIG']['MAXREGTIME'] = self.lineEdit_2.text()
            if self.radioButton_manual.isChecked():
                currentDUTDict['xml']['DUTCONFIG']['AUTOMODE'] = '1'
            elif self.radioButton_powerc.isChecked():
                currentDUTDict['xml']['DUTCONFIG']['AUTOMODE'] = '2'
            elif self.radioButton_AT.isChecked():
                currentDUTDict['xml']['DUTCONFIG']['AUTOMODE'] = '3'
            else:
                currentDUTDict['xml']['DUTCONFIG']['AUTOMODE'] = '1'
            currentDUTDict['xml']['DUTCONFIG']['COMPORT'] = self.lineEdit_comport.text()
            currentDUTDict['xml']['DUTCONFIG']['HV'] = self.lineEdit_HV.text()
            currentDUTDict['xml']['DUTCONFIG']['NV'] = self.lineEdit_NV.text()
            currentDUTDict['xml']['DUTCONFIG']['LV'] = self.lineEdit_LV.text()
            currentDUTDict['xml']['DUTCONFIG']['MAXC'] = self.lineEdit_maxCurrent.text()
            currentDUTDict['xml']['DUTCONFIG']['HT'] = self.lineEdit_HT.text()
            currentDUTDict['xml']['DUTCONFIG']['NT'] = self.lineEdit_NT.text()
            currentDUTDict['xml']['DUTCONFIG']['LT'] = self.lineEdit_LT.text()
            if self.checkBox_halfpi.checkState():
                currentDUTDict['xml']['DUTCONFIG']['halfpi'] = '1'
            else:
                currentDUTDict['xml']['DUTCONFIG']['halfpi'] = '0'
            currentDUTDict['xml']['DUTCONFIG']['powerclass'] = self.comboBox_PowerClass.currentText()

            global_elements.dict_to_xml(currentDUTDict['xml'], global_elements.DUTCONFIGXMLPATH +
                                       currentDUT + '.xml')

            if global_elements.dutAcitveStateDict[currentDUT]:        # 如果当前DUT是激活状态，将内容更新到激活DUT的字典
                global_elements.dutActiveDict = currentDUTDict

        else:
            QMessageBox.warning(self, 'Warning', 'Please select a DUT to save the configuration first!', QMessageBox.Yes)


class newDUTWin(QMainWindow, Ui_NewDUT):
    oksig = pyqtSignal(str)
    def __init__(self, parent=None):
        super(newDUTWin, self).__init__(parent)
        self.setupUi(self)

        # 设置为模拟对话框，阻塞上一层窗口
        self.setWindowModality(Qt.ApplicationModal)

        # 信号槽关系
        self.pushButton_cancel.clicked.connect(self.close)
        self.pushButton_ok.clicked.connect(self.okclicked)

    def okclicked(self):
        """
        点击OK按钮后的槽函数
        :return: 发送New DUT的名称到父窗口，并关闭新建DUT窗口
        """
        if self.lineEdit_dutname.text() == '':
            QMessageBox.warning(self, 'Tip', 'Please enter a NEW DUT name!', QMessageBox.Yes)
        else:
            sendcontent = self.lineEdit_dutname.text()
            self.oksig.emit(sendcontent)
            self.close()


class PathLossWin(QMainWindow, Ui_Loss_win):
    oksig = pyqtSignal(list)
    def __init__(self, parent=None):
        super(PathLossWin, self).__init__(parent)
        self.setupUi(self)
        self.intance_init()

        self.cwd = './rfc/'

        # 设置为模拟对话框，阻塞上一层窗口
        self.setWindowModality(Qt.ApplicationModal)

        # 定义信号槽
        self.pushButton_cancel.clicked.connect(self.close)
        self.pushButton_rf1.clicked.connect(self.rf1scanclicked)
        self.pushButton_rf2.clicked.connect(self.rf2scanclicked)
        self.pushButton_rf3.clicked.connect(self.rf3scanclicked)
        self.pushButton_rf4.clicked.connect(self.rf4scanclicked)
        self.pushButton_ok.clicked.connect(self.okclicked)
        self.pushButton_lossfile.clicked.connect(self.lossFileEdit)

    # 按Loss字典内容更新内容
    def intance_init(self):
        self.lineEdit_rf1.setText(global_elements.pathLossDict['RF1'])
        self.lineEdit_rf2.setText(global_elements.pathLossDict['RF2'])
        self.lineEdit_rf3.setText(global_elements.pathLossDict['RF3'])
        self.lineEdit_rf4.setText(global_elements.pathLossDict['RF4'])

    # 浏览线损文件
    def rf1scanclicked(self):
        fileName_choose, filetype = QFileDialog.getOpenFileName(self,
                                                                'Select path loss file!',
                                                                self.cwd,
                                                                'Loss Files (*.loss);;All Files (*)')
        if fileName_choose != '':
            self.lineEdit_rf1.setText(fileName_choose)

    def rf2scanclicked(self):
        fileName_choose, filetype = QFileDialog.getOpenFileName(self,
                                                                'Select path loss file!',
                                                                self.cwd,
                                                                'Loss Files (*.loss);;All Files (*)')
        if fileName_choose != '':
            self.lineEdit_rf2.setText(fileName_choose)

    def rf3scanclicked(self):
        fileName_choose, filetype = QFileDialog.getOpenFileName(self,
                                                                'Select path loss file!',
                                                                self.cwd,
                                                                'Loss Files (*.loss);;All Files (*)')
        if fileName_choose != '':
            self.lineEdit_rf3.setText(fileName_choose)

    def rf4scanclicked(self):
        fileName_choose, filetype = QFileDialog.getOpenFileName(self,
                                                                'Select path loss file!',
                                                                self.cwd,
                                                                'Loss Files (*.loss);;All Files (*)')
        if fileName_choose != '':
            self.lineEdit_rf4.setText(fileName_choose)

    # ok按钮点击槽函数
    def okclicked(self):
        rf1_loss = self.lineEdit_rf1.text()
        rf2_loss = self.lineEdit_rf2.text()
        rf3_loss = self.lineEdit_rf3.text()
        rf4_loss = self.lineEdit_rf4.text()
        global_elements.pathLossDict['RF1'] = rf1_loss
        global_elements.pathLossDict['RF2'] = rf2_loss
        global_elements.pathLossDict['RF3'] = rf3_loss
        global_elements.pathLossDict['RF4'] = rf4_loss
        self.oksig.emit([rf1_loss, rf2_loss, rf3_loss, rf4_loss])
        self.close()

    # 编辑Loss file窗口
    def lossFileEdit(self):
        self.editLossWin = LossEditWin()
        self.editLossWin.show()


class LossEditWin(QMainWindow, Ui_Edit_loss_file_Window):
    """
        编辑线损文件窗口
    """
    def __init__(self, parent=None):
        super(LossEditWin, self).__init__(parent)
        self.setupUi(self)

        self.cwd = './rfc/'
        self.initexample()

        # 设置为模拟对话框，阻塞上一层窗口
        self.setWindowModality(Qt.ApplicationModal)

        # 信号槽关系
        self.pushButton_cancel.clicked.connect(self.close)
        self.pushButton_addline.clicked.connect(self.addline)
        self.pushButton_removeline.clicked.connect(self.removeline)
        self.pushButton_creat.clicked.connect(self.creatlossfile)
        self.pushButton_loadfile.clicked.connect(self.loadfile)

    def initexample(self):
        self.tableWidget_lossedit.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 自适应水平宽度
        # self.tableWidget_lossedit.horizontalHeader().setStyleSheet('QHeaderView::section{background:lightblue;}')
        # self.tableWidget_lossedit.verticalHeader().setStyleSheet('QHeaderView::section{background:lightblue;}')

        # add line按钮槽函数

    def addline(self):
        current_row = self.tableWidget_lossedit.rowCount()
        self.tableWidget_lossedit.setRowCount(current_row + 1)

        # remove line按钮槽函数

    def removeline(self):
        current_row = self.tableWidget_lossedit.rowCount()
        self.tableWidget_lossedit.setRowCount(current_row - 1)

        # creat loss file按钮槽函数

    def creatlossfile(self):
        loss_list = []
        loss_dict = {}
        loss_dict_final = {}
        loss_dict_final['Loss'] = {}
        current_row = self.tableWidget_lossedit.rowCount()
        if current_row > 0:
            for i in range(current_row):
                Freq = self.tableWidget_lossedit.item(i, 0).text()
                loss = self.tableWidget_lossedit.item(i, 1).text()
                loss_dict['Frequency'] = Freq
                loss_dict['Value'] = loss
                loss_list.append(loss_dict)
                loss_dict = {1: 2, 2: 3}  # 此两行代码是让loss_dict与loss_dict失去关联，以便list中已append的元素随便dict变化
                loss_dict.clear()
            loss_dict_final['Loss']['loss'] = loss_list

            fileName_choose, filetype = QFileDialog.getSaveFileName(self,
                                                                    'Save Path Loss Files',
                                                                    self.cwd,
                                                                    'Loss Files (*.loss);;All Files (*)')

            if fileName_choose != '':
                global_elements.dict_to_xmlstr(loss_dict_final, fileName_choose)

        else:
            # win32api.MessageBox(0, 'There is no data to save Loss File!')
            QMessageBox.warning(self, 'Tip', 'There is no data to save Loss File!', QMessageBox.Yes)

        # 定义load file按钮槽函数

    def loadfile(self):
        self.tableWidget_lossedit.setRowCount(0)
        fileName_choose, filetype = QFileDialog.getOpenFileName(self,
                                                                'Selecting Path Loss Files',
                                                                self.cwd,
                                                                'Loss Files (*.loss);;All Files (*)')
        if fileName_choose != '':
            dict_loss = global_elements.xml_to_dict(fileName_choose)
            self.tableWidget_lossedit.setRowCount(len(dict_loss['Loss']['loss']))
            for i in range(len(dict_loss['Loss']['loss'])):
                item = QTableWidgetItem()
                # print(dict_loss['Loss']['loss'][i]['Frequency'])
                item.setText(dict_loss['Loss']['loss'][i]['Frequency'])
                self.tableWidget_lossedit.setItem(i, 0, item)

                item2 = QTableWidgetItem()
                item2.setText(dict_loss['Loss']['loss'][i]['Value'])
                self.tableWidget_lossedit.setItem(i, 1, item2)


class channelWin(QMainWindow, Ui_win_Channel):
    """
    NR Channel窗口
    """
    def __init__(self, parent=None):
        super(channelWin, self).__init__(parent)
        self.setupUi(self)

        self.intance_init()

        self.pushButton_ok.clicked.connect(self.close)
        self.pushButton_cancel.clicked.connect(self.close)

    def intance_init(self):
        self.treeWidget.header().setSectionResizeMode(QHeaderView.ResizeToContents)  # 自适应水平宽度
        self.treeWidget.setColumnCount(12)
        # 设置树形控件头部的标题
        self.treeWidget.setHeaderLabels(['Key', 'Carrier Centre Fre', 'Carrier Centre Ch', 'PointA Fre', 'PointA Ch',
                                         'offset To Carrier', 'GSCN', 'SSB Ch', 'KSSB', 'offset Carrier CORE',
                                         'CORE SET Index', 'offset To PointA'])
        list_col = ['CarrierCentreFre', 'CarrierCentreCh', 'PointAFre', 'PointACh',
                                         'offsetToCarrier', 'GSCN', 'SSBCh', 'KSSB', 'offsetCarrierCORE', 'CORESETIndex', 'offsetToPointA']

        root = QTreeWidgetItem(self.treeWidget)
        root.setText(0, 'Band')

        for k_band, v_band in global_elements.ChannelConfig_dict['xml'].items():
            child_band = QTreeWidgetItem()
            child_band.setText(0, str(k_band))
            child_band.setForeground(0, Qt.green)
            root.addChild(child_band)

            for k_scs, v_scs in v_band.items():
                child_scs = QTreeWidgetItem()
                child_scs.setText(0, str(k_scs))
                child_scs.setForeground(0, Qt.yellow)
                child_band.addChild(child_scs)

                for k_bw, v_bw in v_scs.items():
                    child_bw = QTreeWidgetItem()
                    child_bw.setText(0, str(k_bw))
                    child_bw.setForeground(0, Qt.blue)
                    child_scs.addChild(child_bw)

                    for k_link, v_link in v_bw.items():
                        child_link = QTreeWidgetItem()
                        child_link.setText(0, str(k_link))
                        child_link.setForeground(0, Qt.gray)
                        child_bw.addChild(child_link)

                        for k_ch, v_ch in v_link.items():
                            child_ch = QTreeWidgetItem()
                            child_ch.setText(0, str(k_ch))
                            child_ch.setForeground(0, Qt.red)
                            for i in range(len(list_col)):
                                child_ch.setText(i+1, str(v_ch[list_col[i]]))
                            child_link.addChild(child_ch)


class SplashPanel(QSplashScreen):
    def __init__(self):
        super(SplashPanel, self).__init__()
        self.movie = QMovie(":/actionicons/loading.gif")
        self.gif_label = QLabel(" ",self)
        self.gif_label.setMovie(self.movie)
        self.movie.start()
        self.setPixmap(self.movie.currentPixmap())

    #     self.timer = QTimer(self)
    #     self.timer.timeout.connect(self.slot_update)
    #     self.timer.start()
    #
    # def slot_update(self):
    #     self.setPixmap(self.movie.currentPixmap())
    #     self.repaint()



    def mousePressEvent(self, evt):
        pass
        # 重写鼠标点击事件，阻止点击后消失
    def mouseDoubleClickEvent(self, *args, **kwargs):
        pass
        # 重写鼠标移动事件，阻止出现卡顿现象
    def enterEvent(self, *args, **kwargs):
        pass
        # 重写鼠标移动事件，阻止出现卡顿现象
    def mouseMoveEvent(self, *args, **kwargs):
        pass
        # 重写鼠标移动事件，阻止出现卡顿现象


class test_Thread(QThread):
    """
        线程类，界面窗口处理耗时任务时另开一个线程，防止耗时任务卡死界面(测试进程)
    """
    handle = -1

    def __init__(self):
        super(test_Thread, self).__init__()

    def run(self):
        try:
            self.handle = ctypes.windll.kernel32.OpenThread(PROCESS_ALL_ACCESS, False,
                                                            int(QThread.currentThreadId()))
        except:
            pass

        Start_project.test_start()
















