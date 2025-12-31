# Prerequisites: 
1. Install python
2. Have an IDE

Steps:
1. Set up the python environment

- Initialize .vnev `python -m venv .venv`/`python3 -m venv .venv`

- Activate virtual env

    - Activate (each new terminal)

    - macOS/Linux: source .venv/bin/activate

    - Windows CMD (Git Bash): source .venv/Scripts/activate

    - Windows PowerShell: .venv\Scripts\Activate.ps1


2. `pip install -r requirements.txt`/`pip3 install -r requirements.txt`

3. Have the following project structure
```
parent_folder/
    multi_tool_agent/
        __init__.py
        agent.py
        .env
```
4. Defined root agent and start integrating tools and services!
5. Run project with `adk web`



### Support Info Agent FastApp backend python on Cloud Run Deployment

Go in support-info-agent subdirectory then run following commands on Cloud Shell

```shell
cd support-info-agent/

export REGION=YOUR_REGION
export PROJECT_ID=$(gcloud config get-value project)
export ELEVENLABS_API_KEY=YOUR_ELEVENLABS_API_KEY
export GOOGLE_API_KEY=YOUR_GOOGLE_API_KEY

echo "cs-venv/" > .gcloudignore

gcloud run deploy support-info-agent-backend-service \
  --source . \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=${PROJECT_ID}" \
  --set-env-vars="GOOGLE_GENAI_USE_VERTEXAI=1" \
  --set-env-vars="ELEVENLABS_API_KEY=${ELEVENLABS_API_KEY}" \
  --set-env-vars="GOOGLE_API_KEY=${GOOGLE_API_KEY}" \
  --set-env-vars="AGENT_MODEL=${AGENT_MODEL}" \
  --set-env-vars="GOOGLE_CLOUD_LOCATION=${REGION}"
```

### Support Info Agent Frontend Streamlit app on Cloud Run Deployment

Go in subdirectory ./apps then run following commands on Cloud Shell

```shell
cd support-info-agent/apps

export REGION=YOUR_REGION
export PROJECT_ID=$(gcloud config get-value project)
export API_BASE_URL=YOUR_API_BASE_URL

echo ".venv/" > .gcloudignore

gcloud run deploy support-info-agent-frontend-service \
  --source . \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=${PROJECT_ID}" \
  --set-env-vars="API_BASE_URL=${API_BASE_URL}$" \
  --set-env-vars="AGENT_APP_NAME=multi_tools_agent" \
  --set-env-vars="GOOGLE_CLOUD_LOCATION=${REGION}"
```

