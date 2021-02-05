#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2020/11/23 14:01
# @Author  : Feng Zhaohui
# @Site    : 
# @File    : NR_SA.py
# @Software: PyCharm

import global_elements
import time
import parmslisthandle
import reporthandle
import testseq_handle


def UEmaximumoutputpower6_2_1(parms_list, connectState):
    global_elements.NR_remark_r = ''
    global_elements.test_item_r = ''
    if parms_list[0]['value'] == 'True':
        state = connectState   # 接收传入的DUT连接状态
        # 判断是否有CHANNEL BW SCS的参数变化，如果有，Reset CU
        ischanged = parmslisthandle.parmslisthandle(parms_list)
        if ischanged:
            # 如果有CHANNEL BW SCS的参数变化，清空主界面结果图表
            # global_elements.emitsingle.resultChartclear.emit()
            # 如果有CHANNEL BW SCS的参数变化，重置图表参数
            testseq_handle.chartResutlClear()
            # 如果有CHANNEL BW SCS的参数变化，重置CU 和DUT
            state = global_elements.CU_intance.reSetCU_and_reConnectDUT()

        global_elements.emitsingle.stateupdataSingle.emit(global_elements.NR_band +
                                                          ' ' + global_elements.test_case_name
                                                          + '  BW:' + global_elements.NR_bw +
                                                          '  Channel:' + global_elements.NR_ch +
                                                          '  SCS:' + global_elements.NR_SCS +
                                                          '  Test Id:' + global_elements.NR_testid)

        ul_fre = reporthandle.NreftoFre(global_elements.NR_ch_r)
        if int(global_elements.NR_bw_num) <= 40:
            if float(ul_fre) <= 3000:
                TT = 0.7
            elif 3000 < float(ul_fre) <= 6000:
                TT = 1
        else:
            TT = 1

        if global_elements.dutActiveDict['xml']['DUTCONFIG']['powerclass'] == '2' and (
                'n41' in global_elements.NR_band or 'n77' in global_elements.NR_band or 'n78' in global_elements.NR_band or 'n79' in global_elements.NR_band):
            highlimit = str(28 + TT)
            lowlimit = str(23 - TT)
        else:
            if 'n28' in global_elements.NR_band:
                highlimit = '25'
                lowlimit = '20.5'
            elif 'n71' in global_elements.NR_band or 'n83' in global_elements.NR_band:
                highlimit = str(25 + TT)
                lowlimit = str(20.5 - TT)
            elif 'n77' in global_elements.NR_band or 'n78' in global_elements.NR_band or 'n79' in global_elements.NR_band:
                highlimit = str(25 + TT)
                lowlimit = str(20 - TT)
            else:
                highlimit = str(25 + TT)
                lowlimit = str(21 - TT)

        if state:
            # 配置Meas 参数
            global_elements.CU_intance.MeasParmsSetingfor6_2_1()
            time.sleep(2)

            # 配置完参数后确认是否还是正常连接
            state = global_elements.CU_intance.checkConnectState()
            if state:
                # 开始测试并取值
                power_value = global_elements.CU_intance.getValue_6_2_1()
                global_elements.emitsingle.stateupdataSingle.emit('Power Value: ' + power_value)
                reporthandle.Reporttool(power_value, lowlimit, highlimit, 'dBm')
            else:
                global_elements.NR_remark_r = 'DUT Connect timeout!'
                power_value = '-999'
                reporthandle.Reporttool(power_value, lowlimit, highlimit, 'dBm')
                global_elements.emitsingle.stateupdataSingle.emit('DUT Connect timeout!')
        else:
            global_elements.NR_remark_r = 'DUT Connect timeout!'
            power_value = '-999'
            reporthandle.Reporttool(power_value, lowlimit, highlimit, 'dBm')
            global_elements.emitsingle.stateupdataSingle.emit('DUT Connect timeout!')

        # 更新图表参数
        global_elements.maxOutputPowerResutl.append(float(power_value))
        global_elements.maxOutputPowerLow.append(float(lowlimit))
        global_elements.maxOutputPowerhigh.append(float(highlimit))
        global_elements.maxOutputPowerTestid.append(global_elements.NR_testid)
        global_elements.emitsingle.maxOutputPowerChartUpdata.emit([global_elements.maxOutputPowerResutl,
                                                                   global_elements.maxOutputPowerLow,
                                                                   global_elements.maxOutputPowerhigh,
                                                                   global_elements.maxOutputPowerTestid])
        time.sleep(2)  # 等待Chart更新完再继续，避免global参数已更新到下一步的内容
        # 更新进度条
        global_elements.finished_step += 1
        process_rate = format(global_elements.finished_step * 100 / global_elements.total_step, '.2f')
        global_elements.emitsingle.process_rateupdataSingle.emit(process_rate)


def UEmaximumoutputpowerreduction6_2_2(parms_list, connectState):
    global_elements.NR_remark_r = ''
    global_elements.test_item_r = ''
    if parms_list[0]['value'] == 'True':
        state = connectState  # 接收传入的DUT连接状态
        # 判断是否有CHANNEL BW SCS的参数变化，如果有，Reset CU
        ischanged = parmslisthandle.parmslisthandle(parms_list)
        if ischanged:
            # 如果有CHANNEL BW SCS的参数变化，清空主界面结果图表
            # global_elements.emitsingle.resultChartclear.emit()
            # 如果有CHANNEL BW SCS的参数变化，重置图表参数
            testseq_handle.chartResutlClear()
            # 如果有CHANNEL BW SCS的参数变化，重置CU 和DUT
            state = global_elements.CU_intance.reSetCU_and_reConnectDUT()

        global_elements.emitsingle.stateupdataSingle.emit(global_elements.NR_band +
                                                          ' ' + global_elements.test_case_name
                                                          + '  BW:' + global_elements.NR_bw +
                                                          '  Channel:' + global_elements.NR_ch +
                                                          '  SCS:' + global_elements.NR_SCS +
                                                          '  Test Id:' + global_elements.NR_testid)

        ul_fre = reporthandle.NreftoFre(global_elements.NR_ch_r)
        if int(global_elements.NR_bw_num) <= 40:
            if float(ul_fre) <= 3000:
                TT = 0.7
            elif 3000 < float(ul_fre) <= 6000:
                TT = 1
        else:
            TT = 1

        # Table 6.2.2.5-1: UE Power Class test requirements(for Bands n1, n2, n3, n5, n7, n8, n12, n20, n25, n34, n38, n39, n40, n41, n50, n51, n65, n66, n70,
        # n74, n80, n81, n82, n84, n86) for Power Class 3 (contiguous allocation)
        lowlimit_list_1 = [23.8, 20.5, 20.5, 22.8, 21.0, 20.5, 20.5, 20.5, 21.0, 20.0, 20.0, 20.0, 20.0, 19.0, 19.0, 19.0,
                         18.0, 18.0, 18.0, 14.5, 14.5, 14.5, 19.5, 17.5, 17.5, 17.5, 19.0, 17.5, 17.5, 17.5, 16.0, 16.0,
                         16.0, 11.5, 11.5, 11.5]
        highlimit_list_1 = [28.0, 28.0, 28.0, 28.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0,
                            25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0,
                            25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0]
        # Table 6.2.2.5-2: UE Power Class test requirements(for Bands n28, n71, n83) for Power Class 3
        # (contiguous allocation)
        lowlimit_list_2 = ['None', 'None', 'None', 'None', 20.5, 20.0, 20.0, 20.0, 20.5, 19.5, 19.5, 19.5, 19.5, 18.5, 18.5, 18.5, 18.0, 18.0, 18.0,
                           14.5, 14.5, 14.5, 19.0, 17.5, 17.5, 17.5, 18.5, 17.5, 17.5, 17.5, 16.0, 16.0, 16.0, 11.5,
                           11.5, 11.5]
        highlimit_list_2 = ['None', 'None', 'None', 'None', 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0,
                            25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0,
                            25.0, 25.0]
        # Table 6.2.2.5-3: UE Power Class test requirements (for Bands n77, n78, n79) for Power Class 3
        # (contiguous allocation)
        lowlimit_list_3 = [22.8, 19.5, 19.5, 21.8, 20.0, 19.5, 19.5, 19.5, 20.0, 19.0, 19.0, 19.0, 19.0, 18.0, 18.0,
                           18.0, 17.5, 17.5, 17.5, 14.5, 14.5, 14.5, 18.5, 17.0, 17.0, 17.0, 18.0, 17.0, 17.0, 17.0,
                           16.0, 16.0, 16.0, 11.5, 11.5, 11.5]
        highlimit_list_3 = [28.0, 28.0, 28.0, 28.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0,
                            25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0,
                            25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0]
        # Table 6.2.2.5-4: UE Power Class test requirements (for Bands n41, n77, n78, n79) for Power Class 2 (contiguous allocation)
        lowlimit_list_4 = [23.0, 19.5, 19.5, 22.5, 23.0, 19.5, 19.5, 22.0, 22.0, 19.5, 19.5, 21.0, 19.5, 19.5, 20.5,
                           18.5, 18.5, 18.5, 21.5, 19.5, 19.5, 20.0, 21.0, 19.5, 19.5, 20.0, 19.5, 19.5, 19.5, 16.0,
                           16.0, 16.0]
        highlimit_list_4 = [28.0, 28.0, 28.0, 28.0, 28.0, 28.0, 28.0, 28.0, 28.0, 28.0, 28.0, 28.0, 28.0, 28.0, 28.0,
                            28.0, 28.0, 28.0, 28.0, 28.0, 28.0, 28.0, 28.0, 28.0, 28.0, 28.0, 28.0, 28.0, 28.0, 28.0,
                            28.0, 28.0,]
        testId = int(global_elements.NR_testid) - 1
        if global_elements.dutActiveDict['xml']['DUTCONFIG']['powerclass'] == '2' and (
                'n41' in global_elements.NR_band or 'n77' in global_elements.NR_band or 'n78' in global_elements.NR_band or 'n79' in global_elements.NR_band):
            highlimit = str(highlimit_list_4[testId] + TT)
            lowlimit = str(lowlimit_list_4[testId] - TT)
        elif global_elements.dutActiveDict['xml']['DUTCONFIG']['powerclass'] == '3' and (global_elements.NR_band in [
            'n1_20_FDD', 'n1_40_FDD', 'n2_FDD', 'n3_FDD', 'n5_FDD', 'n7_FDD', 'n8_FDD', 'n12_FDD', 'n20_FDD', 'n25_FDD',
        'n34_TDD', 'n38_TDD', 'n39_TDD', 'n40_TDD', 'n41_TDD', 'n50_TDD', 'n51_TDD', 'n65_FDD', 'n66_FDD', 'n70_FDD',
        'n74_FDD', 'n80_SUL', 'n81_SUL', 'n82_SUL', 'n84_SUL', 'n86_SUL']):
            highlimit = str(highlimit_list_1[testId] + TT)
            lowlimit = str(lowlimit_list_1[testId] - TT)
        elif global_elements.dutActiveDict['xml']['DUTCONFIG']['powerclass'] == '3' and (global_elements.NR_band in [
            'n28_FDD', 'n71_FDD', 'n83_SUL']):
            if highlimit_list_2[testId] != 'None':
                highlimit = str(highlimit_list_2[testId] + TT)
                lowlimit = str(lowlimit_list_2[testId] - TT)
            else:
                highlimit = 'None'
                lowlimit = 'None'
        elif global_elements.dutActiveDict['xml']['DUTCONFIG']['powerclass'] == '3' and (global_elements.NR_band in [
            'n77_TDD', 'n78_TDD', 'n79_TDD']):
            highlimit = str(highlimit_list_3[testId] + TT)
            lowlimit = str(lowlimit_list_3[testId] - TT)

        if state:
            # 配置Meas 参数
            global_elements.CU_intance.MeasParmsSetingfor6_2_2()
            time.sleep(2)

            # 配置完参数后确认是否还是正常连接
            state = global_elements.CU_intance.checkConnectState()
            if state:
                # 开始测试并取值
                power_value = global_elements.CU_intance.getValue_6_2_2()
                global_elements.emitsingle.stateupdataSingle.emit('Power Value: ' + power_value)
                reporthandle.Reporttool(power_value, lowlimit, highlimit, 'dBm')
            else:
                global_elements.NR_remark_r = 'DUT Connect timeout!'
                power_value = '-999'
                reporthandle.Reporttool(power_value, lowlimit, highlimit, 'dBm')
                global_elements.emitsingle.stateupdataSingle.emit('DUT Connect timeout!')
        else:
            global_elements.NR_remark_r = 'DUT Connect timeout!'
            power_value = '-999'
            reporthandle.Reporttool(power_value, lowlimit, highlimit, 'dBm')
            global_elements.emitsingle.stateupdataSingle.emit('DUT Connect timeout!')

        # 更新图表参数
        global_elements.maxOutputPowerResutl.append(float(power_value))
        global_elements.maxOutputPowerLow.append(float(lowlimit))
        global_elements.maxOutputPowerhigh.append(float(highlimit))
        global_elements.maxOutputPowerTestid.append(global_elements.NR_testid)
        global_elements.emitsingle.maxOutputPowerChartUpdata.emit([global_elements.maxOutputPowerResutl,
                                                                   global_elements.maxOutputPowerLow,
                                                                   global_elements.maxOutputPowerhigh,
                                                                   global_elements.maxOutputPowerTestid])
        time.sleep(2)  # 等待Chart更新完再继续，避免global参数已更新到下一步的内容
        # 更新进度条
        global_elements.finished_step += 1
        process_rate = format(global_elements.finished_step * 100 / global_elements.total_step, '.2f')
        global_elements.emitsingle.process_rateupdataSingle.emit(process_rate)

