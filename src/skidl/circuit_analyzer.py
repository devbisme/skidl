"""Module for analyzing SKIDL circuits using various LLM providers."""

from typing import Dict, Optional, List
from datetime import datetime
import time
from .llm_providers import get_provider

class SkidlCircuitAnalyzer:
    """Analyzes SKIDL circuits using various LLM providers."""
    
    def __init__(
        self, 
        provider: str = "anthropic",
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        custom_prompt: Optional[str] = None,
        analysis_flags: Optional[Dict[str, bool]] = None,
        **kwargs
    ):
        """
        Initialize the circuit analyzer.
        
        Args:
            provider: LLM provider to use ("anthropic", "openai", or "openrouter")
            api_key: API key for the chosen provider
            model: Specific model to use (provider-dependent)
            custom_prompt: Optional custom prompt to append to the base analysis prompt
            analysis_flags: Dictionary to enable/disable specific analysis sections
            **kwargs: Additional provider-specific configuration
        """
        self.provider = get_provider(provider, api_key)
        self.model = model
        self.custom_prompt = custom_prompt
        self.analysis_flags = analysis_flags or {
            "design_review": True,
            "power_analysis": True,
            "signal_integrity": True,
            "component_analysis": True,
            "reliability_safety": True,
            "manufacturing": True,
            "compliance": True,
            "documentation": True,
            "practical_implementation": True
        }
        self.config = kwargs
        
    def _generate_analysis_prompt(self, circuit_description: str) -> str:
        """Generate structured prompt for circuit analysis."""
        
        # Base prompt sections
        sections = {
            "design_review": """
1. Comprehensive Design Architecture Review:
- Evaluate overall hierarchical structure and design patterns
- Assess modularity, reusability, and maintainability
- Analyze interface definitions and protocols
- Review signal flow and control paths
- Evaluate design scalability
- Identify potential bottlenecks
- CHECK FOR MISSING INFORMATION: Document any undefined pin functions, missing part values, or unclear connections
- DESIGN COMPLETENESS: Verify all necessary subsystems are present for intended functionality""",

            "power_analysis": """
2. In-depth Power Distribution Analysis:
- Map complete power distribution network
- Calculate voltage drops and power dissipation
- Verify power supply requirements and ratings
- MISSING SPECIFICATIONS CHECK: Flag any components missing voltage ratings or power specifications
- Analyze voltage regulation performance:
  * Load/line regulation calculations
  * Transient response characteristics
  * PSRR analysis
  * Thermal considerations
- Protection mechanisms analysis:
  * Overvoltage/undervoltage
  * Overcurrent/short circuit
  * Reverse polarity
  * Inrush current
- Power sequencing requirements
- Efficiency calculations
- EMI/EMC considerations for power distribution""",

            "signal_integrity": """
3. Detailed Signal Integrity Analysis:
- Analyze all critical signal paths:
  * Rise/fall time calculations
  * Propagation delay estimation
  * Loading effects
  * Cross-talk potential
- MISSING SPECIFICATIONS CHECK: Identify signals missing timing requirements or voltage levels
- Evaluate noise susceptibility:
  * Common-mode noise rejection
  * Power supply noise coupling
  * Ground bounce effects
- Calculate signal margins and timing budgets
- Assess impedance matching requirements
- Review termination strategies""",

            "component_analysis": """
4. Extensive Component Analysis:
- CRITICAL MISSING INFORMATION CHECK:
  * Flag missing part numbers
  * Identify components lacking tolerance specifications
  * Note missing temperature ratings
  * Check for undefined footprints
- Detailed component review:
  * Voltage/current ratings
  * Operating temperature range
  * Reliability metrics (MTBF)
  * Cost considerations
  * Availability and lifecycle status
- Alternative component recommendations
- Verify component compatibility:
  * Voltage levels
  * Logic families
  * Load capabilities
- Second-source availability
- End-of-life status check
- Cost optimization opportunities""",

            "reliability_safety": """
5. Comprehensive Reliability and Safety Analysis:
- CRITICAL SAFETY CHECKS:
  * Identify missing safety-related specifications
  * Flag undefined isolation requirements
  * Note missing environmental ratings
- Detailed FMEA (Failure Mode and Effects Analysis)
- Environmental considerations:
  * Temperature range analysis
  * Humidity effects
  * Vibration resistance
  * Protection rating requirements
- Safety compliance review:
  * Isolation requirements
  * Clearance and creepage distances
  * Protection against electrical hazards
  * Thermal safety
- Reliability calculations and predictions
- Risk assessment matrix""",

            "manufacturing": """
6. Manufacturing and Testing Considerations:
- MISSING MANUFACTURING INFORMATION CHECK:
  * Flag undefined assembly requirements
  * Identify missing test specifications
  * Note unclear calibration requirements
- DFM (Design for Manufacturing) analysis:
  * Component placement optimization
  * Assembly process requirements
  * Test point accessibility
  * Programming/debugging access
- Test strategy recommendations:
  * Functional test coverage
  * In-circuit test requirements
  * Boundary scan capabilities
  * Built-in self-test features
- Production cost optimization
- Quality control recommendations
- Yield optimization strategies""",

            "compliance": """
7. Regulatory and Standards Compliance:
- MISSING COMPLIANCE INFORMATION CHECK:
  * Flag undefined safety requirements
  * Identify missing environmental compliance needs
  * Note unclear certification requirements
- Industry standard compliance analysis:
  * Safety standards (UL, CE, etc.)
  * EMC requirements
  * Environmental regulations (RoHS, REACH)
  * Industry-specific standards
- Documentation requirements
- Certification considerations
- Testing requirements for compliance
- Required safety margins""",

            "practical_implementation": """
8. Practical Implementation Review:
- MISSING PRACTICAL INFORMATION CHECK:
  * Flag undefined mounting requirements
  * Identify missing connector specifications
  * Note unclear cooling requirements
- Installation considerations:
  * Mounting requirements
  * Cooling needs
  * Connector accessibility
  * Service access
- Field maintenance requirements:
  * Calibration needs
  * Preventive maintenance
  * Repair accessibility
- Operating environment considerations:
  * Temperature extremes
  * Humidity ranges
  * Dust/water protection
  * Vibration resistance""",

            "documentation": """
9. Documentation and Specifications:
- MISSING DOCUMENTATION CHECK:
  * Flag undefined operating parameters
  * Identify missing interface specifications
  * Note unclear performance requirements
- Required documentation:
  * Design specifications
  * Interface control documents
  * Test procedures
  * User manuals
  * Service documentation
- Design history and decisions
- Change control requirements
- Version control needs"""
        }

        # Build the prompt based on enabled analysis flags
        enabled_sections = []
        for section, content in sections.items():
            if self.analysis_flags.get(section, True):
                enabled_sections.append(content)

        base_prompt = f"""
As an expert electronics engineer, please provide a detailed professional analysis of this circuit design.
Focus on practical implementation considerations, safety requirements, and manufacturing readiness.
Flag any missing critical information that would be needed for professional implementation.

Circuit Description:
{circuit_description}

{'\n'.join(enabled_sections)}

For each section:
- Provide detailed technical analysis with specific calculations where applicable
- Flag any missing critical information needed for professional implementation
- Include specific recommendations with justification
- Prioritize issues found (Critical/High/Medium/Low)
- Include relevant industry standards and best practices
- Provide specific action items to address identified issues

Presentation format for each issue:
SEVERITY: (Critical/High/Medium/Low)
DESCRIPTION: Clear description of the issue
IMPACT: Potential consequences
RECOMMENDATION: Specific action items
STANDARDS: Relevant industry standards or best practices
"""

        # Append custom prompt if provided
        if self.custom_prompt:
            base_prompt += f"\n\nAdditional Analysis Requirements:\n{self.custom_prompt}"

        return base_prompt

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