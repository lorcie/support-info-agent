# support-info-agent for DevPost AI Partner Innovation Hackathon

[Google Cloud Run Hosted Project url: https://support-info-agent-frontend-service-457744507163.us-central1.run.app/](https://support-info-agent-frontend-service-457744507163.us-central1.run.app/) 

|           |                                                |
| --------- | ---------------------------------------------- |
| Author(s) | [Adrien Chan](https://github.com/lorcie/support-info-agent) |

# Table of contents
1. [Introduction](#introduction)
4. [Usage](#usage)
5. [Support Info Agent Development](#support-info-agent-development)
6. [Support Info Agent Executions](#support-info-agent-executions)
7. [Codeset Files](#codeset-files)
8. [Application Modules Deploy on Cloud Run](#application-modules-deploy-cloud-run)
9. [Take Away](#take-away)

## Introduction <a name="introduction"></a>

This project proposes to enhance agentic AI based support info with better accessibility thanks to audio text to speech synthesis.

It enables end users to customize Voice Character and Settings and provide audio listening of AI agent responses  powered by **Google Agent Development Kit ADK** Python Application with **ElevenLabs API** call.

The Support Info Agent service has been developed with **Python** language/ecosystem and deployed/operated with Google Cloud technologies (more details on architecture below) :
- **Google Cloud Run** services : mcp toolbox database, mcp amadeus airflight, airflight adk agent, frontend, backend
- **Google Cloud Shell** for easy staging test and debugging before deployment
- **Google Container Registry** hosting docker container images
- **ElevenLabs API** to convert text to speech in **MP3** format

Following Additional modules have been also used :
- **Streamlit** for the frontend web interface

More details about Architecture, Usage and Screenshots (executions, codesets samples) are presented below.

Instructions to Build Docker containers Stored on **Cloud Container Registry** and Deployment either from source either from images on Google Cloud Technologies : **Cloud Run**, Cloud Logging,...) are described below.

## Usage <a name="usage"></a>

On the Support INfo Agent Streamlit Web UI application, you can use the following queries to test various use cases:

1. what is the weather in New York >
return New York weather forecast and provide audio link to launch listening

2. say out loud the forecasted weather in New York >
return New York weather forecast and provide audio link to launch listening


## Support Info Agent Development <a name="support-info-agent-development"></a>

Global Architecture >

![Support Info Agent Global Architecture](https://github.com/lorcie/support-info-agent/blob/master/assets/architecture-elevenlabs.png?raw=true)


## Support Info Agent Executions <a name="support-info-agent-executions"></a>

Conversation >

![Support Info Agent Conversation](https://github.com/lorcie/support-info-agent/blob/master/assets/support-info-agent-frontend-conversation-remote.png?raw=true)


Frontend User Interface ElevenLabs Voice Character / Settings >

![Support Info Agent ElevenLabs Voice Character and Settings](https://github.com/lorcie/support-info-agent/blob/master/assets/support-info-agent-frontend-voice-character-settings.png?raw=true)


Audio Files Google Cloud Bucket >

![Support Info Agent Audio Files Bucket](https://github.com/lorcie/support-info-agent/blob/master/assets/support-info-agent-google-cloud-storage-audio-bucket.png?raw=true)

## Codeset Files <a name="codeset-files"></a>

Application Python Codeset >

![Support Info Agent Codeset](https://github.com/lorcie/support-info-agent/blob/master/assets/support-info-agent-codebase.png?raw=true)

## Application Modules Deploy on Cloud Run <a name="application-modules-deploy-cloud-run"></a>

### Support Info Agent FastApp backend python on Cloud Run Deployment

Go in support-info-agent subdirectory then run following commands on Cloud Shell

```shell
cd support-info-agent/

export REGION=YOUR_REGION
export PROJECT_ID=$(gcloud config get-value project)
export ELEVENLABS_API_KEY=YOUR_ELEVENLABS_API_KEY
export GOOGLE_API_KEY=YOUR_GOOGLE_API_KEY

export SA_NAME=support-info-agent-sa
export SERVICE_ACCOUNT="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

for Cloud Run Deployment, Google Cloud Storage bucket objects access requires to add special role with following command :

# add gcs role
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/storage.objectUser"

For local deployment, key generation and export in json format is necessary followed by environment export as follows :

export GOOGLE_APPLICATION_CREDENTIALS=YOUR_GOOGLE_CLOUD_STORAGE_BUCKET_OBJECT_ROLE_KEY.json

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

## Take Away <a name="take-away"></a>

**ElevenLabs Voice AI** features enable to enhance interaction with end user through :
- its **ElevenLabs API service** access to convert content in audio

- and also to customize **ElevenLabs Voice effects** thanks to its available Character and various Settings (speed, style, boost,...)

**Google Cloud** technologies enable :

- easy deployment and management with **Google Cloud Run**

- audio data storage and sharing with **Google Cloud Storage Bucket**


