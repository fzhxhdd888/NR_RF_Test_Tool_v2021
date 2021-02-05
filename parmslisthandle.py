#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2020/11/27 9:14
# @Author  : Feng Zhaohui
# @Site    : 
# @File    : parmslisthandle.py
# @Software: PyCharm

import global_elements
import reporthandle
import re


def parmslisthandle(parmslist):
    try:
        # 判断是否 有 CHANNEL SCS BW的变化，有变化返回True,用于判断是否要reset CU
        isChanged = False
        if global_elements.NR_bw != parmslist[1]['value'] or global_elements.NR_ch != parmslist[2]['value'] or \
                global_elements.NR_SCS != parmslist[3]['value']:
            isChanged = True

        global_elements.NR_bw = parmslist[1]['value']
        global_elements.NR_ch = parmslist[2]['value']
        global_elements.NR_SCS = parmslist[3]['value']
        global_elements.NR_testid = parmslist[4]['value']
        global_elements.NR_Modulation = parmslist[5]['value']
        global_elements.NR_RBAllocation = parmslist[6]['value']

        if global_elements.dutActiveDict['xml']['DUTCONFIG']['powerclass'] == '2' and \
                global_elements.NR_band in ['n41_TDD', 'n77_TDD', 'n78_TDD', 'n79_TDD']:
            global_elements.NR_p_max = '26'
        else:
            global_elements.NR_p_max = '23'

        # 提取SCS信息
        scs_num = global_elements.NR_SCS
        scs_str = 'SCS_' + scs_num
        global_elements.NR_SCS_r = 'SCS_' + scs_num
        # 提取BW信息
        bw_num = global_elements.SCSBandwidthConfig_dict['xml'][global_elements.NR_band][scs_str][global_elements.NR_bw]
        global_elements.NR_bw_num = bw_num
        bw_str = 'BW_' + bw_num
        global_elements.NR_bw_r = 'NR_BW' + bw_num + 'MHz'

        global_elements.NR_ch_r = global_elements.ChannelConfig_dict['xml'][global_elements.NR_band][scs_str][bw_str]['UL'][
            global_elements.NR_ch]['CarrierCentreCh']
        global_elements.NR_testid_r = global_elements.NR_testid
        global_elements.NR_Modulation_r = global_elements.NR_Modulation

        if '256 QAM' in global_elements.NR_Modulation:
            table_str = 'MCS index table_256QAM: '
        else:
            table_str = 'MCS index table_64QAM: '

        if 'BPSK' in global_elements.NR_Modulation:
            mcs_index = global_elements.MCSindex_dict['xml']['UL']['DFT']['halfpi_BPSK'].split('_')[1]
        elif 'QPSK' in global_elements.NR_Modulation:
            mcs_index = global_elements.MCSindex_dict['xml']['UL']['DFT']['QPSK'].split('_')[1]
        elif '16 QAM' in global_elements.NR_Modulation:
            mcs_index = global_elements.MCSindex_dict['xml']['UL']['DFT']['QAM16'].split('_')[1]
        elif '64 QAM' in global_elements.NR_Modulation:
            mcs_index = global_elements.MCSindex_dict['xml']['UL']['DFT']['QAM64'].split('_')[1]
        else:
            mcs_index = global_elements.MCSindex_dict['xml']['UL']['DFT']['QAM256'].split('_')[1]
        global_elements.NR_MCSindex_r = table_str + mcs_index

        # RB
        rb_str = '_'.join(global_elements.NR_RBAllocation.split(' '))
        if 'DFT' in global_elements.NR_Modulation:
            wave_type_str = 'DFT_s'
        else:
            wave_type_str = 'CP'
        rb_config_str = global_elements.RBConfig_dict['xml'][bw_str][scs_str][wave_type_str][rb_str]
        global_elements.NR_RBAllocation_r = global_elements.NR_RBAllocation + ':' + rb_config_str

        # 波形
        if 'DFT' in global_elements.NR_Modulation:
            global_elements.NR_Waveform_r = 'DFT_s'
        else:
            global_elements.NR_Waveform_r = 'CP'

        return isChanged
    except Exception as e:
        global_elements.emitsingle.thread_exitSingle.emit('parmslisthandle failed('+global_elements.test_case_name+'), Program abnormal exit! '
                                                          'Error: ' + e.__doc__)

def parmslisthandle_for_6_2_4(parmslist):
    try:
        # 判断是否 有 CHANNEL SCS BW Testpoint的变化，有变化返回True,用于判断是否要reset CU
        isChanged = False
        if global_elements.NR_bw != parmslist[1]['value'] or global_elements.NR_ch != parmslist[2]['value'] or \
                global_elements.NR_SCS != parmslist[3]['value']:
            isChanged = True

        global_elements.NR_bw = parmslist[1]['value']
        global_elements.NR_ch = parmslist[2]['value']
        global_elements.NR_SCS = parmslist[3]['value']
        global_elements.NR_testid = parmslist[4]['value']
        global_elements.NR_Modulation = parmslist[5]['value']
        global_elements.NR_RBAllocation = parmslist[6]['value']
        global_elements.NR_TestPoint = parmslist[7]['value']

        if global_elements.NR_TestPoint == '1':
            global_elements.NR_p_max = '-10'
        elif global_elements.NR_TestPoint == '2':
            global_elements.NR_p_max = '10'
        elif global_elements.NR_TestPoint == '3':
            global_elements.NR_p_max = '15'
        elif global_elements.NR_TestPoint == '4':
            global_elements.NR_p_max = '20'

        # 提取SCS信息
        scs_num = global_elements.NR_SCS
        scs_str = 'SCS_' + scs_num
        global_elements.NR_SCS_r = 'SCS_' + scs_num
        # 提取BW信息
        bw_num = global_elements.SCSBandwidthConfig_dict['xml'][global_elements.NR_band][scs_str][global_elements.NR_bw]
        global_elements.NR_bw_num = bw_num
        bw_str = 'BW_' + bw_num
        global_elements.NR_bw_r = 'NR_BW' + bw_num + 'MHz'

        global_elements.NR_ch_r = global_elements.ChannelConfig_dict['xml'][global_elements.NR_band][scs_str][bw_str]['UL'][
            global_elements.NR_ch]['CarrierCentreCh']
        global_elements.NR_testid_r = global_elements.NR_testid
        global_elements.NR_Modulation_r = global_elements.NR_Modulation

        if '256 QAM' in global_elements.NR_Modulation:
            table_str = 'MCS index table_256QAM: '
        else:
            table_str = 'MCS index table_64QAM: '

        if 'BPSK' in global_elements.NR_Modulation:
            mcs_index = global_elements.MCSindex_dict['xml']['UL']['DFT']['halfpi_BPSK'].split('_')[1]
        elif 'QPSK' in global_elements.NR_Modulation:
            mcs_index = global_elements.MCSindex_dict['xml']['UL']['DFT']['QPSK'].split('_')[1]
        elif '16 QAM' in global_elements.NR_Modulation:
            mcs_index = global_elements.MCSindex_dict['xml']['UL']['DFT']['QAM16'].split('_')[1]
        elif '64 QAM' in global_elements.NR_Modulation:
            mcs_index = global_elements.MCSindex_dict['xml']['UL']['DFT']['QAM64'].split('_')[1]
        else:
            mcs_index = global_elements.MCSindex_dict['xml']['UL']['DFT']['QAM256'].split('_')[1]
        global_elements.NR_MCSindex_r = table_str + mcs_index

        # RB
        rb_str = '_'.join(global_elements.NR_RBAllocation.split(' '))
        if 'DFT' in global_elements.NR_Modulation:
            wave_type_str = 'DFT_s'
        else:
            wave_type_str = 'CP'
        rb_config_str = global_elements.RBConfig_dict['xml'][bw_str][scs_str][wave_type_str][rb_str]
        global_elements.NR_RBAllocation_r = global_elements.NR_RBAllocation + ':' + rb_config_str

        # 波形
        if 'DFT' in global_elements.NR_Modulation:
            global_elements.NR_Waveform_r = 'DFT_s'
        else:
            global_elements.NR_Waveform_r = 'CP'

        global_elements.NR_TestPoint_r = global_elements.NR_TestPoint

        return isChanged
    except Exception as e:
        global_elements.emitsingle.thread_exitSingle.emit('parmslisthandle_for_6_2_4 failed, Program abnormal exit! '
                                                          'Error: ' + e.__doc__)

