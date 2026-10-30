from app.tools.exposure_tool import assess_worker_exposure

result = assess_worker_exposure(
    occupation="Construction worker",
    workload="heavy",
    shift_hours=8,
    direct_sunlight=True,
    shade_availability="partial",
    water_access=True,
    acclimatization="not_acclimatized",
    ppe_items=[
        "Safety helmet",
        "Safety boots",
        "Protective clothing",
    ],
    continuous_exposure_minutes=120,
    break_frequency_minutes=None,
    work_area="Outdoor construction site, Vadodara",
)

print("\nHEATSHIELD AI — EXPOSURE TOOL TEST")

print("\nSUCCESS:", result["success"])

print("\nFIELD SUMMARY:")
print(result.get("field_summary"))

print("\nMISSING INFORMATION:")
print(result.get("missing_information"))

print("\nASSESSMENT STATUS:")
print(result.get("assessment_status"))

assert result["success"] is True

assert result["field_summary"]["continuous_exposure_minutes"] == 120

assert result["field_summary"]["break_frequency_minutes"] is None

assert result["field_summary"]["work_area"] == (
    "Outdoor construction site, Vadodara"
)

assert "break_frequency_minutes" in result["missing_information"]

assert "work_area" not in result["missing_information"]

print("\nALL EXPOSURE TOOL TESTS PASSED")
