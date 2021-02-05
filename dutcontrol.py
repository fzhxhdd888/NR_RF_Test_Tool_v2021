#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2020/11/24 10:16
# @Author  : Feng Zhaohui
# @Site    : 
# @File    : dutcontrol.py
# @Software: PyCharm

import global_elements
import win32api
import time
import serial.tools.list_ports



# 查找端口
def findPort():
    ports = serial.tools.list_ports.comports()
    for each in ports:
        return str(each)


# 发送AT OFF指令
def sendAT_off(port):
    global_elements.emitsingle.stateupdataSingle.emit('Send AT command: AT+CFUN=0')
    time_now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    global_elements.emitsingle.updataScpiUI.emit(time_now + '   DUT: -> AT+CFUN=0')
    try:
        comport = 'COM' + port
        ser = serial.Serial(port=comport, baudrate=9600, timeout=3)
        ser.write(b'AT+CFUN=0\r\n')
        ser.close()
    except Exception as e:
        global_elements.emitsingle.stateupdataSingle.emit('Error:    Error sending AT command!  Error: ' + e.__doc__)


# 发送AT ON指令
def sendAT_on(port):
    global_elements.emitsingle.stateupdataSingle.emit('Send AT command: AT+CFUN=1')
    time_now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    global_elements.emitsingle.updataScpiUI.emit(time_now + '   DUT: -> AT+CFUN=1')
    try:
        comport = 'COM' + port
        ser = serial.Serial(port=comport, baudrate=9600, timeout=3)
        ser.write(b'AT+CFUN=1\r\n')
        ser.close()
    except Exception as e:
        global_elements.emitsingle.stateupdataSingle.emit('Error:    Error sending AT command! Error: ' + e.__doc__)


def duton():
    """
    打开待测样机方法定义
    :return:
    """
    dut_control_type = global_elements.dutActiveDict['xml']['DUTCONFIG']['AUTOMODE']
    if dut_control_type == '1':
       win32api.MessageBox(0, 'Please manually power on DUT to be tested!', 'Tip')
    elif dut_control_type == '2':
        global_elements.PS_intance.Outputon()
    elif dut_control_type == '3':
        port = global_elements.dutActiveDict['xml']['DUTCONFIG']['COMPORT']
        sendAT_on(port)
    else:
        global_elements.emitsingle.thread_exitSingle.emit('Please choose the correct cellular test DUT automatic mode')


def dutoff():
    """
    关闭待测样机方法定义
    :return:
    """
    dut_control_type = global_elements.dutActiveDict['xml']['DUTCONFIG']['AUTOMODE']
    if dut_control_type == '1':
       win32api.MessageBox(0, 'Please power off DUT to be tested manually!', 'Tip')
    elif dut_control_type == '2':
        global_elements.PS_intance.Outputoff()
    elif dut_control_type == '3':
        port = global_elements.dutActiveDict['xml']['DUTCONFIG']['COMPORT']
        sendAT_off(port)
    else:
        global_elements.emitsingle.thread_exitSingle.emit('Please choose the correct cellular test DUT automatic mode')


def dutoffon():
    """
    重启待测样机方法定义
    :return:
    """
    dut_control_type = global_elements.dutActiveDict['xml']['DUTCONFIG']['AUTOMODE']
    if dut_control_type == '1':
       win32api.MessageBox(0, 'Please manually restart DUT to be tested!', 'Tip')
    elif dut_control_type == '2':
        global_elements.PS_intance.Outputoffon(global_elements.dutActiveDict['xml']['DUTCONFIG']['NV'], global_elements.dutActiveDict['xml']['DUTCONFIG']['MAXC'])
    elif dut_control_type == '3':
        port = global_elements.dutActiveDict['xml']['DUTCONFIG']['COMPORT']
        sendAT_off(port)
        time.sleep(2)
        sendAT_on(port)
    else:
        global_elements.emitsingle.thread_exitSingle.emit('Please choose the correct cellular test DUT automatic mode')
