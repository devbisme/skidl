from collections import defaultdict
from skidl import Pin, Part, Alias, SchLib, SKIDL, TEMPLATE

from skidl.pin import pin_types

SKIDL_lib_version = '0.0.1'

Sensor_Audio = SchLib(tool=SKIDL).add_parts(*[
        Part(**{ 'name':'ICS-43434', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'ICS-43434'}), 'ref_prefix':'MK', 'fplist':['Sensor_Audio:InvenSense_ICS-43434-6_3.5x2.65mm'], 'footprint':'Sensor_Audio:InvenSense_ICS-43434-6_3.5x2.65mm', 'keywords':'microphone MEMS 24bit I2S ICS-43434 TDK InvenSense', 'description':'', 'datasheet':'https://www.invensense.com/wp-content/uploads/2016/02/DS-000069-ICS-43434-v1.2.pdf', 'search_text':'/usr/share/kicad/symbols/Sensor_Audio.kicad_sym\nICS-43434\n\nmicrophone MEMS 24bit I2S ICS-43434 TDK InvenSense', 'pins':[
            Pin(num='1',name='WS',func=pin_types.INPUT,unit=1),
            Pin(num='2',name='LR',func=pin_types.INPUT,unit=1),
            Pin(num='3',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='4',name='SCK',func=pin_types.INPUT,unit=1),
            Pin(num='5',name='VDD',func=pin_types.PWRIN,unit=1),
            Pin(num='6',name='SD',func=pin_types.OUTPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'IM69D120', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'IM69D120'}), 'ref_prefix':'MK', 'fplist':['Sensor_Audio:Infineon_PG-LLGA-5-1'], 'footprint':'Sensor_Audio:Infineon_PG-LLGA-5-1', 'keywords':'mems microphone', 'description':'', 'datasheet':'https://www.infineon.com/dgdl/Infineon-IM69D120-DS-v01_00-EN.pdf?fileId=5546d462602a9dc801607a0e41a01a2b', 'search_text':'/usr/share/kicad/symbols/Sensor_Audio.kicad_sym\nIM69D120\n\nmems microphone', 'pins':[
            Pin(num='1',name='DATA',func=pin_types.OUTPUT,unit=1),
            Pin(num='2',name='VDD',func=pin_types.PWRIN,unit=1),
            Pin(num='3',name='CLOCK',func=pin_types.INPUT,unit=1),
            Pin(num='4',name='SELECT',func=pin_types.INPUT,unit=1),
            Pin(num='5',name='GND',func=pin_types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'IM73A135V01', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'IM73A135V01'}), 'ref_prefix':'MK', 'fplist':['Sensor_Audio:Infineon_PG-LLGA-5-2'], 'footprint':'Sensor_Audio:Infineon_PG-LLGA-5-2', 'keywords':'Microphone MEMS analog', 'description':'', 'datasheet':'https://www.infineon.com/dgdl/Infineon-IM73A135-DataSheet-v01_00-EN.pdf?fileId=8ac78c8c7f2a768a017fadec36b84500', 'search_text':'/usr/share/kicad/symbols/Sensor_Audio.kicad_sym\nIM73A135V01\n\nMicrophone MEMS analog', 'pins':[
            Pin(num='1',name='OUT+',func=pin_types.OUTPUT,unit=1),
            Pin(num='2',name='V_{DD}',func=pin_types.PWRIN,unit=1),
            Pin(num='3',name='OUT-',func=pin_types.OUTPUT,unit=1),
            Pin(num='4',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='5',name='GND',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'MP45DT02', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MP45DT02'}), 'ref_prefix':'MK', 'fplist':['Sensor_Audio:ST_HLGA-6_3.76x4.72mm_P1.65mm'], 'footprint':'Sensor_Audio:ST_HLGA-6_3.76x4.72mm_P1.65mm', 'keywords':'MEMS Microphone', 'description':'', 'datasheet':'http://www.st.com/st-web-ui/static/active/en/resource/technical/document/datasheet/DM00025467.pdf', 'search_text':'/usr/share/kicad/symbols/Sensor_Audio.kicad_sym\nMP45DT02\n\nMEMS Microphone', 'pins':[
            Pin(num='1',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='2',name='LR',func=pin_types.INPUT,unit=1),
            Pin(num='3',name='GND',func=pin_types.PASSIVE,unit=1),
            Pin(num='4',name='CLK',func=pin_types.INPUT,unit=1),
            Pin(num='5',name='DOUT',func=pin_types.OUTPUT,unit=1),
            Pin(num='6',name='VDD',func=pin_types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'SPH0641LU4H-1', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'SPH0641LU4H-1'}), 'ref_prefix':'MK', 'fplist':['Sensor_Audio:Knowles_LGA-5_3.5x2.65mm'], 'footprint':'Sensor_Audio:Knowles_LGA-5_3.5x2.65mm', 'keywords':'Microphone MEMS', 'description':'', 'datasheet':'https://www.knowles.com/docs/default-source/model-downloads/sph0641lu4h-1-revb.pdf', 'search_text':'/usr/share/kicad/symbols/Sensor_Audio.kicad_sym\nSPH0641LU4H-1\n\nMicrophone MEMS', 'pins':[
            Pin(num='1',name='DATA',func=pin_types.OUTPUT,unit=1),
            Pin(num='2',name='SEL',func=pin_types.INPUT,unit=1),
            Pin(num='3',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='4',name='CLOCK',func=pin_types.INPUT,unit=1),
            Pin(num='5',name='VDD',func=pin_types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'SPH0645LM4H', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'SPH0645LM4H'}), 'ref_prefix':'MK', 'fplist':['Sensor_Audio:Knowles_SPH0645LM4H-6_3.5x2.65mm'], 'footprint':'Sensor_Audio:Knowles_SPH0645LM4H-6_3.5x2.65mm', 'keywords':'microphone MEMS I2S 24bit Knowles SPH0645LM4H Crawford', 'description':'', 'datasheet':'https://www.knowles.com/docs/default-source/default-document-library/sph0645lm4h-1-datasheet.pdf', 'search_text':'/usr/share/kicad/symbols/Sensor_Audio.kicad_sym\nSPH0645LM4H\n\nmicrophone MEMS I2S 24bit Knowles SPH0645LM4H Crawford', 'pins':[
            Pin(num='1',name='WS',func=pin_types.INPUT,unit=1),
            Pin(num='2',name='SEL',func=pin_types.INPUT,unit=1),
            Pin(num='3',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='4',name='BCLK',func=pin_types.INPUT,unit=1),
            Pin(num='5',name='VDD',func=pin_types.PWRIN,unit=1),
            Pin(num='6',name='DATA',func=pin_types.OUTPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'SPM0687LR5H-1', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'SPM0687LR5H-1'}), 'ref_prefix':'MK', 'fplist':['Sensor_Audio:Knowles_LGA-6_4.72x3.76mm'], 'footprint':'Sensor_Audio:Knowles_LGA-6_4.72x3.76mm', 'keywords':'Microphone MEMS Knowles Sisonic winfrey', 'description':'', 'datasheet':'https://www.knowles.com/docs/default-source/default-document-library/spm0687lr5h-1_winfrey_datasheet.pdf?Status=Master&sfvrsn=ac3971b1_0', 'search_text':'/usr/share/kicad/symbols/Sensor_Audio.kicad_sym\nSPM0687LR5H-1\n\nMicrophone MEMS Knowles Sisonic winfrey', 'pins':[
            Pin(num='1',name='OUT+',func=pin_types.OUTPUT,unit=1),
            Pin(num='2',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='3',name='GND',func=pin_types.PASSIVE,unit=1),
            Pin(num='4',name='GND',func=pin_types.PASSIVE,unit=1),
            Pin(num='5',name='Vdd',func=pin_types.PWRIN,unit=1),
            Pin(num='6',name='OUT-',func=pin_types.OUTPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'IM69D130', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'IM69D130'}), 'ref_prefix':'MK', 'fplist':['Sensor_Audio:Infineon_PG-LLGA-5-1', 'Sensor_Audio:Infineon_PG-LLGA-5-1'], 'footprint':'Sensor_Audio:Infineon_PG-LLGA-5-1', 'keywords':'mems microphone', 'description':'', 'datasheet':'https://www.infineon.com/dgdl/Infineon-IM69D130-DS-v01_00-EN.pdf?fileId=5546d462602a9dc801607a0e46511a2e', 'search_text':'/usr/share/kicad/symbols/Sensor_Audio.kicad_sym\nIM69D130\n\nmems microphone', 'pins':[
            Pin(num='1',name='DATA',func=pin_types.OUTPUT,unit=1),
            Pin(num='2',name='VDD',func=pin_types.PWRIN,unit=1),
            Pin(num='3',name='CLOCK',func=pin_types.INPUT,unit=1),
            Pin(num='4',name='SELECT',func=pin_types.INPUT,unit=1),
            Pin(num='5',name='GND',func=pin_types.PWRIN,unit=1)], 'unit_defs':[] })])