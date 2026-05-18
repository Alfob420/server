# mesh/ — Protocolo mesh (Capa 2)

Integración con **Reticulum Network Stack (RNS)** y bridges a redes mesh
existentes. Es la pieza que rutea mensajes entre transportes (Capa 1) sin
servidores ni direcciones IP.

> **Estado: stub.** Solo documentación y un ejemplo de configuración. La
> integración con el daemon `rnsd` y los bridges está pendiente.

## Reticulum como core

- Stack de red basado en criptografía, agnóstico de transporte (no usa IP).
- Cada nodo se identifica por su clave pública.
- Una sola Pi puede tener LoRa + BLE + WiFi + túnel a internet activos a la
  vez; Reticulum elige el mejor medio y forma una mesh encriptada E2E.
- Implementación: paquete Python `rns` (pip), daemon `rnsd` vía systemd.

## Bridges previstos (efecto red)

| Bridge      | Qué conecta                                              |
|-------------|----------------------------------------------------------|
| BitChat     | Celulares con la app BitChat vía BLE.                    |
| Meshtastic  | La red LoRa mundial de Meshtastic (decenas de miles de nodos). |
| Nostr       | Gateway a relays Nostr globales cuando hay internet.     |

## Archivos

- `reticulum.config.example` — configuración de ejemplo para `rnsd` con una
  interfaz LoRa. Copiar a `~/.reticulum/config` y ajustar.

## Pendiente

- [ ] Script de instalación/arranque de `rnsd` (systemd unit).
- [ ] Cliente Reticulum para que `../api` envíe/reciba mensajes por la mesh.
- [ ] Bridge BitChat (BLE).
- [ ] Bridge Meshtastic.
- [ ] Gateway Nostr.
