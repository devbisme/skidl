from collections import defaultdict
from skidl import Pin, Part, Alias, SchLib, SKIDL, TEMPLATE

from skidl.pin import pin_types

SKIDL_lib_version = '0.0.1'

Sensor_Gas = SchLib(tool=SKIDL).add_parts(*[
        Part(**{ 'name':'004-0-0013', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'004-0-0013'}), 'ref_prefix':'U', 'fplist':[''], 'footprint':'', 'keywords':'Senseair co2 gas sensor pwm modbus', 'description':'', 'datasheet':'https://rmtplusstoragesenseair.blob.core.windows.net/docs/publicerat/PSP107.pdf', 'search_text':'/usr/share/kicad/symbols/Sensor_Gas.kicad_sym\n004-0-0013\n\nSenseair co2 gas sensor pwm modbus', 'pins':[
            Pin(num='1',name='G+',func=pin_types.PWRIN,unit=1),
            Pin(num='2',name='G0',func=pin_types.PWRIN,unit=1),
            Pin(num='3',name='ALARM_OC',func=pin_types.OPENCOLL,unit=1),
            Pin(num='4',name='PWM_1KHZ',func=pin_types.OUTPUT,unit=1),
            Pin(num='5',name='BCAL_IN',func=pin_types.INPUT,unit=1),
            Pin(num='6',name='UART_R/T',func=pin_types.OUTPUT,unit=1),
            Pin(num='7',name='UART_TXD',func=pin_types.OUTPUT,unit=1),
            Pin(num='8',name='UART_RXD',func=pin_types.INPUT,unit=1),
            Pin(num='9',name='DVCC_OUT',func=pin_types.PWROUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'3SP-H2S-50_110-304', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'3SP-H2S-50_110-304'}), 'ref_prefix':'U', 'fplist':['Sensor:SPEC_110-xxx_SMD-10Pin_20x20mm_P4.0mm'], 'footprint':'Sensor:SPEC_110-xxx_SMD-10Pin_20x20mm_P4.0mm', 'keywords':'H2S sensor', 'description':'', 'datasheet':'https://www.spec-sensors.com/wp-content/uploads/2016/10/3SP_H2S_50-C-Package-110-304.pdf', 'search_text':'/usr/share/kicad/symbols/Sensor_Gas.kicad_sym\n3SP-H2S-50_110-304\n\nH2S sensor', 'pins':[
            Pin(num='1',name='Working',func=pin_types.OUTPUT,unit=1),
            Pin(num='10',name='Working',func=pin_types.OUTPUT,unit=1),
            Pin(num='5',name='Reference',func=pin_types.PASSIVE,unit=1),
            Pin(num='6',name='Counter',func=pin_types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'CCS811', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'CCS811'}), 'ref_prefix':'U', 'fplist':['Package_LGA:AMS_LGA-10-1EP_2.7x4mm_P0.6mm'], 'footprint':'Package_LGA:AMS_LGA-10-1EP_2.7x4mm_P0.6mm', 'keywords':'metal oxide gas sensor MOX volatile organix comounds VOC I2C', 'description':'', 'datasheet':'https://www.sciosense.com/wp-content/uploads/documents/SC-001232-DS-3-CCS811B-Datasheet-Revision-2.pdf', 'search_text':'/usr/share/kicad/symbols/Sensor_Gas.kicad_sym\nCCS811\n\nmetal oxide gas sensor MOX volatile organix comounds VOC I2C', 'pins':[
            Pin(num='1',name='ADDR',func=pin_types.INPUT,unit=1),
            Pin(num='10',name='SCL',func=pin_types.INPUT,unit=1),
            Pin(num='11',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='2',name='~{RESET}',func=pin_types.INPUT,unit=1),
            Pin(num='3',name='~{INT}',func=pin_types.OUTPUT,unit=1),
            Pin(num='4',name='PWM',func=pin_types.OUTPUT,unit=1),
            Pin(num='5',name='Sense',func=pin_types.BIDIR,unit=1),
            Pin(num='6',name='VDD',func=pin_types.PWRIN,unit=1),
            Pin(num='7',name='~{WAKE}',func=pin_types.INPUT,unit=1),
            Pin(num='8',name='AUX',func=pin_types.INPUT,unit=1),
            Pin(num='9',name='SDA',func=pin_types.BIDIR,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'GM-402B', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'GM-402B'}), 'ref_prefix':'U', 'fplist':['Sensor:Winson_GM-402B_5x5mm_P1.27mm'], 'footprint':'Sensor:Winson_GM-402B_5x5mm_P1.27mm', 'keywords':'gas sensor', 'description':'', 'datasheet':'https://www.winsen-sensor.com/d/files/me2/mems--gm-402b--manual-v1_1.pdf', 'search_text':'/usr/share/kicad/symbols/Sensor_Gas.kicad_sym\nGM-402B\n\ngas sensor', 'pins':[
            Pin(num='1',name='Rh1',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='NC',func=pin_types.NOCONNECT,unit=1),
            Pin(num='3',name='Rh2',func=pin_types.PASSIVE,unit=1),
            Pin(num='4',name='NC',func=pin_types.NOCONNECT,unit=1),
            Pin(num='5',name='Rs1',func=pin_types.PASSIVE,unit=1),
            Pin(num='6',name='NC',func=pin_types.NOCONNECT,unit=1),
            Pin(num='7',name='Rs2',func=pin_types.PASSIVE,unit=1),
            Pin(num='8',name='NC',func=pin_types.NOCONNECT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'LuminOX_LOX-O2', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'LuminOX_LOX-O2'}), 'ref_prefix':'U', 'fplist':['Sensor:LuminOX_LOX-O2'], 'footprint':'Sensor:LuminOX_LOX-O2', 'keywords':'O2 sensor', 'description':'', 'datasheet':'https://sstsensing.com/wp-content/uploads/2021/08/DS0030rev15_LuminOx.pdf', 'search_text':'/usr/share/kicad/symbols/Sensor_Gas.kicad_sym\nLuminOX_LOX-O2\n\nO2 sensor', 'pins':[
            Pin(num='1',name='Vs',func=pin_types.PWRIN,unit=1),
            Pin(num='2',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='3',name='TXD',func=pin_types.OUTPUT,unit=1),
            Pin(num='4',name='RXD',func=pin_types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'MQ-6', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MQ-6'}), 'ref_prefix':'U', 'fplist':['Sensor:MQ-6'], 'footprint':'Sensor:MQ-6', 'keywords':'flammable gas sensor LPG', 'description':'', 'datasheet':'https://www.winsen-sensor.com/d/files/semiconductor/mq-6.pdf', 'search_text':'/usr/share/kicad/symbols/Sensor_Gas.kicad_sym\nMQ-6\n\nflammable gas sensor LPG', 'pins':[
            Pin(num='1',name='B1',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='VH+',func=pin_types.PWRIN,unit=1),
            Pin(num='3',name='B2',func=pin_types.PASSIVE,unit=1),
            Pin(num='4',name='A2',func=pin_types.PASSIVE,unit=1),
            Pin(num='5',name='VH-',func=pin_types.PWRIN,unit=1),
            Pin(num='6',name='A1',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'MiCS-5524', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MiCS-5524'}), 'ref_prefix':'U', 'fplist':['Sensor:Sensortech_MiCS_5x7mm_P1.25mm'], 'footprint':'Sensor:Sensortech_MiCS_5x7mm_P1.25mm', 'keywords':'CO sensor', 'description':'', 'datasheet':'https://www.sgxsensortech.com/content/uploads/2014/07/1084_Datasheet-MiCS-5524-rev-8.pdf', 'search_text':'/usr/share/kicad/symbols/Sensor_Gas.kicad_sym\nMiCS-5524\n\nCO sensor', 'pins':[
            Pin(num='A',name='NC',func=pin_types.NOCONNECT,unit=1),
            Pin(num='B',name='NC',func=pin_types.NOCONNECT,unit=1),
            Pin(num='C',name='Rh1',func=pin_types.OUTPUT,unit=1),
            Pin(num='D',name='Rs1',func=pin_types.OUTPUT,unit=1),
            Pin(num='E',name='NC',func=pin_types.NOCONNECT,unit=1),
            Pin(num='F',name='Rh2',func=pin_types.INPUT,unit=1),
            Pin(num='G',name='Rs2',func=pin_types.INPUT,unit=1),
            Pin(num='H',name='NC',func=pin_types.NOCONNECT,unit=1),
            Pin(num='J',name='NC',func=pin_types.NOCONNECT,unit=1),
            Pin(num='K',name='NC',func=pin_types.NOCONNECT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'SCD40-D-R2', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'SCD40-D-R2'}), 'ref_prefix':'U', 'fplist':['Sensor:Sensirion_SCD4x-1EP_10.1x10.1mm_P1.25mm_EP4.8x4.8mm'], 'footprint':'Sensor:Sensirion_SCD4x-1EP_10.1x10.1mm_P1.25mm_EP4.8x4.8mm', 'keywords':'CO2 sensor I2C', 'description':'', 'datasheet':'https://sensirion.com/media/documents/E0F04247/631EF271/CD_DS_SCD40_SCD41_Datasheet_D1.pdf', 'search_text':'/usr/share/kicad/symbols/Sensor_Gas.kicad_sym\nSCD40-D-R2\n\nCO2 sensor I2C', 'pins':[
            Pin(num='10',name='SDA',func=pin_types.BIDIR,unit=1),
            Pin(num='19',name='VDD',func=pin_types.PASSIVE,unit=1),
            Pin(num='20',name='GND',func=pin_types.PASSIVE,unit=1),
            Pin(num='21',name='GND',func=pin_types.PASSIVE,unit=1),
            Pin(num='6',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='7',name='VDD',func=pin_types.PWRIN,unit=1),
            Pin(num='9',name='SCL',func=pin_types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TGS-5141', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TGS-5141'}), 'ref_prefix':'U', 'fplist':['Sensor:TGS-5141'], 'footprint':'Sensor:TGS-5141', 'keywords':'CO sensor', 'description':'', 'datasheet':'https://figarosensor.com/product/docs/tgs5141-p00_product%20infomation%28fusa%29_rev07.pdf', 'search_text':'/usr/share/kicad/symbols/Sensor_Gas.kicad_sym\nTGS-5141\n\nCO sensor', 'pins':[
            Pin(num='1',name='Working',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='Counter',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'004-0-0010', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'004-0-0010'}), 'ref_prefix':'U', 'fplist':['', ''], 'footprint':'', 'keywords':'Senseair co2 gas sensor pwm modbus', 'description':'', 'datasheet':'https://rmtplusstoragesenseair.blob.core.windows.net/docs/publicerat/PSP103.pdf', 'search_text':'/usr/share/kicad/symbols/Sensor_Gas.kicad_sym\n004-0-0010\n\nSenseair co2 gas sensor pwm modbus', 'pins':[
            Pin(num='1',name='G+',func=pin_types.PWRIN,unit=1),
            Pin(num='2',name='G0',func=pin_types.PWRIN,unit=1),
            Pin(num='3',name='ALARM_OC',func=pin_types.OPENCOLL,unit=1),
            Pin(num='4',name='PWM_1KHZ',func=pin_types.OUTPUT,unit=1),
            Pin(num='5',name='BCAL_IN',func=pin_types.INPUT,unit=1),
            Pin(num='6',name='UART_R/T',func=pin_types.OUTPUT,unit=1),
            Pin(num='7',name='UART_TXD',func=pin_types.OUTPUT,unit=1),
            Pin(num='8',name='UART_RXD',func=pin_types.INPUT,unit=1),
            Pin(num='9',name='DVCC_OUT',func=pin_types.PWROUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'004-0-0050', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'004-0-0050'}), 'ref_prefix':'U', 'fplist':['', '', ''], 'footprint':'', 'keywords':'Senseair co2 gas sensor pwm modbus', 'description':'', 'datasheet':'https://rmtplusstoragesenseair.blob.core.windows.net/docs/publicerat/PSP108.pdf', 'search_text':'/usr/share/kicad/symbols/Sensor_Gas.kicad_sym\n004-0-0050\n\nSenseair co2 gas sensor pwm modbus', 'pins':[
            Pin(num='1',name='G+',func=pin_types.PWRIN,unit=1),
            Pin(num='2',name='G0',func=pin_types.PWRIN,unit=1),
            Pin(num='3',name='ALARM_OC',func=pin_types.OPENCOLL,unit=1),
            Pin(num='4',name='PWM_1KHZ',func=pin_types.OUTPUT,unit=1),
            Pin(num='5',name='BCAL_IN',func=pin_types.INPUT,unit=1),
            Pin(num='6',name='UART_R/T',func=pin_types.OUTPUT,unit=1),
            Pin(num='7',name='UART_TXD',func=pin_types.OUTPUT,unit=1),
            Pin(num='8',name='UART_RXD',func=pin_types.INPUT,unit=1),
            Pin(num='9',name='DVCC_OUT',func=pin_types.PWROUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'004-0-0053', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'004-0-0053'}), 'ref_prefix':'U', 'fplist':['', '', '', ''], 'footprint':'', 'keywords':'Senseair co2 gas sensor pwm modbus', 'description':'', 'datasheet':'https://rmtplusstoragesenseair.blob.core.windows.net/docs/publicerat/PSP126.pdf', 'search_text':'/usr/share/kicad/symbols/Sensor_Gas.kicad_sym\n004-0-0053\n\nSenseair co2 gas sensor pwm modbus', 'pins':[
            Pin(num='1',name='G+',func=pin_types.PWRIN,unit=1),
            Pin(num='2',name='G0',func=pin_types.PWRIN,unit=1),
            Pin(num='3',name='ALARM_OC',func=pin_types.OPENCOLL,unit=1),
            Pin(num='4',name='PWM_1KHZ',func=pin_types.OUTPUT,unit=1),
            Pin(num='5',name='BCAL_IN',func=pin_types.INPUT,unit=1),
            Pin(num='6',name='UART_R/T',func=pin_types.OUTPUT,unit=1),
            Pin(num='7',name='UART_TXD',func=pin_types.OUTPUT,unit=1),
            Pin(num='8',name='UART_RXD',func=pin_types.INPUT,unit=1),
            Pin(num='9',name='DVCC_OUT',func=pin_types.PWROUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'004-0-0071', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'004-0-0071'}), 'ref_prefix':'U', 'fplist':['', '', '', '', ''], 'footprint':'', 'keywords':'Senseair co2 gas sensor pwm modbus', 'description':'', 'datasheet':'https://rmtplusstoragesenseair.blob.core.windows.net/docs/publicerat/PSP0113.pdf', 'search_text':'/usr/share/kicad/symbols/Sensor_Gas.kicad_sym\n004-0-0071\n\nSenseair co2 gas sensor pwm modbus', 'pins':[
            Pin(num='1',name='G+',func=pin_types.PWRIN,unit=1),
            Pin(num='2',name='G0',func=pin_types.PWRIN,unit=1),
            Pin(num='3',name='ALARM_OC',func=pin_types.OPENCOLL,unit=1),
            Pin(num='4',name='PWM_1KHZ',func=pin_types.OUTPUT,unit=1),
            Pin(num='5',name='BCAL_IN',func=pin_types.INPUT,unit=1),
            Pin(num='6',name='UART_R/T',func=pin_types.OUTPUT,unit=1),
            Pin(num='7',name='UART_TXD',func=pin_types.OUTPUT,unit=1),
            Pin(num='8',name='UART_RXD',func=pin_types.INPUT,unit=1),
            Pin(num='9',name='DVCC_OUT',func=pin_types.PWROUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'004-0-0075', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'004-0-0075'}), 'ref_prefix':'U', 'fplist':['', '', '', '', '', ''], 'footprint':'', 'keywords':'Senseair co2 gas sensor pwm modbus', 'description':'', 'datasheet':'https://rmtplusstoragesenseair.blob.core.windows.net/docs/publicerat/PSP103.pdf', 'search_text':'/usr/share/kicad/symbols/Sensor_Gas.kicad_sym\n004-0-0075\n\nSenseair co2 gas sensor pwm modbus', 'pins':[
            Pin(num='1',name='G+',func=pin_types.PWRIN,unit=1),
            Pin(num='2',name='G0',func=pin_types.PWRIN,unit=1),
            Pin(num='3',name='ALARM_OC',func=pin_types.OPENCOLL,unit=1),
            Pin(num='4',name='PWM_1KHZ',func=pin_types.OUTPUT,unit=1),
            Pin(num='5',name='BCAL_IN',func=pin_types.INPUT,unit=1),
            Pin(num='6',name='UART_R/T',func=pin_types.OUTPUT,unit=1),
            Pin(num='7',name='UART_TXD',func=pin_types.OUTPUT,unit=1),
            Pin(num='8',name='UART_RXD',func=pin_types.INPUT,unit=1),
            Pin(num='9',name='DVCC_OUT',func=pin_types.PWROUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'SCD41-D-R2', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'SCD41-D-R2'}), 'ref_prefix':'U', 'fplist':['Sensor:Sensirion_SCD4x-1EP_10.1x10.1mm_P1.25mm_EP4.8x4.8mm', 'Sensor:Sensirion_SCD4x-1EP_10.1x10.1mm_P1.25mm_EP4.8x4.8mm'], 'footprint':'Sensor:Sensirion_SCD4x-1EP_10.1x10.1mm_P1.25mm_EP4.8x4.8mm', 'keywords':'CO2 sensor I2C', 'description':'', 'datasheet':'https://sensirion.com/media/documents/E0F04247/631EF271/CD_DS_SCD40_SCD41_Datasheet_D1.pdf', 'search_text':'/usr/share/kicad/symbols/Sensor_Gas.kicad_sym\nSCD41-D-R2\n\nCO2 sensor I2C', 'pins':[
            Pin(num='10',name='SDA',func=pin_types.BIDIR,unit=1),
            Pin(num='19',name='VDD',func=pin_types.PASSIVE,unit=1),
            Pin(num='20',name='GND',func=pin_types.PASSIVE,unit=1),
            Pin(num='21',name='GND',func=pin_types.PASSIVE,unit=1),
            Pin(num='6',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='7',name='VDD',func=pin_types.PWRIN,unit=1),
            Pin(num='9',name='SCL',func=pin_types.INPUT,unit=1)], 'unit_defs':[] })])