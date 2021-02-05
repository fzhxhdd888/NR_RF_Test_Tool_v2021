#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2020/11/11 8:42
# @Author  : Feng Zhaohui
# @Site    : 
# @File    : testseq_handle.py
# @Software: PyCharm


'''
    这里有方法主要是用于将测试项xml内容根据条件生成对应的字典，便于测试以及保存测试序列时使用
'''

import global_elements
import copy

# 通过新建测试序列生成待测试序列字典函数
def new_testseq_dict(band_list, SCS_list, testcase_list, condition_list):
    '''
    主要的生成函数
    :param band_list:
    :param SCS_list:
    :param testcase_list:
    :param condition_list:
    :return:
    '''
    global_elements.testseq_dict = {'xml': {'testseq': []}}     # 生成前先清空字典

    for index in range(len(band_list)):
        band_dict = {'testplan': []}
        currentSCS_list = SCS_list[index].split(',')
        for casename in testcase_list:
            if casename == 'ts138521_1 6.2.1 UE maximum output power':
                caseDict = sa_6_2_1(currentSCS_list)
            elif casename == 'ts138521_1 6.2.2 UE maximum output power reduction':
                caseDict = sa_6_2_2(currentSCS_list)
            elif casename == 'ts138521_1 6.2.4 Configured transmitted power':
                caseDict = sa_6_2_4(currentSCS_list)
            elif casename == 'ts138521_1 6.3.1 Minimum output power':
                caseDict = sa_6_3_1(currentSCS_list)
            elif casename == 'ts138521_1 6.3.3.2 General ON OFF time mask':
                caseDict = sa_6_3_3_2(currentSCS_list)
            elif casename == 'ts138521_1 6.4.1 Frequency error':
                caseDict = sa_6_4_1(currentSCS_list)
            elif casename == 'ts138521_1 6.4.2.1 Error Vector Magnitude for PUSCH':
                caseDict = sa_6_4_2_1_pusch(currentSCS_list)
            elif casename == 'ts138521_1 6.4.2.2 Carrier leakage':
                caseDict = sa_6_4_2_2(currentSCS_list)
            elif casename == 'ts138521_1 6.4.2.3 In-band emissions for PUSCH':
                caseDict = sa_6_4_2_3_for_pusch(currentSCS_list)
            elif casename == 'ts138521_1 6.4.2.4 EVM equalizer spectrum flatness':
                caseDict = sa_6_4_2_4(currentSCS_list)
            elif casename == 'ts138521_1 6.4.2.5 EVM equalizer spectrum flatness for Half-Pi BPSK':
                caseDict = sa_6_4_2_5(currentSCS_list)
            elif casename == 'ts138521_1 6.5.1 Occupied bandwidth':
                caseDict = sa_6_5_1(currentSCS_list, band_list[index])
            elif casename == 'ts138521_1 6.5.2.2 Spectrum Emission Mask':
                caseDict = sa_6_5_2_2(currentSCS_list)
            elif casename == 'ts138521_1 6.5.2.4 Adjacent channel leakage ratio':
                caseDict = sa_6_5_2_4(currentSCS_list)
            elif casename == 'ts138521_1 7.3.2 Reference sensitivity power level':
                caseDict = sa_7_3_2(currentSCS_list)
            elif casename == 'ts138521_1 7.3.2_c Reference sensitivity power level Search':
                caseDict = sa_7_3_2_c(currentSCS_list)
            elif casename == 'ts138521_1 7.4 Maximum input level':
                caseDict = sa_7_4(currentSCS_list)
            elif casename == 'ts138521_3 6.2B.1.3 UE Maximum Output Power for Inter-Band EN-DC within FR1':
                caseDict = nsa_6_2b_1_3(currentSCS_list)

            caseDict['@band'] = band_list[index]
            caseDict['@testcase'] = casename
            caseDict['@enable'] = 'True'
            caseDict['@condition'] = condition_list[0] + condition_list[1]
            band_dict['testplan'].append(caseDict)
        # 将整理出的字典加入最终字典
        global_elements.testseq_dict['xml']['testseq'].append(band_dict)

