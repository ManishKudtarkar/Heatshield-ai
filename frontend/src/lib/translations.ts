// HeatShield AI — UI string translations.
// Supported languages: English (en), Hindi (hi), Gujarati (gu).
// Backend deterministic safety alerts are localized server-side via the
// `language` field sent in the assess request; the LLM advisory is also
// instructed to respond in the selected language.

export type Lang = "en" | "hi" | "gu";

export const LANGUAGES: { code: Lang; native: string }[] = [
  { code: "en", native: "English" },
  { code: "hi", native: "हिन्दी" },
  { code: "gu", native: "ગુજરાતી" },
];

export interface Strings {
  brand: { name: string; suffix: string };
  nav: {
    workspace: string;
    overview: string;
    newAssessment: string;
    assessments: string;
    safetyGuidance: string;
    resources: string;
    planned: string;
    primaryNav: string;
    openNav: string;
    closeNav: string;
  };
  source: { label: string; name: string; note: string };
  topbar: { observationsAvailable: string };
  heading: { overline: string; title: string; subtitle: string; newAssessment: string };
  env: { overline: string; title: string; observed: string };
  metrics: { airTemp: string; humidity: string; apparentTemp: string; wind: string; currentObs: string; notWbgt: string };
  status: {
    overline: string;
    ready: string;
    completedCopy: string;
    readyCopy: string;
    infoToCollect: string;
    readyForInput: string;
    noAssessment: string;
  };
  latest: {
    overline: string;
    noAssessment: string;
    copy: string;
    workload: string;
    sunlight: string;
    shade: string;
    water: string;
  };
  display: { yes: string; no: string; notProvided: string; noneReported: string };
  enums: {
    workload: Record<string, string>;
    shade: Record<string, string>;
    acclimatization: Record<string, string>;
    assessmentStatus: Record<string, string>;
    missingInfo: Record<string, string>;
    priority: Record<string, string>;
  };
  form: {
    overline: string;
    title: string;
    required: string;
    worksite: string;
    workerProfile: string;
    envExposure: string;
    safetyProvisions: string;
    exposureRecovery: string;
    location: string;
    locationPh: string;
    workArea: string;
    workAreaPh: string;
    occupation: string;
    shiftHours: string;
    workload: string;
    acclimatization: string;
    directSunlight: string;
    sunlightYes: string;
    sunlightNo: string;
    shadeAvailability: string;
    waterAccess: string;
    waterYes: string;
    waterNo: string;
    ppeItems: string;
    ppePh: string;
    continuousExposure: string;
    breakFrequency: string;
    optionalPh: string;
    runAssessment: string;
    analyzing: string;
    errorConnect: string;
    errorDefault: string;
  };
  context: {
    overline: string;
    title: string;
    envObs: string;
    envObsDesc: string;
    exposureFactors: string;
    exposureFactorsDesc: string;
    practicalControls: string;
    practicalControlsDesc: string;
    disclaimer: string;
  };
  alerts: { overline: string; title: string; emergencyHeading: string; viewLimitations: string };
  output: {
    overline: string;
    title: string;
    screeningOnly: string;
    advisoryOverline: string;
    advisoryTitle: string;
    advisoryFallback: string;
    missingOverline: string;
    itemsToCollect: string;
    profileComplete: string;
    allFieldsSupplied: string;
    viewLimitations: string;
  };
  footer: { label: string; note: string };
  langSwitch: { label: string };
  guidance: {
    overline: string;
    title: string;
    subtitle: string;
    searchPh: string;
    searchBtn: string;
    validated: string;
    reviewed: string;
    sources: string;
    guidanceHeading: string;
    noResults: string;
    resultsCount: string;
    kbVersion: string;
    integrityOk: string;
    browseAll: string;
    backToList: string;
    category: string;
    loadError: string;
  };
  resources: {
    overline: string;
    title: string;
    subtitle: string;
    lat: string;
    lng: string;
    radius: string;
    radiusUnit: string;
    categories: string;
    catWater: string;
    catShelter: string;
    catRefuge: string;
    catShade: string;
    findBtn: string;
    searching: string;
    found: string;
    noneFound: string;
    distance: string;
    sourceLink: string;
    osmNote: string;
    useLocation: string;
    loadError: string;
  };
  dashboard: {
    overline: string;
    title: string;
    subtitle: string;
    refresh: string;
    clear: string;
    clearConfirm: string;
    cleared: string;
    total: string;
    critical: string;
    heightened: string;
    advisory: string;
    noneRisk: string;
    urgentHeading: string;
    noUrgent: string;
    locationsHeading: string;
    recentHeading: string;
    completenessHeading: string;
    completeShare: string;
    incomplete: string;
    worker: string;
    locationCol: string;
    riskCol: string;
    tempCol: string;
    timeCol: string;
    alertsCol: string;
    assessmentsCol: string;
    worstCol: string;
    maxTempCol: string;
    empty: string;
    limitationsHeading: string;
    loadError: string;
    unusable: string;
  };
}