def parmslisthandle_for_6_4_1(parmslist):
    try:
        # 判断是否 有 CHANNEL SCS BW Testpoint的变化，有变化返回True,用于判断是否要reset CU
        isChanged = False
        if global_elements.NR_bw != parmslist[1]['value'] or global_elements.NR_ch != parmslist[2]['value'] or \
                global_elements.NR_SCS != parmslist[3]['value']:
            isChanged = True

        global_elements.NR_bw = parmslist[1]['value']
        global_elements.NR_ch = parmslist[2]['value']
        global_elements.NR_SCS = parmslist[3]['value']
        global_elements.NR_testid = parmslist[4]['value']
        global_elements.NR_Modulation = parmslist[5]['value']
        global_elements.NR_RBAllocation = parmslist[6]['value']

        if global_elements.dutActiveDict['xml']['DUTCONFIG']['powerclass'] == '2' and \
                global_elements.NR_band in ['n41_TDD', 'n77_TDD', 'n78_TDD', 'n79_TDD']:
            global_elements.NR_p_max = '26'
        else:
            global_elements.NR_p_max = '23'

        # 提取SCS信息
        scs_num = global_elements.NR_SCS
        scs_str = 'SCS_' + scs_num
        global_elements.NR_SCS_r = 'SCS_' + scs_num
        # 提取BW信息
        bw_num = global_elements.SCSBandwidthConfig_dict['xml'][global_elements.NR_band][scs_str][global_elements.NR_bw]
        global_elements.NR_bw_num = bw_num
        bw_str = 'BW_' + bw_num
        global_elements.NR_bw_r = 'NR_BW' + bw_num + 'MHz'

        global_elements.NR_ch_r = global_elements.ChannelConfig_dict['xml'][global_elements.NR_band][scs_str][bw_str]['UL'][
            global_elements.NR_ch]['CarrierCentreCh']
        global_elements.NR_testid_r = global_elements.NR_testid
        global_elements.NR_Modulation_r = global_elements.NR_Modulation

        if '256 QAM' in global_elements.NR_Modulation:
            table_str = 'MCS index table_256QAM: '
        else:
            table_str = 'MCS index table_64QAM: '

        if 'BPSK' in global_elements.NR_Modulation:
            mcs_index = global_elements.MCSindex_dict['xml']['UL']['DFT']['halfpi_BPSK'].split('_')[1]
        elif 'QPSK' in global_elements.NR_Modulation:
            mcs_index = global_elements.MCSindex_dict['xml']['UL']['DFT']['QPSK'].split('_')[1]
        elif '16 QAM' in global_elements.NR_Modulation:
            mcs_index = global_elements.MCSindex_dict['xml']['UL']['DFT']['QAM16'].split('_')[1]
        elif '64 QAM' in global_elements.NR_Modulation:
            mcs_index = global_elements.MCSindex_dict['xml']['UL']['DFT']['QAM64'].split('_')[1]
        else:
            mcs_index = global_elements.MCSindex_dict['xml']['UL']['DFT']['QAM256'].split('_')[1]
        global_elements.NR_MCSindex_r = table_str + mcs_index

        # RB
        rb_config_str = global_elements.UlRBConfig_dict['xml'][global_elements.NR_band][scs_str][bw_str]
        global_elements.NR_RBAllocation_r = global_elements.NR_RBAllocation + ':' + rb_config_str

        global_elements.NR_DlRBconfig = global_elements.DlRBConfig_dict['xml'][bw_str][scs_str]

        # 波形
        if 'DFT' in global_elements.NR_Modulation:
            global_elements.NR_Waveform_r = 'DFT_s'
        else:
            global_elements.NR_Waveform_r = 'CP'

        return isChanged
    except Exception as e:
        global_elements.emitsingle.thread_exitSingle.emit('parmslisthandle_for_6_4_1 failed, Program abnormal exit! '
                                                          'Error: ' + e.__doc__)

