import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
spec = importlib.util.spec_from_file_location("quant_rag_eval", ROOT / "evaluate_retrieval.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class RetrievalEvaluationTests(unittest.TestCase):
    def test_matching_page_of_wrong_manual_not_credited(self):
        passages = [
            {"rank": 1, "doc_id": "logo", "page_pdf": 6},
            {"rank": 2, "doc_id": "arduino", "page_pdf": 6},
        ]
        metric = module.page_metrics(passages, [6], "arduino")
        self.assertEqual(metric["first_relevant_rank"], 2)
        self.assertEqual(metric["hit_at_k"], 1)
        self.assertAlmostEqual(metric["reciprocal_rank"], 0.5)

    def test_bad_dataset_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "questions.json"
            source.write_text(json.dumps([
                {"id": "ARD-001", "dominio": "arduino",
                 "pregunta": "¿Qué es setup?", "paginas_pdf": [6]},
                {"id": "ARD-001", "dominio": "arduino",
                 "pregunta": "¿Qué es loop?", "paginas_pdf": [7]},
            ]), encoding="utf-8")
            with self.assertRaises(ValueError):
                module.validate_questions(source, strict_count=False)

    def test_frozen_context_contains_no_ground_truth(self):
        fake_passages = [{"rank": 1, "chunk_id": "arduino-p0006-c001",
                          "doc_id": "arduino", "page_pdf": 6,
                          "score": 0.9, "text": "Manual: setup y loop",
                          "text_sha256": "abc"}]
        question = {
            "id": "ARD-001", "dominio": "arduino",
            "pregunta": "¿Qué funciones existen?",
            "paginas_pdf": [6], "respuesta_referencia": "SECRET ANSWER MARKER",
        }
        with patch.object(module, "query", return_value=fake_passages):
            evaluations, contexts = module.run([question], Path("."), object(), top_k=5)
        self.assertEqual(len(evaluations), 2)
        self.assertEqual(len(contexts), 2)
        self.assertTrue(all(e["hit_at_k"] == 1 for e in evaluations))
        self.assertNotIn("SECRET ANSWER MARKER", json.dumps(contexts))
        self.assertNotIn("paginas_pdf", json.dumps(contexts))
        self.assertEqual(contexts[0]["policy"], "global")
        self.assertEqual(contexts[1]["policy"], "domain")

    def test_aggregates_by_domain_and_policy(self):
        fake = [
            {"domain": domain, "policy": policy, "hit_at_k": hit,
             "reciprocal_rank": float(hit), "page_recall_at_k": float(hit)}
            for domain, policy, hit in [
                ("arduino", "global", 1), ("logo", "global", 0),
                ("arduino", "domain", 1), ("logo", "domain", 1),
            ]
        ]
        summary = module.summarize(fake, top_k=5)
        self.assertEqual(summary["global"]["all"]["hit_at_5"], 0.5)
        self.assertEqual(summary["domain"]["all"]["hit_at_5"], 1.0)

if __name__ == "__main__":
    unittest.main()
