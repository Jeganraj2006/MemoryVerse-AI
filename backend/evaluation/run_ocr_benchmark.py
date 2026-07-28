"""Measure OCR key-field recovery on a labeled image manifest."""
from __future__ import annotations
import argparse,json,re
from pathlib import Path
import pytesseract
from PIL import Image
def normalize(value):return [t for t in re.findall(r"[a-z0-9]+",value.casefold()) if len(t)>1]
def recovered(expected,text):
 e=normalize(expected);tokens=set(normalize(text));coverage=sum(t in tokens for t in e)/len(e) if e else 0;return coverage>=.70,round(coverage,3)
def run(manifest_path):
 rows=json.loads(manifest_path.read_text(encoding="utf-8"));total=correct=0;details=[]
 for row in rows:
  text=pytesseract.image_to_string(Image.open(manifest_path.parent/row["image"]),config="--psm 6");fields=[]
  for field in row["expected_fields"]:
   matched,coverage=recovered(field,text);total+=1;correct+=int(matched);fields.append({"field":field,"recovered":matched,"token_coverage":coverage})
  details.append({"image":row["image"],"source_document":row["source_document"],"fields":fields,"ocr_excerpt":" ".join(text.split())[:300]})
 return {"fixture_count":len(rows),"expected_field_count":total,"recovered_field_count":correct,"ocr_key_field_recovery":round(correct/total,4) if total else 0,"metric_definition":"Expected field recovered when >=70% of normalized field tokens occur in Tesseract output.","dataset_disclosure":"20 synthetically degraded scans generated from four visibly watermarked demo documents; not a real-world production dataset.","details":details}
def main():
 p=argparse.ArgumentParser();p.add_argument("--manifest",default="evaluation/ocr_benchmark_manifest.json");p.add_argument("--output");a=p.parse_args();r=run(Path(a.manifest));render=json.dumps(r,indent=2);print(render);Path(a.output).write_text(render+"\n",encoding="utf-8") if a.output else None
if __name__=="__main__":main()
