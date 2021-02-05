#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2020/11/23 11:02
# @Author  : Feng Zhaohui
# @Site    : 
# @File    : testscript_handle.py
# @Software: PyCharm

import global_elements
from testmethods import NR_SA, NR_NSA
import parmslisthandle
import testseq_handle

def testseqhandle():
    # 循环Band
    for band_index in range(len(global_elements.testseq_dict['xml']['testseq'])):
        global_elements.NR_band = global_elements.testseq_dict['xml']['testseq'][band_index]['testplan'][0]['@band']
        global_elements.NR_band_r = global_elements.testseq_dict['xml']['testseq'][band_index]['testplan'][0]['@band']
        if 'DC' not in global_elements.NR_band:
            global_elements.NR_type_r = 'NR_SA'
        else:
            global_elements.NR_type_r = 'NR_NSA'
        # 循环测试项
        for case_index in range(len(global_elements.testseq_dict['xml']['testseq'][band_index]['testplan'])):
            testseq_handle.chartResutlClear()    # 更换测试项，清空图表数据
            global_elements.test_case_name = global_elements.testseq_dict['xml']['testseq'][band_index]['testplan'][case_index]['@testcase']
            global_elements.test_case_name_r = global_elements.testseq_dict['xml']['testseq'][band_index]['testplan'][case_index]['@testcase']
            global_elements.NR_condition = global_elements.testseq_dict['xml']['testseq'][band_index]['testplan'][case_index]['@condition']
            parms_list = global_elements.testseq_dict['xml']['testseq'][band_index]['testplan'][case_index]['step'][0][
                'params']

            if global_elements.testseq_dict['xml']['testseq'][band_index]['testplan'][case_index]['@enable'] == 'True':
                # state窗口提示用户设备电压和温度
                volt = global_elements.dutActiveDict['xml']['DUTCONFIG'][global_elements.NR_condition[2:4]]
                temp = global_elements.dutActiveDict['xml']['DUTCONFIG'][global_elements.NR_condition[0:2]]
                global_elements.emitsingle.stateupdataSingle.emit(
                    'Please check the tempratrue is ' + temp + '℃, the voltage is ' + volt + 'V')

                testParmslisthandle(parms_list)  # 将测试的内容参数更新到global参数中保存
                # 初始化CU (NR信令初始化)-----每一条测试项重新初始化一次CU
                state = False
                if global_elements.NR_type_r == 'NR_SA':
                    state = global_elements.CU_intance.reSetCU_and_reConnectDUT()
                elif global_elements.NR_type_r == 'NR_NSA':
                    state = global_elements.CU_intance.reSetCU_and_reConnectDUT_NSA()
                global_elements.emitsingle.stateupdataSingle.emit(
                    global_elements.NR_band + ' ' + global_elements.test_case_name + ' testing......')

                # if 'DFT' in global_elements.NR_Modulation:
                #     global_elements.CU_intance.MCSTablePreHandle()

                # 循环每个测试项的测试步骤
                for step_index in range(len(global_elements.testseq_dict['xml']['testseq'][band_index]['testplan'][case_index]['step'])):
                    parms_list = global_elements.testseq_dict['xml']['testseq'][band_index]['testplan'][case_index]['step'][step_index]['params']

                    # 针对每一个STEP，调用对应的测试方法
                    testStepHandle(parms_list, state)

                    # 更新summary
                    global_elements.emitsingle.summaryupdataSingle.emit(global_elements.finished_result_list)

def testParmslisthandle(parms_list):
    if global_elements.test_case_name in ['ts138521_1 6.2.1 UE maximum output power',
                                          'ts138521_1 6.2.2 UE maximum output power reduction',
                                          'ts138521_1 6.3.1 Minimum output power',
                                          'ts138521_1 6.3.3.2 General ON OFF time mask',
                                          'ts138521_1 6.4.2.1 Error Vector Magnitude for PUSCH',
                                          'ts138521_1 6.4.2.4 EVM equalizer spectrum flatness',
                                          'ts138521_1 6.4.2.5 EVM equalizer spectrum flatness for Half-Pi BPSK',
                                          'ts138521_1 6.5.2.2 Spectrum Emission Mask',
                                          'ts138521_1 6.5.2.4 Adjacent channel leakage ratio']:
        parmslisthandle.parmslisthandle(parms_list)
    elif global_elements.test_case_name == 'ts138521_1 6.2.4 Configured transmitted power':
        parmslisthandle.parmslisthandle_for_6_2_4(parms_list)
    elif global_elements.test_case_name == 'ts138521_1 6.4.1 Frequency error':
        parmslisthandle.parmslisthandle_for_6_4_1(parms_list)
    elif global_elements.test_case_name == 'ts138521_1 6.4.2.2 Carrier leakage':
        parmslisthandle.parmslisthandle_for_6_4_2_2(parms_list)
    elif global_elements.test_case_name == 'ts138521_1 6.4.2.3 In-band emissions for PUSCH':
        parmslisthandle.parmslisthandle_for_6_4_2_3(parms_list)
    elif global_elements.test_case_name == 'ts138521_1 6.5.1 Occupied bandwidth':
        parmslisthandle.parmslisthandle_for_6_5_1(parms_list)
    elif global_elements.test_case_name == 'ts138521_1 7.3.2 Reference sensitivity power level':
        parmslisthandle.parmslisthandle_for_7_3_2(parms_list)
    elif global_elements.test_case_name == 'ts138521_1 7.3.2_c Reference sensitivity power level Search':
        parmslisthandle.parmslisthandle_for_7_3_2_c(parms_list)
    elif global_elements.test_case_name == 'ts138521_1 7.4 Maximum input level':
        parmslisthandle.parmslisthandle_for_7_4(parms_list)
    elif global_elements.test_case_name == 'ts138521_3 6.2B.1.3 UE Maximum Output Power for Inter-Band EN-DC within FR1':
        parmslisthandle.parmslisthandle_for_6_2b_1_3(parms_list)


