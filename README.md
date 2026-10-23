# Backend de promociones con Azure Blob Storage

Backend API para que un frontend consuma una promoción almacenada en un Blob
privado. La aplicación usa `DefaultAzureCredential` e identidad administrada.
No se usan connection strings ni claves de Storage. El catálogo y la landing
pertenecen al frontend y no están incluidos en este repositorio.

## Ejecutar localmente

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
az login
export STORAGE_ACCOUNT_NAME=<cuenta-de-storage>
export FRONTEND_ORIGIN=https://<tu-frontend>
flask --app app run --debug
```

La identidad local autenticada con `az login` necesita el rol `Storage Blob Data
Reader` sobre la cuenta. Para una prueba rápida también se pueden usar
`az login` y `az account set --subscription <id>`.

## API

### `GET /api/promotion`

Devuelve la promoción actual leída desde `mensajes/mensaje.txt`:

```json
{
  "message": "¡30% de descuento en la nueva colección!"
}
```

Cuando Blob Storage no está disponible, responde con HTTP `503`:

```json
{
  "error": "Promotion unavailable"
}
```

### `GET /health`

Endpoint para comprobar que el proceso está activo:

```json
{
  "status": "ok"
}
```

El frontend debe consumir `GET /api/promotion` y pintar `message` en su banner.
Configura `FRONTEND_ORIGIN` con el origen exacto del frontend para permitir
peticiones CORS. Si frontend y backend comparten origen, esta variable no es
necesaria.

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

Después de cambiar `mensaje.txt`, el siguiente consumo de
`GET /api/promotion` devolverá la promoción actualizada.

## Arquitectura

```text
Frontend -> Backend (Azure App Service) -> identidad administrada
         -> contenedor privado mensajes/mensaje.txt
```

El Bicep crea el plan App Service F1, la aplicación Linux con Python 3.12, la
identidad administrada asignada por el usuario, la cuenta StorageV2, el
contenedor privado y el rol `Storage Blob Data Reader`.
