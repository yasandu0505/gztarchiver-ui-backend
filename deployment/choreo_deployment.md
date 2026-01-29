# Deployment Guide: FastAPI Services with WSO2 Choreo

## Overview
This document provides a guide to deploying a FastAPI service with WSO2 Choreo.
 
## Prerequisites

Ensure you have the following before beginning:

- **Python 3.8+** installed locally
- **FastAPI + Uvicorn** framework
- **Git provider account** (GitHub, GitLab, or Bitbucket)
- **WSO2 Choreo account** (free tier provides 5 components)

> **Note:** [Sign in to Choreo Console](https://console.choreo.dev/login) to create your account.

---

## Getting Started

1. **Setting up the FastAPI project**
You need to have the following files in the ‘root’ directory of your project in order to deploy your service on choreo,

- requirements.txt — Choreo needs to know what dependencies that your FastAPI app requires. So it installs only what you specify.
- Procfile — Choreo needs instructions on which command to execute to start your app. This is how we tell the system to run our service.

Add the following command to Procfile

```bash
web: uvicorn main:app - host 0.0.0.0 - port $PORT
```

2. **Push the project to your Git provider**

Choreo connects to your project through your git provider. You are free to use a different git provider like GitLab or Bitbucket, but here I will continue with Github. 

> **Quick Start:** You can fork this [demo repository](https://github.com/yasandu0505/fastAPI-deployment-demo) to test the deployment process.

--- 

## Deploying on Choreo

### Create a Project

1. Log in to the [Choreo Console](https://console.choreo.dev)
2. Navigate to your organization
3. Click **Create Project**
4. Enter project details:
   - **Project Name:** Archives Backend
   - **Description:** FastAPI service for archives management
5. Click **Create**

### Create a Service Component

1. Inside your project, click **Create Component**
   - *Alternative:* Use the left sidebar → **Components** → **Create**

2. **Select Component Type:** Service

3. **Choose Repository Connection:**
   - **Option A:** GitHub (if signed in with GitHub credentials)
   - **Option B:** Public GitHub Repository URL

4. **Configure Repository Settings:**
   - **Repository URL:** Your GitHub repository URL
   - **Branch:** `main` (or your deployment branch)
   - **Project Directory:** `/` (or subdirectory if applicable)

5. **Set Component Details:**
   - **Display Name:** Archives Backend API
   - **Component Name:** archives-backend-api
   - **Description:** FastAPI service for document archives

6. **Configure Build Settings:**
   - **Buildpack:** Python
   - **Language Version:** Python 3.11 (or your version)
   - **Build Command:** *(leave default)*
   - **Run Command:**

     ```bash
     uvicorn main:app --host 0.0.0.0 --port 8000
     ```

7. **Configure Endpoint:**
   - **Port:** `8000` (must match the port in your run command)
   - **API Type:** REST
   - **Network Visibility:** Public

8. Click **Create** to finalize the component

### Build the Service

1. Navigate to **Build** (left sidebar)
2. Monitor the initial build process
   - Build status will show as "Building"
   - Wait for completion (typically 2-5 minutes)
3. Verify the build succeeded (green checkmark indicator)

### Deploy the Service
#### Basic Deployment (No Configuration Needed)
1. Click the **Deploy** button
   - *Alternative:* Left sidebar → **Deploy** tab
2. Monitor deployment progress
3. Wait for deployment to complete
#### Advanced Deployment (With Configurations)
1. Click the dropdown arrow next to **Deploy**
2. Select **Configure & Deploy**

3. **Add Environment Variables:**
   - Click **+ Add**
   - Enter **Name** and **Value**
   - Mark as **Secret** for sensitive data (API keys, passwords)
   - Click **Add**

4. **Add File Mounts** (if needed):
   - Navigate to **File Mounts** tab
   - Upload configuration files
   - Specify mount path

5. **Configure Authentication:**
   - Proceed to final step
   - **Disable OAuth** if your API doesn't require authentication
   - Toggle **OAuth 2.0** switch to OFF

6. Click **Deploy**

## Access Your Deployed Service
1. Navigate to **Deploy** tab
2. Locate the **Endpoints** section
3. Copy the **Public URL**
4. Test your API endpoints:
   ```bash
   curl https://your-deployment-url/docs
   ```

> **Tip:** FastAPI automatically provides interactive API documentation at `/docs` endpoint.

---

## Troubleshooting

### Common Issues

**Build Failures**
- Verify `requirements.txt` lists all dependencies with correct versions
- Check Python version compatibility
- Review build logs in the Build tab

**Deployment Failures**
- Ensure the port in your run command matches the endpoint configuration
- Verify `Procfile` command syntax
- Check application logs for runtime errors

**404 Errors**
- Confirm your FastAPI routes are correctly defined
- Verify the base path matches your endpoint configuration
- Check if OAuth is blocking unauthenticated requests

## Best Practices

1. **Use Environment Variables:** Never hardcode sensitive data (API keys, database credentials)
2. **Version Pin Dependencies:** Specify exact versions in `requirements.txt`
3. **Enable Logging:** Configure proper logging for production debugging
4. **Set Up Health Checks:** Implement `/health` endpoint for monitoring
5. **Use HTTPS:** Choreo provides SSL certificates automatically


## Additional Resources

For comprehensive documentation, advanced configuration options, and troubleshooting guidance, consult the official WSO2 Choreo documentation:

[WSO2 Choreo Documentation](https://wso2.com/choreo/docs/)

---

*For technical support or implementation assistance, contact your organization's API management team or WSO2 support channels.*