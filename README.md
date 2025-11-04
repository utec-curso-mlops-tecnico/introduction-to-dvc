# Introduction to DVC + Azure ML (control de versión de datos)

## Objetivo
Este proyecto muestra cómo garantizar el control de versión de datos con DVC e integrarlo con Azure Machine Learning. El dataset principal es `data/in/application_data.csv`. Está preparado para uso en una clase de postgrado: reproducibilidad, trazabilidad y ejecución en compute instance `jacobirios1`.

## Estructura principal
- data/in/application_data.csv  : dataset original (seguido por DVC)
- dvc.yaml                      : pipeline reproducible (prepare → train → evaluate)
- params.yaml                   : parámetros versionados
- environment.yml               : entorno reproducible (Conda)
- src/                          : scripts (data prep, train, evaluate, loader)
- scripts/                      : helpers para ejecución local y en Azure ML
- aml/                          : manifests y utilidades para Azure ML (register_data.py, job YAMLs, credenciales)
- .gitignore, .dvcignore

## Cambios clave cuando se usa Azure ML Studio
- Los blobs de datos quedan en Azure Storage (DVC remote). El código y metadatos (.dvc) siguen en Git.
- En Azure ML hay dos formas típicas de consumir los datos versionados:
  1. Registrar un DataAsset que apunte al container donde DVC puso los blobs y usar ese DataAsset en el job (más simple para ejecución).
  2. Ejecutar `dvc pull` dentro del job para recuperar exactamente la versión de datos controlada por DVC (mantiene trazabilidad DVC completa).
- Recomendación de seguridad: usar Managed Identity del compute y asignar rol "Storage Blob Data Reader". Ver `aml/CREDENTIALS.md`.

## Archivos relevantes para Azure ML Studio
- aml/register_data.py               : script para registrar DataAsset que referencia el container con los blobs subidos por DVC.
- aml/train_job_using_dataasset.yml  : job YAML que usa el DataAsset registrado como input.
- aml/train_job_with_dvc_pull.yml    : job YAML que instala DVC y ejecuta `dvc pull` dentro del job (requiere acceso al storage).
- aml/CREDENTIALS.md                 : guía para configurar Managed Identity o uso de secrets.
- aml/USAGE_CLASS.md                 : pasos resumidos para la demo en clase.

## Pasos breves: preparar desde laptop y subir datos (DVC → Remote)
1. Inicializar repo y DVC (si no está hecho):
   - git init
   - dvc init
2. Configurar remote DVC en Azure Blob (ejemplo):
   - dvc remote add -d azureremote azure://<container>/<path>
3. En Windows PowerShell, exportar connection string (si no usas Managed Identity):
   - setx AZURE_STORAGE_CONNECTION_STRING "<connection-string>"
   - (o usar Key Vault / variables seguras)
4. Añadir y subir los datos:
   - dvc add data/in/application_data.csv
   - git add data/in/application_data.csv.dvc .gitignore
   - git commit -m "Add raw data tracked by DVC"
   - dvc push

## Flujo A — Usar DataAsset (recomendado para clase práctica)
1. Registrar DataAsset apuntando al container donde DVC subió los blobs:
   - Configurar variables de entorno (PowerShell):
     - setx SUBSCRIPTION_ID "<subscription-id>"
     - setx RESOURCE_GROUP "<resource-group>"
     - setx WORKSPACE_NAME "<workspace-name>"
     - setx STORAGE_ACCOUNT "<storage-account>"
     - setx CONTAINER "<container>"
     - setx PATH_PREFIX "<optional/path-prefix>"
   - Ejecutar en terminal (local o compute):
     - python aml/register_data.py
   - Apuntar `aml/train_job_using_dataasset.yml` al DataAsset name:version que imprima el script.
2. Enviar job a Azure ML usando el DataAsset:
   - az ml job create --file aml/train_job_using_dataasset.yml
3. Ver estado y descargar outputs:
   - az ml job show --name <job-name>
   - az ml job download --name <job-name> --output-dir ./job_outputs

Ventaja: no necesitas DVC en runtime; el job descargará los datos desde el DataAsset.

## Flujo B — Hacer dvc pull dentro del job (trazabilidad DVC completa)
1. Asegúrate de que el job tenga acceso al storage:
   - Opción recomendada: habilitar Managed Identity en `jacobirios1` y asignarle "Storage Blob Data Reader".
   - Opción alternativa: pasar AZURE_STORAGE_CONNECTION_STRING como variable segura al job (Key Vault o environment variables).
2. Enviar job que ejecuta dvc pull (ejemplo):
   - az ml job create --file aml/train_job_with_dvc_pull.yml --set environment_variables.AZURE_STORAGE_CONNECTION_STRING="$AZ_CONN_STR"
3. El job hará: instalar dvc[azure], `dvc pull data/in/application_data.csv`, preparar y entrenar.

Ventaja: recuperas exactamente los blobs versionados por DVC; ideal para trazabilidad y reproducibilidad estricta.

## Comandos útiles (Azure CLI / PowerShell)
- Iniciar sesión Azure:
  - az login
- Crear/submit job:
  - az ml job create --file aml/train_job_using_dataasset.yml
  - az ml job create --file aml/train_job_with_dvc_pull.yml --set environment_variables.AZURE_STORAGE_CONNECTION_STRING="$AZ_CONN_STR"
- Inspeccionar job:
  - az ml job show --name <job-name>
  - az ml job logs --name <job-name> --all
  - az ml job download --name <job-name> --output-dir ./job_outputs

## Seguridad y credenciales
- No commitees connection strings ni secretos en Git.
- Preferible: usar Managed Identity del compute y asignar roles en Storage (ver `aml/CREDENTIALS.md`).
- Alternativa: Key Vault + pasar secreto como variable al job (Azure ML soporta integración con Key Vault).

## Sugerencia para la clase (agenda práctica)
1. Mostrar DVC local: dvc add, git commit, dvc push.
2. Registrar DataAsset y lanzar job usando `train_job_using_dataasset.yml`.
3. Alternativa: dvc pull en job con `train_job_with_dvc_pull.yml` y comparar trazabilidad.
4. Ejecutar `dvc params diff` y `dvc metrics show` entre commits para explicar versionado de parámetros y métricas.
5. Demostrar recuperación: borrar local `data/in/application_data.csv` y ejecutar `dvc pull` desde compute.

## Referencias y archivos relacionados
- aml/register_data.py
- aml/train_job_using_dataasset.yml
- aml/train_job_with_dvc_pull.yml
- aml/CREDENTIALS.md
- aml/USAGE_CLASS.md
- dvc.yaml, params.yaml, environment.yml, src/