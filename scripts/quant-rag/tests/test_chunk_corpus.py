import importlib.util
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "chunk_corpus.py"
spec = importlib.util.spec_from_file_location("quant_rag_chunk", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class ChunkCorpusTests(unittest.TestCase):
    def test_no_cross_page_chunks_deterministic(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "pages.jsonl"
            pages = []
            for doc, page in (("arduino", 1), ("arduino", 2), ("logo", 1)):
                text = (f"{doc} PAGE {page} some reference text. " * 100).strip()
                pages.append({
                    "doc_id": doc, "source_file": doc + ".pdf",
                    "page_pdf": page, "text": text,
                    "text_sha256": hashlib.sha256(text.encode()).hexdigest()
                })
            source.write_text("".join(json.dumps(p) + "\n" for p in pages), encoding="utf-8")
            manifest = module.chunk_pages(source, root / "out", size=300, overlap=50)
            first = (root / "out" / "chunks.jsonl").read_bytes()
            module.chunk_pages(source, root / "out", size=300, overlap=50)
            self.assertEqual(first, (root / "out" / "chunks.jsonl").read_bytes())
            chunks = [json.loads(s) for s in first.decode().splitlines()]
            self.assertGreater(len(chunks), 3)
            self.assertEqual(manifest["input_pages"], 3)
            self.assertEqual(len({c["chunk_id"] for c in chunks}), len(chunks))
            self.assertTrue(all(c["text"].startswith(c["doc_id"]) or "reference text" in c["text"] for c in chunks))
            for c in chunks:
                original = next(p for p in pages if (p["doc_id"], p["page_pdf"]) == (c["doc_id"], c["page_pdf"]))
                self.assertEqual(c["text"], original["text"][c["start_char"]:c["end_char"]].strip())

    def test_reject_bad_hash(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "pages.jsonl"
            source.write_text(json.dumps({
                "doc_id": "arduino", "source_file": "manual.pdf",
                "page_pdf": 1, "text": "example", "text_sha256": "bad"
            }) + "\n")
            with self.assertRaises(ValueError):
                module.chunk_pages(source, root / "out")

    def test_reject_invalid_parameters(self):
        with self.assertRaises(ValueError):
            module.chunk_pages(Path("nonexistent.jsonl"), Path("output"), size=100, overlap=50)

if __name__ == "__main__":
    unittest.main()
