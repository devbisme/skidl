from random import choice, randint
import numpy as np
import matplotlib.pyplot as plt
from skidl.pyspice import *
import traceback

lib_search_paths[SPICE].append('SpiceLib')

@subcircuit
def vreg(vin, vout, vadj, gnd):
    '''Voltage regulator similar to NCP1117.'''
    v_bandgap = v(dc_value=1.25 @ u_V)  # Bandgap voltage of 1.25V.
    v_o_a = vcvs(gain=1.0)  # Replicate voltage diff (vout - vadj).
    v_o_a['ip, in'] += vout, vadj
    # Generate the difference between the bandgap and v_o_a
    v_bandgap['p,n'] += v_o_a['op'], gnd
    vdiff = v_o_a['on']
    # Generate a current that keeps (vout - vadj) == bandgap.
    i_out = G(gain=1e8 / (1 @ u_Ohm))
    i_out['ip, in'] += vdiff, gnd
    i_out['op, on'] += vout, gnd
    # Output a small current from the adjustment pin.
    i_adj = I(dc_value=50 @ u_uA)
    i_adj['p,n'] += vadj, gnd
    

def create_circuit(connections, resistor_values, num_switches, supply_voltage=20):
    
    global gnd
    
    # Voltage regulator.
    vin, vout, vadj = Net('VIN'), Net('VOUT'), Net('VADJ')
    vreg(vin, vout, vadj, gnd)
    
    # Power supply feeding the voltage regulator. (This is not really
    # needed when using the simplified vreg model above.)
    supply = V(dc_value=supply_voltage @ u_V)
    supply['p', 'n'] += vin, gnd
    
    # Resistors and switches for the voltage feedback.
    resistors = [R(value=resistance @ u_kOhm) for resistance in resistor_values]
    switches = S(dest=TEMPLATE) * num_switches
    
    # Create a list of circuit nodes whose interconnection will be determined by the chromosome.
    nodes = [gnd, vout, vadj]  # Start with ground and voltage regulator output and feedback.
    for r in resistors:
        nodes.extend(r[1,2])  # Add resistor terminals.
    for s in switches:
        nodes.extend(s['op, on'])  # Add switch terminals.
    
    # Create voltage pulse generators to control opening/closing of switches.
    period = 1
    for s in switches:
        open_close = PULSEV(initial_value=0, pulsed_value=1@u_V, pulse_width=0.5*period@u_ms, period=period@u_ms)
        s['ip, in'] += open_close['p, n']
        open_close['n'] += gnd
        period *= 2
        
    def get_node_indices(k):
        '''Return indices of two nodes corresponding to bit k in the connection chromosome.'''
        row = 1
        while True:
            start = (row * (row-1)) // 2
            if start <= k < start+row:
                return row, k-start
            row += 1

    # Connect the nodes as indicated by the bits in the connection chromosome.
    #print('nodes:', [str(n) for n in nodes])
    #print('connections:', connections)
    for k, connection in enumerate(connections):
        if connection:
            i, j = get_node_indices(k)
            print('Connecting nodes', i, j)
            print('Node', i, nodes[i])
            print('Node', j, nodes[j])
            nodes[i] += nodes[j]
            print('Merged Node', i, nodes[i])
            
    
    # Create big-ass resistors to tie every node to ground so nothing is dangling.
    if True:
        bars = R(value=10 @ u_GOhm, dest=TEMPLATE) * len(nodes)
        for node, bar in zip(nodes, bars):
            bar[1,2] += node, gnd

    return generate_netlist(libs='SpiceLib'), nodes, period/2.0

class chromosome(list):
    def __init__(self, *args, **kwargs):
        list.__init__(self, *args, **kwargs)
        
    def _index(self, i, j):
        if i<j:
            i, j = j, i
        assert i!=0
        return ((i-1)*i)//2 + j
    
    def set_(self, i, j):
        self[self._index(i, j)] = 1
        
    def clr_(self, i, j):
        self[self._index(i, j)] = 0
        
    def __str__(self):
        l = len(self)
        s = ''
        indx = 0
        row_idx = 1
        row_len = 1
        while True:
            indx = self._index(row_idx, 0)
            for c in range(row_len):
                s += str(self[indx]) + ' '
                indx += 1
            s += '\n\n'
            row_idx += 1
            row_len += 1
            if indx+1 >= l:
                return s

def generate_random_chromosome(resistor_values, num_switches):
    num_resistors = len(resistor_values)
    num_nodes = 3 + 2*num_resistors + 2*num_switches
    num_connections = (num_nodes * (num_nodes-1)) // 2
    chromosome_ = chromosome([0] * num_connections)
    for i in range(num_resistors):
        rp = 3 + i*2
        rn = rp + 1
        connects = list(range(3, num_nodes))
        connects.remove(rp)
        connects.remove(rn)
        rp_conn = choice(connects)
        connects.remove(rp_conn)
        rn_conn = choice(connects)
        connects.remove(rn_conn)
        chromosome_.set_(rp, rp_conn)
        chromosome_.set_(rn, rn_conn)
    for i in range(num_switches):
        sp = 3 + 2*num_resistors + i*2
        sn = sp + 1
        connects = list(range(3, 3+2*num_resistors))
        sp_conn = choice(connects)
        connects.remove(sp_conn)
        sn_conn = choice(connects)
        connects.remove(sn_conn)
        chromosome_.set_(sp, sp_conn)
        chromosome_.set_(sn, sn_conn)
    connects = list(range(3, num_nodes))
    for i in [0, 1, 2]:
        c = choice(connects)
        connects.remove(c)
        chromosome_.set_(c, i)
    #print(chromosome_)
    return chromosome_

