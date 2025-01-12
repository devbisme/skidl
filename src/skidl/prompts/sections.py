"""Analysis section prompt templates."""

from typing import Dict

__version__ = "1.0.0"

SYSTEM_OVERVIEW: str = """
0. System-Level Analysis:
- Comprehensive system architecture review
- Interface analysis between major blocks
- System-level timing and synchronization
- Resource allocation and optimization
- System-level failure modes
- Integration challenges
- Performance bottlenecks
- Scalability assessment
""".strip()

DESIGN_REVIEW: str = """
1. Comprehensive Design Architecture Review:
- Evaluate overall hierarchical structure
- Assess modularity and reusability
- Interface protocols analysis
- Control path verification
- Design pattern evaluation
- Critical path analysis
- Feedback loop stability
- Clock domain analysis
- Reset strategy review
- State machine verification
- Resource utilization assessment
- Design rule compliance
""".strip()

POWER_ANALYSIS: str = """
2. In-depth Power Distribution Analysis:
- Complete power tree mapping
- Voltage drop calculations
- Current distribution analysis
- Power sequencing requirements
- Brownout behavior analysis
- Load transient response
- Power supply rejection ratio
- Efficiency optimization
- Thermal implications
- Battery life calculations (if applicable)
- Power integrity simulation
- Decoupling strategy
- Ground bounce analysis
""".strip()

SIGNAL_INTEGRITY: str = """
3. Detailed Signal Integrity Analysis:
- Critical path timing analysis
- Setup/hold time verification
- Clock skew analysis
- Propagation delay calculations
- Cross-talk assessment
- Reflection analysis
- EMI/EMC considerations
- Signal loading effects
- Impedance matching
- Common mode noise rejection
- Ground loop analysis
- Shield effectiveness
""".strip()

THERMAL_ANALYSIS: str = """
4. Thermal Performance Analysis:
- Component temperature rise calculations
- Thermal resistance analysis
- Heat spreading patterns
- Cooling requirements
- Thermal gradient mapping
- Hot spot identification
- Thermal cycling effects
- Temperature derating
- Thermal protection mechanisms
- Cooling solution optimization
""".strip()

NOISE_ANALYSIS: str = """
5. Comprehensive Noise Analysis:
- Noise source identification
- Noise coupling paths
- Ground noise analysis
- Power supply noise
- Digital switching noise
- RF interference
- Common mode noise
- Differential mode noise
- Shielding effectiveness
- Filter performance
- Noise margin calculations
""".strip()

TESTING_VERIFICATION: str = """
6. Testing and Verification Strategy:
- Functional test coverage
- Performance verification
- Environmental testing
- Reliability testing
- Safety verification
- EMC/EMI testing
- Production test strategy
- Self-test capabilities
- Calibration requirements
- Diagnostic capabilities
- Test point access
- Debug interface requirements
""".strip()

# Dictionary mapping section names to their prompts
ANALYSIS_SECTIONS: Dict[str, str] = {
    "system_overview": SYSTEM_OVERVIEW,
    "design_review": DESIGN_REVIEW,
    "power_analysis": POWER_ANALYSIS,
    "signal_integrity": SIGNAL_INTEGRITY,
    "thermal_analysis": THERMAL_ANALYSIS,
    "noise_analysis": NOISE_ANALYSIS,
    "testing_verification": TESTING_VERIFICATION
}
