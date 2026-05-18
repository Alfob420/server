# Roadmap de desarrollo

## Fase 0 — Validación (mes 1-2)

- [ ] Prototipo funcional con Pi 5 + LoRa HAT + LLM corriendo + Reticulum activo.
- [ ] Pipeline RAG con corpus inicial (1000-5000 documentos de supervivencia).
- [ ] Demo end-to-end: consulta → respuesta del LLM con contexto RAG → envío
      del resultado por mesh LoRa a otro nodo.
- [ ] Documentación pública en GitHub, anuncio en r/cyberdeck, r/meshtastic,
      HackerNews.

## Fase 1 — Comunidad DIY (mes 3-5)

- [ ] Repo público con BOM detallado, links a proveedores, imagen `.img`.
- [ ] Guía de ensamblado paso a paso con fotos.
- [ ] Discord/Matrix para soporte de la comunidad.
- [ ] Meta: 100-500 builds documentados por la comunidad.

## Fase 2 — Hardware ensamblado Tier 2 (mes 6-9)

- [ ] Diseño final del case (CNC aluminio o impresión 3D resina premium).
- [ ] PCB custom integrando LoRa + GPS + RTC + batería en un solo HAT.
- [ ] Primera producción limitada (50-100 unidades) con feedback de Fase 1.
- [ ] Crowdfunding opcional (Crowd Supply).

## Fase 3 — Escalado (mes 10+)

- [ ] Tier 1 (Pocket Node) y Tier 3 (Base Station).
- [ ] Distribuidores en regiones clave (LATAM, EU, US).
- [ ] Programa de descuentos para periodistas, activistas, ONGs de emergencia.

## Hitos técnicos inmediatos

1. Dos dispositivos chateando por LoRa a 100 m de distancia, cada uno con su
   LLM local.
2. Pipeline RAG con 100 documentos de supervivencia indexados.
3. UI web (PWA) accesible desde el celular conectado al hotspot.