def Configuredtransmittedpower6_2_4(parms_list, connectState):
    global_elements.NR_remark_r = ''
    global_elements.test_item_r = ''
    if parms_list[0]['value'] == 'True':
        state = connectState  # 接收传入的DUT连接状态
        ischanged = parmslisthandle.parmslisthandle_for_6_2_4(parms_list)
        if ischanged:
            # 如果有CHANNEL BW SCS的参数变化，清空主界面结果图表
            # global_elements.emitsingle.resultChartclear.emit()
            # 如果有CHANNEL BW SCS的参数变化，重置图表参数
            testseq_handle.chartResutlClear()


        state = global_elements.CU_intance.reSetCU_and_reConnectDUT()

        global_elements.emitsingle.stateupdataSingle.emit(global_elements.NR_band +
                                                          ' ' + global_elements.test_case_name
                                                          + ' BW:' + global_elements.NR_bw +
                                                          ' Channel:' + global_elements.NR_ch +
                                                          ' SCS:' + global_elements.NR_SCS +
                                                          ' Test Id:' + global_elements.NR_testid +
                                                          ' TP:' + global_elements.NR_TestPoint)

        ul_fre = reporthandle.NreftoFre(global_elements.NR_ch_r)
        if int(global_elements.NR_bw_num) <= 40:
            if float(ul_fre) <= 3000:
                TT = 0.7
            elif 3000 < float(ul_fre) <= 6000:
                TT = 1
        else:
            TT = 1

        if global_elements.NR_TestPoint == '1':
            highlimit = str(-3 + TT)
            lowlimit = str(-17 -TT)
        elif global_elements.NR_TestPoint == '2':
            highlimit = str(16 + TT)
            lowlimit = str(4 - TT)
        elif global_elements.NR_TestPoint == '3':
            highlimit = str(20 + TT)
            lowlimit = str(10 - TT)
        elif global_elements.NR_TestPoint == '4':
            highlimit = str(22.5 + TT)
            lowlimit = str(17.5 - TT)

        if state:
            # 配置Meas 参数
            global_elements.CU_intance.MeasParmsSetingfor6_2_4()
            time.sleep(2)

            # 配置完参数后确认是否还是正常连接
            state = global_elements.CU_intance.checkConnectState()
            if state:
                # 开始测试并取值
                power_value = global_elements.CU_intance.getValue_6_2_4()
                global_elements.emitsingle.stateupdataSingle.emit('Power Value: ' + power_value)
                reporthandle.Reporttool(power_value, lowlimit, highlimit, 'dBm')
            else:
                global_elements.NR_remark_r = 'DUT Connect timeout!'
                power_value = '-999'
                reporthandle.Reporttool(power_value, lowlimit, highlimit, 'dBm')
                global_elements.emitsingle.stateupdataSingle.emit('DUT Connect timeout!')
        else:
            global_elements.NR_remark_r = 'DUT Connect timeout!'
            power_value = '-999'
            reporthandle.Reporttool(power_value, lowlimit, highlimit, 'dBm')
            global_elements.emitsingle.stateupdataSingle.emit('DUT Connect timeout!')

        # 更新图表参数
        global_elements.maxOutputPowerResutl.append(float(power_value))
        global_elements.maxOutputPowerLow.append(float(lowlimit))
        global_elements.maxOutputPowerhigh.append(float(highlimit))
        global_elements.maxOutputPowerTestid.append(global_elements.NR_testid + '_' +  global_elements.NR_TestPoint)
        global_elements.emitsingle.maxOutputPowerChartUpdata.emit([global_elements.maxOutputPowerResutl,
                                                                   global_elements.maxOutputPowerLow,
                                                                   global_elements.maxOutputPowerhigh,
                                                                   global_elements.maxOutputPowerTestid])
        time.sleep(2)  # 等待Chart更新完再继续，避免global参数已更新到下一步的内容
        # 更新进度条
        global_elements.finished_step += 1
        process_rate = format(global_elements.finished_step * 100 / global_elements.total_step, '.2f')
        global_elements.emitsingle.process_rateupdataSingle.emit(process_rate)

def Minimumoutputpower6_3_1(parms_list, connectState):
    global_elements.NR_remark_r = ''
    global_elements.test_item_r = ''
    if parms_list[0]['value'] == 'True':
        state = connectState   # 接收传入的DUT连接状态
        # 判断是否有CHANNEL BW SCS的参数变化，如果有，Reset CU
        ischanged = parmslisthandle.parmslisthandle(parms_list)
        if ischanged:
            # 如果有CHANNEL BW SCS的参数变化，清空主界面结果图表
            # global_elements.emitsingle.resultChartclear.emit()
            # 如果有CHANNEL BW SCS的参数变化，重置图表参数
            testseq_handle.chartResutlClear()
            # 如果有CHANNEL BW SCS的参数变化，重置CU 和DUT
            state = global_elements.CU_intance.reSetCU_and_reConnectDUT()

        global_elements.emitsingle.stateupdataSingle.emit(global_elements.NR_band +
                                                          ' ' + global_elements.test_case_name
                                                          + '  BW:' + global_elements.NR_bw +
                                                          '  Channel:' + global_elements.NR_ch +
                                                          '  SCS:' + global_elements.NR_SCS +
                                                          '  Test Id:' + global_elements.NR_testid)

        ul_fre = reporthandle.NreftoFre(global_elements.NR_ch_r)
        if int(global_elements.NR_bw_num) <= 40:
            if float(ul_fre) <= 3000:
                TT = 1
            else:
                TT = 1.3
        else:
            TT = 1.3

        if global_elements.NR_bw_num in ['5', '10', '15', '20']:
            highlimit = format((-40 + TT), '.1f')
        elif global_elements.NR_bw_num == '25':
            highlimit = format((-39 + TT), '.1f')
        elif global_elements.NR_bw_num == '30':
            highlimit = format((-38.2 + TT), '.1f')
        elif global_elements.NR_bw_num == '40':
            highlimit = format((-37 + TT), '.1f')
        elif global_elements.NR_bw_num == '50':
            highlimit = format((-36 + TT), '.1f')
        elif global_elements.NR_bw_num == '60':
            highlimit = format((-35.2 + TT), '.1f')
        elif global_elements.NR_bw_num == '80':
            highlimit = format((-34 + TT), '.1f')
        elif global_elements.NR_bw_num == '90':
            highlimit = format((-33.5 + TT), '.1f')
        elif global_elements.NR_bw_num == '100':
            highlimit = format((-33 + TT), '.1f')
        else:
            highlimit = 'None'
        lowlimit = 'None'

        if state:
            global_elements.emitsingle.stateupdataSingle.emit('DUT Connect Successed!')
            # 配置Meas 参数
            global_elements.CU_intance.MeasParmsSetingfor6_3_1()
            time.sleep(2)

            # 配置完参数后确认是否还是正常连接
            state = global_elements.CU_intance.checkConnectState()
            if state:
                # 开始测试并取值
                power_value = global_elements.CU_intance.getValue_6_3_1()
                global_elements.emitsingle.stateupdataSingle.emit('Power Value: ' + power_value)
                reporthandle.Reporttool(power_value, lowlimit, highlimit, 'dBm')
            else:
                global_elements.NR_remark_r = 'DUT Connect timeout!'
                power_value = '-999'
                reporthandle.Reporttool(power_value, lowlimit, highlimit, 'dBm')
                global_elements.emitsingle.stateupdataSingle.emit('DUT Connect timeout!')
        else:
            global_elements.NR_remark_r = 'DUT Connect timeout!'
            power_value = '-999'
            reporthandle.Reporttool(power_value, lowlimit, highlimit, 'dBm')
            global_elements.emitsingle.stateupdataSingle.emit('DUT Connect timeout!')

        # 更新图表参数
        global_elements.maxOutputPowerResutl.append(float(power_value))
        global_elements.maxOutputPowerLow.append(float(lowlimit) if lowlimit != 'None' else None)
        global_elements.maxOutputPowerhigh.append(float(highlimit))
        global_elements.maxOutputPowerTestid.append(global_elements.NR_testid)
        global_elements.emitsingle.maxOutputPowerChartUpdata.emit([global_elements.maxOutputPowerResutl,
                                                                   global_elements.maxOutputPowerLow,
                                                                   global_elements.maxOutputPowerhigh,
                                                                   global_elements.maxOutputPowerTestid])
        time.sleep(2)  # 等待Chart更新完再继续，避免global参数已更新到下一步的内容
        # 更新进度条
        global_elements.finished_step += 1
        process_rate = format(global_elements.finished_step * 100 / global_elements.total_step, '.2f')
        global_elements.emitsingle.process_rateupdataSingle.emit(process_rate)

