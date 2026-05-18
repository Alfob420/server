"""smrag — pipeline RAG de Survival Mesh (Capa 3).

Construye y consulta la base de conocimiento de supervivencia que el LLM usa
como contexto. Submódulos:

- embeddings: vectores de texto (backend ONNX all-MiniLM-L6-v2 + fallback hash).
- chunking:   fragmentación de documentos.
- extract:    extracción de texto desde txt/md/pdf.
- store:      almacén vectorial sobre SQLite + sqlite-vec.
- pipeline:   orquestación de la ingesta.
"""

__version__ = "0.1.0"
