# mesh/ — Capa mesh (Capa 2)

Nodo de mensajería descentralizada sobre **Reticulum (RNS)**. **Funcional.**

Reticulum es un stack de red basado en criptografía y agnóstico de transporte:
no usa IP ni servidores, y cada nodo se identifica por su clave pública. El
mismo nodo funciona sobre TCP, interfaces locales o **LoRa** (módulo SX1262)
cambiando solo la configuración de interfaces — el código de mensajería no
cambia.

## Componentes

| Archivo / módulo     | Rol                                                   |
|----------------------|-------------------------------------------------------|
| `smmesh/node.py`     | `MeshNode`: identidad, anuncios, buzón, envío/recepción. |
| `service.py`         | Servicio HTTP que la API (`../api`) consulta.         |
| `reticulum.config.example` | Config de Reticulum (LoRa + TCP de ejemplo).    |

## Uso

```sh
pip install -r requirements.txt          # o usar el venv de scripts/setup.sh

# Configdir de Reticulum (interfaces): copiar y editar el ejemplo
mkdir -p reticulum && cp reticulum.config.example reticulum/config

# Levantar el nodo + servicio HTTP
python3 service.py --configdir reticulum --name mi-nodo --port 8091
```

Cada interfaz del config necesita `interface_enabled = true` para activarse.
Sin ninguna interfaz activa el nodo corre igual, pero aislado (sin peers).

## Servicio HTTP

| Método | Ruta        | Descripción                                          |
|--------|-------------|------------------------------------------------------|
| GET    | `/health`   | Estado del nodo: dirección, nombre, nº de peers/inbox. |
| GET    | `/peers`    | Nodos descubiertos vía anuncios.                     |
| GET    | `/inbox`    | Mensajes recibidos (opcional `?since=<id>`).         |
| POST   | `/send`     | Body `{"to": "<address>", "text": "..."}`.           |
| POST   | `/announce` | Fuerza un anuncio inmediato.                         |

## Mensajería

Los mensajes son paquetes RNS únicos cifrados extremo a extremo. El texto se
limita a 230 caracteres (un paquete `SINGLE` transporta ~380 bytes; el resto es
el sobre JSON). Mensajes más largos requerirían `RNS.Resource` sobre un `Link`,
o adoptar **LXMF** para almacenamiento-y-reenvío — pasos naturales a futuro.

## Pendiente

- [ ] Transporte LoRa real: validar `RNodeInterface` con hardware SX1262.
- [ ] Bridges a BitChat (BLE) y Meshtastic.
- [ ] Gateway Nostr para alcance global cuando hay internet.
- [ ] LXMF para mensajes largos y store-and-forward.