def UEmaximumoutputpower6_3_3_2(parms_list, connectState):
    global_elements.NR_remark_r = ''
    global_elements.test_item_r = ''
    if parms_list[0]['value'] == 'True':
        state = connectState   # 接收传入的DUT连接状态
        # 判断是否有CHANNEL BW SCS的参数变化，如果有，Reset CU
        ischanged = parmslisthandle.parmslisthandle(parms_list)
        if ischanged:
            # 如果有CHANNEL BW SCS的参数变化，清空主界面结果图表
            # global_elements.emitsingle.resultChartclear.emit()
            # 如果有CHANNEL BW SCS的参数变化，重置图表参数
            testseq_handle.chartResutlClear()
            # 如果有CHANNEL BW SCS的参数变化，重置CU 和DUT
            state = global_elements.CU_intance.reSetCU_and_reConnectDUT()

        global_elements.emitsingle.stateupdataSingle.emit(global_elements.NR_band +
                                                          ' ' + global_elements.test_case_name
                                                          + '  BW:' + global_elements.NR_bw +
                                                          '  Channel:' + global_elements.NR_ch +
                                                          '  SCS:' + global_elements.NR_SCS +
                                                          '  Test Id:' + global_elements.NR_testid)

        ul_fre = reporthandle.NreftoFre(global_elements.NR_ch_r)
        if int(global_elements.NR_bw_num) <= 40:
            if float(ul_fre) <= 3000:
                TT = 1.5
            else:
                TT = 1.8
        else:
            if float(ul_fre) <= 3000:
                TT = 1.7
            else:
                TT = 1.8

        exp_power = global_elements.expPower_onoffpower[global_elements.NR_SCS][global_elements.NR_bw_num]
        lowlimit_off = 'None'
        highlimit_off = format((-50 + TT), '.1f')
        try:
            lowlimit_on = format(float(exp_power) - 9 - TT, '.1f')
            highlimit_on = format(float(exp_power) + 9 + TT, '.1f')
        except Exception as e:
            lowlimit_on = 'None'
            highlimit_on = 'None'
            global_elements.emitsingle.stateupdataSingle.emit('Error: Expected Power get failed!')
            global_elements.NR_remark_r = 'Error: Expected Power get failed!'

        if state:
            global_elements.emitsingle.stateupdataSingle.emit('DUT Connect Successed!')
            # 配置Meas 参数 并取值
            onPower, offPowerB, offPowerA = global_elements.CU_intance.MeasParmsSetingfor6_3_3_2()
            time.sleep(1)
            global_elements.emitsingle.stateupdataSingle.emit('Off Power Before: ' + offPowerB)
            global_elements.emitsingle.stateupdataSingle.emit('Off Power After: ' + offPowerA)
            global_elements.emitsingle.stateupdataSingle.emit('On Power: ' + onPower)
            global_elements.test_item_r = 'Off Power Before'
            reporthandle.Reporttool(offPowerB, lowlimit_off, highlimit_off, 'dBm')
            global_elements.test_item_r = 'Off Power After'
            reporthandle.Reporttool(offPowerA, lowlimit_off, highlimit_off, 'dBm')
            global_elements.test_item_r = 'On Power'
            reporthandle.Reporttool(onPower, lowlimit_on, highlimit_on, 'dBm')

        else:
            global_elements.NR_remark_r = 'DUT Connect timeout!'
            offPowerB = '-999'
            offPowerA = '-999'
            onPower = '-999'
            global_elements.test_item_r = 'Off Power Before'
            reporthandle.Reporttool(offPowerB, lowlimit_off, highlimit_off, 'dBm')
            global_elements.test_item_r = 'Off Power After'
            reporthandle.Reporttool(offPowerA, lowlimit_off, highlimit_off, 'dBm')
            global_elements.test_item_r = 'On Power'
            reporthandle.Reporttool(onPower, lowlimit_on, highlimit_on, 'dBm')
            global_elements.emitsingle.stateupdataSingle.emit('DUT Connect timeout!')

        # 更新图表参数
        global_elements.onoffP_low = [None, float(lowlimit_on), None]
        global_elements.onoffP_high = [float(highlimit_off), float(highlimit_on), float(highlimit_off)]
        global_elements.onoffPower = [float(offPowerB), float(onPower), float(offPowerA)]
        global_elements.emitsingle.onoffPowerChartUpdata.emit([global_elements.onoffPower,
                                                                   global_elements.onoffP_low,
                                                                   global_elements.onoffP_high,
                                                                   global_elements.onoffP_labels])
        time.sleep(3)  # 等待Chart更新完再继续，避免global参数已更新到下一步的内容
        # 更新进度条
        global_elements.finished_step += 1
        process_rate = format(global_elements.finished_step * 100 / global_elements.total_step, '.2f')
        global_elements.emitsingle.process_rateupdataSingle.emit(process_rate)

def Frequencyerror6_4_1(parms_list, connectState):
    global_elements.NR_remark_r = ''
    # 保丰将下行的配置，便于报告中查看
    global_elements.test_item_r = 'DL:CP-OFDM QPSK, Full RB:' + global_elements.NR_DlRBconfig
    if parms_list[0]['value'] == 'True':
        state = connectState   # 接收传入的DUT连接状态
        # 判断是否有CHANNEL BW SCS的参数变化，如果有，Reset CU
        ischanged = parmslisthandle.parmslisthandle_for_6_4_1(parms_list)
        if ischanged:
            # 如果有CHANNEL BW SCS的参数变化，清空主界面结果图表
            # global_elements.emitsingle.resultChartclear.emit()
            # 如果有CHANNEL BW SCS的参数变化，重置图表参数
            testseq_handle.chartResutlClear()
            # 如果有CHANNEL BW SCS的参数变化，重置CU 和DUT
            state = global_elements.CU_intance.reSetCU_and_reConnectDUT()

        global_elements.emitsingle.stateupdataSingle.emit(global_elements.NR_band +
                                                          ' ' + global_elements.test_case_name
                                                          + '  BW:' + global_elements.NR_bw +
                                                          '  Channel:' + global_elements.NR_ch +
                                                          '  SCS:' + global_elements.NR_SCS +
                                                          '  Test Id:' + global_elements.NR_testid)

        ul_fre = reporthandle.NreftoFre(global_elements.NR_ch_r)
        highlimit = format(float(ul_fre) * 0.1 + 15, '.2f')
        lowlimit = format(-(float(ul_fre) * 0.1 + 15), '.2f')

        if state:
            # 配置Meas 参数
            global_elements.CU_intance.MeasParmsSetingfor6_4_1()
            time.sleep(2)

            # 配置完参数后确认是否还是正常连接
            state = global_elements.CU_intance.checkConnectState()
            if state:
                # 开始测试并取值
                freError = global_elements.CU_intance.getValue_6_4_1()
                global_elements.emitsingle.stateupdataSingle.emit('Frequency Error: ' + freError + 'Hz')
                reporthandle.Reporttool(freError, lowlimit, highlimit, 'Hz')
            else:
                global_elements.NR_remark_r = 'DUT Connect timeout!'
                freError = '-999'
                reporthandle.Reporttool(freError, lowlimit, highlimit, 'Hz')
                global_elements.emitsingle.stateupdataSingle.emit('DUT Connect timeout!')
        else:
            global_elements.NR_remark_r = 'DUT Connect timeout!'
            freError = '-999'
            reporthandle.Reporttool(freError, lowlimit, highlimit, 'Hz')
            global_elements.emitsingle.stateupdataSingle.emit('DUT Connect timeout!')

        # 更新图表参数
        global_elements.maxOutputPowerResutl.append(float(freError))
        global_elements.maxOutputPowerLow.append(float(lowlimit))
        global_elements.maxOutputPowerhigh.append(float(highlimit))
        global_elements.maxOutputPowerTestid.append(global_elements.NR_testid)
        global_elements.emitsingle.freErrorChartUpdata.emit([global_elements.maxOutputPowerResutl,
                                                                   global_elements.maxOutputPowerLow,
                                                                   global_elements.maxOutputPowerhigh,
                                                                   global_elements.maxOutputPowerTestid])
        time.sleep(2)  # 等待Chart更新完再继续，避免global参数已更新到下一步的内容
        # 更新进度条
        global_elements.finished_step += 1
        process_rate = format(global_elements.finished_step * 100 / global_elements.total_step, '.2f')
        global_elements.emitsingle.process_rateupdataSingle.emit(process_rate)

