"""Base prompt template for circuit analysis."""

__version__ = "1.0.0"

BASE_METHODOLOGY = """
ANALYSIS METHODOLOGY:
1. Begin analysis immediately with available information
2. After completing analysis, identify any critical missing information needed for deeper insights
3. Begin with subcircuit identification and individual analysis
4. Analyze interactions between subcircuits
5. Evaluate system-level performance and integration
6. Assess manufacturing and practical implementation considerations
"""

SECTION_REQUIREMENTS = """
For each analysis section:
1. Analyze with available information first
2. Start with critical missing information identification
3. Provide detailed technical analysis with calculations
4. Include specific numerical criteria and measurements
5. Reference relevant industry standards
6. Provide concrete recommendations
7. Prioritize findings by severity
8. Include specific action items
"""

ISSUE_FORMAT = """
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
"""

SPECIAL_REQUIREMENTS = """
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
"""

OUTPUT_FORMAT = """
Output Format:
1. Executive Summary
2. Critical Findings Summary
3. Detailed Subcircuit Analysis (one section per subcircuit)
4. System-Level Analysis
5. Cross-Cutting Concerns
6. Recommendations Summary
7. Required Action Items (prioritized)
8. Additional Information Needed
"""

IMPORTANT_INSTRUCTIONS = """
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
"""

def get_base_prompt(circuit_description: str, analysis_sections: str) -> str:
    """
    Generate the complete base analysis prompt.
    
    Args:
        circuit_description: Description of the circuit to analyze
        analysis_sections: String containing enabled analysis sections
        
    Returns:
        Complete formatted base prompt
    """
    return f"""
You are an expert electronics engineer. Analyze the following circuit design immediately and provide actionable insights. Do not acknowledge the request or promise to analyze - proceed directly with your analysis.

Circuit Description:
{circuit_description}

{BASE_METHODOLOGY}

REQUIRED ANALYSIS SECTIONS:
{analysis_sections}

{SECTION_REQUIREMENTS}
{ISSUE_FORMAT}
{SPECIAL_REQUIREMENTS}
{OUTPUT_FORMAT}
{IMPORTANT_INSTRUCTIONS}

After completing your analysis, if additional information would enable deeper insights, list specific questions in a separate section titled 'Additional Information Needed' at the end.
""".strip()