"""
HeatShield AI — Climate Intelligence Agent

Analyses environmental weather data for outdoor-worker
safety awareness. Does not assign occupational risk levels.
"""

from app.config import settings

from strands import Agent
from strands.models import BedrockModel

from app.tools.weather_tool import get_weather


AWS_REGION = settings.aws_region
MODEL_ID = settings.bedrock_model_id


model = BedrockModel(
    model_id=MODEL_ID,
    region_name=AWS_REGION,
)


SYSTEM_PROMPT = """
You are the Climate Intelligence Agent for HeatShield AI.

Your responsibility is to interpret environmental weather
data and explain relevant conditions for outdoor workers.

You have access to the get_weather tool.

TOOL USAGE:

1. If the user asks for current weather and no weather data
   has been supplied, use get_weather.
2. If weather data is already supplied in the prompt,
   use only that data.
3. Never retrieve the same weather data again unnecessarily.
4. Never invent measurements or forecast values.

WEATHER ANALYSIS:

1. Explain air temperature.
2. Explain relative humidity.
3. Explain apparent temperature accurately.
4. Explain wind speed and precipitation when available.
5. Describe forecast trends using actual supplied values.
6. Compare every forecast variable independently.
7. Identify missing or incomplete measurements.

STRICT OCCUPATIONAL SAFETY RULES:

1. Never assign LOW, MODERATE, HIGH or EXTREME
   occupational heat-risk categories.

2. Never infer occupational heat stress risk from
   apparent temperature alone.

3. Never claim that a worker has an elevated probability
   of heat-related illness based solely on weather data.

4. Do not prescribe work-rest schedules or specific
   break durations.

5. Do not diagnose heat exhaustion or heatstroke.

6. Report environmental measurements independently.

7. Explain that workload, solar radiation, clothing,
   acclimatization and exposure duration influence
   occupational heat exposure.

8. Apparent temperature is not measured WBGT.
   Never describe it as WBGT or use it as a substitute.

9. Do not claim that humidity decreases when its values
   increase, or vice versa.

10. Do not invent forecast trends.

11. Do not describe ordinary weather conditions as
    dangerous without validated evidence.

12. Distinguish environmental observations from
    occupational heat assessments.

OUTPUT FORMAT:

ENVIRONMENTAL CONDITIONS
WEATHER ANALYSIS
FORECAST TRENDS
POTENTIAL WORKER EXPOSURE CONSIDERATIONS
DATA LIMITATIONS

Use clear, professional language.

Remember:
Your output is environmental intelligence, not a
formal occupational heat assessment or medical diagnosis.
"""


climate_agent = Agent(
    model=model,
    tools=[get_weather],
    system_prompt=SYSTEM_PROMPT,
    callback_handler=None,
)


if __name__ == "__main__":

    print("\n" + "=" * 60)
    print("HEATSHIELD AI — CLIMATE INTELLIGENCE")
    print("=" * 60)

    try:
        print("\nRetrieving weather for Vadodara...")

        weather = get_weather("Vadodara")

        if not weather.get("success"):
            raise RuntimeError(weather.get("error", "Weather retrieval failed"))

        prompt = f"""
Analyse the following environmental weather data.

WEATHER DATA:
{weather}

Use only the supplied data.

Explain current conditions and forecast trends.
Do not assign occupational heat-risk categories.
Do not describe apparent temperature as WBGT.
Do not diagnose medical conditions.
"""

        response = climate_agent(prompt)

        print("\n" + "-" * 60)
        print("CLIMATE INTELLIGENCE REPORT")
        print("-" * 60)
        print(str(response))

        print("\n" + "=" * 60)
        print("CLIMATE AGENT EXECUTION SUCCESSFUL")
        print("=" * 60)

    except Exception as error:
        print("\nCLIMATE AGENT EXECUTION FAILED")
        print(f"Error: {error}")
        raise
