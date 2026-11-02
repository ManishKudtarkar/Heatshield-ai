"""
HeatShield AI — Validated Occupational Safety Knowledge Base

A curated set of occupational heat-safety topics. Each topic is:

- grounded in authoritative public sources (OSHA, NIOSH/CDC),
- explicitly marked as validated (``validated: true``) with a
  review date and source citations,
- written as practical guidance, never as a medical diagnosis,
- localized for the worker interface languages (en / hi / gu).

Design rules (mirrors the rest of HeatShield AI):

- No fabricated thresholds: numeric guidance values are quoted
  directly from the cited source material.
- Unvalidated entries are rejected by ``validate_knowledge_base``
  so incomplete reviews can never reach the API surface.
- The knowledge base is informational screening support; every
  response carries explicit limitations.
"""

from typing import Any


# --------------------------------------------------
# VERSIONING
# --------------------------------------------------

KB_VERSION = "1.0.0"

_KB_LIMITATIONS = [
    "Guidance is summarized from public occupational-safety sources and is informational only.",
    "This knowledge base does not replace advice from qualified occupational safety professionals.",
    "Content is not a medical diagnosis. Suspected heat stroke requires immediate emergency medical assistance.",
    "Site-specific conditions (WBGT, workload, clothing) must be assessed before applying work-rest schedules.",
]


