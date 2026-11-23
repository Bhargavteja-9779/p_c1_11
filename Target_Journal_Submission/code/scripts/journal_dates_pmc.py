"""Received->accepted days for RESEARCH ARTICLES only, from NCBI PMC E-utilities JATS XML
(<article article-type="research-article"> and <history> dates). Works for OA articles in PMC
from any publisher (incl. OUP, Elsevier OA, SAGE, Wiley). Usage: python journal_dates_epmc.py out_dir N
"""
import sys, json, time, csv, re, random, statistics, urllib.request, urllib.parse
import xml.etree.ElementTree as ET
J = [
 ("Critical Care","1364-8535","Springer Nature/BMC"),
 ("Journal of Intensive Care","2052-0492","Springer Nature/BMC"),
 ("Annals of Intensive Care","2110-5820","Springer Nature"),
 ("Cardiovascular Diabetology","1475-2840","Springer Nature/BMC"),
 ("Journal of Hematology & Oncology","1756-8722","Springer Nature/BMC"),
 ("npj Digital Medicine","2398-6352","Springer Nature"),
 ("Communications Medicine","2730-664X","Springer Nature"),
 ("eClinicalMedicine","2589-5370","Elsevier (Lancet)"),
 ("eBioMedicine","2352-3964","Elsevier (Lancet)"),
 ("The Lancet Digital Health","2589-7500","Elsevier (Lancet)"),
 ("JAMIA","1067-5027","Oxford University Press"),
 ("JAMIA Open","2574-2531","Oxford University Press"),
 ("Briefings in Bioinformatics","1467-5463","Oxford University Press"),
 ("Bioinformatics","1367-4803","Oxford University Press"),
 ("GigaScience","2047-217X","Oxford University Press"),
 ("Nucleic Acids Research","0305-1048","Oxford University Press"),
 ("European Heart Journal - Digital Health","2634-3916","Oxford University Press"),
 ("Journal of Medical Internet Research","1438-8871","JMIR"),
 ("JMIR Medical Informatics","2291-9694","JMIR"),
 ("BMJ Health & Care Informatics","2632-1009","BMJ"),
 ("Journal of Biomedical Informatics","1532-0464","Elsevier"),
 ("Intensive Care Medicine Experimental","2197-425X","Springer Nature"),
 ("Journal of Translational Medicine","1479-5876","Springer Nature/BMC"),
 ("Clinical Kidney Journal","2048-8505","Oxford University Press"),
 ("Diabetes Research and Clinical Practice","0168-8227","Elsevier"),
 ("Journal of Cachexia Sarcopenia Muscle","2190-5991","Wiley"),
 ("Alzheimer's Research & Therapy","1758-9193","Springer Nature/BMC"),
 ("Journal of Neuroinflammation","1742-2094","Springer Nature/BMC"),
 ("Molecular Cancer","1476-4598","Springer Nature/BMC"),
 ("Arthritis Research & Therapy","1478-6362","Springer Nature/BMC"),
]
EU="https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
def get(url, js=True):
    for k in range(5):
        try:
            r=urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"research-script/1.0"}),timeout=90).read()
            return json.loads(r) if js else r
        except Exception as e: err=e; time.sleep(3*(k+1))
    raise err
def parse_articles(xml):
    root=ET.fromstring(xml); out=[]
    for art in root.iter("article"):
        atype=art.get("article-type") or ""
        d={}
        hist=art.find(".//article-meta/history")
        if hist is not None:
            for dt in hist.iter("date"):
                t=dt.get("date-type")
                if t in("received","accepted"):
                    try: d[t]=(int(dt.findtext("year")),int(dt.findtext("month") or 1),int(dt.findtext("day") or 1))
                    except: pass
        title="".join(art.find(".//article-meta/title-group/article-title").itertext()) if art.find(".//article-meta/title-group/article-title") is not None else ""
        doi=next((a.text for a in art.iter("article-id") if a.get("pub-id-type")=="doi"),"")
        pmc=next((a.text for a in art.iter("article-id") if a.get("pub-id-type") in("pmc","pmcid")),"")
        out.append((atype,d,title,doi,pmc))
    return out
