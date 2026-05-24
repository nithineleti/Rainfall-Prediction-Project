# AWS Deployment Guide: Dual-Stage Rainfall Prediction Pipeline

To deploy this project to AWS, we recommend using **AWS App Runner** (for the API) and **AWS Amplify** (for the Frontend). This is the fastest and most cost-effective way to get a public link.

## 1. Deploying the Backend API (AWS App Runner)

AWS App Runner is the easiest way to deploy Python/FastAPI apps.

1.  **Connect GitHub**: Log in to [AWS App Runner Console](https://console.aws.amazon.com/apprunner/).
2.  **Create Service**:
    *   **Repository Type**: Source code repository.
    *   **GitHub**: Select your `Rainfall-Prediction-Project` repo.
    *   **Branch**: `main`.
3.  **Configure Build**:
    *   **Runtime**: `Python 3`.
    *   **Build Command**: `pip install -r requirements.txt`.
    *   **Start Command**: `python -m uvicorn main_api:app --host 0.0.0.0 --port 8000`.
    *   **Port**: `8000`.
4.  **Service Settings**:
    *   Set Environment Variable: `PYTHONPATH=.`.
5.  **Deploy**: AWS will provide a link like `https://xxxxxx.aws-region.awsapprunner.com`.

## 2. Deploying the Frontend (AWS Amplify)

1.  **Log in**: Go to [AWS Amplify Console](https://console.aws.amazon.com/amplify/).
2.  **New App**: Select **Host web app**.
3.  **Connect GitHub**: Select your `Rainfall-Prediction-Project` repo.
4.  **Configure Framework**:
    *   Select the `up-weather-intelligence-system` folder.
    *   Amplify will auto-detect **Vite**.
5.  **Environment Variables**:
    *   Add `VITE_API_URL`: (Paste your App Runner link from Step 1 here).
6.  **Save and Deploy**: AWS will provide your final public link!

---

### Project Files Prepared for AWS:
*   `Dockerfile`: Added for container-based deployments (ECS/EKS).
*   `requirements.txt`: Updated with deployment servers.
*   `.gitignore`: Configured to protect sensitive AWS keys.
