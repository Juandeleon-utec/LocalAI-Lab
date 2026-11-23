"""Unit tests for the isolated PDF preparation stage.

Run: python -m unittest discover -s scripts/quant-rag/tests -v
Requires: pymupdf
"""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

import fitz

SCRIPT = Path(__file__).resolve().parents[1] / "prepare_corpus.py"
spec = importlib.util.spec_from_file_location("quant_rag_prepare_corpus", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class CorpusPreparationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.inputs = self.root / "manuals"
        self.outputs = self.root / "output"
        self.inputs.mkdir()
        for name in module.SOURCES.values():
            with fitz.open() as pdf:
                page = pdf.new_page()
                page.insert_text((72, 72), "Texto de prueba")
                pdf.save(self.inputs / name)

    def tearDown(self):
        self.temp.cleanup()

    def test_only_manuals_are_indexed_and_pages_are_one_based(self):
        result = module.prepare(self.inputs, self.outputs)
        self.assertEqual(result["total_pages"], 2)
        records = [json.loads(line) for line in (self.outputs / "pages.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertEqual(len(records), 2)
        self.assertEqual({r["page_pdf"] for r in records}, {1})
        self.assertEqual({r["doc_id"] for r in records}, {"arduino", "logo"})
        self.assertTrue(all("Texto de prueba" in row["text"] for row in records))
        inventory = json.loads((self.outputs / "source_inventory.json").read_text(encoding="utf-8"))
        self.assertEqual(len(inventory["sources"]), 2)
        self.assertTrue(all(len(item["sha256"]) == 64 for item in inventory["sources"]))

    def test_unexpected_pdf_is_rejected(self):
        with fitz.open() as pdf:
            pdf.new_page()
            pdf.save(self.inputs / "questions_answers.pdf")
        with self.assertRaises(ValueError):
            module.prepare(self.inputs, self.outputs)
        self.assertFalse((self.outputs / "pages.jsonl").exists())

    def test_missing_manual_is_rejected(self):
        (self.inputs / "Logo_s.pdf").unlink()
        with self.assertRaises(FileNotFoundError):
            module.prepare(self.inputs, self.outputs)

if __name__ == "__main__":
    unittest.main()