def main(out,N):
    import datetime as D
    rows=[];summ=[]
    for name,issn,pub in J:
        q=f"{issn}[issn] AND 2025/06/01:2026/11/23[pdat]"
        try:
            d=get(f"{EU}/esearch.fcgi?"+urllib.parse.urlencode({"db":"pmc","term":q,"retmax":3000,"retmode":"json"}))
            ids=d["esearchresult"]["idlist"]
        except Exception as e:
            summ.append(dict(journal=name,issn=issn,publisher=pub,n=0,pool=0)); print(summ[-1],e,flush=True); continue
        random.Random(7 if 'repeat' in name else 42).shuffle(ids); days=[]; i=0
        while len(days)<N and i<len(ids) and i<N*4:
            batch=ids[i:i+20]; i+=20
            try: x=get(f"{EU}/efetch.fcgi?db=pmc&id="+",".join(batch),js=False)
            except Exception: continue
            time.sleep(0.4)
            try: arts=parse_articles(x)
            except Exception: continue
            for at,h,title,doi,pmc in arts:
                if at!="research-article" or "received" not in h or "accepted" not in h: continue
                rv=D.date(*h["received"]); ac=D.date(*h["accepted"]); dd=(ac-rv).days
                if dd<0 or len(days)>=N: continue
                days.append(dd); rows.append(dict(journal=name,title=title[:200].replace("\n"," "),doi=doi,pmcid=pmc,received=rv.isoformat(),accepted=ac.isoformat(),days=dd))
        if days:
            s=sorted(days);n=len(s);p=lambda q:s[min(n-1,int(round(q*(n-1))))]
            summ.append(dict(journal=name,issn=issn,publisher=pub,n=n,pool=len(ids),median=statistics.median(s),p75=p(.75),p90=p(.9),max=s[-1],share_le72=round(sum(v<=72 for v in s)/n,2)))
        else: summ.append(dict(journal=name,issn=issn,publisher=pub,n=0,pool=len(ids)))
        print(summ[-1],flush=True)
    tag=sys.argv[3] if len(sys.argv)>3 else ""
    with open(f"{out}/acceptance_time_pmc_research_articles{tag}.csv","w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys()));w.writeheader();w.writerows(rows)
    keys=["journal","issn","publisher","n","pool","median","p75","p90","max","share_le72"]
    with open(f"{out}/acceptance_time_pmc_summary{tag}.csv","w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader();[w.writerow({k:r.get(k,"") for k in keys}) for r in summ]
WAVE4=[
 ("World Journal of Emergency Surgery","1749-7922","Springer Nature/BMC"),
 ("Scand J Trauma Resusc Emerg Med","1757-7241","Springer Nature/BMC"),
 ("Journal of Headache and Pain","1129-2369","Springer Nature/BMC"),
 ("Diabetology & Metabolic Syndrome","1758-5996","Springer Nature/BMC"),
 ("Burns & Trauma","2321-3868","Oxford University Press"),
 ("Journal of Biomedical Science","1423-0127","Springer Nature/BMC"),
 ("Journal of Nanobiotechnology","1477-3155","Springer Nature/BMC"),
 ("Emerging Microbes & Infections","2222-1751","Taylor & Francis"),
 ("Journal of Experimental & Clinical Cancer Research","1756-9966","Springer Nature/BMC"),
 ("Clinical Epigenetics","1868-7083","Springer Nature/BMC"),
 ("Lipids in Health and Disease","1476-511X","Springer Nature/BMC"),
 ("Journal of Inflammation Research","1178-7031","Dove/Taylor & Francis"),
 ("Annals of Medicine","0785-3890","Taylor & Francis"),
 ("Renal Failure","0886-022X","Taylor & Francis"),
 ("International Journal of Surgery","1743-9191","Wolters Kluwer"),
 ("Intensive Care Medicine","0342-4642","Springer Nature"),
 ("Critical Care (repeat, other seed)","1364-8535","Springer Nature/BMC"),
]
if __name__=="__main__":
    if len(sys.argv)>3 and sys.argv[3]=="_wave4": J[:]=WAVE4
    main(sys.argv[1],int(sys.argv[2]))