def ErrorVectorMagnitudeforPUSCH6_4_2_1(parms_list, connectState):
    global_elements.NR_remark_r = ''
    global_elements.test_item_r = ''
    if parms_list[0]['value'] == 'True':
        state = connectState   # 接收传入的DUT连接状态
        # 判断是否有CHANNEL BW SCS的参数变化，如果有，Reset CU
        ischanged = parmslisthandle.parmslisthandle(parms_list)
        if ischanged:
            # 如果有CHANNEL BW SCS的参数变化，清空主界面结果图表
            # global_elements.emitsingle.resultChartclear.emit()
            # 如果有CHANNEL BW SCS的参数变化，重置图表参数
            testseq_handle.chartResutlClear()
            # 如果有CHANNEL BW SCS的参数变化，重置CU 和DUT
            state = global_elements.CU_intance.reSetCU_and_reConnectDUT()

        global_elements.emitsingle.stateupdataSingle.emit(global_elements.NR_band +
                                                          ' ' + global_elements.test_case_name
                                                          + '  BW:' + global_elements.NR_bw +
                                                          '  Channel:' + global_elements.NR_ch +
                                                          '  SCS:' + global_elements.NR_SCS +
                                                          '  Test Id:' + global_elements.NR_testid)

        ul_fre = reporthandle.NreftoFre(global_elements.NR_ch_r)

        if global_elements.NR_bw_num in ['5', '10', '15', '20']:
            pmin = '-40'
        elif global_elements.NR_bw_num == '25':
            pmin = '-39'
        elif global_elements.NR_bw_num == '30':
            pmin = '-38.2'
        elif global_elements.NR_bw_num == '40':
            pmin = '-37'
        elif global_elements.NR_bw_num == '50':
            pmin = '-36'
        elif global_elements.NR_bw_num == '60':
            pmin = '-35.2'
        elif global_elements.NR_bw_num == '80':
            pmin = '-34'
        elif global_elements.NR_bw_num == '90':
            pmin = '-33.5'
        else:
            pmin = '-33'

        lowlimit = 'None'
        if 'BPSK' in global_elements.NR_Modulation:
            highlimit = '30'
        elif 'QPSK' in global_elements.NR_Modulation:
            highlimit = '17.5'
        elif '16 QAM' in global_elements.NR_Modulation:
            highlimit = '12.5'
        elif '64 QAM' in global_elements.NR_Modulation:
            highlimit = '8'
        elif '256 QAM' in global_elements.NR_Modulation:
            highlimit = ['3.8', '4.3', '4.6']
            pmin = str(float(pmin) + 10)

        if state:
            # 配置Meas 参数(Pmax)
            global_elements.CU_intance.MeasParmsSetingfor6_4_2_1_pusch(global_elements.NR_p_max)

            time.sleep(2)

            # 配置完参数后确认是否还是正常连接
            state = global_elements.CU_intance.checkConnectState()
            if state:
                # 开始测试并取值
                evm_rms, evm_dmrs = global_elements.CU_intance.getValue_6_4_2_1(global_elements.NR_p_max)
                global_elements.emitsingle.stateupdataSingle.emit('EVM RMS: ' + evm_rms + '%')
                global_elements.emitsingle.stateupdataSingle.emit('EVM DMRS: ' + evm_dmrs + '%')
                if '256 QAM' not in global_elements.NR_Modulation:
                    activehightlimit = highlimit
                else:
                    activehightlimit = highlimit[0]
                global_elements.test_item_r = 'EVM RMS @ Pmax'
                reporthandle.Reporttool(evm_rms, lowlimit, activehightlimit, '%')
                global_elements.test_item_r = 'EVM DMRS @ Pmax'
                reporthandle.Reporttool(evm_dmrs, lowlimit, activehightlimit, '%')
            else:
                global_elements.NR_remark_r = 'DUT Connect timeout!'
                evm_rms = '-999'
                evm_dmrs = '-999'
                if '256 QAM' not in global_elements.NR_Modulation:
                    activehightlimit = highlimit
                else:
                    activehightlimit = highlimit[0]
                global_elements.test_item_r = 'EVM RMS @ Pmax'
                reporthandle.Reporttool(evm_rms, lowlimit, activehightlimit, '%')
                global_elements.test_item_r = 'EVM DMRS @ Pmax'
                reporthandle.Reporttool(evm_dmrs, lowlimit, activehightlimit, '%')

            # 更新图表参数
            global_elements.evmRMS.append(float(evm_rms))
            global_elements.evmDMRS.append(float(evm_dmrs))
            global_elements.maxOutputPowerLow.append(None)
            global_elements.maxOutputPowerhigh.append(float(activehightlimit))
            global_elements.maxOutputPowerTestid.append(global_elements.NR_testid + '_max')
            global_elements.emitsingle.evmChartUpdata.emit([global_elements.evmRMS,
                                                            global_elements.evmDMRS,
                                                            global_elements.maxOutputPowerLow,
                                                            global_elements.maxOutputPowerhigh,
                                                            global_elements.maxOutputPowerTestid])
            time.sleep(2)  # 等待Chart更新完再继续，避免global参数已更新到下一步的内容

            # 配置Meas 参数(Pmin)
            global_elements.CU_intance.MeasParmsSetingfor6_4_2_1_pusch(pmin)
            time.sleep(2)

            # 配置完参数后确认是否还是正常连接
            state = global_elements.CU_intance.checkConnectState()
            if state:
                # 开始测试并取值
                evm_rms, evm_dmrs = global_elements.CU_intance.getValue_6_4_2_1(pmin)
                global_elements.emitsingle.stateupdataSingle.emit('EVM RMS: ' + evm_rms + '%')
                global_elements.emitsingle.stateupdataSingle.emit('EVM DMRS: ' + evm_dmrs + '%')
                if '256 QAM' not in global_elements.NR_Modulation:
                    activehighlimit = highlimit
                else:
                    if float(pmin) - (-25) > 0 and -15 - float(pmin) >= 0:
                        activehighlimit = highlimit[1]
                    elif -25 - float(pmin) >= 0 and float(pmin) - (-40) >= 0:
                        activehighlimit = highlimit[2]
                global_elements.test_item_r = 'EVM RMS @ ' + pmin + 'dBm'
                reporthandle.Reporttool(evm_rms, lowlimit, activehighlimit, '%')
                global_elements.test_item_r = 'EVM DMRS @ ' + pmin + 'dBm'
                reporthandle.Reporttool(evm_dmrs, lowlimit, activehighlimit, '%')
            else:
                global_elements.NR_remark_r = 'DUT Connect timeout!'
                evm_rms = '-999'
                evm_dmrs = '-999'
                if '256 QAM' not in global_elements.NR_Modulation:
                    activehighlimit = highlimit
                else:
                    if float(pmin) - (-25) > 0 and -15 - float(pmin) >= 0:
                        activehighlimit = highlimit[1]
                    elif -25 - float(pmin) >= 0 and float(pmin) - (-40) >= 0:
                        activehighlimit = highlimit[2]
                global_elements.test_item_r = 'EVM RMS @ ' + pmin + 'dBm'
                reporthandle.Reporttool(evm_rms, lowlimit, activehighlimit, '%')
                global_elements.test_item_r = 'EVM DMRS @ ' + pmin + 'dBm'
                reporthandle.Reporttool(evm_dmrs, lowlimit, activehighlimit, '%')

            # 更新图表参数
            global_elements.evmRMS.append(float(evm_rms))
            global_elements.evmDMRS.append(float(evm_dmrs))
            global_elements.maxOutputPowerLow.append(None)
            global_elements.maxOutputPowerhigh.append(float(activehighlimit))
            global_elements.maxOutputPowerTestid.append(global_elements.NR_testid + '_min')
            global_elements.emitsingle.evmChartUpdata.emit([global_elements.evmRMS,
                                                            global_elements.evmDMRS,
                                                            global_elements.maxOutputPowerLow,
                                                            global_elements.maxOutputPowerhigh,
                                                            global_elements.maxOutputPowerTestid])
            time.sleep(2)  # 等待Chart更新完再继续，避免global参数已更新到下一步的内容
        else:
            global_elements.NR_remark_r = 'DUT Connect timeout!'
            evm_rms = '-999'
            evm_dmrs = '-999'
            if '256 QAM' not in global_elements.NR_Modulation:
                activehighlimit = highlimit
            else:
                activehighlimit = highlimit[0]
            global_elements.test_item_r = 'EVM RMS @ Pmax'
            reporthandle.Reporttool(evm_rms, lowlimit, activehighlimit, '%')
            global_elements.test_item_r = 'EVM DMRS @ Pmax'
            reporthandle.Reporttool(evm_dmrs, lowlimit, activehighlimit, '%')

            global_elements.evmRMS.append(float(evm_rms))
            global_elements.evmDMRS.append(float(evm_dmrs))
            global_elements.maxOutputPowerLow.append(None)
            global_elements.maxOutputPowerhigh.append(float(activehighlimit))
            global_elements.maxOutputPowerTestid.append(global_elements.NR_testid + '_max')
            global_elements.emitsingle.evmChartUpdata.emit([global_elements.evmRMS,
                                                            global_elements.evmDMRS,
                                                            global_elements.maxOutputPowerLow,
                                                            global_elements.maxOutputPowerhigh,
                                                            global_elements.maxOutputPowerTestid])
            time.sleep(2)  # 等待Chart更新完再继续，避免global参数已更新到下一步的内容

            if '256 QAM' not in global_elements.NR_Modulation:
                activehighlimit = highlimit
            else:
                if float(pmin) - (-25) > 0 and -15 - float(pmin) >= 0:
                    activehighlimit = highlimit[1]
                elif -25 - float(pmin) >= 0 and float(pmin) - (-40) >= 0:
                    activehighlimit = highlimit[2]
            global_elements.test_item_r = 'EVM RMS @ P' + pmin + 'dBm'
            reporthandle.Reporttool(evm_rms, lowlimit, activehighlimit, '%')
            global_elements.test_item_r = 'EVM DMRS @ P' + pmin + 'dBm'
            reporthandle.Reporttool(evm_dmrs, lowlimit, activehighlimit, '%')
            global_elements.emitsingle.stateupdataSingle.emit('DUT Connect timeout!')

            # 更新图表参数
            global_elements.evmRMS.append(float(evm_rms))
            global_elements.evmDMRS.append(float(evm_dmrs))
            global_elements.maxOutputPowerLow.append(None)
            global_elements.maxOutputPowerhigh.append(float(activehighlimit))
            global_elements.maxOutputPowerTestid.append(global_elements.NR_testid + '_min')
            global_elements.emitsingle.evmChartUpdata.emit([global_elements.evmRMS,
                                                                       global_elements.evmDMRS,
                                                                       global_elements.maxOutputPowerLow,
                                                                       global_elements.maxOutputPowerhigh,
                                                                       global_elements.maxOutputPowerTestid])
            time.sleep(2)  # 等待Chart更新完再继续，避免global参数已更新到下一步的内容


        # 更新进度条
        global_elements.finished_step += 1
        process_rate = format(global_elements.finished_step * 100 / global_elements.total_step, '.2f')
        global_elements.emitsingle.process_rateupdataSingle.emit(process_rate)