def testStepHandle(parms_list, state):
    if global_elements.test_case_name == 'ts138521_1 6.2.1 UE maximum output power':
        NR_SA.UEmaximumoutputpower6_2_1(parms_list, state)
    elif global_elements.test_case_name == 'ts138521_1 6.2.2 UE maximum output power reduction':
        NR_SA.UEmaximumoutputpowerreduction6_2_2(parms_list, state)
    elif global_elements.test_case_name == 'ts138521_1 6.2.4 Configured transmitted power':
        NR_SA.Configuredtransmittedpower6_2_4(parms_list, state)
    elif global_elements.test_case_name == 'ts138521_1 6.3.1 Minimum output power':
        NR_SA.Minimumoutputpower6_3_1(parms_list, state)
    elif global_elements.test_case_name == 'ts138521_1 6.3.3.2 General ON OFF time mask':
        NR_SA.UEmaximumoutputpower6_3_3_2(parms_list, state)
    elif global_elements.test_case_name == 'ts138521_1 6.4.1 Frequency error':
        NR_SA.Frequencyerror6_4_1(parms_list, state)
    elif global_elements.test_case_name == 'ts138521_1 6.4.2.1 Error Vector Magnitude for PUSCH':
        NR_SA.ErrorVectorMagnitudeforPUSCH6_4_2_1(parms_list, state)
    elif global_elements.test_case_name == 'ts138521_1 6.4.2.2 Carrier leakage':
        NR_SA.Carrierleakage6_4_2_2(parms_list, state)
    elif global_elements.test_case_name == 'ts138521_1 6.4.2.3 In-band emissions for PUSCH':
        NR_SA.In_bandemissionsforpusch6_4_2_3(parms_list, state)
    elif global_elements.test_case_name == 'ts138521_1 6.4.2.4 EVM equalizer spectrum flatness':
        NR_SA.EVMequalizerspectrumflatness6_4_2_4(parms_list, state)
    elif global_elements.test_case_name == 'ts138521_1 6.4.2.5 EVM equalizer spectrum flatness for Half-Pi BPSK':
        NR_SA.EVMequalizerspectrumflatnessforHalfPiBPSK6_4_2_5(parms_list, state)
    elif global_elements.test_case_name == 'ts138521_1 6.5.1 Occupied bandwidth':
        NR_SA.Occupiedbandwidth6_5_1(parms_list, state)
    elif global_elements.test_case_name == 'ts138521_1 6.5.2.2 Spectrum Emission Mask':
        NR_SA.SpectrumEmissionMask6_5_2_2(parms_list, state)
    elif global_elements.test_case_name == 'ts138521_1 6.5.2.4 Adjacent channel leakage ratio':
        NR_SA.Adjacentchannelleakageratio6_5_2_4(parms_list, state)
    elif global_elements.test_case_name == 'ts138521_1 7.3.2 Reference sensitivity power level':
        NR_SA.Referencesensitivitypowerlevel7_3_2(parms_list, state)
    elif global_elements.test_case_name == 'ts138521_1 7.3.2_c Reference sensitivity power level Search':
        NR_SA.Referencesensitivitypowerlevel7_3_2_c(parms_list, state)
    elif global_elements.test_case_name == 'ts138521_1 7.4 Maximum input level':
        NR_SA.Maximuminputlevel7_4(parms_list, state)
    elif global_elements.test_case_name == 'ts138521_3 6.2B.1.3 UE Maximum Output Power for Inter-Band EN-DC within FR1':
        NR_NSA.UEMaximumOutputPowerforInterBandENDCwithinFR1_6_2B_1_3(parms_list, state)