def parmslisthandle_for_6_4_2_2(parmslist):
    try:
        # 判断是否 有 CHANNEL SCS BW 的变化，有变化返回True,用于判断是否要reset CU
        isChanged = False
        if global_elements.NR_bw != parmslist[1]['value'] or global_elements.NR_ch != parmslist[2]['value'] or \
                global_elements.NR_SCS != parmslist[3]['value']:
            isChanged = True

        global_elements.NR_bw = parmslist[1]['value']
        global_elements.NR_ch = parmslist[2]['value']
        global_elements.NR_SCS = parmslist[3]['value']
        global_elements.NR_testid = parmslist[4]['value']
        global_elements.NR_Modulation = parmslist[5]['value']
        global_elements.NR_RBAllocation = parmslist[6]['value']
        p_exp = parmslist[7]['value']
        global_elements.NR_Pexp_pre = parmslist[7]['value']

        if global_elements.dutActiveDict['xml']['DUTCONFIG']['powerclass'] == '2' and \
                global_elements.NR_band in ['n41_TDD', 'n77_TDD', 'n78_TDD', 'n79_TDD']:
            global_elements.NR_p_max = '26'
        else:
            global_elements.NR_p_max = '23'

        # 提取SCS信息
        scs_num = global_elements.NR_SCS
        scs_str = 'SCS_' + scs_num
        global_elements.NR_SCS_r = 'SCS_' + scs_num
        # 提取BW信息
        bw_num = global_elements.SCSBandwidthConfig_dict['xml'][global_elements.NR_band][scs_str][global_elements.NR_bw]
        global_elements.NR_bw_num = bw_num
        bw_str = 'BW_' + bw_num
        global_elements.NR_bw_r = 'NR_BW' + bw_num + 'MHz'

        global_elements.NR_ch_r = global_elements.ChannelConfig_dict['xml'][global_elements.NR_band][scs_str][bw_str]['UL'][
            global_elements.NR_ch]['CarrierCentreCh']
        global_elements.NR_testid_r = global_elements.NR_testid
        global_elements.NR_Modulation_r = global_elements.NR_Modulation

        if '256 QAM' in global_elements.NR_Modulation:
            table_str = 'MCS index table_256QAM: '
        else:
            table_str = 'MCS index table_64QAM: '

        if 'BPSK' in global_elements.NR_Modulation:
            mcs_index = global_elements.MCSindex_dict['xml']['UL']['DFT']['halfpi_BPSK'].split('_')[1]
        elif 'QPSK' in global_elements.NR_Modulation:
            mcs_index = global_elements.MCSindex_dict['xml']['UL']['DFT']['QPSK'].split('_')[1]
        elif '16 QAM' in global_elements.NR_Modulation:
            mcs_index = global_elements.MCSindex_dict['xml']['UL']['DFT']['QAM16'].split('_')[1]
        elif '64 QAM' in global_elements.NR_Modulation:
            mcs_index = global_elements.MCSindex_dict['xml']['UL']['DFT']['QAM64'].split('_')[1]
        else:
            mcs_index = global_elements.MCSindex_dict['xml']['UL']['DFT']['QAM256'].split('_')[1]
        global_elements.NR_MCSindex_r = table_str + mcs_index

        # RB
        rb_str = '_'.join(global_elements.NR_RBAllocation.split(' '))
        if 'DFT' in global_elements.NR_Modulation:
            wave_type_str = 'DFT_s'
        else:
            wave_type_str = 'CP'
        rb_config_str = global_elements.RBConfig_dict['xml'][bw_str][scs_str][wave_type_str][rb_str]
        global_elements.NR_RBAllocation_r = global_elements.NR_RBAllocation + ':' + rb_config_str

        # 波形
        if 'DFT' in global_elements.NR_Modulation:
            global_elements.NR_Waveform_r = 'DFT_s'
        else:
            global_elements.NR_Waveform_r = 'CP'

        # 换算P_exp
        ul_fre = reporthandle.NreftoFre(global_elements.NR_ch_r)
        if 3000 - float(ul_fre) >= 0:
            if 40 - float(bw_num) >= 0:
                ulpower_mu = 0.7
                CarrierLeakage_mu = 0.8
            else:
                ulpower_mu = 1.4
                CarrierLeakage_mu = 1.5
        elif float(ul_fre) - 3000 > 0 and 4200 - float(ul_fre) >= 0:
            if 40 - float(bw_num) >= 0:
                ulpower_mu = 1
                CarrierLeakage_mu = 0.8
            else:
                ulpower_mu = 1.6
                CarrierLeakage_mu = 1.6
        else:
            if 20 - float(bw_num) >= 0:
                ulpower_mu = 1.3
                CarrierLeakage_mu = 1
            elif float(bw_num) - 20 > 0 and 40 - float(bw_num) >= 0:
                ulpower_mu = 1.5
                CarrierLeakage_mu = 1
            else:
                ulpower_mu = 1.6
                CarrierLeakage_mu = 1.6

        if p_exp != 'pmin':
            global_elements.NR_Pexp = format((float(p_exp) + (ulpower_mu + ulpower_mu + 1.7 + CarrierLeakage_mu) / 2), '.2f')
        else:
            if bw_num in ['5', '10', '15', '20']:
                pmin = '-40'
            elif bw_num == '25':
                pmin = '-39'
            elif bw_num == '30':
                pmin = '-38.2'
            elif bw_num == '40':
                pmin = '-37'
            elif bw_num == '50':
                pmin = '-36'
            elif bw_num == '60':
                pmin = '-35.2'
            elif bw_num == '80':
                pmin = '-34'
            elif bw_num == '90':
                pmin = '-33.5'
            else:
                pmin = '-33'
            global_elements.NR_Pexp = format((float(pmin) + (ulpower_mu + ulpower_mu + 1.7 + CarrierLeakage_mu) / 2), '.2f')

        return isChanged
    except Exception as e:
        global_elements.emitsingle.thread_exitSingle.emit('parmslisthandle_for_6_4_2_2 failed, Program abnormal exit! '
                                                          'Error: ' + e.__doc__)

