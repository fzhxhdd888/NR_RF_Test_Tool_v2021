#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2020/11/10 13:53
# @Author  : Feng Zhaohui
# @Site    : 
# @File    : Start_project.py
# @Software: PyCharm

import time
from PyQt5.QtWidgets import QApplication
import sys
import gui.init_ui
import qdarkstyle
import global_elements
from Equipments import Equipments
import testscript_handle


def test_start():
    global_elements.isStatusError = False
    global_elements.finished_result_list = [0, 0, 0]
    global_elements.finished_step = 0
    global_elements.emitsingle.process_rateupdataSingle.emit('0')
    global_elements.checkreportpath()  # 检查报告路径
    global_elements.checkdutactive()  # 检查是否有激活的DUT
    global_elements.checktestseq()  # 检查测试序列中是否有内容

    # 保存配置
    global_elements.save_to_last_config()

    # # 计算测试步骤，用于更新进度条
    global_elements.total_step = global_elements.calc_total_step()
    #
    Equipments.init_devices_checked()  # 初始化已勾选的设备（根据地址实例化，以便测试时调用）

    testscript_handle.testseqhandle()  # 处理测试序列

def main():
    app = QApplication(sys.argv)

    # 定义QSplashScreen 插入启动页背景图
    splash = gui.init_ui.SplashPanel()
    splash.show()
    i = 0
    while i <= 3:
        time.sleep(0.01)
        i += 0.01
        app.processEvents()

    my_mainwin = gui.init_ui.MainWin()
    app.processEvents()
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    app.processEvents()
    my_mainwin.show()
    app.processEvents()

    # # 结束启动页
    splash.finish(my_mainwin)
    splash.deleteLater()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
    # r = global_elements.xml_to_dict('./config/ParmsConfig/MCSindex.xml')
    # pass

