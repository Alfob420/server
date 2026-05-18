# Survival Mesh — Arquitectura Técnica (Documento 1)

Dispositivo de bolsillo con IA offline y comunicación mesh descentralizada.
Hardware comercial · Software open source.

## 1. Resumen ejecutivo

Survival Mesh es un dispositivo portable de código abierto que combina tres
capacidades nunca antes integradas en un solo producto comercial:

- Un **LLM** corriendo localmente con base de conocimiento de supervivencia.
- **Comunicación mesh descentralizada multi-transporte** (LoRa + BLE + WiFi + Nostr).
- **Autonomía total** sin dependencia de internet, antenas celulares ni servidores.

**Modelo de negocio:** se vende el hardware ensamblado y el kit DIY. El
software es 100% open source y lo instala el usuario desde una imagen
pre-armada. El margen se captura en el hardware, no en software ni servicios.

**Diferenciador clave:** no existe hoy un producto comercial que combine LLM
offline + mesh descentralizada multi-transporte. Meshtastic tiene mesh pero no
IA. PocketPal tiene IA pero no mesh. BitChat tiene mesh BLE pero no LLM ni LoRa.

## 2. Arquitectura de software

### 2.1. Stack en capas

```
┌─────────────────────────────────────────────────┐
│  CAPA 4 — APLICACIÓN                            │
│  PWA cyberpunk + API local Rust/Axum            │
├─────────────────────────────────────────────────┤
│  CAPA 3 — INTELIGENCIA                          │
│  llama.cpp + Qwen 2.5 3B + SQLite-vec (RAG)     │
├─────────────────────────────────────────────────┤
│  CAPA 2 — PROTOCOLO MESH                        │
│  Reticulum (RNS) + bridges a BitChat/Meshtastic │
├─────────────────────────────────────────────────┤
│  CAPA 1 — TRANSPORTE FÍSICO                     │
│  LoRa SX1262 + BlueZ (BLE) + WiFi + Nostr       │
└─────────────────────────────────────────────────┘
```

### 2.2. Capa de inteligencia (LLM + RAG)

**Modelo LLM:** Qwen 2.5 3B Instruct, cuantizado a Q4_K_M (~2 GB en disco).
Licencia Apache 2.0, MMLU 65.6, ~8 tokens/s en Raspberry Pi 5.

**Fallback Tier 1** (Pi Zero 2W, 512 MB RAM): Llama 3.2 1B Q4_K_M (~800 MB).

**Runtime:** llama.cpp (MIT). Único runtime nativo en ARM64 Linux, ARM64
Android y x86 desktop con el mismo formato GGUF. Optimizaciones: ARM NEON SIMD,
OpenCL/Vulkan opcional en Android, KV cache quantization a Q8.

**RAG:** SQLite + extensión `sqlite-vec` + embeddings `all-MiniLM-L6-v2`
(90 MB, multiplataforma). El índice es un archivo `.db` portable.

**Corpus de supervivencia** (todas licencias compatibles con redistribución):
Survivor Library (dominio público), Wikipedia offline (Kiwix, CC BY-SA),
FM 21-76 US Army Survival Manual, Where There Is No Doctor/Dentist (Hesperian),
ARRL Handbook (porciones liberadas), manuales Cruz Roja (CC BY-NC), y material
original propio.

## 3. Capa de comunicación descentralizada

### 3.1. Reticulum como core

Reticulum Network Stack (RNS) es un stack de red completo basado en
criptografía, agnóstico de transporte. No corre sobre IP. Cada nodo se
identifica por su clave pública. Una sola Pi puede tener activos LoRa,
Bluetooth, WiFi y un túnel a internet simultáneamente; Reticulum rutea por el
mejor medio disponible y forma una mesh autoconfigurable y encriptada E2E.

Implementación: paquete Python `rns` (pip), daemon `rnsd` como servicio systemd.

### 3.2. Transportes físicos