def parmslisthandle_for_6_4_2_3(parmslist):
    try:
        # 判断是否 有 CHANNEL SCS BW 的变化，有变化返回True,用于判断是否要reset CU
        isChanged = False
        PexpisChanged = False
        if global_elements.NR_bw != parmslist[1]['value'] or global_elements.NR_ch != parmslist[2]['value'] or \
                global_elements.NR_SCS != parmslist[3]['value']:
            isChanged = True
        if global_elements.NR_Pexp_pre != parmslist[7]['value']:
            PexpisChanged = True

        global_elements.NR_bw = parmslist[1]['value']
        global_elements.NR_ch = parmslist[2]['value']
        global_elements.NR_SCS = parmslist[3]['value']
        global_elements.NR_testid = parmslist[4]['value']
        global_elements.NR_Modulation = parmslist[5]['value']
        global_elements.NR_RBAllocation = parmslist[6]['value']
        p_exp = parmslist[7]['value']
        global_elements.NR_Pexp_pre = parmslist[7]['value']

        if global_elements.dutActiveDict['xml']['DUTCONFIG']['powerclass'] == '2' and \
                global_elements.NR_band in ['n41_TDD', 'n77_TDD', 'n78_TDD', 'n79_TDD']:
            global_elements.NR_p_max = '26'
        else:
            global_elements.NR_p_max = '23'

        # 提取SCS信息
        scs_num = global_elements.NR_SCS
        scs_str = 'SCS_' + scs_num
        global_elements.NR_SCS_r = 'SCS_' + scs_num
        # 提取BW信息
        bw_num = global_elements.SCSBandwidthConfig_dict['xml'][global_elements.NR_band][scs_str][global_elements.NR_bw]
        global_elements.NR_bw_num = bw_num
        bw_str = 'BW_' + bw_num
        global_elements.NR_bw_r = 'NR_BW' + bw_num + 'MHz'

        global_elements.NR_ch_r = global_elements.ChannelConfig_dict['xml'][global_elements.NR_band][scs_str][bw_str]['UL'][
            global_elements.NR_ch]['CarrierCentreCh']
        global_elements.NR_testid_r = global_elements.NR_testid
        global_elements.NR_Modulation_r = global_elements.NR_Modulation

        if '256 QAM' in global_elements.NR_Modulation:
            table_str = 'MCS index table_256QAM: '
        else:
            table_str = 'MCS index table_64QAM: '

        if 'BPSK' in global_elements.NR_Modulation:
            mcs_index = global_elements.MCSindex_dict['xml']['UL']['DFT']['halfpi_BPSK'].split('_')[1]
        elif 'QPSK' in global_elements.NR_Modulation:
            mcs_index = global_elements.MCSindex_dict['xml']['UL']['DFT']['QPSK'].split('_')[1]
        elif '16 QAM' in global_elements.NR_Modulation:
            mcs_index = global_elements.MCSindex_dict['xml']['UL']['DFT']['QAM16'].split('_')[1]
        elif '64 QAM' in global_elements.NR_Modulation:
            mcs_index = global_elements.MCSindex_dict['xml']['UL']['DFT']['QAM64'].split('_')[1]
        else:
            mcs_index = global_elements.MCSindex_dict['xml']['UL']['DFT']['QAM256'].split('_')[1]
        global_elements.NR_MCSindex_r = table_str + mcs_index

        # RB
        rb_str = '_'.join(global_elements.NR_RBAllocation.split(' '))
        if 'DFT' in global_elements.NR_Modulation:
            wave_type_str = 'DFT_s'
        else:
            wave_type_str = 'CP'
        rb_config_str = global_elements.RBConfig_dict['xml'][bw_str][scs_str][wave_type_str][rb_str]
        global_elements.NR_RBAllocation_r = global_elements.NR_RBAllocation + ':' + rb_config_str

        # 波形
        if 'DFT' in global_elements.NR_Modulation:
            global_elements.NR_Waveform_r = 'DFT_s'
        else:
            global_elements.NR_Waveform_r = 'CP'

        # 换算P_exp
        ul_fre = reporthandle.NreftoFre(global_elements.NR_ch_r)
        if 3000 - float(ul_fre) >= 0:
            if 40 - float(bw_num) >= 0:
                ulpower_mu = 0.7
                CarrierLeakage_mu = 0.8
            else:
                ulpower_mu = 1.4
                CarrierLeakage_mu = 1.5
        elif float(ul_fre) - 3000 > 0 and 4200 - float(ul_fre) >= 0:
            if 40 - float(bw_num) >= 0:
                ulpower_mu = 1
                CarrierLeakage_mu = 0.8
            else:
                ulpower_mu = 1.6
                CarrierLeakage_mu = 1.6
        else:
            if 20 - float(bw_num) >= 0:
                ulpower_mu = 1.3
                CarrierLeakage_mu = 1
            elif float(bw_num) - 20 > 0 and 40 - float(bw_num) >= 0:
                ulpower_mu = 1.5
                CarrierLeakage_mu = 1
            else:
                ulpower_mu = 1.6
                CarrierLeakage_mu = 1.6

        if p_exp != 'pmin':
            global_elements.NR_Pexp = format((float(p_exp) + (ulpower_mu + ulpower_mu + 1.7 + CarrierLeakage_mu) / 2), '.2f')
        else:
            if bw_num in ['5', '10', '15', '20']:
                pmin = '-40'
            elif bw_num == '25':
                pmin = '-39'
            elif bw_num == '30':
                pmin = '-38.2'
            elif bw_num == '40':
                pmin = '-37'
            elif bw_num == '50':
                pmin = '-36'
            elif bw_num == '60':
                pmin = '-35.2'
            elif bw_num == '80':
                pmin = '-34'
            elif bw_num == '90':
                pmin = '-33.5'
            else:
                pmin = '-33'
            global_elements.NR_Pexp = format((float(pmin) + (ulpower_mu + ulpower_mu + 1.7 + CarrierLeakage_mu) / 2), '.2f')

        return isChanged, PexpisChanged
    except Exception as e:
        global_elements.emitsingle.thread_exitSingle.emit('parmslisthandle_for_6_4_2_3 failed, Program abnormal exit! '
                                                          'Error: ' + e.__doc__)

