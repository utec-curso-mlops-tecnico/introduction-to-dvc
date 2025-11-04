# Script para registrar un DataAsset en Azure ML apuntando al contenedor donde DVC sube los blobs.
# Uso: configurar variables de entorno SUBSCRIPTION_ID, RESOURCE_GROUP, WORKSPACE_NAME, STORAGE_ACCOUNT, CONTAINER, PATH_PREFIX
# Ejemplo:
# setx SUBSCRIPTION_ID "..."
# setx RESOURCE_GROUP "..."
# setx WORKSPACE_NAME "..."
# setx STORAGE_ACCOUNT "mystorageacct"
# setx CONTAINER "dvc-remote"
# setx PATH_PREFIX "path/where/dvc/put/files"
# python aml/register_data.py

from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential
from azure.ai.ml.entities import Data
import os

SUBSCRIPTION_ID = os.environ.get("SUBSCRIPTION_ID")
RESOURCE_GROUP = os.environ.get("RESOURCE_GROUP")
WORKSPACE_NAME = os.environ.get("WORKSPACE_NAME")
STORAGE_ACCOUNT = os.environ.get("STORAGE_ACCOUNT")
CONTAINER = os.environ.get("CONTAINER")
PATH_PREFIX = os.environ.get("PATH_PREFIX", "")

if not all([SUBSCRIPTION_ID, RESOURCE_GROUP, WORKSPACE_NAME, STORAGE_ACCOUNT, CONTAINER]):
    raise SystemExit("Configure SUBSCRIPTION_ID, RESOURCE_GROUP, WORKSPACE_NAME, STORAGE_ACCOUNT y CONTAINER como variables de entorno.")

ml_client = MLClient(DefaultAzureCredential(), SUBSCRIPTION_ID, RESOURCE_GROUP, WORKSPACE_NAME)

# Construye la URL del folder donde DVC puso los blobs
path = f"https://{STORAGE_ACCOUNT}.blob.core.windows.net/{CONTAINER}"
if PATH_PREFIX:
    path = f"{path}/{PATH_PREFIX}"

data_asset = Data(
    path=path,
    type="uri_folder",
    description="Dataset versioned by DVC (blob container path)",
    name="application_data_dvc"
)

registered = ml_client.data.create_or_update(data_asset)
print(f"Registered DataAsset: {registered.name}, version: {registered.version}, path: {path}")