# Landing page con Azure Blob Storage

MVP de la hackathon: una landing de ropa sirve una promoción desde un Blob
privado usando `DefaultAzureCredential` e identidad administrada. No se usan
connection strings ni claves de Storage.

## Ejecutar localmente

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
az login
export STORAGE_ACCOUNT_NAME=<cuenta-de-storage>
flask --app app run --debug
```

La identidad local autenticada con `az login` necesita el rol `Storage Blob Data
Reader` sobre la cuenta. Para una prueba rápida también se pueden usar
`az login` y `az account set --subscription <id>`.

## Desplegar infraestructura

Los nombres de Storage Account deben ser globalmente únicos y contener solo
minúsculas y números.

```bash
az group create --name rg-nova-hackathon --location westeurope
az deployment group create \
  --resource-group rg-nova-hackathon \
  --template-file infra/main.bicep \
  --parameters appName=nova-landing-<unico> storageAccountName=nova<unico>
```

## Subir o cambiar la promoción

El archivo se administra desde Azure Portal o con Azure CLI. El contenedor es
privado y la aplicación solo necesita leerlo.

```bash
az storage blob upload \
  --account-name <cuenta-de-storage> \
  --container-name mensajes \
  --name mensaje.txt \
  --file message.txt \
  --auth-mode login \
  --overwrite
```

Después de cambiar `mensaje.txt`, recarga la URL del App Service para ver la
promoción actualizada.

## Arquitectura

```text
Navegador -> Azure App Service -> identidad administrada
          -> contenedor privado mensajes/mensaje.txt
```

El Bicep crea el plan App Service F1, la aplicación Linux con Python 3.12, la
identidad administrada asignada por el usuario, la cuenta StorageV2, el
contenedor privado y el rol `Storage Blob Data Reader`.
