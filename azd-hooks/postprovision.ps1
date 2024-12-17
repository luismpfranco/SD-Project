#!/usr/bin/env pwsh

$services=@("ai-service", "makeline-service", "order-service", "product-service", "store-admin", "store-front", "virtual-customer", "virtual-worker")

if (($env:DEPLOY_AZURE_CONTAINER_REGISTRY -like "true") -and ($env:BUILD_CONTAINERS -like "true")) {
  echo "Build container images"
  foreach ($service in $services) {
    echo "Building aks-store-demo/${service}:latest"
    az acr build --registry $env:AZURE_REGISTRY_NAME --image aks-store-demo/${service}:latest ./src/${service}/
  }
} 
elseif (($env:DEPLOY_AZURE_CONTAINER_REGISTRY -like "true") -and ($env:BUILD_CONTAINERS -like "false")) {
  echo "Import container images"
  foreach ($service in $services) {
    echo "Importing aks-store-demo/${service}:latest"
    az acr import --name $env:AZURE_REGISTRY_NAME --source 2083121/aks-store-demo:${service} --image aks-store-demo:${service}
  }
} 
else {
  echo "No BUILD_CONTAINERS variable set, skipping container build/import"
}

