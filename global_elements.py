#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2020/11/11 14:46
# @Author  : Feng Zhaohui
# @Site    : 
# @File    : global_elements.py
# @Software: PyCharm


from PyQt5.QtCore import pyqtSignal, QObject
import xmltodict
from xml.etree import ElementTree
import os
import time
from Equipments import CU, PS
import re
import math



DUTCONFIGXMLPATH = './config/DUTConfig/'
DEFUALTCONFIGXMLPATH = './config/'
REPORTPATH = ''

isStatusError = False

class EmitSingle(QObject):
    updataScpiUI = pyqtSignal(str)                 # 更新SCPI指令界面信号
    thread_exitSingle = pyqtSignal(str)            # 测试线程退出信号
    stateupdataSingle = pyqtSignal(str)            # 更新测试状态界面信号
    reportupdataSingle = pyqtSignal(list)          # 更新log界面信号
    faileditemsupdataSingle = pyqtSignal(list)     # 更新failed items界面信号
    process_rateupdataSingle = pyqtSignal(str)      # 更新测试进度信号
    summaryupdataSingle = pyqtSignal(list)         # 更新summry
    resultChartclear = pyqtSignal()                # 清空结果图表信号
    maxOutputPowerChartUpdata = pyqtSignal(list)   # 更新最大功率的图表信号  list:[list_result, list_low, list_high, list_id]
    onoffPowerChartUpdata = pyqtSignal(list)       # 更新on off功率的图表信号  list:[list_result, list_low, list_high, list_labels]
    freErrorChartUpdata = pyqtSignal(list)
    inbandemissionChartUpdata = pyqtSignal(list)
    evmflatnessChartUpdata = pyqtSignal(list)
    evmChartUpdata = pyqtSignal(list)
    bwChartUpdata = pyqtSignal(list)
    semChartUpdata = pyqtSignal(list)
    aclrChartUpdata = pyqtSignal(list)
    blerChartUpdata = pyqtSignal(list)
    blerSearchChartUpdata = pyqtSignal(list)
    nsa6_2b_1_3ChartUpdata = pyqtSignal(list)
    totalStepupdata = pyqtSignal(str)

emitsingle = EmitSingle()                          # 实例化发射信号类，以便其它线程调用

dutNameList = []
dutAcitveStateDict = {}
dutActiveDict = {}

pathLossDict = {'RF1': '',
                'RF2': '',
                'RF3': '',
                'RF4': ''}

last_config = {'xml': {'lastconfig': {'lossfilepath1': '',
                                      'lossfilepath2': '',
                                      'lossfilepath3': '',
                                      'lossfilepath4': '',
                          'reportpath': '',
                          'DUT': ''}}}

MCSindex_dict = {}
ChannelConfig_dict = {}
RBConfig_dict = {}
DlRBConfig_dict = {}
UlRBConfig_dict = {}
DLlevel_dict = {}
SCSBandwidthConfig_dict  = {}
DevicesConfig_dict = {}
LTEBW_dict = {}
LTEChannel_dict = {}
LTERBConfig_dict = {}

CU_intance = CU.VisaCU('', '', '')                 # 用于存放实例化仪器
PS_intance = PS.VisaPS('', '', '')

clicked_rowindex = 0
clicked_colindex = 0

# 待测试的测试序列存放字典
testseq_dict = {'xml': {'testseq': []}}

# 存放测试过程中的各个参数
NR_band = ''
test_case_name = ''
NR_bw = ''
NR_bw_num = ''
NR_ch = ''
NR_dl_ch = ''
NR_UL_fre = ''
NR_SCS = ''
NR_testid = ''
NR_Modulation = ''
NR_DL_Modulation = ''
NR_RBAllocation = ''
NR_TestPoint = ''
NR_p_max = ''
NR_DlRBconfig = ''
NR_Pexp_pre = ''
NR_Pexp = ''
NR_condition = ''
NR_DL_level = ''
# NR_MCSindex = ''

# 存放用于出报告的参数
NR_type_r = ''
NR_band_r = ''
test_case_name_r = ''
test_item_r = ''
NR_bw_r = ''
NR_ch_r = ''
NR_dl_ch_r = ''
NR_SCS_r = ''
NR_testid_r = ''
NR_Modulation_r = ''
NR_RBAllocation_r = ''
NR_MCSindex_r = ''
NR_Waveform_r = ''
NR_remark_r = ''
NR_TestPoint_r = ''

NSA_LTE_band = ''
NSA_NR_band = ''
NSA_LTE_DuplexMode = ''
NSA_NR_DuplexMode = ''
NSA_NR_bw = ''
NSA_LTE_bw = ''
NSA_LTE_ULchannel = ''
NSA_LTE_ULFreq = ''
NSA_LTE_DLchannel = ''
NSA_LTE_DLFreq = ''
NSA_NR_channel = ''
NSA_NR_ULFreq = ''
NSA_NR_DLchannel = ''
NSA_NR_DLFreq = ''
NSA_LTE_modulation = ''
NSA_NR_modulation = ''
NSA_LTE_rb = ''
NSA_NR_rb = ''

