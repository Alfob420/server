# transport/ — Transporte físico (Capa 1)

La capa más baja: los medios físicos por los que viajan los bits. Reticulum
(Capa 2) rutea sobre estos transportes; aquí solo se documenta y configura el
hardware/sistema.

> **Estado: stub.** Solo documentación. Los scripts de configuración del SO
> (BlueZ, hostapd, SPI para LoRa) están pendientes.

## Transportes

| Transporte | Hardware                  | Alcance        | Throughput        |
|------------|---------------------------|----------------|-------------------|
| LoRa       | Semtech SX1262 (SPI)      | 1-3 km ciudad, 5-15 km abierto | 250 bps – 27 kbps |
| BLE        | Bluetooth 5.0 (BlueZ)     | ~30 m          | medio             |
| WiFi       | 2.4/5 GHz integrado        | ~50-100 m      | alto              |
| Nostr      | Cualquier salida a internet| global         | alto (requiere internet) |

## Notas por transporte

- **LoRa** — banda según región (868 EU / 915 US-AR / 433 Asia). La frecuencia
  se configura en `../mesh/reticulum.config.example`. Bloqueo regional por
  firmware al primer boot.
- **BLE** — el dispositivo actúa como repetidor BLE para celulares cercanos
  (app BitChat). Gestionado por BlueZ.
- **WiFi** — el dispositivo arma su propio hotspot para servir la PWA y
  transferir archivos grandes (modelos, índices RAG, mapas).
- **Nostr** — al detectar internet, sincroniza mensajes pendientes con relays
  públicos para alcance global.

## Pendiente

- [ ] Habilitar SPI y enumerar el módulo LoRa en Pi OS.
- [ ] Perfil BlueZ para el rol de repetidor BLE.
- [ ] Configuración `hostapd` + `dnsmasq` para el hotspot WiFi.
- [ ] Detección automática de internet para activar el gateway Nostr.
