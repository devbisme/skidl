from collections import defaultdict
from skidl import Pin, Part, Alias, SchLib, SKIDL, TEMPLATE

from skidl.pin import pin_types

SKIDL_lib_version = '0.0.1'

Motor = SchLib(tool=SKIDL).add_parts(*[
        Part(**{ 'name':'Fan', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Fan'}), 'ref_prefix':'M', 'fplist':[''], 'footprint':'', 'keywords':'Fan Motor', 'description':'', 'datasheet':'~', 'search_text':'/usr/share/kicad/symbols/Motor.kicad_sym\nFan\n\nFan Motor', 'pins':[
            Pin(num='1',name='+',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='-',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'Fan_ALT', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Fan_ALT'}), 'ref_prefix':'M', 'fplist':[''], 'footprint':'', 'keywords':'Fan Motor', 'description':'', 'datasheet':'~', 'search_text':'/usr/share/kicad/symbols/Motor.kicad_sym\nFan_ALT\n\nFan Motor', 'pins':[
            Pin(num='1',name='+',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='-',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'Fan_IEC-60617', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Fan_IEC-60617'}), 'ref_prefix':'M', 'fplist':[''], 'footprint':'', 'keywords':'fan motor iec 60617', 'description':'', 'datasheet':'~', 'search_text':'/usr/share/kicad/symbols/Motor.kicad_sym\nFan_IEC-60617\n\nfan motor iec 60617', 'pins':[
            Pin(num='1',name='+',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='-',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'Fan_ISO-14617', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Fan_ISO-14617'}), 'ref_prefix':'M', 'fplist':[''], 'footprint':'', 'keywords':'fan motor iso 14617', 'description':'', 'datasheet':'~', 'search_text':'/usr/share/kicad/symbols/Motor.kicad_sym\nFan_ISO-14617\n\nfan motor iso 14617', 'pins':[
            Pin(num='1',name='+',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='-',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'Fan_Tacho', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Fan_Tacho'}), 'ref_prefix':'M', 'fplist':[''], 'footprint':'', 'keywords':'Fan Motor tacho', 'description':'', 'datasheet':'http://www.hardwarecanucks.com/forum/attachments/new-builds/16287d1330775095-help-chassis-power-fan-connectors-motherboard-asus_p8z68.jpg', 'search_text':'/usr/share/kicad/symbols/Motor.kicad_sym\nFan_Tacho\n\nFan Motor tacho', 'pins':[
            Pin(num='1',name='-',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='+',func=pin_types.PASSIVE,unit=1),
            Pin(num='3',name='Tacho',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'Fan_Tacho_PWM', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Fan_Tacho_PWM'}), 'ref_prefix':'M', 'fplist':[''], 'footprint':'', 'keywords':'Fan Motor tacho PWM', 'description':'', 'datasheet':'http://www.formfactors.org/developer%5Cspecs%5Crev1_2_public.pdf', 'search_text':'/usr/share/kicad/symbols/Motor.kicad_sym\nFan_Tacho_PWM\n\nFan Motor tacho PWM', 'pins':[
            Pin(num='1',name='-',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='+',func=pin_types.PASSIVE,unit=1),
            Pin(num='3',name='Tacho',func=pin_types.PASSIVE,unit=1),
            Pin(num='4',name='PWM',func=pin_types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'Motor_AC', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Motor_AC'}), 'ref_prefix':'M', 'fplist':[''], 'footprint':'', 'keywords':'AC Motor', 'description':'', 'datasheet':'~', 'search_text':'/usr/share/kicad/symbols/Motor.kicad_sym\nMotor_AC\n\nAC Motor', 'pins':[
            Pin(num='1',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='~',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'Motor_DC', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Motor_DC'}), 'ref_prefix':'M', 'fplist':[''], 'footprint':'', 'keywords':'DC Motor', 'description':'', 'datasheet':'~', 'search_text':'/usr/share/kicad/symbols/Motor.kicad_sym\nMotor_DC\n\nDC Motor', 'pins':[
            Pin(num='1',name='+',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='-',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'Motor_DC_ALT', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Motor_DC_ALT'}), 'ref_prefix':'M', 'fplist':[''], 'footprint':'', 'keywords':'DC Motor', 'description':'', 'datasheet':'~', 'search_text':'/usr/share/kicad/symbols/Motor.kicad_sym\nMotor_DC_ALT\n\nDC Motor', 'pins':[
            Pin(num='1',name='+',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='-',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'Motor_Servo', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Motor_Servo'}), 'ref_prefix':'M', 'fplist':[''], 'footprint':'', 'keywords':'Servo Motor', 'description':'', 'datasheet':'http://forums.parallax.com/uploads/attachments/46831/74481.png', 'search_text':'/usr/share/kicad/symbols/Motor.kicad_sym\nMotor_Servo\n\nServo Motor', 'pins':[
            Pin(num='1',name='PWM',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='+',func=pin_types.PASSIVE,unit=1),
            Pin(num='3',name='-',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'Motor_Servo_AirTronics', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Motor_Servo_AirTronics'}), 'ref_prefix':'M', 'fplist':[''], 'footprint':'', 'keywords':'Servo Motor', 'description':'', 'datasheet':'http://forums.parallax.com/uploads/attachments/46831/74481.png', 'search_text':'/usr/share/kicad/symbols/Motor.kicad_sym\nMotor_Servo_AirTronics\n\nServo Motor', 'pins':[
            Pin(num='1',name='+',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='-',func=pin_types.PASSIVE,unit=1),
            Pin(num='3',name='PWM',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'Stepper_Motor_bipolar', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Stepper_Motor_bipolar'}), 'ref_prefix':'M', 'fplist':[''], 'footprint':'', 'keywords':'bipolar stepper motor', 'description':'', 'datasheet':'http://www.infineon.com/dgdl/Application-Note-TLE8110EE_driving_UniPolarStepperMotor_V1.1.pdf?fileId=db3a30431be39b97011be5d0aa0a00b0', 'search_text':'/usr/share/kicad/symbols/Motor.kicad_sym\nStepper_Motor_bipolar\n\nbipolar stepper motor', 'pins':[
            Pin(num='1',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='-',func=pin_types.PASSIVE,unit=1),
            Pin(num='3',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='4',name='~',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'Stepper_Motor_unipolar_5pin', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Stepper_Motor_unipolar_5pin'}), 'ref_prefix':'M', 'fplist':[''], 'footprint':'', 'keywords':'unipolar stepper motor', 'description':'', 'datasheet':'http://www.infineon.com/dgdl/Application-Note-TLE8110EE_driving_UniPolarStepperMotor_V1.1.pdf?fileId=db3a30431be39b97011be5d0aa0a00b0', 'search_text':'/usr/share/kicad/symbols/Motor.kicad_sym\nStepper_Motor_unipolar_5pin\n\nunipolar stepper motor', 'pins':[
            Pin(num='1',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='3',name='-',func=pin_types.PASSIVE,unit=1),
            Pin(num='4',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='5',name='~',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'Stepper_Motor_unipolar_6pin', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Stepper_Motor_unipolar_6pin'}), 'ref_prefix':'M', 'fplist':[''], 'footprint':'', 'keywords':'unipolar stepper motor', 'description':'', 'datasheet':'http://www.infineon.com/dgdl/Application-Note-TLE8110EE_driving_UniPolarStepperMotor_V1.1.pdf?fileId=db3a30431be39b97011be5d0aa0a00b0', 'search_text':'/usr/share/kicad/symbols/Motor.kicad_sym\nStepper_Motor_unipolar_6pin\n\nunipolar stepper motor', 'pins':[
            Pin(num='1',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='3',name='-',func=pin_types.PASSIVE,unit=1),
            Pin(num='4',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='5',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='6',name='~',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'Fan_3pin', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Fan_3pin'}), 'ref_prefix':'M', 'fplist':['', ''], 'footprint':'', 'keywords':'Fan Motor tacho', 'description':'', 'datasheet':'http://www.hardwarecanucks.com/forum/attachments/new-builds/16287d1330775095-help-chassis-power-fan-connectors-motherboard-asus_p8z68.jpg', 'search_text':'/usr/share/kicad/symbols/Motor.kicad_sym\nFan_3pin\n\nFan Motor tacho', 'pins':[
            Pin(num='1',name='-',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='+',func=pin_types.PASSIVE,unit=1),
            Pin(num='3',name='Tacho',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'Fan_4pin', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Fan_4pin'}), 'ref_prefix':'M', 'fplist':['', ''], 'footprint':'', 'keywords':'Fan Motor tacho PWM', 'description':'', 'datasheet':'http://www.formfactors.org/developer%5Cspecs%5Crev1_2_public.pdf', 'search_text':'/usr/share/kicad/symbols/Motor.kicad_sym\nFan_4pin\n\nFan Motor tacho PWM', 'pins':[
            Pin(num='1',name='-',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='+',func=pin_types.PASSIVE,unit=1),
            Pin(num='3',name='Tacho',func=pin_types.PASSIVE,unit=1),
            Pin(num='4',name='PWM',func=pin_types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'Fan_CPU_4pin', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Fan_CPU_4pin'}), 'ref_prefix':'M', 'fplist':['', '', ''], 'footprint':'', 'keywords':'Fan Motor tacho PWM', 'description':'', 'datasheet':'http://www.formfactors.org/developer%5Cspecs%5Crev1_2_public.pdf', 'search_text':'/usr/share/kicad/symbols/Motor.kicad_sym\nFan_CPU_4pin\n\nFan Motor tacho PWM', 'pins':[
            Pin(num='1',name='-',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='+',func=pin_types.PASSIVE,unit=1),
            Pin(num='3',name='Tacho',func=pin_types.PASSIVE,unit=1),
            Pin(num='4',name='PWM',func=pin_types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'Fan_PC_Chassis', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Fan_PC_Chassis'}), 'ref_prefix':'M', 'fplist':['', '', ''], 'footprint':'', 'keywords':'Fan Motor tacho', 'description':'', 'datasheet':'http://www.hardwarecanucks.com/forum/attachments/new-builds/16287d1330775095-help-chassis-power-fan-connectors-motherboard-asus_p8z68.jpg', 'search_text':'/usr/share/kicad/symbols/Motor.kicad_sym\nFan_PC_Chassis\n\nFan Motor tacho', 'pins':[
            Pin(num='1',name='-',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='+',func=pin_types.PASSIVE,unit=1),
            Pin(num='3',name='Tacho',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'Motor_Servo_Futaba_J', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Motor_Servo_Futaba_J'}), 'ref_prefix':'M', 'fplist':['', ''], 'footprint':'', 'keywords':'Servo Motor', 'description':'', 'datasheet':'http://forums.parallax.com/uploads/attachments/46831/74481.png', 'search_text':'/usr/share/kicad/symbols/Motor.kicad_sym\nMotor_Servo_Futaba_J\n\nServo Motor', 'pins':[
            Pin(num='1',name='PWM',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='+',func=pin_types.PASSIVE,unit=1),
            Pin(num='3',name='-',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'Motor_Servo_Grapner_JR', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Motor_Servo_Grapner_JR'}), 'ref_prefix':'M', 'fplist':['', '', ''], 'footprint':'', 'keywords':'Servo Motor', 'description':'', 'datasheet':'http://forums.parallax.com/uploads/attachments/46831/74481.png', 'search_text':'/usr/share/kicad/symbols/Motor.kicad_sym\nMotor_Servo_Grapner_JR\n\nServo Motor', 'pins':[
            Pin(num='1',name='PWM',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='+',func=pin_types.PASSIVE,unit=1),
            Pin(num='3',name='-',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'Motor_Servo_Hitec', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Motor_Servo_Hitec'}), 'ref_prefix':'M', 'fplist':['', '', '', ''], 'footprint':'', 'keywords':'Servo Motor', 'description':'', 'datasheet':'http://forums.parallax.com/uploads/attachments/46831/74481.png', 'search_text':'/usr/share/kicad/symbols/Motor.kicad_sym\nMotor_Servo_Hitec\n\nServo Motor', 'pins':[
            Pin(num='1',name='PWM',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='+',func=pin_types.PASSIVE,unit=1),
            Pin(num='3',name='-',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'Motor_Servo_JR', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Motor_Servo_JR'}), 'ref_prefix':'M', 'fplist':['', '', '', '', ''], 'footprint':'', 'keywords':'Servo Motor', 'description':'', 'datasheet':'http://forums.parallax.com/uploads/attachments/46831/74481.png', 'search_text':'/usr/share/kicad/symbols/Motor.kicad_sym\nMotor_Servo_JR\n\nServo Motor', 'pins':[
            Pin(num='1',name='PWM',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='+',func=pin_types.PASSIVE,unit=1),
            Pin(num='3',name='-',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'Motor_Servo_Robbe', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Motor_Servo_Robbe'}), 'ref_prefix':'M', 'fplist':['', '', '', '', '', ''], 'footprint':'', 'keywords':'Servo Motor', 'description':'', 'datasheet':'http://forums.parallax.com/uploads/attachments/46831/74481.png', 'search_text':'/usr/share/kicad/symbols/Motor.kicad_sym\nMotor_Servo_Robbe\n\nServo Motor', 'pins':[
            Pin(num='1',name='PWM',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='+',func=pin_types.PASSIVE,unit=1),
            Pin(num='3',name='-',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] })])