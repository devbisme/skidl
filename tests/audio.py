# -*- coding: utf-8 -*-

from skidl import *


def C__xesscorp_PRODUCTS_StickIt_2nd_gen_StickIt_AudioIO_pcb_StickIt_AudioIO_sch():

    STK1 = Part('xess', 'STICKIT2_HDR', ref='STK1', value='STICKIT2_HDR')
    setattr(STK1, 'footprint', 'XESS:STICKIT2_HDR')
    setattr(STK1, 'kicost:pricing', '1:0.09')

    JP1 = Part('device', 'JUMPER', ref='JP1', value='JUMPER')
    setattr(JP1, 'footprint', 'XESS:HDR_1x2')

    JP2 = Part('device', 'JUMPER', ref='JP2', value='JUMPER')
    setattr(JP2, 'footprint', 'XESS:HDR_1x2')

    U1 = Part('xess', 'AK4565', ref='U1', value='AK4565VF')
    setattr(U1, 'footprint', 'XESS:VSOP28')
    setattr(U1, 'kicost:link', 'http://www.aliexpress.com/item/100-New-AK4565VF-AK4565-TSSOP28-AKM-Brand-new-original-orders-are-welcome/32617934313.html?ws_ab_test=searchweb201556_8,searchweb201602_1_10037_10017_10021_507_10022_10032_10009_10020_10008_10018_10019_101,searchweb201603_2&btsid=f1412ba2-0f0a-4e39-9924-091cc8da27fc')
    setattr(U1, 'kicost:pricing', '1:$5.45')
    setattr(U1, 'manf', 'Asahi Kasei')
    setattr(U1, 'manf#', 'AK4565VF')

    U2 = Part('xess', 'LM4808', ref='U2', value='LM4808')
    setattr(U2, 'footprint', 'XESS:MSOP8')
    setattr(U2, 'manf', 'TI')
    setattr(U2, 'manf#', 'LM4808MM')

    J1 = Part('xess', 'STEREO_JACK', ref='J1', value='STEREO_JACK')
    setattr(J1, 'footprint', 'XESS:PJ-313-TH')
    setattr(J1, 'kicost:link', 'http://www.aliexpress.com/item/20Pcs-3-5mm-Female-Audio-Connector-5-Pin-DIP-Stereo-Headphone-Jack-PJ-313-Green/32600096063.html?ws_ab_test=searchweb201556_8,searchweb201602_1_10037_10017_10021_507_10022_10032_10009_10020_10008_10018_10019_101,searchweb201603_2&btsid=e31655d7-f43d-4ec6-a859-bfbd2dcde38a')
    setattr(J1, 'kicost:pricing', '1:$0.123')

    J2 = Part('xess', 'STEREO_JACK', ref='J2', value='STEREO_JACK')
    setattr(J2, 'footprint', 'XESS:PJ-313-TH')
    setattr(J2, 'kicost:link', 'http://www.aliexpress.com/item/20Pcs-3-5mm-Female-Audio-Connector-5-Pin-DIP-Stereo-Headphone-Jack-PJ-313-Green/32600096063.html?ws_ab_test=searchweb201556_8,searchweb201602_1_10037_10017_10021_507_10022_10032_10009_10020_10008_10018_10019_101,searchweb201603_2&btsid=e31655d7-f43d-4ec6-a859-bfbd2dcde38a')
    setattr(J2, 'kicost:pricing', '1:$0.123')

    C7 = Part('device', 'C', ref='C7', value='0.1uF')
    setattr(C7, 'footprint', 'Capacitors_SMD:C_0603_HandSoldering')
    setattr(C7, 'manf#', 'CL03A104KQ3NNNH')

    C2 = Part('device', 'CP1', ref='C2', value='33uF')
    setattr(C2, 'footprint', 'Capacitors_SMD:c_elec_5x4.5')
    setattr(C2, 'manf#', 'UWX1A330MCL1GB')

    C6 = Part('device', 'C', ref='C6', value='4.7uF')
    setattr(C6, 'footprint', 'Capacitors_SMD:C_0603_HandSoldering')
    setattr(C6, 'manf#', 'EMK107ABJ475KA-T')

    RN3 = Part('xess', 'RN2', ref='RN3', value='4K7')
    setattr(RN3, 'footprint', 'XESS:CTS_742C043')
    setattr(RN3, 'manf#', '742c043472')

    RN1 = Part('xess', 'RN4', ref='RN1', value='4K7')
    setattr(RN1, 'footprint', 'XESS:CTS_742C083')
    setattr(RN1, 'manf#', '742c083472')

    RN2 = Part('xess', 'RN2', ref='RN2', value='4K7')
    setattr(RN2, 'footprint', 'XESS:CTS_742C043')
    setattr(RN2, 'manf#', '742c043472')

    C4 = Part('device', 'CP1', ref='C4', value='33uF')
    setattr(C4, 'footprint', 'Capacitors_SMD:c_elec_5x4.5')
    setattr(C4, 'manf#', 'UWX1A330MCL1GB')

    C5 = Part('device', 'CP1', ref='C5', value='33uF')
    setattr(C5, 'footprint', 'Capacitors_SMD:c_elec_5x4.5')
    setattr(C5, 'manf#', 'UWX1A330MCL1GB')

    C1 = Part('device', 'CP1', ref='C1', value='33uF')
    setattr(C1, 'footprint', 'Capacitors_SMD:c_elec_5x4.5')
    setattr(C1, 'manf#', 'UWX1A330MCL1GB')

    C9 = Part('device', 'C', ref='C9', value='0.1uF')
    setattr(C9, 'footprint', 'Capacitors_SMD:C_0603_HandSoldering')
    setattr(C9, 'manf#', 'CL03A104KQ3NNNH')

    C3 = Part('device', 'C', ref='C3', value='0.1uF')
    setattr(C3, 'footprint', 'Capacitors_SMD:C_0603_HandSoldering')
    setattr(C3, 'manf#', 'CL03A104KQ3NNNH')

    C8 = Part('device', 'C', ref='C8', value='4.7uF')
    setattr(C8, 'footprint', 'Capacitors_SMD:C_0603_HandSoldering')
    setattr(C8, 'manf#', 'EMK107ABJ475KA-T')

    L1 = Part('xess', 'FERRITE_BEAD', ref='L1', value='FERRITE_BEAD')
    setattr(L1, 'footprint', 'Capacitors_SMD:C_0805_HandSoldering')
    setattr(L1, 'manf#', 'CIM21J252NE')

    PCB1 = Part('xess', 'PCB', ref='PCB1', value='PCB')
    setattr(PCB1, 'kicost:pricing', '1:$0.32')

    net__1 = Net('Net-(RN1-Pad3)')
    net__1 += RN1['4'],U2['2'],RN1['3']

    net__2 = Net('Net-(C1-Pad1)')
    net__2 += RN1['5'],U2['1'],C1['1']

    net__3 = Net('Net-(RN1-Pad1)')
    net__3 += U2['6'],RN1['1'],RN1['2']

    net__4 = Net('Net-(C2-Pad1)')
    net__4 += U2['7'],RN1['8'],C2['1']

    net__5 = Net('Net-(C1-Pad2)')
    net__5 += J1['tip'],C1['2']

    net__6 = Net('Net-(C2-Pad2)')
    net__6 += J1['ring'],C2['2']

    net__7 = Net('Net-(C4-Pad2)')
    net__7 += RN3['1'],C4['2'],J2['tip']

    net__8 = Net('Net-(C5-Pad2)')
    net__8 += C5['2'],J2['ring'],RN3['2']

    net__9 = Net('LRCK')
    net__9 += STK1['D2'],U1['21']

    net__10 = Net('CCLK')
    net__10 += U1['27'],STK1['D7']

    net__11 = Net('SDTI')
    net__11 += U1['20'],U1['25'],STK1['D1']

    net__12 = Net('SCLK')
    net__12 += U1['23'],STK1['D5']

    net__13 = Net('MCLK')
    net__13 += STK1['D3'],U1['22']

    net__14 = Net('Net-(RN1-Pad7)')
    net__14 += U1['2'],RN1['7']

    net__15 = Net('SDTO')
    net__15 += STK1['D0'],U1['18']

    net__16 = Net('~CS')
    net__16 += STK1['D4'],RN2['3'],U1['26']

    net__17 = Net('~RESET')
    net__17 += U1['28'],STK1['D6'],RN2['4']

    net__18 = Net('+3.3V-A')
    net__18 += RN3['4'],U1['14'],RN3['3'],U2['8'],C6['1'],C7['1'],L1['1'],U1['13']

    net__19 = Net('+3.3V')
    net__19 += STK1['VCC'],RN2['2'],JP2['2'],JP2['1'],RN2['1'],C9['1'],C8['1'],L1['2'],U1['17'],U1['15']

    net__20 = Net('Net-(U1-Pad19)')
    net__20 += U1['19']

    net__21 = Net('Net-(U1-Pad24)')
    net__21 += U1['24']

    net__22 = Net('Net-(U1-Pad5)')
    net__22 += U1['5']

    net__23 = Net('Net-(U1-Pad6)')
    net__23 += U1['6']

    net__24 = Net('Net-(U1-Pad7)')
    net__24 += U1['7']

    net__25 = Net('Net-(U1-Pad8)')
    net__25 += U1['8']

    net__26 = Net('Net-(C5-Pad1)')
    net__26 += C5['1'],U1['10'],U1['4']

    net__27 = Net('Net-(RN1-Pad6)')
    net__27 += RN1['6'],U1['1']

    net__28 = Net('Net-(C4-Pad1)')
    net__28 += U1['3'],C4['1'],U1['9']

    net__29 = Net('Net-(C3-Pad1)')
    net__29 += U2['3'],U1['11'],U2['5'],C3['1']

    net__30 = Net('GND')
    net__30 += J1['slv'],JP1['2'],JP1['1'],STK1['GND'],J2['slv'],U2['4'],U1['12'],U1['16'],C8['2'],C3['2'],C7['2'],C9['2'],C6['2']


if __name__ == "__main__":

    C__xesscorp_PRODUCTS_StickIt_2nd_gen_StickIt_AudioIO_pcb_StickIt_AudioIO_sch()
    generate_xml()
