# rag/ — Pipeline RAG (Capa 3)

Construye y consulta la base de conocimiento de supervivencia que el LLM usa
como contexto (Retrieval Augmented Generation). **Funcional.**

## Componentes

| Archivo / módulo        | Rol                                                  |
|-------------------------|------------------------------------------------------|
| `smrag/embeddings.py`   | Embeddings ONNX (MiniLM) con fallback hash.          |
| `smrag/chunking.py`     | Fragmentación de documentos por párrafos.            |
| `smrag/extract.py`      | Extracción de texto desde txt/md/pdf.                |
| `smrag/store.py`        | Almacén vectorial SQLite + sqlite-vec.               |
| `smrag/pipeline.py`     | Orquestación de la ingesta.                          |
| `ingest.py`             | CLI: indexa `corpus/` en `survival.db`.              |
| `query.py`              | CLI: consulta el índice (depuración).                |
| `service.py`            | Servicio HTTP que la API (`../api`) consulta.        |

## Modelo de embeddings

Por defecto se usa **`paraphrase-multilingual-MiniLM-L12-v2`** en formato ONNX
(~118 MB, cuantizado). Documento 1 mencionaba `all-MiniLM-L6-v2`, pero ese
modelo es solo inglés y la recuperación sobre un corpus en español es pobre; el
modelo multilingüe es el correcto para el producto. Ambos producen vectores de
384 dimensiones y se puede elegir con `--model {multilingual,english}`.

El modelo se descarga de Hugging Face al primer uso y se cachea en `models/`
(ignorado por git). Sin red, el pipeline degrada a un embedder hash
determinista (`--embedder hash`), útil solo para probar la mecánica.

## Uso

```sh
pip install -r requirements.txt          # o usar el venv de scripts/setup.sh

# 1. Indexar el corpus
python3 ingest.py --corpus corpus/ --out survival.db

# 2. Probar la recuperación
python3 query.py "como purifico agua del rio"

# 3. Levantar el servicio HTTP que consume la API
python3 service.py --db survival.db --port 8090
```

## Servicio HTTP

| Método | Ruta        | Descripción                                       |
|--------|-------------|---------------------------------------------------|
| GET    | `/health`   | Estado, backend de embeddings y nº de chunks.     |
| POST   | `/retrieve` | Body `{"query": "...", "k": 4}` → `{"hits": [...]}`. |

## Corpus

`corpus/` incluye un corpus de muestra (material original del proyecto, licencia
libre) sobre agua, refugio, fuego y señalización. Para producción se suma
material con licencia compatible con redistribución (CC BY/BY-SA, dominio
público): Survivor Library, FM 21-76, Wikipedia offline, etc. NO incluir libros
con copyright tradicional.
