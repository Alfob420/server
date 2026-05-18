# hardware/ — Hardware

Especificación de los tres tiers del dispositivo, BOM y notas de fabricación.
El detalle completo de proveedores irá en el Documento 2.

## Tiers

| Tier      | Pocket Node   | Field Unit      | Base Station        |
|-----------|---------------|-----------------|---------------------|
| SBC       | Pi Zero 2W    | Pi 5 4GB        | Pi 5 8GB + SSD      |
| LLM       | Llama 3.2 1B  | Qwen 2.5 3B     | Qwen 2.5 7B         |
| LoRa      | SX1262 100mW  | MeshAdv 1W      | 1W + antena ext.    |
| Pantalla  | OLED 1.3"     | Touch 3.5"      | Headless            |
| Energía   | 18650 6h      | PiSugar 3 12h   | Solar + LiFePO4     |
| BOM aprox | $100 USD      | $260 USD        | $380 USD            |
| Retail    | $250 USD      | $700 USD        | $1100 USD           |

## Hardware mínimo viable (Fase 0)

Para arrancar el prototipo (~$250 USD):

- 2× Raspberry Pi 5 4GB
- 2× Waveshare SX1262 LoRa HAT (banda regional correspondiente)
- 2× antena 3 dBi
- 2× microSD 64GB A2

## Licencia de hardware

PCB del HAT custom y case bajo **CERN Open Hardware License v2** (permisiva).

## Regulación radio

**CRÍTICO:** la banda LoRa depende de la región. El HAT LoRa es detachable y se
vende por separado según la región del comprador; la configuración regional se
bloquea por firmware al primer boot. Certificación CE/FCC pendiente para
escalar; venta inicial bajo categoría "development kit".

## Pendiente

- [ ] Documento 2: BOM detallado con proveedores y links.
- [ ] Diseño del PCB del HAT (LoRa + GPS + RTC + batería).
- [ ] Diseño del case (impresión 3D / CNC aluminio).