def parmslisthandle_for_6_5_1(parmslist):
    try:
        # 判断是否 有 CHANNEL SCS BW的变化，有变化返回True,用于判断是否要reset CU
        isChanged = False
        if global_elements.NR_bw != parmslist[1]['value'] or global_elements.NR_ch != parmslist[2]['value'] or \
                global_elements.NR_SCS != parmslist[3]['value']:
            isChanged = True

        global_elements.NR_bw = parmslist[1]['value']
        global_elements.NR_ch = parmslist[2]['value']
        global_elements.NR_SCS = parmslist[3]['value']
        global_elements.NR_testid = parmslist[4]['value']
        global_elements.NR_Modulation = parmslist[5]['value']
        global_elements.NR_RBAllocation = parmslist[6]['value']

        if global_elements.dutActiveDict['xml']['DUTCONFIG']['powerclass'] == '2' and \
                global_elements.NR_band in ['n41_TDD', 'n77_TDD', 'n78_TDD', 'n79_TDD']:
            global_elements.NR_p_max = '26'
        else:
            global_elements.NR_p_max = '23'

        # 提取SCS信息
        scs_num = global_elements.NR_SCS
        scs_str = 'SCS_' + scs_num
        global_elements.NR_SCS_r = 'SCS_' + scs_num
        # 提取BW信息
        bw_num = global_elements.NR_bw
        global_elements.NR_bw_num = bw_num
        bw_str = 'BW_' + bw_num
        global_elements.NR_bw_r = 'NR_BW' + bw_num + 'MHz'

        global_elements.NR_ch_r = global_elements.ChannelConfig_dict['xml'][global_elements.NR_band][scs_str][bw_str]['UL'][
            global_elements.NR_ch]['CarrierCentreCh']
        global_elements.NR_testid_r = global_elements.NR_testid
        global_elements.NR_Modulation_r = global_elements.NR_Modulation

        if '256 QAM' in global_elements.NR_Modulation:
            table_str = 'MCS index table_256QAM: '
        else:
            table_str = 'MCS index table_64QAM: '

        if 'BPSK' in global_elements.NR_Modulation:
            mcs_index = global_elements.MCSindex_dict['xml']['UL']['DFT']['halfpi_BPSK'].split('_')[1]
        elif 'QPSK' in global_elements.NR_Modulation:
            mcs_index = global_elements.MCSindex_dict['xml']['UL']['DFT']['QPSK'].split('_')[1]
        elif '16 QAM' in global_elements.NR_Modulation:
            mcs_index = global_elements.MCSindex_dict['xml']['UL']['DFT']['QAM16'].split('_')[1]
        elif '64 QAM' in global_elements.NR_Modulation:
            mcs_index = global_elements.MCSindex_dict['xml']['UL']['DFT']['QAM64'].split('_')[1]
        else:
            mcs_index = global_elements.MCSindex_dict['xml']['UL']['DFT']['QAM256'].split('_')[1]
        global_elements.NR_MCSindex_r = table_str + mcs_index

        # RB
        rb_str = '_'.join(global_elements.NR_RBAllocation.split(' '))
        if 'DFT' in global_elements.NR_Modulation:
            wave_type_str = 'DFT_s'
        else:
            wave_type_str = 'CP'
        rb_config_str = global_elements.RBConfig_dict['xml'][bw_str][scs_str][wave_type_str][rb_str]
        global_elements.NR_RBAllocation_r = global_elements.NR_RBAllocation + ':' + rb_config_str

        # 波形
        if 'DFT' in global_elements.NR_Modulation:
            global_elements.NR_Waveform_r = 'DFT_s'
        else:
            global_elements.NR_Waveform_r = 'CP'

        return isChanged
    except Exception as e:
        global_elements.emitsingle.thread_exitSingle.emit('parmslisthandle_for_6_5_1 failed, Program abnormal exit! '
                                                          'Error: ' + e.__doc__)

def parmslisthandle_for_7_3_2(parmslist):
    try:
        # 判断是否 有 CHANNEL SCS BW Testpoint的变化，有变化返回True,用于判断是否要reset CU
        isChanged = False
        if global_elements.NR_bw != parmslist[1]['value'] or global_elements.NR_ch != parmslist[2]['value'] or \
                global_elements.NR_SCS != parmslist[3]['value']:
            isChanged = True

        global_elements.NR_bw = parmslist[1]['value']
        global_elements.NR_ch = parmslist[2]['value']
        global_elements.NR_SCS = parmslist[3]['value']
        global_elements.NR_testid = parmslist[4]['value']
        global_elements.NR_Modulation = parmslist[5]['value']
        global_elements.NR_RBAllocation = parmslist[6]['value']

        if global_elements.dutActiveDict['xml']['DUTCONFIG']['powerclass'] == '2' and \
                global_elements.NR_band in ['n41_TDD', 'n77_TDD', 'n78_TDD', 'n79_TDD']:
            global_elements.NR_p_max = '26'
        else:
            global_elements.NR_p_max = '23'

        # 提取SCS信息
        scs_num = global_elements.NR_SCS
        scs_str = 'SCS_' + scs_num
        global_elements.NR_SCS_r = 'SCS_' + scs_num
        # 提取BW信息
        bw_num = global_elements.SCSBandwidthConfig_dict['xml'][global_elements.NR_band][scs_str][global_elements.NR_bw]
        global_elements.NR_bw_num = bw_num
        bw_str = 'BW_' + bw_num
        global_elements.NR_bw_r = 'NR_BW' + bw_num + 'MHz'

        global_elements.NR_ch_r = global_elements.ChannelConfig_dict['xml'][global_elements.NR_band][scs_str][bw_str]['UL'][
            global_elements.NR_ch]['CarrierCentreCh']
        global_elements.NR_dl_ch_r = global_elements.ChannelConfig_dict['xml'][global_elements.NR_band][scs_str][bw_str]['DL'][
            global_elements.NR_ch]['CarrierCentreCh']
        global_elements.NR_testid_r = global_elements.NR_testid
        global_elements.NR_Modulation_r = global_elements.NR_Modulation

        if '256 QAM' in global_elements.NR_Modulation:
            table_str = 'MCS index table_256QAM: '
        else:
            table_str = 'MCS index table_64QAM: '

        if 'BPSK' in global_elements.NR_Modulation:
            mcs_index = global_elements.MCSindex_dict['xml']['UL']['DFT']['halfpi_BPSK'].split('_')[1]
        elif 'QPSK' in global_elements.NR_Modulation:
            mcs_index = global_elements.MCSindex_dict['xml']['UL']['DFT']['QPSK'].split('_')[1]
        elif '16 QAM' in global_elements.NR_Modulation:
            mcs_index = global_elements.MCSindex_dict['xml']['UL']['DFT']['QAM16'].split('_')[1]
        elif '64 QAM' in global_elements.NR_Modulation:
            mcs_index = global_elements.MCSindex_dict['xml']['UL']['DFT']['QAM64'].split('_')[1]
        else:
            mcs_index = global_elements.MCSindex_dict['xml']['UL']['DFT']['QAM256'].split('_')[1]
        global_elements.NR_MCSindex_r = table_str + mcs_index

        # DL level
        global_elements.NR_DL_level = global_elements.DLlevel_dict['xml'][global_elements.NR_band][scs_str][bw_str]

        # RB
        rb_config_str = global_elements.UlRBConfig_dict['xml'][global_elements.NR_band][scs_str][bw_str]
        global_elements.NR_RBAllocation_r = global_elements.NR_RBAllocation + ':' + rb_config_str

        global_elements.NR_DlRBconfig = global_elements.DlRBConfig_dict['xml'][bw_str][scs_str]

        # 波形
        if 'DFT' in global_elements.NR_Modulation:
            global_elements.NR_Waveform_r = 'DFT_s'
        else:
            global_elements.NR_Waveform_r = 'CP'

        return isChanged
    except Exception as e:
        global_elements.emitsingle.thread_exitSingle.emit('parmslisthandle_for_7_3_2 failed, Program abnormal exit! '
                                                          'Error: ' + e.__doc__)