NSA_NR_bw_r = ''
NSA_LTE_bw_r = ''
NSA_LTE_rb_r = ''
NSA_NR_rb_r = ''


# 用于存放测试ON OFF Power时的目标功率
expPower_onoffpower = {'15': {'5': '-3.6',
                             '10': '0.4',
                             '15': '1.4',
                             '20': '2.7',
                             '25': '3.6',
                             '30': '4.4',
                             '40': '5.7',
                             '50': '6.7'},
                       '30': {'5': '-4.2',
                              '10': '-0.8',
                              '15': '1.2',
                              '20': '2.5',
                              '25': '3.5',
                              '30': '4.3',
                              '40': '5.7',
                              '50': '6.6',
                              '60': '7.5',
                              '80': '8.8',
                              '90': '9.3',
                              '100': '9.8'},
                       '60': {'10': '-1.2',
                              '15': '1.0',
                              '20': '2.2',
                              '25': '3.3',
                              '30': '4.2',
                              '40': '5.5',
                              '50': '6.5',
                              '60': '7.4',
                              '80': '8.7',
                              '90': '9.2',
                              '100': '9.7'}}

finished_result_list = [0, 0, 0]                # 记录已完成的步数中有多少PASS，多少FAIL，多少INCONCLUSIVE
total_step = 0                                  # 记录总步数
finished_step = 0                               # 记录已完成步数

maxOutputPowerResutl = []                       # 存放每一个信道 带宽 SCS的 6个testid 结果，用于生成曲线图
maxOutputPowerTestid = []                       # 存放每一个信道 带宽 SCS的 6个testid index，用于生成曲线图
maxOutputPowerLow = []                          # 存放每一个信道 带宽 SCS的 6个testid lowlimit，用于生成曲线图
maxOutputPowerhigh = []                          # 存放每一个信道 带宽 SCS的 6个testid highlimit，用于生成曲线图

evmRMS = []
evmDMRS = []

onoffPower = []
onoffP_low = []
onoffP_high = []
onoffP_labels = ['Off Power Before', 'On Power', 'Off Power After']


# 将xml文件转换成dict*****************************************************************************************
def xml_to_dict(filename):
    with open(filename, encoding='utf-8') as fd:
        doc = xmltodict.parse(fd.read())
    return doc

# 字典转xml功能函数********************************************************************************************
def dict_to_xml(data, filename):
    def to_xml(data):
        xx = []
        for k, v in data.items():
            if isinstance(v, dict):
                aa = to_xml(v)
                s = '<{key}>{value}</{key}>'.format(key=k, value=aa)
            else:
                s = '<{key}>{value}</{key}>'.format(key=k, value=v)
            xx.append(s)
        return ''.join(xx)
    # return '<xml>'+to_xml(data)+'</xml>'
    xml_data = '<xml>'+to_xml(data)+'</xml>'
    f = open(filename, 'w', encoding='utf-8')
    f.write(xml_data)
    f.close()
    tree = ElementTree.parse(filename)
    root = tree.getroot()
    prettyXml(root, '\t', '\n')
    tree.write(filename, encoding='utf-8')


# 美化xml文件格式************************************************************************************************
def prettyXml(element, indent, newline, level=0):  # element为传进来的elment类，
    if element:
        if element.text == None or element.text.isspace():
            element.text = newline + indent * (level + 1)
        else:
            element.text = newline + indent * (level + 1) + element.text.strip() + newline + indent * (level + 1)
    # else:  # 此两行取消注释可以把元素的内容单独成行
    #     element.text = newline + indent * (level + 1) + element.text.strip() + newline + indent * level

    temp = list(element)
    for subelement in temp:
        if temp.index(subelement) < (len(temp) - 1):
            subelement.tail = newline + indent * (level + 1)
        else:
            subelement.tail = newline + indent * level
        prettyXml(subelement, indent, newline, level=level + 1)


def dict_to_xmlstr(data, filename):
    ff = xmltodict.unparse(data)
    f = open(filename, 'w', encoding='utf-8')
    f.write(ff)
    f.close()
    tree = ElementTree.parse(filename)
    root = tree.getroot()
    prettyXml(root, '\t', '\n')
    tree.write(filename, encoding='utf-8')

# 遍历文件夹下所有文件名********************************************************************************
def ergodic_dir(dir_path):
    filename_fianl_list = []
    filename_list = os.listdir(dir_path)
    for i in filename_list:
        i = i[:-4]
        filename_fianl_list.append(i)
    return filename_fianl_list

