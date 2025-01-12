"""Module containing prompt templates for circuit analysis."""

SYSTEM_OVERVIEW_PROMPT = """
0. System-Level Analysis:
- Comprehensive system architecture review
- Interface analysis between major blocks
- System-level timing and synchronization
- Resource allocation and optimization
- System-level failure modes
- Integration challenges
- Performance bottlenecks
- Scalability assessment"""

DESIGN_REVIEW_PROMPT = """
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
- Design rule compliance"""

POWER_ANALYSIS_PROMPT = """
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
- Ground bounce analysis"""

SIGNAL_INTEGRITY_PROMPT = """
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
- Shield effectiveness"""

THERMAL_ANALYSIS_PROMPT = """
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
- Cooling solution optimization"""

NOISE_ANALYSIS_PROMPT = """
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
- Noise margin calculations"""

TESTING_VERIFICATION_PROMPT = """
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
- Debug interface requirements"""

BASE_ANALYSIS_PROMPT = """
You are an expert electronics engineer. Analyze the following circuit design immediately and provide actionable insights. Do not acknowledge the request or promise to analyze - proceed directly with your analysis.

Circuit Description:
{circuit_description}

ANALYSIS METHODOLOGY:
1. Begin analysis immediately with available information
2. After completing analysis, identify any critical missing information needed for deeper insights
3. Begin with subcircuit identification and individual analysis
4. Analyze interactions between subcircuits
5. Evaluate system-level performance and integration
6. Assess manufacturing and practical implementation considerations

REQUIRED ANALYSIS SECTIONS:
{analysis_sections}

For each analysis section:
1. Analyze with available information first
2. Start with critical missing information identification
3. Provide detailed technical analysis with calculations
4. Include specific numerical criteria and measurements
5. Reference relevant industry standards
6. Provide concrete recommendations
7. Prioritize findings by severity
8. Include specific action items

For each identified issue:
SEVERITY: (Critical/High/Medium/Low)
CATEGORY: (Design/Performance/Safety/Manufacturing/etc.)
SUBCIRCUIT: Affected subcircuit or system level
DESCRIPTION: Detailed issue description
IMPACT: Quantified impact on system performance
VERIFICATION: How to verify the issue exists
RECOMMENDATION: Specific action items with justification
STANDARDS: Applicable industry standards
TRADE-OFFS: Impact of proposed changes
PRIORITY: Implementation priority level

Special Requirements:
- Analyze each subcircuit completely before moving to system-level analysis
- Provide specific component recommendations where applicable
- Include calculations and formulas used in analysis
- Reference specific standards and requirements
- Consider worst-case scenarios
- Evaluate corner cases
- Assess impact of component variations
- Consider environmental effects
- Evaluate aging effects
- Assess maintenance requirements

Output Format:
1. Executive Summary
2. Critical Findings Summary
3. Detailed Subcircuit Analysis (one section per subcircuit)
4. System-Level Analysis
5. Cross-Cutting Concerns
6. Recommendations Summary
7. Required Action Items (prioritized)
8. Additional Information Needed

IMPORTANT INSTRUCTIONS:
- Start analysis immediately - do not acknowledge the request or state that you will analyze
- Be specific and quantitative where possible
- Include calculations and methodology
- Reference specific standards
- Provide actionable recommendations
- Consider practical implementation
- Evaluate cost implications
- Assess manufacturing feasibility
- Consider maintenance requirements

After completing your analysis, if additional information would enable deeper insights, list specific questions in a separate section titled 'Additional Information Needed' at the end."""

ANALYSIS_SECTIONS = {
    "system_overview": SYSTEM_OVERVIEW_PROMPT,
    "design_review": DESIGN_REVIEW_PROMPT,
    "power_analysis": POWER_ANALYSIS_PROMPT,
    "signal_integrity": SIGNAL_INTEGRITY_PROMPT,
    "thermal_analysis": THERMAL_ANALYSIS_PROMPT,
    "noise_analysis": NOISE_ANALYSIS_PROMPT,
    "testing_verification": TESTING_VERIFICATION_PROMPT
}