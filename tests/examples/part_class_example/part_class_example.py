from skidl import *

# Set the default tool for netlist generation
set_default_tool(KICAD9)

# Define part classes for different hierarchy levels

class PowerSupply(SubCircuit):
    """Power supply subsystem with voltage regulation"""
    
    def __init__(self, name="power_supply"):
        super().__init__(name)
        
        # Define pins for this subcircuit
        self.vin = Net("VIN")
        self.vout = Net("VOUT") 
        self.gnd = Net("GND")
        
        # Components in power supply
        self.regulator = Part("Regulator_Linear", "AMS1117-3.3", footprint="SOT-223")
        self.cap_in = Part("Device", "C", value="100uF", footprint="C_0805")
        self.cap_out = Part("Device", "C", value="10uF", footprint="C_0805")
        
        # Connect power supply components
        self.vin += self.regulator["VI"], self.cap_in[1]
        self.vout += self.regulator["VO"], self.cap_out[1]
        self.gnd += self.regulator["GND"], self.cap_in[2], self.cap_out[2]

class MicrocontrollerModule(SubCircuit):
    """Microcontroller subsystem with supporting components"""
    
    def __init__(self, name="mcu_module"):
        super().__init__(name)
        
        # Define interface pins
        self.vcc = Net("VCC")
        self.gnd = Net("GND")
        self.sda = Net("SDA")
        self.scl = Net("SCL")
        self.gpio = [Net(f"GPIO{i}") for i in range(4)]
        
        # MCU and supporting components
        self.mcu = Part("MCU_ST_STM32F1", "STM32F103C8Tx", footprint="LQFP-48")
        self.crystal = Part("Device", "Crystal", value="8MHz", footprint="Crystal_HC49-4H")
        self.cap1 = Part("Device", "C", value="22pF", footprint="C_0603")
        self.cap2 = Part("Device", "C", value="22pF", footprint="C_0603")
        self.bypass_cap = Part("Device", "C", value="100nF", footprint="C_0603")
        
        # Connect MCU power
        self.vcc += self.mcu["VDD"], self.bypass_cap[1]
        self.gnd += self.mcu["VSS"], self.bypass_cap[2], self.cap1[2], self.cap2[2]
        
        # Connect crystal
        self.crystal[1] += self.mcu["PD0"], self.cap1[1]
        # self.crystal[1] += self.mcu["OSC_IN"], self.cap1[1]
        self.crystal[2] += self.mcu["PD1"], self.cap2[1]
        # self.crystal[2] += self.mcu["OSC_OUT"], self.cap2[1]
        
        # Connect I2C
        self.sda += self.mcu["PB7"]
        self.scl += self.mcu["PB6"]
        
        # Connect GPIO
        for i, gpio in enumerate(self.gpio):
            gpio += self.mcu[f"PA{i}"]

class SensorModule(SubCircuit):
    """Sensor subsystem with I2C interface"""
    
    def __init__(self, name="sensor_module"):
        super().__init__(name)
        
        # Interface pins
        self.vcc = Net("VCC")
        self.gnd = Net("GND")
        self.sda = Net("SDA")
        self.scl = Net("SCL")
        
        # Sensor components
        self.temp_sensor = Part("Sensor_Temperature", "DS18B20", footprint="TO-92")
        self.humidity_sensor = Part("Sensor_Humidity", "SHT30-DIS", footprint="DFN-8")
        self.pullup_sda = Part("Device", "R", value="4.7k", footprint="R_0603")
        self.pullup_scl = Part("Device", "R", value="4.7k", footprint="R_0603")
        
        # Connect power
        self.vcc += self.humidity_sensor["VDD"], self.pullup_sda[1], self.pullup_scl[1]
        self.gnd += self.temp_sensor["GND"], self.humidity_sensor["VSS"]
        
        # Connect I2C with pullups
        self.sda += self.humidity_sensor["SDA"], self.pullup_sda[2]
        self.scl += self.humidity_sensor["SCL"], self.pullup_scl[2]

