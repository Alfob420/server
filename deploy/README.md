# deploy/ — Despliegue en el dispositivo

Unidades systemd para correr Survival Mesh como servicios en el dispositivo
(Raspberry Pi). Las unidades asumen que el repo está clonado en
`/opt/survival-mesh` y que el venv del RAG está en `/opt/survival-mesh/rag/.venv`
(lo crea `scripts/setup.sh`).

## Unidades

| Archivo                      | Capa | Servicio                          |
|------------------------------|------|-----------------------------------|
| `survival-mesh-rag.service`  | 3    | Servicio RAG (puerto 8090).       |
| `survival-mesh-api.service`  | 4    | API local + PWA (puerto 8080).    |
| `rnsd.service`               | 2    | Daemon Reticulum.                 |

## Instalación

```sh
# 1. Clonar y compilar en /opt/survival-mesh
sudo git clone <repo> /opt/survival-mesh
cd /opt/survival-mesh && sudo scripts/setup.sh

# 2. Instalar y activar las unidades
sudo cp deploy/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now survival-mesh-rag survival-mesh-api
```

`rnsd.service` se activa una vez instalado el paquete `rns` y configurado
`~/.reticulum/config` (ver `mesh/README.md`):

```sh
/opt/survival-mesh/rag/.venv/bin/pip install rns
sudo systemctl enable --now rnsd
```

## Notas

- Las unidades de mesh/transporte (`rnsd`) dependen de hardware físico (módulo
  LoRa SX1262, BLE) y no se pueden validar sin él.
- Si se rutea el tráfico HTTP por un hotspot WiFi del dispositivo, configurar
  `hostapd` + `dnsmasq` aparte (ver `transport/README.md`).
