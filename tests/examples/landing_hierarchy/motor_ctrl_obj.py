from skidl import *

class VoltageRegulator(SubCircuit):
    """3.3V linear voltage regulator module."""
    
    def __init__(self):
        # Initialize this subcircuit. DO NOT USE super().__init__()!
        self.initialize()

        # Create voltage regulator and filter capacitors
        reg = Part('Regulator_Linear', 'AMS1117-3.3')
        c_in = Part('Device', 'C', value='100nF')
        c_out = Part('Device', 'C', value='10uF')
        
        # Define I/O attributes
        self.vin = reg['VI']      # Voltage input
        self.vout = reg['VO']     # Regulated output
        self.gnd = reg['GND']     # Ground connection
        
        # Attach input/output filter capacitors
        self.vin & c_in & self.gnd
        self.vout & c_out & self.gnd

        # Finalize the creation of the subcircuit
        self.finalize()

class MotorDriver(SubCircuit):
    """H-bridge motor driver module."""
    
    def __init__(self):
        # Initialize this subcircuit. DO NOT USE super().__init__()!
        self.initialize()
        
        # Create MOSFETS for H-bridge
        q1, q2, q3, q4 = Part('Transistor_FET', 'Q_NMOS_GSD', dest=TEMPLATE)(4)
        
        # Define I/O attributes
        self.vcc = Net()          # Motor supply voltage
        self.gnd = Net()          # Ground
        self.motor_a = Net()      # Motor terminal A
        self.motor_b = Net()      # Motor terminal B
        self.ctrl1 = q1['G']      # Control signal 1
        self.ctrl2 = q2['G']      # Control signal 2
        self.ctrl3 = q3['G']      # Control signal 3
        self.ctrl4 = q4['G']      # Control signal 4
        
        # Build H-bridge topology
        self.vcc & q1['D,S'] & self.motor_a & q2['D,S'] & self.gnd
        self.vcc & q3['D,S'] & self.motor_b & q4['D,S'] & self.gnd

        # Finalize the creation of the subcircuit
        self.finalize()

# Instantiate subcircuit modules
regulator = VoltageRegulator()
motor_drv = MotorDriver()

# Instantiate a DC motor
motor = Part("Motor", "Motor_DC")

# Create nets for power distribution
power_12v = Net('12V_IN')
power_3v3 = Net('3V3')
system_gnd = Net('GND')

# Connect power distribution to subcircuit modules
power_12v += regulator.vin, motor_drv.vcc
power_3v3 += regulator.vout
system_gnd += regulator.gnd, motor_drv.gnd

# Connect control signals
mcu = Part('MCU_ST_STM32F1', 'STM32F103C8Tx')
mcu['PA0,PA1,PA2,PA3'] += motor_drv.ctrl1, motor_drv.ctrl2, motor_drv.ctrl3, motor_drv.ctrl4

# Connect motor
motor["+"] += motor_drv.motor_a
motor["-"] += motor_drv.motor_b

generate_netlist()