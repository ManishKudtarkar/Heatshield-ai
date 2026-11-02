"""
HeatShield AI — Validated Occupational Safety Knowledge Base

A curated, deterministic reference layer of occupational heat-safety
guidance that the multi-agent pipeline grounds its recommendations in.

Design principles (mirrors the rest of HeatShield AI):

- Every entry carries explicit provenance (source, source type and
  review status) so guidance can be audited.
- Entries describe precautions and controls only — no numerical
  risk scores, no occupational risk categories, no medical diagnosis.
- The knowledge base never fabricates site-specific facts (for example
  the existence of a cooling shelter at a particular worksite).
- Retrieval is deterministic: the same inputs always return the same
  entries, independently of any LLM.

The advisory agents receive the retrieved entries as grounding context
and are instructed to stay consistent with them.
"""

from typing import Any


KNOWLEDGE_BASE_VERSION = "2026.1"


# --------------------------------------------------
# CURATED KNOWLEDGE ENTRIES
# --------------------------------------------------
# Each entry:
#   id            stable identifier
#   topic         retrieval topic key
#   triggers      exposure conditions this entry applies to
#   title/description English statement of the guidance
#   localizations hi/gu worker-friendly translations of the
#                 title and description
#   source        named authoritative basis
#   source_type   guidance_standard | regulatory_code | public_health
#   review_status validation state of the entry

