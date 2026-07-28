# Owner-supplied real scan benchmark

The committed 82% result uses reproducibly degraded synthetic fixtures so anyone can reproduce it. For a stronger final submission, place 20 genuinely scanned, anonymized certificates or letters in this directory and create a separate manifest using `real_ocr_manifest.example.json`.

Do not overwrite the synthetic result. Save the real-world run separately:

```bash
python -m evaluation.run_ocr_benchmark \
  --manifest evaluation/real_scans/real_ocr_manifest.json \
  --output evaluation/results/real_ocr_benchmark_result.json
```

Before publishing:

- remove names, registration numbers, addresses, QR codes, signatures, and credential IDs;
- obtain permission from the document owners;
- label the dataset size and scan conditions;
- report the result exactly, including failures.
