# ✈️ Travel Concierge Agent

An intelligent, multi-tool AI Travel Concierge built with the **Google Agent Development Kit (ADK)**. This agent provides personalized travel recommendations, queries live weather and exchange rates, searches nearby places using Google Maps APIs, generates AI travel photography and video previews, and maintains long-term user preferences across sessions.

![Travel Concierge Demo](./demo.gif)

---

## 🚀 Implemented Capabilities & Architecture

The agent is built using **Python**, **Google ADK (acli 1.1.0)**, **FastAPI**, and **A2UI v0.8**. It integrates directly with the following Google Cloud services and APIs:

### 1. 🌐 Google Cloud & Generative AI Integration
- **Vertex AI Gemini Models**: Uses `gemini-2.5-flash` as the core reasoning engine.
- **Vertex AI Memory Bank (`VertexAiMemoryBankService`)**: Persists long-term user facts and travel preferences across chat sessions via `PreloadMemoryTool` and automated memory-generation callbacks.
- **Gemini AI Image Generation**: Generates high-quality travel destination photos on-demand using `gemini-3.1-flash-lite-image` in the `global` region.
- **Gemini Omni Video Generation**: Generates short video clips using `gemini-omni-flash-preview` in the `global` region.
- **Google Cloud Storage (GCS)**: Automatically uploads generated images and videos to a public GCS bucket (`travel-concierge-media-*`) and returns public HTTPS media URLs.
- **Google Cloud Firestore**: Persists curated destination catalogs, tags, ratings, and descriptions with real-time stream queries.
- **Agent Engine Sandbox**: Safe Python code execution environment (`AgentEngineSandboxCodeExecutor`) for calculations and data transformation.

### 2. 🧰 Domain Tools & External APIs
- **Firestore Travel Database**: `list_destinations`, `get_destination_details`, and `save_destination` for catalog management and tag filtering (`culture`, `food`, `nature`, `beach`).
- **Live Real-time Weather**: `fetch_weather` using Open-Meteo geocoding and forecast APIs (current temperature, condition, and wind speed).
- **Currency Converter**: `convert_currency` via Frankfurter exchange rate API for real-time currency conversions.
- **Google Maps & Places API**: `geocode_address` and `find_nearby_places` for place discovery and location lookup.
- **AI Media Generation**: `generate_destination_image` and `generate_destination_video` with dual saving to ADK Playground Artifacts (`tool_context.save_artifact`) and Cloud Storage.

### 3. 🎨 Rich A2UI Card UI & Custom Web Frontend
- **A2UI Protocol (v0.8)**: Formats agent responses into structured UI components (`Card`, `Column`, `Row`, `Image`, `Text`, `Icon`) via an `after_model_callback`.
- **FastAPI A2A Proxy**: Lightweight backend proxy (`frontend/main.py`) translating browser chat requests to the Agent Runtime using the Agent-to-Agent (A2A) protocol.
- **Modern Chat Frontend**: Responsive single-page web UI (`frontend/static/index.html`) featuring prompt suggestion chips, dialogue styling, and an inline A2UI renderer.

---

## 📂 Project Structure

```text
.
├── agents-cli-manifest.yaml   # Agent CLI deployment manifest (ADK 1.1.0)
├── app/
│   ├── __init__.py
│   ├── agent.py               # Core ADK agent, tools, Firestore, Memory Bank & Gemini setup
│   └── a2ui_utils.py          # A2UI schema manager & callback transformer
├── frontend/
│   ├── main.py                # FastAPI proxy server (A2A protocol client)
│   ├── static/
│   │   └── index.html         # Travel-themed Chat UI & A2UI card renderer
│   ├── pyproject.toml         # Frontend dependencies
│   └── Dockerfile             # Container configuration for Cloud Run
├── demo.gif                   # Recorded video demo GIF
├── record_demo.py             # Automated Playwright demo recording script
└── generate_lofi.py           # Lo-fi soundtrack synthesis script
```

---

## 🛠️ Setup & Local Execution Instructions

### Prerequisites
- Python 3.11+
- Google Cloud SDK (`gcloud`) authenticated to your GCP project
- `agents-cli` (ADK 1.1.0)

### 1. Environment Configuration
Set your GCP Project ID:
```bash
export GOOGLE_CLOUD_PROJECT="qwiklabs-gcp-02-9a8f822bd17b"
export GOOGLE_MAPS_API_KEY=<YOUR_MAPS_API_KEY>
```

### 2. Run the ADK Agent Locally (Dev Server)
To start the local ADK developer playground:
```bash
cd travel-concierge
agents-cli web --port 8000
```

### 3. Run the Custom Web Frontend Locally
Install dependencies and launch the FastAPI proxy server:
```bash
cd travel-concierge/frontend
uv pip install -r pyproject.toml
export AGENT_ENGINE_RESOURCE_NAME="projects/<PROJECT_NUMBER>/locations/us-east1/reasoningEngines/<ENGINE_ID>"
export AGENT_DIRECTORY="app"
uv run python main.py
```
Open your browser to the local server address output by FastAPI (typically port 8080).

---

## ☁️ Deployment Instructions

### 1. Deploy Agent to Agent Runtime (Agent Engine)
```bash
agents-cli deploy --update-env-vars GOOGLE_MAPS_API_KEY=$GOOGLE_MAPS_API_KEY
```

### 2. Grant Required IAM Roles to Agent Service Account
```bash
gcloud projects add-iam-policy-binding qwiklabs-gcp-02-9a8f822bd17b \
  --member="serviceAccount:service-<PROJECT_NUMBER>@gcp-sa-aiplatform.iam.gserviceaccount.com" \
  --role="roles/datastore.user"

gcloud storage buckets add-iam-policy-binding gs://travel-concierge-media-qwiklabs-gcp-02-9a8f822bd17b \
  --member="serviceAccount:service-<PROJECT_NUMBER>@gcp-sa-aiplatform.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"
```

### 3. Deploy Frontend to Cloud Run
```bash
cd travel-concierge/frontend
gcloud run deploy travel-concierge-frontend \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars AGENT_ENGINE_RESOURCE_NAME="projects/<PROJECT_NUMBER>/locations/us-east1/reasoningEngines/<ENGINE_ID>",AGENT_DIRECTORY="app"
```

---

## 🔮 Planned / Future Enhancements

- **Unimplemented**: Vertex AI RAG Engine document retrieval (currently retrieval is handled via Firestore and real-time APIs).
