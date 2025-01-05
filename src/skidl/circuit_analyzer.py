from typing import Dict, Optional, List
from datetime import datetime
import time
from .llm_providers import get_provider

class SkidlCircuitAnalyzer:
    def __init__(
        self,
        provider: str = "anthropic",
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        custom_prompt: Optional[str] = None,
        analysis_flags: Optional[Dict[str, bool]] = None,
        **kwargs
    ):
        """Initialize with same parameters as original"""
        self.provider = get_provider(provider, api_key)
        self.model = model
        self.custom_prompt = custom_prompt
        self.analysis_flags = analysis_flags or {
            "system_overview": True,
            "subcircuit_analysis": True,
            "design_review": True,
            "power_analysis": True,
            "signal_integrity": True,
            "component_analysis": True,
            "reliability_safety": True,
            "manufacturing": True,
            "compliance": True,
            "documentation": True,
            "practical_implementation": True,
            "thermal_analysis": True,
            "noise_analysis": True,
            "testing_verification": True
        }
        self.config = kwargs

    def _generate_system_requirements_prompt(self) -> str:
        """Generate prompt section for system requirements"""
        return """
REQUIRED SYSTEM INFORMATION:
Please provide the following critical information for accurate analysis:

1. System Overview:
- Primary function and purpose of the circuit
- Target application domain
- Required performance specifications
- Operating environment details

2. Electrical Specifications:
- Input voltage specifications (range, ripple, regulation)
- Output requirements (voltage, current, regulation)
- Power budget and efficiency targets
- Signal specifications (levels, timing, protocols)

3. Environmental Requirements:
- Operating temperature range
- Humidity requirements
- Vibration/shock specifications
- IP rating requirements

4. Regulatory Requirements:
- Required certifications (UL, CE, etc.)
- EMC/EMI requirements
- Safety standards
- Industry-specific regulations

5. Manufacturing/Cost Targets:
- Production volume estimates
- Target BOM cost
- Assembly requirements
- Testing requirements

Please provide as much of this information as possible to enable comprehensive analysis."""

    def _generate_subcircuit_analysis_prompt(self) -> str:
        """Generate prompt for subcircuit analysis"""
        return """
SUBCIRCUIT ANALYSIS REQUIREMENTS:

For each identified subcircuit, provide detailed analysis covering:

1. Functional Analysis:
- Primary purpose and operation
- Input/output specifications
- Critical parameters and constraints
- Performance requirements
- Integration with other subcircuits

2. Component-Level Review:
- Critical component specifications
- Operating point analysis
- Tolerance analysis
- Worst-case scenario analysis
- Component interaction effects

3. Performance Analysis:
- Transfer function analysis
- Frequency response
- Stability analysis
- Temperature effects
- Power consumption

4. Failure Mode Analysis:
- Single point failure analysis
- Cascade failure potential
- Protection mechanisms
- Recovery mechanisms
- Reliability projections

5. Implementation Considerations:
- Layout requirements
- Thermal considerations
- EMI/EMC requirements
- Test point access
- Debug capabilities

Analyze each subcircuit individually before assessing system-level interactions."""

    def _generate_analysis_sections(self) -> Dict[str, str]:
        """Generate all analysis section prompts"""
        return {
            "system_overview": """
0. System-Level Analysis:
- Comprehensive system architecture review
- Interface analysis between major blocks
- System-level timing and synchronization
- Resource allocation and optimization
- System-level failure modes
- Integration challenges
- Performance bottlenecks
- Scalability assessment""",

            "design_review": """
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
- Design rule compliance""",

            "power_analysis": """
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
- Ground bounce analysis""",

            "signal_integrity": """
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
- Shield effectiveness""",

            "thermal_analysis": """
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
- Cooling solution optimization""",

            "noise_analysis": """
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
- Noise margin calculations""",

            "testing_verification": """
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
        }

    def _generate_analysis_prompt(self, circuit_description: str) -> str:
        """Generate enhanced structured prompt for circuit analysis"""
        
        # Get all section prompts
        sections = self._generate_analysis_sections()
        
        # Build base prompt
        base_prompt = f"""
You are an expert electronics engineer conducting a thorough professional analysis of a circuit design.
Your goal is to provide actionable insights and identify potential issues before implementation.

{self._generate_system_requirements_prompt()}

Circuit Description:
{circuit_description}

{self._generate_subcircuit_analysis_prompt()}

ANALYSIS METHODOLOGY:
1. Begin with subcircuit identification and individual analysis
2. Analyze interactions between subcircuits
3. Evaluate system-level performance and integration
4. Assess manufacturing and practical implementation considerations

REQUIRED ANALYSIS SECTIONS:"""

        # Add enabled analysis sections
        for section, content in sections.items():
            if self.analysis_flags.get(section, True):
                base_prompt += f"\n{content}"

        # Add analysis requirements
        base_prompt += """

For each analysis section:
1. Start with critical missing information identification
2. Provide detailed technical analysis with calculations
3. Include specific numerical criteria and measurements
4. Reference relevant industry standards
5. Provide concrete recommendations
6. Prioritize findings by severity
7. Include specific action items

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

Remember to:
- Be specific and quantitative where possible
- Include calculations and methodology
- Reference specific standards
- Provide actionable recommendations
- Consider practical implementation
- Evaluate cost implications
- Assess manufacturing feasibility
- Consider maintenance requirements"""

        # Append custom prompt if provided
        if self.custom_prompt:
            base_prompt += f"\n\nAdditional Analysis Requirements:\n{self.custom_prompt}"

        return base_prompt

    # Rest of the class implementation remains the same...
    def analyze_circuit(
        self, 
        circuit_description: str,
        output_file: Optional[str] = "circuit_llm_analysis.txt",
        verbose: bool = True
    ) -> Dict:
        """
        Perform LLM analysis of the circuit.
        
        Args:
            circuit_description: Description of the circuit to analyze
            output_file: File to save the analysis results (None to skip saving)
            verbose: Whether to print progress messages
        
        Returns:
            Dictionary containing analysis results and metadata
        """
        start_time = time.time()
        
        if verbose:
            print("\n=== Starting Circuit Analysis with LLM ===")
            print(f"Using provider: {self.provider.__class__.__name__}")
        
        try:
            # Generate and validate prompt
            if verbose:
                print("\nGenerating analysis prompt...")
            prompt = self._generate_analysis_prompt(circuit_description)
            prompt_tokens = len(prompt.split())
            
            if verbose:
                print(f"Prompt generated ({prompt_tokens} estimated tokens)")
                print("\nPrompt preview (first 200 chars):")
                print(f"{prompt[:200]}...")
                print("\nSending request to LLM...")
            
            # Configure for maximum response length
            self.config['max_tokens'] = self.config.get('max_tokens', 4000)
            
            # Generate analysis
            request_start = time.time()
            analysis_result = self.provider.generate_analysis(
                prompt,
                model=self.model,
                **self.config
            )
            
            request_time = time.time() - request_start
            
            if not analysis_result["success"]:
                raise Exception(analysis_result["error"])
            
            # Add metadata to results
            analysis_text = analysis_result["analysis"]
            analysis_tokens = len(analysis_text.split())
            
            results = {
                **analysis_result,
                "timestamp": int(datetime.now().timestamp()),
                "request_time_seconds": request_time,
                "prompt_tokens": prompt_tokens,
                "response_tokens": analysis_tokens,
                "total_time_seconds": time.time() - start_time,
                "enabled_analyses": [k for k, v in self.analysis_flags.items() if v]
            }
            
            if verbose:
                print(f"\nResponse received in {request_time:.2f} seconds")
                print(f"Response length: {len(analysis_text)} characters")
                print(f"Estimated response tokens: {analysis_tokens}")
            
            # Save results if requested
            if output_file:
                if verbose:
                    print(f"\nSaving analysis to {output_file}...")
                with open(output_file, "w") as f:
                    f.write(analysis_text)
                if verbose:
                    print("Analysis saved successfully")
            
            if verbose:
                print(f"\n=== Analysis completed in {results['total_time_seconds']:.2f} seconds ===")
            
            return results
            
        except Exception as e:
            error_results = {
                "success": False,
                "error": str(e),
                "timestamp": int(datetime.now().timestamp()),
                "total_time_seconds": time.time() - start_time
            }
            
            if verbose:
                print(f"\nERROR: Analysis failed: {str(e)}")
            
            if output_file:
                if verbose:
                    print(f"\nSaving error message to {output_file}...")
                with open(output_file, "w") as f:
                    f.write(f"Analysis failed: {error_results['error']}")
                if verbose:
                    print("Error message saved")
            
            if verbose:
                print("\n=== Analysis failed ===")
            
            return error_results