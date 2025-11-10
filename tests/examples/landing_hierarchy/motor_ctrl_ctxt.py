from skidl import *

# Create nets for power distribution
power_12v = Net('12V_IN')
power_3v3 = Net('3V3')
system_gnd = Net('GND')

with SubCircuit('voltage_regulator') as voltage_regulator:
    """3.3V linear voltage regulator."""

    # Create voltage regulator and filter capacitors
    reg = Part('Regulator_Linear', 'AMS1117-3.3')
    c_in = Part('Device', 'C', value='100nF')
    c_out = Part('Device', 'C', value='10uF')
    
    # Attach power in/out connections and input/output filter capacitors
    power_12v & reg['VI'] & c_in & system_gnd
    power_3v3 & reg['VO'] & c_out & system_gnd

with SubCircuit('motor_driver') as motor_driver:
    """H-bridge motor driver."""
    
    # Create MOSFETs for H-bridge
    q1, q2, q3, q4 = Part('Transistor_FET', 'Q_NMOS_GSD', dest=TEMPLATE)(4)
    
    # Define local nets for connecting motor
    motor_a, motor_b = Net(), Net()  # Motor terminals
    
    # Build H-bridge topology
    power_12v & q1['D,S'] & motor_a & q2['D,S'] & system_gnd
    power_12v & q3['D,S'] & motor_b & q4['D,S'] & system_gnd

    # H-bridge control pins.
    motor_ctrl1=q1['G']
    motor_ctrl2=q2['G']
    motor_ctrl3=q3['G']
    motor_ctrl4=q4['G']

# Instantiate a DC motor
motor = Part("Motor", "Motor_DC")

# Connect control signals to microcontroller
mcu = Part('MCU_ST_STM32F1', 'STM32F103C8Tx')
mcu['PA0,PA1,PA2,PA3'] += motor_ctrl1, motor_ctrl2, motor_ctrl3, motor_ctrl4

# Connect motor
motor["+"] += motor_a
motor["-"] += motor_b

generate_netlist()