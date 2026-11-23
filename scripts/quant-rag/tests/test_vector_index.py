import importlib.util
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

SCRIPT = Path(__file__).resolve().parents[1] / "vector_index.py"
spec = importlib.util.spec_from_file_location("quant_rag_vector_index", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

REVISION = "a" * 40

class FakeEmbeddingModel:
    def encode(self, texts, **kwargs):
        # deterministic dimensionality, supports both E5 prefixes
        result = []
        for text in texts:
            result.append([float("arduino" in text.lower()) + 0.1,
                           float("logo" in text.lower()) + 0.1,
                           float(len(text) % 13) + 0.1])
        return np.asarray(result, dtype=np.float32)

class VectorIndexTests(unittest.TestCase):
    def test_build_and_retrieve_with_domain_filter(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            chunks = root / "chunks.jsonl"
            items = []
            for doc, page in [("arduino", 1), ("logo", 2), ("arduino", 3)]:
                fragment = f"Manual {doc}, página {page}"
                items.append({
                    "chunk_id": f"{doc}-p{page:04d}-c001", "doc_id": doc,
                    "page_pdf": page, "text": fragment,
                    "text_sha256": hashlib.sha256(fragment.encode()).hexdigest()
                })
            chunks.write_text("".join(json.dumps(item) + "\n" for item in items), encoding="utf-8")
            manifest = module.build(chunks, root / "index", FakeEmbeddingModel(),
                                    module.EMBEDDING_MODEL, REVISION)
            self.assertEqual(manifest["chunk_count"], 3)
            results = module.query(root / "index", "arduino", FakeEmbeddingModel(), top_k=2, domain="arduino")
            self.assertEqual(len(results), 2)
            self.assertTrue(all(row["doc_id"] == "arduino" for row in results))
            self.assertEqual([r["rank"] for r in results], [1, 2])
            # reject unannounced modifications to the corpus
            chunks.write_text(chunks.read_text(encoding="utf-8") + "\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                module.query(root / "index", "arduino", FakeEmbeddingModel(), top_k=2)

    def test_non_immutable_revision_rejected(self):
        with self.assertRaises(ValueError):
            module.frozen_revision("main")

    def test_invalid_topk(self):
        with self.assertRaises(ValueError):
            module.retrieve("question", [], np.zeros((0, 3)), FakeEmbeddingModel(), 0)

if __name__ == "__main__":
    unittest.main()