def parmslisthandle_for_7_3_2_c(parmslist):
    try:
        # 判断是否 有 CHANNEL SCS BW Testpoint的变化，有变化返回True,用于判断是否要reset CU
        isChanged = False
        if global_elements.NR_bw != parmslist[1]['value'] or global_elements.NR_ch != parmslist[2]['value'] or \
                global_elements.NR_SCS != parmslist[3]['value']:
            isChanged = True

        global_elements.NR_bw = parmslist[1]['value']
        global_elements.NR_ch = parmslist[2]['value']
        global_elements.NR_SCS = parmslist[3]['value']
        global_elements.NR_testid = parmslist[4]['value']
        global_elements.NR_Modulation = parmslist[5]['value']
        global_elements.NR_RBAllocation = parmslist[6]['value']

        if global_elements.dutActiveDict['xml']['DUTCONFIG']['powerclass'] == '2' and \
                global_elements.NR_band in ['n41_TDD', 'n77_TDD', 'n78_TDD', 'n79_TDD']:
            global_elements.NR_p_max = '26'
        else:
            global_elements.NR_p_max = '23'

        # 提取SCS信息
        scs_num = global_elements.NR_SCS
        scs_str = 'SCS_' + scs_num
        global_elements.NR_SCS_r = 'SCS_' + scs_num
        # 提取BW信息
        bw_num = global_elements.SCSBandwidthConfig_dict['xml'][global_elements.NR_band][scs_str][global_elements.NR_bw]
        global_elements.NR_bw_num = bw_num
        bw_str = 'BW_' + bw_num
        global_elements.NR_bw_r = 'NR_BW' + bw_num + 'MHz'

        global_elements.NR_ch_r = global_elements.ChannelConfig_dict['xml'][global_elements.NR_band][scs_str][bw_str]['UL'][
            global_elements.NR_ch]['CarrierCentreCh']
        global_elements.NR_dl_ch_r = global_elements.ChannelConfig_dict['xml'][global_elements.NR_band][scs_str][bw_str]['DL'][
            global_elements.NR_ch]['CarrierCentreCh']
        global_elements.NR_testid_r = global_elements.NR_testid
        global_elements.NR_Modulation_r = global_elements.NR_Modulation

        if '256 QAM' in global_elements.NR_Modulation:
            table_str = 'MCS index table_256QAM: '
        else:
            table_str = 'MCS index table_64QAM: '

        if 'BPSK' in global_elements.NR_Modulation:
            mcs_index = global_elements.MCSindex_dict['xml']['UL']['DFT']['halfpi_BPSK'].split('_')[1]
        elif 'QPSK' in global_elements.NR_Modulation:
            mcs_index = global_elements.MCSindex_dict['xml']['UL']['DFT']['QPSK'].split('_')[1]
        elif '16 QAM' in global_elements.NR_Modulation:
            mcs_index = global_elements.MCSindex_dict['xml']['UL']['DFT']['QAM16'].split('_')[1]
        elif '64 QAM' in global_elements.NR_Modulation:
            mcs_index = global_elements.MCSindex_dict['xml']['UL']['DFT']['QAM64'].split('_')[1]
        else:
            mcs_index = global_elements.MCSindex_dict['xml']['UL']['DFT']['QAM256'].split('_')[1]
        global_elements.NR_MCSindex_r = table_str + mcs_index

        # DL level
        global_elements.NR_DL_level = global_elements.DLlevel_dict['xml'][global_elements.NR_band][scs_str][bw_str]

        # RB
        rb_config_str = global_elements.UlRBConfig_dict['xml'][global_elements.NR_band][scs_str][bw_str]
        global_elements.NR_RBAllocation_r = global_elements.NR_RBAllocation + ':' + rb_config_str

        global_elements.NR_DlRBconfig = global_elements.DlRBConfig_dict['xml'][bw_str][scs_str]

        # 波形
        if 'DFT' in global_elements.NR_Modulation:
            global_elements.NR_Waveform_r = 'DFT_s'
        else:
            global_elements.NR_Waveform_r = 'CP'

        return isChanged
    except Exception as e:
        global_elements.emitsingle.thread_exitSingle.emit('parmslisthandle_for_7_3_2_c failed, Program abnormal exit! '
                                                          'Error: ' + e.__doc__)

