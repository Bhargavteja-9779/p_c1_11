"""Build journal_benchmark.csv from Critical Care ML research articles (PMC JATS full text)."""
import json, re, csv, time, sys, urllib.request, urllib.parse
import xml.etree.ElementTree as ET
EU="https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
def get(u, js=True):
    for k in range(5):
        try:
            r=urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"research-script/1.0"}),timeout=90).read()
            return json.loads(r) if js else r
        except Exception as e: err=e; time.sleep(3*(k+1))
    raise err
q='"Crit Care"[journal] AND ("machine learning"[tiab] OR "deep learning"[tiab] OR "artificial intelligence"[tiab] OR "prediction model"[tiab] OR "neural network"[tiab]) AND 2024/01/01:2026/11/23[pdat]'
ids=get(f"{EU}/esearch.fcgi?"+urllib.parse.urlencode({"db":"pmc","term":q,"retmax":400,"retmode":"json"}))["esearchresult"]["idlist"]
print("pool",len(ids),file=sys.stderr)
txt=lambda e: " ".join("".join(e.itertext()).split()) if e is not None else ""
KW={ "mimic":r"\bMIMIC", "eicu":r"\beICU", "hirid":r"HiRID", "amsterdam":r"AmsterdamUMC", "sicdb":r"SICdb",
 "external_validation":r"external(ly)? validat", "multicenter":r"multi-?cent(er|re)|multicent", "prospective":r"\bprospective",
 "calibration":r"calibrat", "decision_curve":r"decision curve", "shap":r"\bSHAP\b|Shapley", "delong":r"DeLong", "bootstrap":r"bootstrap",
 "confidence_interval":r"95% ?CI|confidence interval", "cross_validation":r"cross-?validation", "tripod":r"TRIPOD", "subgroup_fairness":r"subgroup|fairness|sex and race|ethnic",
 "lead_time":r"lead time|hours? (before|prior to) onset|in advance", "alarm_rate":r"false alarm|alert fatigue|alarms? per", "github":r"github\.com|gitlab|zenodo"}
rows=[]
for i in range(0,len(ids),20):
    x=get(f"{EU}/efetch.fcgi?db=pmc&id="+",".join(ids[i:i+20]),js=False); time.sleep(0.4)
    root=ET.fromstring(x)
    for art in root.iter("article"):
        if art.get("article-type")!="research-article": continue
        meta=art.find(".//article-meta"); title=txt(meta.find("title-group/article-title"))
        ab=txt(meta.find("abstract")); body=art.find("body"); bt=txt(body)
        back=art.find("back"); backt=txt(back)
        year=next((d.findtext("year") for d in meta.iter("pub-date")),"")
        doi=next((a.text for a in meta.iter("article-id") if a.get("pub-id-type")=="doi"),"")
        nref=len(list(art.iter("ref"))); nfig=len(list(art.iter("fig"))); ntab=len(list(art.iter("table-wrap")))
        secs=[txt(s.find("title")) for s in (body.findall("sec") if body is not None else [])]
        words=len(bt.split())
        full=ab+" "+bt+" "+backt
        d=dict(title=title,year=year,doi=doi,words_body=words,n_figs=nfig,n_tables=ntab,n_refs=nref,sections="; ".join(secs)[:300],abstract_words=len(ab.split()))
        for k,p in KW.items(): d[k]=int(bool(re.search(p,full,re.I)))
        DBS=["MIMIC-III","MIMIC-IV","eICU","HiRID","AmsterdamUMCdb","SICdb","VitalDB","UK Biobank","PhysioNet","Zhejiang","NICU","INSPIRE"]
        d["datasets_named"]="; ".join(x for x in DBS if re.search(re.escape(x),full,re.I))
        d["n_cohorts_est"]=max(len(set(re.findall(r"(?i)(?:MIMIC-I[VI]+|eICU|HiRID|AmsterdamUMCdb|SICdb|VitalDB)",full))), len(set(re.findall(r"(?i)\b(?:hospital|centre|center) [A-Z]\b",bt))), 1)
        BL=["logistic regression","random forest","XGBoost","LightGBM","CatBoost","support vector","LSTM","GRU","transformer","SOFA","APACHE","SAPS","NEWS","MEWS","qSOFA","neural network","decision tree","naive Bayes","k-nearest","AdaBoost","gradient boosting","elastic net","Cox"]
        d["baselines_named"]=sum(bool(re.search(re.escape(b),full,re.I)) for b in BL)
        d["seeds_mentioned"]=int(bool(re.search(r"random seed|different seeds|\bseeds\b|repeated (runs|cross)",full,re.I)))
        d["ablation"]=int(bool(re.search(r"ablation",full,re.I)))
        d["robustness_or_cross_dataset"]=int(bool(re.search(r"external validation|externally validated|cross-(database|dataset|site)|robustness|sensitivity analys",full,re.I)))
        d["deployment_evidence"]=int(bool(re.search(r"prospective(ly)? (validat|deploy|evaluat|implement)|silent (mode|trial)|real-time deployment|bedside implementation|randomi[sz]ed",full,re.I)))
        d["stat_tests"]="; ".join(t for t,pp in [("DeLong",r"DeLong"),("bootstrap",r"bootstrap"),("chi-square",r"chi-?squared?"),("Mann-Whitney/Wilcoxon",r"Mann.Whitney|Wilcoxon"),("t-test",r"t-test"),("Hosmer-Lemeshow",r"Hosmer"),("NRI/IDI",r"net reclassification|\bIDI\b"),("DCA",r"decision curve"),("Brier",r"Brier")] if re.search(pp,full,re.I))
        m=re.search(r"(Conclusions?:?)(.*)$",ab); d["abstract_conclusion"]=(m.group(2).strip()[:400] if m else "")
        n=re.findall(r"(\d[\d,]{2,})\s+(patients|admissions|ICU stays|stays|subjects|children|episodes)",ab)
        d["sample_sizes_in_abstract"]="; ".join(a+" "+b for a,b in n[:4])
        rows.append(d)
print("research articles",len(rows),file=sys.stderr)
out=sys.argv[1]
with open(out,"w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
