import redis
import json
import numpy as np

r = redis.Redis(host="localhost", port=6379, db=0)

doc_id = "e8688352-dbaf-4a66-ac8d-9a5e03e3d0bc"

text = r.get(f"text:{doc_id}")
meta = r.get(f"meta:{doc_id}")
embedding = r.get(f"embedding:{doc_id}")

# Decode text and metadata normally
text_str = text.decode("utf-8") if text else None
metadata_dict = json.loads(meta.decode("utf-8")) if meta else None

# Decode embedding from binary float32 buffer
embedding_vector = (
    np.frombuffer(embedding, dtype=np.float32).tolist() if embedding else None
)

document = {
    "id": doc_id,
    "text": text_str,
    "metadata": metadata_dict,
    "embedding": embedding_vector
}

print(json.dumps(document, indent=2))
