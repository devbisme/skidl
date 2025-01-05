from skidl import *
import os

@subcircuit
def rc_filter(inp, outp, gnd):
    """RC low-pass filter"""
    r = Part("Device", 'R', footprint='Resistor_SMD.pretty:R_0805_2012Metric', value='10K')
    c = Part("Device", 'C', footprint='Capacitor_SMD:C_0805_2012Metric', value='0.1uF')
    inp += r[1]
    r[2] += c[1]
    c[2] += gnd
    outp += r[2]

@subcircuit
def input_protection(inp, outp, gnd):
    """Input protection and bulk capacitance"""
    d_protect = Part("Device", 'D',
                    footprint='Diode_SMD:D_SOD-123',
                    value='1N4148W')
    c_bulk = Part("Device", 'C',
                  footprint='Capacitor_THT:CP_Radial_D10.0mm_P5.00mm',
                  value='100uF')
    
    inp += d_protect['A']
    outp += d_protect['K']
    inp += c_bulk[1]
    gnd += c_bulk[2]

@subcircuit
def voltage_regulator(inp, outp, gnd):
    """5V voltage regulator with decoupling caps"""
    reg = Part("Regulator_Linear", "LM7805_TO220",
               footprint="Package_TO_SOT_THT:TO-220-3_Vertical")
    cin = Part("Device", 'C', footprint='Capacitor_SMD:C_0805_2012Metric', value='10uF')
    cout = Part("Device", 'C', footprint='Capacitor_SMD:C_0805_2012Metric', value='10uF')
    inp += cin[1], reg['VI']
    cin[2] += gnd
    reg['GND'] += gnd
    reg['VO'] += cout[1], outp
    cout[2] += gnd

@subcircuit
def voltage_divider(inp, outp, gnd):
    """Basic voltage divider subcircuit"""
    r1 = Part("Device", 'R', footprint='Resistor_SMD.pretty:R_0805_2012Metric', value='1K')
    r2 = Part("Device", 'R', footprint='Resistor_SMD.pretty:R_0805_2012Metric', value='500')
    inp += r1[1]
    r1[2] += r2[1]
    r2[2] += gnd
    outp += r1[2]

@subcircuit
def output_termination(inp, gnd):
    """Output termination resistor"""
    r_term = Part("Device", 'R',
                  footprint='Resistor_SMD.pretty:R_0805_2012Metric',
                  value='100K')
    inp += r_term[1]
    gnd += r_term[2]

@subcircuit
def power_section(raw_in, reg_out, filt_out, gnd):
    """Power section with regulation and filtering"""
    protected_in = Net()
    input_protection(raw_in, protected_in, gnd)
    voltage_regulator(protected_in, reg_out, gnd)
    rc_filter(reg_out, filt_out, gnd)

@subcircuit
def double_divider(inp, outp, gnd):
    """Two voltage dividers in series with termination"""
    mid = Net()
    voltage_divider(inp, mid, gnd)
    voltage_divider(mid, outp, gnd)
    output_termination(outp, gnd)

@subcircuit
def complete_circuit():
    """Top level circuit connecting all subcircuits"""
    vin = Net()
    vreg = Net()
    vfilt = Net()
    vout = Net()
    gnd = Net()

    power_section(vin, vreg, vfilt, gnd)
    double_divider(vfilt, vout, gnd)

# Create the complete circuit
complete_circuit()

# Get circuit info
circuit_description = get_circuit_info()


# Using Anthropic Claude (original behavior)
analyzer = SkidlCircuitAnalyzer(
    provider="anthropic",
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    model="claude-3-sonnet-20240229",
    custom_prompt="Additional specific requirements...",
    analysis_flags={
        "design_review": True,
        "power_analysis": False,  # Disable sections you don't need
        "signal_integrity": True,
        # ... other flags
    }
)

# # Using OpenAI
# analyzer = SkidlCircuitAnalyzer(
#     provider="openai",
#     api_key="your_openai_key",
#     model="gpt-4-turbo-preview"  # optional
# )

# # Using OpenRouter
# analyzer = SkidlCircuitAnalyzer(
#     provider="openrouter",
#     api_key="your_openrouter_key",
#     model="anthropic/claude-3-opus-20240229",  # optional
#     referer="your_domain",  # required for OpenRouter
#     title="Your App Name"   # optional
# )

# Analyze circuit with any provider
results = analyzer.analyze_circuit(circuit_description)
