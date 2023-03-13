import skidl


def my_empty_footprint_handler(part):
    """Function for handling parts with no footprint.

    Args:
        part (Part): Part with no footprint.
    """
    ref_prefix = part.ref_prefix.upper()

    if ref_prefix in ("R", "C", "L") and len(part.pins) == 2:
        # Resistor, capacitors, inductors default to 0805 SMD footprint.
        part.footprint = "Resistor_SMD:R_0805_2012Metric"

    elif ref_prefix in ("Q",) and len(part.pins) == 3:
        # Transistors default to SOT-23 footprint.
        part.footprint = "Package_TO_SOT_SMD:SOT-23"

    else:
        # Everything else goes to the default empty footprint handler.
        skidl.default_empty_footprint_handler(part)


# Replace the default empty footprint handler with your own handler.
skidl.empty_footprint_handler = my_empty_footprint_handler

# Create parts with no footprints.
r = skidl.PartTmplt("Device", "R")
r1, r2 = r(), r()
r2.footprint = "Resistor_SMD:R_1206_3216Metric"

# Generate a netlist. R1 has no footprint so it will be assigned an 0805.
# R2 already has a footprint so it will not change because it is not passed
# to the empty footprint handler.
skidl.generate_netlist()