#resistors = [0.5, 1.0]
#num_switches = 1
#num_nodes = 3 + 2*len(resistors) + 2*num_switches
#num_connections = (num_nodes * (num_nodes-1))//2
#connections = [choice([0,1,1,1]) for _ in range(num_connections)]
#connections = [0, 0,0, 0,1,0, 0,0,1,0, 0,0,1,0,1, 1,0,0,0,0,0, 0,0,1,0,1,1,0, 1,0,0,0,0,0,1,0]
#              Vo  Vf,  R1+     R1-       R2+         R2-           R3+              R3-               S1+              S1-                      S2+                     S2-                       
#resistors = [1,1,1]
#num_switches = 2
#num_nodes = 3 + 2*len(resistors) + 2*num_switches
#connections = [0, 0,0, 0,1,0, 0,0,1,0, 0,0,1,0,1, 0,0,0,0,0,0, 0,0,0,0,0,0,1, 1,0,0,0,0,0,0,0, 0,0,1,0,1,1,0,0,0, 0,0,0,0,0,0,1,1,0,0, 0,0,0,0,0,0,1,1,0,0,1, 1,0,0,0,0,0,0,0,1,0,0,0]

#resistors = [1,1,1,1,1,1,1,1]
#num_switches = 8
#num_nodes = 3 + 2*len(resistors) + 2*num_switches
#num_connections = (num_nodes * (num_nodes-1))//2
#connections = generate_random_chromosome(resistors, num_switches)
#connections = [choice([0,0,0,1]) for _ in range(num_connections)]
#obj_func_value = evaluate(connections, resistors, num_switches)
#print(obj_func_value)
#connections = generate_random_chromosome(resistors, num_switches)
#circ, nodes, sim_time = create_circuit(resistors, num_switches, connections)
#sim = circ.simulator()
#waveforms = sim.transient(step_time=0.01@u_ms, end_time=sim_time@u_ms)
#time = waveforms.time                # Time values for each point on the waveforms.
#vout = waveforms[node(nodes[1])]
#print(circ)

# Plot the pulsed source and capacitor voltage values versus time.
#figure = plt.figure(1)
#plt.title('Voltage Regulator Output')
#plt.xlabel('Time (ms)')
#plt.ylabel('Voltage (V)')
#plt.plot(time*1000, vout)
#plt.legend(('Voltage Regulator Output'), loc=(1.1, 0.5))
#plt.show()

def objective_function(generated_voltages, low_voltage, high_voltage, voltage_step):
    try:
        desired_voltages = np.arange(low_voltage, high_voltage+voltage_step, voltage_step)
        obj_value = 0
        for dv in desired_voltages:
            min_diff = float('inf')
            for gv in generated_voltages:
                min_diff = min(min_diff, abs(dv-gv))
            obj_value += min_diff**2
        return obj_value
    except Exception:
        return 1.0e8
        return float('inf')

def evaluate_fitness(connections):
    try:
        reset()
        global gnd, GND
        GND = gnd = Net('0')
        circ, nodes, sim_time = create_circuit(connections, resistor_values, num_switches, supply_voltage)
        print('*'*80, '\n', circ)
        sim = circ.simulator()
        step_time = 0.01 @ u_ms
        waveforms = sim.transient(step_time=step_time, end_time=sim_time@u_ms)
        vout = waveforms[node(nodes[1])]
        vout_levels = set()
        last_v = vout[0]
        stable_cnt = 1
        stable_thresh = (0.5@u_ms / step_time) // 2
        noise = 0.01 @ u_V
        for v in vout[1:]:
            if last_v - noise <= v <= last_v + noise:
                stable_cnt += 1
                if stable_cnt >= stable_thresh:
                    vout_levels.add(round(v.value,2))
            else:
                stable_cnt = 1
                last_v = v
        return (objective_function(vout_levels, 1.2, supply_voltage, 0.1),)
    except Exception as e:
        msg = '\n'.join((str(e), traceback.format.exc()))
        print(msg)
        print('!'*40, 'EXCEPTION', '!'*40)
        return (1.0e8,)
        return (float('inf'),)

from deap import creator, base, tools, algorithms

creator.create('FitnessMin', base.Fitness, weights=(-1.0,))
creator.create('Individual', list, fitness=creator.FitnessMin)

resistor_values = [1,1,1]
num_switches = 3
supply_voltage = 9 @ u_V
num_nodes = 3 + 2 * len(resistor_values) + 2 * num_switches
num_connections = ((num_nodes-1) * num_nodes) // 2

population_size = 3
num_generations = 0

toolbox = base.Toolbox()
toolbox.register('bit', choice, [0,0,0,0,0,0,1])
toolbox.register('individual', tools.initRepeat, creator.Individual, toolbox.bit, n=num_connections)
toolbox.register('population', tools.initRepeat, list, toolbox.individual, n=population_size)
toolbox.register('evaluate', evaluate_fitness)
toolbox.register('mate', tools.cxUniform, indpb=0.1)
toolbox.register('mutate', tools.mutFlipBit, indpb=0.05)
toolbox.register('select', tools.selNSGA2)

population = toolbox.population()
fits = toolbox.map(toolbox.evaluate, population)
for fit, ind in zip(fits, population):
    ind.fitness.values = fit
    
for gen in range(num_generations):
    offspring = algorithms.varOr(population, toolbox, lambda_=population_size, cxpb=0.5, mutpb=0.1)
    fits = toolbox.map(toolbox.evaluate, offspring)
    for fit, ind in zip(fits, offspring):
        ind.fitness.values = fit
    population = toolbox.select(offspring+population, k=population_size)
    print('Generation =', gen, 'Best Fitness =', min([ind.fitness.values for ind in population]))