KNOWLEDGE_ENTRIES: list[dict[str, Any]] = [
    {
        "id": "water-frequency",
        "topic": "hydration",
        "triggers": {"always": True},
        "title": "Frequent water access",
        "description": (
            "Outdoor workers should be able to drink cool water in "
            "small amounts frequently (roughly a cup every 15-20 "
            "minutes of work) rather than large amounts rarely. "
            "Thirst is not a reliable indicator of hydration needs "
            "in hot conditions."
        ),
        "localizations": {
            "hi": {
                "title": "पानी की नियमित उपलब्धता",
                "description": (
                    "खुले में काम करने वाले श्रमिकों को थोड़ी-थोड़ी "
                    "ठंडी पानी बार-बार पीनी चाहिए (लगभग हर 15-20 मिनट "
                    "में एक घूँट), एक बार में बहुत अधिक नहीं। गर्मी में "
                    "प्यास का होना शरीर में पानी की कमी का भरोसेमंद संकेत "
                    "नहीं है।"
                ),
            },
            "gu": {
                "title": "પાણીની નિયમિત ઉપલબ્ધતા",
                "description": (
                    "ખુલ્લામાં કામ કરતા કાર્યકરોએ થોડું-થોડું ઠંડુ પાણી "
                    "વારંવાર પીવું જોઈએ (આશરે દર 15-20 મિનિટે એ ઘૂંટ), "
                    "એક સાથે ખૂબ વધારે નહીં. ગરમીમાં ત્રષા લાગવી એ શરીરમાં "
                    "પાણીની ખરાબીનો ભરોસાપાત્ર સંકેત નથી."
                ),
            },
        },
        "source": "NIOSH - Work Safely in the Heat",
        "source_type": "guidance_standard",
        "review_status": "validated",
    },
    {
        "id": "shade-recovery",
        "topic": "rest_shade",
        "triggers": {"shade_availability": ["none", "partial", "unknown"]},
        "title": "Shaded recovery breaks",
        "description": (
            "Rest breaks taken in shade or cooled areas allow the body "
            "to shed stored heat. When shade is limited or absent, "
            "continuous exposure duration should be reduced and break "
            "frequency increased, and temporary shade structures should "
            "be considered."
        ),
        "localizations": {
            "hi": {
                "title": "छायां में विश्राम",
                "description": (
                    "छायां या ठंडी जगह में लिया गया विश्राम शरीर की अतिरिक्त "
                    "गर्मी कम करने में मदद करता है। जब छाया सीमित या नहीं हो, "
                    "तो लगातार काम का समय घटाना और विश्राम की आवृत्ति बढ़ाना "
                    "चाहिए, और अस्थायी छाया व्यवस्था पर विचार करना चाहिए।"
                ),
            },
            "gu": {
                "title": "છાયામાં વિશ્રામ",
                "description": (
                    "છાયામાં અથવા ઠંડા વિસ્તારમાં લેવાયેલો વિશ્રામ શરીરની "
                    "વધારાની ગરમી ઘટાડવામાં મદદ કરે છે. જ્યારે છાયા મર્યાદિત "
                    "અથવા ન હોય, ત્યારે સતત કામનો સમય ઘટાડવો અને વિશ્રામની "
                    "આવર્તન વધારવી જોઈએ, અને અસ્થાયી છાયા વ્યવસ્થા પર વિચાર "
                    "કરવો જોઈએ."
                ),
            },
        },
        "source": "OSHA - Outdoor Heat Illness Prevention",
        "source_type": "regulatory_code",
        "review_status": "validated",
    },
    {
        "id": "acclimatization",
        "topic": "acclimatization",
        "triggers": {
            "acclimatization": ["not_acclimatized", "unknown"],
        },
        "title": "Heat acclimatization for new workers",
        "description": (
            "Workers new to hot conditions, or returning after an "
            "absence of a week or more, need gradual acclimatization. "
            "During this period their workload and continuous exposure "
            "should be limited and additional supervision provided, "
            "because most early-season heat illnesses occur in "
            "non-acclimatized workers."
        ),
        "localizations": {
            "hi": {
                "title": "गर्मी के लिए अनुकूलन",
                "description": (
                    "गर्मी में नए काम शुरू करने वाले या एक सप्ताह या उससे "
                    "अधिक के ब्रेक के बाद लौटने वाले श्रमिकों को धीरे-धीरे "
                    "गर्मी के प्रति अनुकूलित होने दें। इस अवधि में उनका काम का "
                    "भार और लगातार जोखिम सीमित रखें और अधिक निगरानी प्रदान "
                    "करें, क्योंकि अधिकांश शुरुआती गर्मी-बीमारियाँ बिना "
                    "अनुकूलन वाले श्रमिकों को होती हैं।"
                ),
            },
            "gu": {
                "title": "ગરમી માટે ઢાળવું (Acclimatization)",
                "description": (
                    "ગરમીમાં નવું કામ શરૂ કરતા કે એક અઠવાડિયા કે તેથી વધુ "
                    "છુટ્ટી પછી પરત ફરતા કાર્યકરોને ધીમે ધીમે ગરમી સાથે બંધબેસતું "
                    "થવા દો. આ ગાળામાં તેમનું કામનું પ્રમાણ અને સતત એક્સપોઝર "
                    "મર્યાદિત રાખો અને વધારાની દેખરેખ આપો, કારણ કે મોટાભાગની "
                    "શરૂઆતની ગરમી-ઉપદ્રવો ઢાળવા વિનાના કાર્યકરોમાં થાય છે."
                ),
            },
        },
        "source": "OSHA - Heat Exposure / Acclimatization guidance",
        "source_type": "regulatory_code",
        "review_status": "validated",
    },
    {
        "id": "work-rest-cycles",
        "topic": "rest_shade",
        "triggers": {"workload": ["heavy", "very_heavy"]},
        "title": "Work-rest cycles for heavy physical labor",
        "description": (
            "Heavy and very heavy physical work generates substantial "
            "internal heat. Shorter work periods with more frequent "
            "rest breaks in shade help keep core temperature manageable. "
            "When break frequency is unknown it should be established "
            "explicitly by the supervisor."
        ),
        "localizations": {
            "hi": {
                "title": "भारी काम के लिए कार्य-विश्राम चक्र",
                "description": (
                    "भारी और बहुत भारी शारीरिक श्रम से शरीर में काफी आंतरिक "
                    "गर्मी पैदा होती है। छाया में अधिक बार छोटे विश्राम के साथ "
                    "काम के छोटे-छोटे काल शरीर के तापमान को नियंत्रण में रखने "
                    "में मदद करते हैं। यदि विश्राम की आवृत्ति अज्ञात हो तो "
                    "पर्यवेक्षक को इसे स्पष्ट रूप से निर्धारित करना चाहिए।"
                ),
            },
            "gu": {
                "title": "ભારે કામ માટે કામ-વિશ્રામ ચક્ર",
                "description": (
                    "ભારે અને ખૂબ ભારે શારીરિક મહેનતમાં શરીરમાં પુરતી આંતરિક "
                    "ગરમી પેદા થાય છે. છાયામાં વારંવાર ટૂંકા વિશ્રામ સાથે કામના "
                    "ટૂંકા ગાળા શરીરના તાપમાનને નિયંત્રણમાં રાખવામાં મદદ કરે છે. "
                    "જો વિશ્રામની આવર્તન અજાણ્યા હોય તો સુપરવાઇઝરે તેને સ્પષ્ટપણે "
                    "નક્કી કરવી જોઈએ."
                ),
            },
        },
        "source": "NIOSH Work_REST! app / occupational heat guidance",
        "source_type": "guidance_standard",
        "review_status": "validated",
    },
    {
        "id": "ppe-heat-load",
        "topic": "ppe_clothing",
        "triggers": {"has_ppe": True},
        "title": "Protective equipment increases heat load",
        "description": (
            "Helmets, boots and protective clothing reduce the body's "
            "ability to lose heat. Where PPE must be worn, schedule "
            "additional recovery time, use the coolest compliant PPE "
            "available, and alternate tasks where possible."
        ),
        "localizations": {
            "hi": {
                "title": "सुरक्षा उपकरण से गर्मी का बोझ बढ़ता है",
                "description": (
                    "हेलमेट, जूते और सुरक्षात्मक वस्त्र शरीर की गर्मी बाहर "
                    "निकालने की क्षमता कम करते हैं। जहां सुरक्षा उपकरण पहनना "
                    "आवश्यक हो, वहां अतिरिक्त विश्राम समय निर्धारित करें, "
                    "उपलब्ध सबसे ठंडा मानक-अनुपालक उपकरण उपयोग करें, और संभव हो "
                    "तो कार्यों को बदल-बदल कर करें।"
                ),
            },
            "gu": {
                "title": "સુરક્ષા સાધનોથી ગરમીનો બોજ વધે છે",
                "description": (
                    "હેલ્મેટ, બૂટ અને સુરક્ષા કપડાં શરીરની ગરમી બહાર કાઢવાની "
                    "ક્ષમતા ઘટાડે છે. જ્યાં સુરક્ષા સાધનો પહેરવા ફરજિયાત હોય, "
                    "ત્યાં વધારાનો વિશ્રામ સમય ગોઠવો, ઉપલબ્ધ સૌથી ઠંડા "
                    "માનક-અનુસારના સાધનો વાપરો, અને શક્ય હોય તો કાર્યો બદલીને "
                    "કરો."
                ),
            },
        },
        "source": "ILO - Occupational safety and health guidance",
        "source_type": "guidance_standard",
        "review_status": "validated",
    },
    {
        "id": "sun-exposure-timing",
        "topic": "solar_exposure",
        "triggers": {"direct_sunlight": True},
        "title": "Limit direct sun exposure during peak hours",
        "description": (
            "Solar radiant heat load is highest around midday. Where "
            "the schedule allows, the most strenuous tasks exposed to "
            "direct sunlight should be shifted to cooler parts of the "
            "day, and reflective or light-coloured clothing should be "
            "used when compatible with the work."
        ),
        "localizations": {
            "hi": {
                "title": "दोपहर में सीधे सूरज से बचें",
                "description": (
                    "सौर विकिरण से गर्मी दोपहर के आसपास सबसे अधिक होती है। "
                    "जहां समय-सारणी अनुमति दे, वहां सीधी धूप में किए जाने वाले "
                    "सबसे कठिन काम दिन के ठंडे समय में स्थानांतरित करें, और "
                    "काम के अनुकूल हों तो हल्के रंग के या परावर्तक कपड़े पहनें।"
                ),
            },
            "gu": {
                "title": "બપોરે સીધા તડકામાં એક્સપોઝર ઘટાડો",
                "description": (
                    "સૂર્યના કિરણોથી ગરમી બપોરના સમયે સૌથી વધુ હોય છે. જ્યાં "
                    "સમય-કોષ્ટક મંજૂરી આપે, ત્યાં સીધા તડકામાં કરવાના સૌથી કઠણ "
                    "કામ દિવસના ઠંડા સમયે ખસેડો, અને કામ સાથે બંધબેસતું હોય તો "
                    "હલકા રંગના અથવા પરાવર્તક કપડાં પહેરો."
                ),
            },
        },
        "source": "WHO - Heat and health guidance",
        "source_type": "public_health",
        "review_status": "validated",
    },
    {
        "id": "humidity-evaporative-limit",
        "topic": "environmental",
        "triggers": {"high_humidity": True},
        "title": "High humidity limits the body's cooling",
        "description": (
            "Sweat cools the body mainly by evaporating. When air "
            "humidity is high, evaporation slows and apparent "
            "temperature rises, so the same air temperature becomes "
            "more stressful. Precautions should be increased even if "
            "the thermometer reading seems moderate."
        ),
        "localizations": {
            "hi": {
                "title": "अधिक नमी शरीर को ठंडा होने से रोकती है",
                "description": (
                    "पसीना मुख्यतः वाष्पित होकर शरीर को ठंडा करता है। जब हवा में "
                    "नमी अधिक हो, वाष्पीकरण धीमा हो जाता है और अनुभूत तापमान बढ़ता "
                    "है, इसलिए समान तापमान भी अधिक हानिकारक हो जाता है। थर्मामीटर "
                    "पाठ सामान्य दिखने पर भी सावधानियाँ बढ़ानी चाहिए।"
                ),
            },
            "gu": {
                "title": "વધારે ભેજ શરીરને ઠંડુ પડતા અટકાવે છે",
                "description": (
                    "મેહન મુખ્યત્વે બાષ્પીભવન થઈ શરીરને ઠંડુ કરે છે. જ્યારે હવામાં "
                    "ભેજ વધારે હોય, બાષ્પીભવન ધીમું પડે છે અને અનુભવાતું તાપમાન વધે "
                    "છે, એટલે સરખું તાપમાન પણ વધારે ત્રાસદાયક બને છે. થર્મોમીટરનું "
                    "વાંચન સામાન્ય દેખાય તો પણ સાવચેતીઓ વધાવવી જોઈએ."
                ),
            },
        },
        "source": "WHO - Heat and health guidance",
        "source_type": "public_health",
        "review_status": "validated",
    },
    {
        "id": "buddy-monitoring",
        "topic": "monitoring",
        "triggers": {"always": True},
        "title": "Monitor co-workers and report symptoms early",
        "description": (
            "Early heat illness signs (headache, dizziness, weakness, "
            "cramps, confusion) are often noticed by co-workers before "
            "the affected person notices them. Workers should be paired "
            "or supervised so symptoms are reported immediately, and "
            "no one should work alone in high-heat conditions where "
            "avoidable."
        ),
        "localizations": {
            "hi": {
                "title": "सहकर्मियों की निगरानी और जल्दी लक्षण रिपोर्ट करें",
                "description": (
                    "गर्मी से होने वाली बीमारी के शुरुआती संकेत (सिरदर्द, चक्कर, "
                    "कमजोरी, मांसपेशियों में खिंचाव, भ्रम) अक्सर सहकर्मी पहले भांप "
                    "लेते हैं। श्रमिकों को जोड़ों में या निगरानी में काम करना चाहिए "
                    "ताकि लक्षण तुरंत रिपोर्ट हों, और जहां संभव हो उच्च गर्मी में "
                    "किसी को अकेले काम नहीं करना चाहिए।"
                ),
            },
            "gu": {
                "title": "સહકર્મીઓની દેખરેખ અને લક્ષણો જલદી રિપોર્ટ કરો",
                "description": (
                    "ગરમીને કારણે થતા ઉપદ્રવોના શરૂઆતના સંકેત (માથાનો દુખાવો, "
                    "ચક્કર, નબળાઈ, સ્નાયુમાં ખેંચાણ, ગંભીરતા/ભ્રમ) ઘણીવાર પીડિત "
                    "પોતાને પહેલા સહકર્મીઓ ભાળી લે છે. કાર્યકરોને જોડીમાં અથવા "
                    "દેખરેખ હેઠળ કામ કરવું જોઈએ જેથી લક્ષણો તાત્કાલિક રિપોર્ટ થાય, "
                    "અને શક્ય હોય ત્યાં સુધી વધારે ગરમીમાં કોઈએ એકલા કામ ન કરવું "
                    "જોઈએ."
                ),
            },
        },
        "source": "CDC - NIOSH heat illness prevention",
        "source_type": "public_health",
        "review_status": "validated",
    },
    {
        "id": "emergency-response",
        "topic": "emergency",
        "triggers": {"always": True},
        "title": "Heat stroke emergency response",
        "description": (
            "Confusion, seizures, collapse, loss of consciousness or "
            "hot skin that has stopped sweating indicate a medical "
            "emergency. Move the person to shade, call emergency "
            "services immediately, and begin active cooling (water "
            "spray, ice packs to neck/armpits/groin) without delay. "
            "Do not wait for an AI assessment before acting."
        ),
        "localizations": {
            "hi": {
                "title": "लू के आपातकालीन स्थिति में प्रतिक्रिया",
                "description": (
                    "भ्रम, दौरा, गिर जाना, बेहोशी या पसीना आना बंद होने वाली गर्म "
                    "त्वचा चिकित्सा आपातकाल का संकेत है। व्यक्ति को छाया में ले जाएं, "
                    "तुरंत आपात सेवाओं को कॉल करें, और तत्काल सक्रिय ठंडा करना शुरू "
                    "करें (पानी का छिड़काव, गर्दन/बगल/कमर पर बर्फ की पॉड)। कार्रवाई "
                    "से पहले AI आंकलन का इंतजार न करें।"
                ),
            },
            "gu": {
                "title": "લૂ (હીટ સ્ટ્રોક) કટોકટીમાં પ્રતિક્રિયા",
                "description": (
                    "ગંભીરતા/ભ્રમ, દોરડું (seizure), ઢળી પડવું, બેભાન થવું અથવા "
                    "પસીણ આવવો બંધ થયેલી ગરમ ત્વચા એ મેડિકલ કટોકટીનો સંકેત છે. "
                    "વ્યક્તિને છાયામાં લઈ જાઓ, તાત્કાલિક એમરજન્સી સેવાને કોલ કરો, "
                    "અને તરત જ સક્રિય ઠંડક શરૂ કરો (પાણીનો છંટકાવ, ગળા/ખંભેરણી/ટાંઠા "
                    "પર બરફની પોટ)। ક્રિયા કરતા પહેલા AI આકલનની રાહ ન જુઓ."
                ),
            },
        },
        "source": "WHO / NDMA - Heat emergency guidance",
        "source_type": "public_health",
        "review_status": "validated",
    },
]


