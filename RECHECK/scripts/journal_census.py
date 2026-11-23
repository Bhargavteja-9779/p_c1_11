"""Stage 1 recheck: CENSUS of received->accepted days for research articles published in a window.
Source: NCBI PMC E-utilities JATS <history> dates; article-type="research-article" only.
Usage: python journal_census.py OUT_CSV START END [MAX_PER_JOURNAL]
"""
import sys, json, time, csv, statistics, urllib.request, urllib.parse, datetime as D
import xml.etree.ElementTree as ET
J = [("Critical Care","1364-8535"),("Intensive Care Medicine","0342-4642"),("Annals of Intensive Care","2110-5820"),
 ("Journal of Intensive Care","2052-0492"),("British Journal of Anaesthesia","0007-0912"),("Anaesthesia","0003-2409"),
 ("Anesthesiology","0003-3022"),("Critical Care Medicine","0090-3493"),("American J Respir Crit Care Med","1073-449X"),
 ("Chest","0012-3692"),("Journal of Clinical Monitoring and Computing","1387-1307"),("BMC Anesthesiology","1471-2253"),
 ("Perioperative Medicine","2047-0525"),("Resuscitation","0300-9572"),("Shock","1073-2322"),
 ("European Journal of Anaesthesiology","0265-0215"),("Anesthesia and Analgesia","0003-2999"),
 ("Critical Care Explorations","2639-8028"),("Journal of Critical Care","0883-9441"),("Intensive Care Med Experimental","2197-425X"),
 ("Canadian Journal of Anesthesia","0832-610X"),("npj Digital Medicine","2398-6352"),("Journal of Headache and Pain","1129-2369"),
 ("Cardiovascular Diabetology","1475-2840"),("Military Medical Research","2054-9369"),("Respiratory Research","1465-993X"),
 ("Journal of Neuroinflammation","1742-2094"),("World Journal of Emergency Surgery","1749-7922"),
 ("Scand J Trauma Resusc Emerg Med","1757-7241"),("Burns & Trauma","2321-3868"),("Annals of Emergency Medicine","0196-0644")]
EU = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
def get(url, js=True):
    err = None
    for k in range(6):
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "research-script/1.0"}), timeout=90).read()
            return json.loads(r) if js else r
        except Exception as e: err = e; time.sleep(3 * (k + 1))
    raise err
def dt(node):
    try: return D.date(int(node.findtext("year")), int(node.findtext("month") or 1), int(node.findtext("day") or 1))
    except Exception: return None
def main(out, start, end, cap):
    rows, summ = [], []
    for name, issn in J:
        q = f"{issn}[issn] AND {start}:{end}[pdat]"
        try: ids = get(f"{EU}/esearch.fcgi?" + urllib.parse.urlencode({"db": "pmc", "term": q, "retmax": 5000, "retmode": "json"}))["esearchresult"]["idlist"]
        except Exception as e: print(name, "search fail", e, flush=True); ids = []
        ids = ids[:cap]; days = []; ntypes = {}
        for i in range(0, len(ids), 50):
            try: x = get(f"{EU}/efetch.fcgi?db=pmc&id=" + ",".join(ids[i:i+50]), js=False)
            except Exception as e: print("fetch fail", e); continue
            time.sleep(0.4)
            try: root = ET.fromstring(x)
            except Exception: continue
            for art in root.iter("article"):
                at = art.get("article-type") or ""; ntypes[at] = ntypes.get(at, 0) + 1
                if at != "research-article": continue
                h = art.find(".//article-meta/history"); d = {}
                if h is not None:
                    for e in h.iter("date"):
                        if e.get("date-type") in ("received", "accepted"): d[e.get("date-type")] = dt(e)
                pub = None
                for pd_ in art.iter("pub-date"):
                    v = dt(pd_)
                    if v and (pub is None or v < pub): pub = v
                doi = next((a.text for a in art.iter("article-id") if a.get("pub-id-type") == "doi"), "")
                t = art.find(".//article-meta/title-group/article-title"); title = "".join(t.itertext()).strip() if t is not None else ""
                if d.get("received") and d.get("accepted"):
                    n = (d["accepted"] - d["received"]).days
                    if 0 <= n < 2000:
                        days.append(n); rows.append(dict(journal=name, issn=issn, doi=doi, title=title[:200], received=d["received"],
                                                         accepted=d["accepted"], published=pub, days=n))
        if days:
            s = sorted(days); q = statistics.quantiles(s, n=100, method="inclusive")
            summ.append(dict(journal=name, issn=issn, pmc_items=len(ids), n_research_with_dates=len(s), median=statistics.median(s),
                             p25=round(q[24], 1), p75=round(q[74], 1), p90=round(q[89], 1), share_le72=round(sum(x <= 72 for x in s) / len(s), 3),
                             passes_rule=bool(statistics.median(s) < 72 and q[74] <= 72)))
        else: summ.append(dict(journal=name, issn=issn, pmc_items=len(ids), n_research_with_dates=0))
        print(summ[-1], flush=True)
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    keys = ["journal","issn","pmc_items","n_research_with_dates","median","p25","p75","p90","share_le72","passes_rule"]
    with open(out.replace(".csv", "_summary.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); [w.writerow({k: r.get(k, "") for k in keys}) for r in summ]
if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]) if len(sys.argv) > 4 else 1500)
