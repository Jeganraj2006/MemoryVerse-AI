"""Secure file ingestion and portfolio seeding."""
from __future__ import annotations

import mimetypes
import re
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile

from api.auth_middleware import get_current_user
from db.supabase_client import (
    find_document_by_hash,
    get_all_documents,
    store_document,
    store_relationship,
)
from embeddings.embed_service import embed_chunks
from embeddings.vector_store import add_document_chunks
from ingestion.file_router import extract_text
from ingestion.llm_structurer import structure_document
from relationships.relationship_engine import find_relationships
from services.chunking import chunk_extracted_content
from services.review_gate import document_is_graph_eligible, review_decision
from services.security import sha256_bytes, validate_upload

router = APIRouter()

DEMO_METADATA = {
    "python_data_science_cert.pdf": {
        "title": "Python for Data Science & Machine Learning Bootcamp",
        "type": "Certification",
        "issuer": "Coursera | DeepLearning.AI",
        "organization": "DeepLearning.AI",
        "date": "2023-03-15",
        "skills": ["Python", "NumPy", "Pandas", "Matplotlib", "Scikit-learn", "Machine Learning", "Data Visualization", "Statistical Analysis"],
        "technologies": ["Jupyter Notebooks"],
        "achievements": ["Completed with 94.5% and Distinction"],
        "tags": ["python", "data science", "machine learning", "certification"],
        "summary": "Certificate showing completion of a 42-hour Python for Data Science and Machine Learning bootcamp with a Distinction grade.",
    },
    "sentiment_analysis_project.pdf": {
        "title": "Sentiment Analysis on Social Media Data",
        "type": "Project",
        "issuer": "National Institute of Technology, Trichy",
        "organization": "National Institute of Technology, Trichy",
        "date": "2024-11-01",
        "skills": ["Python", "Natural Language Processing", "Machine Learning", "Deep Learning", "Data Analysis"],
        "technologies": ["TensorFlow", "Keras", "BERT", "Hugging Face Transformers", "NLTK", "SpaCy", "Pandas", "NumPy", "Scikit-learn"],
        "achievements": ["Reported 89.3% held-out test accuracy and 0.887 F1-score"],
        "tags": ["nlp", "sentiment analysis", "bert", "project"],
        "summary": "Capstone report for a BERT-based sentiment analysis pipeline trained on social-media data, including methodology and reported evaluation metrics.",
    },
    "smart_india_hackathon_winner.pdf": {
        "title": "Smart India Hackathon 2024 — Winner",
        "type": "Achievement",
        "issuer": "Government of India — Ministry of Education Innovation Cell",
        "organization": "Smart India Hackathon",
        "date": "2024-12-09",
        "skills": ["Python", "Natural Language Processing", "Computer Vision", "Geospatial Analysis", "Teamwork"],
        "technologies": ["FastAPI", "TensorFlow", "React.js", "PostgreSQL", "GDAL"],
        "achievements": ["Winner — 1st Prize"],
        "tags": ["hackathon", "achievement", "disaster response", "winner"],
        "summary": "Winner certificate for an AI-powered disaster-response coordination project at Smart India Hackathon 2024.",
    },
    "data_analytics_internship_offer.pdf": {
        "title": "Data Analytics Internship Offer",
        "type": "Internship",
        "issuer": "DataSpark Analytics Pvt. Ltd.",
        "organization": "DataSpark Analytics Pvt. Ltd.",
        "location": "Bangalore — Hybrid",
        "date": "2025-01-12",
        "skills": ["Python", "SQL", "Power BI", "Pandas", "NumPy", "Machine Learning", "Excel", "Tableau", "Data Engineering"],
        "technologies": ["Apache Airflow", "Power BI"],
        "achievements": [],
        "tags": ["internship", "data analytics", "business intelligence", "data engineering"],
        "summary": "Offer letter for a six-month Data Analytics internship involving dashboards, SQL, exploratory analysis, and data-pipeline automation.",
    },
}



