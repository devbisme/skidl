from skidl import *

class TerminalBlocks(SubCircuit):
    """terminal connectors"""
    
    def __init__(self, connections=1):
        super().__init__()

        assert connections <= 20

        # a terminal to connect wires
        terminal_power = Part(
            lib="Connector", 
            name=f"Screw_Terminal_01x{connections:02d}", 
            footprint="position_indicator:TerminalBlock_CamdenBoss_CTBP5000_1x02_P5.00mm_90Degree",
            ref_prefix="J"
        )
        
        # You could use a Bus() here, but it's unnecessary overhead for this simple example.
        # contacts = Bus('conn', connections)

        # Just create a pin for each pin of the terminal.
        self.create_pins('conn', connections=terminal_power[1:8])
        
        # create_pins() takes care of all this stuff...
        # interface bus to rest of circuit
        # for n in range(connections):
        #     terminal_power[n+1] += contacts[n]
        #     setattr(self, f"conn{n+1}", contacts[n])
        #     # if this was like a Part(), the above line could be:
        #     # self[f"conn{n}"] = contacts[n]
  
# ---------------------------------------------------------------------
if __name__ == "__main__":
    vcc = Net('VCC')
    gnd = Net('GND')

    # some dummy terminal blocks
    terminals = TerminalBlocks(connections=8)
    # a dummy resistor to GND
    r1 = Part("Device", "R", value="3k")
    r1[1] += gnd

    terminals[1] += vcc
    terminals[2] += gnd
    terminals[3] += r1[2]

    # No-connects don't currently work.
    # terminals[4,5,6,7] += NC
    
    generate_netlist()
