# !/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Author    : Feng Zhaohui
# @Time      : 2019/2/22
# @File      : CU.py
# @Funcyusa  :
# @Version   : 1.0

import pyvisa
from win32api import MessageBox
import global_elements
import time
import dutcontrol
import re


class VisaCU(object):
    """
        综测仪类构建
        定义综测仪的类函数和参数
    """
    def __init__(self, device_name, visa_address, visa_address_type,  visaDLL=None, *args):
        self.device_address = visa_address
        self.device_name = device_name
        self.device_address_type = visa_address_type
        self.visaDLL = 'visa32.dll' if visaDLL is None else visaDLL

        if self.device_address_type == 'GPIB':
            if self.device_name == 'CMW500':
                self.address = "GPIB0::%s::INSTR" % self.device_address

        elif self.device_address_type == 'TCPIP':
            self.address = "TCPIP::%s::inst0::INSTR" % self.device_address
        try:
            self.resourceManager = pyvisa.ResourceManager(self.visaDLL)
        except pyvisa.errors.VisaIOError:
            MessageBox(0,
                       'Please install pyvisa dependent libraries NI-VISA first, download link http://www.ni.com/download/',
                       'Warning!!!')
            # QMessageBox.warning(self, 'Tip', 'Please select at least one band!', QMessageBox.Yes)


    def open(self):
        self.instance = self.resourceManager.open_resource(self.address)
        self.instance.timeout = 5000

    def close(self):
        if self.instance is not None:
            self.instance.close()
            self.instance = None

    def writespic(self, scpistr, timesleep = 0.01):
        # 重新定义SCPI写入方法
        self.instance.write(scpistr)
        time_now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        global_elements.emitsingle.updataScpiUI.emit(time_now + '   ' + self.device_name + ': -> ' + scpistr)
        time.sleep(timesleep)
        scpiResutl = self.instance.query("*OPC?")
        time.sleep(0.01)
        time_now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        global_elements.emitsingle.updataScpiUI.emit(time_now + '   ' + self.device_name + ': -> *OPC?')
        global_elements.emitsingle.updataScpiUI.emit(time_now + '   '+self.device_name+': <- ' + scpiResutl + '\n')

    def readspic(self, scpistr):
        # 重新定义SCPI读取方法
        scpiResutl = self.instance.query(scpistr)
        time_now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        global_elements.emitsingle.updataScpiUI.emit(time_now + '   '+self.device_name+': -> ' + scpistr)
        global_elements.emitsingle.updataScpiUI.emit(time_now + '   '+self.device_name+': <- ' + scpiResutl + '\n')
        return scpiResutl


    def read_idn(self):
        idn = self.readspic("*IDN?")
        return idn

    def nr_sig_init(self):
        global_elements.emitsingle.stateupdataSingle.emit('NR sig parms init ---------------------------------')
        try:
            if self.device_name == 'CMX500':
                self.fetchoption()                                   # 查询选件
                dutcontrol.dutoff()                                  # 关闭DUT
                self.resetCU()                                       # 重置仪器,并直到重置完成（network state 返回NAV）
                self.set_lossandcom()                                # 设置线损表格及配置端口
                self.creat_netw()                                    # 创建network，直到返回状态 IDLE
                self.creat_PLMN()                                    # 创建PLMN，直到返回状态正常,然后创建 5G TrackingArea
                self.creat_nrcell()                                  # 创建 5G NR CELL(根据待测Band,初始化FDD、TDD)
        except Exception as e:
            global_elements.emitsingle.thread_exitSingle.emit('NR signaling initialization failed, program abnormal exit! Error: ' + e.__doc__)

    def nsa_sig_init(self):
        global_elements.emitsingle.stateupdataSingle.emit('NSA sig parms init ---------------------------------')
        try:
            if self.device_name == 'CMX500':
                self.fetchoption()                                   # 查询选件
                dutcontrol.dutoff()                                  # 关闭DUT
                self.resetCU()                                       # 重置仪器,并直到重置完成（network state 返回NAV）
                self.set_lossandcom()                                # 设置线损表格及配置端口
                self.creat_netw()                                    # 创建network，直到返回状态 IDLE
                self.creat_PLMN()                                    # 创建PLMN，直到返回状态正常,然后创建 TrackingArea
                self.creat_endc_cell()                                  # 创建 5G NR CELL(根据待测Band,初始化FDD、TDD)
        except Exception as e:
            global_elements.emitsingle.thread_exitSingle.emit('NSA signaling initialization failed, program abnormal exit! Error: ' + e.__doc__)

    def fetchoption(self):
        try:
            if self.device_name == 'CMX500':
                self.readspic('SYSTem:BASE:OPTion:LIST? HWOP,ALL')  # 查询选件
                self.readspic('SYSTem:BASE:OPTion:LIST? SWOP,VAL')
        except Exception as e:
            global_elements.emitsingle.thread_exitSingle.emit(
                'read the CU options method failed, program abnormal exit! Error: ' + e.__doc__)

    def set_lossandcom(self):
        # 设置线损
        try:
            state1, fre_list1, loss_list1 = global_elements.lossfilehandle('RF1')
            state2, fre_list2, loss_list2 = global_elements.lossfilehandle('RF2')
            state3, fre_list3, loss_list3 = global_elements.lossfilehandle('RF3')
            state4, fre_list4, loss_list4 = global_elements.lossfilehandle('RF4')

            if self.device_name == 'CMX500':
                # 配置NR主口  RF2COM
                loss_str2 = ''
                for fre_index in range(len(fre_list2)):
                        loss_str2 = loss_str2 + ',' + fre_list2[fre_index] + 'e6,' + loss_list2[fre_index]

                self.writespic("CONF:BASE:FDC:CTAB:CRE 'NR_MAIN_UL'" + loss_str2)
                self.writespic("CONF:BASE:FDC:CTAB:CRE 'NR_MAIN_DL'" + loss_str2)
                self.writespic('CONF:FDC:DEAC RF2C')
                self.writespic("CONF:FDC:ACT RF2C, 'NR_MAIN_UL', RX")
                self.writespic("CONF:FDC:ACT RF2C, 'NR_MAIN_DL', TX")

                # 配置NR DIV口， RF1COM
                loss_str1 = ''
                for fre_index in range(len(fre_list1)):
                    loss_str1 = loss_str1 + ',' + fre_list1[fre_index] + 'e6,' + loss_list1[fre_index]

                self.writespic("CONF:BASE:FDC:CTAB:CRE 'NR_DIV_DL'" + loss_str1)
                self.writespic('CONF:FDC:DEAC RF1C')
                self.writespic("CONF:FDC:ACT RF1C, 'NR_DIV_DL', TX")

                # 配置LTE 主口， RF4COM
                loss_str4 = ''
                for fre_index in range(len(fre_list4)):
                    loss_str4 = loss_str4 + ',' + fre_list4[fre_index] + 'e6,' + loss_list4[fre_index]

                self.writespic("CONF:BASE:FDC:CTAB:CRE 'LTE_MAIN_UL'" + loss_str4)
                self.writespic("CONF:BASE:FDC:CTAB:CRE 'LTE_MAIN_DL'" + loss_str4)
                self.writespic('CONF:FDC:DEAC RF4C')
                self.writespic("CONF:FDC:ACT RF4C, 'LTE_MAIN_UL', RX")
                self.writespic("CONF:FDC:ACT RF4C, 'LTE_MAIN_DL', TX")
        except Exception as e:
            global_elements.emitsingle.thread_exitSingle.emit('CU set path loss failed, Program abnormal exit! Error: ' + e.__doc__)

    def resetCU(self):
        global_elements.emitsingle.stateupdataSingle.emit('Reset CU ------------------------------------------')
        try:
            if self.device_name == 'CMX500':
                self.writespic('*RST')  # 重置仪器
                self.writespic('*CLS')

                result = self.readspic('FETCh:SIGNaling:TOPology:CNETwork:STATe?')  # 询问仪器network状态，直到为 NAV
                while result != 'NAV\n':
                    time.sleep(1)
                    result = self.readspic('FETCh:SIGNaling:TOPology:CNETwork:STATe?')
            global_elements.emitsingle.stateupdataSingle.emit('Reset CU successed!')

        except Exception as e:
            global_elements.emitsingle.thread_exitSingle.emit('CU reset failed, Program abnormal exit! Error: ' + e.__doc__)

    def creat_netw(self):
        # 创建network，直到返回状态 IDLE
        try:
            global_elements.emitsingle.stateupdataSingle.emit('Creat Network......')
            if self.device_name == 'CMX500':
                self.writespic('CREate:SIGNaling:TOPology:CNETwork')
                result = self.readspic('FETCh:SIGNaling:TOPology:CNETwork:STATe?')
                time.sleep(1)
                while result != 'IDLE\n':
                    time.sleep(1)
                    result = self.readspic('FETCh:SIGNaling:TOPology:CNETwork:STATe?')

            global_elements.emitsingle.stateupdataSingle.emit('Creat Network successed!')
        except Exception as e:
            global_elements.emitsingle.thread_exitSingle.emit('CU creat network failed, Program abnormal exit! Error: ' + e.__doc__)

    def creat_PLMN(self):
        # 创建PLMN，直到返回状态正常,然后创建 5G TrackingArea
        try:
            global_elements.emitsingle.stateupdataSingle.emit('Creat PLMN.....')
            if self.device_name == 'CMX500':
                result = self.readspic('CATalog:SIGNaling:TOPology:PLMN?')
                if result == '""\n':
                    self.writespic("CREate:SIGNaling:TOPology:PLMN 'Plmn1'")
                    result = self.readspic('CATalog:SIGNaling:TOPology:PLMN?')
                    while result == '""\n':
                        time.sleep(1)
                        result = self.readspic('CATalog:SIGNaling:TOPology:PLMN?')

                self.readspic("CONFigure:SIGNaling:TOPology:PLMN:INFO? 'Plmn1'")
                if global_elements.NR_type_r == 'NR_SA':
                    self.writespic("CREate:SIGNaling:TOPology:FGS 'FgsTa1','Plmn1'")      # 创建 5G TrackingArea
                    time.sleep(0.2)
                    result = self.readspic("CONFigure:SIGNaling:TOPology:FGS:INFO? 'FgsTa1'")
                elif global_elements.NR_type_r == 'NR_NSA':
                    self.writespic("CREate:SIGNaling:TOPology:EPS 'EpsTa1','Plmn1'")  # 创建 EPS TrackingArea
                    time.sleep(0.2)
                    result = self.readspic("CONFigure:SIGNaling:TOPology:EPS:INFO? 'EpsTa1'")
            global_elements.emitsingle.stateupdataSingle.emit('Creat PLMN successed!')
        except Exception as e:
            global_elements.emitsingle.thread_exitSingle.emit('CU creat PLMN failed, Program abnormal exit! Error: ' + e.__doc__)

    def creat_nrcell(self):
        # 创建 5G NR CELL
        try:
            global_elements.emitsingle.stateupdataSingle.emit('Creat NR Cell.......')
            if self.device_name == 'CMX500':
                self.writespic("CREate:SIGNaling:NRADio:CELL 'NrCell1'")
                self.writespic("ADD:SIGNaling:TOPology:FGS 'FgsTa1','NrCell1'")
                if 'FDD' in global_elements.NR_band:
                    self.writespic("CONFigure:SIGNaling:NRADio:CELL:RFS:DMODe 'NrCell1',FDD")
                else:
                    self.writespic("CONFigure:SIGNaling:NRADio:CELL:RFS:DMODe 'NrCell1',TDD")
                self.readspic("CONFigure:SIGNaling:NRADio:CELL:RFS:DMODe? 'NrCell1'")
            global_elements.emitsingle.stateupdataSingle.emit('Creat NR Cell successed!')
        except Exception as e:
            global_elements.emitsingle.thread_exitSingle.emit('CU creat NR Cell failed, Program abnormal exit! Error: ' + e.__doc__)

    def creat_endc_cell(self):
        # 创建 ENDC  CELL
        try:
            global_elements.emitsingle.stateupdataSingle.emit('Creat ENDC Cell.......')
            if self.device_name == 'CMX500':
                self.writespic("CREate:SIGNaling:LTE:CELL 'LteCell1'")     # 创建 LTE CELL
                self.writespic("ADD:SIGNaling:TOPology:EPS 'EpsTa1', 'LteCell1'")
                if 'FDD' == global_elements.NSA_LTE_DuplexMode:
                    self.writespic("CONFigure:SIGNaling:LTE:CELL:RFSettings:DMODe 'LteCell1', FDD")
                else:
                    self.writespic("CONFigure:SIGNaling:LTE:CELL:RFSettings:DMODe 'LteCell1', TDD")

                self.writespic("CREate:SIGNaling:NRADio:CELL 'NrCell1'")   # 创建 NR CELL
                self.writespic("ADD:SIGNaling:TOPology:EPS 'EpsTa1','NrCell1'")
                if 'FDD' == global_elements.NSA_NR_DuplexMode:
                    self.writespic("CONFigure:SIGNaling:NRADio:CELL:RFS:DMODe 'NrCell1',FDD")
                else:
                    self.writespic("CONFigure:SIGNaling:NRADio:CELL:RFS:DMODe 'NrCell1',TDD")

            global_elements.emitsingle.stateupdataSingle.emit('Creat ENDC Cell successed!')
        except Exception as e:
            global_elements.emitsingle.thread_exitSingle.emit('CU creat ENDC Cell failed, Program abnormal exit! Error: ' + e.__doc__)

    def SigparmsSeting(self):
        # 6_2_1的信令单元参数设置
        global_elements.emitsingle.stateupdataSingle.emit('Sig parms setting-------------------------------')
        try:
            if self.device_name == 'CMX500':
                # 提取BAND信息
                reg = re.compile(r"(?<=n)\d+")
                match = reg.search(global_elements.NR_band)
                band_num = match.group(0)
                # 提取SCS信息
                scs_num = global_elements.NR_SCS
                scs_str = 'SCS_' + scs_num
                # 提取BW信息
                if global_elements.test_case_name == 'ts138521_1 6.5.1 Occupied bandwidth':     #  6.5.1 Occupied bandwidth 在Step中BW以具体数值出现，其它项以Low Mid High出现
                    bw_num = global_elements.NR_bw
                else:
                    bw_num = global_elements.SCSBandwidthConfig_dict['xml'][global_elements.NR_band][scs_str][global_elements.NR_bw]

                bw_str = 'BW_' + bw_num
                if len(bw_num) == 1:
                    bw_num_final = '00' + bw_num
                elif len(bw_num) == 2:
                    bw_num_final = '0' + bw_num
                else:
                    bw_num_final = bw_num
                # 提取信道信息
                ch_ul_num = global_elements.ChannelConfig_dict['xml'][global_elements.NR_band][scs_str][bw_str]['UL'][global_elements.NR_ch]
                ch_dl_num = global_elements.ChannelConfig_dict['xml'][global_elements.NR_band][scs_str][bw_str]['DL'][
                    global_elements.NR_ch]
                if 'FDD' in global_elements.NR_band:
                    self.writespic("CONFigure:SIGNaling:NRADio:CELL:RFS:DMODe 'NrCell1',FDD")
                elif 'TDD' in global_elements.NR_band:
                    self.writespic("CONFigure:SIGNaling:NRADio:CELL:RFS:DMODe 'NrCell1',TDD")

                self.writespic("CONFigure:SIGNaling:NRADio:CELL:MCON:MOD 'NrCell1', Q256")
                self.writespic("CONFigure:SIGNaling:NRADio:CELL:RFS:FBINdicator 'NrCell1', " + band_num)
                self.writespic("CONFigure:SIGNaling:NRADio:CELL:RFS:DL:BWIDth 'NrCell1', B" + bw_num_final)
                self.writespic("CONFigure:SIGNaling:NRADio:CELL:RFS:SSPacing 'NrCell1', " + scs_num)
                if 'FDD' in global_elements.NR_band:
                    self.writespic("CONFigure:SIGNaling:NRADio:CELL:RFSettings:DL:OCARrier 'NrCell1'," + ch_dl_num['offsetToCarrier'])
                    self.writespic(
                        "CONFigure:SIGNaling:NRADio:CELL:RFS:DL:APOint:ARFCn 'NrCell1'," + ch_dl_num['PointACh'])

                self.writespic("CONFigure:SIGNaling:NRADio:CELL:RFSettings:UL:OCARrier 'NrCell1'," + ch_ul_num['offsetToCarrier'])
                self.writespic("CONFigure:SIGNaling:NRADio:CELL:RFS:UL:APOint:ARFCn 'NrCell1'," + ch_ul_num['PointACh'])
                self.writespic("CONFigure:SIGNaling:NRADio:CELL:POW:DL:SEPRe 'NrCell1',-73.7939248775923")
                self.writespic("CONFigure:SIGNaling:NRADio:CELL:CSSZero:CRZero 'NrCell1'," + ch_dl_num['CORESETIndex'])
                self.writespic("CONFigure:SIGNaling:NRADio:CELL:SSB:SOFFset 'NrCell1'," + ch_dl_num['KSSB'])
                self.writespic("CONFigure:SIGNaling:NRADio:CELL:SSB:PAOFfset 'NrCell1'," + ch_dl_num['offsetToPointA'])
                self.writespic("CONFigure:SIGNaling:NRADio:CELL:POWer:CONTrol:PMAX 'NrCell1', " + global_elements.NR_p_max)
                self.writespic("CONFigure:NRSub:MEAS:RFSettings:ENPower " + global_elements.NR_p_max, timesleep=5)

                if 'DFT' in global_elements.NR_Modulation:
                    self.writespic("CONFigure:NRSub:MEAS:BWPart:PUSCh:DFTPrecoding BWP0,ON")
                    self.writespic("CONFigure:SIGNaling:NRADio:CELL:PUSCh:TPRecoding 'NrCell1', DTFS")
                else:
                    self.writespic("CONFigure:NRSub:MEAS:BWPart:PUSCh:DFTPrecoding BWP0,OFF")
                    self.writespic("CONFigure:SIGNaling:NRADio:CELL:PUSCh:TPRecoding 'NrCell1', CP")
                self.readspic("syst:err:all?")

                # Go to live,直到完成
                global_elements.emitsingle.stateupdataSingle.emit("NetWork go to live......, pls wait!")
                result = self.readspic("FETCh:SIGNaling:TOPology:CNETwork:STATe?")
                if result == 'IDLE\n':
                    self.writespic("SOURce:SIGNaling:TOPology:CNETwork:ENABle ON")
                    result = self.readspic("FETCh:SIGNaling:TOPology:CNETwork:STATe?")
                    while result != 'RUNN\n':
                        time.sleep(1)
                        result = self.readspic("FETCh:SIGNaling:TOPology:CNETwork:STATe?")

                # 打开cell
                result = self.readspic("SOURce:SIGNaling:NRADio:CELL:STATe? 'NrCell1'")
                if result != 'ON\n':
                    self.writespic("SOURCe:SIGNaling:NRADio:CELL:STATe 'NrCell1', ON")
                    # time.sleep(2)
                    result = self.readspic("SOURce:SIGNaling:NRADio:CELL:STATe? 'NrCell1'")
                    while result != 'ON\n':
                        time.sleep(1)
                        result = self.readspic("SOURce:SIGNaling:NRADio:CELL:STATe? 'NrCell1'")
            global_elements.emitsingle.stateupdataSingle.emit('Sig parms setting completed!')
        except Exception as e:
            global_elements.emitsingle.thread_exitSingle.emit('SigparmsSeting failed, Program abnormal exit! Error: ' + e.__doc__)

    def SigparmsSeting_NSA(self):
        global_elements.emitsingle.stateupdataSingle.emit('NSA Sig parms setting-------------------------------')
        try:
            if self.device_name == 'CMX500':
                # 提取BAND信息
                reg = re.compile(r"(?<=n)\d+")
                lte_band_num = global_elements.NSA_LTE_band[1:]
                nr_match = reg.search(global_elements.NSA_NR_band)
                nr_band_num = nr_match.group(0)
                # 提取SCS信息
                scs_num = global_elements.NR_SCS
                scs_str = 'SCS_' + scs_num
                # 提取BW信息
                lte_bw_str = 'BW_' + global_elements.NSA_LTE_bw
                nr_bw_str = 'BW_' + global_elements.NSA_NR_bw
                lte_bw_num_final = str(int(float(global_elements.NSA_LTE_bw) * 10)).zfill(3)
                nr_bw_num_final = global_elements.NSA_NR_bw.zfill(3)

                # 提取信道信息
                nr_ch_ul_num = global_elements.ChannelConfig_dict['xml'][global_elements.NSA_NR_band][scs_str][nr_bw_str]['UL'][global_elements.NR_ch.split(',')[1]]
                nr_ch_dl_num = global_elements.ChannelConfig_dict['xml'][global_elements.NSA_NR_band][scs_str][nr_bw_str]['DL'][
                    global_elements.NR_ch.split(',')[1]]
                if global_elements.test_case_name == 'ts138521_3 6.2B.1.3 UE Maximum Output Power for Inter-Band EN-DC within FR1':
                    if int(global_elements.NR_testid) in range(1, 7):
                        p_max = str(float(global_elements.NR_p_max) - 3)
                    else:
                        p_max = global_elements.NR_p_max
                else:
                    p_max = global_elements.NR_p_max

                # 配置LTE CELL的参数
                if 'FDD' == global_elements.NSA_LTE_DuplexMode:
                    self.writespic("CONFigure:SIGNaling:LTE:CELL:RFSettings:DMODe 'LteCell1', FDD")
                elif 'TDD' == global_elements.NSA_LTE_DuplexMode:
                    self.writespic("CONFigure:SIGNaling:LTE:CELL:RFSettings:DMODe 'LteCell1', TDD")
                self.writespic("CONFigure:SIGNaling:LTE:CELL:RFS:FBINdicator 'LteCell1'," + lte_band_num)
                self.writespic("CONFigure:SIGNaling:LTE:CELL:RFS:UL:BWIDth 'LteCell1',B" + lte_bw_num_final)
                self.writespic("CONFigure:SIGNaling:LTE:CELL:RFS:DL:BWIDth 'LteCell1',B" + lte_bw_num_final)
                self.writespic("CONFigure:SIGNaling:LTE:CELL:RFS:UL:EARFcn 'LteCell1'," + global_elements.NSA_LTE_ULchannel)
                self.writespic("CONFigure:SIGNaling:LTE:CELL:RFS:DL:EARFcn 'LteCell1'," + global_elements.NSA_LTE_DLchannel)
                self.writespic("CONFigure:SIGNaling:LTE:CELL:POWer:DL:RSEPre 'LteCell1',-85")
                self.writespic("CONFigure:SIGNaling:LTE:CELL:POWer:CONTrol:TPControl 'LteCell1',CLOop")
                self.writespic("CONFigure:SIGNaling:LTE:CELL:POWer:CONTrol:TPControl:CLOop:TPOWer 'LteCell1',-20")
                self.writespic("CONFigure:SIGNaling:LTE:CELL:POWer:UL:PMAX 'LteCell1', " + p_max)
                self.writespic("CONFigure:LTE:MEAS1:RFSettings:ENPower " + p_max, timesleep=5)

                # 配置NR CELL参数
                if 'FDD' == global_elements.NSA_NR_DuplexMode:
                    self.writespic("CONFigure:SIGNaling:NRADio:CELL:RFS:DMODe 'NrCell1',FDD")
                elif 'TDD' == global_elements.NSA_NR_DuplexMode:
                    self.writespic("CONFigure:SIGNaling:NRADio:CELL:RFS:DMODe 'NrCell1',TDD")
                self.writespic("CONFigure:SIGNaling:NRADio:CELL:RFS:FBINdicator 'NrCell1', " + nr_band_num)
                self.writespic("CONFigure:SIGNaling:NRADio:CELL:RFS:DL:BWIDth 'NrCell1', B" + nr_bw_num_final)
                self.writespic("CONFigure:SIGNaling:NRADio:CELL:RFS:SSPacing 'NrCell1', " + scs_num)
                # self.writespic("")
                if 'FDD' in global_elements.NSA_NR_DuplexMode:
                    self.writespic("CONFigure:SIGNaling:NRADio:CELL:RFSettings:DL:OCARrier 'NrCell1'," + nr_ch_dl_num['offsetToCarrier'])
                    self.writespic(
                        "CONFigure:SIGNaling:NRADio:CELL:RFS:DL:APOint:ARFCn 'NrCell1'," + nr_ch_dl_num['PointACh'])

                self.writespic("CONFigure:SIGNaling:NRADio:CELL:RFSettings:UL:OCARrier 'NrCell1'," + nr_ch_ul_num['offsetToCarrier'])
                self.writespic("CONFigure:SIGNaling:NRADio:CELL:RFS:UL:APOint:ARFCn 'NrCell1'," + nr_ch_ul_num['PointACh'])
                self.writespic("CONFigure:SIGNaling:NRADio:CELL:POW:DL:SEPRe 'NrCell1',-73.7939248775923")
                self.writespic("CONFigure:SIGNaling:NRADio:CELL:CSSZero:CRZero 'NrCell1'," + nr_ch_dl_num['CORESETIndex'])
                self.writespic("CONFigure:SIGNaling:NRADio:CELL:SSB:SOFFset 'NrCell1'," + nr_ch_dl_num['KSSB'])
                self.writespic("CONFigure:SIGNaling:NRADio:CELL:SSB:PAOFfset 'NrCell1'," + nr_ch_dl_num['offsetToPointA'])
                self.writespic("CONFigure:SIGNaling:NRADio:CELL:POWer:CONTrol:PMAX 'NrCell1', " + p_max)
                self.writespic("CONFigure:NRSub:MEAS:RFSettings:ENPower " + p_max, timesleep=5)

                if global_elements.NSA_NR_modulation != 'NA':
                    if 'DFT' in global_elements.NSA_NR_modulation:
                        self.writespic("CONFigure:NRSub:MEAS:BWPart:PUSCh:DFTPrecoding BWP0,ON")
                        self.writespic("CONFigure:SIGNaling:NRADio:CELL:PUSCh:TPRecoding 'NrCell1', DTFS")
                    else:
                        self.writespic("CONFigure:NRSub:MEAS:BWPart:PUSCh:DFTPrecoding BWP0,OFF")
                        self.writespic("CONFigure:SIGNaling:NRADio:CELL:PUSCh:TPRecoding 'NrCell1', CP")
                    self.readspic("syst:err:all?")

                # Go to live,直到完成
                global_elements.emitsingle.stateupdataSingle.emit("NetWork go to live......, pls wait!")
                result = self.readspic("FETCh:SIGNaling:TOPology:CNETwork:STATe?")
                if result == 'IDLE\n':
                    self.writespic("SOURce:SIGNaling:TOPology:CNETwork:ENABle ON")
                    result = self.readspic("FETCh:SIGNaling:TOPology:CNETwork:STATe?")
                    while result != 'RUNN\n':
                        time.sleep(1)
                        result = self.readspic("FETCh:SIGNaling:TOPology:CNETwork:STATe?")

                # 打开 LTE Cell
                result = self.readspic("SOURce:SIGNaling:LTE:CELL:STATe? 'LteCell1'")
                if result != 'ON\n':
                    self.writespic("SOURce:SIGNaling:LTE:CELL:STATe 'LteCell1', ON")
                    result = self.readspic("SOURce:SIGNaling:LTE:CELL:STATe? 'LteCell1'")
                    while result != 'ON\n':
                        time.sleep(1)
                        result = self.readspic("SOURce:SIGNaling:LTE:CELL:STATe? 'LteCell1'")
                # 打开 NR cell
                result = self.readspic("SOURce:SIGNaling:NRADio:CELL:STATe? 'NrCell1'")
                if result != 'ON\n':
                    self.writespic("SOURCe:SIGNaling:NRADio:CELL:STATe 'NrCell1', ON")
                    # time.sleep(2)
                    result = self.readspic("SOURce:SIGNaling:NRADio:CELL:STATe? 'NrCell1'")
                    while result != 'ON\n':
                        time.sleep(1)
                        result = self.readspic("SOURce:SIGNaling:NRADio:CELL:STATe? 'NrCell1'")
            global_elements.emitsingle.stateupdataSingle.emit('NSA Sig parms setting completed!')
        except Exception as e:
            global_elements.emitsingle.thread_exitSingle.emit('NSA SigparmsSeting failed, Program abnormal exit! Error: ' + e.__doc__)

    def NR_connect(self):
        global_elements.emitsingle.stateupdataSingle.emit('DUT Callsetup --------------------------------------------')
        try:
            state = True
            if self.device_name == 'CMX500':
                count = 0
                try:
                    max_reg_time = int(global_elements.dutActiveDict['xml']['DUTCONFIG']['MAXREGTIME'])
                except:
                    max_reg_time = 90
                result = self.readspic("FETCh:SIGNaling:UE:RRCState?")
                time.sleep(1)
                while result != 'CONN,OK\n':
                    count += 1
                    result = self.readspic("FETCh:SIGNaling:UE:RRCState?")
                    time.sleep(1)
                    if count >= max_reg_time:
                        global_elements.emitsingle.stateupdataSingle.emit('DUT Connect timeout!')
                        state = False
                        break

                result = self.readspic("FETCh:SIGNaling:TOPology:FGS:UE:STATe?")
            if state:
                global_elements.emitsingle.stateupdataSingle.emit('DUT connected!')
            return state          # 返回是否连接超时
        except Exception as e:
            global_elements.emitsingle.thread_exitSingle.emit('NR_connect  failed, Program abnormal exit! Error: ' + e.__doc__)

    def NSA_connect(self):
        global_elements.emitsingle.stateupdataSingle.emit('DUT Callsetup --------------------------------------------')
        try:
            state = True
            if self.device_name == 'CMX500':
                count = 0
                try:
                    max_reg_time = int(global_elements.dutActiveDict['xml']['DUTCONFIG']['MAXREGTIME'])
                except:
                    max_reg_time = 90
                result = self.readspic("FETCh:SIGNaling:TOPology:EPS:UE:STATe?")
                time.sleep(1)
                while result != 'REG,CREG\n':
                    count += 1
                    result = self.readspic("FETCh:SIGNaling:TOPology:EPS:UE:STATe?")
                    time.sleep(1)
                    if count >= max_reg_time:
                        global_elements.emitsingle.stateupdataSingle.emit('DUT Connect timeout!')
                        state = False
                        break
                self.writespic("Configure:Signaling:Lte:Ue:Nsa:Activate")            # 激活NSA

                result = self.readspic("FETCh:SIGNaling:UE:DCMode?")
                while result != 'ENDC\n':
                    time.sleep(1)
                    result = self.readspic("FETCh:SIGNaling:UE:DCMode?")
            if state:
                global_elements.emitsingle.stateupdataSingle.emit('DUT connected!')
            return state          # 返回是否连接超时
        except Exception as e:
            global_elements.emitsingle.thread_exitSingle.emit('NSA_connect  failed, Program abnormal exit! Error: ' + e.__doc__)

    def MeasParmsSetingfor6_2_1(self):
        # 6_2_1的测试参数设置
        global_elements.emitsingle.stateupdataSingle.emit('Meas parms setting for 6.2.1 -----------------------------')
        try:
            if self.device_name == 'CMX500':
                band_num, scs_num, scs_str, bw_num, bw_str, bw_num_final, ch_ul_num, ch_dl_num = self.getParams()
                self.configRFPortAndDuplexMode()
                self.measParams1(band_num, ch_ul_num, scs_num, bw_num_final, False, True, global_elements.NR_p_max)
                self.measParams2()

                self.writespic("CONFigure:NRSub:MEAS:MEValuation:RESult:PMONitor ON")
                self.writespic("CONFigure:NRSub:MEAS:MEValuation:RESult:TXM ON")
                self.writespic("SIGNaling:NRADio:CELL:POWer:CONTrol:TPControl 'NrCell1', MAX")

                self.configULMCSTable()
                modu_str, mcs_index = self.getMCSIndexandModulation()

                self.writespic("CONFigure:NRSub:MEAS1:ALLocation1:PUSCh A,14,0,ON,1,0," + modu_str)

                # global_elements.NR_MCSindex = mcs_index       # MCS的值赋值给global，用于出报告时使用
                # 配置MCS Index
                if 'FDD' in global_elements.NR_band:
                    start_index = 0
                else:
                    start_index = 8
                for i in range(start_index, 10):
                    self.writespic("CONFigure:SIGNaling:NRADio:CELL:UESCheduling:UDEFined:SASSignment:UL:MCS 'NrCell1',"+str(i)+", " + mcs_index)

                self.setDFTorCP()
                self.conULRB(bw_str, scs_str, start_index)
        except Exception as e:
            global_elements.emitsingle.thread_exitSingle.emit('MeasParmsSetingfor6_2_1  failed, Program abnormal exit! Error: ' + e.__doc__)

    def MeasParmsSetingfor6_2_2(self):
        # 6_2_1的测试参数设置
        global_elements.emitsingle.stateupdataSingle.emit('Meas parms setting for 6.2.2 -----------------------------')
        try:
            if self.device_name == 'CMX500':
                band_num, scs_num, scs_str, bw_num, bw_str, bw_num_final, ch_ul_num, ch_dl_num = self.getParams()
                self.configRFPortAndDuplexMode()
                self.measParams1(band_num, ch_ul_num, scs_num, bw_num_final, True, True, global_elements.NR_p_max)
                self.measParams2()

                self.writespic("CONFigure:NRSub:MEAS:MEValuation:RESult:PMONitor ON")
                self.writespic("CONFigure:NRSub:MEAS:MEValuation:RESult:TXM ON")
                self.writespic("SIGNaling:NRADio:CELL:POWer:CONTrol:TPControl 'NrCell1', MAX")

                self.configULMCSTable()
                modu_str, mcs_index = self.getMCSIndexandModulation()

                self.writespic("CONFigure:NRSub:MEAS1:ALLocation1:PUSCh A,14,0,ON,1,0," + modu_str)

                # global_elements.NR_MCSindex = mcs_index       # MCS的值赋值给global，用于出报告时使用
                # 配置MCS Index
                if 'FDD' in global_elements.NR_band:
                    start_index = 0
                else:
                    start_index = 8
                for i in range(start_index, 10):
                    self.writespic("CONFigure:SIGNaling:NRADio:CELL:UESCheduling:UDEFined:SASSignment:UL:MCS 'NrCell1',"+str(i)+", " + mcs_index)
                    # time.sleep(0.2)

                self.setDFTorCP()
                self.conULRB(bw_str, scs_str, start_index)
        except Exception as e:
            global_elements.emitsingle.thread_exitSingle.emit('MeasParmsSetingfor6_2_2  failed, Program abnormal exit! Error: ' + e.__doc__)

    def MeasParmsSetingfor6_2_4(self):
        # 6_2_1的测试参数设置
        global_elements.emitsingle.stateupdataSingle.emit('Meas parms setting for 6.2.4 -----------------------------')
        try:
            if self.device_name == 'CMX500':
                band_num, scs_num, scs_str, bw_num, bw_str, bw_num_final, ch_ul_num, ch_dl_num = self.getParams()
                self.configRFPortAndDuplexMode()
                if 'TDD' in global_elements.NR_band:
                    self.writespic("CONFigure:NRSub:MEAS:MEValuation:MSLot UDEF, 8")

                self.measParams1(band_num, ch_ul_num, scs_num, bw_num_final, True, True, ENPower='20')
                self.measParams2()

                self.writespic("CONFigure:NRSub:MEAS:MEValuation:RESult:EVM ON")
                self.writespic("CONFigure:NRSub:MEAS:MEValuation:RESult:TXM ON")
                self.writespic("CONFigure:NRSub:MEAS:MEValuation:RESult:EVMC ON")
                self.writespic("CONFigure:SIGNaling:NRADio:CELL:POW:UL:MERM 'NrCell1', " + global_elements.NR_p_max)
                self.writespic("CONFigure:NRSub:MEAS:RFSettings:ENPower " + global_elements.NR_p_max)
                self.writespic("CONFigure:SIGNaling:NRADio:CELL:POWer:CONTrol:TPControl 'NrCell1', CLOop")
                self.writespic("CONFigure:SIGNaling:NRADio:CELL:POWer:CONTrol:TPControl:CLOop:TPOWer 'NrCell1', " +
                               global_elements.NR_p_max)
                self.writespic("CONFigure:NRSub:MEAS:RFSettings:ENPower " + global_elements.NR_p_max)

                self.configULMCSTable()
                modu_str, mcs_index = self.getMCSIndexandModulation()

                self.writespic("CONFigure:NRSub:MEAS1:ALLocation1:PUSCh A,14,0,ON,1,0," + modu_str)

                # global_elements.NR_MCSindex = mcs_index       # MCS的值赋值给global，用于出报告时使用
                # 配置MCS Index
                if 'FDD' in global_elements.NR_band:
                    start_index = 0
                else:
                    start_index = 8
                for i in range(start_index, 10):
                    self.writespic("CONFigure:SIGNaling:NRADio:CELL:UESCheduling:UDEFined:SASSignment:UL:MCS 'NrCell1',"+str(i)+", " + mcs_index)
                    # time.sleep(0.2)

                self.setDFTorCP()
                self.conULRB(bw_str, scs_str, start_index)
        except Exception as e:
            global_elements.emitsingle.thread_exitSingle.emit('MeasParmsSetingfor6_2_4  failed, Program abnormal exit! Error: ' + e.__doc__)

    def MeasParmsSetingfor6_3_1(self):
        # 6_3_1的测试参数设置
        global_elements.emitsingle.stateupdataSingle.emit('Meas parms setting for 6.3.1 -----------------------------')
        try:
            if self.device_name == 'CMX500':
                band_num, scs_num, scs_str, bw_num, bw_str, bw_num_final, ch_ul_num, ch_dl_num = self.getParams()
                self.writespic("CONFigure:NRSub:MEAS:MEValuation:MOEXception ON")
                self.configRFPortAndDuplexMode()
                if 'TDD' in global_elements.NR_band:
                    self.writespic("CONFigure:NRSub:MEAS:MEValuation:MSLot UDEF, 8")

                self.measParams1(band_num, ch_ul_num, scs_num, bw_num_final, True, True, ENPower='-30')
                self.measParams2()

                self.writespic("CONFigure:NRSub:MEAS:MEValuation:RESult:EVM ON")
                self.writespic("CONFigure:NRSub:MEAS:MEValuation:RESult:TXM ON")
                self.writespic("CONFigure:NRSub:MEAS:MEValuation:RESult:EVMC ON")
                self.writespic("CONFigure:SIGNaling:NRADio:CELL:POWer:CONTrol:TPControl 'NrCell1', MIN")

                self.configULMCSTable()
                modu_str, mcs_index = self.getMCSIndexandModulation()

                self.writespic("CONFigure:NRSub:MEAS1:ALLocation1:PUSCh A,14,0,ON,1,0," + modu_str)

                # global_elements.NR_MCSindex = mcs_index       # MCS的值赋值给global，用于出报告时使用
                # 配置MCS Index
                if 'FDD' in global_elements.NR_band:
                    start_index = 0
                else:
                    start_index = 8

                for i in range(start_index, 10):
                    self.writespic("CONFigure:SIGNaling:NRADio:CELL:UESCheduling:UDEFined:SASSignment:UL:MCS 'NrCell1',"+str(i)+", " + mcs_index)
                    # time.sleep(0.2)

                self.writespic("CONFigure:NRSub:MEAS:BWPart:PUSCh:DFTPrecoding BWP0,ON")
                self.setDFTorCP()
                self.conULRB(bw_str, scs_str, start_index)
        except Exception as e:
            global_elements.emitsingle.thread_exitSingle.emit('MeasParmsSetingfor6_3_1  failed, Program abnormal exit!  Error: ' + e.__doc__)

    def MeasParmsSetingfor6_3_3_2(self):
        # 6_2_1的测试参数设置
        global_elements.emitsingle.stateupdataSingle.emit('Meas parms setting for 6.3.3.2 -----------------------------')
        try:
            if self.device_name == 'CMX500':
                band_num, scs_num, scs_str, bw_num, bw_str, bw_num_final, ch_ul_num, ch_dl_num = self.getParams()

                self.nr_sig_init()
                self.writespic("CONFigure:SIGNaling:NRADio:CELL:MCON:MOD 'NrCell1', Q256")
                self.writespic("CONFigure:SIGNaling:NRADio:CELL:RFS:FBINdicator 'NrCell1', " + band_num)
                self.writespic("CONFigure:SIGNaling:NRADio:CELL:RFS:DL:BWIDth 'NrCell1', B" + bw_num_final)
                self.writespic("CONFigure:SIGNaling:NRADio:CELL:RFS:SSPacing 'NrCell1', " + scs_num)
                if 'FDD' in global_elements.NR_band:
                    self.writespic(
                        "CONFigure:SIGNaling:NRADio:CELL:RFSettings:DL:OCARrier 'NrCell1'," + ch_dl_num['offsetToCarrier'])
                    self.writespic("CONFigure:SIGNaling:NRADio:CELL:RFS:DL:APOint:ARFCn 'NrCell1'," + ch_dl_num['PointACh'])
                self.writespic(
                    "CONFigure:SIGNaling:NRADio:CELL:RFSettings:UL:OCARrier 'NrCell1'," + ch_ul_num['offsetToCarrier'])
                self.writespic("CONFigure:SIGNaling:NRADio:CELL:RFS:UL:APOint:ARFCn 'NrCell1'," + ch_ul_num['PointACh'])
                if 'FDD' in global_elements.NR_band:
                    self.writespic("CONFigure:SIGNaling:NRADio:CELL:POW:DL:SEPRe 'NrCell1',-85")
                else:
                    self.writespic("CONFigure:SIGNaling:NRADio:CELL:POW:DL:SEPRe 'NrCell1',-81.9897000433602")
                self.writespic("CONFigure:SIGNaling:NRADio:CELL:CSSZero:CRZero 'NrCell1'," + ch_dl_num['CORESETIndex'])
                self.writespic("CONFigure:SIGNaling:NRADio:CELL:SSB:SOFFset 'NrCell1'," + ch_dl_num['KSSB'])
                self.writespic("CONFigure:SIGNaling:NRADio:CELL:SSB:PAOFfset 'NrCell1'," + ch_dl_num['offsetToPointA'])
                self.readspic("syst:err:all?")

                # Go to live,直到完成
                result = self.readspic("FETCh:SIGNaling:TOPology:CNETwork:STATe?")
                if result == 'IDLE\n':
                    self.writespic("SOURce:SIGNaling:TOPology:CNETwork:ENABle ON")
                    result = self.readspic("FETCh:SIGNaling:TOPology:CNETwork:STATe?")
                    while result != 'RUNN\n':
                        time.sleep(1)
                        result = self.readspic("FETCh:SIGNaling:TOPology:CNETwork:STATe?")

                if 'DFT' in global_elements.NR_Modulation:
                    self.writespic("CONFigure:NRSub:MEAS:BWPart:PUSCh:DFTPrecoding BWP0,ON")
                    self.writespic("CONFigure:SIGNaling:NRADio:CELL:PUSCh:TPRecoding 'NrCell1', DTFS")
                else:
                    self.writespic("CONFigure:NRSub:MEAS:BWPart:PUSCh:DFTPrecoding BWP0,OFF")
                    self.writespic("CONFigure:SIGNaling:NRADio:CELL:PUSCh:TPRecoding 'NrCell1', CP")

                self.configULMCSTable()
                modu_str, mcs_index = self.getMCSIndexandModulation()

                self.writespic("CONFigure:NRSub:MEAS1:ALLocation1:PUSCh A,14,0,ON,1,0," + modu_str)

                # 配置RB
                rb_str = '_'.join(global_elements.NR_RBAllocation.split(' '))
                if 'DFT' in global_elements.NR_Modulation:
                    wave_type_str = 'DFT_s'
                else:
                    wave_type_str = 'CP'
                rb_config_list = global_elements.RBConfig_dict['xml'][bw_str][scs_str][wave_type_str][rb_str].split('@')

                if 'FDD' in global_elements.NR_band:
                    start_index = 0
                else:
                    start_index = 8
                for j in range(start_index, 10):
                    self.writespic(
                        "CONFigure:SIGNaling:NRADio:CELL:UESCheduling:UDEFined:SASSignment:UL:RB 'NrCell1'," + str(
                            j) + ", " + rb_config_list[0] + ", " + rb_config_list[1])

                if 'FDD' in global_elements.NR_band:
                    self.writespic("CONFigure:SIGNaling:NRADio:CELL:POWer:CONTrol:SPBPower 'NrCell1', 18")
                else:
                    self.writespic("CONFigure:SIGNaling:NRADio:CELL:POWer:CONTrol:SPBPower 'NrCell1', 21")
                self.writespic("CONFigure:SIGNaling:NRADio:CELL:POWer:CONTrol:TPControl 'NrCell1', KEEP")
                if 'TDD' in global_elements.NR_band:
                    self.writespic("CONFigure:SIGNaling:NRADio:CELL:TDD:PATTern1:PERiodicity 'NrCell1', P5")
                    self.writespic("CONFigure:SIGNaling:NRADio:CELL:TDD:PATTern1:DL:NSLots 'NrCell1', 6")
                    self.writespic("CONFigure:SIGNaling:NRADio:CELL:TDD:PATTern1:UL:NSLots 'NrCell1', 3")
                    self.writespic("CONFigure:SIGNaling:NRADio:CELL:TDD:PATTern1:DL:FSSYmbol 'NrCell1', 6")
                    self.writespic("CONFigure:SIGNaling:NRADio:CELL:TDD:PATTern1:UL:FSSYmbol 'NrCell1', 4")
                self.writespic("TRIGger:NRSub:MEAS:MEValuation:SOURce 'Base1: NR Trigger'")
                self.writespic("CONFigure:SIGNaling:NRADio:CELL:POWer:CONTrol:PNWGrant 'NrCell1', -100")
                # 打开cell
                result = self.readspic("SOURce:SIGNaling:NRADio:CELL:STATe? 'NrCell1'")
                if result != 'ON\n':
                    self.writespic("SOURCe:SIGNaling:NRADio:CELL:STATe 'NrCell1', ON")
                    # time.sleep(2)
                    result = self.readspic("SOURce:SIGNaling:NRADio:CELL:STATe? 'NrCell1'")
                    while result != 'ON\n':
                        time.sleep(1)
                        result = self.readspic("SOURce:SIGNaling:NRADio:CELL:STATe? 'NrCell1'")

                dutcontrol.duton()
                state = self.NR_connect()
                time.sleep(1)
                if state:
                    if 'FDD' in global_elements.NR_band:
                        for i in range(9):
                            self.writespic("CONF:SIGN:NRAD:CELL:UESCheduling:UDEFined:SASSignment:DL:ENABle 'NrCell1'," + str(i + 1) + ", OFF")
                        for j in range(9):
                            if j == 8:
                                self.writespic("CONF:SIGN:NRAD:CELL:UESCheduling:UDEFined:SASSignment:UL:ENABle 'NrCell1', 9, OFF")
                            else:
                                self.writespic("CONF:SIGN:NRAD:CELL:UESCheduling:UDEFined:SASSignment:UL:ENABle 'NrCell1',"+str(j)+", OFF")
                    elif 'TDD' in global_elements.NR_band:
                        for i in range(7):
                            self.writespic("CONF:SIGN:NRAD:CELL:UESCheduling:UDEFined:SASSignment:DL:ENABle 'NrCell1'," + str(i) + ", OFF")
                        self.writespic("CONF:SIGN:NRAD:CELL:UESCheduling:UDEFined:SASSignment:UL:ENABle 'NrCell1', 7, OFF")
                        self.writespic("CONF:SIGN:NRAD:CELL:UESCheduling:UDEFined:SASSignment:UL:ENABle 'NrCell1', 9, OFF")

                    self.writespic("ROUTe:NRSub:MEAS:SCENario:SALone RF2C, RX1")
                    if 'FDD' in global_elements.NR_band:
                        self.writespic("CONFigure:NRSub:MEAS:SPATH NETW")
                    elif 'TDD' in global_elements.NR_band:
                        self.writespic("CONFigure:NRSub:MEAS:MEValuation:DMOD TDD")
                        self.writespic("CONFigure:NRSub:MEAS:BAND OB" + band_num)
                        self.writespic("CONFigure:NRSub:MEAS:RFSettings:FREQuency " + ch_ul_num['CarrierCentreFre'] + 'e6')
                    self.writespic("CONFigure:NRSub:MEAS:RFSettings:UMARgin 12")
                    self.writespic("CONFigure:NRSub:MEAS:MEValuation:SCOunt:MODulation 3")
                    self.writespic("CONFigure:NRSub:MEAS:MEValuation:SCOunt:POWer 3")
                    self.writespic("CONFigure:NRSub:MEAS:MEValuation:SCOunt:SPEC:ACLR 3")
                    self.writespic("CONFigure:NRSub:MEAS:MEValuation:SCOunt:SPEC:SEM 3")
                    if 'TDD' in global_elements.NR_band:
                        self.writespic("CONFigure:NRSub:MEAS:MEValuation:BWConfig S" + scs_num + "K, B" + bw_num_final)
                    self.writespic("CONFigure:NRSub:MEAS:TXBWidth:OFFSet " + ch_ul_num['offsetToCarrier'])
                    self.writespic("CONFigure:NRSub:MEAS:MEValuation:PCOMp CAF, KEEP")

                    self.writespic("CONFigure:NRSub:MEAS:MEValuation:REPetition SING")
                    self.writespic("TRIGger:NRSub:MEAS:MEValuation:SOURce 'Base1: NR Trigger'")
                    self.writespic("CONFigure:NRSub:MEAS:MEValuation:MSLot UDEF, 8")
                    self.writespic("CONFigure:NRSub:MEAS:MEValuation:RESult:ALL OFF,OFF,OFF,OFF,OFF,OFF,OFF,OFF,OFF,OFF,OFF,OFF")
                    self.writespic("CONFigure:NRSub:MEAS:MEValuation:RESult:PDYN ON")
                    self.writespic("CONFigure:NRSub:MEAS:MEValuation:RESult:TXM ON")
                    self.writespic("CONFigure:NRSub:MEAS:MEValuation:SCOunt:POWer 10")
                    exp_power = global_elements.expPower_onoffpower[global_elements.NR_SCS][global_elements.NR_bw_num]
                    self.writespic("CONFigure:NRSub:MEAS:RFSettings:ENPower " + exp_power)
                    self.writespic("CONFigure:NRSub:MEAS:MEValuation:PCOMp CAF, KEEP")
                    time.sleep(5)

                    self.writespic("INITiate:NRSub:MEAS:MEValuation")
                    result = self.readspic("FETCh:NRSub:MEAS:MEValuation:STATe?")
                    while result != 'RDY\n':
                        time.sleep(1)
                        result = self.readspic("FETCh:NRSub:MEAS:MEValuation:STATe?")

                    onpower_result = self.readspic("FETCh:NRSub:MEAS:MEValuation:PDYNamics:AVERage?")
                    try:
                        onpower_result_final = str(format(eval(onpower_result.split(',')[3]), '.2f'))
                    except:
                        onpower_result_final = '-999'

                    self.writespic("CONFigure:NRSub:MEAS:RFSettings:ENPower -20")
                    self.writespic("CONFigure:NRSub:MEAS:MEValuation:MOEXception ON")
                    self.writespic("INITiate:NRSub:MEAS:MEValuation")
                    result = self.readspic('FETCh:NRSub:MEAS:MEValuation:STATe?')
                    while result != 'RDY\n':
                        time.sleep(1)
                        result = self.readspic('FETCh:NRSub:MEAS:MEValuation:STATe?')

                    off_power = self.readspic("FETCh:NRSub:MEAS:MEValuation:PDYNamics:AVERage?")
                    try:
                        off_power_before = str(format(eval(off_power.split(',')[2]), '.2f'))
                    except:
                        off_power_before = '-999'
                    try:
                        off_power_after = str(format(eval(off_power.split(',')[5]), '.2f'))
                    except:
                        off_power_after = '-999'
                else:
                    onpower_result_final = '-999'
                    off_power_before = '-999'
                    off_power_after = '-999'
                    global_elements.NR_remark_r = 'DUT connect timeout!'

                return onpower_result_final, off_power_before, off_power_after
        except Exception as e:
            global_elements.emitsingle.thread_exitSingle.emit('MeasParmsSetingfor6_3_3_2  failed, Program abnormal exit! Error: ' + e.__doc__)

    def MeasParmsSetingfor6_4_1(self):
        # 6_4_1的测试参数设置
        global_elements.emitsingle.stateupdataSingle.emit('Meas parms setting for 6.4.1 -----------------------------')
        try:
            if self.device_name == 'CMX500':
                band_num, scs_num, scs_str, bw_num, bw_str, bw_num_final, ch_ul_num, ch_dl_num = self.getParams()
                self.configRFPortAndDuplexMode()
                if 'FDD' in global_elements.NR_band:
                    DLleve_str = "-84.7712125471966"
                else:
                    DLleve_str = "-95.1534389308838"
                self.measParams1(band_num, ch_ul_num, scs_num, bw_num_final, True, True, global_elements.NR_p_max, DLLevl=DLleve_str)

                self.writespic("TRIGger:NRSub:MEAS:MEValuation:SOURce 'Base1: NR Trigger'")
                self.measParams2()

                self.writespic("CONFigure:NRSub:MEAS:MEValuation:RESult:TXM ON")
                self.writespic("CONFigure:NRSub:MEAS:MEValuation:RESult:EVM ON")
                self.writespic("CONFigure:NRSub:MEAS:MEValuation:RESult:EVMC ON")
                self.writespic("SIGNaling:NRADio:CELL:POWer:CONTrol:TPControl 'NrCell1', MAX")
                self.configULMCSTable()
                modu_str, mcs_index = self.getMCSIndexandModulation()

                self.writespic("CONFigure:NRSub:MEAS1:ALLocation1:PUSCh A,14,0,ON,1,0," + modu_str)

                # 配置下行
                if 'FDD' in global_elements.NR_band:
                    end_index = 10
                    start_index = 0
                else:
                    end_index = 7
                    start_index = 8
                for i in range(end_index):
                    self.writespic("CONFigure:SIGNaling:NRADio:CELL:UESCheduling:UDEFined:SASSignment:DL:MCS 'NrCell1'," + str(i) + ", 2")
                result = self.readspic("SYSTem:ERRor?")
                rb_config = global_elements.NR_DlRBconfig.split('@')
                for j in range(end_index):
                    self.writespic("CONFigure:SIGNaling:NRADio:CELL:UESCheduling:UDEFined:SASSignment:DL:RB 'NrCell1',"+str(j)+", "+rb_config[0]+", " + rb_config[1])

                # global_elements.NR_MCSindex = mcs_index       # MCS的值赋值给global，用于出报告时使用
                # 配置MCS Index
                for i in range(start_index, 10):
                    self.writespic("CONFigure:SIGNaling:NRADio:CELL:UESCheduling:UDEFined:SASSignment:UL:MCS 'NrCell1',"+str(i)+", " + mcs_index)

                self.setDFTorCP()

                # 配置RB
                rb_str = global_elements.UlRBConfig_dict['xml'][global_elements.NR_band][scs_str][bw_str]
                rb_config_list = rb_str.split('@')

                for j in range(start_index, 10):
                    self.writespic("CONFigure:SIGNaling:NRADio:CELL:UESCheduling:UDEFined:SASSignment:UL:RB 'NrCell1',"+str(j)+", "+rb_config_list[0]+", " + rb_config_list[1])
        except Exception as e:
            global_elements.emitsingle.thread_exitSingle.emit('MeasParmsSetingfor6_4_1  failed, Program abnormal exit! Error: ' + e.__doc__)

    def MeasParmsSetingfor6_4_2_1_pusch(self, Pexp):
        # 6_2_1的测试参数设置
        global_elements.emitsingle.stateupdataSingle.emit('Meas parms setting for 6.4.2.1 -----------------------------')
        try:
            if self.device_name == 'CMX500':
                if 'TDD' in global_elements.NR_band:
                    DLLevel = '-95.1534389308838'
                else:
                    DLLevel = '-84.5939248775923'
                band_num, scs_num, scs_str, bw_num, bw_str, bw_num_final, ch_ul_num, ch_dl_num = self.getParams()
                self.configRFPortAndDuplexMode()
                self.measParams1(band_num, ch_ul_num, scs_num, bw_num_final, True, False , global_elements.NR_p_max, DLLevl= DLLevel)
                self.measParams2()

                self.writespic("CONFigure:NRSub:MEAS:MEValuation:RESult:TXM ON")
                self.writespic("CONFigure:NRSub:MEAS:MEValuation:RESult:EVM ON")
                self.writespic("CONFigure:NRSub:MEAS:MEValuation:RESult:EVMC ON")

                if Pexp == global_elements.NR_p_max:
                    self.writespic("SIGNaling:NRADio:CELL:POWer:CONTrol:TPControl 'NrCell1', MAX")
                    self.writespic("CONFigure:NRSub:MEAS:RFSettings:ENPower " + global_elements.NR_p_max, timesleep=5)
                else:
                    self.writespic("CONFigure:SIGNaling:NRADio:CELL:POWer:CONTrol:TPControl 'NrCell1', CLOop")
                    self.writespic("CONFigure:SIGNaling:NRADio:CELL:POWer:CONTrol:TPControl:CLOop:TPOWer 'NrCell1', " + Pexp)
                    self.writespic("CONFigure:NRSub:MEAS:RFSettings:ENPower " + Pexp, timesleep=5)

                self.configULMCSTable()
                modu_str, mcs_index = self.getMCSIndexandModulation()

                self.writespic("CONFigure:NRSub:MEAS1:ALLocation1:PUSCh A,14,0,ON,1,0," + modu_str)

                # global_elements.NR_MCSindex = mcs_index       # MCS的值赋值给global，用于出报告时使用
                # 配置MCS Index
                if 'FDD' in global_elements.NR_band:
                    start_index = 0
                else:
                    start_index = 8
                for i in range(start_index, 10):
                    self.writespic("CONFigure:SIGNaling:NRADio:CELL:UESCheduling:UDEFined:SASSignment:UL:MCS 'NrCell1',"+str(i)+", " + mcs_index)
                    # time.sleep(0.2)

                self.setDFTorCP()
                self.conULRB(bw_str, scs_str, start_index)
        except Exception as e:
            global_elements.emitsingle.thread_exitSingle.emit('MeasParmsSetingfor6_4_2_1  failed, Program abnormal exit! Error: ' + e.__doc__)

    def MeasParmsSetingfor6_4_2_2(self):
        # 6_4_2_2的测试参数设置
        global_elements.emitsingle.stateupdataSingle.emit('Meas parms setting for 6.4.2.2 -----------------------------')
        try:
            if self.device_name == 'CMX500':
                band_num, scs_num, scs_str, bw_num, bw_str, bw_num_final, ch_ul_num, ch_dl_num = self.getParams()
                self.configRFPortAndDuplexMode()
                if 'FDD' in global_elements.NR_band:
                    DLlevel_str = '-84.7712125471966'
                else:
                    DLlevel_str = '-92.0303288701471'
                self.measParams1(band_num, ch_ul_num, scs_num, bw_num_final, True, False, global_elements.NR_p_max, DLLevl=DLlevel_str)
                self.measParams2()

                self.writespic("CONFigure:NRSub:MEAS:MEValuation:RESult:TXM ON")
                self.writespic("CONFigure:NRSub:MEAS:MEValuation:RESult:EVM ON")
                self.writespic("CONFigure:NRSub:MEAS:MEValuation:RESult:EVMC ON")
                self.writespic("CONFigure:SIGNaling:NRADio:CELL:POWer:CONTrol:TPControl 'NrCell1', CLOop")
                self.writespic("CONFigure:SIGNaling:NRADio:CELL:POWer:CONTrol:TPControl:CLOop:TPOWer 'NrCell1', " + global_elements.NR_Pexp)
                self.writespic("CONFigure:NRSub:MEAS:RFSettings:ENPower " + global_elements.NR_Pexp, timesleep=5)

                self.configULMCSTable()
                modu_str, mcs_index = self.getMCSIndexandModulation()

                self.writespic("CONFigure:NRSub:MEAS1:ALLocation1:PUSCh A,14,0,ON,1,0," + modu_str)

                # global_elements.NR_MCSindex = mcs_index       # MCS的值赋值给global，用于出报告时使用
                # 配置MCS Index
                if 'FDD' in global_elements.NR_band:
                    start_index = 0
                else:
                    start_index = 8
                for i in range(start_index, 10):
                    self.writespic("CONFigure:SIGNaling:NRADio:CELL:UESCheduling:UDEFined:SASSignment:UL:MCS 'NrCell1',"+str(i)+", " + mcs_index)
                    # time.sleep(0.2)

                self.setDFTorCP()
                self.conULRB(bw_str, scs_str, start_index)
        except Exception as e:
            global_elements.emitsingle.thread_exitSingle.emit('MeasParmsSetingfor6_4_2_2 failed, Program abnormal exit! Error: ' + e.__doc__)

    def MeasParmsSetingfor6_4_2_3_pusch(self):
        # 6_4_2_3的测试参数设置
        global_elements.emitsingle.stateupdataSingle.emit('Meas parms setting for 6.4.2.3(PUSCH) -----------------------------')
        try:
            isError = False
            if self.device_name == 'CMX500':
                band_num, scs_num, scs_str, bw_num, bw_str, bw_num_final, ch_ul_num, ch_dl_num = self.getParams()
                self.configRFPortAndDuplexMode()
                self.measParams1(band_num, ch_ul_num, scs_num, bw_num_final, True, False, global_elements.NR_p_max)
                self.measParams2()

                self.writespic("CONFigure:NRSub:MEAS:MEValuation:RESult:TXM ON")
                self.writespic("CONFigure:NRSub:MEAS:MEValuation:RESult:EVM ON")
                self.writespic("CONFigure:NRSub:MEAS:MEValuation:RESult:EVMC ON")
                self.writespic("CONFigure:NRSub:MEAS:MEValuation:RESult:IEMissions ON")
                self.writespic("CONFigure:SIGNaling:NRADio:CELL:POWer:CONTrol:TPControl 'NrCell1', CLOop")
                self.writespic("CONFigure:SIGNaling:NRADio:CELL:POWer:CONTrol:TPControl:CLOop:TPOWer 'NrCell1', " + global_elements.NR_Pexp)
                self.writespic("CONFigure:NRSub:MEAS:RFSettings:ENPower " + global_elements.NR_Pexp, timesleep=5)

                self.writespic("CONFigure:SIGNaling:NRADio:CELL:UESCheduling:UDEFined:UL:MCSTable 'NrCell1', Q64")
                self.writespic("CONFigure:NRSub:MEAS1:ALLocation1:PUSCh A,14,0,ON,1,0,Q64")
                if 'FDD' in global_elements.NR_band:
                    start_index = 0
                else:
                    start_index = 8
                for i in range(start_index, 10):
                    self.writespic("CONFigure:SIGNaling:NRADio:CELL:UESCheduling:UDEFined:SASSignment:UL:MCS 'NrCell1',"+str(i)+", 3")
                    result = self.readspic("SYSTem:ERRor?")
                    if result.split(',')[0] != '0':
                        global_elements.emitsingle.stateupdataSingle.emit("CU receive SCPI error, Reset CU!")
                        isError = True
                        return isError


                if 'DFT' in global_elements.NR_Modulation:
                    self.writespic("CONFigure:NRSub:MEAS:BWPart:PUSCh:DFTPrecoding BWP0,ON")
                    self.writespic("CONFigure:SIGNaling:NRADio:CELL:PUSCh:TPRecoding 'NrCell1', DTFS")
                    if '256 QAM' in global_elements.NR_Modulation:
                        self.writespic("CONFigure:SIGNaling:NRADio:CELL:PUSCh:DTFS:MCSTable 'NrCell1', Q256")
                    else:
                        self.writespic("CONFigure:SIGNaling:NRADio:CELL:PUSCh:DTFS:MCSTable 'NrCell1', Q64")
                    result = self.readspic("SYSTem:ERRor?")
                    if result.split(',')[0] != '0':
                        global_elements.emitsingle.stateupdataSingle.emit("CU receive SCPI error, Reset CU!")
                        isError = True
                        return isError
                else:
                    self.writespic("CONFigure:NRSub:MEAS:BWPart:PUSCh:DFTPrecoding BWP0,OFF", timesleep=3)
                    result = self.readspic("SYSTem:ERRor?")
                    if result.split(',')[0] != '0':
                        global_elements.emitsingle.stateupdataSingle.emit("CU receive SCPI error, Reset CU!")
                        isError = True
                        return isError
                    self.writespic("CONFigure:SIGNaling:NRADio:CELL:PUSCh:TPRecoding 'NrCell1', CP")
                    result = self.readspic("SYSTem:ERRor?")
                    if result.split(',')[0] != '0':
                        global_elements.emitsingle.stateupdataSingle.emit("CU receive SCPI error, Reset CU!")
                        isError = True
                        return isError

                self.configULMCSTable()

                result = self.readspic("SYSTem:ERRor?")
                if result.split(',')[0] != '0':
                    global_elements.emitsingle.stateupdataSingle.emit("CU receive SCPI error, Reset CU!")
                    isError = True
                    return isError

                modu_str, mcs_index = self.getMCSIndexandModulation()

                self.writespic("CONFigure:NRSub:MEAS1:ALLocation1:PUSCh A,14,0,ON,1,0," + modu_str)
                result = self.readspic("SYSTem:ERRor?")
                if result.split(',')[0] != '0':
                    global_elements.emitsingle.stateupdataSingle.emit("CU receive SCPI error, Reset CU!")
                    isError = True
                    return isError

                # global_elements.NR_MCSindex = mcs_index       # MCS的值赋值给global，用于出报告时使用
                # 配置MCS Index
                for i in range(start_index, 10):
                    self.writespic("CONFigure:SIGNaling:NRADio:CELL:UESCheduling:UDEFined:SASSignment:UL:MCS 'NrCell1',"+str(i)+", " + mcs_index)
                    result = self.readspic("SYSTem:ERRor?")
                    if result.split(',')[0] != '0':
                        global_elements.emitsingle.stateupdataSingle.emit("CU receive SCPI error, Reset CU!")
                        isError = True
                        return isError

                # 配置RB
                rb_str = '_'.join(global_elements.NR_RBAllocation.split(' '))
                if 'DFT' in global_elements.NR_Modulation:
                    wave_type_str = 'DFT_s'
                else:
                    wave_type_str = 'CP'
                rb_config_list = global_elements.RBConfig_dict['xml'][bw_str][scs_str][wave_type_str][rb_str].split('@')

                for j in range(start_index, 10):
                    self.writespic("CONFigure:SIGNaling:NRADio:CELL:UESCheduling:UDEFined:SASSignment:UL:RB 'NrCell1',"+str(j)+", "+rb_config_list[0]+", " + rb_config_list[1])
                    result = self.readspic("SYSTem:ERRor?")
                    if result.split(',')[0] != '0':
                        global_elements.emitsingle.stateupdataSingle.emit("CU receive SCPI error, Reset CU!")
                        isError = True
                        return isError

                return isError
        except Exception as e:
            global_elements.emitsingle.thread_exitSingle.emit('MeasParmsSetingfor6_4_2_3_pusch failed, Program abnormal exit! Error: ' + e.__doc__)

    def MeasParmsSetingfor6_4_2_4(self):
        # 6_2_1的测试参数设置
        global_elements.emitsingle.stateupdataSingle.emit('Meas parms setting for 6.4.2.4 -----------------------------')
        try:
            if self.device_name == 'CMX500':
                band_num, scs_num, scs_str, bw_num, bw_str, bw_num_final, ch_ul_num, ch_dl_num = self.getParams()
                self.configRFPortAndDuplexMode()
                self.measParams1(band_num, ch_ul_num, scs_num, bw_num_final, True, True, global_elements.NR_p_max)
                self.measParams2()

                self.writespic("CONFigure:NRSub:MEAS:MEValuation:RESult:TXM ON")
                self.writespic("CONFigure:NRSub:MEAS:MEValuation:RESult:ESFL ON")
                self.writespic("CONFigure:NRSub:MEAS:RFSettings:ENPower " + global_elements.NR_p_max)
                self.writespic("SIGNaling:NRADio:CELL:POWer:CONTrol:TPControl 'NrCell1', MAX")

                self.configULMCSTable()
                modu_str, mcs_index = self.getMCSIndexandModulation()

                self.writespic("CONFigure:NRSub:MEAS1:ALLocation1:PUSCh A,14,0,ON,1,0," + modu_str)

                # global_elements.NR_MCSindex = mcs_index       # MCS的值赋值给global，用于出报告时使用
                # 配置MCS Index
                if 'FDD' in global_elements.NR_band:
                    start_index = 0
                else:
                    start_index = 8
                for i in range(start_index, 10):
                    self.writespic("CONFigure:SIGNaling:NRADio:CELL:UESCheduling:UDEFined:SASSignment:UL:MCS 'NrCell1',"+str(i)+", " + mcs_index)
                    # time.sleep(0.2)

                self.setDFTorCP()
                self.conULRB(bw_str, scs_str, start_index)
        except Exception as e:
            global_elements.emitsingle.thread_exitSingle.emit('MeasParmsSetingfor6_4_2_4  failed, Program abnormal exit! Error: ' + e.__doc__)

    def MeasParmsSetingfor6_4_2_5(self):
        # 6_2_1的测试参数设置
        global_elements.emitsingle.stateupdataSingle.emit('Meas parms setting for 6.4.2.5 -----------------------------')
        try:
            if self.device_name == 'CMX500':
                band_num, scs_num, scs_str, bw_num, bw_str, bw_num_final, ch_ul_num, ch_dl_num = self.getParams()
                self.configRFPortAndDuplexMode()
                self.measParams1(band_num,ch_ul_num, scs_num, bw_num_final, True, False, global_elements.NR_p_max)
                self.measParams2()

                self.writespic("CONFigure:NRSub:MEAS:MEValuation:RESult:TXM ON")
                self.writespic("CONFigure:NRSub:MEAS:MEValuation:RESult:ESFL ON")
                self.writespic("CONFigure:NRSub:MEAS:RFSettings:ENPower " + global_elements.NR_p_max)
                self.writespic("SIGNaling:NRADio:CELL:POWer:CONTrol:TPControl 'NrCell1', MAX")

                self.configULMCSTable()
                modu_str, mcs_index = self.getMCSIndexandModulation()

                self.writespic("CONFigure:NRSub:MEAS1:ALLocation1:PUSCh A,14,0,ON,1,0," + modu_str)

                # global_elements.NR_MCSindex = mcs_index       # MCS的值赋值给global，用于出报告时使用
                # 配置MCS Index
                if 'FDD' in global_elements.NR_band:
                    start_index = 0
                else:
                    start_index = 8
                for i in range(start_index, 10):
                    self.writespic("CONFigure:SIGNaling:NRADio:CELL:UESCheduling:UDEFined:SASSignment:UL:MCS 'NrCell1',"+str(i)+", " + mcs_index)
                    # time.sleep(0.2)

                self.setDFTorCP()
                self.conULRB(bw_str, scs_str, start_index)
        except Exception as e:
            global_elements.emitsingle.thread_exitSingle.emit('MeasParmsSetingfor6_4_2_5  failed, Program abnormal exit! Error: ' + e.__doc__)

    def MeasParmsSetingfor6_5_1(self):
        # 6_2_1的测试参数设置
        global_elements.emitsingle.stateupdataSingle.emit('Meas parms setting for 6.5.1 -----------------------------')
        try:
            if self.device_name == 'CMX500':
                band_num, scs_num, scs_str, bw_num, bw_str, bw_num_final, ch_ul_num, ch_dl_num = self.getParams()
                self.configRFPortAndDuplexMode()
                self.measParams1(band_num, ch_ul_num, scs_num, bw_num_final, True, True, global_elements.NR_p_max)
                self.measParams2()

                self.writespic("CONFigure:NRSub:MEAS:MEValuation:RESult:TXM ON")
                self.writespic("CONFigure:NRSub:MEAS:MEValuation:RESult:EVM ON")
                self.writespic("CONFigure:NRSub:MEAS:MEValuation:RESult:EVMC ON")
                self.writespic("CONFigure:NRSub:MEAS:MEValuation:RESult:SEM ON")
                self.writespic("CONFigure:NRSub:MEAS:RFSettings:ENPower " + global_elements.NR_p_max)
                self.writespic("SIGNaling:NRADio:CELL:POWer:CONTrol:TPControl 'NrCell1', MAX")

                self.configULMCSTable()
                modu_str, mcs_index = self.getMCSIndexandModulation()

                self.writespic("CONFigure:NRSub:MEAS1:ALLocation1:PUSCh A,14,0,ON,1,0," + modu_str)

                # global_elements.NR_MCSindex = mcs_index       # MCS的值赋值给global，用于出报告时使用
                # 配置MCS Index
                if 'FDD' in global_elements.NR_band:
                    start_index = 0
                else:
                    start_index = 8
                for i in range(start_index, 10):
                    self.writespic("CONFigure:SIGNaling:NRADio:CELL:UESCheduling:UDEFined:SASSignment:UL:MCS 'NrCell1',"+str(i)+", " + mcs_index)
                    # time.sleep(0.2)

                self.setDFTorCP()
                self.conULRB(bw_str, scs_str, start_index)
        except Exception as e:
            global_elements.emitsingle.thread_exitSingle.emit('MeasParmsSetingfor6_5_1  failed, Program abnormal exit! Error: ' + e.__doc__)

    def MeasParmsSetingfor6_5_2_2(self):
        # 6_2_1的测试参数设置
        global_elements.emitsingle.stateupdataSingle.emit('Meas parms setting for 6.5.2.2 -----------------------------')
        try:
            if self.device_name == 'CMX500':
                band_num, scs_num, scs_str, bw_num, bw_str, bw_num_final, ch_ul_num, ch_dl_num = self.getParams()
                self.configRFPortAndDuplexMode()
                self.measParams1(band_num, ch_ul_num, scs_num, bw_num_final, True, True, global_elements.NR_p_max)
                self.measParams2()

                self.writespic("CONFigure:NRSub:MEAS:MEValuation:RESult:TXM ON")
                self.writespic("CONFigure:NRSub:MEAS:MEValuation:RESult:SEM ON")
                self.writespic("SIGNaling:NRADio:CELL:POWer:CONTrol:TPControl 'NrCell1', MAX")

                self.configULMCSTable()
                modu_str, mcs_index = self.getMCSIndexandModulation()

                self.writespic("CONFigure:NRSub:MEAS1:ALLocation1:PUSCh A,14,0,ON,1,0," + modu_str)

                # global_elements.NR_MCSindex = mcs_index       # MCS的值赋值给global，用于出报告时使用
                # 配置MCS Index
                if 'FDD' in global_elements.NR_band:
                    start_index = 0
                else:
                    start_index = 8
                for i in range(start_index, 10):
                    self.writespic("CONFigure:SIGNaling:NRADio:CELL:UESCheduling:UDEFined:SASSignment:UL:MCS 'NrCell1',"+str(i)+", " + mcs_index)
                    # time.sleep(0.2)

                self.setDFTorCP()
                self.conULRB(bw_str, scs_str, start_index)
        except Exception as e:
            global_elements.emitsingle.thread_exitSingle.emit('MeasParmsSetingfor6_5_2_2  failed, Program abnormal exit! Error: ' + e.__doc__)

    def MeasParmsSetingfor6_5_2_4(self):
        # 6_2_1的测试参数设置
        global_elements.emitsingle.stateupdataSingle.emit('Meas parms setting for 6.5.2.4 -----------------------------')
        try:
            if self.device_name == 'CMX500':
                band_num, scs_num, scs_str, bw_num, bw_str, bw_num_final, ch_ul_num, ch_dl_num = self.getParams()
                self.configRFPortAndDuplexMode()
                self.measParams1(band_num, ch_ul_num, scs_num, bw_num_final, True, True, global_elements.NR_p_max)
                self.measParams2()

                self.writespic("CONFigure:NRSub:MEAS:MEValuation:RESult:TXM ON")
                self.writespic("CONFigure:NRSub:MEAS:MEValuation:RESult:EVM ON")
                self.writespic("CONFigure:NRSub:MEAS:MEValuation:RESult:EVMC ON")
                self.writespic("CONFigure:NRSub:MEAS:MEValuation:RESult:ACLR ON")
                self.writespic("SIGNaling:NRADio:CELL:POWer:CONTrol:TPControl 'NrCell1', MAX")

                self.configULMCSTable()
                modu_str, mcs_index = self.getMCSIndexandModulation()

                self.writespic("CONFigure:NRSub:MEAS1:ALLocation1:PUSCh A,14,0,ON,1,0," + modu_str)

                # global_elements.NR_MCSindex = mcs_index       # MCS的值赋值给global，用于出报告时使用
                # 配置MCS Index
                if 'FDD' in global_elements.NR_band:
                    start_index = 0
                else:
                    start_index = 8
                for i in range(start_index, 10):
                    self.writespic("CONFigure:SIGNaling:NRADio:CELL:UESCheduling:UDEFined:SASSignment:UL:MCS 'NrCell1',"+str(i)+", " + mcs_index)
                    # time.sleep(0.2)

                self.setDFTorCP()
                self.conULRB(bw_str, scs_str, start_index)
        except Exception as e:
            global_elements.emitsingle.thread_exitSingle.emit('MeasParmsSetingfor6_5_2_4  failed, Program abnormal exit! Error: ' + e.__doc__)

    def MeasParmsSetingfor7_3_2(self, dl_level):
        # 6_4_1的测试参数设置
        global_elements.emitsingle.stateupdataSingle.emit('Meas parms setting for 7.3.2 -----------------------------')
        try:
            if self.device_name == 'CMX500':
                band_num, scs_num, scs_str, bw_num, bw_str, bw_num_final, ch_ul_num, ch_dl_num = self.getParams()
                self.configRFPortAndDuplexMode()
                self.measParamsDL1()

                self.configULMCSTable()
                modu_str, mcs_index = self.getMCSIndexandModulation()

                self.writespic("CONFigure:NRSub:MEAS1:ALLocation1:PUSCh A,14,0,ON,1,0," + modu_str)

                # 配置下行
                if 'FDD' in global_elements.NR_band:
                    end_index = 10
                    start_index = 0
                else:
                    end_index = 7
                    start_index = 8
                for i in range(end_index):
                    self.writespic("CONFigure:SIGNaling:NRADio:CELL:UESCheduling:UDEFined:SASSignment:DL:MCS 'NrCell1'," + str(i) + ", 2")
                result = self.readspic("SYSTem:ERRor?")
                rb_config = global_elements.NR_DlRBconfig.split('@')
                for j in range(end_index):
                    self.writespic("CONFigure:SIGNaling:NRADio:CELL:UESCheduling:UDEFined:SASSignment:DL:RB 'NrCell1',"+str(j)+", "+rb_config[0]+", " + rb_config[1])

                self.setDFTorCP()

                self.writespic("CONFigure:NRSub:MEAS1:ALLocation1:PUSCh A,14,0,ON,1,0," + modu_str)
                # 配置MCS Index
                for i in range(start_index, 10):
                    self.writespic(
                        "CONFigure:SIGNaling:NRADio:CELL:UESCheduling:UDEFined:SASSignment:UL:MCS 'NrCell1'," + str(
                            i) + ", " + mcs_index)

                # 配置RB
                rb_str = global_elements.UlRBConfig_dict['xml'][global_elements.NR_band][scs_str][bw_str]
                rb_config_list = rb_str.split('@')

                for j in range(start_index, 10):
                    self.writespic("CONFigure:SIGNaling:NRADio:CELL:UESCheduling:UDEFined:SASSignment:UL:RB 'NrCell1',"+str(j)+", "+rb_config_list[0]+", " + rb_config_list[1])

                self.writespic("CONFigure:SIGNaling:NRADio:CELL:POW:DL:TCELL 'NrCell1', " + dl_level)
                self.writespic("CONFigure:SIGNaling:MEASurement:BLER:REPetition SING")
        except Exception as e:
            global_elements.emitsingle.thread_exitSingle.emit('MeasParmsSetingfor7_3_2  failed, Program abnormal exit! Error: ' + e.__doc__)

    def MeasParmsSetingfor7_3_2_c(self):
        # 7_3_2_c的测试参数设置
        global_elements.emitsingle.stateupdataSingle.emit('Meas parms setting for 7.3.2_c -----------------------------')
        try:
            if self.device_name == 'CMX500':
                band_num, scs_num, scs_str, bw_num, bw_str, bw_num_final, ch_ul_num, ch_dl_num = self.getParams()
                self.writespic("ROUTe:NRSub:MEAS:SCENario:SALone RF2C, RX1")
                self.measParamsDL1()

                self.configULMCSTable()
                modu_str, mcs_index = self.getMCSIndexandModulation()

                self.writespic("CONFigure:NRSub:MEAS1:ALLocation1:PUSCh A,14,0,ON,1,0," + modu_str)

                # 配置下行
                if 'FDD' in global_elements.NR_band:
                    end_index = 10
                    start_index = 0
                else:
                    end_index = 7
                    start_index = 8
                for i in range(end_index):
                    self.writespic("CONFigure:SIGNaling:NRADio:CELL:UESCheduling:UDEFined:SASSignment:DL:MCS 'NrCell1'," + str(i) + ", 2")
                result = self.readspic("SYSTem:ERRor?")
                rb_config = global_elements.NR_DlRBconfig.split('@')
                for j in range(end_index):
                    self.writespic("CONFigure:SIGNaling:NRADio:CELL:UESCheduling:UDEFined:SASSignment:DL:RB 'NrCell1',"+str(j)+", "+rb_config[0]+", " + rb_config[1])

                self.setDFTorCP()

                self.writespic("CONFigure:NRSub:MEAS1:ALLocation1:PUSCh A,14,0,ON,1,0," + modu_str)
                # 配置MCS Index
                for i in range(start_index, 10):
                    self.writespic(
                        "CONFigure:SIGNaling:NRADio:CELL:UESCheduling:UDEFined:SASSignment:UL:MCS 'NrCell1'," + str(
                            i) + ", " + mcs_index)

                # 配置RB
                rb_str = global_elements.UlRBConfig_dict['xml'][global_elements.NR_band][scs_str][bw_str]
                rb_config_list = rb_str.split('@')

                for j in range(start_index, 10):
                    self.writespic("CONFigure:SIGNaling:NRADio:CELL:UESCheduling:UDEFined:SASSignment:UL:RB 'NrCell1',"+str(j)+", "+rb_config_list[0]+", " + rb_config_list[1])

        except Exception as e:
            global_elements.emitsingle.thread_exitSingle.emit('MeasParmsSetingfor7_3_2_c  failed, Program abnormal exit! Error: ' + e.__doc__)

    def MeasParmsSetingfor7_4(self, dl_level):
        # 6_4_1的测试参数设置
        global_elements.emitsingle.stateupdataSingle.emit('Meas parms setting for 7.4 -----------------------------')
        try:
            if self.device_name == 'CMX500':
                band_num, scs_num, scs_str, bw_num, bw_str, bw_num_final, ch_ul_num, ch_dl_num = self.getParams()
                self.configRFPortAndDuplexMode()
                self.measParamsDL1()
                #配置下行参数
                if '256 QAM' in global_elements.NR_DL_Modulation:
                    self.writespic("CONFigure:NRSub:MEAS1:ALLocation1:PUSCh A,14,0,ON,1,0,Q256")
                elif '64 QAM' in global_elements.NR_DL_Modulation:
                    self.writespic("CONFigure:NRSub:MEAS1:ALLocation1:PUSCh A,14,0,ON,1,0,Q64")
                #配置下行MCS Index
                if 'QPSK' in global_elements.NR_DL_Modulation:
                    dl_mcs_index = global_elements.MCSindex_dict['xml']['DL']['QPSK'].split('_')[1]
                elif '64 QAM' in global_elements.NR_DL_Modulation:
                    dl_mcs_index = global_elements.MCSindex_dict['xml']['DL']['QAM64'].split('_')[1]
                else:
                    dl_mcs_index = global_elements.MCSindex_dict['xml']['DL']['QAM256'].split('_')[1]

                if 'FDD' in global_elements.NR_band:
                    end_index = 10
                    start_index = 0
                else:
                    end_index = 7
                    start_index = 8
                for i in range(end_index):
                    self.writespic(
                        "CONFigure:SIGNaling:NRADio:CELL:UESCheduling:UDEFined:SASSignment:DL:MCS 'NrCell1'," + str(
                            i) + ", " + dl_mcs_index)

                self.readspic("SYSTem:ERRor?")

                # 配置下行RB
                rb_config = global_elements.NR_DlRBconfig.split('@')
                for j in range(end_index):
                    self.writespic(
                        "CONFigure:SIGNaling:NRADio:CELL:UESCheduling:UDEFined:SASSignment:DL:RB 'NrCell1'," + str(
                            j) + ", " + rb_config[0] + ", " + rb_config[1])

                # 配置上行参数
                self.configULMCSTable()
                modu_str, mcs_index = self.getMCSIndexandModulation()

                self.writespic("CONFigure:NRSub:MEAS1:ALLocation1:PUSCh A,14,0,ON,1,0," + modu_str)

                self.setDFTorCP()

                self.writespic("CONFigure:NRSub:MEAS1:ALLocation1:PUSCh A,14,0,ON,1,0," + modu_str)
                # 配置MCS Index
                for i in range(start_index, 10):
                    self.writespic(
                        "CONFigure:SIGNaling:NRADio:CELL:UESCheduling:UDEFined:SASSignment:UL:MCS 'NrCell1'," + str(
                            i) + ", " + mcs_index)

                # 配置RB
                rb_str = global_elements.UlRBConfig_dict['xml'][global_elements.NR_band][scs_str][bw_str]
                rb_config_list = rb_str.split('@')

                for j in range(start_index, 10):
                    self.writespic("CONFigure:SIGNaling:NRADio:CELL:UESCheduling:UDEFined:SASSignment:UL:RB 'NrCell1',"+str(j)+", "+rb_config_list[0]+", " + rb_config_list[1])

                self.writespic("CONFigure:SIGNaling:NRADio:CELL:POW:DL:TCELL 'NrCell1', " + dl_level)
                self.writespic("CONFigure:SIGNaling:MEASurement:BLER:REPetition SING")
        except Exception as e:
            global_elements.emitsingle.thread_exitSingle.emit('MeasParmsSetingfor7_4  failed, Program abnormal exit! Error: ' + e.__doc__)

    def nsa_MeasParmsSetingfor6_2b_1_3(self):
        global_elements.emitsingle.stateupdataSingle.emit('Meas parms setting for 6.2b.1.3 -----------------------------')
        try:
            if self.device_name == 'CMX500':
                self.writespic("SIGNaling:NRADio:CELL:POWer:CONTrol:TPControl 'NrCell1', MAX")
                self.writespic("SIGNaling:LTE:CELL:POWer:CONTrol:TPControl 'LteCell1', MAX")
                if 'FDD' == global_elements.NSA_NR_DuplexMode:
                    nr_start_index = 0
                else:
                    nr_start_index = 8
                if global_elements.NSA_NR_modulation != 'NA':
                    nr_modu_str, nr_mcs_index = self.getMCSIndexandModulation_NSA_NR()
                    self.writespic("CONFigure:NRSub:MEAS1:ALLocation1:PUSCh A,14,0,ON,1,0," + nr_modu_str)
                    for i in range(nr_start_index, 10):
                        self.writespic("CONFigure:SIGNaling:NRADio:CELL:UESCheduling:UDEFined:SASSignment:UL:MCS 'NrCell1',"+str(i)+", " + nr_mcs_index)
                if global_elements.NSA_NR_rb != 'NA':
                    nr_rb_config_list = global_elements.NSA_NR_rb.split('@')
                    for j in range(nr_start_index, 10):
                        self.writespic(
                            "CONFigure:SIGNaling:NRADio:CELL:UESCheduling:UDEFined:SASSignment:UL:RB 'NrCell1'," + str(
                                j) + ", " +
                            nr_rb_config_list[0] + ", " + nr_rb_config_list[1])

                if 'FDD' == global_elements.NSA_LTE_DuplexMode:
                    lte_start_index = 0
                else:
                    lte_start_index = 8
                if global_elements.NSA_LTE_modulation != 'NA':
                    lte_modu_str = self.getModulation_NSA_LTE()
                    self.writespic("CONFigure:LTE:MEAS1:MEValuation:MODulation:MSCHeme " + lte_modu_str)
                    for i in range(lte_start_index, 10):
                        self.writespic("CONFigure:SIGNaling:LTE:CELL:UESCheduling:UDEFined:SASSignment:UL:CWORd:MCS 'LteCell1',"+str(i)+", 2")

                if global_elements.NSA_LTE_rb != 'NA':
                    lte_rb_config_list = global_elements.NSA_LTE_rb.split('@')
                    for j in range(lte_start_index, 10):
                        self.writespic(
                            "CONFigure:SIGNaling:LTE:CELL:UESCheduling:UDEFined:SASSignment:UL:RB 'LteCell1'," + str(
                                j) + ", " +
                            lte_rb_config_list[0] + ", " + lte_rb_config_list[1])

                self.writespic("ROUTe:NRSub:MEAS:SCENario:SALone RF2C, RX1")
                self.writespic("ROUTe:LTE:MEAS:SCENario:SALone RF4C, RX2")
                if 'FDD' == global_elements.NSA_NR_DuplexMode:
                    self.writespic("CONFigure:NRSub:MEAS:MEValuation:DMOD FDD")
                elif 'TDD' == global_elements.NSA_NR_DuplexMode:
                    self.writespic("CONFigure:NRSub:MEAS:MEValuation:DMOD TDD")

                self.writespic("TRIGger:NRSub:MEAS:MEValuation:SOURce 'Base1: NR Trigger'")
                if 'FDD' == global_elements.NSA_LTE_DuplexMode:
                    self.writespic("CONFigure:LTE:MEAS1:MEValuation:DMOD FDD")
                elif 'TDD' == global_elements.NSA_LTE_DuplexMode:
                    self.writespic("CONFigure:LTE:MEAS1:MEValuation:DMOD TDD")
                self.writespic("TRIGger:LTE:MEAS1:MEValuation:SOURce 'Free Run (Fast Sync)'")
                reg = re.compile(r"(?<=n)\d+")
                match_nr = reg.search(global_elements.NSA_NR_band)
                nr_band_num = match_nr.group(0)
                lte_band_num = global_elements.NSA_LTE_band[1:]
                self.writespic("CONFigure:NRSub:MEAS:BAND OB" + nr_band_num)
                self.writespic("CONFigure:LTE:MEAS1:BAND OB" + lte_band_num)
                self.writespic("CONFigure:NRSub:MEAS:RFSettings:FREQuency " + global_elements.NSA_NR_ULFreq + "e6")
                self.writespic("CONFigure:LTE:MEAS1:RFSettings:FREQuency " + global_elements.NSA_LTE_ULFreq + "e6")
                self.writespic("CONFigure:NRSub:MEAS:RFSettings:ENPower " + global_elements.NR_p_max)
                self.writespic("CONFigure:NRSub:MEAS:RFSettings:UMARgin 12")
                self.writespic("CONFigure:NRSub:MEAS:MEValuation:SCOunt:MODulation 3")
                self.writespic("CONFigure:NRSub:MEAS:MEValuation:SCOunt:POWer 3")
                self.writespic("CONFigure:NRSub:MEAS:MEValuation:SCOunt:SPEC:ACLR 3")
                self.writespic("CONFigure:NRSub:MEAS:MEValuation:SCOunt:SPEC:SEM 3")
                self.writespic("CONFigure:LTE:MEAS1:RFSettings:ENPower " + global_elements.NR_p_max)
                self.writespic("CONFigure:LTE:MEAS1:RFSettings:UMARgin 12")
                self.writespic("CONFigure:LTE:MEAS1:MEValuation:SCOunt:MODulation 3")
                self.writespic("CONFigure:LTE:MEAS1:MEValuation:SCOunt:POWer 3")
                self.writespic("CONFigure:LTE:MEAS1:MEValuation:SCOunt:SPEC:ACLR 3")
                self.writespic("CONFigure:LTE:MEAS1:MEValuation:SCOunt:SPEC:SEM 3")
                # 提取SCS信息
                scs_num = global_elements.NR_SCS
                # 提取BW信息
                nr_final_bw_str = global_elements.NSA_NR_bw.zfill(3)
                self.writespic("CONFigure:NRSub:MEAS:MEValuation:BWConfig S"+scs_num+"K, B" + nr_final_bw_str)
                self.writespic("CONFigure:NRSub:MEAS:TXBWidth:OFFSet 0")
                self.writespic("CONFigure:NRSub:MEAS:MEValuation:PCOMp CAF, KEEP")

                self.writespic("CONFigure:NRSub:MEAS:MEValuation:REPetition SING")
                self.writespic("CONFigure:NRSub:MEAS:MEValuation:PUSChconfig  AUTO, A, ON, KEEP, KEEP, 14, 0, T1, SING, 2, 2")
                self.writespic("TRIGger:NRSub:MEAS:MEValuation:THReshold -20")
                self.writespic("CONFigure:NRSub:MEAS:MEValuation:RESult:ALL OFF,OFF,OFF,OFF,OFF,OFF,OFF,OFF,OFF,OFF,OFF,OFF")
                self.writespic("CONFigure:NRSub:MEAS:MEValuation:RESult:PMONitor ON")
                self.writespic("CONFigure:NRSub:MEAS:MEValuation:RESult:TXM ON")
                self.writespic("CONFigure:LTE:MEAS1:MEValuation:REPetition SING")
                self.writespic("TRIGger:LTE:MEAS1:MEValuation:THReshold -20")
                self.writespic("CONFigure:LTE:MEAS1:MEValuation:RESult:ALL OFF,OFF,OFF,OFF,OFF,OFF,OFF,OFF,OFF,OFF,OFF,OFF")
                self.writespic("CONFigure:LTE:MEAS1:MEValuation:RESult:PMONitor ON")
                self.writespic("CONFigure:LTE:MEAS1:MEValuation:RESult:TXM ON")
                if int(global_elements.NR_testid) in range(10, 16):
                    for i in range(10):
                        self.writespic("CONFigure:SIGNaling:LTE:CELL:UESCheduling:UDEFined:SASSignment:UL:ENABle 'LteCell1',"+str(i)+", OFF")
        except Exception as e:
            global_elements.emitsingle.thread_exitSingle.emit('nsa_MeasParmsSetingfor6_2b_1_3  failed, Program abnormal exit! Error: ' + e.__doc__)

    def reSetCU_and_reConnectDUT(self):
        global_elements.emitsingle.stateupdataSingle.emit('Reset CU and reconnect DUT!')
        self.nr_sig_init()
        self.SigparmsSeting()
        dutcontrol.dutoffon()  # 打开DUT
        state = self.NR_connect()  # 等待DUT连接并返回状态
        return state

    def reSetCU_and_reConnectDUT_NSA(self):
        global_elements.emitsingle.stateupdataSingle.emit('Reset CU and reconnect DUT!')
        self.nsa_sig_init()
        self.SigparmsSeting_NSA()
        dutcontrol.dutoffon()  # 打开DUT
        state = self.NSA_connect() # 等待DUT连接并返回状态
        return state

    def offCell_and_reConnectDUT(self):
        if self.device_name == 'CMX500':
            try:
                global_elements.emitsingle.stateupdataSingle.emit('OnOff NR Cell and reconnect DUT!')
                dutcontrol.dutoff()
                time.sleep(0.5)

                self.writespic("SOURCe:SIGNaling:NRADio:CELL:STATe 'NrCell1', OFF")
                self.writespic("*CLS")

                # 提取BAND信息
                reg = re.compile(r"(?<=n)\d+")
                match = reg.search(global_elements.NR_band)
                band_num = match.group(0)
                # 提取SCS信息
                scs_num = global_elements.NR_SCS
                scs_str = 'SCS_' + scs_num
                # 提取BW信息
                if global_elements.test_case_name == 'ts138521_1 6.5.1 Occupied bandwidth':  # 6.5.1 Occupied bandwidth 在Step中BW以具体数值出现，其它项以Low Mid High出现
                    bw_num = global_elements.NR_bw
                else:
                    bw_num = global_elements.SCSBandwidthConfig_dict['xml'][global_elements.NR_band][scs_str][
                        global_elements.NR_bw]

                bw_str = 'BW_' + bw_num
                if len(bw_num) == 1:
                    bw_num_final = '00' + bw_num
                elif len(bw_num) == 2:
                    bw_num_final = '0' + bw_num
                else:
                    bw_num_final = bw_num
                # 提取信道信息
                ch_ul_num = global_elements.ChannelConfig_dict['xml'][global_elements.NR_band][scs_str][bw_str]['UL'][
                    global_elements.NR_ch]
                ch_dl_num = global_elements.ChannelConfig_dict['xml'][global_elements.NR_band][scs_str][bw_str]['DL'][
                    global_elements.NR_ch]
                if 'FDD' in global_elements.NR_band:
                    self.writespic("CONFigure:SIGNaling:NRADio:CELL:RFS:DMODe 'NrCell1',FDD")
                elif 'TDD' in global_elements.NR_band:
                    self.writespic("CONFigure:SIGNaling:NRADio:CELL:RFS:DMODe 'NrCell1',TDD")

                self.writespic("CONFigure:SIGNaling:NRADio:CELL:MCON:MOD 'NrCell1', Q256")
                self.writespic("CONFigure:SIGNaling:NRADio:CELL:RFS:FBINdicator 'NrCell1', " + band_num)
                self.writespic("CONFigure:SIGNaling:NRADio:CELL:RFS:DL:BWIDth 'NrCell1', B" + bw_num_final)
                self.writespic("CONFigure:SIGNaling:NRADio:CELL:RFS:SSPacing 'NrCell1', " + scs_num)
                self.writespic(
                    "CONFigure:SIGNaling:NRADio:CELL:RFSettings:DL:OCARrier 'NrCell1'," + ch_dl_num['offsetToCarrier'])
                self.writespic("CONFigure:SIGNaling:NRADio:CELL:RFS:DL:APOint:ARFCn 'NrCell1'," + ch_dl_num['PointACh'])
                self.writespic(
                    "CONFigure:SIGNaling:NRADio:CELL:RFSettings:UL:OCARrier 'NrCell1'," + ch_ul_num['offsetToCarrier'])
                self.writespic("CONFigure:SIGNaling:NRADio:CELL:RFS:UL:APOint:ARFCn 'NrCell1'," + ch_ul_num['PointACh'])
                self.writespic("CONFigure:SIGNaling:NRADio:CELL:POW:DL:SEPRe 'NrCell1',-70")
                self.writespic("CONFigure:SIGNaling:NRADio:CELL:CSSZero:CRZero 'NrCell1'," + ch_dl_num['CORESETIndex'])
                self.writespic("CONFigure:SIGNaling:NRADio:CELL:SSB:SOFFset 'NrCell1'," + ch_dl_num['KSSB'])
                self.writespic("CONFigure:SIGNaling:NRADio:CELL:SSB:PAOFfset 'NrCell1'," + ch_dl_num['offsetToPointA'])
                self.writespic(
                    "CONFigure:SIGNaling:NRADio:CELL:POWer:CONTrol:PMAX 'NrCell1', " + global_elements.NR_p_max)
                self.writespic("CONFigure:NRSub:MEAS:RFSettings:ENPower " + global_elements.NR_p_max, timesleep=5)

                if 'DFT' in global_elements.NR_Modulation:
                    self.writespic("CONFigure:NRSub:MEAS:BWPart:PUSCh:DFTPrecoding BWP0,ON")
                    self.writespic("CONFigure:SIGNaling:NRADio:CELL:PUSCh:TPRecoding 'NrCell1', DTFS")
                else:
                    self.writespic("CONFigure:NRSub:MEAS:BWPart:PUSCh:DFTPrecoding BWP0,OFF")
                    self.writespic("CONFigure:SIGNaling:NRADio:CELL:PUSCh:TPRecoding 'NrCell1', CP")
                self.readspic("syst:err:all?")

                result = self.readspic("SOURce:SIGNaling:NRADio:CELL:STATe? 'NrCell1'")
                if result != 'ON\n':
                    self.writespic("SOURCe:SIGNaling:NRADio:CELL:STATe 'NrCell1', ON")
                    # time.sleep(2)
                    result = self.readspic("SOURce:SIGNaling:NRADio:CELL:STATe? 'NrCell1'")
                    while result != 'ON\n':
                        time.sleep(1)
                        result = self.readspic("SOURce:SIGNaling:NRADio:CELL:STATe? 'NrCell1'")

                dutcontrol.duton()
                time.sleep(1)
                state = self.checkConnectState()
                return state
            except Exception as e:
                global_elements.emitsingle.thread_exitSingle.emit(
                    'offCell_and_reConnectDUT  failed, Program abnormal exit! Error: ' + e.__doc__)


    def checkConnectState(self):
        global_elements.emitsingle.stateupdataSingle.emit('Check DUT connection state....')
        try:
            state = True
            if self.device_name == 'CMX500':
                result = self.readspic("FETCh:SIGNaling:UE:RRCState?")
                if result != 'CONN,OK\n':
                    dutcontrol.dutoffon()           # 如果不是正常连接状态，重启DUT
                    time.sleep(2)

                count = 0
                try:
                    max_reg_time = int(global_elements.dutActiveDict['xml']['DUTCONFIG']['MAXREGTIME'])
                except:
                    max_reg_time = 90

                result = self.readspic("FETCh:SIGNaling:UE:RRCState?")
                while result != 'CONN,OK\n':
                    time.sleep(1)
                    result = self.readspic("FETCh:SIGNaling:UE:RRCState?")
                    count += 1
                    if count > max_reg_time:
                        state = self.reSetCU_and_reConnectDUT()
                        if state == False:
                            global_elements.emitsingle.stateupdataSingle.emit('DUT connect retry failed!')
                            break

                if state:
                    global_elements.emitsingle.stateupdataSingle.emit('DUT Connected!')
                else:
                    global_elements.emitsingle.stateupdataSingle.emit('DUT Call Drop!')
                return state
        except Exception as e:
            global_elements.emitsingle.thread_exitSingle.emit('checkConnectState  failed, Program abnormal exit! Error: ' + e.__doc__)

    def getValue_6_2_1(self):
        # 获取测试结果
        try:
            global_elements.emitsingle.stateupdataSingle.emit('Get the value....')
            if self.device_name == 'CMX500':
                self.writespic("INITiate:NRSub:MEAS:MEValuation")
                result = self.readspic("FETCh:NRSub:MEAS:MEValuation:STATe?")
                while result != 'RDY\n':
                    time.sleep(1)
                    result = self.readspic("FETCh:NRSub:MEAS:MEValuation:STATe?")
                value_str = self.readspic("FETCh:NRSub:MEAS:MEValuation:MODulation:AVERage?")
                try:
                    power_value = str(format(eval(value_str.split(',')[17]), '.2f'))
                except:
                    power_value = '-999'

                return power_value
        except Exception as e:
            global_elements.emitsingle.thread_exitSingle.emit('getValue_6_2_1  failed, Program abnormal exit! Error: ' + e.__doc__)

    def getValue_6_2_2(self):
        # 获取测试结果
        try:
            global_elements.emitsingle.stateupdataSingle.emit('Get the value....')
            if self.device_name == 'CMX500':
                self.writespic("INITiate:NRSub:MEAS:MEValuation")
                result = self.readspic("FETCh:NRSub:MEAS:MEValuation:STATe?")
                while result != 'RDY\n':
                    time.sleep(1)
                    result = self.readspic("FETCh:NRSub:MEAS:MEValuation:STATe?")
                value_str = self.readspic("FETCh:NRSub:MEAS:MEValuation:MODulation:AVERage?")
                try:
                    power_value = str(format(eval(value_str.split(',')[17]), '.2f'))
                except:
                    power_value = '-999'

                return power_value
        except Exception as e:
            global_elements.emitsingle.thread_exitSingle.emit('getValue_6_2_2  failed, Program abnormal exit! Error: ' + e.__doc__)

    def getValue_6_2_4(self):
        # 获取测试结果
        try:
            global_elements.emitsingle.stateupdataSingle.emit('Get the value.......')
            if self.device_name == 'CMX500':
                self.writespic("INITiate:NRSub:MEAS:MEValuation")
                result = self.readspic("FETCh:NRSub:MEAS:MEValuation:STATe?")
                while result != 'RDY\n':
                    time.sleep(1)
                    result = self.readspic("FETCh:NRSub:MEAS:MEValuation:STATe?")
                value_str = self.readspic("FETCh:NRSub:MEAS:MEValuation:MODulation:AVERage?")
                try:
                    power_value = str(format(eval(value_str.split(',')[17]), '.2f'))
                except:
                    power_value = '-999'

                return power_value
        except Exception as e:
            global_elements.emitsingle.thread_exitSingle.emit('getValue_6_2_4  failed, Program abnormal exit! Error: ' +
                                                              e.__doc__)

    def getValue_6_3_1(self):
        # 获取测试结果
        try:
            global_elements.emitsingle.stateupdataSingle.emit('Get the value......')
            if self.device_name == 'CMX500':
                self.writespic("INITiate:NRSub:MEAS:MEValuation")
                result = self.readspic("FETCh:NRSub:MEAS:MEValuation:STATe?")
                while result != 'RDY\n':
                    time.sleep(1)
                    result = self.readspic("FETCh:NRSub:MEAS:MEValuation:STATe?")
                value_str = self.readspic("FETCh:NRSub:MEAS:MEValuation:MODulation:AVERage?")
                try:
                    power_value = str(format(eval(value_str.split(',')[17]), '.2f'))
                except:
                    power_value = '-999'

                return power_value
        except Exception as e:
            global_elements.emitsingle.thread_exitSingle.emit('getValue_6_3_1  failed, Program abnormal exit! Error: ' +
                                                              e.__doc__)

    def getValue_6_4_1(self):
        # 获取测试结果
        try:
            global_elements.emitsingle.stateupdataSingle.emit('Get the value....')
            if self.device_name == 'CMX500':
                self.writespic("INITiate:NRSub:MEAS:MEValuation")
                result = self.readspic("FETCh:NRSub:MEAS:MEValuation:STATe?")
                while result != 'RDY\n':
                    time.sleep(1)
                    result = self.readspic("FETCh:NRSub:MEAS:MEValuation:STATe?")
                value_str = self.readspic("FETCh:NRSub:MEAS:MEValuation:MODulation:AVERage?")
                try:
                    freError = str(format(eval(value_str.split(',')[15]), '.2f'))
                except:
                    freError = '-999'

                return freError
        except Exception as e:
            global_elements.emitsingle.thread_exitSingle.emit('getValue_6_4_1  failed, Program abnormal exit! Error: ' + e.__doc__)

    def getValue_6_4_2_1(self, Pexp):
        # 获取测试结果
        try:
            global_elements.emitsingle.stateupdataSingle.emit('Get the value....')
            if self.device_name == 'CMX500':
                self.writespic("INITiate:NRSub:MEAS:MEValuation")
                result = self.readspic("FETCh:NRSub:MEAS:MEValuation:STATe?")
                while result != 'RDY\n':
                    time.sleep(1)
                    result = self.readspic("FETCh:NRSub:MEAS:MEValuation:STATe?")
                value_str = self.readspic("FETCh:NRSub:MEAS:MEValuation:MODulation:AVERage?")
                try:
                    evm_rms_value = str(format(eval(value_str.split(',')[2]), '.2f'))
                except:
                    evm_rms_value = '-999'

                try:
                    evm_dmrs_value = str(format(eval(value_str.split(',')[20]), '.2f'))
                except:
                    evm_dmrs_value = '-999'

                if evm_dmrs_value == '-999':
                    self.writespic("CONFigure:NRSub:MEAS:RFSettings:ENPower " + str(float(Pexp) + 5), timesleep=1)

                    self.writespic("INITiate:NRSub:MEAS:MEValuation")
                    result = self.readspic("FETCh:NRSub:MEAS:MEValuation:STATe?")
                    while result != 'RDY\n':
                        time.sleep(1)
                        result = self.readspic("FETCh:NRSub:MEAS:MEValuation:STATe?")
                    value_str = self.readspic("FETCh:NRSub:MEAS:MEValuation:MODulation:AVERage?")
                    try:
                        evm_rms_value = str(format(eval(value_str.split(',')[2]), '.2f'))
                    except:
                        evm_rms_value = '-999'

                    try:
                        evm_dmrs_value = str(format(eval(value_str.split(',')[20]), '.2f'))
                    except:
                        evm_dmrs_value = '-999'

                return evm_rms_value, evm_dmrs_value
        except Exception as e:
            global_elements.emitsingle.thread_exitSingle.emit('getValue_6_2_1  failed, Program abnormal exit! Error: ' + e.__doc__)

    def getValue_6_4_2_2(self):
        # 获取测试结果
        try:
            global_elements.emitsingle.stateupdataSingle.emit('Get the value....')
            if self.device_name == 'CMX500':
                self.writespic("INITiate:NRSub:MEAS:MEValuation")
                result = self.readspic("FETCh:NRSub:MEAS:MEValuation:STATe?")
                while result != 'RDY\n':
                    time.sleep(1)
                    result = self.readspic("FETCh:NRSub:MEAS:MEValuation:STATe?")
                value_str = self.readspic("FETCh:NRSub:MEAS:MEValuation:MODulation:AVERage?")
                try:
                    power_value = str(format(eval(value_str.split(',')[14]), '.2f'))
                except:
                    power_value = '-999'

                return power_value
        except Exception as e:
            global_elements.emitsingle.thread_exitSingle.emit('getValue_6_4_2_2  failed, Program abnormal exit! Error: ' + e.__doc__)

    def getValue_6_4_2_3(self):
        # 获取测试结果
        try:
            global_elements.emitsingle.stateupdataSingle.emit('Get the value....')
            if self.device_name == 'CMX500':
                self.writespic("INITiate:NRSub:MEAS:MEValuation")
                result = self.readspic("FETCh:NRSub:MEAS:MEValuation:STATe?")
                while result != 'RDY\n':
                    time.sleep(1)
                    result = self.readspic("FETCh:NRSub:MEAS:MEValuation:STATe?")
                value_str = self.readspic("FETCh:NRSub:MEAS:MEValuation:IEMission:MARGin:CURR?")
                try:
                    power_value = str(format(eval(value_str.split(',')[2]), '.2f'))
                except:
                    power_value = '-999'

                return power_value
        except Exception as e:
            global_elements.emitsingle.thread_exitSingle.emit('getValue_6_4_2_3  failed, Program abnormal exit! Error: ' + e.__doc__)

    def getValue_6_4_2_4(self):
        # 获取测试结果
        try:
            global_elements.emitsingle.stateupdataSingle.emit('Get the value....')
            if self.device_name == 'CMX500':
                self.writespic("INITiate:NRSub:MEAS:MEValuation")
                result = self.readspic("FETCh:NRSub:MEAS:MEValuation:STATe?")
                while result != 'RDY\n':
                    time.sleep(1)
                    result = self.readspic("FETCh:NRSub:MEAS:MEValuation:STATe?")
                value_str = self.readspic("FETCh:NRSub:MEAS:MEValuation:ESFLatness:AVERage?")
                try:
                    value_Ripple1 = str(format(eval(value_str.split(',')[2]), '.2f'))
                except:
                    value_Ripple1 = '-999'
                try:
                    value_Ripple2 = str(format(eval(value_str.split(',')[3]), '.2f'))
                except:
                    value_Ripple2 = '-999'
                try:
                    value_Ripple12 = str(format(eval(value_str.split(',')[4]), '.2f'))
                except:
                    value_Ripple12 = '-999'
                try:
                    value_Ripple21 = str(format(eval(value_str.split(',')[5]), '.2f'))
                except:
                    value_Ripple21 = '-999'

                return [value_Ripple1, value_Ripple2, value_Ripple12, value_Ripple21]
        except Exception as e:
            global_elements.emitsingle.thread_exitSingle.emit('getValue_6_4_2_4  failed, Program abnormal exit! Error: ' + e.__doc__)

    def getValue_6_4_2_5(self):
        # 获取测试结果
        try:
            global_elements.emitsingle.stateupdataSingle.emit('Get the value....')
            if self.device_name == 'CMX500':
                self.writespic("INITiate:NRSub:MEAS:MEValuation")
                result = self.readspic("FETCh:NRSub:MEAS:MEValuation:STATe?")
                while result != 'RDY\n':
                    time.sleep(1)
                    result = self.readspic("FETCh:NRSub:MEAS:MEValuation:STATe?")
                value_str = self.readspic("FETCh:NRSub:MEAS:MEValuation:ESFLatness:AVERage?")
                try:
                    value_Ripple1 = str(format(eval(value_str.split(',')[2]), '.2f'))
                except:
                    value_Ripple1 = '-999'
                try:
                    value_Ripple2 = str(format(eval(value_str.split(',')[4]), '.2f'))
                except:
                    value_Ripple2 = '-999'

                return [value_Ripple1, value_Ripple2]
        except Exception as e:
            global_elements.emitsingle.thread_exitSingle.emit('getValue_6_4_2_5  failed, Program abnormal exit! Error: ' + e.__doc__)

    def getValue_6_5_1(self):
        # 获取测试结果
        try:
            global_elements.emitsingle.stateupdataSingle.emit('Get the value....')
            if self.device_name == 'CMX500':
                self.writespic("INITiate:NRSub:MEAS:MEValuation")
                result = self.readspic("FETCh:NRSub:MEAS:MEValuation:STATe?")
                while result != 'RDY\n':
                    time.sleep(1)
                    result = self.readspic("FETCh:NRSub:MEAS:MEValuation:STATe?")
                self.writespic("CONFigure:NRSub:MEAS:MEValuation:MOEXception OFF")
                value_str = self.readspic("FETCh:NRSub:MEAS:MEValuation:SEMask:AVERage?")
                try:
                    bw_value = str(format(float(value_str.split(',')[2]) / 1e6, '.2f'))
                except:
                    bw_value = '-999'

                return bw_value
        except Exception as e:
            global_elements.emitsingle.thread_exitSingle.emit('getValue_6_5_1  failed, Program abnormal exit! Error: ' + e.__doc__)

    def getValue_6_5_2_2(self):
        # 获取测试结果
        try:
            global_elements.emitsingle.stateupdataSingle.emit('Get the value....')
            if self.device_name == 'CMX500':
                self.writespic("INITiate:NRSub:MEAS:MEValuation")
                result = self.readspic("FETCh:NRSub:MEAS:MEValuation:STATe?")
                while result != 'RDY\n':
                    time.sleep(1)
                    result = self.readspic("FETCh:NRSub:MEAS:MEValuation:STATe?")
                value_str = self.readspic("FETCh:NRSub:MEAS:MEValuation:SEMask:MARGin:ALL?")
                try:
                    margin1_value = str(format(eval(value_str.split(',')[26]), '.2f'))
                except:
                    margin1_value = '-999'
                try:
                    margin2_value = str(format(eval(value_str.split(',')[27]), '.2f'))
                except:
                    margin2_value = '-999'
                try:
                    margin3_value = str(format(eval(value_str.split(',')[28]), '.2f'))
                except:
                    margin3_value = '-999'
                try:
                    margin4_value = str(format(eval(value_str.split(',')[29]), '.2f'))
                except:
                    margin4_value = '-999'

                return [margin1_value, margin2_value, margin3_value, margin4_value]
        except Exception as e:
            global_elements.emitsingle.thread_exitSingle.emit('getValue_6_5_2_2  failed, Program abnormal exit! Error: ' + e.__doc__)

    def getValue_6_5_2_4(self):
        # 获取测试结果
        try:
            global_elements.emitsingle.stateupdataSingle.emit('Get the value....')
            if self.device_name == 'CMX500':
                self.writespic("INITiate:NRSub:MEAS:MEValuation")
                result = self.readspic("FETCh:NRSub:MEAS:MEValuation:STATe?")
                while result != 'RDY\n':
                    time.sleep(1)
                    result = self.readspic("FETCh:NRSub:MEAS:MEValuation:STATe?")
                value_str = self.readspic("FETCh:NRSub:MEAS:MEValuation:ACLR:AVERage?")
                try:
                    nraclr_left_value = str(format(eval(value_str.split(',')[3]), '.2f'))
                except:
                    nraclr_left_value = '-999'
                try:
                    nraclr_right_value = str(format(eval(value_str.split(',')[5]), '.2f'))
                except:
                    nraclr_right_value = '-999'
                try:
                    utraaclr1_left_value = str(format(eval(value_str.split(',')[2]), '.2f'))
                except:
                    utraaclr1_left_value = '-999'
                try:
                    utraaclr1_right_value = str(format(eval(value_str.split(',')[6]), '.2f'))
                except:
                    utraaclr1_right_value = '-999'
                try:
                    utraaclr2_left_value = str(format(eval(value_str.split(',')[1]), '.2f'))
                except:
                    utraaclr2_left_value = '-999'
                try:
                    utraaclr2_right_value = str(format(eval(value_str.split(',')[7]), '.2f'))
                except:
                    utraaclr2_right_value = '-999'

                return [nraclr_left_value, nraclr_right_value, utraaclr2_left_value, utraaclr1_left_value, utraaclr1_right_value,
                         utraaclr2_right_value]
        except Exception as e:
            global_elements.emitsingle.thread_exitSingle.emit('getValue_6_5_2_4  failed, Program abnormal exit! Error: ' + e.__doc__)

    def getValue_7_3_2(self):
        # 获取测试结果
        try:
            global_elements.emitsingle.stateupdataSingle.emit('Get the value....')
            if self.device_name == 'CMX500':
                self.writespic("INIT:SIGN:MEAS:BLER")
                result = self.readspic("FETCh:SIGN:MEAS:BLER:STATe?")
                while result != 'RDY\n':
                    time.sleep(1)
                    result = self.readspic("FETCh:SIGN:MEAS:BLER:STATe?")
                value_str = self.readspic("FETCh:SIGN:MEAS:BLER:REL?")
                try:
                    per_result = str(format(eval(value_str.split(',')[5]), '.2f'))
                except:
                    per_result = '-999'

                return per_result
        except Exception as e:
            global_elements.emitsingle.thread_exitSingle.emit('getValue_7_3_2  failed, Program abnormal exit! Error: ' + e.__doc__)

    def getValue_7_3_2_c(self, dl_level):
        # 获取测试结果
        try:
            global_elements.emitsingle.stateupdataSingle.emit('Get the value....')
            if self.device_name == 'CMX500':
                final_result = ''
                primary_level = str(float(dl_level) + 5)

                # step为1dB进度扫描
                while True:
                    self.writespic("CONFigure:SIGNaling:NRADio:CELL:POW:DL:TCELL 'NrCell1', " + primary_level)
                    self.writespic("CONFigure:SIGNaling:MEASurement:BLER:REPetition SING")
                    time.sleep(2)
                    state = self.checkConnectState()
                    if state == False:
                        final_result = '-999'
                        break
                    self.writespic("INIT:SIGN:MEAS:BLER")

                    result = self.readspic("FETCh:SIGN:MEAS:BLER:STATe?")
                    while result != 'RDY\n':
                        time.sleep(1)
                        result = self.readspic("FETCh:SIGN:MEAS:BLER:STATe?")
                    value_str = self.readspic("FETCh:SIGN:MEAS:BLER:REL?")
                    try:
                        per_result = str(format(eval(value_str.split(',')[5]), '.2f'))
                    except:
                        final_result = '-999'
                        break
                    if (5 - float(per_result)) < 0:
                        global_elements.emitsingle.stateupdataSingle.emit(
                            'DL Level ' + primary_level + 'dBm: BLER:' + per_result + '%')
                        break
                    global_elements.emitsingle.stateupdataSingle.emit(
                        'DL Level ' + primary_level + 'dBm: BLER:' + per_result + '%')
                    primary_level = str(float(primary_level) -1)

                # 如果上面的1dB扫描没出错，再进行微调扫描
                if final_result != '-999':
                    primary_level = str(format((float(primary_level) + 0.2), '.2f'))
                    while True:
                        self.writespic("CONFigure:SIGNaling:NRADio:CELL:POW:DL:TCELL 'NrCell1', " + primary_level)
                        self.writespic("CONFigure:SIGNaling:MEASurement:BLER:REPetition SING")
                        time.sleep(2)
                        state = self.checkConnectState()
                        if state == False:
                            final_result = '-999'
                            break
                        self.writespic("INIT:SIGN:MEAS:BLER")

                        result = self.readspic("FETCh:SIGN:MEAS:BLER:STATe?")
                        while result != 'RDY\n':
                            time.sleep(1)
                            result = self.readspic("FETCh:SIGN:MEAS:BLER:STATe?")
                        value_str = self.readspic("FETCh:SIGN:MEAS:BLER:REL?")
                        try:
                            per_result = str(format(eval(value_str.split(',')[5]), '.2f'))
                        except:
                            final_result = '-999'
                            break
                        if (5 - float(per_result)) >= 0:
                            global_elements.emitsingle.stateupdataSingle.emit(
                                'DL Level ' + primary_level + 'dBm: BLER:' + per_result + '%')
                            break
                        global_elements.emitsingle.stateupdataSingle.emit('DL Level ' + primary_level + 'dBm: BLER:' + per_result + '%')
                        primary_level = str(format((float(primary_level) + 0.2), '.2f'))

                if final_result != '-999':
                    final_result = primary_level

                # 测试完成恢复到一个比较稳定的DL LEVEL
                self.writespic("CONFigure:SIGNaling:NRADio:CELL:POW:DL:TCELL 'NrCell1', -60")

                return final_result

        except Exception as e:
            global_elements.emitsingle.thread_exitSingle.emit('getValue_7_3_2_c failed, Program abnormal exit! Error: ' + e.__doc__)

    def getValue_7_4(self):
        # 获取测试结果
        try:
            global_elements.emitsingle.stateupdataSingle.emit('Get the value....')
            if self.device_name == 'CMX500':
                self.writespic("INIT:SIGN:MEAS:BLER")
                result = self.readspic("FETCh:SIGN:MEAS:BLER:STATe?")
                while result != 'RDY\n':
                    time.sleep(1)
                    result = self.readspic("FETCh:SIGN:MEAS:BLER:STATe?")
                value_str = self.readspic("FETCh:SIGN:MEAS:BLER:REL?")
                try:
                    per_result = str(format(eval(value_str.split(',')[5]), '.2f'))
                except:
                    per_result = '-999'

                return per_result
        except Exception as e:
            global_elements.emitsingle.thread_exitSingle.emit('getValue_7_4  failed, Program abnormal exit! Error: ' + e.__doc__)

    def getValue_6_2b_1_3(self, testid):
        # 获取测试结果
        try:
            global_elements.emitsingle.stateupdataSingle.emit('Get the value....')
            if self.device_name == 'CMX500':
                lte_power_value = '-999'
                nr_power_value = '-999'
                if testid in range(1, 10):    # testid 1-9，都需要取得Lte的Power
                    self.writespic("INITiate:LTE:MEAS1:MEValuation")
                    result = self.readspic("FETCh:LTE:MEAS1:MEValuation:STATe?")
                    while result != 'RDY\n':
                        time.sleep(1)
                        result = self.readspic("FETCh:LTE:MEAS1:MEValuation:STATe?")
                    value_str = self.readspic("FETCh:LTE:MEAS1:MEValuation:MODulation:AVERage?")
                    try:
                        lte_power_value = str(format(eval(value_str.split(',')[17]), '.2f'))
                    except:
                        lte_power_value = '-999'

                if testid not in [7, 8, 9]:      # testid 不是 7， 8， 9时，都需要取得nr的power
                    self.readspic("FETCh:SIGNaling:UE:RRCState?")
                    self.writespic("INITiate:NRSub:MEAS:MEValuation")
                    state = self.readspic("FETCh:NRSub:MEAS:MEValuation:STATe?")
                    while state != 'RDY\n':
                        time.sleep(1)
                        state = self.readspic("FETCh:NRSub:MEAS:MEValuation:STATe?")
                    value_str = self.readspic("FETCh:NRSub:MEAS:MEValuation:MODulation:AVERage?")
                    try:
                        nr_power_value = str(format(eval(value_str.split(',')[17]), '.2f'))
                    except:
                        nr_power_value = '-999'

                return lte_power_value, nr_power_value
        except Exception as e:
            global_elements.emitsingle.thread_exitSingle.emit('getValue_6_2b_1_3  failed, Program abnormal exit! Error: ' + e.__doc__)


    def getParams(self):
        '''
        获取当前的BAND BW CHANNEL等信息，用于测试参数设置
        :return: band_num, scs_num, scs_str, bw_num, bw_str, bw_num_final, ch_ul_num, ch_dl_num
        '''

        # 提取BAND信息
        reg = re.compile(r"(?<=n)\d+")
        match = reg.search(global_elements.NR_band)
        band_num = match.group(0)
        # 提取SCS信息
        scs_num = global_elements.NR_SCS
        scs_str = 'SCS_' + scs_num
        # 提取BW信息
        if global_elements.test_case_name == 'ts138521_1 6.5.1 Occupied bandwidth':
            bw_num = global_elements.NR_bw
        else:
            bw_num = global_elements.SCSBandwidthConfig_dict['xml'][global_elements.NR_band][scs_str][global_elements.NR_bw]
        bw_str = 'BW_' + bw_num
        if len(bw_num) == 1:
            bw_num_final = '00' + bw_num
        elif len(bw_num) == 2:
            bw_num_final = '0' + bw_num
        else:
            bw_num_final = bw_num

        ch_ul_num = global_elements.ChannelConfig_dict['xml'][global_elements.NR_band][scs_str][bw_str]['UL'][
            global_elements.NR_ch]
        ch_dl_num = global_elements.ChannelConfig_dict['xml'][global_elements.NR_band][scs_str][bw_str]['DL'][
            global_elements.NR_ch]

        return band_num, scs_num, scs_str, bw_num, bw_str, bw_num_final, ch_ul_num, ch_dl_num

    def configRFPortAndDuplexMode(self):
        '''
        配置 RF端口和双工方式
        :return: None
        '''
        self.writespic("ROUTe:NRSub:MEAS:SCENario:SALone RF2C, RX1")
        if 'FDD' in global_elements.NR_band:
            self.writespic("CONFigure:NRSub:MEAS:MEValuation:DMOD FDD")
        elif 'TDD' in global_elements.NR_band:
            self.writespic("CONFigure:NRSub:MEAS:MEValuation:DMOD TDD")

    def measParams1(self, band_num, ch_ul_num, scs_num, bw_num_final, isSetDLLevel, isSetENPower, ENPower, DLLevl='-84.5939248775923'):
        '''
        发射项测试参数配置第一部分，用于配置部分测试参数
        :param band_num:
        :param ch_ul_num:
        :param scs_num:
        :param bw_num_final:
        :param isSetDLLevel:  用于判断是否需要设置 DL Level
        :param isSetENPower:  用于判断是否需要设置 ENPower
        :param ENPower:   ENPower 的值
        :param DLLevl:   DL Level 的值，可选参数，默认为-84.5939248775923
        :return:  None
        '''
        self.writespic("TRIGger:NRSub:MEAS:MEValuation:SOURce 'Base1: NR Trigger'")
        self.writespic("CONFigure:NRSub:MEAS:BAND OB" + band_num)
        self.writespic("CONFigure:NRSub:MEAS:RFSettings:FREQuency " + ch_ul_num['CarrierCentreFre'] + 'e6')
        if isSetDLLevel:
            self.writespic("CONFigure:SIGNaling:NRADio:CELL:POW:DL:SEPRe 'NrCell1'," + DLLevl)
        if isSetENPower:
            self.writespic("CONFigure:NRSub:MEAS:RFSettings:ENPower " + ENPower)
        self.writespic("CONFigure:NRSub:MEAS:RFSettings:UMARgin 12")
        self.writespic("CONFigure:NRSub:MEAS:MEValuation:SCOunt:MODulation 3")
        self.writespic("CONFigure:NRSub:MEAS:MEValuation:SCOunt:POWer 3")
        self.writespic("CONFigure:NRSub:MEAS:MEValuation:SCOunt:SPEC:ACLR 3")
        self.writespic("CONFigure:NRSub:MEAS:MEValuation:SCOunt:SPEC:SEM 3")
        self.writespic("CONFigure:NRSub:MEAS:MEValuation:BWConfig S" + scs_num + "K, B" + bw_num_final)
        self.writespic("CONFigure:NRSub:MEAS:TXBWidth:OFFSet " + ch_ul_num['offsetToCarrier'])
        self.writespic("CONFigure:NRSub:MEAS:MEValuation:PCOMp CAF, KEEP")

    def measParams2(self):
        '''
        配置发射项测试参数配置第二部分
        :return:
        '''
        self.writespic("CONFigure:NRSub:MEAS:MEValuation:REPetition SING")
        self.writespic("CONFigure:NRSub:MEAS:MEValuation:PUSChconfig  AUTO, A, ON, KEEP, KEEP, 14, 0, T1, SING, 2, 2")
        self.writespic("TRIGger:NRSub:MEAS:MEValuation:THReshold -20")
        self.writespic("CONFigure:NRSub:MEAS:MEValuation:RESult:ALL OFF,OFF,OFF,OFF,OFF,OFF,OFF,OFF,OFF,OFF,OFF,OFF")

    def measParamsDL1(self):
        '''
        配置接收项测试参数配置第一部分
        :return:
        '''
        self.writespic("TRIGger:NRSub:MEAS:MEValuation:SOURce 'Base1: NR Trigger'")
        self.writespic("CONFigure:NRSub:MEAS:RFSettings:ENPower " + global_elements.NR_p_max)
        self.writespic("CONFigure:NRSub:MEAS:RFSettings:UMARgin 12")
        self.writespic("SIGNaling:NRADio:CELL:POWer:CONTrol:TPControl 'NrCell1', MAX")

    def configULMCSTable(self):
        '''
        配置上行 MCS Table
        :return:
        '''
        if '256 QAM' in global_elements.NR_Modulation:
            self.writespic("CONFigure:SIGNaling:NRADio:CELL:UESCheduling:UDEFined:UL:MCSTable 'NrCell1', Q256")
        else:
            self.writespic("CONFigure:SIGNaling:NRADio:CELL:UESCheduling:UDEFined:UL:MCSTable 'NrCell1', Q64")

    def getMCSIndexandModulation(self):
        # 获取 MCS Index 和 调制方式
        '''
        # 获取 MCS Index 和 调制方式
        :return: modu_str, mcs_index
        '''
        if 'BPSK' in global_elements.NR_Modulation:
            modu_str = 'BPSK'
            mcs_index = global_elements.MCSindex_dict['xml']['UL']['DFT']['halfpi_BPSK'].split('_')[1]
        elif 'QPSK' in global_elements.NR_Modulation:
            modu_str = 'QPSK'
            mcs_index = global_elements.MCSindex_dict['xml']['UL']['DFT']['QPSK'].split('_')[1]
        elif '16 QAM' in global_elements.NR_Modulation:
            modu_str = 'Q16'
            mcs_index = global_elements.MCSindex_dict['xml']['UL']['DFT']['QAM16'].split('_')[1]
        elif '64 QAM' in global_elements.NR_Modulation:
            modu_str = 'Q64'
            mcs_index = global_elements.MCSindex_dict['xml']['UL']['DFT']['QAM64'].split('_')[1]
        else:
            modu_str = 'Q256'
            mcs_index = global_elements.MCSindex_dict['xml']['UL']['DFT']['QAM256'].split('_')[1]
        return modu_str, mcs_index

    def getMCSIndexandModulation_NSA_NR(self):
        # 获取 MCS Index 和 调制方式
        '''
        # 获取 MCS Index 和 调制方式
        :return: modu_str, mcs_index
        '''
        if 'BPSK' in global_elements.NSA_NR_modulation:
            modu_str = 'BPSK'
            mcs_index = global_elements.MCSindex_dict['xml']['UL']['DFT']['halfpi_BPSK'].split('_')[1]
        elif 'QPSK' in global_elements.NSA_NR_modulation:
            modu_str = 'QPSK'
            mcs_index = global_elements.MCSindex_dict['xml']['UL']['DFT']['QPSK'].split('_')[1]
        elif '16 QAM' in global_elements.NSA_NR_modulation:
            modu_str = 'Q16'
            mcs_index = global_elements.MCSindex_dict['xml']['UL']['DFT']['QAM16'].split('_')[1]
        elif '64 QAM' in global_elements.NSA_NR_modulation:
            modu_str = 'Q64'
            mcs_index = global_elements.MCSindex_dict['xml']['UL']['DFT']['QAM64'].split('_')[1]
        else:
            modu_str = 'Q256'
            mcs_index = global_elements.MCSindex_dict['xml']['UL']['DFT']['QAM256'].split('_')[1]
        return modu_str, mcs_index

    def getModulation_NSA_LTE(self):
        # 获取  调制方式
        '''
        # 获取  调制方式
        :return: modu_str
        '''
        if 'BPSK' in global_elements.NSA_LTE_modulation:
            modu_str = 'BPSK'
        elif 'QPSK' in global_elements.NSA_LTE_modulation:
            modu_str = 'QPSK'
        elif '16 QAM' in global_elements.NSA_LTE_modulation:
            modu_str = 'Q16'
        elif '64 QAM' in global_elements.NSA_LTE_modulation:
            modu_str = 'Q64'
        else:
            modu_str = 'Q256'
        return modu_str

    def setDFTorCP(self):
        '''
        按参数设置DFT或者CP 波形
        :return: None
        '''
        if 'DFT' in global_elements.NR_Modulation:
            self.writespic("CONFigure:NRSub:MEAS:BWPart:PUSCh:DFTPrecoding BWP0,ON")
            self.writespic("CONFigure:SIGNaling:NRADio:CELL:PUSCh:TPRecoding 'NrCell1', DTFS")
            if '256 QAM' in global_elements.NR_Modulation:
                self.writespic("CONFigure:SIGNaling:NRADio:CELL:PUSCh:DTFS:MCSTable 'NrCell1', Q256")
            else:
                self.writespic("CONFigure:SIGNaling:NRADio:CELL:PUSCh:DTFS:MCSTable 'NrCell1', Q64")
        else:
            self.writespic("CONFigure:NRSub:MEAS:BWPart:PUSCh:DFTPrecoding BWP0,OFF")
            self.writespic("CONFigure:SIGNaling:NRADio:CELL:PUSCh:TPRecoding 'NrCell1', CP")

    def conULRB(self, bw_str, scs_str, start_index):
        # 配置RB
        '''
        配置上行RB
        :param bw_str:  带宽
        :param scs_str:  子载波间距
        :param start_index:  循环开始的索引
        :return:  None
        '''
        rb_str = '_'.join(global_elements.NR_RBAllocation.split(' '))
        if 'DFT' in global_elements.NR_Modulation:
            wave_type_str = 'DFT_s'
        else:
            wave_type_str = 'CP'
        rb_config_list = global_elements.RBConfig_dict['xml'][bw_str][scs_str][wave_type_str][rb_str].split('@')

        for j in range(start_index, 10):
            self.writespic(
                "CONFigure:SIGNaling:NRADio:CELL:UESCheduling:UDEFined:SASSignment:UL:RB 'NrCell1'," + str(j) + ", " +
                rb_config_list[0] + ", " + rb_config_list[1])