#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2021/1/21 9:09
# @Author  : Feng Zhaohui
# @Site    : 
# @File    : NR_NSA.py
# @Software: PyCharm

import global_elements
import time
import parmslisthandle
import reporthandle
import testseq_handle

def UEMaximumOutputPowerforInterBandENDCwithinFR1_6_2B_1_3(parms_list, connectState):
    global_elements.NR_remark_r = ''
    global_elements.test_item_r = ''
    if parms_list[0]['value'] == 'True':
        state = connectState   # 接收传入的DUT连接状态
        # 判断是否有CHANNEL BW SCS的参数变化，如果有，Reset CU
        ischanged = parmslisthandle.parmslisthandle_for_6_2b_1_3(parms_list)
        if ischanged:
            # 如果有CHANNEL BW SCS的参数变化，清空主界面结果图表
            # global_elements.emitsingle.resultChartclear.emit()
            # 如果有CHANNEL BW SCS的参数变化，重置图表参数
            testseq_handle.chartResutlClear()
            # 如果有CHANNEL BW SCS的参数变化，重置CU 和DUT
            state = global_elements.CU_intance.reSetCU_and_reConnectDUT_NSA()

        global_elements.emitsingle.stateupdataSingle.emit(global_elements.NR_band +
                                                          ' ' + global_elements.test_case_name
                                                          + '  BW:' + global_elements.NR_bw +
                                                          '  Channel:' + global_elements.NR_ch +
                                                          '  SCS:' + global_elements.NR_SCS +
                                                          '  Test Id:' + global_elements.NR_testid)

        nr_ul_fre = reporthandle.NreftoFre(global_elements.NSA_NR_channel)
        lte_ul_fre = global_elements.NSA_LTE_ULFreq
        if int(global_elements.NSA_NR_bw) <= 40 and float(nr_ul_fre) <= 3000:
            TT_NR = 0.7
        else:
            TT_NR = 1
        if float(lte_ul_fre) <= 3000:
            TT_LTE = 0.7
        else:
            TT_LTE = 0.7

        if int(global_elements.NR_testid) in range(1, 7) or int(global_elements.NR_testid) in range(10, 16):
            lowlimit = format((20 - TT_NR), '.1f')
            highlimit = format((25 + TT_NR), '.1f')
        else:
            lowlimit = format((20 - TT_LTE), '.1f')
            highlimit = format((25 + TT_LTE), '.1f')


        if state:
            # 配置Meas 参数
            global_elements.CU_intance.nsa_MeasParmsSetingfor6_2b_1_3()
            time.sleep(2)

            # 配置完参数后确认是否还是正常连接
            state = global_elements.CU_intance.checkConnectState()
            if state:
                # 开始测试并取值
                lte_power_value, nr_power_value = global_elements.CU_intance.getValue_6_2b_1_3(int(global_elements.NR_testid))
                total_power = global_elements.dBmplus(lte_power_value, nr_power_value)
                if int(global_elements.NR_testid) in range(1, 7):
                    global_elements.test_item_r = 'Maximum Output Power: Overall'
                    global_elements.emitsingle.stateupdataSingle.emit(
                        'Maximum Output Power: Overall  ' + total_power + 'dBm')
                    reporthandle.Reporttool(total_power, lowlimit, highlimit, 'dBm')
                    global_elements.test_item_r = 'Maximum Output Power: Overall:LTE'
                    global_elements.emitsingle.stateupdataSingle.emit(
                        'Maximum Output Power: Overall:LTE  ' + lte_power_value + 'dBm')
                    reporthandle.Reporttool(lte_power_value, 'None', 'None', 'dBm')
                    global_elements.test_item_r = 'Maximum Output Power: Overall:NR'
                    global_elements.emitsingle.stateupdataSingle.emit(
                        'Maximum Output Power: Overall:NR  ' + nr_power_value + 'dBm')
                    reporthandle.Reporttool(nr_power_value, 'None', 'None', 'dBm')
                elif int(global_elements.NR_testid) in [7, 8, 9]:
                    global_elements.test_item_r = 'Maximum Output Power: LTE'
                    global_elements.emitsingle.stateupdataSingle.emit(
                        'Maximum Output Power:LTE  ' + lte_power_value + 'dBm')
                    reporthandle.Reporttool(lte_power_value, lowlimit, highlimit, 'dBm')
                elif int(global_elements.NR_testid) in range(10, 16):
                    global_elements.test_item_r = 'Maximum Output Power: NR'
                    global_elements.emitsingle.stateupdataSingle.emit(
                        'Maximum Output Power: NR  ' + nr_power_value + 'dBm')
                    reporthandle.Reporttool(nr_power_value, lowlimit, highlimit, 'dBm')

            else:
                global_elements.NR_remark_r = 'DUT Connect timeout!'
                lte_power_value = '-999'
                nr_power_value = '-999'
                total_power = global_elements.dBmplus(lte_power_value, nr_power_value)
                if int(global_elements.NR_testid) in range(1, 7):
                    global_elements.test_item_r = 'Maximum Output Power: Overall'
                    global_elements.emitsingle.stateupdataSingle.emit(
                        'Maximum Output Power: Overall  ' + total_power + 'dBm')
                    reporthandle.Reporttool(total_power, lowlimit, highlimit, 'dBm')
                    global_elements.test_item_r = 'Maximum Output Power: Overall:LTE'
                    global_elements.emitsingle.stateupdataSingle.emit(
                        'Maximum Output Power: Overall:LTE  ' + lte_power_value + 'dBm')
                    reporthandle.Reporttool(lte_power_value, 'None', 'None', 'dBm')
                    global_elements.test_item_r = 'Maximum Output Power: Overall:NR'
                    global_elements.emitsingle.stateupdataSingle.emit(
                        'Maximum Output Power: Overall:NR  ' + nr_power_value + 'dBm')
                    reporthandle.Reporttool(nr_power_value, 'None', 'None', 'dBm')
                elif int(global_elements.NR_testid) in [7, 8, 9]:
                    global_elements.test_item_r = 'Maximum Output Power: LTE'
                    global_elements.emitsingle.stateupdataSingle.emit(
                        'Maximum Output Power:LTE  ' + lte_power_value + 'dBm')
                    reporthandle.Reporttool(lte_power_value, lowlimit, highlimit, 'dBm')
                elif int(global_elements.NR_testid) in range(10, 16):
                    global_elements.test_item_r = 'Maximum Output Power: NR'
                    global_elements.emitsingle.stateupdataSingle.emit(
                        'Maximum Output Power: NR  ' + nr_power_value + 'dBm')
                    reporthandle.Reporttool(nr_power_value, lowlimit, highlimit, 'dBm')
                global_elements.emitsingle.stateupdataSingle.emit('DUT Connect timeout!')
        else:
            global_elements.NR_remark_r = 'DUT Connect timeout!'
            lte_power_value = '-999'
            nr_power_value = '-999'
            total_power = global_elements.dBmplus(lte_power_value, nr_power_value)
            if int(global_elements.NR_testid) in range(1, 7):
                global_elements.test_item_r = 'Maximum Output Power: Overall'
                global_elements.emitsingle.stateupdataSingle.emit(
                    'Maximum Output Power: Overall  ' + total_power + 'dBm')
                reporthandle.Reporttool(total_power, lowlimit, highlimit, 'dBm')
                global_elements.test_item_r = 'Maximum Output Power: Overall:LTE'
                global_elements.emitsingle.stateupdataSingle.emit(
                    'Maximum Output Power: Overall:LTE  ' + lte_power_value + 'dBm')
                reporthandle.Reporttool(lte_power_value, 'None', 'None', 'dBm')
                global_elements.test_item_r = 'Maximum Output Power: Overall:NR'
                global_elements.emitsingle.stateupdataSingle.emit(
                    'Maximum Output Power: Overall:NR  ' + nr_power_value + 'dBm')
                reporthandle.Reporttool(nr_power_value, 'None', 'None', 'dBm')
            elif int(global_elements.NR_testid) in [7, 8, 9]:
                global_elements.test_item_r = 'Maximum Output Power: LTE'
                global_elements.emitsingle.stateupdataSingle.emit(
                    'Maximum Output Power:LTE  ' + lte_power_value + 'dBm')
                reporthandle.Reporttool(lte_power_value, lowlimit, highlimit, 'dBm')
            elif int(global_elements.NR_testid) in range(10, 16):
                global_elements.test_item_r = 'Maximum Output Power: NR'
                global_elements.emitsingle.stateupdataSingle.emit(
                    'Maximum Output Power: NR  ' + nr_power_value + 'dBm')
                reporthandle.Reporttool(nr_power_value, lowlimit, highlimit, 'dBm')
            global_elements.emitsingle.stateupdataSingle.emit('DUT Connect timeout!')

        # 更新图表参数
        global_elements.maxOutputPowerResutl.extend([float(total_power), float(lte_power_value), float(nr_power_value)])
        global_elements.maxOutputPowerLow.append(float(lowlimit))
        global_elements.maxOutputPowerhigh.append(float(highlimit))
        global_elements.maxOutputPowerTestid.append(global_elements.NR_testid)
        global_elements.emitsingle.nsa6_2b_1_3ChartUpdata.emit([global_elements.maxOutputPowerResutl,
                                                                   global_elements.maxOutputPowerLow,
                                                                   global_elements.maxOutputPowerhigh,
                                                                   global_elements.maxOutputPowerTestid])
        time.sleep(2)  # 等待Chart更新完再继续，避免global参数已更新到下一步的内容
        # 更新进度条
        global_elements.finished_step += 1
        process_rate = format(global_elements.finished_step * 100 / global_elements.total_step, '.2f')
        global_elements.emitsingle.process_rateupdataSingle.emit(process_rate)