from skidl import SKIDL, TEMPLATE, Part, Pin, SchLib

SKIDL_lib_version = '0.0.1'

motors = SchLib(tool=SKIDL).add_parts(*[
        Part(name='Fan',dest=TEMPLATE,tool=SKIDL,keywords='Fan Motor',description='Fan',ref_prefix='M',num_units=1,fplist=['Pin_Headers:Pin_Header_Straight_1x02', 'Connect:bornier2', 'TerminalBlock*2pol'],do_erc=True,pins=[
            Pin(num='1',name='+',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='-',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Fan_ALT',dest=TEMPLATE,tool=SKIDL,keywords='Fan Motor',description='Fan without PWM or tach, alternative symbol',ref_prefix='M',num_units=1,fplist=['Pin_Headers:Pin_Header_Straight_1x02', 'Connect:bornier2', 'TerminalBlock*2pol'],do_erc=True,pins=[
            Pin(num='1',name='+',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='-',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Fan_IEC60617',dest=TEMPLATE,tool=SKIDL,keywords='Fan Motor IEC-60617',description='Fan (according to IEC-60617)',ref_prefix='M',num_units=1,fplist=['Pin_Headers:Pin_Header_Straight_1x02', 'Connect:bornier2', 'TerminalBlock*2pol'],do_erc=True,pins=[
            Pin(num='1',name='+',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='-',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Fan_Tacho',dest=TEMPLATE,tool=SKIDL,keywords='Fan Motor tacho',description='Fan, tacho output, 3-pin connector',ref_prefix='M',num_units=1,fplist=['Pin_Headers:Fan_Pin_Header_Straight_1x03', 'Pin_Headers:Pin_Header_Straight_1x03', 'TerminalBlock*3pol', 'bornier3'],do_erc=True,aliases=['Fan_3pin', 'Fan_PC_Chassis'],pins=[
            Pin(num='1',name='Tacho',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='+',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='-',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Fan_Tacho_PWM',dest=TEMPLATE,tool=SKIDL,keywords='Fan Motor tacho PWM',description='Fan, tacho output, PWM input, 4-pin connector',ref_prefix='M',num_units=1,fplist=['Pin_Headers:Fan_Pin_Header_Straight_1x04', 'Pin_Headers:Pin_Header_Straight_1x04', 'TerminalBlock*4pol', 'bornier4'],do_erc=True,aliases=['Fan_CPU_4pin', 'Fan_4pin'],pins=[
            Pin(num='1',name='-',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='+',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='Tacho',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='PWM',do_erc=True)]),
        Part(name='Motor_AC',dest=TEMPLATE,tool=SKIDL,keywords='AC Motor',description='AC Motor',ref_prefix='M',num_units=1,fplist=['Pin_Headers:Pin_Header_Straight_1x02', 'Connect:bornier2', 'TerminalBlock*2pol'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Motor_DC',dest=TEMPLATE,tool=SKIDL,keywords='DC Motor',description='DC Motor',ref_prefix='M',num_units=1,fplist=['Pin_Headers:Pin_Header_Straight_1x02', 'Connect:bornier2', 'TerminalBlock*2pol'],do_erc=True,pins=[
            Pin(num='1',name='+',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='-',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Motor_DC_ALT',dest=TEMPLATE,tool=SKIDL,keywords='DC Motor',description='DC Motor, alternative symbol',ref_prefix='M',num_units=1,fplist=['Pin_Headers:Pin_Header_Straight_1x02', 'Connect:bornier2', 'TerminalBlock*2pol'],do_erc=True,pins=[
            Pin(num='1',name='+',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='-',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Motor_Servo',dest=TEMPLATE,tool=SKIDL,keywords='Servo Motor',description='Servo Motor (Robbe connector)',ref_prefix='M',num_units=1,fplist=['Pin_Headers:Pin_Header_Straight_1x03'],do_erc=True,aliases=['Motor_Servo_JR', 'Motor_Servo_Hitec', 'Motor_Servo_Futaba_J', 'Motor_Servo_Robbe', 'Motor_Servo_Grapner_JR'],pins=[
            Pin(num='1',name='PWM',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='+',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='-',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Motor_Servo_AirTronics',dest=TEMPLATE,tool=SKIDL,keywords='Servo Motor',description='Servo Motor (AirTronics connector)',ref_prefix='M',num_units=1,fplist=['Pin_Headers:Pin_Header_Straight_1x03'],do_erc=True,pins=[
            Pin(num='1',name='+',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='-',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='PWM',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Stepper_Motor_bipolar',dest=TEMPLATE,tool=SKIDL,keywords='bipolar stepper motor',description='4-wire bipolar stepper motor',ref_prefix='M',num_units=1,fplist=['Pin_Headers:Pin_Header_Straight_1x04', 'Connect:bornier4', 'TerminalBlock*4pol'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='-',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Stepper_Motor_unipolar_5pin',dest=TEMPLATE,tool=SKIDL,keywords='unipolar stepper motor',description='5-wire unipolar stepper motor',ref_prefix='M',num_units=1,fplist=['Pin_Headers:Pin_Header_Straight_1x05', 'Connect:bornier5', 'TerminalBlock*5pol'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='-',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Stepper_Motor_unipolar_6pin',dest=TEMPLATE,tool=SKIDL,keywords='unipolar stepper motor',description='6-wire unipolar stepper motor',ref_prefix='M',num_units=1,fplist=['Pin_Headers:Pin_Header_Straight_1x06', 'Connect:bornier6', 'TerminalBlock*6pol'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='-',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='~',func=Pin.PASSIVE,do_erc=True)])])