# 检查是否有选择报告保存的路径
def checkreportpath():
    if REPORTPATH == '':
        emitsingle.thread_exitSingle.emit('Error:   Reporting path error!')
        time.sleep(0.1)

# 检查是否有选择DUT
def checkdutactive():
    if dutActiveDict == {}:
        emitsingle.thread_exitSingle.emit('Error:   No DUT was activated!')
        time.sleep(0.1)

# 检查测试序列是否有内容
def checktestseq():
    if len(testseq_dict['xml']['testseq']) == 0:
        emitsingle.thread_exitSingle.emit('Error:   There is nothing in the test sequence!')
        time.sleep(0.1)

# 保存当前配置到last config xml文件
def save_to_last_config():
        last_config['xml']['lastconfig']['lossfilepath1'] = pathLossDict['RF1']
        last_config['xml']['lastconfig']['lossfilepath2'] = pathLossDict['RF2']
        last_config['xml']['lastconfig']['lossfilepath3'] = pathLossDict['RF3']
        last_config['xml']['lastconfig']['lossfilepath4'] = pathLossDict['RF4']
        last_config['xml']['lastconfig']['reportpath'] = REPORTPATH
        activeDUTname = ''
        for k, v in dutAcitveStateDict.items():
            if v:
                activeDUTname = k
                break
        last_config['xml']['lastconfig']['DUT'] = activeDUTname
        dict_to_xmlstr(last_config, './config/Last Config.xml')

def lossfilehandle(COM_index):
    """
    :param COM_index:  需要处理的RF COM，如‘RF1’  'RF2'
    :return:  state: 0表示成功处理，1表示处理时出错
    """
    fre_list = []
    loss_list = []
    state = 0
    try:
        RF_lossdict = xml_to_dict(pathLossDict[COM_index])
        if isinstance(RF_lossdict['Loss']['loss'], list):
            for loss_index in range(len(RF_lossdict['Loss']['loss'])):
                fre_list.append(RF_lossdict['Loss']['loss'][loss_index]['Frequency'])
                loss_list.append(RF_lossdict['Loss']['loss'][loss_index]['Value'])
        elif isinstance(RF_lossdict['Loss']['loss'], list):
            fre_list.append(RF_lossdict['Loss']['loss']['Frequency'])
            loss_list.append(RF_lossdict['Loss']['loss']['Value'])
    except:
        fre_list = ['0']
        loss_list = ['0']
        state = 1
        emitsingle.stateupdataSingle.emit(
            'Thers is a problem with the '+COM_index+'COM Path loss file. The Path loss'
            'is set to 0dB!')

    return state, fre_list, loss_list

# 粗略计算测试总步骤，用于显示测试进度
def calc_total_step():
    sum_step = 0
    for i in range(len(testseq_dict['xml']['testseq'])):
        for j in range(len(testseq_dict['xml']['testseq'][i]['testplan'])):
            if testseq_dict['xml']['testseq'][i]['testplan'][j]['@enable'] == 'True':
                for k in range(len(testseq_dict['xml']['testseq'][i]['testplan'][j]['step'])):
                    if testseq_dict['xml']['testseq'][i]['testplan'][j]['step'][k]['params'][0]['value'] == 'True':
                        sum_step += 1

    emitsingle.totalStepupdata.emit(str(sum_step))

    return sum_step

# 获取LTE频段的双工方式
def getLTEDuplexMode(LTEBandNumber):
    '''
    :param LTEBandNumber:   包含LTE BAND 数字的字符串
    :return:  返回LTE BAND的双工方式
    '''
    try:
        if int(LTEBandNumber) in range(33) or int(LTEBandNumber) in range(64, 77):
            lte_duplexMode = 'FDD'
        else:
            lte_duplexMode = 'TDD'
        return lte_duplexMode
    except Exception as e:
        pass

def getNRDuplexMode(NRBandNumber):
    '''
    :param NRBandNumber: 包含NR BAND 数字的字符串
    :return:  返回NR BAND的双工方式
    '''
    try:
        if int(NRBandNumber) in range(29) or int(NRBandNumber) in range(66, 75):
            nr_duplexMode = 'FDD'
        elif int(NRBandNumber) in range(34, 52) or int(NRBandNumber) in [77, 78, 79]:
            nr_duplexMode = 'TDD'
        return nr_duplexMode
    except Exception as e:
        pass

def dBmplus(dbm1, dbm2):
    if '-999' not in [dbm1, dbm2]:
        mw1 = 10**(float(dbm1) / 10)
        mw2 = 10**(float(dbm2) / 10)
        total_mw = mw1 + mw2
        total_dbm = 10 * math.log10(total_mw)
        return format(total_dbm, '.2f')
    else:
        return '-999'