# ts138521_1 6_2_1 UE maximum output power xml文件处理
def sa_6_2_1(SCS_list):
    case_dict = global_elements.xml_to_dict('./config/TestcaseConfig/ts138521_1 6_2_1 UE maximum output power.xml')
    if len(SCS_list) == 1:
       for i in range(len(case_dict['xml']['step'])):    # SCS  Highest的测试内容关闭, 并给SCS赋值
           if case_dict['xml']['step'][i]['params'][3]['value']  != 'Low':
                case_dict['xml']['step'][i]['params'][0]['value'] = 'False'
           if case_dict['xml']['step'][i]['params'][3]['value'] == 'Low':
               case_dict['xml']['step'][i]['params'][3]['value'] = SCS_list[0]

    elif len(SCS_list) in [2, 3]:
        for i in range(len(case_dict['xml']['step'])):
            if case_dict['xml']['step'][i]['params'][3]['value']  == 'Low':
                case_dict['xml']['step'][i]['params'][3]['value'] = SCS_list[0]
            else:
                case_dict['xml']['step'][i]['params'][3]['value'] = SCS_list[-1]

    return case_dict['xml']

# tts138521_1 6_2_2 UE maximum output power reduction xml文件处理
def sa_6_2_2(SCS_list):
    if global_elements.dutActiveDict['xml']['DUTCONFIG']['powerclass'] == '3':
        case_dict = global_elements.xml_to_dict(
            './config/TestcaseConfig/ts138521_1 6_2_2 UE maximum output power reduction_cl3.xml')
    else:
        case_dict = global_elements.xml_to_dict(
            './config/TestcaseConfig/ts138521_1 6_2_2 UE maximum output power reduction_cl2.xml')
    if len(SCS_list) == 1:
        for i in range(len(case_dict['xml']['step'])):  # SCS  Highest的测试内容关闭, 并给SCS赋值
            if case_dict['xml']['step'][i]['params'][3]['value'] != 'Low':
                case_dict['xml']['step'][i]['params'][0]['value'] = 'False'
            if case_dict['xml']['step'][i]['params'][3]['value'] == 'Low':
                case_dict['xml']['step'][i]['params'][3]['value'] = SCS_list[0]

    elif len(SCS_list) in [2, 3]:
        for i in range(len(case_dict['xml']['step'])):
            if case_dict['xml']['step'][i]['params'][3]['value'] == 'Low':
                case_dict['xml']['step'][i]['params'][3]['value'] = SCS_list[0]
            else:
                case_dict['xml']['step'][i]['params'][3]['value'] = SCS_list[-1]

    return case_dict['xml']

# ts138521_1 6_2_4 Configured transmitted power xml文件处理
def sa_6_2_4(SCS_list):
    case_dict = global_elements.xml_to_dict('./config/TestcaseConfig/ts138521_1 6_2_4 Configured transmitted power.xml')

    for i in range(len(case_dict['xml']['step'])):    # 给SCS赋值
       case_dict['xml']['step'][i]['params'][3]['value'] = SCS_list[0]

    return case_dict['xml']

# ts138521_1 6_3_1 Configured transmitted power xml文件处理
def sa_6_3_1(SCS_list):
    case_dict = global_elements.xml_to_dict('./config/TestcaseConfig/ts138521_1 6_3_1 Minimum output power.xml')

    for i in range(len(case_dict['xml']['step'])):    # 给SCS赋值  Highest
       case_dict['xml']['step'][i]['params'][3]['value'] = SCS_list[-1]

    return case_dict['xml']