def Carrierleakage6_4_2_2(parms_list, connectState):
    global_elements.NR_remark_r = ''
    global_elements.test_item_r = ''
    if parms_list[0]['value'] == 'True':
        state = connectState   # 接收传入的DUT连接状态
        # 判断是否有CHANNEL BW SCS的参数变化，如果有，Reset CU
        ischanged = parmslisthandle.parmslisthandle_for_6_4_2_2(parms_list)
        if ischanged:
            # 如果有CHANNEL BW SCS的参数变化，清空主界面结果图表
            # global_elements.emitsingle.resultChartclear.emit()
            # 如果有CHANNEL BW SCS的参数变化，重置图表参数
            testseq_handle.chartResutlClear()
            # 如果有CHANNEL BW SCS的参数变化，重置CU 和DUT
            state = global_elements.CU_intance.reSetCU_and_reConnectDUT()

        global_elements.emitsingle.stateupdataSingle.emit(global_elements.NR_band +
                                                          ' ' + global_elements.test_case_name
                                                          + '  BW:' + global_elements.NR_bw +
                                                          '  Channel:' + global_elements.NR_ch +
                                                          '  SCS:' + global_elements.NR_SCS +
                                                          '  Test Id:' + global_elements.NR_testid +
                                                          '  Pexp@' + global_elements.NR_Pexp)

        ul_fre = reporthandle.NreftoFre(global_elements.NR_ch_r)
        TT = 0.8
        lowlimit = 'None'
        if global_elements.NR_Pexp_pre == '10':
            highlimit = str(-28 + TT)
        elif global_elements.NR_Pexp_pre == '0':
            highlimit = str(-25 + TT)
        elif global_elements.NR_Pexp_pre == '-30':
            highlimit = str(-20 + TT)
        else:
            highlimit = str(-10 + TT)

        global_elements.test_item_r = 'Exp. Power@' + global_elements.NR_Pexp + 'dBm'

        if state:
            # 配置Meas 参数
            global_elements.CU_intance.MeasParmsSetingfor6_4_2_2()
            time.sleep(2)

            # 配置完参数后确认是否还是正常连接
            state = global_elements.CU_intance.checkConnectState()
            if state:
                # 开始测试并取值
                power_value = global_elements.CU_intance.getValue_6_4_2_2()
                global_elements.emitsingle.stateupdataSingle.emit('Value: ' + power_value)
                reporthandle.Reporttool(power_value, lowlimit, highlimit, 'dBm')
            else:
                global_elements.NR_remark_r = 'DUT Connect timeout!'
                power_value = '-999'
                reporthandle.Reporttool(power_value, lowlimit, highlimit, 'dBm')
                global_elements.emitsingle.stateupdataSingle.emit('DUT Connect timeout!')
        else:
            global_elements.NR_remark_r = 'DUT Connect timeout!'
            power_value = '-999'
            reporthandle.Reporttool(power_value, lowlimit, highlimit, 'dBm')
            global_elements.emitsingle.stateupdataSingle.emit('DUT Connect timeout!')

        # 更新图表参数
        global_elements.maxOutputPowerResutl.append(float(power_value))
        global_elements.maxOutputPowerLow.append(None)
        global_elements.maxOutputPowerhigh.append(float(highlimit))
        global_elements.maxOutputPowerTestid.append('Pexp @' + global_elements.NR_Pexp_pre)
        global_elements.emitsingle.maxOutputPowerChartUpdata.emit([global_elements.maxOutputPowerResutl,
                                                                   global_elements.maxOutputPowerLow,
                                                                   global_elements.maxOutputPowerhigh,
                                                                   global_elements.maxOutputPowerTestid])
        time.sleep(2)  # 等待Chart更新完再继续，避免global参数已更新到下一步的内容
        # 更新进度条
        global_elements.finished_step += 1
        process_rate = format(global_elements.finished_step * 100 / global_elements.total_step, '.2f')
        global_elements.emitsingle.process_rateupdataSingle.emit(process_rate)

def In_bandemissionsforpusch6_4_2_3(parms_list, connectState):
    global_elements.NR_remark_r = ''
    global_elements.test_item_r = ''
    isError = False
    if parms_list[0]['value'] == 'True':
        state = connectState   # 接收传入的DUT连接状态
        # 判断是否有CHANNEL BW SCS的参数变化，如果有，Reset CU
        ischanged, PexpisChanged = parmslisthandle.parmslisthandle_for_6_4_2_3(parms_list)
        if ischanged:
            # 如果有CHANNEL BW SCS的参数变化，清空主界面结果图表
            # global_elements.emitsingle.resultChartclear.emit()
            # 如果有CHANNEL BW SCS的参数变化，重置图表参数
            testseq_handle.chartResutlClear()
            # 如果有CHANNEL BW SCS的参数变化，重置CU 和DUT
            state = global_elements.CU_intance.reSetCU_and_reConnectDUT()
        # if PexpisChanged:
        #     # 如果有Pexp的参数变化，重置CU 和DUT,主要是防止SPIC指令出错（如果不重置）
        #     state = global_elements.CU_intance.reSetCU_and_reConnectDUT()

        global_elements.emitsingle.stateupdataSingle.emit(global_elements.NR_band +
                                                          ' ' + global_elements.test_case_name
                                                          + '  BW:' + global_elements.NR_bw +
                                                          '  Channel:' + global_elements.NR_ch +
                                                          '  SCS:' + global_elements.NR_SCS +
                                                          '  Test Id:' + global_elements.NR_testid +
                                                          '  Pexp@' + global_elements.NR_Pexp)

        ul_fre = reporthandle.NreftoFre(global_elements.NR_ch_r)

        lowlimit = '0'
        highlimit = 'None'


        global_elements.test_item_r = 'In-band emissions Margin Exp. Power@' + global_elements.NR_Pexp + 'dBm'

        if state:
            # 配置Meas 参数
            isError = global_elements.CU_intance.MeasParmsSetingfor6_4_2_3_pusch()
            if isError:
                state = global_elements.CU_intance.reSetCU_and_reConnectDUT()
                In_bandemissionsforpusch6_4_2_3(parms_list, state)
                return
            else:
                time.sleep(2)

                # 配置完参数后确认是否还是正常连接
                state = global_elements.CU_intance.checkConnectState()
                if state:
                    # 开始测试并取值
                    power_value = global_elements.CU_intance.getValue_6_4_2_3()
                    global_elements.emitsingle.stateupdataSingle.emit('Value: ' + power_value)
                    reporthandle.Reporttool(power_value, lowlimit, highlimit, 'dB')
                else:
                    global_elements.NR_remark_r = 'DUT Connect timeout!'
                    power_value = '-999'
                    reporthandle.Reporttool(power_value, lowlimit, highlimit, 'dB')
                    global_elements.emitsingle.stateupdataSingle.emit('DUT Connect timeout!')
        else:
            global_elements.NR_remark_r = 'DUT Connect timeout!'
            power_value = '-999'
            reporthandle.Reporttool(power_value, lowlimit, highlimit, 'dB')
            global_elements.emitsingle.stateupdataSingle.emit('DUT Connect timeout!')

        if not isError:
            # 更新图表参数
            global_elements.maxOutputPowerResutl.append(float(power_value))
            global_elements.maxOutputPowerLow.append(float(lowlimit))
            global_elements.maxOutputPowerhigh.append(None)
            global_elements.maxOutputPowerTestid.append(global_elements.NR_testid + '@' + global_elements.NR_Pexp_pre)
            global_elements.emitsingle.inbandemissionChartUpdata.emit([global_elements.maxOutputPowerResutl,
                                                                       global_elements.maxOutputPowerLow,
                                                                       global_elements.maxOutputPowerhigh,
                                                                       global_elements.maxOutputPowerTestid])
            time.sleep(2)  # 等待Chart更新完再继续，避免global参数已更新到下一步的内容
            # 更新进度条
            global_elements.finished_step += 1
            process_rate = format(global_elements.finished_step * 100 / global_elements.total_step, '.2f')
            global_elements.emitsingle.process_rateupdataSingle.emit(process_rate)