const en: Strings = {
  brand: { name: "HeatShield", suffix: "AI" },
  nav: {
    workspace: "WORKSPACE",
    overview: "Overview",
    newAssessment: "New assessment",
    assessments: "Assessments",
    safetyGuidance: "Safety guidance",
    resources: "Resources",
    planned: "Planned",
    primaryNav: "Primary navigation",
    openNav: "Open navigation",
    closeNav: "Close navigation",
  },
  source: { label: "Data source", name: "Open-Meteo", note: "Environmental observations are not worksite measurements." },
  topbar: { observationsAvailable: "Observations available" },
  heading: {
    overline: "CLIMATE OPERATIONS / OVERVIEW",
    title: "Worker heat safety",
    subtitle: "Understand current conditions, reported exposure, and the next practical action.",
    newAssessment: "New assessment",
  },
  env: { overline: "ENVIRONMENTAL CONDITIONS", title: "Current observations", observed: "Observed" },
  metrics: {
    airTemp: "Air temperature",
    humidity: "Relative humidity",
    apparentTemp: "Apparent temperature",
    wind: "Wind speed",
    currentObs: "Current observation",
    notWbgt: "Not measured WBGT",
  },
  status: {
    overline: "ASSESSMENT STATUS",
    ready: "Ready to assess",
    completedCopy: "Screening completed from environmental observations and the reported worker profile.",
    readyCopy: "Complete a worker profile to generate a transparent heat-exposure screening assessment.",
    infoToCollect: "Information to collect",
    readyForInput: "Ready for input",
    noAssessment: "No assessment has been submitted yet.",
  },
  latest: {
    overline: "LATEST WORKER ASSESSMENT",
    noAssessment: "No assessment yet",
    copy: "Reported work conditions will be summarized here after an assessment.",
    workload: "Workload",
    sunlight: "Direct sunlight",
    shade: "Shade",
    water: "Water access",
  },
  display: { yes: "Yes", no: "No", notProvided: "Not provided", noneReported: "None reported" },
  enums: {
    workload: { light: "Light", moderate: "Moderate", heavy: "Heavy", very_heavy: "Very heavy", unknown: "Unknown" },
    shade: { full: "Full", partial: "Partial", none: "None", unknown: "Unknown" },
    acclimatization: { acclimatized: "Acclimatized", not_acclimatized: "Not acclimatized", unknown: "Unknown" },
    assessmentStatus: {
      screening_only: "Screening only",
      incomplete: "Incomplete",
      wbgt_requires_professional_review: "Requires professional review",
    },
    missingInfo: {
      continuous_exposure_minutes: "Continuous exposure minutes",
      break_frequency_minutes: "Break frequency minutes",
      work_area: "Work area",
      shade_availability: "Shade availability",
      acclimatization: "Acclimatization",
      workload: "Workload",
      temperature_c: "Air temperature",
      humidity_percent: "Relative humidity",
      wind_speed_kmh: "Wind speed",
    },
    priority: {
      advisory: "Advisory",
      heightened_precaution: "Heightened precaution",
      critical_precaution: "Critical precaution",
      none: "None",
    },
  },
  form: {
    overline: "NEW ASSESSMENT",
    title: "Worker and worksite information",
    required: "* Required",
    worksite: "Worksite",
    workerProfile: "Worker profile",
    envExposure: "Environmental exposure",
    safetyProvisions: "Safety provisions",
    exposureRecovery: "Exposure and recovery",
    location: "Location",
    locationPh: "City or worksite",
    workArea: "Work area",
    workAreaPh: "Describe the worksite",
    occupation: "Occupation",
    shiftHours: "Shift duration (hours)",
    workload: "Workload",
    acclimatization: "Acclimatization",
    directSunlight: "Direct sunlight",
    sunlightYes: "Yes — direct exposure",
    sunlightNo: "No direct exposure",
    shadeAvailability: "Shade availability",
    waterAccess: "Drinking water access",
    waterYes: "Available",
    waterNo: "Not available",
    ppeItems: "PPE items",
    ppePh: "Separate items with commas",
    continuousExposure: "Continuous exposure (minutes)",
    breakFrequency: "Break frequency (minutes)",
    optionalPh: "Optional",
    runAssessment: "Run heat assessment",
    analyzing: "Analyzing conditions...",
    errorConnect: "Unable to connect to the HeatShield API.",
    errorDefault: "The assessment could not be completed.",
  },
  context: {
    overline: "ASSESSMENT CONTEXT",
    title: "What you'll receive",
    envObs: "Environmental observations",
    envObsDesc: "Current temperature, humidity, apparent temperature, and wind from Open-Meteo.",
    exposureFactors: "Exposure factors",
    exposureFactorsDesc: "A transparent summary of the reported work conditions and what is missing.",
    practicalControls: "Practical controls",
    practicalControlsDesc: "Safety guidance grounded in the assessment, with its limitations clearly stated.",
    disclaimer: "Apparent temperature is not WBGT. This tool provides screening support, not a medical diagnosis or a worksite measurement.",
  },
  alerts: {
    overline: "PROACTIVE SAFETY ALERTS",
    title: "Safety alerts",
    emergencyHeading: "Seek emergency medical assistance if needed",
    viewLimitations: "View alert limitations",
  },
  output: {
    overline: "ASSESSMENT OUTPUT",
    title: "What to do next",
    screeningOnly: "Screening only",
    advisoryOverline: "SAFETY ADVISORY",
    advisoryTitle: "Recommended guidance",
    advisoryFallback: "No advisory was returned.",
    missingOverline: "MISSING INFORMATION",
    itemsToCollect: "{count} item(s) to collect",
    profileComplete: "Profile complete",
    allFieldsSupplied: "All tracked worker profile fields were supplied.",
    viewLimitations: "View assessment limitations",
  },
  footer: {
    label: "Safety note:",
    note: "If someone shows confusion, seizures, collapse, or loss of consciousness, seek immediate emergency medical assistance. Do not delay for an AI assessment.",
  },
  langSwitch: { label: "Language" },
  guidance: {
    overline: "VALIDATED SAFETY KNOWLEDGE",
    title: "Occupational heat-safety guidance",
    subtitle: "Curated guidance reviewed against OSHA / NIOSH / CDC sources. Every topic is validated and cited.",
    searchPh: "Search topics, e.g. hydration, WBGT, acclimatization",
    searchBtn: "Search",
    validated: "Validated",
    reviewed: "Reviewed",
    sources: "Sources",
    guidanceHeading: "Guidance",
    noResults: "No matching topics found. Try another term or browse all topics.",
    resultsCount: "{count} topic(s) found",
    kbVersion: "Knowledge base version",
    integrityOk: "All topics validated and cited",
    browseAll: "Browse all topics",
    backToList: "Back to topic list",
    category: "Category",
    loadError: "Safety guidance could not be loaded. Check the API connection.",
  },
  resources: {
    overline: "COOLING RESOURCE DISCOVERY",
    title: "Find cooling resources near a worksite",
    subtitle: "Publicly mapped drinking water, shelters, indoor refuges and shaded spaces from OpenStreetMap.",
    lat: "Worksite latitude",
    lng: "Worksite longitude",
    radius: "Search radius",
    radiusUnit: "m",
    categories: "Categories",
    catWater: "Drinking water",
    catShelter: "Cooling shelters",
    catRefuge: "Indoor refuges",
    catShade: "Shaded spaces",
    findBtn: "Find resources",
    searching: "Searching map data...",
    found: "{count} resource(s) found",
    noneFound: "No mapped cooling resources were found within this radius. Widen the search or verify the coordinates.",
    distance: "Distance",
    sourceLink: "View on OpenStreetMap",
    osmNote: "Results come only from OpenStreetMap; unverified places are never listed. On-site conditions may differ — confirm before relying on a resource.",
    useLocation: "Use my current location",
    loadError: "Cooling resource discovery failed. Please try again.",
  },
  dashboard: {
    overline: "SUPERVISOR MONITORING",
    title: "Cohort heat-risk overview",
    subtitle: "Aggregated, deterministic view of submitted worker assessments across sites.",
    refresh: "Refresh",
    clear: "Clear shift records",
    clearConfirm: "Clear all stored assessment summaries for this shift?",
    cleared: "Stored assessment summaries cleared.",
    total: "Total assessments",
    critical: "Critical precaution",
    heightened: "Heightened precaution",
    advisory: "Advisory",
    noneRisk: "No precaution flag",
    urgentHeading: "Urgent cases requiring attention",
    noUrgent: "No critical-precaution cases in the current cohort.",
    locationsHeading: "Site risk hotspots",
    recentHeading: "Recent assessments",
    completenessHeading: "Profile completeness",
    completeShare: "Complete profiles",
    incomplete: "Assessments missing information",
    worker: "Worker",
    locationCol: "Location",
    riskCol: "Risk level",
    tempCol: "Air temp",
    timeCol: "Submitted",
    alertsCol: "Alerts",
    assessmentsCol: "Assessments",
    worstCol: "Worst risk",
    maxTempCol: "Max temp",
    empty: "No assessments recorded yet. Supervisor statistics appear here as workers submit assessments.",
    limitationsHeading: "Interpretation limits",
    loadError: "Supervisor overview could not be loaded.",
    unusable: "Unusable records excluded",
  },
};

