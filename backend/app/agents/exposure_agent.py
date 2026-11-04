"""
HeatShield AI — Worker Exposure Intelligence Agent

Analyses worker-specific occupational exposure factors
using validated worker information.
"""

from app.config import settings

from strands import Agent
from strands.models import BedrockModel

from app.tools.exposure_tool import assess_worker_exposure


AWS_REGION = settings.aws_region
MODEL_ID = settings.bedrock_model_id


# ==================================================
# BEDROCK MODEL
# ==================================================

model = BedrockModel(
    model_id=MODEL_ID,
    region_name=AWS_REGION,
)


# ==================================================
# SYSTEM PROMPT
# ==================================================

SYSTEM_PROMPT = """
You are the Worker Exposure Intelligence Agent for HeatShield AI.

Your responsibility is to understand the occupational
conditions that may influence a worker's heat exposure.

You have access to the assess_worker_exposure tool.

TOOL USAGE:

1. Always use assess_worker_exposure to validate
   supplied worker information.
2. Base your analysis on the validated tool output.
3. Do not independently modify worker profile values.

DATA INTEGRITY RULES:

1. Never invent missing worker information.
2. Clearly identify missing information.
3. continuous_exposure_minutes and
   break_frequency_minutes are two different fields.
4. Never interpret continuous exposure duration
   as break frequency.
5. Never copy a value from one field into another.
6. If break_frequency_minutes is null, report:
   "Break frequency: Not provided."
7. If information is missing, never report:
   "No missing information identified."
8. Preserve the exact values returned by the tool.
9. Distinguish reported information from verified data.

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

SAFETY RULES:

1. Do not diagnose medical conditions.
2. Do not generate arbitrary numerical risk scores.
3. Do not independently declare a worker safe or unsafe.
4. Do not assign occupational heat-risk categories.
5. Do not claim that weather data alone determines
   individual occupational heat exposure.
6. Recommend collecting missing information.
7. If drinking water is unavailable, highlight this
   as a practical safety concern.
8. Do not invent work-rest ratios or break schedules.

OUTPUT FORMAT:

WORKER PROFILE
EXPOSURE FACTORS
MISSING INFORMATION
PRACTICAL SAFETY CONSIDERATIONS
ASSESSMENT LIMITATIONS

Use clear, simple language.

IMPORTANT:

The deterministic HeatShield AI assessment engine
is authoritative for assessment status and missing
information. Your narrative must not contradict
validated worker data or deterministic results.
"""


# ==================================================
# EXPOSURE AGENT
# ==================================================

exposure_agent = Agent(
    model=model,
    tools=[assess_worker_exposure],
    system_prompt=SYSTEM_PROMPT,
    callback_handler=None,
)


# ==================================================
# TEST EXECUTION
# ==================================================

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

    IMPORTANT DATA DISTINCTION:

    Continuous exposure duration is 120 minutes.
    Break frequency is NOT PROVIDED.

    These are separate fields.
    Do not use 120 minutes as the break frequency.

    Use the worker exposure tool.
    Identify exposure factors and missing information.
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