def EVMequalizerspectrumflatness6_4_2_4(parms_list, connectState):
    global_elements.NR_remark_r = ''
    global_elements.test_item_r = ''
    if parms_list[0]['value'] == 'True':
        state = connectState   # 接收传入的DUT连接状态
        # 判断是否有CHANNEL BW SCS的参数变化，如果有，Reset CU
        ischanged = parmslisthandle.parmslisthandle(parms_list)
        if ischanged:
            # 如果有CHANNEL BW SCS的参数变化，清空主界面结果图表
            # global_elements.emitsingle.resultChartclear.emit()
            # 如果有CHANNEL BW SCS的参数变化，重置图表参数
            testseq_handle.chartResutlClear()
            # 如果有CHANNEL BW SCS的参数变化，重置CU 和DUT
            state = global_elements.CU_intance.reSetCU_and_reConnectDUT()

        global_elements.emitsingle.stateupdataSingle.emit(global_elements.NR_band +
                                                          ' ' + global_elements.test_case_name
                                                          + '  BW:' + global_elements.NR_bw +
                                                          '  Channel:' + global_elements.NR_ch +
                                                          '  SCS:' + global_elements.NR_SCS +
                                                          '  Test Id:' + global_elements.NR_testid)

        ul_fre = reporthandle.NreftoFre(global_elements.NR_ch_r)
        lowlimit = 'None'
        if global_elements.NR_condition == 'NTNV':
            highlimit1 = '9.4'
            highlimit2 = '8.4'
            highlimit3 = '5.4'
            highlimit4 = '6.4'
        else:
            highlimit1 = '13.4'
            highlimit2 = '11.4'
            highlimit3 = '5.4'
            highlimit4 = '7.4'

        if state:
            # 配置Meas 参数
            global_elements.CU_intance.MeasParmsSetingfor6_4_2_4()
            time.sleep(2)

            # 配置完参数后确认是否还是正常连接
            state = global_elements.CU_intance.checkConnectState()
            if state:
                # 开始测试并取值
                value = global_elements.CU_intance.getValue_6_4_2_4()
                if global_elements.NR_ch == 'Mid':
                    global_elements.emitsingle.stateupdataSingle.emit('Ripple1: ' + value[0])
                    global_elements.test_item_r = 'Ripple1'
                    reporthandle.Reporttool(value[0], lowlimit, highlimit1, 'dB')
                else:
                    global_elements.emitsingle.stateupdataSingle.emit('Ripple1: ' + value[0])
                    global_elements.test_item_r = 'Ripple1'
                    reporthandle.Reporttool(value[0], lowlimit, highlimit1, 'dB')
                    global_elements.emitsingle.stateupdataSingle.emit('Ripple2: ' + value[1])
                    global_elements.test_item_r = 'Ripple2'
                    reporthandle.Reporttool(value[1], lowlimit, highlimit2, 'dB')
                    global_elements.emitsingle.stateupdataSingle.emit('Ripple12: ' + value[2])
                    global_elements.test_item_r = 'Ripple12'
                    reporthandle.Reporttool(value[2], lowlimit, highlimit3, 'dB')
                    global_elements.emitsingle.stateupdataSingle.emit('Ripple21: ' + value[3])
                    global_elements.test_item_r = 'Ripple21'
                    reporthandle.Reporttool(value[3], lowlimit, highlimit4, 'dB')
            else:
                global_elements.NR_remark_r = 'DUT Connect timeout!'
                value = ['-999', '-999', '-999', '-999']
                if global_elements.NR_ch == 'Mid':
                    global_elements.test_item_r = 'Ripple1'
                    reporthandle.Reporttool(value[0], lowlimit, highlimit1, 'dB')
                else:
                    global_elements.test_item_r = 'Ripple1'
                    reporthandle.Reporttool(value[0], lowlimit, highlimit1, 'dB')
                    global_elements.test_item_r = 'Ripple2'
                    reporthandle.Reporttool(value[1], lowlimit, highlimit2, 'dB')
                    global_elements.test_item_r = 'Ripple12'
                    reporthandle.Reporttool(value[2], lowlimit, highlimit3, 'dB')
                    global_elements.test_item_r = 'Ripple21'
                    reporthandle.Reporttool(value[3], lowlimit, highlimit4, 'dB')
                global_elements.emitsingle.stateupdataSingle.emit('DUT Connect timeout!')
        else:
            global_elements.NR_remark_r = 'DUT Connect timeout!'
            value = ['-999', '-999', '-999', '-999']
            if global_elements.NR_ch == 'Mid':
                global_elements.test_item_r = 'Ripple1'
                reporthandle.Reporttool(value[0], lowlimit, highlimit1, 'dB')
            else:
                global_elements.test_item_r = 'Ripple1'
                reporthandle.Reporttool(value[0], lowlimit, highlimit1, 'dB')
                global_elements.test_item_r = 'Ripple2'
                reporthandle.Reporttool(value[1], lowlimit, highlimit2, 'dB')
                global_elements.test_item_r = 'Ripple12'
                reporthandle.Reporttool(value[2], lowlimit, highlimit3, 'dB')
                global_elements.test_item_r = 'Ripple21'
                reporthandle.Reporttool(value[3], lowlimit, highlimit4, 'dB')
            global_elements.emitsingle.stateupdataSingle.emit('DUT Connect timeout!')

        # 更新图表参数
        global_elements.maxOutputPowerResutl.extend([float(x) for x in value])
        global_elements.maxOutputPowerLow.extend([None, None, None, None])
        global_elements.maxOutputPowerhigh.extend([float(highlimit1), float(highlimit2), float(highlimit3), float(highlimit4)])
        global_elements.maxOutputPowerTestid.extend([global_elements.NR_testid + '_Ripple1',
                                                     global_elements.NR_testid + '_Ripple2',
                                                     global_elements.NR_testid + '_Ripple12',
                                                     global_elements.NR_testid + '_Ripple21'])
        global_elements.emitsingle.evmflatnessChartUpdata.emit([global_elements.maxOutputPowerResutl,
                                                                   global_elements.maxOutputPowerLow,
                                                                   global_elements.maxOutputPowerhigh,
                                                                   global_elements.maxOutputPowerTestid])
        time.sleep(2)  # 等待Chart更新完再继续，避免global参数已更新到下一步的内容
        # 更新进度条
        global_elements.finished_step += 1
        process_rate = format(global_elements.finished_step * 100 / global_elements.total_step, '.2f')
        global_elements.emitsingle.process_rateupdataSingle.emit(process_rate)

def EVMequalizerspectrumflatnessforHalfPiBPSK6_4_2_5(parms_list, connectState):
    global_elements.NR_remark_r = ''
    global_elements.test_item_r = ''
    if parms_list[0]['value'] == 'True':
        state = connectState   # 接收传入的DUT连接状态
        # 判断是否有CHANNEL BW SCS的参数变化，如果有，Reset CU
        ischanged = parmslisthandle.parmslisthandle(parms_list)
        if ischanged:
            # 如果有CHANNEL BW SCS的参数变化，清空主界面结果图表
            # global_elements.emitsingle.resultChartclear.emit()
            # 如果有CHANNEL BW SCS的参数变化，重置图表参数
            testseq_handle.chartResutlClear()
            # 如果有CHANNEL BW SCS的参数变化，重置CU 和DUT
            state = global_elements.CU_intance.reSetCU_and_reConnectDUT()

        global_elements.emitsingle.stateupdataSingle.emit(global_elements.NR_band +
                                                          ' ' + global_elements.test_case_name
                                                          + '  BW:' + global_elements.NR_bw +
                                                          '  Channel:' + global_elements.NR_ch +
                                                          '  SCS:' + global_elements.NR_SCS +
                                                          '  Test Id:' + global_elements.NR_testid)

        ul_fre = reporthandle.NreftoFre(global_elements.NR_ch_r)
        lowlimit = 'None'
        if global_elements.NR_condition == 'NTNV':
            highlimit1 = '15.4'
            highlimit2 = '7.4'

        else:
            highlimit1 = '15.4'
            highlimit2 = '7.4'

        if state:
            # 配置Meas 参数
            global_elements.CU_intance.MeasParmsSetingfor6_4_2_5()
            time.sleep(2)

            # 配置完参数后确认是否还是正常连接
            state = global_elements.CU_intance.checkConnectState()
            if state:
                # 开始测试并取值
                value = global_elements.CU_intance.getValue_6_4_2_5()
                if global_elements.NR_ch == 'Mid':
                    global_elements.emitsingle.stateupdataSingle.emit('Ripple1: ' + value[0])
                    global_elements.test_item_r = 'Ripple1'
                    reporthandle.Reporttool(value[0], lowlimit, highlimit1, 'dB')
                else:
                    global_elements.emitsingle.stateupdataSingle.emit('Ripple1: ' + value[0])
                    global_elements.test_item_r = 'Ripple1'
                    reporthandle.Reporttool(value[0], lowlimit, highlimit1, 'dB')
                    global_elements.emitsingle.stateupdataSingle.emit('Ripple2: ' + value[1])
                    global_elements.test_item_r = 'Ripple2'
                    reporthandle.Reporttool(value[1], lowlimit, highlimit2, 'dB')
            else:
                global_elements.NR_remark_r = 'DUT Connect timeout!'
                value = ['-999', '-999']
                if global_elements.NR_ch == 'Mid':
                    global_elements.test_item_r = 'Ripple1'
                    reporthandle.Reporttool(value[0], lowlimit, highlimit1, 'dB')
                else:
                    global_elements.test_item_r = 'Ripple1'
                    reporthandle.Reporttool(value[0], lowlimit, highlimit1, 'dB')
                    global_elements.test_item_r = 'Ripple2'
                    reporthandle.Reporttool(value[1], lowlimit, highlimit2, 'dB')

                global_elements.emitsingle.stateupdataSingle.emit('DUT Connect timeout!')
        else:
            global_elements.NR_remark_r = 'DUT Connect timeout!'
            value = ['-999', '-999']
            if global_elements.NR_ch == 'Mid':
                global_elements.test_item_r = 'Ripple1'
                reporthandle.Reporttool(value[0], lowlimit, highlimit1, 'dB')
            else:
                global_elements.test_item_r = 'Ripple1'
                reporthandle.Reporttool(value[0], lowlimit, highlimit1, 'dB')
                global_elements.test_item_r = 'Ripple2'
                reporthandle.Reporttool(value[1], lowlimit, highlimit2, 'dB')
            global_elements.emitsingle.stateupdataSingle.emit('DUT Connect timeout!')

        # 更新图表参数
        global_elements.maxOutputPowerResutl.extend([float(x) for x in value])
        global_elements.maxOutputPowerLow.extend([None, None])
        global_elements.maxOutputPowerhigh.extend([float(highlimit1), float(highlimit2)])
        global_elements.maxOutputPowerTestid.extend([global_elements.NR_testid + '_Ripple1',
                                                     global_elements.NR_testid + '_Ripple2'])
        global_elements.emitsingle.evmflatnessChartUpdata.emit([global_elements.maxOutputPowerResutl,
                                                                   global_elements.maxOutputPowerLow,
                                                                   global_elements.maxOutputPowerhigh,
                                                                   global_elements.maxOutputPowerTestid])
        time.sleep(2)  # 等待Chart更新完再继续，避免global参数已更新到下一步的内容
        # 更新进度条
        global_elements.finished_step += 1
        process_rate = format(global_elements.finished_step * 100 / global_elements.total_step, '.2f')
        global_elements.emitsingle.process_rateupdataSingle.emit(process_rate)