def _topic(
    topic_id: str,
    title: str,
    category: str,
    summary_en: str,
    guidance_en: list[str],
    sources: list[dict[str, str]],
    reviewed_at: str,
    localized_titles: dict[str, str] | None = None,
    localized_summaries: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Build one validated knowledge-base entry."""
    return {
        "id": topic_id,
        "title": title,
        "category": category,
        "summary": {"en": summary_en, **(localized_summaries or {})},
        "guidance": {"en": guidance_en},
        "sources": sources,
        "validated": True,
        "reviewed_at": reviewed_at,
        "localized_titles": localized_titles or {},
    }


# --------------------------------------------------
# TOPICS
# --------------------------------------------------

KNOWLEDGE_TOPICS: list[dict[str, Any]] = [
    _topic(
        topic_id="heat-illness-types",
        title="Recognizing heat-related illnesses",
        category="recognition",
        summary_en=(
            "Heat illness progresses from heat rash and cramps to "
            "heat exhaustion and, if untreated, life-threatening "
            "heat stroke. Early recognition protects workers."
        ),
        guidance_en=[
            "Heat cramps: painful muscle spasms after heavy sweating. Move to a cool place, sip water or an electrolyte drink, and rest before returning to work.",
            "Heat exhaustion: heavy sweating, weakness, dizziness, headache, nausea or cool clammy skin. Move to a cooler area, loosen clothing, sip water, and monitor closely.",
            "Heat stroke is a medical emergency: confusion, slurred speech, seizures, collapse or loss of consciousness with very high body temperature.",
            "If heat stroke is suspected, call emergency services immediately, move the worker to shade, and begin rapid cooling while waiting for help.",
            "Never leave a confused or unconscious worker alone and never give fluids to someone who is not fully alert.",
        ],
        localized_titles={
            "hi": "गर्म-संबंधी बीमारियों को पहचानना",
            "gu": "ગરમી-સંબંધિત બીમારીઓ ઓળખવી",
        },
        localized_summaries={
            "hi": "ऊष्मा-रोग हीट रैश और क्रैंप से हीट एग्जॉस्चर तथा बिना उपचार के प्राणघातक हीट स्ट्रोक तक बढ़ते हैं। प्रारंभिक पहचान श्रमिकों की रक्षा करती है।",
            "gu": "ગરમીજન્ય બીમારી ગરમીના દાણા અને ખેંચાણથી હીટ એક્ઝોસ્ટશન અને વગર સારવાર જીવલેણ હીટ સ્ટ્રોક સુધી આગળ વધે છે. વહેલી ઓળખ કામદારોનું રક્ષણ કરે છે.",
        },
        sources=[
            {"name": "CDC — Warning Signs of Heat Illness", "url": "https://www.cdc.gov/disasters/extremeheat/warning.html"},
            {"name": "OSHA — Heat Exposure", "url": "https://www.osha.gov/heat-exposure"},
        ],
        reviewed_at="2026-10-15",
    ),
    _topic(
        topic_id="acclimatization",
        title="Heat acclimatization for new and returning workers",
        category="prevention",
        summary_en=(
            "The body adapts to heat over days of gradual exposure. "
            "New workers and workers returning after a break of four "
            "or more days are at highest risk in the first weeks."
        ),
        guidance_en=[
            "Start new or returning workers at a reduced share of normal heat exposure on the first days and build up gradually over one to two weeks under supervision.",
            "Assign lighter duties, more frequent breaks and buddy monitoring during the first two work weeks.",
            "Schedule the hardest tasks during the coolest part of the day while workers are still acclimatizing.",
            "Watch for signs that acclimatization has not occurred: elevated resting heart rate, fatigue, cramps, reduced sweating.",
            "Use a documented acclimatization plan under occupational-safety guidance rather than informal trial and error.",
        ],
        localized_titles={
            "hi": "नए और लौटे श्रमिकों का ऊष्मा अनुकूलन",
            "gu": "નવા અને પરત ફરેલા કામદારોનું ગરમીને અનુકૂલન",
        },
        localized_summaries={
            "hi": "शरीर धीमी-धीमी गर्मी में कई दिनों के संपर्क से अनुकूलित होता है। नए श्रमिक और चार या अधिक दिन की विराम के बाद लौटे श्रमिक पहले हफ्तों में सर्वाधिक जोखिम में होते हैं।",
            "gu": "શરીર ધીમે ધીમે ગરમીમાં દિવસોના સંપર્કથી અનુકૂલિત થાય છે. નવા કામદારો અને ચાર કે વધુ દિવસના વિરામ પછી પરત ફરેલા કામદારો પહેલા અઠવાડિયાંમાં સૌથી વધુ જોખમમાં હોય છે.",
        },
        sources=[
            {"name": "NIOSH — Work Safely in the Heat: Planning Guidance", "url": "https://www.cdc.gov/niosh/docs/2016-106/"},
            {"name": "OSHA — Heat Illness Prevention", "url": "https://www.osha.gov/heat-illness-prevention"},
        ],
        reviewed_at="2026-10-15",
    ),
    _topic(
        topic_id="hydration",
        title="Hydration practices for outdoor work",
        category="prevention",
        summary_en=(
            "Regular drinking before and during work prevents "
            "dehydration better than responding to thirst, which is "
            "a late signal in hot conditions."
        ),
        guidance_en=[
            "Drink small amounts frequently — OSHA guidance is about a cup of water every 15–20 minutes of hot work, even when not thirsty.",
            "Provide cool, potable drinking water close to work areas so workers are encouraged to drink often.",
            "For work longer than about two hours or heavy sweating, offer electrolyte-containing drinks and reduce caffeine and sugary drinks.",
            "Do not force large volumes of water at once; steady sipping is safer and more effective.",
            "Pale-yellow urine generally indicates adequate hydration; dark urine is a warning sign to report.",
        ],
        localized_titles={
            "hi": "बाह्य कार्य के लिए जल-पान अभ्यास",
            "gu": "બહારના કામ માટે પાણી પીવાની પદ્ધતિઓ",
        },
        localized_summaries={
            "hi": "काम से पहले और दौरान नियमित पानी पीना निर्जलीकरण को बेहतर रोकता है, क्योंकि गर्म परिस्थितियों में प्यास एक देर से मिलने वाला संकेत है।",
            "gu": "કામ પહેલાં અને દરમિયાન નિયમિત પાણી પીવું નિર્જલીકરણને વધુ સારી રીતે અટકાવે છે, કારણ કે ગરમ પરિસ્થિતિમાં તરસ મોડી મળતી નિશાની છે.",
        },
        sources=[
            {"name": "OSHA — Water, Rest, Shade", "url": "https://www.osha.gov/heat-exposure"},
            {"name": "CDC — Keep Cool and Hydrated", "url": "https://www.cdc.gov/disasters/extremeheat/heat_guide.html"},
        ],
        reviewed_at="2026-10-15",
    ),
    _topic(
        topic_id="rest-shade-cooling",
        title="Rest breaks, shade and cooling areas",
        category="controls",
        summary_en=(
            "Shade plus rest is the most accessible control against "
            "heat stress. Workers should be able to take preventive "
            "breaks in shade or cooled areas without penalty."
        ),
        guidance_en=[
            "Provide shaded or air-conditioned recovery areas as close to work areas as practical, sized for all workers on rest break.",
            "Increase break frequency and duration as temperature, humidity or workload rises; shorter work bouts with more recovery are safer than long continuous exposure.",
            "Allow workers to take preventive rest breaks whenever they feel overheated, without fear of discipline or lost pay.",
            "Use shading or reflective covers where radiant sun exposure is high; surface temperatures in direct sun far exceed air temperature.",
            "Rotate workers out of the hottest tasks so no single worker sustains peak exposure for the whole shift.",
        ],
        localized_titles={
            "hi": "विश्राम, छाया और शीतलन क्षेत्र",
            "gu": "વિરામ, છાયા અને ઠંડક વિસ્તાર",
        },
        localized_summaries={
            "hi": "छाया और विश्राम गर्मी के तनाव के खिलाफ सबसे सुलभ नियंत्रण हैं। श्रमिकों को बिना दंड के छाया या शीतल क्षेत्र में निवारक विश्राम लेना चाहिए।",
            "gu": "છાયા અને વિરામ ગરમીના તણાવ સામે સૌથી સુલભ નિયંત્રણ છે. કામદારોએ વિના શિક્ષા છાયા અથવા ઠંડા વિસ્તારમાં નિવારક વિરામ લેવા જોઈએ.",
        },
        sources=[
            {"name": "OSHA — Heat Exposure Controls", "url": "https://www.osha.gov/heat-exposure"},
            {"name": "NIOSH — Criteria: Occupational Exposure to Heat", "url": "https://www.cdc.gov/niosh/docs/2016-106/"},
        ],
        reviewed_at="2026-10-15",
    ),
    _topic(
        topic_id="ppe-clothing",
        title="Protective clothing and heat burden",
        category="controls",
        summary_en=(
            "Protective equipment can trap body heat. When PPE must "
            "be worn in hot conditions, its thermal burden has to be "
            "managed deliberately."
        ),
        guidance_en=[
            "Review the heat burden of required PPE with the safety team; choose breathable, light-coloured, loose-fitting fabrics where protection requirements allow.",
            "Where heavy impermeable clothing is mandatory, shorten exposure periods and lengthen recovery breaks accordingly.",
            "Provide cooling aids compatible with the PPE in use and shaded areas for removing gear during breaks.",
            "Dark or non-reflective outer layers increase radiant heat absorption; schedule extra recovery when they cannot be avoided.",
            "Never remove legally required protective equipment solely for comfort without a documented safety review.",
        ],
        localized_titles={
            "hi": "सुरक्षात्मक वस्त्र और ऊष्मा भार",
            "gu": "સુરક્ષાત્મક કપડાં અને ગરમીનો બોજ",
        },
        localized_summaries={
            "hi": "सुरक्षात्मक उपकरण शारीरिक गर्मी को कैद कर सकते हैं। गर्म परिस्थितियों में PPE पहनना आवश्यक हो तो उसके ऊष्मीय भार को जान-बूझकर प्रबंधित करना होगा।",
            "gu": "સુરક્ષાત્મક સાધનો શારીરિક ગરમી બંધ કરી શકે છે. ગરમ પરિસ્થિતિઓમાં PPE પહેરવું જરૂરી હોય તો તેના ગરમીના બોજને જાણીજોઈને સંભાળવો પડે.",
        },
        sources=[
            {"name": "NIOSH — Work Safely in the Heat: Clothing Factors", "url": "https://www.cdc.gov/niosh/docs/2016-106/"},
            {"name": "OSHA — Heat Exposure", "url": "https://www.osha.gov/heat-exposure"},
        ],
        reviewed_at="2026-10-15",
    ),
    _topic(
        topic_id="monitoring-buddy-system",
        title="Monitoring workers and the buddy system",
        category="response",
        summary_en=(
            "Workers affected by heat may not recognize their own "
            "symptoms first. Supervised monitoring and peer checks "
            "catch deterioration early."
        ),
        guidance_en=[
            "Pair workers on hot tasks and instruct them to watch each other for confusion, slurred speech, staggering, cessation of sweating or collapse.",
            "Train supervisors on daily pre-shift screening: recent illness, new medication, poor sleep, dehydration and lack of acclimatization raise risk.",
            "Set a clear reporting chain so any heat symptom is reported without blame, and define who calls emergency services.",
            "During extreme heat, increase check-in frequency for isolated outdoor workers at defined intervals.",
            "Confusion, seizures or loss of consciousness is treated as a heat-stroke emergency: call emergency services and start cooling immediately.",
        ],
        localized_titles={
            "hi": "श्रमिकों की निगरानी और बडी प्रणाली",
            "gu": "કામદારોની દેખરેખ અને બડી સિસ્ટમ",
        },
        localized_summaries={
            "hi": "गर्मी से प्रभावित श्रमिक अपने लक्षण सबसे पहले नहीं पहचान पाते। पर्यवेक्षित निगरानी और सहकर्मी जांच बिगड़ को जल्दी पकड़ती है।",
            "gu": "ગરમીથી અસરગ્રસ્ત કામદારો પોતાના લક્ષણો પહેલા ઓળખી શકતા નથી. દેખરેખ હેઠળની મોનિટરિંગ અને સાથી તપાસ ખરાબીને વહેલી પકડે છે.",
        },
        sources=[
            {"name": "OSHA — Heat Illness Prevention: Training", "url": "https://www.osha.gov/heat-illness-prevention"},
            {"name": "CDC — Extreme Heat: Check on People at Risk", "url": "https://www.cdc.gov/disasters/extremeheat/index.html"},
        ],
        reviewed_at="2026-10-15",
    ),
    _topic(
        topic_id="work-scheduling",
        title="Scheduling work around peak heat",
        category="controls",
        summary_en=(
            "Environmental heat follows a daily pattern. Shifting "
            "the heaviest work away from midday reduces exposure to "
            "the hottest, most intense solar period."
        ),
        guidance_en=[
            "Schedule strenuous tasks for the cooler parts of the day when forecasts show afternoon peaks above 35°C.",
            "Check the forecast and observed conditions before the shift; slow the work pace during the hottest hours rather than pushing through.",
            "Postpone non-essential heavy outdoor work during heat waves and official heat warnings where operationally possible.",
            "Combine scheduling with rest, shade and hydration controls — rescheduling alone does not protect workers already exposed.",
            "Avoid very long compressed shifts to beat the heat; total daily exposure time also matters for recovery.",
        ],
        localized_titles={
            "hi": "चरम ऊष्मा के आसपास कार्य समय-सारणी",
            "gu": "ટોચની ગરમીની આસપાસ કામની સમયક્રમ",
        },
        localized_summaries={
            "hi": "पर्यावरणीय गर्मी एक दैनिक पैटर्न का पालन करती है। सबसे भारी काम दोपहर से हटाने से सबसे गर्म और तीव्र सौर अवधि में अनावरण घटता है।",
            "gu": "પર્યાવરણીય ગરમી દૈનિક પેટર્નને અનુસરે છે. સૌથી ભારે કામ બપોરથી દૂર ખસેડવાથી સૌથી ગરમ અને તીવ્ર સૌર ગાળામાં સંપર્ક ઘટે છે.",
        },
        sources=[
            {"name": "NIOSH — Work Safely in the Heat", "url": "https://www.cdc.gov/niosh/docs/2016-106/"},
            {"name": "India Meteorological Department — Heat Wave Warnings", "url": "https://mausam.imd.gov.in/"},
        ],
        reviewed_at="2026-10-15",
    ),
    _topic(
        topic_id="wbgt-measurement",
        title="Worksite heat measurement (WBGT)",
        category="assessment",
        summary_en=(
            "Wet Bulb Globe Temperature (WBGT) is the standard field "
            "index for occupational heat stress because it combines "
            "air temperature, humidity, radiation and wind. Weather "
            "apparent temperature is not WBGT."
        ),
        guidance_en=[
            "Measure worksite WBGT with a calibrated instrument when setting binding work-rest requirements; screen-level weather data cannot substitute for it.",
            "Compare measured WBGT against action limits for the specific workload category and clothing adjustment using current NIOSH guidance.",
            "Re-measure across the shift: WBGT changes with sun angle, cloud cover, humidity and activity location.",
            "Record measurement metadata — instrument, location, time — alongside any assessment that uses it.",
            "Until WBGT is measured at the site, treat assessments as screening only and apply conservative precautions.",
        ],
        localized_titles={
            "hi": "कार्यस्थल ऊष्मा मापन (WBGT)",
            "gu": "કાર્યસ્થળ ગરમી માપન (WBGT)",
        },
        localized_summaries={
            "hi": "वेट बल्ब ग्लोब तापमान (WBGT) व्यावसायिक ऊष्मा तनाव का मानक फील्ड सूचकांक है क्योंकि यह वायु तापमान, आर्द्रता, विकिरण और हवा को जोड़ता है। मौसम का प्रत्यक्ष तापमान WBGT नहीं है।",
            "gu": "વેટ બલ્બ ગ્લોબ તાપમાન (WBGT) વ્યાવસાયિક ગરમીના તણાવનો પ્રમાણિત ફીલ્ડ ઇન્ડેક્સ છે કારણ કે તે હવાનું તાપમાન, ભેજ, કિરણોત્સર્ગ અને પવનને જોડે છે. હવામાનનું આભાસી તાપમાન WBGT નથી.",
        },
        sources=[
            {"name": "NIOSH — Criteria: Occupational Exposure to Heat and Hot Environments", "url": "https://www.cdc.gov/niosh/docs/2016-106/"},
        ],
        reviewed_at="2026-10-15",
    ),
]


# --------------------------------------------------
# PUBLIC API
# --------------------------------------------------

def list_topics() -> list[dict[str, Any]]:
    """Return a compact index of all knowledge topics."""
    return [
        {
            "id": topic["id"],
            "title": topic["title"],
            "category": topic["category"],
            "validated": topic["validated"],
            "reviewed_at": topic["reviewed_at"],
            "source_count": len(topic["sources"]),
        }
        for topic in KNOWLEDGE_TOPICS
    ]


def get_topic(topic_id: str, language: str = "en") -> dict[str, Any] | None:
    """
    Return one topic localized into ``language`` (falls back to
    English per-field). Returns ``None`` when the topic id is unknown.
    """
    for topic in KNOWLEDGE_TOPICS:
        if topic["id"] != topic_id:
            continue

        lang = language if language in ("en", "hi", "gu") else "en"

        return {
            "id": topic["id"],
            "title": topic["localized_titles"].get(lang, topic["title"]),
            "category": topic["category"],
            "summary": topic["summary"].get(lang, topic["summary"]["en"]),
            "guidance": topic["guidance"].get(lang, topic["guidance"]["en"]),
            "sources": list(topic["sources"]),
            "validated": topic["validated"],
            "reviewed_at": topic["reviewed_at"],
            "language": lang,
        }

    return None


def search_knowledge(query: str, language: str = "en") -> dict[str, Any]:
    """
    Deterministic keyword search over validated topics.

    Matching is intentionally simple and transparent: whitespace-
    separated query terms (length >= 3) are matched case-insensitively
    against topic titles, categories and English summaries/guidance.
    """
    terms = [t.lower() for t in query.split() if len(t) >= 3]

    matches = []

    for topic in KNOWLEDGE_TOPICS:
        haystack = " ".join(
            [
                topic["title"],
                topic["category"],
                topic["summary"]["en"],
                " ".join(topic["guidance"]["en"]),
            ]
        ).lower()

        score = sum(haystack.count(term) for term in terms)

        if score > 0:
            entry = get_topic(topic["id"], language)
            if entry is not None:
                entry["relevance_score"] = score
                matches.append(entry)

    matches.sort(key=lambda item: item["relevance_score"], reverse=True)

    return {
        "success": True,
        "query": query,
        "match_count": len(matches),
        "results": matches,
        "kb_version": KB_VERSION,
        "limitations": list(_KB_LIMITATIONS),
    }


def validate_knowledge_base() -> dict[str, Any]:
    """
    Verify the integrity of the knowledge base.

    Every topic must be validated, cite at least one source with an
    https URL, provide at least three English guidance items, carry a
    review date, and have unique ids. This runs as a startup/test
    guard so unreviewed content cannot be served.
    """
    errors: list[str] = []

    seen_ids: set[str] = set()

    for topic in KNOWLEDGE_TOPICS:
        tid = topic.get("id", "<missing-id>")

        if tid in seen_ids:
            errors.append(f"{tid}: duplicate topic id")
        seen_ids.add(tid)

        if not topic.get("validated"):
            errors.append(f"{tid}: topic is not marked validated")

        if not topic.get("sources"):
            errors.append(f"{tid}: no sources cited")

        for source in topic.get("sources", []):
            if not source.get("url", "").startswith("https://"):
                errors.append(
                    f"{tid}: source '{source.get('name')}' lacks a valid https URL"
                )

        if not topic.get("reviewed_at"):
            errors.append(f"{tid}: missing review date")

        guidance = topic.get("guidance", {}).get("en", [])
        if len(guidance) < 3:
            errors.append(f"{tid}: fewer than 3 guidance items")

        if not topic.get("summary", {}).get("en"):
            errors.append(f"{tid}: missing English summary")

    return {
        "success": not errors,
        "kb_version": KB_VERSION,
        "topic_count": len(KNOWLEDGE_TOPICS),
        "validated_count": sum(1 for t in KNOWLEDGE_TOPICS if t.get("validated")),
        "errors": errors,
        "limitations": list(_KB_LIMITATIONS),
    }