const hi: Strings = {
  brand: { name: "HeatShield", suffix: "AI" },
  nav: {
    workspace: "वर्कस्पेस",
    overview: "अवलोकन",
    newAssessment: "नई जांच",
    assessments: "जांचें",
    safetyGuidance: "सुरक्षा मार्गदर्शन",
    resources: "संसाधन",
    planned: "योजित",
    primaryNav: "मुख्य नेविगेशन",
    openNav: "नेविगेशन खोलें",
    closeNav: "नेविगेशन बंद करें",
  },
  source: { label: "डेटा स्रोत", name: "Open-Meteo", note: "पर्यावरणीय अवलोकन कार्यस्थल माप नहीं हैं।" },
  topbar: { observationsAvailable: "अवलोकन उपलब्ध हैं" },
  heading: {
    overline: "जलवायु संचालन / अवलोकन",
    title: "श्रमिक ऊष्मा सुरक्षा",
    subtitle: "वर्तमान परिस्थितियों, अनुभव किए गए अनावरण और अगले व्यावहारिक कदम को समझें।",
    newAssessment: "नई जांच",
  },
  env: { overline: "पर्यावरणीय परिस्थितियां", title: "वर्तमान अवलोकन", observed: "अवलोकित" },
  metrics: {
    airTemp: "वायु तापमान",
    humidity: "सापेक्ष आर्द्रता",
    apparentTemp: "प्रत्यक्ष तापमान",
    wind: "हवा की गति",
    currentObs: "वर्तमान अवलोकन",
    notWbgt: "मापा हुआ WBGT नहीं",
  },
  status: {
    overline: "जांच स्थिति",
    ready: "जांच के लिए तैयार",
    completedCopy: "पर्यावरणीय अवलोकनों और दी गई श्रमिक प्रोफ़ाइल से जांच पूर्ण हुई।",
    readyCopy: "पारदर्शी ऊष्मा-अनावरण जांच बनाने हेतु श्रमिक प्रोफ़ाइल पूर्ण करें।",
    infoToCollect: "एकत्र करने योग्य जानकारी",
    readyForInput: "इनपुट के लिए तैयार",
    noAssessment: "अभी तक कोई जांच सबमिट नहीं की गई है।",
  },
  latest: {
    overline: "नवीनतम श्रमिक जांच",
    noAssessment: "अभी कोई जांच नहीं",
    copy: "जांच के बाद दी गई कार्य परिस्थितियां यहां सारांशित होंगी।",
    workload: "कार्यभार",
    sunlight: "सीधी धूप",
    shade: "छाया",
    water: "पानी उपलब्धता",
  },
  display: { yes: "हां", no: "नहीं", notProvided: "दी गई नहीं", noneReported: "कुछ नहीं बताया" },
  enums: {
    workload: { light: "हल्का", moderate: "मध्यम", heavy: "भारी", very_heavy: "बहुत भारी", unknown: "अज्ञात" },
    shade: { full: "पूर्ण", partial: "आंशिक", none: "कोई नहीं", unknown: "अज्ञात" },
    acclimatization: { acclimatized: "अनुकूलित", not_acclimatized: "अनुकूलित नहीं", unknown: "अज्ञात" },
    assessmentStatus: {
      screening_only: "केवल जांच",
      incomplete: "अपूर्ण",
      wbgt_requires_professional_review: "पेशेवर समीक्षा आवश्यक",
    },
    missingInfo: {
      continuous_exposure_minutes: "सतत अनावरण मिनट",
      break_frequency_minutes: "विराम आवृत्ति मिनट",
      work_area: "कार्य क्षेत्र",
      shade_availability: "छाया उपलब्धता",
      acclimatization: "अनुकूलन",
      workload: "कार्यभार",
      temperature_c: "वायु तापमान",
      humidity_percent: "सापेक्ष आर्द्रता",
      wind_speed_kmh: "हवा की गति",
    },
    priority: {
      advisory: "सामान्य सतर्कता",
      heightened_precaution: "उच्च सतर्कता",
      critical_precaution: "गंभीर सतर्कता",
      none: "कोई नहीं",
    },
  },
  form: {
    overline: "नई जांच",
    title: "श्रमिक और कार्यस्थल जानकारी",
    required: "* आवश्यक",
    worksite: "कार्यस्थल",
    workerProfile: "श्रमिक प्रोफ़ाइल",
    envExposure: "पर्यावरणीय अनावरण",
    safetyProvisions: "सुरक्षा व्यवस्था",
    exposureRecovery: "अनावरण और पुनर्प्राप्ति",
    location: "स्थान",
    locationPh: "शहर या कार्यस्थल",
    workArea: "कार्य क्षेत्र",
    workAreaPh: "कार्यस्थल का वर्णन करें",
    occupation: "व्यवसाय",
    shiftHours: "पाली अवधि (घंटे)",
    workload: "कार्यभार",
    acclimatization: "अनुकूलन",
    directSunlight: "सीधी धूप",
    sunlightYes: "हां — सीधा अनावरण",
    sunlightNo: "सीधा अनावरण नहीं",
    shadeAvailability: "छाया उपलब्धता",
    waterAccess: "पीने का पानी उपलब्धता",
    waterYes: "उपलब्ध",
    waterNo: "उपलब्ध नहीं",
    ppeItems: "PPE वस्तुएं",
    ppePh: "वस्तुओं को अल्पविराम से अलग करें",
    continuousExposure: "सतत अनावरण (मिनट)",
    breakFrequency: "विराम आवृत्ति (मिनट)",
    optionalPh: "वैकल्पिक",
    runAssessment: "ऊष्मा जांच चलाएं",
    analyzing: "परिस्थितियों का विश्लेषण हो रहा है...",
    errorConnect: "HeatShield API से जुड़ने में असमर्थ।",
    errorDefault: "जांच पूरी नहीं हो सकी।",
  },
  context: {
    overline: "जांच संदर्भ",
    title: "आपको क्या प्राप्त होगा",
    envObs: "पर्यावरणीय अवलोकन",
    envObsDesc: "Open-Meteo से वर्तमान तापमान, आर्द्रता, प्रत्यक्ष तापमान और हवा।",
    exposureFactors: "अनावरण कारक",
    exposureFactorsDesc: "दी गई कार्य परिस्थितियों और कमी वाली जानकारी का पारदर्शी सारांश।",
    practicalControls: "व्यावहारिक नियंत्रण",
    practicalControlsDesc: "जांच पर आधारित सुरक्षा मार्गदर्शन, इसकी सीमाएं स्पष्ट रूप से बताई गई।",
    disclaimer: "प्रत्यक्ष तापमान WBGT नहीं है। यह उपकरण जांच सहायता देता है, चिकित्सा निदान या कार्यस्थल माप नहीं।",
  },
  alerts: {
    overline: "सक्रिय सतर्कता अलर्ट",
    title: "सुरक्षा अलर्ट",
    emergencyHeading: "आवश्यक हो तो आपातकालीन चिकित्सा सहायता लें",
    viewLimitations: "अलर्ट सीमाएं देखें",
  },
  output: {
    overline: "जांच परिणाम",
    title: "अगला कदम",
    screeningOnly: "केवल जांच",
    advisoryOverline: "सुरक्षा सलाह",
    advisoryTitle: "अनुशंसित मार्गदर्शन",
    advisoryFallback: "कोई सलाह नहीं लौटाई गई।",
    missingOverline: "अपूर्ण जानकारी",
    itemsToCollect: "{count} जानकारी एकत्र करनी है",
    profileComplete: "प्रोफ़ाइल पूर्ण",
    allFieldsSupplied: "सभी अनुसरण किए गए श्रमिक प्रोफ़ाइल क्षेत्र दिए गए थे।",
    viewLimitations: "जांच सीमाएं देखें",
  },
  footer: {
    label: "सुरक्षा नोट:",
    note: "यदि किसी में भ्रम, ऐंठन, गिरना, या चेतना खोने के लक्षण दिखें, तो तुरंत आपातकालीन चिकित्सा सहायता प्राप्त करें। AI मूल्यांकन के लिए देरी न करें।",
  },
  langSwitch: { label: "भाषा" },
  guidance: {
    overline: "प्रमाणित सुरक्षा ज्ञान",
    title: "व्यावसायिक गर्मी-सुरक्षा मार्गदर्शन",
    subtitle: "OSHA / NIOSH / CDC स्रोतों से समीक्षित चयनित मार्गदर्शन। प्रत्येक विषय प्रमाणित और संदर्भित है।",
    searchPh: "विषय खोजें, जैसे जलपान, WBGT, अनुकूलन",
    searchBtn: "खोजें",
    validated: "प्रमाणित",
    reviewed: "समीक्षित",
    sources: "स्रोत",
    guidanceHeading: "मार्गदर्शन",
    noResults: "कोई मेल खाता विषय नहीं मिला। दूसरा शब्द आज़माएँ या सभी विषय देखें।",
    resultsCount: "{count} विषय मिले",
    kbVersion: "ज्ञान-आधार संस्करण",
    integrityOk: "सभी विषय प्रमाणित और संदर्भित",
    browseAll: "सभी विषय देखें",
    backToList: "विषय सूची पर वापस",
    category: "श्रेणी",
    loadError: "सुरक्षा मार्गदर्शन लोड नहीं हो सका। API कनेक्शन जाँचें।",
  },
  resources: {
    overline: "शीतलन संसाधन खोज",
    title: "कार्यस्थल के पास शीतलन संसाधन खोजें",
    subtitle: "OpenStreetMap से सार्वजनिक रूप से मानचित्रित पेयजल, आश्रय, इनडोर शरण और छायादार स्थान।",
    lat: "कार्यस्थल अक्षांश",
    lng: "कार्यस्थल देशांतर",
    radius: "खोज दायरा",
    radiusUnit: "मी",
    categories: "श्रेणियाँ",
    catWater: "पेयजल",
    catShelter: "शीतलन आश्रय",
    catRefuge: "इनडोर शरण",
    catShade: "छायादार स्थान",
    findBtn: "संसाधन खोजें",
    searching: "मानचित्र डेटा खोजा जा रहा है...",
    found: "{count} संसाधन मिले",
    noneFound: "इस दायरे में कोई मानचित्रित शीतलन संसाधन नहीं मिला। दायरा बढ़ाएँ या निर्देशांक जाँचें।",
    distance: "दूरी",
    sourceLink: "OpenStreetMap पर देखें",
    osmNote: "परिणाम केवल OpenStreetMap से हैं; असत्यापित स्थान कभी सूचीबद्ध नहीं किए जाते। भेरोसे पहले स्थलीय परिस्थितियाँ पुष्टि करें।",
    useLocation: "मेरी वर्तमान स्थिति उपयोग करें",
    loadError: "शीतलन संसाधन खोज विफल। कृपया पुनः प्रयास करें।",
  },
  dashboard: {
    overline: "पर्यवेक्षक निगरानी",
    title: "समूह गर्मी-जोखिम अवलोकन",
    subtitle: "सभी कार्यस्थलों से प्रस्तुत कर्मचारी आकलनों का समग्र, निर्धारित दृश्य।",
    refresh: "ताज़ा करें",
    clear: "शिफ्ट रिकॉर्ड हटाएँ",
    clearConfirm: "इस शिफ्ट के सभी संग्रहीत आकलन सारांश हटाएँ?",
    cleared: "संग्रहीत आकलन सारांश हटाए गए।",
    total: "कुल आकलन",
    critical: "गंभीर सावधानी",
    heightened: "उच्च सावधानी",
    advisory: "सलाह",
    noneRisk: "कोई सावधानी संकेत नहीं",
    urgentHeading: "तत्काल ध्यान आवश्यक मामले",
    noUrgent: "वर्तमान समूह में कोई गंभीर-सावधानी मामला नहीं है।",
    locationsHeading: "साइट जोखिम हॉटस्पॉट",
    recentHeading: "हाल के आकलन",
    completenessHeading: "प्रोफ़ाइल पूर्णता",
    completeShare: "पूर्ण प्रोफ़ाइल",
    incomplete: "जानकारी रहित आकलन",
    worker: "कर्मचारी",
    locationCol: "स्थान",
    riskCol: "जोखिम स्तर",
    tempCol: "वायु ताप",
    timeCol: "प्रस्तुति समय",
    alertsCol: "चेतावनियाँ",
    assessmentsCol: "आकलन",
    worstCol: "सर्वोच्च जोखिम",
    maxTempCol: "अधिकतम ताप",
    empty: "अभी कोई आकलन दर्ज नहीं है। कर्मचारी आकलन जमा करते ही पर्यवेक्षक आँकड़े यहाँ दिखेंगे।",
    limitationsHeading: "व्याख्या सीमाएँ",
    loadError: "पर्यवेक्षक अवलोकन लोड नहीं हो सका।",
    unusable: "अनुपयोगी रिकॉर्ड बाहर",
  },
};

