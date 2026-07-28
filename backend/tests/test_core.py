import unittest

from services.chunking import chunk_extracted_content
from services.evidence import build_skill_evidence
from relationships.relationship_engine import _deterministic_relationships


class ChunkingTests(unittest.TestCase):
    def test_chunks_keep_page_numbers(self):
        chunks = chunk_extracted_content({
            "pages": [
                {"page_number": 1, "text": "A sentence. " * 400},
                {"page_number": 2, "text": "Second page evidence. " * 200},
            ]
        })
        self.assertGreater(len(chunks), 2)
        self.assertEqual(chunks[0].page_number, 1)
        self.assertTrue(any(chunk.page_number == 2 for chunk in chunks))
        self.assertEqual([c.chunk_index for c in chunks], list(range(len(chunks))))


class EvidenceTests(unittest.TestCase):
    def test_repeated_evidence_requires_multiple_sources(self):
        docs = [
            {"id": "1", "title": "Certificate", "type": "Certification", "skills": ["Python"], "technologies": []},
            {"id": "2", "title": "Project", "type": "Project", "skills": ["Python"], "technologies": []},
            {"id": "3", "title": "Internship", "type": "Internship", "skills": ["Python"], "technologies": []},
        ]
        result = build_skill_evidence(docs)[0]
        self.assertEqual(result["evidence_level"], "Repeated")
        self.assertEqual(result["evidence_score"], 100)

    def test_resume_only_skill_is_claimed(self):
        result = build_skill_evidence([
            {"id": "1", "title": "Resume", "type": "Skill", "skills": ["Java"], "technologies": []}
        ])[0]
        self.assertEqual(result["evidence_level"], "Claimed")


class RelationshipTests(unittest.TestCase):
    def test_shared_skill_creates_progression_not_causation(self):
        old = {"id": "1", "title": "Python Certificate", "type": "Certification", "date": "2024-01-01", "skills": ["Python"]}
        new = {"id": "2", "title": "NLP Project", "type": "Project", "date": "2025-01-01", "skills": ["Python"]}
        relationships = _deterministic_relationships(new, [old])
        self.assertEqual(relationships[0]["relation_type"], "SUPPORTS_PROGRESSION_TO")
        self.assertNotIn("LED_TO", {r["relation_type"] for r in relationships})


class SecurityTests(unittest.TestCase):
    def test_rejects_extension_content_mismatch(self):
        from services.security import validate_upload
        with self.assertRaises(ValueError):
            validate_upload("fake.pdf", b"not a pdf")

    def test_accepts_pdf_signature(self):
        from services.security import validate_upload
        validate_upload("sample.pdf", b"%PDF-1.7\nminimal test bytes")


class DateTests(unittest.TestCase):
    def test_normalizes_partial_iso_dates(self):
        from api.upload_route import _normalize_date
        self.assertEqual(_normalize_date("2026"), "2026-01-01")
        self.assertEqual(_normalize_date("2026-07"), "2026-07-01")
        self.assertEqual(_normalize_date("2026-07-17"), "2026-07-17")

    def test_rejects_invalid_dates(self):
        from api.upload_route import _normalize_date
        self.assertIsNone(_normalize_date("17 July 2026"))
        self.assertIsNone(_normalize_date("2026-02-31"))


class ReviewGateTests(unittest.TestCase):
    def test_low_confidence_is_held_out(self):
        from services.review_gate import review_decision
        result = review_decision(0.69, [])
        self.assertTrue(result["review_required"]); self.assertFalse(result["graph_eligible"])

    def test_high_confidence_clean_metadata_is_eligible(self):
        from services.review_gate import review_decision
        result = review_decision(0.91, [])
        self.assertFalse(result["review_required"]); self.assertTrue(result["graph_eligible"])

    def test_review_fields_hold_out_even_above_threshold(self):
        from services.review_gate import review_decision
        result = review_decision(0.95, ["date"])
        self.assertTrue(result["review_required"]); self.assertIn("date", result["reasons"][0])


class RerankerTests(unittest.IsolatedAsyncioTestCase):
    async def test_reranker_orders_by_question_relevance(self):
        from unittest.mock import AsyncMock, patch
        from retrieval.reranker import rerank_chunks
        chunks = [
            {"doc_id": "1", "title": "General Python", "text": "Python basics", "similarity": 0.92},
            {"doc_id": "2", "title": "SQL Internship", "text": "Applied SQL in analytics internship", "similarity": 0.71},
        ]
        response = {"scores": [
            {"candidate_id": "C1", "relevance": 0.2, "reason": "general overlap"},
            {"candidate_id": "C2", "relevance": 0.95, "reason": "direct professional SQL evidence"},
        ]}
        with patch("retrieval.reranker.generate_json", new=AsyncMock(return_value=response)):
            ranked, meta = await rerank_chunks("Where did I apply SQL professionally?", chunks, top_k=2)
        self.assertEqual(meta["status"], "applied")
        self.assertEqual(ranked[0]["doc_id"], "2")
        self.assertEqual(ranked[0]["rerank_score"], 0.95)

    async def test_reranker_failure_preserves_semantic_order(self):
        from unittest.mock import AsyncMock, patch
        from retrieval.reranker import rerank_chunks
        chunks = [
            {"doc_id": "1", "title": "First", "text": "first", "similarity": 0.9},
            {"doc_id": "2", "title": "Second", "text": "second", "similarity": 0.8},
        ]
        with patch("retrieval.reranker.generate_json", new=AsyncMock(side_effect=RuntimeError("model unavailable"))):
            ranked, meta = await rerank_chunks("question", chunks, top_k=2)
        self.assertEqual(meta["status"], "unavailable")
        self.assertEqual([row["doc_id"] for row in ranked], ["1", "2"])


if __name__ == "__main__":
    unittest.main()
