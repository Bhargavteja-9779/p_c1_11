"""Measure received->accepted days for candidate journals from Crossref assertions.
Samples research articles published in the last ~18 months (random sample via Crossref `sample`).
Usage: python journal_dates.py out_dir
"""
import json, sys, time, re, csv, datetime as dt, urllib.request, urllib.parse, statistics
from dateutil import parser as dparser

CANDS = [  # name, ISSN (any), publisher
 ("Journal of Big Data","2196-1115","Springer Nature"),
 ("Complex & Intelligent Systems","2199-4536","Springer Nature"),
 ("Energy Informatics","2520-8942","Springer Nature"),
 ("Journal of Cloud Computing","2192-113X","Springer Nature"),
 ("Cybersecurity","2523-3246","Springer Nature"),
 ("EPJ Data Science","2193-1127","Springer Nature"),
 ("Artificial Intelligence Review","0269-2821","Springer Nature"),
 ("Neural Computing and Applications","0941-0643","Springer Nature"),
 ("Applied Intelligence","0924-669X","Springer Nature"),
 ("Journal of Intelligent Manufacturing","0956-5515","Springer Nature"),
 ("Water Resources Management","0920-4741","Springer Nature"),
 ("Stochastic Environmental Research and Risk Assessment","1436-3240","Springer Nature"),
 ("Journal of Medical Systems","0148-5598","Springer Nature"),
 ("npj Digital Medicine","2398-6352","Springer Nature"),
 ("BMC Medical Informatics and Decision Making","1472-6947","Springer Nature"),
 ("Int J Educational Technology in Higher Education","2365-9440","Springer Nature"),
 ("Engineering with Computers","0177-0667","Springer Nature"),
 ("International Journal of Machine Learning and Cybernetics","1868-8071","Springer Nature"),
 ("Data Mining and Knowledge Discovery","1384-5810","Springer Nature"),
 ("Journal of Translational Medicine","1479-5876","Springer Nature"),
 ("Smart Learning Environments","2196-7091","Springer Nature"),
 ("Humanities & Social Sciences Communications","2662-9992","Springer Nature"),
 ("Int J Computational Intelligence Systems","1875-6883","Springer Nature"),
 ("Journal of Ambient Intelligence and Humanized Computing","1868-5137","Springer Nature"),
 ("Intl J of Digital Earth","1753-8947","Taylor & Francis"),
 ("Geo-spatial Information Science","1009-5020","Taylor & Francis"),
 ("GIScience & Remote Sensing","1548-1603","Taylor & Francis"),
 ("Enterprise Information Systems","1751-7575","Taylor & Francis"),
 ("International Journal of Production Research","0020-7543","Taylor & Francis"),
 ("Connection Science","0954-0091","Taylor & Francis"),
 ("Big Earth Data","2096-4471","Taylor & Francis"),
 ("Computer-Aided Civil and Infrastructure Engineering","1093-9687","Wiley"),
 ("International Journal of Intelligent Systems","0884-8173","Wiley"),
 ("Expert Systems","0266-4720","Wiley"),
 ("Concurrency and Computation","1532-0626","Wiley"),
 ("Int J Energy Research","0363-907X","Wiley"),
 ("Energy Science & Engineering","2050-0505","Wiley"),
 ("IET Renewable Power Generation","1752-1416","Wiley/IET"),
 ("IET Generation Transmission & Distribution","1751-8687","Wiley/IET"),
 ("CAAI Trans on Intelligence Technology","2468-2322","Wiley/IET"),
 ("Protection and Control of Modern Power Systems","2367-2617","Springer/IEEE"),
 ("Sustainable Energy Research","2731-9237","Springer Nature"),
 ("Carbon Neutrality","2731-3948","Springer Nature"),
 ("Journal of Hydroinformatics","1464-7141","IWA"),
]
UA = "research-script/1.0 (mailto:anonymous@example.org)"

def get(url):
    for k in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            return json.load(urllib.request.urlopen(req, timeout=60))
        except Exception as e:
            time.sleep(3*(k+1)); err=e
    raise err

def pdate(s):
    try: return dparser.parse(s, dayfirst=True).date()
    except Exception: return None

