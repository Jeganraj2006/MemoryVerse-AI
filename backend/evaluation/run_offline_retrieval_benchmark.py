"""Reproducible offline retrieval baseline over synthetic demo documents."""
from __future__ import annotations
import argparse,json,subprocess
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
ROOT=Path(__file__).resolve().parents[2];TITLE_BY_FILE={"python_data_science_cert.pdf":"Python Data Science Certification","sentiment_analysis_project.pdf":"Sentiment Analysis Project","smart_india_hackathon_winner.pdf":"Smart India Hackathon Winner","data_analytics_internship_offer.pdf":"Data Analytics Internship"}
def pdf_text(path):return subprocess.run(["pdftotext",str(path),"-"],check=True,capture_output=True,text=True).stdout
def run(path,k):
 titles=list(TITLE_BY_FILE.values());texts=[pdf_text(ROOT/"demo"/f) for f in TITLE_BY_FILE];cases=json.loads(path.read_text());vec=TfidfVectorizer(ngram_range=(1,2),stop_words="english");matrix=vec.fit_transform(texts+[c["query"] for c in cases]);sims=cosine_similarity(matrix[len(texts):],matrix[:len(texts)]);correct=0;details=[]
 for case,row in zip(cases,sims):
  ranking=sorted(zip(titles,row),key=lambda x:x[1],reverse=True)[:k];retrieved=[t for t,_ in ranking];matched=bool(set(case["expected_document_titles"])&set(retrieved));correct+=int(matched);details.append({"query":case["query"],"expected":case["expected_document_titles"],"retrieved":[{"title":t,"score":round(float(s),4)} for t,s in ranking],"matched":matched})
 return {"cases":len(cases),f"recall_at_{k}":round(correct/len(cases),4) if cases else 0,"method":"offline TF-IDF cosine baseline over four synthetic demo documents","semantic_embedding_claim":False,"details":details}
def main():
 p=argparse.ArgumentParser();p.add_argument("--file",default="evaluation/sample_benchmark.json");p.add_argument("--k",type=int,default=5);p.add_argument("--output");a=p.parse_args();r=run(Path(a.file),a.k);render=json.dumps(r,indent=2);print(render);Path(a.output).write_text(render+"\n",encoding="utf-8") if a.output else None
if __name__=="__main__":main()
