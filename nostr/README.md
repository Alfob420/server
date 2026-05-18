# nostr/ — Gateway Nostr (transporte global)

Da **alcance global gratis** cuando el dispositivo tiene internet: publica y
recibe mensajes a través de relays [Nostr](https://nostr.com) públicos, sin
servidores propios. Es el transporte de última milla cuando la mesh local
(LoRa/BLE) no llega al destino. **Funcional.**

## Componentes

| Archivo / módulo       | Rol                                                  |
|------------------------|------------------------------------------------------|
| `smnostr/protocol.py`  | Claves secp256k1, eventos (NIP-01), DMs cifrados (NIP-04). |
| `smnostr/gateway.py`   | `NostrGateway`: identidad, relays, buzón.            |
| `service.py`           | Servicio HTTP que la API (`../api`) consulta.        |

## Cómo funciona

- El nodo tiene una identidad Nostr persistente: un par de claves secp256k1.
  La clave pública (hex x-only) es su dirección global.
- Se conecta a varios relays públicos; cada uno en su hilo, con reconexión
  automática.
- Los mensajes son **directos y cifrados extremo a extremo** (NIP-04, kind 4):
  solo el destinatario puede leerlos, aunque pasen por relays públicos.

## Uso

```sh
pip install -r requirements.txt          # o usar el venv de scripts/setup.sh

python3 service.py --secret nostr.key --port 8092
```

La clave privada se crea en `--secret` al primer arranque (permisos 600). El
archivo de clave **no debe versionarse ni compartirse**.

## Servicio HTTP

| Método | Ruta      | Descripción                                          |
|--------|-----------|------------------------------------------------------|
| GET    | `/health` | Estado: pubkey, relays conectados, nº de mensajes.   |
| GET    | `/inbox`  | Mensajes recibidos (opcional `?since=<id>`).         |
| POST   | `/send`   | Body `{"to": "<pubkey hex>", "text": "..."}`.        |

## Relays

Por defecto usa `relay.damus.io`, `nos.lol` y `relay.primal.net`. Se ajustan
con `--relays` (lista separada por comas).

## Pendiente

- [ ] NIP-17/NIP-44 (cifrado moderno) en lugar de NIP-04.
- [ ] Reenvío automático: si un mensaje de la mesh local no se entrega, saltar
      a Nostr (puente mesh ⇄ Nostr).
- [ ] Codificación bech32 (`npub`/`nsec`) para mostrar claves.
