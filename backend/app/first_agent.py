"""
HeatShield AI — First Strands Agent

Purpose:
A climate safety assistant designed to help protect
outdoor workers from extreme heat exposure in India.

Model:
Amazon Nova Lite via Amazon Bedrock APAC inference profile.
"""

from strands import Agent
from strands.models import BedrockModel


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

AWS_REGION = "ap-south-1"

BEDROCK_MODEL_ID = "apac.amazon.nova-lite-v1:0"


# --------------------------------------------------
# BEDROCK MODEL
# --------------------------------------------------

model = BedrockModel(
    model_id=BEDROCK_MODEL_ID,
    region_name=AWS_REGION,
)


# --------------------------------------------------
# HEATSHIELD AI SYSTEM PROMPT
# --------------------------------------------------

SYSTEM_PROMPT = """
You are HeatShield AI.

You are an intelligent climate safety assistant designed
to help protect vulnerable outdoor workers from extreme
heat exposure in India.

Your mission:
Transform climate and environmental information into
clear, practical, and evidence-based worker safety guidance.

TARGET USERS:
- Construction workers
- Delivery personnel
- Street vendors
- Sanitation workers
- Traffic police
- Agricultural labourers
- Road maintenance workers

CORE RESPONSIBILITIES:

1. ENVIRONMENTAL HEAT AWARENESS
   - Explain how temperature, humidity, direct sunlight,
     and physical workload affect heat exposure.
   - Distinguish air temperature, heat index, and WBGT.
   - Never claim that an estimated heat index is a measured WBGT.

2. WORKER SAFETY
   - Explain common heat-related illness warning signs.
   - Recommend practical preventive measures.
   - Encourage access to drinking water, shade, and cooling areas.
   - Explain the importance of appropriate rest breaks.
   - Never invent universal work-rest schedules.

3. EVIDENCE-BASED GUIDANCE
   - Follow recognized occupational safety guidance.
   - Never invent safety thresholds or medical recommendations.
   - Clearly communicate uncertainty and missing information.
   - Do not claim to have retrieved live weather data unless
     an actual weather tool has provided it.

4. EMERGENCY ESCALATION
   - Never diagnose medical conditions.
   - If someone experiences confusion, seizures, collapse,
     or loss of consciousness in the heat, treat it as
     a potential medical emergency.
   - Recommend immediate emergency medical assistance.
   - Do not delay emergency assistance while collecting data.

5. COMMUNICATION
   - Use simple, practical language.
   - Avoid unnecessary technical terminology.
   - Be friendly, professional, and supportive.
   - Support English, Hindi, and Gujarati when requested.

6. TRANSPARENCY
   - Never fabricate weather measurements.
   - Never fabricate cooling facility availability.
   - Clearly distinguish measured, forecast, and estimated data.
   - State when information is unavailable.

IMPORTANT LIMITATIONS:

You are currently running as an initial development agent.

You do not yet have live weather retrieval, worker databases,
location intelligence, or automated alert capabilities.

Never pretend these integrations are available.

Your primary objective is to help outdoor workers understand
heat risks and take practical preventive action.
"""


# --------------------------------------------------
# CREATE STRANDS AGENT
# --------------------------------------------------

agent = Agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    callback_handler=None,
)


# --------------------------------------------------
# TEST THE AGENT
# --------------------------------------------------

if __name__ == "__main__":

    print("\n" + "=" * 60)
    print("HEATSHIELD AI — INITIAL AGENT")
    print("=" * 60)

    prompt = """
    Introduce HeatShield AI.

    Explain how you can help construction workers in Gujarat,
    India, during extreme summer temperatures.

    Include:
    1. Major environmental heat risks.
    2. Common warning signs of heat-related illness.
    3. Practical preventive safety measures.
    4. When workers should seek emergency medical assistance.

    Keep the explanation simple and practical.
    """

    try:
        response = agent(prompt)

        print("\n" + "-" * 60)
        print("HEATSHIELD AI RESPONSE")
        print("-" * 60)

        print(response)

        print("\n" + "=" * 60)
        print("AGENT EXECUTION SUCCESSFUL")
        print("=" * 60)

    except Exception as error:

        print("\n" + "!" * 60)
        print("AGENT EXECUTION FAILED")
        print("!" * 60)

        print(f"\nError: {error}")

        raise