def parmslisthandle_for_7_4(parmslist):
    try:
        # 判断是否 有 CHANNEL SCS BW Testpoint的变化，有变化返回True,用于判断是否要reset CU
        isChanged = False
        if global_elements.NR_bw != parmslist[1]['value'] or global_elements.NR_ch != parmslist[2]['value'] or \
                global_elements.NR_SCS != parmslist[3]['value']:
            isChanged = True

        global_elements.NR_bw = parmslist[1]['value']
        global_elements.NR_ch = parmslist[2]['value']
        global_elements.NR_SCS = parmslist[3]['value']
        global_elements.NR_testid = parmslist[4]['value']
        global_elements.NR_Modulation = parmslist[5]['value']
        global_elements.NR_DL_Modulation = parmslist[6]['value']
        global_elements.NR_RBAllocation = parmslist[7]['value']

        if global_elements.dutActiveDict['xml']['DUTCONFIG']['powerclass'] == '2' and \
                global_elements.NR_band in ['n41_TDD', 'n77_TDD', 'n78_TDD', 'n79_TDD']:
            global_elements.NR_p_max = '26'
        else:
            global_elements.NR_p_max = '23'

        # 提取SCS信息
        scs_num = global_elements.NR_SCS
        scs_str = 'SCS_' + scs_num
        global_elements.NR_SCS_r = 'SCS_' + scs_num
        # 提取BW信息
        bw_num = global_elements.SCSBandwidthConfig_dict['xml'][global_elements.NR_band][scs_str][global_elements.NR_bw]
        global_elements.NR_bw_num = bw_num
        bw_str = 'BW_' + bw_num
        global_elements.NR_bw_r = 'NR_BW' + bw_num + 'MHz'

        global_elements.NR_ch_r = global_elements.ChannelConfig_dict['xml'][global_elements.NR_band][scs_str][bw_str]['UL'][
            global_elements.NR_ch]['CarrierCentreCh']
        global_elements.NR_dl_ch_r = global_elements.ChannelConfig_dict['xml'][global_elements.NR_band][scs_str][bw_str]['DL'][
            global_elements.NR_ch]['CarrierCentreCh']
        global_elements.NR_testid_r = global_elements.NR_testid
        global_elements.NR_Modulation_r = global_elements.NR_Modulation

        # MCS Index
        if '256 QAM' in global_elements.NR_Modulation:
            ul_table_str = 'UL table_256QAM: '
        else:
            ul_table_str = 'UL table_64QAM: '
        if '256 QAM' in global_elements.NR_DL_Modulation:
            dl_table_str = 'DL table_256QAM: '
        else:
            dl_table_str = 'DL table_64QAM: '

        if 'BPSK' in global_elements.NR_Modulation:
            ul_mcs_index = global_elements.MCSindex_dict['xml']['UL']['DFT']['halfpi_BPSK'].split('_')[1]
        elif 'QPSK' in global_elements.NR_Modulation:
            ul_mcs_index = global_elements.MCSindex_dict['xml']['UL']['DFT']['QPSK'].split('_')[1]
        elif '16 QAM' in global_elements.NR_Modulation:
            ul_mcs_index = global_elements.MCSindex_dict['xml']['UL']['DFT']['QAM16'].split('_')[1]
        elif '64 QAM' in global_elements.NR_Modulation:
            ul_mcs_index = global_elements.MCSindex_dict['xml']['UL']['DFT']['QAM64'].split('_')[1]
        else:
            ul_mcs_index = global_elements.MCSindex_dict['xml']['UL']['DFT']['QAM256'].split('_')[1]

        if 'QPSK' in global_elements.NR_DL_Modulation:
            dl_mcs_index = global_elements.MCSindex_dict['xml']['DL']['QPSK'].split('_')[1]
        elif '64 QAM' in global_elements.NR_DL_Modulation:
            dl_mcs_index = global_elements.MCSindex_dict['xml']['DL']['QAM64'].split('_')[1]
        else:
            dl_mcs_index = global_elements.MCSindex_dict['xml']['DL']['QAM256'].split('_')[1]

        global_elements.NR_MCSindex_r = 'MCS Index:' + ul_table_str + ul_mcs_index + '; ' + dl_table_str + dl_mcs_index

        # DL level
        dl_fre = reporthandle.NreftoFre(global_elements.NR_dl_ch_r)
        if 3000 - float(dl_fre) >= 0:
            TT = 0.7
        else:
            TT = 1

        if float(bw_num) -20 <= 0:
            if '64 QAM' in global_elements.NR_DL_Modulation:
                dl_level = str(-25 - TT)
            else:
                dl_level = str(-27 - TT)
        elif float(bw_num) == '25':
            if '64 QAM' in global_elements.NR_DL_Modulation:
                dl_level = str(-24 - TT)
            else:
                dl_level = str(-26 - TT)
        elif float(bw_num) == '30':
            if '64 QAM' in global_elements.NR_DL_Modulation:
                dl_level = str(-23 - TT)
            else:
                dl_level = str(-25 - TT)
        elif float(bw_num) == '40':
            if '64 QAM' in global_elements.NR_DL_Modulation:
                dl_level = str(-22 - TT)
            else:
                dl_level = str(-24 - TT)
        elif float(bw_num) == '50':
            if '64 QAM' in global_elements.NR_DL_Modulation:
                dl_level = str(-21 - TT)
            else:
                dl_level = str(-23 - TT)
        else:
            if '64 QAM' in global_elements.NR_DL_Modulation:
                dl_level = str(-20 - TT)
            else:
                dl_level = str(-22 - TT)
        global_elements.NR_DL_level = dl_level

        # RB
        rb_config_str = global_elements.UlRBConfig_dict['xml'][global_elements.NR_band][scs_str][bw_str]
        global_elements.NR_RBAllocation_r = global_elements.NR_RBAllocation + ':' + rb_config_str

        global_elements.NR_DlRBconfig = global_elements.DlRBConfig_dict['xml'][bw_str][scs_str]

        # 波形
        if 'DFT' in global_elements.NR_Modulation:
            global_elements.NR_Waveform_r = 'DFT_s'
        else:
            global_elements.NR_Waveform_r = 'CP'

        return isChanged
    except Exception as e:
        global_elements.emitsingle.thread_exitSingle.emit('parmslisthandle_for_7_4 failed, Program abnormal exit! '
                                                          'Error: ' + e.__doc__)

