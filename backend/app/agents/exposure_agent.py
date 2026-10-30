"""
HeatShield AI — Worker Exposure Intelligence Agent

Interprets validated worker exposure information.
Does not diagnose illness or calculate occupational risk.
"""

from strands import Agent
from strands.models import BedrockModel

from app.tools.exposure_tool import assess_worker_exposure


AWS_REGION = "ap-south-1"
MODEL_ID = "apac.amazon.nova-lite-v1:0"


model = BedrockModel(
    model_id=MODEL_ID,
    region_name=AWS_REGION,
)


SYSTEM_PROMPT = """
You are the Worker Exposure Intelligence Agent for HeatShield AI.

Your responsibility is to interpret worker-specific
occupational conditions that may influence heat exposure.

You have access to the assess_worker_exposure tool.

TOOL USAGE:

1. If a raw worker profile is supplied, use the tool
   to validate the information.
2. If a validated exposure result is supplied, interpret
   that result without calling the tool again.
3. Use validated tool output as the source of truth.
4. Never independently modify worker profile values.

DATA INTEGRITY RULES:

1. Never invent missing worker information.
2. Clearly identify missing information.
3. continuous_exposure_minutes and
   break_frequency_minutes are separate fields.
4. Never interpret continuous exposure duration
   as break frequency.
5. Never copy a value from one field into another.
6. If break_frequency_minutes is null, report:
   "Break frequency: Not provided."
7. If work_area is present, report the supplied value.
8. If work_area is null, identify it as missing.
9. If water_access is true, report that water access
   is available according to the supplied profile.
10. If water_access is false, identify the lack of
    reported water access as a practical concern.
11. Never report missing information as complete.

EXPOSURE ANALYSIS:

Explain how the following factors may influence
occupational heat exposure:

- Physical workload
- Direct sunlight
- Shade availability
- Drinking water access
- Acclimatization
- Personal protective equipment
- Continuous exposure duration
- Work and recovery-break schedule

STRICT SAFETY AND LANGUAGE RULES:

1. Do not diagnose medical conditions.
2. Do not generate numerical risk scores.
3. Do not assign occupational heat-risk categories.
4. Do not independently declare a worker safe or unsafe.
5. Do not predict an individual's probability of
   developing heat-related illness.
6. Do not say that an individual worker has an elevated
   or high probability of heat-related illness.
7. Describe exposure factors rather than medical outcomes.
8. Use cautious wording such as:
   - "This factor may influence heat exposure."
   - "This condition requires occupational safety review."
   - "Additional measurements are needed."
9. Never invent work-rest ratios or break schedules.
10. Recommend collecting missing information.
11. Distinguish reported information from verified data.

OUTPUT FORMAT:

WORKER PROFILE
EXPOSURE FACTORS
MISSING INFORMATION
PRACTICAL SAFETY CONSIDERATIONS
ASSESSMENT LIMITATIONS

Use clear, professional language.

The deterministic HeatShield AI assessment engine is
authoritative for assessment status and missing information.

Your narrative must not contradict validated worker data
or the deterministic assessment.
"""


exposure_agent = Agent(
    model=model,
    tools=[assess_worker_exposure],
    system_prompt=SYSTEM_PROMPT,
    callback_handler=None,
)


if __name__ == "__main__":

    print("\n" + "=" * 60)
    print("HEATSHIELD AI — WORKER EXPOSURE INTELLIGENCE")
    print("=" * 60)

    prompt = """
    Assess the following example worker profile.

    Occupation: Construction worker
    Workload: Heavy
    Shift duration: 8 hours
    Direct sunlight: Yes
    Shade availability: Partial
    Drinking water access: Yes
    Acclimatization: Not acclimatized

    PPE:
    Safety helmet, safety boots and protective clothing

    Continuous exposure duration: 120 minutes
    Break frequency: Not provided

    Work area:
    Outdoor construction site in Vadodara, Gujarat

    IMPORTANT:

    Continuous exposure is 120 minutes.
    Break frequency is not provided.
    These are separate fields.

    Use the worker exposure tool.
    Do not invent missing information.
    Do not predict medical outcomes.
    Do not generate a numerical heat-risk score.
    """

    try:
        response = exposure_agent(prompt)

        print("\n" + "-" * 60)
        print("WORKER EXPOSURE REPORT")
        print("-" * 60)
        print(str(response))

        print("\n" + "=" * 60)
        print("EXPOSURE AGENT EXECUTION SUCCESSFUL")
        print("=" * 60)

    except Exception as error:
        print("\nEXPOSURE AGENT EXECUTION FAILED")
        print(f"Error: {error}")
        raise
