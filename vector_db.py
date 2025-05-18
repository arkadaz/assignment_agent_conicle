import pandas as pd
import qdrant_client
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer

import settings
from models import Competency


def load_competency_data(file_path=settings.COMPETENCY_DATA_PATH):
    try:
        print(f"Attempting to load data from: {file_path}")
        df = pd.read_csv(file_path)
        print(f"Successfully loaded data with {len(df)} rows")
        df.columns = [col.strip().lower() for col in df.columns]
        df = df.dropna(subset=["competency", "description"])
        print(f"After cleaning, {len(df)} rows remain")
        df["competency"] = df["competency"].str.strip()
        df["description"] = df["description"].str.strip()
        return df
    except FileNotFoundError:
        print(f"FileNotFoundError: File not found at {file_path}")
        raise FileNotFoundError(f"Error: Competency data file not found at {file_path}")
    except Exception as e:
        print(f"Exception loading data: {str(e)}")
        raise Exception(f"Error loading competency data from {file_path}: {e}")


def init_model_and_db():
    model = SentenceTransformer(settings.MODEL_NAME)
    client = qdrant_client.QdrantClient(location=":memory:")
    return model, client


def setup_vector_db(client, model, df, collection_name=settings.QDRANT_COLLECTION_NAME):
    vector_size = model.get_sentence_embedding_dimension()

    try:
        client.get_collection(collection_name=collection_name)
        client.delete_collection(collection_name=collection_name)
        print(f"Deleted existing collection: {collection_name}")
    except:
        pass

    client.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(
            size=vector_size,
            distance=models.Distance.COSINE,
        ),
    )

    texts = (df["competency"] + ". " + df["description"]).tolist()
    embeddings = model.encode(texts)

    points = []
    for i, (_, row) in enumerate(df.iterrows()):
        points.append(
            models.PointStruct(
                id=i,
                vector=embeddings[i].tolist(),
                payload={
                    "competency": row["competency"],
                    "description": row["description"],
                },
            )
        )

    # Calculate total points AFTER populating the list
    total_points = len(points)

    batch_size = 100
    uploaded_count = 0
    for i in range(0, total_points, batch_size):
        batch = points[i : i + batch_size]
        client.upsert(collection_name=collection_name, points=batch, wait=True)
        uploaded_count += len(batch)

    count = client.count(collection_name=collection_name, exact=True).count
    return count


def search_competencies(
    client,
    model,
    query,
    collection_name=settings.QDRANT_COLLECTION_NAME,
    top_n=settings.TOP_N,
    similarity_threshold=settings.SIMILARITY_THRESHOLD,
) -> list[Competency]:
    query_vector = model.encode(query)

    results = client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=top_n,
    )

    competencies = []
    for res in results:
        if res.score > similarity_threshold:
            competencies.append(
                Competency(
                    name=res.payload["competency"],
                    description=res.payload["description"],
                    similarity_score=res.score,
                )
            )

    competencies.sort(key=lambda x: x.similarity_score, reverse=True)

    return competencies