# ts138521_1 6_3_3_2 xml文件处理
def sa_6_3_3_2(SCS_list):
    case_dict = global_elements.xml_to_dict('./config/TestcaseConfig/ts138521_1 6_3_3_2 General ON OFF time mask.xml')
    if len(SCS_list) == 1:
       for i in range(len(case_dict['xml']['step'])):    # SCS  Highest的测试内容关闭, 并给SCS赋值
           if case_dict['xml']['step'][i]['params'][3]['value']  != 'Low':
                case_dict['xml']['step'][i]['params'][0]['value'] = 'False'
           if case_dict['xml']['step'][i]['params'][3]['value'] == 'Low':
               case_dict['xml']['step'][i]['params'][3]['value'] = SCS_list[0]

    elif len(SCS_list) in [2, 3]:
        for i in range(len(case_dict['xml']['step'])):
            if case_dict['xml']['step'][i]['params'][3]['value']  == 'Low':
                case_dict['xml']['step'][i]['params'][3]['value'] = SCS_list[0]
            else:
                case_dict['xml']['step'][i]['params'][3]['value'] = SCS_list[-1]

    return case_dict['xml']

# tts138521_1 6_4_1 Frequency error.xml文件处理
def sa_6_4_1(SCS_list):
    case_dict = global_elements.xml_to_dict('./config/TestcaseConfig/ts138521_1 6_4_1 Frequency error.xml')
     # 给SCS赋值
    if isinstance(case_dict['xml']['step'], dict):
        case_dict['xml']['step']['params'][3]['value'] = SCS_list[0]
        case_dict['xml']['step'] = [case_dict['xml']['step']]
    elif isinstance(case_dict['xml']['step'], list):
        for i in range(len(case_dict['xml']['step'])):  # 给SCS赋值
            case_dict['xml']['step'][i]['params'][3]['value'] = SCS_list[0]

    return case_dict['xml']

# tts138521_1 6_4_2_1 Frequency error.xml文件处理
def sa_6_4_2_1_pusch(SCS_list):
    case_dict = global_elements.xml_to_dict('./config/TestcaseConfig/ts138521_1 6_4_2_1 Error Vector Magnitude for PUSCH.xml')
    final_dict = {'xml':{'step': []}}
     # 给SCS赋值
    for scs in SCS_list:
        for i in range(len(case_dict['xml']['step'])):    # ALL SCS，每个scs生成一个列表，最后合并
            case_dict['xml']['step'][i]['params'][3]['value'] = scs
        final_dict['xml']['step'].extend(copy.deepcopy(case_dict['xml']['step']))

    return final_dict['xml']

def sa_6_4_2_2(SCS_list):
    case_dict = global_elements.xml_to_dict('./config/TestcaseConfig/ts138521_1 6_4_2_2 Carrier leakage.xml')
     # 给SCS赋值
    for i in range(len(case_dict['xml']['step'])):  # 给SCS赋值
            case_dict['xml']['step'][i]['params'][3]['value'] = SCS_list[0]

    return case_dict['xml']

def sa_6_4_2_3_for_pusch(SCS_list):
    case_dict = global_elements.xml_to_dict('./config/TestcaseConfig/ts138521_1 6_4_2_3 In-band emissions for PUSCH.xml')
     # 给SCS赋值
    for i in range(len(case_dict['xml']['step'])):  # 给SCS赋值
            case_dict['xml']['step'][i]['params'][3]['value'] = SCS_list[0]

    return case_dict['xml']

# ts138521_1 6_4_2_4 Configured transmitted power xml文件处理
def sa_6_4_2_4(SCS_list):
    case_dict = global_elements.xml_to_dict('./config/TestcaseConfig/ts138521_1 6_4_2_4 EVM equalizer spectrum flatness.xml')

    for i in range(len(case_dict['xml']['step'])):    # 给SCS赋值
       case_dict['xml']['step'][i]['params'][3]['value'] = SCS_list[0]

    return case_dict['xml']

# ts138521_1 6_4_2_5  xml文件处理
def sa_6_4_2_5(SCS_list):
    case_dict = global_elements.xml_to_dict('./config/TestcaseConfig/ts138521_1 6_4_2_5 EVM equalizer spectrum flatness for Half-Pi BPSK.xml')

    for i in range(len(case_dict['xml']['step'])):    # 给SCS赋值
       case_dict['xml']['step'][i]['params'][3]['value'] = SCS_list[0]

    return case_dict['xml']

