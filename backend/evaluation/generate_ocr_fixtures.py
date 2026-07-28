"""Generate reproducible degraded scan fixtures from visibly synthetic demo PDFs."""
from __future__ import annotations
import hashlib,json,random
from pathlib import Path
from pdf2image import convert_from_path
from PIL import Image,ImageEnhance,ImageFilter
ROOT=Path(__file__).resolve().parents[2];OUTPUT=Path(__file__).with_name("ocr_fixture_scans")
EXPECTED={
"python_data_science_cert.pdf":["Certificate of Completion","Arjun Mehta","Python for Data Science","DeepLearning.AI","March 15 2023"],
"sentiment_analysis_project.pdf":["Sentiment Analysis","Arjun Mehta","National Institute of Technology","November 2024","BERT"],
"smart_india_hackathon_winner.pdf":["Smart India Hackathon 2024","Winner 1st Prize","Arjun Mehta","IIT Bombay","December 2024"],
"data_analytics_internship_offer.pdf":["Internship Offer Letter","Data Analytics Intern","DataSpark Analytics","January 12 2025","Power BI"]}
def degrade(image:Image.Image,variant:int,seed:int)->Image.Image:
 rng=random.Random(seed);image=image.convert("L");scale=[.82,.72,.78,.68,.74][variant];image=image.resize((max(600,int(image.width*scale)),max(780,int(image.height*scale))));image=image.rotate([1.3,-1.7,.7,-1.0,1.9][variant],expand=True,fillcolor=245);image=ImageEnhance.Contrast(image).enhance([.86,.76,.82,.70,.78][variant]);image=ImageEnhance.Brightness(image).enhance([.98,.92,1.03,.95,.90][variant]);image=image.filter(ImageFilter.GaussianBlur([.35,.55,.45,.68,.50][variant]));pixels=image.load();specks=int(image.width*image.height*[.00035,.0007,.0005,.0009,.00065][variant]);
 for _ in range(specks):
  x=rng.randrange(image.width);y=rng.randrange(image.height);pixels[x,y]=0 if rng.random()<.55 else 255
 return image
def main():
 OUTPUT.mkdir(parents=True,exist_ok=True);manifest=[]
 for pdf_name,fields in EXPECTED.items():
  page=convert_from_path(ROOT/"demo"/pdf_name,dpi=185,first_page=1,last_page=1)[0];seed=int(hashlib.sha256(pdf_name.encode()).hexdigest()[:8],16)
  for variant in range(5):
   result=degrade(page,variant,seed+variant);filename=f"{Path(pdf_name).stem}__messy_{variant+1}.jpg";result.save(OUTPUT/filename,"JPEG",quality=[68,58,64,52,60][variant],optimize=True);manifest.append({"image":f"ocr_fixture_scans/{filename}","source_document":pdf_name,"expected_fields":fields,"fixture_kind":"synthetically degraded scan of a visibly watermarked demo document"})
 Path(__file__).with_name("ocr_benchmark_manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8");print(f"Generated {len(manifest)} degraded scan fixtures")
if __name__=="__main__":main()
