# Synthetic Demo Evidence Journey

**All four PDFs in this directory are fictional hackathon fixtures. They are visibly watermarked and must never be represented as real credentials, awards, projects, or employment records.**

The files form a controlled demonstration path:

1. Python data-science certification fixture
2. Sentiment-analysis project fixture
3. Hackathon-achievement fixture
4. Data-analytics internship fixture

Use **Load hackathon demo journey** on the Upload page. The seed endpoint applies curated fixture metadata so the judge demo remains stable even when an external AI call is unavailable. Normal user uploads still use extraction and AI structuring.

Recommended demo question:

> What evidence proves that I am prepared for a data analyst role?

To regenerate the fixtures:

```bash
pip install -r demo/requirements.txt
python demo/generate_seeds.py
```
