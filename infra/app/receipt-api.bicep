param name string
param location string = resourceGroup().location
param tags object = {}

param containerAppsEnvironmentName string
param containerRegistryName string
param imageName string = ''
param serviceName string = 'receipt'
param managedIdentityName string = ''
param storageAccountName string
param containerName string
param applicationInsightsConnectionString string

module app '../core/host/container-app.bicep' = {
  name: '${serviceName}-container-app-module'
  params: {
    name: name
    location: location
    tags: union(tags, { 'azd-service-name': '${serviceName}-api' })
    containerAppsEnvironmentName: containerAppsEnvironmentName
    containerRegistryName: containerRegistryName
    containerCpuCoreCount: '1.0'
    containerMemory: '2.0Gi'
    imageName: !empty(imageName) ? imageName : 'nginx:latest'
    containerName: serviceName
    external: false
    managedIdentityEnabled: true
    managedIdentityName: managedIdentityName
    env: [
      {
        name: 'STORAGE_ACCOUNT_NAME'
        value: storageAccountName
      }
      {
        name: 'STORAGE_ACCOUNT_CONTAINER_NAME'
        value: containerName
      }
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

resource storageAccount 'Microsoft.Storage/storageAccounts@2022-05-01' existing = {
  name: storageAccountName
}

var storageRoleDefinitionId = 'ba92f5b4-2d11-453d-a403-e96b0029c9fe'
var storageRoleAssignmentId = '/subscriptions/${subscription().subscriptionId}/providers/Microsoft.Authorization/roleDefinitions/${storageRoleDefinitionId}'
resource roleAssignment 'Microsoft.Authorization/roleAssignments@2020-04-01-preview' = {
  name: guid(resourceGroup().id, storageAccount.id, storageRoleAssignmentId)
  scope: storageAccount
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', storageRoleDefinitionId)
    principalId: app.outputs.identityPrincipalId
    principalType: 'ServicePrincipal'
  }
}

output SERVICE_API_IDENTITY_PRINCIPAL_ID string = app.outputs.identityPrincipalId
output SERVICE_API_NAME string = app.outputs.name
output SERVICE_API_URI string = app.outputs.uri
output SERVICE_API_IMAGE_NAME string = app.outputs.imageName