def run(out):
    rows=[]; summ=[]
    for name, issn, pub in CANDS:
        q = {"filter": "type:journal-article,from-pub-date:2025-05-01,until-pub-date:2026-11-23", "sample": "100"}
        url = f"https://api.crossref.org/journals/{issn}/works?" + urllib.parse.urlencode(q)
        try: d = get(url)
        except Exception as e:
            summ.append(dict(journal=name, issn=issn, publisher=pub, n=0, note=f"error {e}")); continue
        days=[]
        for it in d["message"]["items"]:
            a = {x.get("name","").lower(): x.get("value","") for x in it.get("assertion",[])}
            title = (it.get("title") or [""])[0]
            if re.search(r"(?i)^(correction|retraction|erratum|editorial|publisher correction|author correction)", title): continue
            r, ac = pdate(a.get("received","")), pdate(a.get("accepted",""))
            if r and ac and ac>=r:
                dd=(ac-r).days; days.append(dd)
                rows.append(dict(journal=name, title=title[:200], doi=it["DOI"], received=r.isoformat(), accepted=ac.isoformat(), days=dd))
        if days:
            s=sorted(days); n=len(s)
            p = lambda q: s[min(n-1,int(round(q*(n-1))))]
            summ.append(dict(journal=name, issn=issn, publisher=pub, n=n, median=statistics.median(s), p75=p(.75), p90=p(.9), max=s[-1], mean=round(sum(s)/n,1), share_le72=round(sum(x<=72 for x in s)/n,2), note=""))
        else:
            summ.append(dict(journal=name, issn=issn, publisher=pub, n=0, note="no received/accepted dates in Crossref"))
        print(summ[-1], flush=True); time.sleep(1)
    tag = "_wave2" if (len(sys.argv)>2) else ""
    with open(f"{out}/acceptance_time_all_candidates{tag}.csv","w",newline="") as f:
        w=csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    keys=["journal","issn","publisher","n","median","p75","p90","max","mean","share_le72","note"]
    with open(f"{out}/acceptance_time_summary{tag}.csv","w",newline="") as f:
        w=csv.DictWriter(f, fieldnames=keys); w.writeheader(); [w.writerow({k:r.get(k,"") for k in keys}) for r in summ]

WAVE2 = [
 ("Critical Care","1364-8535","Springer Nature/BMC"),
 ("Annals of Intensive Care","2110-5820","Springer Nature"),
 ("Journal of Intensive Care","2052-0492","Springer Nature/BMC"),
 ("Cardiovascular Diabetology","1475-2840","Springer Nature/BMC"),
 ("Military Medical Research","2054-9369","Springer Nature/BMC"),
 ("BMC Medicine","1741-7015","Springer Nature/BMC"),
 ("J NeuroEngineering and Rehabilitation","1743-0003","Springer Nature/BMC"),
 ("Respiratory Research","1465-993X","Springer Nature/BMC"),
 ("Environmental Health","1476-069X","Springer Nature/BMC"),
 ("Int J Health Geographics","1476-072X","Springer Nature/BMC"),
 ("Journal of Cheminformatics","1758-2946","Springer Nature"),
 ("Infectious Diseases of Poverty","2049-9957","Springer Nature/BMC"),
 ("Eng Appl Computational Fluid Mechanics","1994-2060","Taylor & Francis"),
 ("Virtual and Physical Prototyping","1745-2759","Taylor & Francis"),
 ("Materials Research Letters","2166-3831","Taylor & Francis"),
 ("J Computational Design and Engineering","2288-5048","Oxford University Press"),
 ("JAMIA","1067-5027","Oxford University Press"),
 ("Briefings in Bioinformatics","1467-5463","Oxford University Press"),
 ("Bioinformatics","1367-4803","Oxford University Press"),
 ("GigaScience","2047-217X","Oxford University Press"),
 ("Nucleic Acids Research","0305-1048","Oxford University Press"),
 ("Structural Health Monitoring","1475-9217","SAGE"),
 ("Data-Centric Engineering","2632-6736","Cambridge"),
 ("High Voltage","2397-7264","IET/Wiley"),
 ("Journal of Hematology & Oncology","1756-8722","Springer Nature/BMC"),
 ("Biomarker Research","2050-7771","Springer Nature/BMC"),
 ("Journal of Big Data (ctrl)","2196-1115","Springer Nature"),
 ("Int J Behavioral Nutrition and Physical Activity","1479-5868","Springer Nature/BMC"),
 ("Insights into Imaging","1869-4101","Springer Nature"),
 ("European Radiology Experimental","2509-9280","Springer Nature"),
 ("Radiation Oncology","1748-717X","Springer Nature/BMC"),
 ("Journal of Medical Internet Research","1438-8871","JMIR"),
 ("Sustainable Cities and Society? (Elsevier ctrl)","2210-6707","Elsevier"),
 ("Journal of Global Health","2047-2978","ISoGH"),
 ("Translational Psychiatry","2158-3188","Springer Nature"),
 ("npj Climate and Atmospheric Science","2397-3722","Springer Nature"),
 ("Communications Earth & Environment","2662-4435","Springer Nature"),
 ("Climate Risk Management (ctrl)","2212-0963","Elsevier"),
 ("Geoscience Frontiers (ctrl)","1674-9871","Elsevier"),
 ("International Journal of Disaster Risk Science","2095-0055","Springer Nature"),
]
if __name__=="__main__":
    if len(sys.argv)>2 and sys.argv[2]=="wave2": CANDS[:] = WAVE2
    run(sys.argv[1])
