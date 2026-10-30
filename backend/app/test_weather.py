from tools.weather_tool import get_weather


if __name__ == "__main__":

    print("\nHEATSHIELD AI — WEATHER TEST")
    print("=" * 50)

    result = get_weather("Vadodara")

    if result["success"]:
        print("\nLOCATION:")
        print(result["location"])

        print("\nCURRENT WEATHER:")
        print(result["current_weather"])

        print("\nNEXT 6 HOURS:")
        for hour in result["hourly_forecast"]:
            print(hour)

        print("\nDATA NOTE:")
        print(result["data_note"])

    else:
        print("\nERROR:", result["error"])