# ts138521_1 6_5_1  xml文件处理
def sa_6_5_1(SCS_list, band):
    final_step = {'xml':{'step':[]}}
    case_dict = global_elements.xml_to_dict('./config/TestcaseConfig/ts138521_1 6_5_1 Occupied bandwidth.xml')
    scsNumber = SCS_list[0]
    scsStr = 'SCS_' + scsNumber
    bandname = band
    allbw_dict = global_elements.xml_to_dict('./config/ParmsConfig/NRAllBW.xml')
    if allbw_dict['xml'][bandname][scsStr]['AllBW'] != 'NA':
        bw_list = allbw_dict['xml'][bandname][scsStr]['AllBW'].split(',')
    else:
        bw_list = []

    if bandname in ['n77_TDD', 'n78_TDD', 'n79_TDD']:
        if len(bw_list) > 0:
            for bw_index in range(len(bw_list)):
                for channel in ['Low', 'Mid', 'High']:
                    case_dict['xml']['step']['params'][3]['value'] = SCS_list[0]
                    case_dict['xml']['step']['params'][1]['value'] = bw_list[bw_index]
                    case_dict['xml']['step']['params'][2]['value'] = channel
                    final_step['xml']['step'].append(copy.deepcopy(case_dict['xml']['step']))

    else:
        if len(bw_list) > 0:
            for bw_index in range(len(bw_list)):
                case_dict['xml']['step']['params'][3]['value'] = SCS_list[0]
                case_dict['xml']['step']['params'][1]['value'] = bw_list[bw_index]
                case_dict['xml']['step']['params'][2]['value'] = 'Mid'
                final_step['xml']['step'].append(copy.deepcopy(case_dict['xml']['step']))

    return final_step['xml']

# tts138521_1 6_5_2_2  xml文件处理
def sa_6_5_2_2(SCS_list):
    if global_elements.dutActiveDict['xml']['DUTCONFIG']['powerclass'] == '3':
        case_dict = global_elements.xml_to_dict(
            './config/TestcaseConfig/ts138521_1 6_5_2_2 Spectrum Emission Mask_cl3.xml')
    else:
        case_dict = global_elements.xml_to_dict(
            './config/TestcaseConfig/ts138521_1 6_5_2_2 Spectrum Emission Mask_cl2.xml')
    if len(SCS_list) == 1:
        for i in range(len(case_dict['xml']['step'])):  # SCS  Highest的测试内容关闭, 并给SCS赋值
            if case_dict['xml']['step'][i]['params'][3]['value'] != 'Low':
                case_dict['xml']['step'][i]['params'][0]['value'] = 'False'
            if case_dict['xml']['step'][i]['params'][3]['value'] == 'Low':
                case_dict['xml']['step'][i]['params'][3]['value'] = SCS_list[0]

    elif len(SCS_list) in [2, 3]:
        for i in range(len(case_dict['xml']['step'])):
            if case_dict['xml']['step'][i]['params'][3]['value'] == 'Low':
                case_dict['xml']['step'][i]['params'][3]['value'] = SCS_list[0]
            else:
                case_dict['xml']['step'][i]['params'][3]['value'] = SCS_list[-1]

    return case_dict['xml']

