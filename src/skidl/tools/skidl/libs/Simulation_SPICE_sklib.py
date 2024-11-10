from collections import defaultdict
from skidl import Pin, Part, Alias, SchLib, SKIDL, TEMPLATE

from skidl.pin import pin_types

SKIDL_lib_version = '0.0.1'

Simulation_SPICE = SchLib(tool=SKIDL).add_parts(*[
        Part(**{ 'name':'0', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'0'}), 'ref_prefix':'#GND', 'fplist':[''], 'footprint':'', 'keywords':'simulation', 'description':'', 'datasheet':'https://ngspice.sourceforge.io/docs/ngspice-html-manual/manual.xhtml#subsec_Circuit_elements__device', 'search_text':'/usr/share/kicad/symbols/Simulation_SPICE.kicad_sym\n0\n\nsimulation', 'pins':[
            Pin(num='1',name='~',func=pin_types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'BSOURCE', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'BSOURCE'}), 'ref_prefix':'B', 'fplist':[''], 'footprint':'', 'keywords':'simulation dependent', 'description':'', 'datasheet':'https://ngspice.sourceforge.io/docs/ngspice-html-manual/manual.xhtml#sec_Non_linear_Dependent_Sources', 'search_text':'/usr/share/kicad/symbols/Simulation_SPICE.kicad_sym\nBSOURCE\n\nsimulation dependent', 'pins':[
            Pin(num='1',name='N+',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='N-',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'D', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'D'}), 'ref_prefix':'D', 'fplist':[''], 'footprint':'', 'keywords':'simulation', 'description':'', 'datasheet':'https://ngspice.sourceforge.io/docs/ngspice-html-manual/manual.xhtml#cha_DIODEs', 'search_text':'/usr/share/kicad/symbols/Simulation_SPICE.kicad_sym\nD\n\nsimulation', 'pins':[
            Pin(num='1',name='K',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='A',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'ESOURCE', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'ESOURCE'}), 'ref_prefix':'E', 'fplist':[''], 'footprint':'', 'keywords':'simulation vcvs dependent', 'description':'', 'datasheet':'https://ngspice.sourceforge.io/docs/ngspice-html-manual/manual.xhtml#subsec_Exxxx__Linear_Voltage_Controlled', 'search_text':'/usr/share/kicad/symbols/Simulation_SPICE.kicad_sym\nESOURCE\n\nsimulation vcvs dependent', 'pins':[
            Pin(num='1',name='N+',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='N-',func=pin_types.PASSIVE,unit=1),
            Pin(num='3',name='C+',func=pin_types.INPUT,unit=1),
            Pin(num='4',name='C-',func=pin_types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'GSOURCE', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'GSOURCE'}), 'ref_prefix':'G', 'fplist':[''], 'footprint':'', 'keywords':'simulation vccs dependent', 'description':'', 'datasheet':'https://ngspice.sourceforge.io/docs/ngspice-html-manual/manual.xhtml#subsec_Gxxxx__Linear_Voltage_Controlled', 'search_text':'/usr/share/kicad/symbols/Simulation_SPICE.kicad_sym\nGSOURCE\n\nsimulation vccs dependent', 'pins':[
            Pin(num='1',name='N+',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='N-',func=pin_types.PASSIVE,unit=1),
            Pin(num='3',name='C+',func=pin_types.INPUT,unit=1),
            Pin(num='4',name='C-',func=pin_types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'IAM', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'IAM'}), 'ref_prefix':'I', 'fplist':[''], 'footprint':'', 'keywords':'simulation amplitude modulated', 'description':'', 'datasheet':'https://ngspice.sourceforge.io/docs/ngspice-html-manual/manual.xhtml#sec_Independent_Sources_for', 'search_text':'/usr/share/kicad/symbols/Simulation_SPICE.kicad_sym\nIAM\n\nsimulation amplitude modulated', 'pins':[
            Pin(num='1',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='~',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'IBIS_DEVICE', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'IBIS_DEVICE'}), 'ref_prefix':'U?', 'fplist':[''], 'footprint':'', 'keywords':'Simulation IBIS', 'description':'', 'datasheet':'https://ibis.org', 'search_text':'/usr/share/kicad/symbols/Simulation_SPICE.kicad_sym\nIBIS_DEVICE\n\nSimulation IBIS', 'pins':[
            Pin(num='1',name='REF',func=pin_types.PWRIN,unit=1),
            Pin(num='2',func=pin_types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'IBIS_DEVICE_DIFF', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'IBIS_DEVICE_DIFF'}), 'ref_prefix':'U?', 'fplist':[''], 'footprint':'', 'keywords':'Simulation IBIS', 'description':'', 'datasheet':'https://ibis.org', 'search_text':'/usr/share/kicad/symbols/Simulation_SPICE.kicad_sym\nIBIS_DEVICE_DIFF\n\nSimulation IBIS', 'pins':[
            Pin(num='1',name='REF',func=pin_types.PWRIN,unit=1),
            Pin(num='2',name='+',func=pin_types.INPUT,unit=1),
            Pin(num='3',name='-',func=pin_types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'IBIS_DRIVER', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'IBIS_DRIVER'}), 'ref_prefix':'U?', 'fplist':[''], 'footprint':'', 'keywords':'Simulation IBIS', 'description':'', 'datasheet':'https://ibis.org', 'search_text':'/usr/share/kicad/symbols/Simulation_SPICE.kicad_sym\nIBIS_DRIVER\n\nSimulation IBIS', 'pins':[
            Pin(num='1',name='REF',func=pin_types.PWRIN,unit=1),
            Pin(num='2',func=pin_types.BIDIR,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'IBIS_DRIVER_DIFF', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'IBIS_DRIVER_DIFF'}), 'ref_prefix':'U?', 'fplist':[''], 'footprint':'', 'keywords':'Simulation IBIS', 'description':'', 'datasheet':'https://ibis.org', 'search_text':'/usr/share/kicad/symbols/Simulation_SPICE.kicad_sym\nIBIS_DRIVER_DIFF\n\nSimulation IBIS', 'pins':[
            Pin(num='1',name='REF',func=pin_types.PWRIN,unit=1),
            Pin(num='2',name='+',func=pin_types.BIDIR,unit=1),
            Pin(num='3',name='-',func=pin_types.BIDIR,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'IDC', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'IDC'}), 'ref_prefix':'I', 'fplist':[''], 'footprint':'', 'keywords':'simulation', 'description':'', 'datasheet':'https://ngspice.sourceforge.io/docs/ngspice-html-manual/manual.xhtml#sec_Independent_Sources_for', 'search_text':'/usr/share/kicad/symbols/Simulation_SPICE.kicad_sym\nIDC\n\nsimulation', 'pins':[
            Pin(num='1',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='~',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'IEXP', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'IEXP'}), 'ref_prefix':'I', 'fplist':[''], 'footprint':'', 'keywords':'simulation', 'description':'', 'datasheet':'https://ngspice.sourceforge.io/docs/ngspice-html-manual/manual.xhtml#sec_Independent_Sources_for', 'search_text':'/usr/share/kicad/symbols/Simulation_SPICE.kicad_sym\nIEXP\n\nsimulation', 'pins':[
            Pin(num='1',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='~',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'IPULSE', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'IPULSE'}), 'ref_prefix':'I', 'fplist':[''], 'footprint':'', 'keywords':'simulation', 'description':'', 'datasheet':'https://ngspice.sourceforge.io/docs/ngspice-html-manual/manual.xhtml#sec_Independent_Sources_for', 'search_text':'/usr/share/kicad/symbols/Simulation_SPICE.kicad_sym\nIPULSE\n\nsimulation', 'pins':[
            Pin(num='1',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='~',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'IPWL', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'IPWL'}), 'ref_prefix':'I', 'fplist':[''], 'footprint':'', 'keywords':'simulation', 'description':'', 'datasheet':'https://ngspice.sourceforge.io/docs/ngspice-html-manual/manual.xhtml#sec_Independent_Sources_for', 'search_text':'/usr/share/kicad/symbols/Simulation_SPICE.kicad_sym\nIPWL\n\nsimulation', 'pins':[
            Pin(num='1',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='~',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'ISFFM', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'ISFFM'}), 'ref_prefix':'I', 'fplist':[''], 'footprint':'', 'keywords':'simulation frequency modulated', 'description':'', 'datasheet':'https://ngspice.sourceforge.io/docs/ngspice-html-manual/manual.xhtml#sec_Independent_Sources_for', 'search_text':'/usr/share/kicad/symbols/Simulation_SPICE.kicad_sym\nISFFM\n\nsimulation frequency modulated', 'pins':[
            Pin(num='1',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='~',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'ISIN', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'ISIN'}), 'ref_prefix':'I', 'fplist':[''], 'footprint':'', 'keywords':'simulation', 'description':'', 'datasheet':'https://ngspice.sourceforge.io/docs/ngspice-html-manual/manual.xhtml#sec_Independent_Sources_for', 'search_text':'/usr/share/kicad/symbols/Simulation_SPICE.kicad_sym\nISIN\n\nsimulation', 'pins':[
            Pin(num='1',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='~',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'ITRNOISE', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'ITRNOISE'}), 'ref_prefix':'I', 'fplist':[''], 'footprint':'', 'keywords':'simulation', 'description':'', 'datasheet':'https://ngspice.sourceforge.io/docs/ngspice-html-manual/manual.xhtml#subsec_Transient_noise_source', 'search_text':'/usr/share/kicad/symbols/Simulation_SPICE.kicad_sym\nITRNOISE\n\nsimulation', 'pins':[
            Pin(num='1',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='~',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'ITRRANDOM', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'ITRRANDOM'}), 'ref_prefix':'I', 'fplist':[''], 'footprint':'', 'keywords':'simulation', 'description':'', 'datasheet':'https://ngspice.sourceforge.io/docs/ngspice-html-manual/manual.xhtml#subsec_Random_voltage_source', 'search_text':'/usr/share/kicad/symbols/Simulation_SPICE.kicad_sym\nITRRANDOM\n\nsimulation', 'pins':[
            Pin(num='1',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='~',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'NJFET', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'NJFET'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'transistor NJFET N-JFET', 'description':'', 'datasheet':'https://ngspice.sourceforge.io/docs/ngspice-html-manual/manual.xhtml#cha_JFETs', 'search_text':'/usr/share/kicad/symbols/Simulation_SPICE.kicad_sym\nNJFET\n\ntransistor NJFET N-JFET', 'pins':[
            Pin(num='1',name='D',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='G',func=pin_types.INPUT,unit=1),
            Pin(num='3',name='S',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'NMOS', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'NMOS'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'transistor NMOS N-MOS N-MOSFET simulation', 'description':'', 'datasheet':'https://ngspice.sourceforge.io/docs/ngspice-html-manual/manual.xhtml#cha_MOSFETs', 'search_text':'/usr/share/kicad/symbols/Simulation_SPICE.kicad_sym\nNMOS\n\ntransistor NMOS N-MOS N-MOSFET simulation', 'pins':[
            Pin(num='1',name='D',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='G',func=pin_types.INPUT,unit=1),
            Pin(num='3',name='S',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'NMOS_Substrate', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'NMOS_Substrate'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'mosfet nmos simulation', 'description':'', 'datasheet':'https://ngspice.sourceforge.io/docs/ngspice-html-manual/manual.xhtml#cha_MOSFETs', 'search_text':'/usr/share/kicad/symbols/Simulation_SPICE.kicad_sym\nNMOS_Substrate\n\nmosfet nmos simulation', 'pins':[
            Pin(num='1',name='D',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='G',func=pin_types.INPUT,unit=1),
            Pin(num='3',name='S',func=pin_types.PASSIVE,unit=1),
            Pin(num='4',name='Bulk',func=pin_types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'NPN', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'NPN'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'simulation', 'description':'', 'datasheet':'https://ngspice.sourceforge.io/docs/ngspice-html-manual/manual.xhtml#cha_BJTs', 'search_text':'/usr/share/kicad/symbols/Simulation_SPICE.kicad_sym\nNPN\n\nsimulation', 'pins':[
            Pin(num='1',name='C',func=pin_types.OPENCOLL,unit=1),
            Pin(num='2',name='B',func=pin_types.INPUT,unit=1),
            Pin(num='3',name='E',func=pin_types.OPENEMIT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'NPN_Substrate', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'NPN_Substrate'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'simulation', 'description':'', 'datasheet':'https://ngspice.sourceforge.io/docs/ngspice-html-manual/manual.xhtml#cha_BJTs', 'search_text':'/usr/share/kicad/symbols/Simulation_SPICE.kicad_sym\nNPN_Substrate\n\nsimulation', 'pins':[
            Pin(num='1',name='C',func=pin_types.OPENCOLL,unit=1),
            Pin(num='2',name='B',func=pin_types.INPUT,unit=1),
            Pin(num='3',name='E',func=pin_types.OPENEMIT,unit=1),
            Pin(num='4',name='Substrate',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'OPAMP', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'OPAMP'}), 'ref_prefix':'U', 'fplist':[''], 'footprint':'', 'keywords':'simulation', 'description':'', 'datasheet':'https://ngspice.sourceforge.io/docs/ngspice-html-manual/manual.xhtml#sec__SUBCKT_Subcircuits', 'search_text':'/usr/share/kicad/symbols/Simulation_SPICE.kicad_sym\nOPAMP\n\nsimulation', 'pins':[
            Pin(num='1',name='+',func=pin_types.INPUT,unit=1),
            Pin(num='2',name='-',func=pin_types.INPUT,unit=1),
            Pin(num='3',name='V+',func=pin_types.PWRIN,unit=1),
            Pin(num='4',name='V-',func=pin_types.PWRIN,unit=1),
            Pin(num='5',name='~',func=pin_types.OUTPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'PJFET', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'PJFET'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'transistor PJFET P-JFET', 'description':'', 'datasheet':'https://ngspice.sourceforge.io/docs/ngspice-html-manual/manual.xhtml#cha_JFETs', 'search_text':'/usr/share/kicad/symbols/Simulation_SPICE.kicad_sym\nPJFET\n\ntransistor PJFET P-JFET', 'pins':[
            Pin(num='1',name='D',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='G',func=pin_types.INPUT,unit=1),
            Pin(num='3',name='S',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'PMOS', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'PMOS'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'transistor PMOS P-MOS P-MOSFET simulation', 'description':'', 'datasheet':'https://ngspice.sourceforge.io/docs/ngspice-html-manual/manual.xhtml#cha_MOSFETs', 'search_text':'/usr/share/kicad/symbols/Simulation_SPICE.kicad_sym\nPMOS\n\ntransistor PMOS P-MOS P-MOSFET simulation', 'pins':[
            Pin(num='1',name='D',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='G',func=pin_types.INPUT,unit=1),
            Pin(num='3',name='S',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'PMOS_Substrate', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'PMOS_Substrate'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'mosfet pmos simulation', 'description':'', 'datasheet':'https://ngspice.sourceforge.io/docs/ngspice-html-manual/manual.xhtml#cha_MOSFETs', 'search_text':'/usr/share/kicad/symbols/Simulation_SPICE.kicad_sym\nPMOS_Substrate\n\nmosfet pmos simulation', 'pins':[
            Pin(num='1',name='D',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='G',func=pin_types.INPUT,unit=1),
            Pin(num='3',name='S',func=pin_types.PASSIVE,unit=1),
            Pin(num='4',name='Bulk',func=pin_types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'PNP', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'PNP'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'simulation', 'description':'', 'datasheet':'https://ngspice.sourceforge.io/docs/ngspice-html-manual/manual.xhtml#cha_BJTs', 'search_text':'/usr/share/kicad/symbols/Simulation_SPICE.kicad_sym\nPNP\n\nsimulation', 'pins':[
            Pin(num='1',name='C',func=pin_types.OPENCOLL,unit=1),
            Pin(num='2',name='B',func=pin_types.INPUT,unit=1),
            Pin(num='3',name='E',func=pin_types.OPENEMIT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'PNP_Substrate', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'PNP_Substrate'}), 'ref_prefix':'Q', 'fplist':[''], 'footprint':'', 'keywords':'simulation', 'description':'', 'datasheet':'https://ngspice.sourceforge.io/docs/ngspice-html-manual/manual.xhtml#cha_BJTs', 'search_text':'/usr/share/kicad/symbols/Simulation_SPICE.kicad_sym\nPNP_Substrate\n\nsimulation', 'pins':[
            Pin(num='1',name='C',func=pin_types.OPENCOLL,unit=1),
            Pin(num='2',name='B',func=pin_types.INPUT,unit=1),
            Pin(num='3',name='E',func=pin_types.OPENEMIT,unit=1),
            Pin(num='4',name='Substrate',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'SWITCH', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'SWITCH'}), 'ref_prefix':'S', 'fplist':[''], 'footprint':'', 'keywords':'simulation', 'description':'', 'datasheet':'https://ngspice.sourceforge.io/docs/ngspice-html-manual/manual.xhtml#subsec_Switches', 'search_text':'/usr/share/kicad/symbols/Simulation_SPICE.kicad_sym\nSWITCH\n\nsimulation', 'pins':[
            Pin(num='1',name='N+',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='N-',func=pin_types.PASSIVE,unit=1),
            Pin(num='3',name='C+',func=pin_types.INPUT,unit=1),
            Pin(num='4',name='C-',func=pin_types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TLINE', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TLINE'}), 'ref_prefix':'T', 'fplist':[''], 'footprint':'', 'keywords':'lossless transmission line characteristic impedance', 'description':'', 'datasheet':'https://ngspice.sourceforge.io/docs/ngspice-html-manual/manual.xhtml#sec_Lossless_Transmission_Lines', 'search_text':'/usr/share/kicad/symbols/Simulation_SPICE.kicad_sym\nTLINE\n\nlossless transmission line characteristic impedance', 'pins':[
            Pin(num='1',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',func=pin_types.PASSIVE,unit=1),
            Pin(num='3',func=pin_types.PASSIVE,unit=1),
            Pin(num='4',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'VAM', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'VAM'}), 'ref_prefix':'V', 'fplist':[''], 'footprint':'', 'keywords':'simulation amplitude modulated', 'description':'', 'datasheet':'https://ngspice.sourceforge.io/docs/ngspice-html-manual/manual.xhtml#sec_Independent_Sources_for', 'search_text':'/usr/share/kicad/symbols/Simulation_SPICE.kicad_sym\nVAM\n\nsimulation amplitude modulated', 'pins':[
            Pin(num='1',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='~',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'VDC', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'VDC'}), 'ref_prefix':'V', 'fplist':[''], 'footprint':'', 'keywords':'simulation', 'description':'', 'datasheet':'https://ngspice.sourceforge.io/docs/ngspice-html-manual/manual.xhtml#sec_Independent_Sources_for', 'search_text':'/usr/share/kicad/symbols/Simulation_SPICE.kicad_sym\nVDC\n\nsimulation', 'pins':[
            Pin(num='1',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='~',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'VEXP', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'VEXP'}), 'ref_prefix':'V', 'fplist':[''], 'footprint':'', 'keywords':'simulation', 'description':'', 'datasheet':'https://ngspice.sourceforge.io/docs/ngspice-html-manual/manual.xhtml#sec_Independent_Sources_for', 'search_text':'/usr/share/kicad/symbols/Simulation_SPICE.kicad_sym\nVEXP\n\nsimulation', 'pins':[
            Pin(num='1',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='~',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'VOLTMETER_DIFF', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'VOLTMETER_DIFF'}), 'ref_prefix':'MES?', 'fplist':[''], 'footprint':'', 'keywords':'voltmeter differential vdiff', 'description':'', 'datasheet':'https://ngspice.sourceforge.io/docs/ngspice-html-manual/manual.xhtml#sec__SUBCKT_Subcircuits', 'search_text':'/usr/share/kicad/symbols/Simulation_SPICE.kicad_sym\nVOLTMETER_DIFF\n\nvoltmeter differential vdiff', 'pins':[
            Pin(num='1',name='+',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='-',func=pin_types.PASSIVE,unit=1),
            Pin(num='3',name='out',func=pin_types.OUTPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'VPULSE', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'VPULSE'}), 'ref_prefix':'V', 'fplist':[''], 'footprint':'', 'keywords':'simulation', 'description':'', 'datasheet':'https://ngspice.sourceforge.io/docs/ngspice-html-manual/manual.xhtml#sec_Independent_Sources_for', 'search_text':'/usr/share/kicad/symbols/Simulation_SPICE.kicad_sym\nVPULSE\n\nsimulation', 'pins':[
            Pin(num='1',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='~',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'VPWL', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'VPWL'}), 'ref_prefix':'V', 'fplist':[''], 'footprint':'', 'keywords':'simulation', 'description':'', 'datasheet':'https://ngspice.sourceforge.io/docs/ngspice-html-manual/manual.xhtml#sec_Independent_Sources_for', 'search_text':'/usr/share/kicad/symbols/Simulation_SPICE.kicad_sym\nVPWL\n\nsimulation', 'pins':[
            Pin(num='1',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='~',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'VSFFM', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'VSFFM'}), 'ref_prefix':'V', 'fplist':[''], 'footprint':'', 'keywords':'simulation frequency modulated', 'description':'', 'datasheet':'https://ngspice.sourceforge.io/docs/ngspice-html-manual/manual.xhtml#sec_Independent_Sources_for', 'search_text':'/usr/share/kicad/symbols/Simulation_SPICE.kicad_sym\nVSFFM\n\nsimulation frequency modulated', 'pins':[
            Pin(num='1',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='~',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'VSIN', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'VSIN'}), 'ref_prefix':'V', 'fplist':[''], 'footprint':'', 'keywords':'simulation ac vac', 'description':'', 'datasheet':'https://ngspice.sourceforge.io/docs/ngspice-html-manual/manual.xhtml#sec_Independent_Sources_for', 'search_text':'/usr/share/kicad/symbols/Simulation_SPICE.kicad_sym\nVSIN\n\nsimulation ac vac', 'pins':[
            Pin(num='1',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='~',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'VTRNOISE', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'VTRNOISE'}), 'ref_prefix':'V', 'fplist':[''], 'footprint':'', 'keywords':'simulation', 'description':'', 'datasheet':'https://ngspice.sourceforge.io/docs/ngspice-html-manual/manual.xhtml#subsec_Transient_noise_source', 'search_text':'/usr/share/kicad/symbols/Simulation_SPICE.kicad_sym\nVTRNOISE\n\nsimulation', 'pins':[
            Pin(num='1',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='~',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'VTRRANDOM', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'VTRRANDOM'}), 'ref_prefix':'V', 'fplist':[''], 'footprint':'', 'keywords':'simulation', 'description':'', 'datasheet':'https://ngspice.sourceforge.io/docs/ngspice-html-manual/manual.xhtml#subsec_Random_voltage_source', 'search_text':'/usr/share/kicad/symbols/Simulation_SPICE.kicad_sym\nVTRRANDOM\n\nsimulation', 'pins':[
            Pin(num='1',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='~',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] })])