def parmslisthandle_for_6_2b_1_3(parmslist):
    try:
        # 判断是否 有 CHANNEL SCS BW的变化，有变化返回True,用于判断是否要reset CU
        isChanged = False
        if global_elements.NR_bw != parmslist[1]['value'] or global_elements.NR_ch != parmslist[2]['value'] or \
                global_elements.NR_SCS != parmslist[3]['value'] or global_elements.NR_testid != parmslist[4]['value'] or \
                global_elements.NR_Modulation != parmslist[5]['value'] or global_elements.NR_RBAllocation != parmslist[6]['value']:
            isChanged = True

        global_elements.NR_bw = parmslist[1]['value']
        global_elements.NR_ch = parmslist[2]['value']
        global_elements.NR_SCS = parmslist[3]['value']
        global_elements.NR_testid = parmslist[4]['value']
        global_elements.NR_Modulation = parmslist[5]['value']
        global_elements.NR_RBAllocation = parmslist[6]['value']

        if global_elements.dutActiveDict['xml']['DUTCONFIG']['powerclass'] == '2' and \
                global_elements.NR_band in ['n41_TDD', 'n77_TDD', 'n78_TDD', 'n79_TDD']:
            global_elements.NR_p_max = '26'
        else:
            global_elements.NR_p_max = '23'


        reg = re.compile(r"(?<=n)\d+")
        match_nr = reg.search(global_elements.NR_band.split('_')[2])
        lte_band_num = global_elements.NR_band.split('_')[1][:-1]
        nr_band_num = match_nr.group(0)
        # 获取双工方式
        global_elements.NSA_LTE_DuplexMode = global_elements.getLTEDuplexMode(lte_band_num)
        global_elements.NSA_NR_DuplexMode = global_elements.getNRDuplexMode(nr_band_num)
        # 提取Band
        global_elements.NSA_LTE_band = 'b' + lte_band_num
        global_elements.NSA_NR_band = 'n' + nr_band_num + '_' + global_elements.NSA_NR_DuplexMode
        # 提取SCS信息
        scs_num = global_elements.NR_SCS
        scs_str = 'SCS_' + scs_num
        global_elements.NR_SCS_r = 'SCS_' + scs_num
        # 提取BW信息
        LTE_bw = global_elements.NR_bw.split(',')[0]
        NR_bw = global_elements.NR_bw.split(',')[1]
        if LTE_bw != '5':
            if LTE_bw == 'Low':
                global_elements.NSA_LTE_bw = global_elements.LTEBW_dict['xml'][global_elements.NSA_LTE_band]['BW'].split(',')[0]
            elif LTE_bw == 'High':
                global_elements.NSA_LTE_bw = \
                global_elements.LTEBW_dict['xml'][global_elements.NSA_LTE_band]['BW'].split(',')[-1]
        else:
            global_elements.NSA_LTE_bw = '5'
        lte_bw_str = 'BW_' + global_elements.NSA_LTE_bw
        global_elements.NSA_LTE_bw_r = global_elements.NSA_LTE_bw + 'MHz'

        global_elements.NSA_NR_bw = global_elements.SCSBandwidthConfig_dict['xml'][global_elements.NSA_NR_band][scs_str][NR_bw]
        nr_bw_str = 'BW_' + global_elements.NSA_NR_bw
        global_elements.NSA_NR_bw_r = global_elements.NSA_NR_bw + 'MHz'
        # 获取channel
        LTE_ch = global_elements.NR_ch.split(',')[0]
        NR_ch = global_elements.NR_ch.split(',')[1]
        global_elements.NSA_NR_channel = global_elements.ChannelConfig_dict['xml'][global_elements.NSA_NR_band][scs_str][nr_bw_str]['UL'][NR_ch]['CarrierCentreCh']
        global_elements.NSA_NR_ULFreq = global_elements.ChannelConfig_dict['xml'][global_elements.NSA_NR_band][scs_str][nr_bw_str]['UL'][NR_ch]['CarrierCentreFre']
        global_elements.NSA_NR_DLchannel = global_elements.ChannelConfig_dict['xml'][global_elements.NSA_NR_band][scs_str][nr_bw_str]['DL'][NR_ch]['CarrierCentreCh']
        global_elements.NSA_NR_DLFreq = global_elements.ChannelConfig_dict['xml'][global_elements.NSA_NR_band][scs_str][nr_bw_str]['DL'][NR_ch]['CarrierCentreFre']
        global_elements.NSA_LTE_ULchannel = global_elements.LTEChannel_dict['xml'][global_elements.NSA_LTE_band][lte_bw_str][LTE_ch]['UL']['channel']
        global_elements.NSA_LTE_ULFreq = global_elements.LTEChannel_dict['xml'][global_elements.NSA_LTE_band][lte_bw_str][LTE_ch]['UL']['Freq']
        global_elements.NSA_LTE_DLchannel = global_elements.LTEChannel_dict['xml'][global_elements.NSA_LTE_band][lte_bw_str][LTE_ch]['DL']['channel']
        global_elements.NSA_LTE_DLFreq = global_elements.LTEChannel_dict['xml'][global_elements.NSA_LTE_band][lte_bw_str][LTE_ch]['DL']['Freq']

        global_elements.NR_testid_r = global_elements.NR_testid
        global_elements.NSA_LTE_modulation = global_elements.NR_Modulation.split(',')[0]
        global_elements.NSA_NR_modulation = global_elements.NR_Modulation.split(',')[1]

        if global_elements.NSA_NR_modulation != 'NA':
            if '256 QAM' in global_elements.NR_Modulation:
                table_str = 'MCS index table_256QAM: '
            else:
                table_str = 'MCS index table_64QAM: '

            if 'BPSK' in global_elements.NR_Modulation:
                mcs_index = global_elements.MCSindex_dict['xml']['UL']['DFT']['halfpi_BPSK'].split('_')[1]
            elif 'QPSK' in global_elements.NR_Modulation:
                mcs_index = global_elements.MCSindex_dict['xml']['UL']['DFT']['QPSK'].split('_')[1]
            elif '16 QAM' in global_elements.NR_Modulation:
                mcs_index = global_elements.MCSindex_dict['xml']['UL']['DFT']['QAM16'].split('_')[1]
            elif '64 QAM' in global_elements.NR_Modulation:
                mcs_index = global_elements.MCSindex_dict['xml']['UL']['DFT']['QAM64'].split('_')[1]
            else:
                mcs_index = global_elements.MCSindex_dict['xml']['UL']['DFT']['QAM256'].split('_')[1]
            global_elements.NR_MCSindex_r = table_str + mcs_index
        else:
            global_elements.NR_MCSindex_r = 'NA'

        # RB
        lte_rb = global_elements.NR_RBAllocation.split(',')[0]
        nr_rb = global_elements.NR_RBAllocation.split(',')[1]
        if lte_rb != 'NA':
            lte_rb_str = '_'.join(lte_rb.split(' '))
            if lte_rb_str =='1RB_Left':
                lte_rb_str = 'oneRB_Left'
            elif lte_rb_str == '1RB_Right':
                lte_rb_str = 'oneRB_Right'
            global_elements.NSA_LTE_rb = global_elements.LTERBConfig_dict['xml'][lte_bw_str][lte_rb_str]
            global_elements.NSA_LTE_rb_r = lte_rb + ':' + global_elements.NSA_LTE_rb
        else:
            global_elements.NSA_LTE_rb = 'NA'
            global_elements.NSA_LTE_rb_r = 'NA'
        if nr_rb != 'NA':
            nr_rb_str = '_'.join(nr_rb.split(' '))
            if 'DFT' in global_elements.NSA_NR_modulation:
                wave_type_str = 'DFT_s'
            else:
                wave_type_str = 'CP'
            global_elements.NSA_NR_rb = global_elements.RBConfig_dict['xml'][nr_bw_str][scs_str][wave_type_str][nr_rb_str]
            global_elements.NSA_NR_rb_r = nr_rb + ':' + global_elements.NSA_NR_rb
        else:
            global_elements.NSA_NR_rb = 'NA'
            global_elements.NSA_NR_rb_r = 'NA'

        # 波形
        if global_elements.NSA_NR_modulation != 'NA':
            if 'DFT' in global_elements.NR_Modulation:
                global_elements.NR_Waveform_r = 'DFT_s'
            else:
                global_elements.NR_Waveform_r = 'CP'
        else:
            global_elements.NR_Waveform_r = 'NA'

        return isChanged
    except Exception as e:
        global_elements.emitsingle.thread_exitSingle.emit('parmslisthandle_for_6_2b_1_3 failed, Program abnormal exit! '
                                                          'Error: ' + e.__doc__)