const gu: Strings = {
  brand: { name: "HeatShield", suffix: "AI" },
  nav: {
    workspace: "વર્કસ્પેસ",
    overview: "નિરીક્ષણ",
    newAssessment: "નવી જાંચ",
    assessments: "જાંચો",
    safetyGuidance: "સુરક્ષા માર્ગદર્શન",
    resources: "સંસાધનો",
    planned: "યોજિત",
    primaryNav: "મુખ્ય નેવિગેશન",
    openNav: "નેવિગેશન ખોલો",
    closeNav: "નેવિગેશન બંધ કરો",
  },
  source: { label: "ડેટા સ્રોત", name: "Open-Meteo", note: "પર્યાવરણીય નિરીક્ષણો કાર્યસ્થળ માપ નથી." },
  topbar: { observationsAvailable: "નિરીક્ષણો ઉપલબ્ધ છે" },
  heading: {
    overline: "જલવાયુ સંચાલન / નિરીક્ષણ",
    title: "કામદાર ગરમી સુરક્ષા",
    subtitle: "વર્તમાન સ્થિતિઓ, અનુભવેલ સંપર્ક અને આગળના વ્યાવહારિક પગલાંને સમજો.",
    newAssessment: "નવી જાંચ",
  },
  env: { overline: "પર્યાવરણીય સ્થિતિઓ", title: "વર્તમાન નિરીક્ષણો", observed: "નિરીક્ષિત" },
  metrics: {
    airTemp: "હવાનું તાપમાન",
    humidity: "સાપેક્ષ ભેજ",
    apparentTemp: "આભાસી તાપમાન",
    wind: "હવાની ગતિ",
    currentObs: "વર્તમાન નિરીક્ષણ",
    notWbgt: "માપેલું WBGT નથી",
  },
  status: {
    overline: "જાંચ સ્થિતિ",
    ready: "જાંચ માટે તૈયાર",
    completedCopy: "પર્યાવરણીય નિરીક્ષણો અને આપેલી કામદાર પ્રોફાઇલમાંથી જાંચ પૂર્ણ થઈ.",
    readyCopy: "પારદર્શી ગરમી-સંપર્ક જાંચ બનાવવા કામદાર પ્રોફાઇલ પૂર્ણ કરો.",
    infoToCollect: "એકત્ર કરવા યોગ્ય માહિતી",
    readyForInput: "ઇનપુટ માટે તૈયાર",
    noAssessment: "હજુ સુધી કોઈ જાંચ સબમિટ થઈ નથી.",
  },
  latest: {
    overline: "નવીનતમ કામદાર જાંચ",
    noAssessment: "હજુ કોઈ જાંચ નથી",
    copy: "જાંચ પછી આપેલી કાર્ય સ્થિતિઓ અહીં સારાંશિત થશે.",
    workload: "કાર્યભાર",
    sunlight: "સીધી ધાબો",
    shade: "છાયા",
    water: "પાણી ઉપલબ્ધતા",
  },
  display: { yes: "હા", no: "ના", notProvided: "આપેલ નથી", noneReported: "કંઈ જણાવ્યું નથી" },
  enums: {
    workload: { light: "હળવું", moderate: "મધ્યમ", heavy: "ભારે", very_heavy: "ખૂબ ભારે", unknown: "અજ્ઞાત" },
    shade: { full: "પૂર્ણ", partial: "આંશિક", none: "કોઈ નહીં", unknown: "અજ્ઞાત" },
    acclimatization: { acclimatized: "ટેવાયેલ", not_acclimatized: "ટેવાયેલ નહીં", unknown: "અજ્ઞાત" },
    assessmentStatus: {
      screening_only: "માત્ર જાંચ",
      incomplete: "અપૂર્ણ",
      wbgt_requires_professional_review: "વ્યવસાયી સમીક્ષા જરૂરી",
    },
    missingInfo: {
      continuous_exposure_minutes: "સળંગ સંપર્ક મિનિટ",
      break_frequency_minutes: "વિરામ વારંવારતા મિનિટ",
      work_area: "કાર્ય વિસ્તાર",
      shade_availability: "છાયા ઉપલબ્ધતા",
      acclimatization: "ટેકાવવાનું",
      workload: "કાર્યભાર",
      temperature_c: "હવાનું તાપમાન",
      humidity_percent: "સાપેક્ષ ભેજ",
      wind_speed_kmh: "હવાની ગતિ",
    },
    priority: {
      advisory: "સામાન્ય સાવધાની",
      heightened_precaution: "ઊંચી સાવધાની",
      critical_precaution: "ગંભીર સાવધાની",
      none: "કોઈ નહીં",
    },
  },
  form: {
    overline: "નવી જાંચ",
    title: "કામદાર અને કાર્યસ્થળ માહિતી",
    required: "* જરૂરી",
    worksite: "કાર્યસ્થળ",
    workerProfile: "કામદાર પ્રોફાઇલ",
    envExposure: "પર્યાવરણીય સંપર્ક",
    safetyProvisions: "સુરક્ષા વ્યવસ્થા",
    exposureRecovery: "સંપર્ક અને પુનઃપ્રાપ્તિ",
    location: "સ્થાન",
    locationPh: "શહેર કે કાર્યસ્થળ",
    workArea: "કાર્ય વિસ્તાર",
    workAreaPh: "કાર્યસ્થળનું વર્ણન કરો",
    occupation: "વ્યવસાય",
    shiftHours: "પાળી અવધિ (કલાક)",
    workload: "કાર્યભાર",
    acclimatization: "ટેકાવવાનું",
    directSunlight: "સીધી ધાબો",
    sunlightYes: "હા — સીધો સંપર્ક",
    sunlightNo: "સીધો સંપર્ક નથી",
    shadeAvailability: "છાયા ઉપલબ્ધતા",
    waterAccess: "પીવાના પાણીની ઉપલબ્ધતા",
    waterYes: "ઉપલબ્ધ",
    waterNo: "ઉપલબ્ધ નથી",
    ppeItems: "PPE વસ્તુઓ",
    ppePh: "વસ્તુઓને અલ્પવિરામથી અલગ કરો",
    continuousExposure: "સળંગ સંપર્ક (મિનિટ)",
    breakFrequency: "વિરામ વારંવારતા (મિનિટ)",
    optionalPh: "વૈકલ્પિક",
    runAssessment: "ગરમી જાંચ ચલાવો",
    analyzing: "સ્થિતિઓનું વિશ્લેષણ થઈ રહ્યું છે...",
    errorConnect: "HeatShield API સાથે જોડાવા અસમર્થ.",
    errorDefault: "જાંચ પૂર્ણ થઈ શકી નહીં.",
  },
  context: {
    overline: "જાંચ સંદર્ભ",
    title: "તમને શું મળશે",
    envObs: "પર્યાવરણીય નિરીક્ષણો",
    envObsDesc: "Open-Meteo માંથી વર્તમાન તાપમાન, ભેજ, આભાસી તાપમાન અને હવા.",
    exposureFactors: "સંપર્ક પરિબાળ",
    exposureFactorsDesc: "આપેલી કાર્ય સ્થિતિઓ અને ગુમ માહિતીનો પારદર્શી સારાંશ.",
    practicalControls: "વ્યાવહારિક નિયંત્રણો",
    practicalControlsDesc: "જાંચ પર આધારિત સુરક્ષા માર્ગદર્શન, તેની મર્યાદાઓ સ્પષ્ટ રીતે જણાવેલ.",
    disclaimer: "આભાસી તાપમાન WBGT નથી. આ સાધન જાંચ સહાય આપે છે, તબીબી નિદાન કે કાર્યસ્થળ માપ નથી.",
  },
  alerts: {
    overline: "સક્રિય સાવધાની અલર્ટ",
    title: "સુરક્ષા અલર્ટ",
    emergencyHeading: "જરૂરી હોય તો કટોકટો તબીબી સહાય લો",
    viewLimitations: "અલર્ટ મર્યાદાઓ જુઓ",
  },
  output: {
    overline: "જાંચ પરિણામ",
    title: "આગળનું પગલું",
    screeningOnly: "માત્ર જાંચ",
    advisoryOverline: "સુરક્ષા સલાહ",
    advisoryTitle: "અનુશંસિત માર્ગદર્શન",
    advisoryFallback: "કોઈ સલાહ મળી નથી.",
    missingOverline: "અપૂર્ણ માહિતી",
    itemsToCollect: "{count} માહિતી એકત્ર કરવાની",
    profileComplete: "પ્રોફાઇલ પૂર્ણ",
    allFieldsSupplied: "બધા અનુસરણ કરેલ કામદાર પ્રોફાઇલ ક્ષેત્ર આપેલ હતા.",
    viewLimitations: "જાંચ મર્યાદાઓ જુઓ",
  },
  footer: {
    label: "સુરક્ષા નોંધ:",
    note: "જો કોઈને ગૂંચવાઈ જવું, ઝાંપા આવવા, પડી જવું અથવા મૂર્છા આવવા જેવા લક્ષણો દેખાય, તો તાત્કાલિક કટોકટો તબીબી સહાય લો. AI મૂલ્યાંકન માટે વિલંબ ન કરો.",
  },
  langSwitch: { label: "ભાષા" },
  guidance: {
    overline: "ચકાસાયેલ સુરક્ષા જ્ઞાન",
    title: "વ્યવસાયિક ગરમી-સુરક્ષા માર્ગદર્શન",
    subtitle: "OSHA / NIOSH / CDC સ્રોતોથી સમીક્ષાયેલ પસંદગીયુત માર્ગદર્શન. દરેક વિષય ચકાસાયેલ અને સંદર્ભિત છે.",
    searchPh: "વિષય શોધો, જેમ કે પાણી પીવું, WBGT, અનુકૂલન",
    searchBtn: "શોધો",
    validated: "ચકાસાયેલ",
    reviewed: "સમીક્ષાયેલ",
    sources: "સ્રોતો",
    guidanceHeading: "માર્ગદર્શન",
    noResults: "કોઈ મેળ ખાતું વિષય મળ્યું નથી. બીજો શબ્દ અજમાવો અથવા બધા વિષય જુઓ.",
    resultsCount: "{count} વિષય મળ્યા",
    kbVersion: "જ્ઞાન-આધાર આવૃત્તિ",
    integrityOk: "બધા વિષય ચકાસાયેલ અને સંદર્ભિત",
    browseAll: "બધા વિષય જુઓ",
    backToList: "વિષય યાદી પર પાછા",
    category: "શ્રેણી",
    loadError: "સુરક્ષા માર્ગદર્શન લોડ થઈ શક્યું નથી. API કનેક્શન તપાસો.",
  },
  resources: {
    overline: "શીતલિકા સંસાધન શોધ",
    title: "કાર્યસ્થલ નજીક શીતલિકા સંસાધનો શોધો",
    subtitle: "OpenStreetMap થી જાહેરપક્ષે નકશાંકિત પીવાનું પાણી, આશ્રયસ્થાનો, इनडोर આશરો અને છાયાદાર સ્થળો.",
    lat: "કાર્યસ્થલ અક્ષાંશ",
    lng: "કાર્યસ્થલ રેખાંશ",
    radius: "શોધ ત્રિજ્યા",
    radiusUnit: "મી",
    categories: "શ્રેણીઓ",
    catWater: "પીવાનું પાણી",
    catShelter: "શીતલિકા આશ્રયસ્થાનો",
    catRefuge: "इनडोर આશરો",
    catShade: "છાયાદાર સ્થળો",
    findBtn: "સંસાધનો શોધો",
    searching: "નકશો ડેટા શોધાઈ રહ્યો છે...",
    found: "{count} સંસાધનો મળ્યાં",
    noneFound: "આ ત્રિજ્યામાં કોઈ નકશાંકિત શીતલિકા સંસાધન મળ્યું નથી. ત્રિજ્યા વધારો અથવા યામ તપાસો.",
    distance: "અંતર",
    sourceLink: "OpenStreetMap પર જુઓ",
    osmNote: "પરિણામો ફક્ત OpenStreetMap થી છે; અસત્યાપિત સ્થળો ક્યારેય સૂચિબદ્ધ થતા નથી. ભરોસો કરતાં પહેલાં સ્થળ પરની પરિસ્થિતિ ચકાસો.",
    useLocation: "મારી વર્તમાન સ્થિતિ વાપરો",
    loadError: "શીતલિકા સંસાધન શોધ નિષ્ફળ. કૃપા કરીને ફરી પ્રયાસ કરો.",
  },
  dashboard: {
    overline: "સુપરવઝર નિરીક્ષણ",
    title: "સમૂહ ગરમી-જોખમ ઝલક",
    subtitle: "બધા કાર્યસ્થલો પરથી સબમિટ કરેલ કામદાર મૂલ્યાંકનોનું સમગ્ર, નિર્ધારિત દૃશ્ય.",
    refresh: "તાજું કરો",
    clear: "શિફ્ટ રેકોર્ડ સાફ કરો",
    clearConfirm: "આ શિફ્ટના સંગ્રહિત બધા મૂલ્યાંકન સારાંશ સાફ કરવા?",
    cleared: "સંગ્રહિત મૂલ્યાંકન સારાંશ સાફ થયા.",
    total: "કુલ મૂલ્યાંકનો",
    critical: "ગંભીર સાવધાની",
    heightened: "વધેલી સાવધાની",
    advisory: "સલાહ",
    noneRisk: "કોઈ સાવધાની સંકેત નથી",
    urgentHeading: "તાત્કાલિક ધ્યાન જરૂરી કિસ્સા",
    noUrgent: "વર્તમાન સમૂહમાં કોઈ ગંભીર-સાવધાની કિસ્સો નથી.",
    locationsHeading: "સાઇટ જોખમ હોટસ્પોટ",
    recentHeading: "તાજેતરના મૂલ્યાંકનો",
    completenessHeading: "પ્રોફાઇલ પૂર્ણતા",
    completeShare: "પૂર્ણ પ્રોફાઇલ",
    incomplete: "માહિતી રહિત મૂલ્યાંકનો",
    worker: "કામદાર",
    locationCol: "સ્થળ",
    riskCol: "જોખમ સ્તર",
    tempCol: "હવાનું તાપમાન",
    timeCol: "સબમિટ સમય",
    alertsCol: "એલર્ટ",
    assessmentsCol: "મૂલ્યાંકનો",
    worstCol: "સર્વોચ્ચ જોખમ",
    maxTempCol: "મહત્તમ તાપમાન",
    empty: "હજી કોઈ મૂલ્યાંકન નจด્જ થયું નથી. કામદારો મૂલ્યાંકન સબમિટ કરે એટલે સુપરવઝર આંકડા અહીં દેખાશે.",
    limitationsHeading: "અર્ઘઘટન મર્યાદાઓ",
    loadError: "સુપરવઝર ઝલક લોડ થઈ શકી નથી.",
    unusable: "અનુપયોગી રેકોર્ડ બાદ",
  },
};

export const translations: Record<Lang, Strings> = { en, hi, gu };
