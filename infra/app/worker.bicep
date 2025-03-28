param name string
param location string = resourceGroup().location
param tags object = {}

param containerAppsEnvironmentName string
param containerRegistryName string
param imageName string = ''
param serviceName string = 'checkout'
param managedIdentityName string = ''
param applicationInsightsConnectionString string

module app '../core/host/container-app-worker.bicep' = {
  name: '${serviceName}-container-app-module'
  params: {
    name: name
    location: location
    tags: union(tags, { 'azd-service-name': 'worker' })
    containerAppsEnvironmentName: containerAppsEnvironmentName
    containerRegistryName: containerRegistryName
    imageName: !empty(imageName) ? imageName : 'nginx:latest'
    containerName: serviceName
    managedIdentityEnabled: true
    managedIdentityName: managedIdentityName
    env: [
      {
        name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
        value: applicationInsightsConnectionString
      }
      {
        name: 'OTEL_SERVICE_NAME'
        value: serviceName
      }
      {
        name: 'OTLP_EXPORT_ENDPOINT'
        value: 'http://tempo.monitoring.svc.cluster.local:3100'
      }
    ]
  }
}

output SERVICE_WEB_IDENTITY_PRINCIPAL_ID string = app.outputs.identityPrincipalId
output SERVICE_WEB_NAME string = app.outputs.name
output SERVICE_WEB_IMAGE_NAME string = app.outputs.imageName
