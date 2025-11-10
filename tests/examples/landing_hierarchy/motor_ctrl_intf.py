from skidl import *

@subcircuit
def voltage_regulator():
    """3.3V linear voltage regulator module."""

    # Create voltage regulator and filter capacitors
    reg = Part('Regulator_Linear', 'AMS1117-3.3')
    c_in = Part('Device', 'C', value='100nF')
    c_out = Part('Device', 'C', value='10uF')
    
    # Attach input/output filter capacitors.
    reg['VI'] & c_in & reg['GND']
    reg['VO'] & c_out & reg['GND']

    # Return interface connections
    return Interface(
        vin=reg['VI'],      # Unregulated supply voltage
        vout=reg['VO'],     # Regulated output voltage
        gnd=reg['GND']      # Ground connection
        )

@subcircuit
def motor_driver():
    """H-bridge motor driver module."""
    
    # Create MOSFETs for H-bridge
    q1, q2, q3, q4 = Part('Transistor_FET', 'Q_NMOS_GSD', dest=TEMPLATE)(4)
    
    # Define local nets for power and motor connections
    vcc, gnd = Net(), Net()          # Motor supply voltages
    motor_a, motor_b = Net(), Net()  # Motor terminals
    
    # Build H-bridge topology
    vcc & q1['D,S'] & motor_a & q2['D,S'] & gnd
    vcc & q3['D,S'] & motor_b & q4['D,S'] & gnd

    # Return interface connections
    return Interface(
        vcc=vcc,             # Motor supply voltage
        gnd=gnd,             # Ground
        motor_a=motor_a,     # Motor terminal A
        motor_b=motor_b,     # Motor terminal B
        ctrl1=q1['G'],       # Control signal 1
        ctrl2=q2['G'],       # Control signal 2
        ctrl3=q3['G'],       # Control signal 3
        ctrl4=q4['G']        # Control signal 4
        )

# Instantiate subcircuit modules
regulator = voltage_regulator()
motor_drv = motor_driver()

# Instantiate a DC motor
motor = Part("Motor", "Motor_DC")

# Create nets for power distribution
power_12v = Net('12V_IN')
power_3v3 = Net('3V3')
system_gnd = Net('GND')

# Connect power distribution to subcircuit module interfaces
power_12v += regulator.vin, motor_drv.vcc
power_3v3 += regulator.vout
system_gnd += regulator.gnd, motor_drv.gnd

# Connect control signals to microcontroller
mcu = Part('MCU_ST_STM32F1', 'STM32F103C8Tx')
mcu['PA0,PA1,PA2,PA3'] += motor_drv.ctrl1, motor_drv.ctrl2, motor_drv.ctrl3, motor_drv.ctrl4

# Connect motor
motor["+"] += motor_drv.motor_a
motor["-"] += motor_drv.motor_b

generate_netlist()