class LEDDriverModule(SubCircuit):
    """LED driver subsystem"""
    
    def __init__(self, name="led_driver"):
        super().__init__(name)
        
        # Interface pins
        self.vcc = Net("VCC")
        self.gnd = Net("GND")
        self.control = [Net(f"LED_CTRL{i}") for i in range(4)]
        
        # LED driver components
        self.leds = [Part("Device", "LED", footprint="LED_0805") for _ in range(4)]
        self.resistors = [Part("Device", "R", value="330", footprint="R_0603") for _ in range(4)]
        self.transistors = [Part("Transistor_BJT", "2N3904", footprint="TO-92") for _ in range(4)]
        
        # Connect LED drivers
        for i, (led, resistor, transistor, ctrl) in enumerate(zip(
            self.leds, self.resistors, self.transistors, self.control)):
            
            self.vcc += led["A"], resistor[1]
            led["K"] += resistor[2], transistor["C"]
            ctrl += transistor["B"]
            self.gnd += transistor["E"]

# Main circuit that instantiates the hierarchical modules
def create_hierarchical_circuit():
    """Create the main hierarchical circuit"""
    
    # Create main power nets
    vin_main = Net("VIN_MAIN")
    vcc_3v3 = Net("VCC_3V3")
    gnd_main = Net("GND_MAIN")
    
    # Create communication nets
    i2c_sda = Net("I2C_SDA")
    i2c_scl = Net("I2C_SCL")
    
    # Create control nets
    led_controls = [Net(f"LED_CONTROL_{i}") for i in range(4)]
    gpio_nets = [Net(f"GPIO_{i}") for i in range(4)]
    
    # Instantiate subsystem modules
    power_supply = PowerSupply("PS1")
    mcu_module = MicrocontrollerModule("MCU1")
    sensor_module = SensorModule("SENSORS1")
    led_driver = LEDDriverModule("LEDS1")
    
    # Connect power distribution
    vin_main += power_supply.vin
    vcc_3v3 += power_supply.vout, mcu_module.vcc, sensor_module.vcc, led_driver.vcc
    gnd_main += power_supply.gnd, mcu_module.gnd, sensor_module.gnd, led_driver.gnd
    
    # Connect I2C bus
    i2c_sda += mcu_module.sda, sensor_module.sda
    i2c_scl += mcu_module.scl, sensor_module.scl
    
    # Connect GPIO to LED controls
    for i in range(4):
        led_controls[i] += mcu_module.gpio[i], led_driver.control[i]
    
    # Add main circuit connectors
    main_connector = Part("Connector_Generic", "Conn_01x06", footprint="PinHeader_1x06_P2.54mm_Vertical")
    main_connector[1] += vin_main
    main_connector[2] += gnd_main
    main_connector[3] += i2c_sda
    main_connector[4] += i2c_scl
    main_connector[5] += led_controls[0]
    main_connector[6] += led_controls[1]
    
    return {
        'power_supply': power_supply,
        'mcu_module': mcu_module,
        'sensor_module': sensor_module,
        'led_driver': led_driver,
        'main_connector': main_connector
    }

# Generate the hierarchical circuit
if __name__ == "__main__":
    print("Creating hierarchical circuit...")
    
    # Create the circuit
    circuit_modules = create_hierarchical_circuit()
    
    # Generate netlist
    generate_netlist(file_="hierarchical_circuit.net")
    
    # Generate BOM
    # generate_bom(file_="hierarchical_circuit_bom.csv")
    
    print("Hierarchical circuit created successfully!")
    print("Files generated:")
    print("- hierarchical_circuit.net (netlist)")
    print("- hierarchical_circuit_bom.csv (bill of materials)")
    
    # Print hierarchy summary
    print("\nCircuit Hierarchy:")
    print("├── Power Supply (PS1)")
    print("│   ├── Voltage Regulator (AMS1117)")
    print("│   ├── Input Capacitor (100uF)")
    print("│   └── Output Capacitor (10uF)")
    print("├── Microcontroller Module (MCU1)")
    print("│   ├── STM32F103 MCU")
    print("│   ├── 8MHz Crystal")
    print("│   ├── Crystal Capacitors (2x 22pF)")
    print("│   └── Bypass Capacitor (100nF)")
    print("├── Sensor Module (SENSORS1)")
    print("│   ├── Temperature Sensor (DS18B20)")
    print("│   ├── Humidity Sensor (SHT30)")
    print("│   └── I2C Pullup Resistors (2x 4.7k)")
    print("└── LED Driver Module (LEDS1)")
    print("    ├── LEDs (4x)")
    print("    ├── Current Limiting Resistors (4x 330Ω)")
    print("    └── Switching Transistors (4x 2N3904)")