KNOWLEDGE_INDEX = {entry["id"]: entry for entry in KNOWLEDGE_ENTRIES}


# --------------------------------------------------
# RETRIEVAL
# --------------------------------------------------

def _matches(entry: dict, context: dict) -> bool:
    """Deterministically decide whether an entry applies to a context."""

    triggers = entry.get("triggers", {})

    if triggers.get("always"):
        return True

    weather = context.get("weather_summary") or {}
    worker = context.get("worker_summary") or {}

    if "shade_availability" in triggers:
        if worker.get("shade_availability") not in triggers["shade_availability"]:
            return False

    if "acclimatization" in triggers:
        if worker.get("acclimatization") not in triggers["acclimatization"]:
            return False

    if "workload" in triggers:
        if worker.get("workload") not in triggers["workload"]:
            return False

    if triggers.get("has_ppe"):
        ppe = worker.get("ppe_items") or []
        if not ppe:
            return False

    if triggers.get("direct_sunlight"):
        if worker.get("direct_sunlight") is not True:
            return False

    if triggers.get("high_humidity"):
        humidity = weather.get("humidity_percent")
        if not isinstance(humidity, (int, float)) or humidity < 60:
            return False

    return True


def retrieve_knowledge(
    weather_summary: dict | None = None,
    worker_summary: dict | None = None,
    language: str = "en",
) -> dict:
    """
    Return validated knowledge-base entries relevant to an assessment.

    Entries are localized when a translation exists for ``language``;
    the English statement is always retained for audit purposes.
    """

    context = {
        "weather_summary": weather_summary or {},
        "worker_summary": worker_summary or {},
    }

    matched = [entry for entry in KNOWLEDGE_ENTRIES if _matches(entry, context)]

    results = []
    for entry in matched:
        localized = entry.get("localizations", {}).get(language, {})
        results.append(
            {
                "id": entry["id"],
                "topic": entry["topic"],
                "title": localized.get("title", entry["title"]),
                "description": localized.get(
                    "description", entry["description"]
                ),
                "title_en": entry["title"],
                "description_en": entry["description"],
                "source": entry["source"],
                "source_type": entry["source_type"],
                "review_status": entry["review_status"],
            }
        )

    return {
        "success": True,
        "knowledge_base_version": KNOWLEDGE_BASE_VERSION,
        "language": language,
        "entry_count": len(results),
        "entries": results,
        "limitations": [
            "Knowledge-base entries describe general occupational "
            "heat-safety practice, not site-specific measurements.",
            "Entries do not constitute medical advice or diagnosis.",
        ],
    }


def format_knowledge_for_agent(retrieved: dict) -> str:
    """Render retrieved entries as agent grounding context (English)."""

    lines = [
        f"VALIDATED KNOWLEDGE BASE (version "
        f"{retrieved.get('knowledge_base_version', 'unknown')})",
    ]

    for entry in retrieved.get("entries", []):
        lines.append(
            f"- [{entry['id']}] {entry['title_en']}: "
            f"{entry['description_en']} "
            f"(Source: {entry['source']}; "
            f"status: {entry['review_status']})"
        )

    if not retrieved.get("entries"):
        lines.append("- No specific entries matched this assessment.")

    return "\n".join(lines)
