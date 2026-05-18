# rag/ — Pipeline RAG (Capa 3)

Construye y consulta la base de conocimiento de supervivencia que el LLM usa
como contexto (Retrieval Augmented Generation).

> **Estado: stub.** `ingest.py` define la estructura del pipeline pero no
> ejecuta embeddings reales todavía. Ver los `TODO` en el archivo.

## Stack previsto

| Pieza            | Elección             | Por qué                                  |
|------------------|----------------------|-------------------------------------------|
| Base vectorial   | SQLite + `sqlite-vec`| Embedded, nativo en Android NDK y Pi.     |
| Embeddings       | `all-MiniLM-L6-v2`   | 90 MB, multiplataforma, Apache 2.0.       |
| Formato corpus   | PDF / TXT / Markdown | Survivor Library, FM 21-76, Kiwix, etc.   |

El índice resultante es un único archivo `.db` portable que se copia entre
dispositivos.

## Uso previsto

```sh
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Ingestar el corpus en corpus/ -> survival.db
python3 ingest.py --corpus corpus/ --out survival.db
```

## Corpus

Dejá los documentos fuente en `corpus/` (ignorado por git salvo `.gitkeep`).
Solo incluir material con licencia compatible con redistribución comercial
(CC BY, CC BY-SA, Apache, MIT, dominio público).

## Pendiente

- [ ] Extracción de texto de PDF.
- [ ] Chunking con solapamiento.
- [ ] Generación de embeddings con `sentence-transformers`.
- [ ] Escritura a `sqlite-vec`.
- [ ] Función de consulta (top-k) para enchufar al `LlmEngine` de `../api`.
