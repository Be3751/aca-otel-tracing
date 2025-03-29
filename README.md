<!--
---
page_type: sample
languages:
- azdeveloper
- python
- bicep
products:
- azure
- azure-container-apps
urlFragment: svc-invoke-python
name: Microservice communication using Python with OpenTelemetry Tracing
description: Create microservices with Python that communicate reliably and securely. Instrument the services with OpenTelemetry and Azure Monitor Distro for distributed tracing and observability.
---
-->
<!-- YAML front-matter schema: https://review.learn.microsoft.com/en-us/help/contribute/samples/process/onboarding?branch=main#supported-metadata-fields-for-readmemd -->

# Microservice Communication with OpenTelemetry Tracing

This repository demonstrates how to build microservices that communicate reliably and securely. It also showcases how to instrument these services with OpenTelemetry and Azure Monitor Distro (AzMon Distro) for distributed tracing and observability.

## Inspiration

This repository is inspired by the [Azure Samples repository](https://github.com/Azure-Samples/svc-invoke-dapr-python), which demonstrates microservice communication using Dapr. However, this implementation focuses on using OpenTelemetry to trace service-to-service communication between the following services:
- **Checkout Service**: Initiates the order process.
- **Order Service**: Processes the order.
- **Receipt Service**: Generates a receipt for the order.
- **Azure Storage Account**: Stores the receipt data.

---

## Features
- Reliable and secure microservice communication.
- Deployment to Azure Container Apps (ACA) using Azure Developer CLI (azd).
- Distributed tracing and monitoring with Azure Application Insights and AzMon Distro.
- Tracing service-to-service communication, including interactions with Azure Storage Account.

---

## Run Locally

### Prerequisites
- Install [Python 3.8+](https://www.python.org/downloads/).
- Install [Azure Developer CLI (azd)](https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/install-azd).

### Steps
1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd aca-otel-tracing
   ```

2. Follow the instructions below to run the services locally:
   - **Checkout Service**:  
     ```bash
     cd checkout
     pip3 install -r requirements.txt 
     python3 app.py
     ```
   - **Order Service**:  
     ```bash
     cd order
     pip3 install -r requirements.txt 
     python3 app.py
     ```
   - **Receipt Service**:  
     ```bash
     cd receipt
     pip3 install -r requirements.txt 
     python3 app.py
     ```

3. Expected output:
In the terminal logs, you'll see traces of service-to-service communication, including interactions with the Azure Storage Account.

---

## Deploy to Azure and Verify Tracing

### Prerequisites
- Ensure you have Azure CLI installed and authenticated.
- Install Azure Developer CLI (azd) version 0.9.0-beta.3 or greater.

### Steps
1. Initialize the project:
   ```bash
   azd init --template https://github.com/Azure-Samples/svc-invoke-python
   ```

   Provide the following information when prompted:
   - `Environment Name`: Unique name for your Azure resources.
   - `Azure Location`: Region where resources will be deployed.
   - `Azure Subscription`: Subscription to use for deployment.

2. Deploy the application:
   ```bash
   azd up
   ```

   This command will:
   - Package the application (`azd package`).
   - Provision Azure resources (`azd provision`).
   - Deploy the application code (`azd deploy`).

3. Verify the deployment:
   - Navigate to the Azure Portal and locate the Container Apps for all services.
   - Check the `Log stream` for each app to confirm successful communication.

4. View distributed traces:
   - Open the Azure Application Insights resource in the Azure Portal.
   - Use the "Transaction Search" or "Live Metrics" features to view traces of service invocation and Azure Storage interactions.

---

## Instrumentation with AzMon Distro

### Overview
The Azure Monitor OpenTelemetry Distro (AzMon Distro) simplifies the process of instrumenting your applications for distributed tracing and metrics collection. It integrates seamlessly with Azure Application Insights.

### Steps to Enable AzMon Distro
1. Install the AzMon Distro package:
   ```bash
   pip install azure-monitor-opentelemetry
   ```

2. Update your application code to initialize the AzMon Distro SDK:
   ```python
   from azure.monitor.opentelemetry import configure_azure_monitor

   configure_azure_monitor(connection_string="InstrumentationKey=<your-instrumentation-key>")
   ```

3. Redeploy the services locally or to Azure to start collecting traces and metrics.

### Benefits
- Automatic instrumentation for HTTP, database, and messaging libraries.
- Seamless integration with Azure Monitor for end-to-end observability.

---

## Resources
- [Azure Samples Repository](https://github.com/Azure-Samples/svc-invoke-dapr-python)
- [Azure Monitor OpenTelemetry Distro](https://learn.microsoft.com/en-us/azure/azure-monitor/app/opentelemetry-overview)
- [Azure Developer CLI](https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/)

