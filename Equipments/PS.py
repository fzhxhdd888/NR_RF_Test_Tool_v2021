# !/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Author    : Feng Zhaohui
# @Time      : 2019/2/22
# @File      : PS.py
# @Funcyusa  :
# @Version   : 1.0

import pyvisa
import time
import global_elements
from win32api import MessageBox


class VisaPS(object):
    """
        直流电源类构建
        定义直流电源的类函数和参数
    """
    def __init__(self, device_name, visa_address, visa_address_type,  visaDLL=None, *args):
        self.device_address = visa_address
        self.device_name = device_name
        self.device_address_type = visa_address_type
        self.visaDLL = 'visa32.dll' if visaDLL is None else visaDLL
        if self.device_address_type == 'GPIB':
            self.address = "GPIB0::%s::INSTR" % self.device_address
        elif self.device_address_type == 'TCPIP':
            self.address = "TCPIP::%s::inst0::INSTR" % self.device_address

        try:
            self.resourceManager = pyvisa.ResourceManager(self.visaDLL)
        except pyvisa.errors.VisaIOError:
            MessageBox(0,
                       'Please install pyvisa dependent libraries NI-VISA first, download link http://www.ni.com/download/',
                       'Warning!!!')

    def open(self):
        self.instance = self.resourceManager.open_resource(self.address)

    def close(self):
        if self.instance is not None:
            self.instance.close()
            self.instance = None

    def writespic(self, scpistr):
        # 重新定义SCPI写入方法
        scpiResutl = self.instance.write(scpistr +  ',*OPC?')
        time_now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        global_elements.emitsingle.updataScpiUI.emit(time_now + '   '+self.device_name+': -> ' + scpistr +  ',*OPC?')
        global_elements.emitsingle.updataScpiUI.emit(time_now + '   '+self.device_name+': <- ' + scpiResutl + '\n')

    def readspic(self, scpistr):
        # 重新定义SCPI读取方法
        scpiResutl = self.instance.query(scpistr)
        time_now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        global_elements.emitsingle.updataScpiUI.emit(time_now + '   '+self.device_name+': -> ' + scpistr)
        global_elements.emitsingle.updataScpiUI.emit(time_now + '   '+self.device_name+': <- ' + scpiResutl + '\n')
        return scpiResutl

    def read_idn(self):
        idn = self.readspic('*IDN?')
        return idn

    # 设置电压及限流，并重启电源
    def Outputoffon(self, volt, curr):
        if self.device_name == 'E3632A':
            global_elements.emitsingle.stateupdataSingle.emit('Restart DUT……')
            self.writespic('OUTP OFF')
            time.sleep(2)
            self.writespic('VOLT ' + volt)
            self.writespic('CURR ' + curr)
            self.writespic('OUTP ON')

    # 设置电压及限流，并关闭电源
    def Outputoff(self):
        if self.device_name == 'E3632A':
            global_elements.emitsingle.stateupdataSingle.emit('Power off DUT')
            self.writespic('OUTP OFF')