@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user),
):
    filename = file.filename or "document"
    file_bytes = await file.read()
    try:
        validate_upload(filename, file_bytes)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    file_hash = sha256_bytes(file_bytes)
    duplicate = await find_document_by_hash(user_id, file_hash)
    if duplicate:
        raise HTTPException(
            status_code=409,
            detail=f"This exact file already exists as '{duplicate.get('title')}'.",
        )

    try:
        extracted = await extract_text(file_bytes, filename)
        structured = await structure_document(extracted.get("text", ""), filename)
        chunks = [chunk.to_dict() for chunk in chunk_extracted_content(extracted)]
        normalized_date = _normalize_date(structured.date)
        if structured.date and not normalized_date and "date" not in structured.fields_needing_review:
            structured.fields_needing_review.append("date")
        gate = review_decision(structured.confidence, structured.fields_needing_review)
        metadata = {
            **structured.model_dump(),
            "date": normalized_date,
            "raw_text": extracted.get("text", ""),
            "extracted_pages": extracted.get("pages") or [],
            "page_count": extracted.get("page_count") or 1,
            "mime_type": file.content_type or mimetypes.guess_type(filename)[0],
            "file_hash": file_hash,
            "user_id": user_id,
            "source_kind": "file",
            "trust_level": "self_uploaded",
            "verification_status": "self_uploaded",
            "verification_details": {
                "sha256": file_hash,
                "extraction_method": extracted.get("method"),
                "original_date_value": structured.date,
            },
            "review_required": gate["review_required"],
        }
        stored = await store_document(metadata, file_bytes, filename)

        indexing_warning = None
        held_out_reason = None
        if gate["graph_eligible"]:
            try:
                vectors = await embed_chunks(chunks, stored["title"])
                await add_document_chunks(stored, chunks, vectors)
                background_tasks.add_task(_discover_and_store_relationships, stored, user_id)
            except Exception as exc:
                indexing_warning = f"Document saved, but semantic indexing needs attention: {exc}"
                print(f"[Upload] Indexing failed: {exc}")
        else:
            held_out_reason = "; ".join(gate["reasons"])
            indexing_warning = "Held out of semantic search and the knowledge graph until metadata review is confirmed."
        return {
            "status": "success",
            "document": stored,
            "processing": {
                "extraction_method": extracted.get("method"),
                "page_count": extracted.get("page_count") or 1,
                "chunk_count": len(chunks),
                "review_required": metadata["review_required"],
                "fields_needing_review": structured.fields_needing_review,
                "indexing_warning": indexing_warning,
                "graph_eligible": gate["graph_eligible"],
                "held_out_of_knowledge_graph": not gate["graph_eligible"],
                "review_confidence_threshold": gate["threshold"],
                "held_out_reason": held_out_reason,
            },
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Document processing failed: {exc}")


@router.post("/seed-portfolio")
async def seed_portfolio(
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user),
):
    demo_dir = Path(__file__).resolve().parents[2] / "demo"
    filenames = [
        "python_data_science_cert.pdf",
        "sentiment_analysis_project.pdf",
        "smart_india_hackathon_winner.pdf",
        "data_analytics_internship_offer.pdf",
    ]
    imported = []
    skipped = []
    for filename in filenames:
        path = demo_dir / filename
        if not path.exists():
            continue
        file_bytes = path.read_bytes()
        file_hash = sha256_bytes(file_bytes)
        if await find_document_by_hash(user_id, file_hash):
            skipped.append(filename)
            continue
        extracted = await extract_text(file_bytes, filename)
        fixed = DEMO_METADATA[filename]
        chunks = [chunk.to_dict() for chunk in chunk_extracted_content(extracted)]
        metadata = {
            **fixed,
            "confidence": 1.0,
            "fields_needing_review": [],
            "raw_text": extracted.get("text", ""),
            "extracted_pages": extracted.get("pages") or [],
            "page_count": extracted.get("page_count") or 1,
            "mime_type": "application/pdf",
            "file_hash": file_hash,
            "user_id": user_id,
            "source_kind": "file",
            "trust_level": "self_uploaded",
            "verification_status": "self_uploaded",
            "verification_details": {"sha256": file_hash, "demo_seed": True, "metadata_source": "curated_demo_fixture"},
            "review_required": False,
        }
        stored = await store_document(metadata, file_bytes, filename)
        try:
            await add_document_chunks(stored, chunks, await embed_chunks(chunks, stored["title"]))
        except Exception as exc:
            print(f"[Seed] Indexing failed for {filename}: {exc}")
        await _discover_and_store_relationships(stored, user_id)
        imported.append(stored)
    return {"status": "success", "imported": imported, "skipped": skipped}


async def _discover_and_store_relationships(new_document: dict, user_id: str) -> None:
    if not document_is_graph_eligible(new_document):
        return
    existing = [doc for doc in await get_all_documents(user_id=user_id) if str(doc.get("id")) != str(new_document.get("id")) and document_is_graph_eligible(doc)]
    for relationship in await find_relationships(new_document, existing):
        await store_relationship(
            relationship["source_id"],
            relationship["target_id"],
            relationship["relation_type"],
            relationship["label"],
            relationship["confidence"],
            user_id=user_id,
            evidence=relationship.get("evidence"),
        )


def _normalize_date(value: str | None) -> str | None:
    if not value:
        return None
    text = str(value).strip()
    if re.fullmatch(r"\d{4}", text):
        text = f"{text}-01-01"
    elif re.fullmatch(r"\d{4}-\d{2}", text):
        text = f"{text}-01"
    elif not re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        return None
    try:
        return datetime.strptime(text, "%Y-%m-%d").date().isoformat()
    except ValueError:
        return None
