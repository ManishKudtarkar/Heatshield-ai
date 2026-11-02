# 🔥 HeatShield AI
### Intelligence Against Extreme Heat. Protection for Every Worker.

**An AI-powered, multi-agent climate safety and early-warning platform designed to protect outdoor workers from extreme heat exposure.**

[![Python](https://img.shields.io/badge/Python-3.14-blue?logo=python)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-15-black?logo=next.js)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![AWS](https://img.shields.io/badge/AWS-Amazon%20Bedrock-FF9900?logo=amazonaws)](https://aws.amazon.com/bedrock/)
[![Strands Agents](https://img.shields.io/badge/AI-Strands%20Agents-orange)](https://strandsagents.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🌍 The Problem

Extreme heat is an increasing occupational safety challenge, particularly for people whose jobs require them to work outdoors.

Construction workers, delivery personnel, agricultural labourers, sanitation workers, street vendors and traffic police often have limited control over their exposure to environmental heat.

Traditional weather applications provide general weather information, but they do not account for individual workplace exposure factors such as:

- Physical workload and activity intensity.
- Direct sunlight and solar radiation.
- Availability of shade and cooling facilities.
- Access to drinking water.
- Acclimatization to heat.
- Protective clothing and personal protective equipment (PPE).
- Continuous exposure duration and recovery breaks.

**Weather information alone is not an occupational heat-risk assessment.**

There is a need to connect environmental intelligence with worker-specific information and practical safety guidance.

## 💡 Our Solution

HeatShield AI transforms environmental weather information and worker exposure profiles into structured, actionable safety intelligence.

It uses a coordinated multi-agent architecture powered by **AWS Strands Agents and Amazon Bedrock**.

The platform:

1. Retrieves environmental weather observations.
2. Analyzes environmental conditions using an AI agent.
3. Validates worker exposure information.
4. Evaluates exposure factors through a deterministic assessment engine.
5. Generates contextual safety recommendations.
6. Identifies missing information that may affect the assessment.

Our initial focus is outdoor workers in Gujarat, India, with the architecture designed for broader deployment.

## ✨ Key Features

### 🌡️ Climate Intelligence
- Real-time environmental weather retrieval through Open-Meteo.
- Temperature, relative humidity and apparent temperature.
- Wind speed and precipitation observations.
- Hourly weather forecast interpretation.
- Environmental data-quality information.

### 👷 Worker Exposure Intelligence
- Worker occupation and physical workload.
- Direct sunlight exposure.
- Shade availability.
- Drinking water access.
- Heat acclimatization status.
- PPE information.
- Continuous exposure duration.
- Recovery-break information.

### 🤖 Multi-Agent AI System
- Climate Intelligence Agent.
- Worker Exposure Intelligence Agent.
- Safety Advisory Agent.
- Central orchestration system.
- Deterministic assessment engine.

### 🛡️ Safety Advisory
- Contextual preventive recommendations.
- Worker and supervisor guidance.
- Identification of missing information.
- Explicit assessment limitations.
- Occupational safety considerations.

### 📊 Dashboard
- Climate intelligence visualization.
- Worker exposure assessment.
- AI-generated safety recommendations.
- Responsive worker assessment form.
- Structured deterministic assessment details.

### 🌐 Multilingual Worker Interface
- English, Hindi and Gujarati interface support.
- Localized precautionary alerts in the worker's preferred language.
- Language discovery endpoint for client applications.

### 📚 Validated Occupational Safety Knowledge Base
- Curated occupational heat-safety guidance with explicit provenance.
- Deterministic retrieval that grounds advisory agents.
- Precautions and controls only — no risk scores or medical diagnosis.

### 🧊 Cooling Resource Discovery
- Nearby shaded rest points, drinking-water stations and public shelters.
- Powered by OpenStreetMap data with verifiable resource provenance.
- Explicit limitations since remote availability cannot be confirmed.

### 👔 Supervisor Monitoring Dashboard
- Aggregated team-wide precaution levels from recent assessments.
- Attention items for critical precautions and missing information.
- Coverage-gap visibility such as water access and shade availability.
- Screening summaries only — no personal medical records.

### 🚨 Proactive Safety Alerts
- Deterministic, evidence-grounded precautionary alerts.
- Each alert lists the specific observations that triggered it.
- Emergency guidance surfaced alongside critical-precaution alerts.

---

## 🏗️ System Architecture

```text
                     HEATSHIELD AI
                           |
                           v
                    Next.js Frontend
                           |
                           v
                    FastAPI Backend
                           |
                           v
                  STRANDS ORCHESTRATOR
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
     CLIMATE AGENT    EXPOSURE AGENT    SAFETY AGENT
          |                |                ^
          v                v                |
     Open-Meteo       Worker Profile        |
          |                |                |
          +----------------+                |
                           |                |
                           v                |
                DETERMINISTIC ENGINE        |
                           |                |
                           v                |
                STRUCTURED ASSESSMENT       |
                           |                |
                           +----------------+
                           |
                           v
                  SAFETY RECOMMENDATIONS
                           |
                           v
                     API RESPONSE
                           |
                           v
                    USER DASHBOARD
```

### Agent Responsibilities

| Component | Responsibility |
|---|---|
| Climate Intelligence Agent | Interprets environmental weather observations and hourly forecasts. |
| Worker Exposure Agent | Analyzes validated worker profiles and exposure factors. |
| Deterministic Assessment Engine | Evaluates structured weather and worker information using Python logic. |
| Safety Advisory Agent | Generates contextual preventive guidance from assessment results. |
| Orchestrator | Coordinates execution and checks consistency between assessment components. |

The deterministic engine provides structured evaluation independently of LLM-generated interpretations.

---

## 🧰 Technology Stack

| Category | Technology |
|---|---|
| Frontend | Next.js, TypeScript |
| Styling | Tailwind CSS |
| UI Icons | Lucide React |
| Data Visualization | Recharts |
| Backend | Python, FastAPI |
| AI Framework | Strands Agents SDK |
| Foundation Model | Amazon Bedrock Nova Lite |
| Weather Data | Open-Meteo API |
| Data Validation | Pydantic |
| HTTP Client | HTTPX |
| Cloud Platform | Amazon Web Services |
| Cloud Region | Asia Pacific (Mumbai) — `ap-south-1` |

---

## 📁 Project Structure

```text
heatshield-ai/
│
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   ├── climate_agent.py
│   │   │   ├── exposure_agent.py
│   │   │   ├── safety_agent.py
│   │   │   └── orchestrator.py
│   │   │
│   │   ├── engine/
│   │   │   └── heat_assessment.py
│   │   │
│   │   ├── schemas/
│   │   │   └── worker.py
│   │   │
│   │   ├── tools/
│   │   │   ├── weather_tool.py
│   │   │   └── exposure_tool.py
│   │   │
│   │   ├── api.py
│   │   └── first_agent.py
│   │
│   └── .env.example
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   └── app/
│   │       ├── page.tsx
│   │       ├── globals.css
│   │       └── layout.tsx
│   └── package.json
│
├── demo/
│
├── docs/
│
├── infrastructure/
│
├── .gitignore
├── LICENSE
└── README.md
```

*The frontend and infrastructure directories are being developed incrementally.*

---

## 🚀 Getting Started

### Prerequisites

Make sure you have:

- Python 3.14 or a compatible Python version.
- Node.js 24 or a compatible supported version.
- npm.
- AWS CLI.
- An AWS account with Amazon Bedrock model access.
- Git.

### 1. Clone the Repository

```bash
git clone https://github.com/ManishKudtarkar/Heatshield-ai.git

cd heatshield-ai
```

### 2. Configure AWS Credentials

Configure your AWS credentials:

```bash
aws configure
```

Set your AWS region:

```bash
aws configure set region ap-south-1
```

Verify your identity:

```bash
aws sts get-caller-identity
```

Ensure your IAM identity has permission to invoke the selected Amazon Bedrock model or inference profile.

### 3. Set Up the Backend

```bash
cd backend
```

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate it:

**Linux/macOS**

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install strands-agents boto3 fastapi uvicorn httpx pydantic-settings
```

### 4. Configure Environment Variables

Create a `.env` file if additional application configuration is required.

Example:

```env
AWS_REGION=ap-south-1
BEDROCK_MODEL_ID=apac.amazon.nova-lite-v1:0
```

Do not commit AWS credentials, access keys, secrets or personal tokens to GitHub.

The application uses your configured AWS credential chain.

### 5. Test the AI Agent

```bash
python3 -m app.first_agent
```

### 6. Run Individual Agents

Climate Agent:

```bash
python3 -m app.agents.climate_agent
```

Worker Exposure Agent:

```bash
python3 -m app.agents.exposure_agent
```

Deterministic Assessment:

```bash
python3 -m app.test_exposure_tool
```

Run the complete multi-agent pipeline:

```bash
python3 -m app.agents.orchestrator
```

### 7. Start the FastAPI Server

```bash
uvicorn app.api:app --reload --host 127.0.0.1 --port 8000
```

The backend will be available at:

| Endpoint | Description |
|---|---|
| `GET /` | API information |
| `GET /health` | Health check |
| `POST /api/v1/assess` | Execute complete assessment |
| `GET /api/v1/languages` | Supported interface languages |
| `GET /api/v1/cooling-resources` | Discover cooling resources near a location |
| `GET /api/v1/supervisor/dashboard` | Aggregated supervisor monitoring view |
| `GET /docs` | Interactive Swagger documentation |

### 8. Start the Frontend Dashboard

Open a second terminal from the repository root:

```bash
cd frontend
npm ci
npm run dev
```

The dashboard will be available at [http://localhost:3000](http://localhost:3000).
It sends assessments to `http://127.0.0.1:8000` by default. To use a different
backend URL, create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

The backend allows the local Next.js development origins
(`localhost:3000` and `127.0.0.1:3000`). Update the CORS configuration in
`backend/app/api.py` before deploying the frontend and backend on different
origins.

---

## 🔌 API Usage

### Create a Worker Assessment

**Endpoint**

```http
POST /api/v1/assess
```

**Request Body**

```json
{
  "location": "Vadodara",
  "worker": {
    "occupation": "Construction worker",
    "workload": "heavy",
    "shift_hours": 8,
    "direct_sunlight": true,
    "shade_availability": "partial",
    "water_access": true,
    "acclimatization": "not_acclimatized",
    "ppe_items": [
      "Safety helmet",
      "Safety boots",
      "Protective clothing"
    ],
    "continuous_exposure_minutes": 120,
    "break_frequency_minutes": null,
    "work_area": "Outdoor construction site, Vadodara"
  }
}
```

**Example Response Structure**

```json
{
  "success": true,
  "result": {
    "success": true,
    "project": "HeatShield AI",
    "location": "Vadodara",
    "climate_analysis": "...",
    "worker_exposure_analysis": "...",
    "validated_exposure_data": {},
    "deterministic_assessment": {},
    "safety_advisory": "..."
  }
}
```

The actual response includes structured weather observations, worker exposure information, assessment limitations and safety recommendations.

---

## 🔬 Safety and Responsible AI

Worker safety is the central design principle of HeatShield AI.

We follow these principles:

**1. No fabricated environmental data**

Weather observations are retrieved from the configured weather provider.

**2. No unsupported occupational risk scores**

The system does not invent numerical risk scores or occupational risk categories.

**3. Apparent temperature is not WBGT**

Apparent temperature and Wet Bulb Globe Temperature represent different measurements. They must not be treated as interchangeable.

**4. Environmental observations are not worksite measurements**

Weather-station data may differ from actual workplace conditions.

**5. No medical diagnosis**

HeatShield AI is an informational screening and safety-support platform, not a medical diagnostic system.

**6. Missing information is explicitly identified**

Incomplete worker information must be communicated rather than silently assumed.

**7. Emergency situations require immediate action**

Suspected heatstroke symptoms, including confusion, seizures, collapse or loss of consciousness, require immediate emergency medical assistance.

---

## 📚 Safety and Research References

- [OSHA — Heat Exposure](https://www.osha.gov/heat-exposure)
- [NIOSH — Criteria for a Recommended Standard: Occupational Exposure to Heat and Hot Environments](https://www.cdc.gov/niosh/docs/2016-106/)
- [India Meteorological Department](https://mausam.imd.gov.in/)
- [Open-Meteo Weather API](https://open-meteo.com/en/docs)
- [Strands Agents Documentation](https://strandsagents.com/)
- [Amazon Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)

---

## 🗺️ Development Roadmap

- [x] Initial project architecture.
- [x] Amazon Bedrock integration.
- [x] Strands Agents SDK integration.
- [x] Climate Intelligence Agent.
- [x] Worker Exposure Agent.
- [x] Deterministic Heat Assessment Engine.
- [x] Safety Advisory Agent.
- [x] Multi-agent orchestration.
- [x] Open-Meteo integration.
- [x] FastAPI backend.
- [x] Health check and API endpoints.
- [x] Successful end-to-end API assessment.
- [x] Responsive frontend assessment dashboard.
- [x] Frontend-to-backend assessment integration.
- [x] Multilingual worker interface.
- [x] Validated occupational safety knowledge base.
- [x] Cooling resource discovery.
- [x] Supervisor monitoring dashboard.
- [x] Proactive safety alerts.
- [ ] AWS production deployment.

---

## 🌱 Our Vision

We believe access to occupational heat-safety intelligence should not be limited to large organizations with advanced monitoring infrastructure.

HeatShield AI aims to make environmental intelligence more accessible, actionable and understandable for the people who need it most.

**Because workers should not have to choose between earning a living and protecting their health.**

---

## 👨‍💻 Project

**HeatShield AI**

*Intelligence Against Extreme Heat. Protection for Every Worker.*

Built using AWS Strands Agents, Amazon Bedrock and Python.

---

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for details.