def Occupiedbandwidth6_5_1(parms_list, connectState):
    global_elements.NR_remark_r = ''
    global_elements.test_item_r = ''
    if parms_list[0]['value'] == 'True':
        state = connectState   # 接收传入的DUT连接状态
        # 判断是否有CHANNEL BW SCS的参数变化，如果有，Reset CU
        ischanged = parmslisthandle.parmslisthandle_for_6_5_1(parms_list)
        if ischanged:
            # 如果有CHANNEL BW SCS的参数变化，清空主界面结果图表
            # global_elements.emitsingle.resultChartclear.emit()
            # 如果有CHANNEL BW SCS的参数变化，重置图表参数
            testseq_handle.chartResutlClear()
            # 如果有CHANNEL BW SCS的参数变化，重置CU 和DUT
            state = global_elements.CU_intance.reSetCU_and_reConnectDUT()

        global_elements.emitsingle.stateupdataSingle.emit(global_elements.NR_band +
                                                          ' ' + global_elements.test_case_name
                                                          + '  BW:' + global_elements.NR_bw +
                                                          '  Channel:' + global_elements.NR_ch +
                                                          '  SCS:' + global_elements.NR_SCS +
                                                          '  Test Id:' + global_elements.NR_testid)

        ul_fre = reporthandle.NreftoFre(global_elements.NR_ch_r)
        lowlimit = 'None'
        highlimit = global_elements.NR_bw

        if state:
            # 配置Meas 参数
            global_elements.CU_intance.MeasParmsSetingfor6_5_1()
            time.sleep(2)

            # 配置完参数后确认是否还是正常连接
            state = global_elements.CU_intance.checkConnectState()
            if state:
                # 开始测试并取值
                bw_value = global_elements.CU_intance.getValue_6_5_1()
                global_elements.emitsingle.stateupdataSingle.emit('BandWidth Value: ' + bw_value)
                reporthandle.Reporttool(bw_value, lowlimit, highlimit, 'MHz')
            else:
                global_elements.NR_remark_r = 'DUT Connect timeout!'
                bw_value = '-999'
                reporthandle.Reporttool(bw_value, lowlimit, highlimit, 'MHz')
                global_elements.emitsingle.stateupdataSingle.emit('DUT Connect timeout!')
        else:
            global_elements.NR_remark_r = 'DUT Connect timeout!'
            bw_value = '-999'
            reporthandle.Reporttool(bw_value, lowlimit, highlimit, 'MHz')
            global_elements.emitsingle.stateupdataSingle.emit('DUT Connect timeout!')

        # 更新图表参数
        global_elements.maxOutputPowerResutl.append(float(bw_value))
        global_elements.maxOutputPowerLow.append(None)
        global_elements.maxOutputPowerhigh.append(float(highlimit))
        global_elements.maxOutputPowerTestid.append(global_elements.NR_testid)
        global_elements.emitsingle.bwChartUpdata.emit([global_elements.maxOutputPowerResutl,
                                                                   global_elements.maxOutputPowerLow,
                                                                   global_elements.maxOutputPowerhigh,
                                                                   global_elements.maxOutputPowerTestid])
        time.sleep(2)  # 等待Chart更新完再继续，避免global参数已更新到下一步的内容
        # 更新进度条
        global_elements.finished_step += 1
        process_rate = format(global_elements.finished_step * 100 / global_elements.total_step, '.2f')
        global_elements.emitsingle.process_rateupdataSingle.emit(process_rate)

def SpectrumEmissionMask6_5_2_2(parms_list, connectState):
    global_elements.NR_remark_r = ''
    global_elements.test_item_r = ''
    if parms_list[0]['value'] == 'True':
        state = connectState   # 接收传入的DUT连接状态
        # 每个step都清空图表数据
        testseq_handle.chartResutlClear()
        # 判断是否有CHANNEL BW SCS的参数变化，如果有，Reset CU
        ischanged = parmslisthandle.parmslisthandle(parms_list)
        if ischanged:
            # 如果有CHANNEL BW SCS的参数变化，重置CU 和DUT
            state = global_elements.CU_intance.reSetCU_and_reConnectDUT()

        global_elements.emitsingle.stateupdataSingle.emit(global_elements.NR_band +
                                                          ' ' + global_elements.test_case_name
                                                          + '  BW:' + global_elements.NR_bw +
                                                          '  Channel:' + global_elements.NR_ch +
                                                          '  SCS:' + global_elements.NR_SCS +
                                                          '  Test Id:' + global_elements.NR_testid)

        ul_fre = reporthandle.NreftoFre(global_elements.NR_ch_r)
        lowlimit = '0'
        highlimit = 'None'

        if state:
            # 配置Meas 参数
            global_elements.CU_intance.MeasParmsSetingfor6_5_2_2()
            time.sleep(2)

            # 配置完参数后确认是否还是正常连接
            state = global_elements.CU_intance.checkConnectState()
            if state:
                # 开始测试并取值
                margin_value = global_elements.CU_intance.getValue_6_5_2_2()
                for i in range(4):
                    global_elements.emitsingle.stateupdataSingle.emit('Margin'+ str(i+1)+' Value: ' + margin_value[i])
                    global_elements.test_item_r = 'SEM_MARGIN'+ str(i+1)
                    reporthandle.Reporttool(margin_value[i], lowlimit, highlimit, 'dB')

            else:
                global_elements.NR_remark_r = 'DUT Connect timeout!'
                margin_value = ['-999', '-999', '-999', '-999']
                for i in range(4):
                    global_elements.emitsingle.stateupdataSingle.emit(
                        'Margin' + str(i + 1) + ' Value: ' + margin_value[i])
                    global_elements.test_item_r = 'SEM_MARGIN' + str(i + 1)
                    reporthandle.Reporttool(margin_value[i], lowlimit, highlimit, 'dB')
        else:
            global_elements.NR_remark_r = 'DUT Connect timeout!'
            margin_value = ['-999', '-999', '-999', '-999']
            for i in range(4):
                global_elements.emitsingle.stateupdataSingle.emit(
                    'Margin' + str(i + 1) + ' Value: ' + margin_value[i])
                global_elements.test_item_r = 'SEM_MARGIN' + str(i + 1)
                reporthandle.Reporttool(margin_value[i], lowlimit, highlimit, 'dB')

        # 更新图表参数
        global_elements.maxOutputPowerResutl.extend([float(x) for x in margin_value])
        global_elements.maxOutputPowerLow.extend([0, 0, 0, 0])
        global_elements.maxOutputPowerhigh.extend([None, None, None, None])
        global_elements.maxOutputPowerTestid.extend(['SEM_MARGIN1', 'SEM_MARGIN2', 'SEM_MARGIN3', 'SEM_MARGIN4'])
        global_elements.emitsingle.semChartUpdata.emit([global_elements.maxOutputPowerResutl,
                                                                   global_elements.maxOutputPowerLow,
                                                                   global_elements.maxOutputPowerhigh,
                                                                   global_elements.maxOutputPowerTestid])
        time.sleep(2)  # 等待Chart更新完再继续，避免global参数已更新到下一步的内容
        # 更新进度条
        global_elements.finished_step += 1
        process_rate = format(global_elements.finished_step * 100 / global_elements.total_step, '.2f')
        global_elements.emitsingle.process_rateupdataSingle.emit(process_rate)

def Adjacentchannelleakageratio6_5_2_4(parms_list, connectState):
    global_elements.NR_remark_r = ''
    global_elements.test_item_r = ''
    if parms_list[0]['value'] == 'True':
        testseq_handle.chartResutlClear()
        state = connectState   # 接收传入的DUT连接状态
        # 判断是否有CHANNEL BW SCS的参数变化，如果有，Reset CU
        ischanged = parmslisthandle.parmslisthandle(parms_list)
        if ischanged:
            # 如果有CHANNEL BW SCS的参数变化，清空主界面结果图表
            # global_elements.emitsingle.resultChartclear.emit()
            # 如果有CHANNEL BW SCS的参数变化，重置图表参数
            # 如果有CHANNEL BW SCS的参数变化，重置CU 和DUT
            state = global_elements.CU_intance.reSetCU_and_reConnectDUT()

        global_elements.emitsingle.stateupdataSingle.emit(global_elements.NR_band +
                                                          ' ' + global_elements.test_case_name
                                                          + '  BW:' + global_elements.NR_bw +
                                                          '  Channel:' + global_elements.NR_ch +
                                                          '  SCS:' + global_elements.NR_SCS +
                                                          '  Test Id:' + global_elements.NR_testid)

        ul_fre = reporthandle.NreftoFre(global_elements.NR_ch_r)

        TT = 0.8
        highlimit = 'None'
        lowlimit_utraaclr1 = str(33 - TT)
        lowlimit_utraaclr2 = str(36 - TT)
        if global_elements.dutActiveDict['xml']['DUTCONFIG']['powerclass'] == '2':
            lowlimit_nraclr = str(31 - TT)
        else:
            lowlimit_nraclr = str(30 - TT)

        lowlimit_list = [lowlimit_nraclr, lowlimit_nraclr, lowlimit_utraaclr2, lowlimit_utraaclr1, lowlimit_utraaclr1, lowlimit_utraaclr2]

        items_list = ['NR_ACLR_L', 'NR_ACLR_R', 'NR_ACLR_UTRA2_L', 'NR_ACLR_UTRA1_L', 'NR_ACLR_UTRA1_R', 'NR_ACLR_UTRA2_R']
        if state:
            # 配置Meas 参数
            global_elements.CU_intance.MeasParmsSetingfor6_5_2_4()
            time.sleep(2)

            # 配置完参数后确认是否还是正常连接
            state = global_elements.CU_intance.checkConnectState()
            if state:
                # 开始测试并取值
                aclr_value = global_elements.CU_intance.getValue_6_5_2_4()
                for index in range(len(items_list)):
                    global_elements.test_item_r = items_list[index]
                    global_elements.emitsingle.stateupdataSingle.emit(items_list[index] + ' Value: ' + aclr_value[index])
                    reporthandle.Reporttool(aclr_value[index], lowlimit_list[index], highlimit, 'dB')
            else:
                global_elements.NR_remark_r = 'DUT Connect timeout!'
                aclr_value = ['-999', '-999', '-999', '-999', '-999', '-999']
                for index in range(len(items_list)):
                    global_elements.test_item_r = items_list[index]
                    global_elements.emitsingle.stateupdataSingle.emit(
                        items_list[index] + ' Value: ' + aclr_value[index])
                    reporthandle.Reporttool(aclr_value[index], lowlimit_list[index], highlimit, 'dB')
        else:
            global_elements.NR_remark_r = 'DUT Connect timeout!'
            aclr_value = ['-999', '-999', '-999', '-999', '-999', '-999']
            for index in range(len(items_list)):
                global_elements.test_item_r = items_list[index]
                global_elements.emitsingle.stateupdataSingle.emit(
                    items_list[index] + ' Value: ' + aclr_value[index])
                reporthandle.Reporttool(aclr_value[index], lowlimit_list[index], highlimit, 'dB')

        # 更新图表参数
        global_elements.maxOutputPowerResutl.extend([float(x) for x in aclr_value])
        global_elements.maxOutputPowerLow.extend([float(x) for x in lowlimit_list])
        global_elements.maxOutputPowerhigh.extend([None, None, None, None, None, None])
        global_elements.maxOutputPowerTestid.extend(items_list)
        global_elements.emitsingle.aclrChartUpdata.emit([global_elements.maxOutputPowerResutl,
                                                                   global_elements.maxOutputPowerLow,
                                                                   global_elements.maxOutputPowerhigh,
                                                                   global_elements.maxOutputPowerTestid])
        time.sleep(2)  # 等待Chart更新完再继续，避免global参数已更新到下一步的内容
        # 更新进度条
        global_elements.finished_step += 1
        process_rate = format(global_elements.finished_step * 100 / global_elements.total_step, '.2f')
        global_elements.emitsingle.process_rateupdataSingle.emit(process_rate)