# tts138521_1 6_5_2_4  xml文件处理
def sa_6_5_2_4(SCS_list):
    if global_elements.dutActiveDict['xml']['DUTCONFIG']['powerclass'] == '3':
        case_dict = global_elements.xml_to_dict(
            './config/TestcaseConfig/ts138521_1 6_5_2_4 Adjacent channel leakage ratio_cl3.xml')
    else:
        case_dict = global_elements.xml_to_dict(
            './config/TestcaseConfig/ts138521_1 6_5_2_4 Adjacent channel leakage ratio_cl2.xml')
    if len(SCS_list) == 1:
        for i in range(len(case_dict['xml']['step'])):  # SCS  Highest的测试内容关闭, 并给SCS赋值
            if case_dict['xml']['step'][i]['params'][3]['value'] != 'Low':
                case_dict['xml']['step'][i]['params'][0]['value'] = 'False'
            if case_dict['xml']['step'][i]['params'][3]['value'] == 'Low':
                case_dict['xml']['step'][i]['params'][3]['value'] = SCS_list[0]

    elif len(SCS_list) in [2, 3]:
        for i in range(len(case_dict['xml']['step'])):
            if case_dict['xml']['step'][i]['params'][3]['value'] == 'Low':
                case_dict['xml']['step'][i]['params'][3]['value'] = SCS_list[0]
            else:
                case_dict['xml']['step'][i]['params'][3]['value'] = SCS_list[-1]

    return case_dict['xml']

# tts138521_1 7_3_2 .xml文件处理
def sa_7_3_2(SCS_list):
    case_dict = global_elements.xml_to_dict('./config/TestcaseConfig/ts138521_1 7_3_2 Reference sensitivity power level.xml')
     # 给SCS赋值
    for i in range(len(case_dict['xml']['step'])):  # 给SCS赋值
        case_dict['xml']['step'][i]['params'][3]['value'] = SCS_list[0]

    return case_dict['xml']

# tts138521_1 7_3_2 .xml文件处理
def sa_7_3_2_c(SCS_list):
    case_dict = global_elements.xml_to_dict('./config/TestcaseConfig/ts138521_1 7_3_2_c Reference sensitivity power level Search.xml')
     # 给SCS赋值
    for i in range(len(case_dict['xml']['step'])):  # 给SCS赋值
        case_dict['xml']['step'][i]['params'][3]['value'] = SCS_list[0]

    return case_dict['xml']

# tts138521_1 7_4 .xml文件处理
def sa_7_4(SCS_list):
    case_dict = global_elements.xml_to_dict('./config/TestcaseConfig/ts138521_1 7_4 Maximum input level.xml')
     # 给SCS赋值
    for i in range(len(case_dict['xml']['step'])):  # 给SCS赋值
        case_dict['xml']['step'][i]['params'][3]['value'] = SCS_list[0]

    return case_dict['xml']

# ts138521_3 6_2B_1_3 UE Maximum Output Power for Inter-Band EN-DC within FR1.xml 文件处理
def nsa_6_2b_1_3(SCS_list):
    case_dict = global_elements.xml_to_dict('./config/TestcaseConfig/ts138521_3 6_2B_1_3 UE Maximum Output Power for Inter-Band EN-DC within FR1.xml')
    if len(SCS_list) == 1:
       for i in range(len(case_dict['xml']['step'])):    # SCS  Highest的测试内容关闭, 并给SCS赋值
           if case_dict['xml']['step'][i]['params'][3]['value']  != 'Low':
                case_dict['xml']['step'][i]['params'][0]['value'] = 'False'
           if case_dict['xml']['step'][i]['params'][3]['value'] == 'Low':
               case_dict['xml']['step'][i]['params'][3]['value'] = SCS_list[0]

    elif len(SCS_list) in [2, 3]:
        for i in range(len(case_dict['xml']['step'])):
            if case_dict['xml']['step'][i]['params'][3]['value']  == 'Low':
                case_dict['xml']['step'][i]['params'][3]['value'] = SCS_list[0]
            else:
                case_dict['xml']['step'][i]['params'][3]['value'] = SCS_list[-1]

    return case_dict['xml']

#  chart 参数清零
def chartResutlClear():
    global_elements.maxOutputPowerResutl = []
    global_elements.maxOutputPowerLow = []
    global_elements.maxOutputPowerhigh = []
    global_elements.maxOutputPowerTestid = []

    global_elements.evmDMRS = []
    global_elements.evmRMS = []
