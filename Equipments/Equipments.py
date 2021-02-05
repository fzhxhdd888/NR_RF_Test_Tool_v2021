# !/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Author    : Feng Zhaohui
# @Time      : 2019/2/22
# @File      : Equipments.py
# @Funcyusa  :
# @Version   : 1.0


import pyvisa
import time
import global_elements
from Equipments import CU, PS


def scandevice():
    """
        通过visa扫描仪器
    :return: 仪器idn列表和地址列表
    """
    visaDLL = 'visa32.dll'
    list_address = []
    list_device_idn = []
    rm = pyvisa.ResourceManager(visaDLL)
    device_list = rm.list_resources()
    if len(device_list) > 0:
        for i in device_list:
            try:
                inst = rm.open_resource(i)
                idn = inst.query('*IDN?')
                list_device_idn.append(idn)
                list_address.append(i)
            except:
                pass
    return list_device_idn, list_address


# 初始化已勾选的设备
def init_devices_checked():
    global_elements.emitsingle.stateupdataSingle.emit('Instrument Initialization…………')
    global_elements.emitsingle.stateupdataSingle.emit('Initialization of CU…………')

    CU_device_name = global_elements.DevicesConfig_dict['xml']['CU']['DeviceName']
    CU_device_addr_type = global_elements.DevicesConfig_dict['xml']['CU']['ConnectionType']
    CU_device_addr = global_elements.DevicesConfig_dict['xml']['CU']['Address']

    PS_device_name = global_elements.DevicesConfig_dict['xml']['PS']['DeviceName']
    PS_device_addr_type = global_elements.DevicesConfig_dict['xml']['PS']['ConnectionType']
    PS_device_addr = global_elements.DevicesConfig_dict['xml']['PS']['Address']

    # 初始化CU
    time.sleep(2)
    intance_CU = CU.VisaCU(CU_device_name, CU_device_addr, CU_device_addr_type)
    try:
        intance_CU.open()
        cu_idn = intance_CU.read_idn()
        global_elements.emitsingle.stateupdataSingle.emit('%s Initialization of the CU is successful!' % cu_idn[:-2])
        global_elements.CU_intance = intance_CU                            # 初始化成功后将实例保存到全局变量中，以便调用
    except:
        global_elements.emitsingle.thread_exitSingle.emit('The CU initialization failed!')
        time.sleep(0.1)

    if global_elements.dutActiveDict['xml']['DUTCONFIG']['AUTOMODE'] == '2':    # 如果DUT控制方式是电源控制，测初始化PS
        # 初始化PS
        global_elements.emitsingle.stateupdataSingle.emit('Initialization of DC Power Supply…………')
        time.sleep(2)
        intance_PS = PS.VisaPS(PS_device_name, PS_device_addr, PS_device_addr_type)
        try:
            intance_PS.open()
            ps_idn = intance_PS.read_idn()
            global_elements.emitsingle.stateupdataSingle.emit('%s Initialization of DC power supply is '
                                                             'successful!' % ps_idn[:-2])
            global_elements.PS_intance = intance_PS
        except:
            global_elements.emitsingle.thread_exitSingle.emit('Initialization failure of DC power supply!')
            time.sleep(0.1)