def Referencesensitivitypowerlevel7_3_2(parms_list, connectState):
    global_elements.NR_remark_r = ''

    if parms_list[0]['value'] == 'True':
        state = connectState   # 接收传入的DUT连接状态
        # 判断是否有CHANNEL BW SCS的参数变化，如果有，Reset CU
        ischanged = parmslisthandle.parmslisthandle_for_7_3_2(parms_list)
        if ischanged:
            # 如果有CHANNEL BW SCS的参数变化，重置CU 和DUT
            state = global_elements.CU_intance.offCell_and_reConnectDUT()

        global_elements.emitsingle.stateupdataSingle.emit(global_elements.NR_band +
                                                          ' ' + global_elements.test_case_name
                                                          + '  BW:' + global_elements.NR_bw +
                                                          '  Channel:' + global_elements.NR_ch +
                                                          '  SCS:' + global_elements.NR_SCS +
                                                          '  Test Id:' + global_elements.NR_testid)


        dl_fre = reporthandle.NreftoFre(global_elements.NR_dl_ch_r)
        if float(dl_fre) - 3000 <= 0:
            TT = 0.7
        else:
            TT = 1

        dl_level = str(float(global_elements.NR_DL_level) + TT)
        # 保丰将下行的配置，便于报告中查看
        global_elements.test_item_r = 'DL:CP-OFDM QPSK, Full RB:' + global_elements.NR_DlRBconfig + ' @DL level ' + dl_level

        lowlimit = 'None'
        highlimit = '5'

        if state:
            # 配置Meas 参数
            global_elements.CU_intance.MeasParmsSetingfor7_3_2(dl_level)
            time.sleep(2)

            # 配置完参数后确认是否还是正常连接
            state = global_elements.CU_intance.checkConnectState()
            if state:
                # 开始测试并取值
                per_result = global_elements.CU_intance.getValue_7_3_2()
                global_elements.emitsingle.stateupdataSingle.emit('BLER: ' + per_result + '%')
                reporthandle.Reporttool(per_result, lowlimit, highlimit, '%')
            else:
                global_elements.NR_remark_r = 'DUT Connect timeout!'
                per_result = '-999'
                reporthandle.Reporttool(per_result, lowlimit, highlimit, '%')
                global_elements.emitsingle.stateupdataSingle.emit('DUT Connect timeout!')
        else:
            global_elements.NR_remark_r = 'DUT Connect timeout!'
            per_result = '-999'
            reporthandle.Reporttool(per_result, lowlimit, highlimit, '%')
            global_elements.emitsingle.stateupdataSingle.emit('DUT Connect timeout!')

        # 更新图表参数
        global_elements.maxOutputPowerResutl.append(float(per_result))
        global_elements.maxOutputPowerLow.append(None)
        global_elements.maxOutputPowerhigh.append(float(highlimit))
        global_elements.maxOutputPowerTestid.append(global_elements.NR_bw_num + 'M_' + global_elements.NR_ch)
        global_elements.emitsingle.blerChartUpdata.emit([global_elements.maxOutputPowerResutl,
                                                                   global_elements.maxOutputPowerLow,
                                                                   global_elements.maxOutputPowerhigh,
                                                                   global_elements.maxOutputPowerTestid])
        time.sleep(2)  # 等待Chart更新完再继续，避免global参数已更新到下一步的内容
        # 更新进度条
        global_elements.finished_step += 1
        process_rate = format(global_elements.finished_step * 100 / global_elements.total_step, '.2f')
        global_elements.emitsingle.process_rateupdataSingle.emit(process_rate)

def Referencesensitivitypowerlevel7_3_2_c(parms_list, connectState):
    global_elements.NR_remark_r = ''

    if parms_list[0]['value'] == 'True':
        state = connectState   # 接收传入的DUT连接状态
        # 判断是否有CHANNEL BW SCS的参数变化，如果有，Reset CU
        ischanged = parmslisthandle.parmslisthandle_for_7_3_2_c(parms_list)
        if ischanged:
            # 如果有CHANNEL BW SCS的参数变化，重置CU 和DUT
            state = global_elements.CU_intance.reSetCU_and_reConnectDUT()

        global_elements.emitsingle.stateupdataSingle.emit(global_elements.NR_band +
                                                          ' ' + global_elements.test_case_name
                                                          + '  BW:' + global_elements.NR_bw +
                                                          '  Channel:' + global_elements.NR_ch +
                                                          '  SCS:' + global_elements.NR_SCS +
                                                          '  Test Id:' + global_elements.NR_testid)


        dl_fre = reporthandle.NreftoFre(global_elements.NR_dl_ch_r)
        if float(dl_fre) - 3000 <= 0:
            TT = 0.7
        else:
            TT = 1

        dl_level = str(float(global_elements.NR_DL_level) + TT)
        # 保丰将下行的配置，便于报告中查看
        global_elements.test_item_r = 'DL:CP-OFDM QPSK, Full RB:' + global_elements.NR_DlRBconfig

        lowlimit = 'None'
        highlimit = dl_level

        if state:
            # 配置Meas 参数
            global_elements.CU_intance.MeasParmsSetingfor7_3_2_c()
            time.sleep(2)

            # 配置完参数后确认是否还是正常连接
            state = global_elements.CU_intance.checkConnectState()
            if state:
                # 开始测试并取值
                final_result = global_elements.CU_intance.getValue_7_3_2_c(dl_level)

                reporthandle.Reporttool(final_result, lowlimit, highlimit, 'dBm')
            else:
                global_elements.NR_remark_r = 'DUT Connect timeout!'
                final_result = '-999'
                reporthandle.Reporttool(final_result, lowlimit, highlimit, 'dBm')
                global_elements.emitsingle.stateupdataSingle.emit('DUT Connect timeout!')
        else:
            global_elements.NR_remark_r = 'DUT Connect timeout!'
            final_result = '-999'
            reporthandle.Reporttool(final_result, lowlimit, highlimit, 'dBm')
            global_elements.emitsingle.stateupdataSingle.emit('DUT Connect timeout!')

        # 更新图表参数
        global_elements.maxOutputPowerResutl.append(float(final_result))
        global_elements.maxOutputPowerLow.append(None)
        global_elements.maxOutputPowerhigh.append(float(highlimit))
        global_elements.maxOutputPowerTestid.append(global_elements.NR_bw_num + 'M_' + global_elements.NR_ch)
        global_elements.emitsingle.blerSearchChartUpdata.emit([global_elements.maxOutputPowerResutl,
                                                                   global_elements.maxOutputPowerLow,
                                                                   global_elements.maxOutputPowerhigh,
                                                                   global_elements.maxOutputPowerTestid])
        time.sleep(2)  # 等待Chart更新完再继续，避免global参数已更新到下一步的内容
        # 更新进度条
        global_elements.finished_step += 1
        process_rate = format(global_elements.finished_step * 100 / global_elements.total_step, '.2f')
        global_elements.emitsingle.process_rateupdataSingle.emit(process_rate)

def Maximuminputlevel7_4(parms_list, connectState):
    global_elements.NR_remark_r = ''

    if parms_list[0]['value'] == 'True':
        state = connectState   # 接收传入的DUT连接状态
        # 判断是否有CHANNEL BW SCS的参数变化，如果有，Reset CU
        ischanged = parmslisthandle.parmslisthandle_for_7_4(parms_list)
        if ischanged:
            # 如果有CHANNEL BW SCS的参数变化，重置CU 和DUT
            state = global_elements.CU_intance.offCell_and_reConnectDUT()

        global_elements.emitsingle.stateupdataSingle.emit(global_elements.NR_band +
                                                          ' ' + global_elements.test_case_name
                                                          + '  BW:' + global_elements.NR_bw +
                                                          '  Channel:' + global_elements.NR_ch +
                                                          '  SCS:' + global_elements.NR_SCS +
                                                          '  Test Id:' + global_elements.NR_testid)

        # 保丰将下行的配置，便于报告中查看
        global_elements.test_item_r = global_elements.NR_DL_Modulation + ', Full RB:' + global_elements.NR_DlRBconfig + ' @DL level ' + global_elements.NR_DL_level

        lowlimit = 'None'
        highlimit = '5'

        if state:
            # 配置Meas 参数
            global_elements.CU_intance.MeasParmsSetingfor7_4(global_elements.NR_DL_level)
            time.sleep(2)

            # 配置完参数后确认是否还是正常连接
            state = global_elements.CU_intance.checkConnectState()
            if state:
                # 开始测试并取值
                per_result = global_elements.CU_intance.getValue_7_4()
                global_elements.emitsingle.stateupdataSingle.emit('BLER: ' + per_result + '%')
                reporthandle.Reporttool(per_result, lowlimit, highlimit, '%')
            else:
                global_elements.NR_remark_r = 'DUT Connect timeout!'
                per_result = '-999'
                reporthandle.Reporttool(per_result, lowlimit, highlimit, '%')
                global_elements.emitsingle.stateupdataSingle.emit('DUT Connect timeout!')
        else:
            global_elements.NR_remark_r = 'DUT Connect timeout!'
            per_result = '-999'
            reporthandle.Reporttool(per_result, lowlimit, highlimit, '%')
            global_elements.emitsingle.stateupdataSingle.emit('DUT Connect timeout!')

        # 更新图表参数
        global_elements.maxOutputPowerResutl.append(float(per_result))
        global_elements.maxOutputPowerLow.append(None)
        global_elements.maxOutputPowerhigh.append(float(highlimit))
        global_elements.maxOutputPowerTestid.append(global_elements.NR_bw_num + 'M_' + global_elements.NR_testid)
        global_elements.emitsingle.blerChartUpdata.emit([global_elements.maxOutputPowerResutl,
                                                                   global_elements.maxOutputPowerLow,
                                                                   global_elements.maxOutputPowerhigh,
                                                                   global_elements.maxOutputPowerTestid])
        time.sleep(2)  # 等待Chart更新完再继续，避免global参数已更新到下一步的内容
        # 更新进度条
        global_elements.finished_step += 1
        process_rate = format(global_elements.finished_step * 100 / global_elements.total_step, '.2f')
        global_elements.emitsingle.process_rateupdataSingle.emit(process_rate)