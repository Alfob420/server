# deploy/ — Despliegue en el dispositivo

Unidades systemd para correr Survival Mesh como servicios en el dispositivo
(Raspberry Pi). Las unidades asumen que el repo está en `/opt/survival-mesh` y
que el venv de Python está en `/opt/survival-mesh/.venv` (lo crea
`scripts/setup.sh`).

## Unidades

| Archivo                       | Capa | Servicio                          |
|-------------------------------|------|-----------------------------------|
| `survival-mesh-mesh.service`  | 2    | Nodo Reticulum (puerto 8091).     |
| `survival-mesh-nostr.service` | 1    | Gateway Nostr (puerto 8092).      |
| `survival-mesh-rag.service`   | 3    | Servicio RAG (puerto 8090).       |
| `survival-mesh-api.service`   | 4    | API local + PWA (puerto 8080).    |

La API depende de los servicios mesh, Nostr y RAG (`Wants`/`After`); si alguno
no está disponible, la API degrada con elegancia en vez de fallar.

## Instalación

```sh
# 1. Clonar y compilar en /opt/survival-mesh
sudo git clone <repo> /opt/survival-mesh
cd /opt/survival-mesh && sudo scripts/setup.sh

# 2. Configurar las interfaces de Reticulum (LoRa, TCP, etc.)
sudo cp mesh/reticulum.config.example mesh/reticulum/config
sudo nano mesh/reticulum/config        # activar interface_enabled = true

# 3. Instalar y activar las unidades
sudo cp deploy/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now survival-mesh-mesh survival-mesh-nostr \
  survival-mesh-rag survival-mesh-api
```

## Notas

- El servicio mesh corre su propio nodo Reticulum; no hace falta un `rnsd`
  aparte salvo que se quiera compartir el stack con otras apps.
- El transporte LoRa (`RNodeInterface`) depende del hardware físico (módulo
  SX1262) y no se puede validar sin él.
- Para servir la PWA por un hotspot WiFi del dispositivo, configurar `hostapd`
  + `dnsmasq` aparte (ver `transport/README.md`).
- Para inferencia LLM real, correr un `llama-server` y descomentar `SM_LLM_URL`
  en `survival-mesh-api.service`.
