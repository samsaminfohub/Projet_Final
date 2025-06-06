FROM python:3.9-slim

WORKDIR /mlflow

RUN pip install mlflow psycopg2-binary

EXPOSE 5000

CMD ["mlflow", "server", \
     "--backend-store-uri", "postgresql://admin:secret@postgres:5432/movie_recommender", \
     "--default-artifact-root", "/mlflow/artifacts", \
     "--host", "0.0.0.0"]