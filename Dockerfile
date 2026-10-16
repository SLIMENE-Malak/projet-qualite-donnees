FROM apache/airflow:3.3.2

COPY requirements.txt /requirements.txt

RUN python -m pip install --no-cache-dir -r /requirements.txt

# Télécharger le modèle une seule fois lors du build
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')"