- **LoRa** — Semtech SX1262 por SPI. 868 MHz EU / 915 MHz US-AR / 433 MHz Asia.
  Alcance 1-3 km ciudad, 5-15 km abierto, 20+ km con yagi. Throughput bajo
  (250 bps – 27 kbps): texto y datos pequeños, no audio ni imágenes.
- **Bluetooth LE** — BlueZ. Repetidor BLE para celulares cercanos (~30 m) vía
  app BitChat. Crítico en aglomeraciones.
- **WiFi Direct / Hotspot** — transferencia rápida de archivos grandes; el
  dispositivo arma su propio hotspot para la UI web.
- **Nostr** — cuando hay internet, sincroniza mensajes pendientes con relays
  públicos. Alcance global gratis.

### 3.3. Bridges con redes existentes

El producto no compite con BitChat/Meshtastic, los abraza: bridge BitChat,
bridge Meshtastic (interop con la red LoRa mundial) y gateway Nostr.

## 4. Hardware (resumen)

| Tier      | Pocket Node   | Field Unit      | Base Station        |
|-----------|---------------|-----------------|---------------------|
| SBC       | Pi Zero 2W    | Pi 5 4GB        | Pi 5 8GB + SSD      |
| LLM       | Llama 3.2 1B  | Qwen 2.5 3B     | Qwen 2.5 7B         |
| LoRa      | SX1262 100mW  | MeshAdv 1W      | 1W + antena ext.    |
| Pantalla  | OLED 1.3"     | Touch 3.5"      | Headless            |
| Energía   | 18650 6h      | PiSugar 3 12h   | Solar + LiFePO4     |
| BOM aprox | $100 USD      | $260 USD        | $380 USD            |
| Retail    | $250 USD      | $700 USD        | $1100 USD           |

## 5. Roadmap

Ver [`ROADMAP.md`](ROADMAP.md).

## 6. Licencias y consideraciones legales

### 6.1. Software

| Componente        | Licencia            | Uso comercial            |
|-------------------|---------------------|--------------------------|
| llama.cpp         | MIT                 | OK, atribución en docs   |
| Qwen 2.5 3B       | Apache 2.0          | OK, sin restricciones    |
| Reticulum (RNS)   | MIT/Reticulum       | OK, atribución           |
| BlueZ             | GPL v2              | OK pero no linkeo estático |
| SQLite + sqlite-vec | Public Domain / Apache | OK total            |
| all-MiniLM-L6-v2  | Apache 2.0          | OK, sin restricciones    |

### 6.2. Hardware

PCB del HAT custom y case bajo **CERN Open Hardware License v2** (permisiva).

### 6.3. Regulación radio (LoRa)

**CRÍTICO:** cada región tiene banda permitida diferente. El dispositivo NO
puede venderse con LoRa configurado para banda equivocada. Estrategia: HAT LoRa
detachable vendido por separado según región, configuración regional bloqueada
por firmware al primer boot, certificación CE/FCC eventual, venta inicial como
"development kit".

### 6.4. Corpus RAG

Solo material con licencia explícita compatible con redistribución comercial
(CC BY, CC BY-SA, Apache, MIT, dominio público). NO incluir libros con
copyright tradicional. El usuario puede agregar lo que quiera a su copia.

## 7. Riesgos y mitigaciones

| Riesgo                          | Mitigación                                        |
|---------------------------------|---------------------------------------------------|
| Regulación radio por país       | HAT LoRa regional, locking por firmware, CE/FCC   |
| LLM dice algo peligroso         | System prompt "educacional", disclaimers, curación |
| Clones chinos baratos           | Diferencial = comunidad + soporte + curación      |
| Dependencia de un fabricante SBC | Software portable (Radxa, Orange Pi, Banana Pi)  |
| Reticulum en beta               | Meshtastic como fallback estable, aportar upstream |
| Uso por actores malintencionados | Producto neutral; documentar uso legítimo        |
