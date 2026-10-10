from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List
import random, re

app = FastAPI(
    title="INDUX-OS Industrial Intelligence API",
    description="Prototype API for SOP retrieval and industrial capability demonstrations. Simulated modules are explicitly marked.",
    version="2.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to your deployed frontend domain before production.
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

class Query(BaseModel):
    query: str = Field(default="", max_length=2000)

KB = [
    {"manual":"CNC_Maintenance_v3.pdf","page":47,"section":"Bearing Replacement","text":"Bearing failure due to vibration >4.5mm/s. Steps: Power OFF + LOTO, Remove housing 12mm wrench, Replace bearing 6205ZZ, Lubricate NLGI-2, Torque 25Nm, Test 10min","kw":["bearing","vibration","noise","cnc"]},
    {"manual":"Motor_SOP_v2.pdf","page":112,"section":"Motor Overheating","text":"Motor overheating >85C. Causes: coolant low, filter clogged. Steps: Check coolant >80%, Clean air filter, Check sensor 10k ohm, Cool 10min, Restart","kw":["motor","overheat","garam","heat","temperature","hot"]},
    {"manual":"Quality_SOP_v4.pdf","page":89,"section":"Surface Defect","text":"Scratch defect <0.2mm acceptable. Steps: Stop conveyor, Photo defect, Check mold pressure 150bar, Check temp 180C, Re-calibrate","kw":["defect","scratch","quality","dent","surface"]},
    {"manual":"Hydraulic_SOP_v1.pdf","page":33,"section":"Hydraulic Leak","text":"Hydraulic leak fix: Identify with UV dye, Depressurize 0 bar, Replace O-ring 20x2mm, Tighten 30Nm, Refill ISO 46, Pressure test 200bar","kw":["hydraulic","leak","oil"]},
    {"manual":"Safety_SOP_v1.pdf","page":15,"section":"Safety Checklist","text":"Safety before maintenance: Helmet ISI, Gloves cut-resistant, Goggles, Power isolated, Fatigue <70%, Supervisor approval","kw":["safety","helmet","ppe","gloves","loto","maintenance checklist"]},
    {"manual":"Gearbox_SOP_v2.pdf","page":58,"section":"Gearbox Oil & Noise","text":"Gearbox whine or oil temp >90C. Steps: Power OFF + LOTO, Drain and sample oil, Check metal particles, Refill ISO VG 220, Check backlash 0.1mm, Test 15min","kw":["gearbox","gear","whine","oil temp"]},
    {"manual":"Conveyor_SOP_v3.pdf","page":21,"section":"Belt Misalignment","text":"Belt drifting >10mm off centre. Steps: Stop conveyor + LOTO, Inspect idlers, Adjust take-up evenly, Re-tension to spec, Run empty 5min","kw":["conveyor","belt","misalign","drift"]},
    {"manual":"Pneumatic_SOP_v1.pdf","page":40,"section":"Air Pressure Drop","text":"Line pressure <5.5bar. Steps: Isolate branch, Check FRL unit, Soap-test fittings, Replace seals, Drain moisture trap, Restore to 6.5bar","kw":["pneumatic","air","pressure drop","compressor"]},
    {"manual":"Drive_SOP_v2.pdf","page":77,"section":"VFD Fault Trip","text":"VFD overcurrent trip. Steps: Power OFF + LOTO, Wait 5min capacitor discharge, Check motor insulation, Inspect cable, Reset fault, Ramp test","kw":["vfd","drive","trip","overcurrent","inverter"]},
]

MODULES = {"sop","predict","quality","energy","robot_pick","delivery","cyber","deepfake","twin_prod","twin_emerg","surface","retail","demand","multilingual","farmer","safety","water","disaster","satellite","health","drone","mapping","agentic"}

SYN={"garam":"overheat","gram":"overheat","awaaz":"noise","shor":"noise","tel":"oil","risaav":"leak","patta":"belt","hawa":"air"}

def search(q: str):
    """Keyword + Hinglish-synonym ranking. Replace with parsing + vector retrieval for production."""
    toks=re.findall(r"[a-z0-9]+",q.lower())
    ql=q.lower()+" "+" ".join(SYN[t] for t in toks if t in SYN)
    scored=[(sum(1 for kw in i["kw"] if kw in ql),i) for i in KB]
    scored=[x for x in scored if x[0]]
    if not scored: return None
    scored.sort(key=lambda x:x[0],reverse=True)
    return {**scored[0][1],"_score":scored[0][0]}

@app.get("/")
def health():
    return {"service":"INDUX-OS API","status":"online","mode":"prototype","docs":"/docs"}

@app.get("/api/health")
def health_check():
    return {"status":"ok","timestamp":datetime.now(timezone.utc).isoformat(),"mode":"prototype"}

@app.post("/api/module/{name}")
async def module_api(name: str, q: Query):
    if name not in MODULES:
        raise HTTPException(status_code=404, detail=f"Unknown module '{name}'.")
    query = q.query.strip() or "bearing vibration high hai"
    now = datetime.now(timezone.utc).isoformat()
    base = {"module": name, "query": query, "timestamp": now, "status": "SIMULATED DEMO — NOT LIVE PLANT DATA"}

    if name == "sop":
        s = search(query)
        if not s:
            return {**base, "module":"SOP-Genius · no confident match", "grounded_source":"No matching source found in the demo knowledge base", "cited_text":"No source was matched. Do not infer a procedure. Search approved site documentation or contact a qualified supervisor.", "steps":["Clarify the machine and symptom","Consult the approved site SOP","Escalate to authorized maintenance staff"], "confidence":"low", "safety_checklist":["Follow site lockout/tagout procedure","Obtain supervisor authorization"]}
        return {**base, "module":"SOP-Genius · keyword retrieval demo", "grounded_source":f"{s['manual']} · Page {s['page']} · {s['section']}", "cited_text":s["text"], "steps":s["text"].split("Steps:")[-1].split(",") if "Steps:" in s["text"] else [s["text"]], "retrieval_method":"keyword match (not vector RAG)", "confidence":"unvalidated", "keyword_match_strength":s["_score"], "safety_checklist":["Follow approved site LOTO and PPE rules","Confirm procedure revision and machine model","Get supervisor approval before maintenance"], "note":"Reference is a sample record. Confirm against the original approved manual before acting."}

    # These endpoints intentionally return clearly labelled simulated values.
    if name == "predict": return {**base,"signals":{"vibration_mm_s":round(random.uniform(2,6),2),"temperature_c":random.randint(60,95)},"prediction":"DEMO ALERT — validate with real sensor history" if random.random()>.3 else "DEMO NORMAL — not a diagnostic","recommended_action":"Inspect approved maintenance procedure; do not rely on this randomized output."}
    if name == "quality": return {**base,"inference_latency_ms":"illustrative 45","defect_detected":random.choice([True,False]),"confidence":"simulated only","validation":"No vision model or camera connected"}
    if name == "energy": return {**base,"energy_kwh":"simulated 120–200","suggestion":"Illustrative idea: evaluate scheduling against real tariff and production constraints"}
    if name == "robot_pick": return {**base,"objects":"simulated 3–8","accuracy":"not measured","cycle_ms":"illustrative 800–1200"}
    if name == "delivery": return {**base,"battery":"simulated","eta_sec":"simulated","obstacles":"simulated","integration":"No robot connected"}
    if name == "cyber": return {**base,"anomaly_score":"randomized demo score","action":"Do not isolate real OT equipment based on this demo; use approved incident response"}
    if name == "deepfake": return {**base,"authenticity_result":"not evaluated","confidence":"not available","integration":"No media forensic model connected"}
    if name == "twin_prod": return {**base,"throughput":"scenario placeholder","what_if":"Scenario modelling is not connected to production data"}
    if name == "twin_emerg": return {**base,"evac_time":"not calculated","best_route":"Use site-approved emergency plans and signage"}
    if name == "surface": return {**base,"defect_type":random.choice(["scratch","none","dent"]),"size_mm":"randomized illustration","validation":"No image/model supplied"}
    if name == "retail": return {**base,"bill_total":"not calculated","recognition":"not measured","integration":"No product catalog or camera connected"}
    if name == "demand": return {**base,"forecast":"not calculated","price_suggestion":"not calculated","integration":"Requires historical data and business rules"}
    if name == "multilingual": return {**base,"languages":["Hindi","English","Tamil","Bengali"],"voice":"browser integration required"}
    if name == "farmer": return {**base,"advice":"No crop-specific recommendation generated","market_price":"not connected","note":"Check local agricultural extension and current market sources"}
    if name == "safety": return {**base,"fatigue":"not measured","alert":"No wearable or safety sensor connected"}
    if name == "water": return {**base,"pH":"not measured","prediction":"No water sensor connected; do not infer potability"}
    if name == "disaster": return {**base,"hazard":"not assessed","lead_time":"not calculated","note":"Use official alerts and validated hazard models"}
    if name == "satellite": return {**base,"change":"not analyzed","integration":"No imagery or remote-sensing model supplied"}
    if name == "health": return {**base,"vitals":"not measured","risk":"not assessed","note":"Not a medical device or diagnostic"}
    if name == "drone": return {**base,"field_health":"not analyzed","gps":"example coordinate only; not a live location"}
    if name == "mapping": return {**base,"area_m2":"not mapped","slam":"No lidar/camera stream connected"}
    if name == "agentic": return {**base,"workflow":"illustrative ERP → automation → CRM","time_saved":"not measured","integration":"No business systems connected"}
    return base


class Series(BaseModel):
    values: List[float] = Field(min_length=8, max_length=500)
    threshold: float = Field(default=4.5, gt=0)
    interval_s: float = Field(default=1.0, gt=0)
    symptom: str = Field(default="bearing vibration", max_length=200)

@app.post("/api/analyze")
def analyze(sr: Series):
    """Real analytics on supplied data: baseline z-score of EWMA, linear trend, time-to-limit, auto work order."""
    v=sr.values; n=len(v)
    b=v[:max(5,n//3)]; mu=sum(b)/len(b); sd=max((sum((x-mu)**2 for x in b)/len(b))**.5,0.05)
    e=v[0]
    for x in v[1:]: e=.3*x+.7*e
    z=(e-mu)/sd
    k=min(n,20); ys=v[-k:]; xm=(k-1)/2; ym=sum(ys)/k
    slope=sum((i-xm)*(y-ym) for i,y in enumerate(ys))/sum((i-xm)**2 for i in range(k))
    last=v[-1]
    ttl=0.0 if last>=sr.threshold else (round((sr.threshold-last)/slope*sr.interval_s,1) if slope>1e-3 else None)
    level="CRITICAL" if last>=sr.threshold else "WARNING" if (z>4 or (ttl is not None and ttl<90)) else "NORMAL"
    out={"level":level,"z_score":round(z,2),"trend_per_sample":round(slope,4),"time_to_limit_s":ttl,"latest":round(last,2),"method":"EWMA z-score + 20-sample linear trend","data_source":"client-supplied series (simulated in demo)"}
    if level!="NORMAL":
        hit=search(sr.symptom) or KB[4]
        out["work_order"]={"id":"WO-"+datetime.now(timezone.utc).strftime("%y%m%d-%H%M%S"),"priority":"P1 — stop & inspect" if level=="CRITICAL" else "P2 — schedule within shift","source":f"{hit['manual']} · Page {hit['page']} · {hit['section']}","steps":hit["text"].split("Steps:")[-1].split(","),"loto_required":True,"approval":"Supervisor sign-off required","note":"Auto-drafted from anomaly + SOP match. Verify against the approved manual."}
    return out

# ================= v4: real PDF RAG + CSV / live sensor feed =================
import io, csv, math, os, glob, collections
from fastapi import UploadFile, File, Form
from pypdf import PdfReader

STOP=set("the a an of to and or in on is are for with at by from it this that be as".split())
CHUNKS=[]; DOCS={}

def stem(w): return w[:-3] if len(w)>6 and w.endswith("ing") else (w[:-1] if len(w)>4 and w.endswith("s") else w)
def tok(t): return [stem(w) for w in re.findall(r"[a-z0-9]+",t.lower()) if w not in STOP]

def ingest(name: str, data: bytes):
    if name.lower().endswith(".pdf"):
        pages=[(i+1,p.extract_text() or "") for i,p in enumerate(PdfReader(io.BytesIO(data)).pages)]
    else:
        pages=[(1,data.decode("utf-8","ignore"))]
    CHUNKS[:]=[c for c in CHUNKS if c["doc"]!=name]; n=0
    for pg,t in pages:
        w=t.split()
        for i in range(0,len(w),70):
            seg=" ".join(w[i:i+90])
            if len(seg)>30:
                CHUNKS.append({"doc":name,"page":pg,"text":seg,"tf":collections.Counter(tok(seg))}); n+=1
    DOCS[name]={"pages":len(pages),"chunks":n}
    return DOCS[name]

def retrieve(q: str, k: int=3):
    """BM25 ranking over page-level chunks, with Hinglish query expansion."""
    raw=re.findall(r"[a-z0-9]+",q.lower())
    qt=set(tok(q)+[stem(SYN[t]) for t in raw if t in SYN]); N=len(CHUNKS)
    if not N: return []
    avg=sum(sum(c["tf"].values()) for c in CHUNKS)/N
    df=collections.Counter(t for c in CHUNKS for t in c["tf"]); out=[]
    for c in CHUNKS:
        L=sum(c["tf"].values()); s=0.0
        for t in qt:
            f=c["tf"].get(t,0)
            if f: s+=math.log(1+(N-df[t]+.5)/(df[t]+.5))*f*2.2/(f+1.2*(.25+.75*L/avg))
        if s>0: out.append((s,c))
    out.sort(key=lambda x:-x[0]); return out[:k]

for _f in sorted(glob.glob(os.path.join(os.path.dirname(__file__),"sop_library","*.pdf"))):
    ingest(os.path.basename(_f),open(_f,"rb").read())

@app.get("/api/docs")
def list_docs(): return DOCS

@app.post("/api/docs/upload")
async def upload_docs(files: List[UploadFile]=File(...)):
    res={}
    for f in files[:10]:
        data=await f.read()
        if len(data)>15_000_000: raise HTTPException(413,f"{f.filename} exceeds 15 MB")
        try: res[f.filename]=ingest(f.filename,data)
        except Exception as e: raise HTTPException(400,f"Could not parse {f.filename}: {e}")
    return res

class Ask(BaseModel):
    query: str = Field(min_length=2, max_length=2000)

SAFETY="Verify against the approved manual revision. Lockout/tagout and supervisor approval are mandatory before hazardous work."

@app.post("/api/ask")
async def ask(a: Ask):
    hits=retrieve(a.query)
    if not hits or hits[0][0]<1.5:
        return {"answer":None,"sources":[],"message":"No confident match in the indexed documents. Do not guess — consult the approved SOP or a supervisor."}
    ctx="\n\n".join(f"[{i+1}] {c['doc']} p.{c['page']}: {c['text']}" for i,(s,c) in enumerate(hits))
    ans=hits[0][1]["text"]; mode="extractive (set ANTHROPIC_API_KEY for LLM answers)"
    key=os.getenv("ANTHROPIC_API_KEY")
    if key:
        try:
            import httpx
            model=os.getenv("LLM_MODEL","claude-sonnet-4-5")
            async with httpx.AsyncClient(timeout=30) as h:
                r=await h.post("https://api.anthropic.com/v1/messages",headers={"x-api-key":key,"anthropic-version":"2023-06-01"},json={"model":model,"max_tokens":600,"system":"You are an industrial maintenance assistant. Answer ONLY from the numbered excerpts. Cite sources as [n]. Give short numbered steps and state safety/LOTO requirements if present. If the excerpts do not answer, say so. The user may write English or Hinglish; answer in the same language.","messages":[{"role":"user","content":f"Excerpts:\n{ctx}\n\nQuestion: {a.query}"}]})
                r.raise_for_status(); ans=r.json()["content"][0]["text"]; mode=f"LLM ({model}) grounded on retrieved excerpts"
        except Exception as e:
            mode=f"extractive (LLM call failed: {type(e).__name__})"
    return {"answer":ans,"grounding":mode,"safety":SAFETY,"sources":[{"doc":c["doc"],"page":c["page"],"score":round(s,2),"excerpt":c["text"][:320]} for s,c in hits]}

def core(v, limit, direction="high", label="vibration"):
    sg=-1 if direction=="low" else 1; x=[sg*a for a in v]; lim=sg*limit; n=len(x)
    b=x[:max(5,n//3)]; mu=sum(b)/len(b); sd=max((sum((a-mu)**2 for a in b)/len(b))**.5,1e-6*max(1,abs(mu)),0.02*abs(mu) or 0.02)
    e=x[0]
    for a in x[1:]: e=.3*a+.7*e
    z=(e-mu)/sd; k=min(n,20); ys=x[-k:]; xm=(k-1)/2; ym=sum(ys)/k
    slope=sum((i-xm)*(y-ym) for i,y in enumerate(ys))/sum((i-xm)**2 for i in range(k))
    last=x[-1]; ttl=0 if last>=lim else (round((lim-last)/slope) if slope>1e-6 else None)
    level="CRITICAL" if last>=lim else "WARNING" if (z>4 or (ttl is not None and ttl<30)) else "NORMAL"
    out={"level":level,"z_score":round(z,2),"trend_per_sample":round(sg*slope,4),"samples_to_limit":ttl,"latest":round(v[-1],3),"anomalies":sum(1 for a in x if (a-mu)/sd>4),"method":"EWMA z-score + 20-sample linear trend","sop":None}
    if level!="NORMAL":
        h=retrieve(label,1)
        if h and h[0][0]>=1.5: out["sop"]={"source":f"{h[0][1]['doc']} · page {h[0][1]['page']}","excerpt":h[0][1]["text"][:320]}
    return out

def _num(s):
    try: return float(s)
    except (TypeError, ValueError): return None

@app.post("/api/feed/csv")
async def feed_csv(file: UploadFile=File(...), column: str=Form(""), limit: float=Form(4.5), direction: str=Form("high"), label: str=Form("vibration")):
    rows=list(csv.DictReader(io.StringIO((await file.read()).decode("utf-8","ignore"))))
    if len(rows)<8: raise HTTPException(400,"CSV needs a header row and at least 8 data rows")
    cols=_numcols(rows)
    if not cols: raise HTTPException(400,"No numeric columns found")
    col=column if column in cols else cols[0]
    v=[_num(r.get(col)) for r in rows]; v=[a for a in v if a is not None]
    st=max(1,len(v)//300)
    return {"columns":cols,"column":col,"rows":len(v),"series":v[::st][-300:],"min":min(v),"max":max(v),"mean":round(sum(v)/len(v),3),**core(v,limit,direction,label)}

SENS=collections.defaultdict(lambda: collections.deque(maxlen=1000))

class Reading(BaseModel):
    sensor: str = Field(min_length=1, max_length=40)
    value: float

@app.post("/api/sensor")
def push_sensor(r: Reading):
    SENS[r.sensor].append(r.value); return {"stored":len(SENS[r.sensor])}

@app.get("/api/sensor/{sid}")
def read_sensor(sid: str, limit: float=4.5, direction: str="high", label: str="vibration"):
    v=list(SENS.get(sid,[]))
    if len(v)<8: return {"error":"need at least 8 readings","count":len(v)}
    return {"series":v[-150:],"rows":len(v),**core(v,limit,direction,label)}

# ================= v5: image understanding (vision) =================
import base64

async def _claude(content, system, max_tokens=500):
    import httpx
    async with httpx.AsyncClient(timeout=40) as h:
        r=await h.post("https://api.anthropic.com/v1/messages",headers={"x-api-key":os.getenv("ANTHROPIC_API_KEY",""),"anthropic-version":"2023-06-01"},json={"model":os.getenv("LLM_MODEL","claude-sonnet-4-5"),"max_tokens":max_tokens,"system":system,"messages":[{"role":"user","content":content}]})
        r.raise_for_status(); return r.json()["content"][0]["text"]

@app.post("/api/vision")
async def vision(file: UploadFile=File(...), note: str=Form("", max_length=500)):
    """Photo/diagram -> visual description + keywords -> retrieval over the indexed SOP PDFs."""
    data=await file.read(); mt=file.content_type or ""
    if mt not in ("image/jpeg","image/png","image/webp","image/gif"): raise HTTPException(400,"Upload a JPG, PNG, WEBP or GIF image")
    if len(data)>5_000_000: raise HTTPException(413,"Image exceeds 5 MB")
    if not os.getenv("ANTHROPIC_API_KEY"):
        return {"analysis":None,"sources":[],"message":"Image understanding needs ANTHROPIC_API_KEY set on the backend. Add it on Render, or describe the problem in text."}
    sysmsg="You are an industrial maintenance inspector. Describe only what is visible in the image: equipment, part, gauge reading, diagram labels, or defect. Do not claim a diagnosis with certainty. End with one final line: KEYWORDS: followed by 3-8 plain search keywords (equipment, component, symptom)."
    try:
        txt=await _claude([{"type":"image","source":{"type":"base64","media_type":mt,"data":base64.b64encode(data).decode()}},{"type":"text","text":"Operator note: "+(note or "none")}],sysmsg)
    except Exception as e:
        raise HTTPException(502,f"Vision call failed: {type(e).__name__}")
    m=re.search(r"KEYWORDS:\s*(.+)",txt,re.I); kw=(m.group(1) if m else "")+" "+note
    desc=re.sub(r"KEYWORDS:.*","",txt,flags=re.I|re.S).strip()
    hits=[h for h in retrieve(kw) if h[0]>=1.5]
    return {"analysis":desc,"keywords":kw.strip(),"safety":SAFETY,"sources":[{"doc":c["doc"],"page":c["page"],"score":round(s,2),"excerpt":c["text"][:320]} for s,c in hits]}

# ================= v6: advanced suites =================
import statistics, uuid, json as _json

def _is_index(vals):
    d=[b-a for a,b in zip(vals,vals[1:])]
    return len(d)>3 and len(set(round(x,6) for x in d))==1 and d[0]>0

def _numcols(rows):
    ok=[c for c in rows[0] if c and all(_num(r.get(c)) is not None for r in rows[:20])]
    keep=[c for c in ok if not _is_index([_num(r.get(c)) for r in rows[:20]])]
    return keep or ok

def _col(rows, col):
    cols=_numcols(rows)
    c=col if col in cols else (cols[0] if cols else None)
    return c,[_num(r.get(c)) for r in rows if c and _num(r.get(c)) is not None]

async def _rows(f):
    rows=list(csv.DictReader(io.StringIO((await f.read()).decode("utf-8","ignore"))))
    if len(rows)<14: raise HTTPException(400,"Need a header and at least 14 data rows")
    return rows

@app.post("/api/forecast")
async def forecast(file: UploadFile=File(...), column: str=Form(""), lead_days: int=Form(7), stock: float=Form(0), price: float=Form(100)):
    """Weekday-seasonal + trend demand forecast, reorder quantity, rule-based price action."""
    c,v=_col(await _rows(file),column)
    if not c: raise HTTPException(400,"No numeric column")
    n=len(v); m=sum(v)/n or 1
    si=[(sum(v[i] for i in range(w,n,7))/len(range(w,n,7)))/m for w in range(7)]
    ds=[v[i]/(si[i%7] or 1) for i in range(n)]
    lvl=sum(ds[-7:])/7; tr=(lvl-sum(ds[-14:-7])/7)/7
    fc=[max(0,round((lvl+tr*(j+1))*si[(n+j)%7],1)) for j in range(14)]
    lead=max(1,min(14,lead_days)); sd=statistics.pstdev(ds[-28:])
    reorder=max(0,round(sum(fc[:lead])+1.65*sd*lead**.5-stock))
    cover=stock/((sum(fc[:7])/7) or 1); chg=(sum(fc[:7])-sum(v[-7:]))/(sum(v[-7:]) or 1)*100
    act,f=("Raise price ~4% (demand rising, thin cover)",1.04) if chg>10 and cover<10 else ("Run ~7% clearance (overstock)",.93) if cover>30 else ("Hold price",1.0)
    return {"column":c,"history":v[-42:],"forecast":fc,"reorder_qty":reorder,"stock_cover_days":round(cover,1),"demand_change_pct":round(chg,1),"price_action":act,"suggested_price":round(price*f,2),"method":"weekday seasonality + trend; pricing is rule-based, validate with real elasticity"}

@app.post("/api/energy")
async def energy(file: UploadFile=File(...), column: str=Form(""), tariff_peak: float=Form(9), tariff_off: float=Form(6)):
    """Expects hourly rows. Finds daily profile, peak/idle behaviour and load-shift saving."""
    c,v=_col(await _rows(file),column); n=len(v)
    if not c or n<48: raise HTTPException(400,"Need numeric hourly data, at least 48 rows")
    prof=[sum(v[i] for i in range(h,n,24))/len(range(h,n,24)) for h in range(24)]
    order=sorted(range(24),key=lambda h:-prof[h]); peak,off=order[:4],order[-4:]
    med=sorted(v)[n//2]; mu=sum(v)/n; sd=statistics.pstdev(v)
    save=0.15*sum(prof[h] for h in peak)*(tariff_peak-tariff_off)*365
    return {"column":c,"profile":[round(p,1) for p in prof],"peak_hours":sorted(peak),"offpeak_hours":sorted(off),"idle_share_pct":round(100*sum(1 for x in v if x<.5*med)/n,1),"abnormal_points":sum(1 for x in v if x>mu+3*sd),"recommendation":f"Shift ~15% of peak-hour load (hours {sorted(peak)}) to hours {sorted(off)}","est_annual_saving":round(save),"method":"hour-of-day profile; saving assumes your tariffs and a feasible 15% shift"}

WF={}; AUDIT=[]
def _log(i, ev, by="agent"): AUDIT.append({"ts":datetime.now(timezone.utc).isoformat(),"id":i,"event":ev,"by":by})

class WReq(BaseModel):
    title: str=Field(min_length=3,max_length=200)
    amount: float=Field(default=0,ge=0)
class Dec(BaseModel):
    approve: bool
    by: str=Field(default="supervisor",max_length=40)

@app.post("/api/workflow")
def wf_new(r: WReq):
    i="WF-"+uuid.uuid4().hex[:6].upper(); hold=r.amount>=10000
    WF[i]={"id":i,"title":r.title,"amount":r.amount,"status":"awaiting_approval" if hold else "executed","steps":["Understand request","ERP lookup: stock & vendor (simulated connector)","Draft purchase order / task","Notify stakeholders (simulated email connector)"]}
    _log(i,"agent planned 4 steps"); _log(i,"held for human approval (amount >= 10000)" if hold else "auto-executed (below approval threshold)")
    return WF[i]

@app.post("/api/workflow/{i}/decide")
def wf_decide(i: str, d: Dec):
    w=WF.get(i)
    if not w or w["status"]!="awaiting_approval": raise HTTPException(404,"No pending request with that id")
    w["status"]="executed" if d.approve else "rejected"; _log(i,"approved -> executed" if d.approve else "rejected",d.by); return w

@app.get("/api/workflow")
def wf_list(): return {"items":list(WF.values())[-10:],"audit":AUDIT[-20:]}

DOM={"farmer":"You are a regional-language farm advisor for India. Give practical advice on crop selection, sowing, irrigation, fertiliser and pest control. Ask for location and season if missing. Never invent market prices; say mandi prices are not connected. Refer to the local KVK or agriculture officer for pesticide doses.",
"service":"You are a multilingual citizen-service assistant (government, education, banking, healthcare information). Give process steps and required documents. Say when unsure. No legal or medical decisions.",
"patient":"You summarise patient monitoring readings for a clinician in plain language. Highlight abnormal trends, never diagnose, and recommend clinician review."}
class AssistReq(BaseModel):
    domain: str="service"
    query: str=Field(min_length=2,max_length=2000)
    lang: str="auto"

@app.post("/api/assist")
async def assist(a: AssistReq):
    if a.domain not in DOM: raise HTTPException(400,"Unknown domain")
    if not os.getenv("ANTHROPIC_API_KEY"): return {"answer":None,"message":"Set ANTHROPIC_API_KEY on the backend to enable multilingual assistance."}
    try: return {"answer":await _claude(a.query,DOM[a.domain]+f" Reply in this language: {a.lang} (if 'auto', use the user's language).",600)}
    except Exception as e: raise HTTPException(502,f"Assistant call failed: {type(e).__name__}")

MODES={"defect":'Inspect this product/surface image. Reply ONLY JSON: {"defects":[{"type":"scratch|crack|dent|discolouration|dimensional|other","severity":"low|medium|high","where":"short location","confidence":0.0}],"verdict":"PASS|FAIL|REVIEW","note":"..."}',
"aerial":'Analyse this aerial/drone image. Reply ONLY JSON: {"zones":[{"label":"healthy crop|stressed crop|pest-affected|flooded|damaged building|blocked road|person|other","priority":"low|medium|high","where":"short location"}],"summary":"...","recommended_inspection":"..."}',
"retail":'List retail products visible. Reply ONLY JSON: {"items":[{"name":"...","qty":1}],"note":"..."}'}
CAT={"milk":30,"biscuit":20,"chips":25,"soap":40,"rice":60,"juice":35}
DEFECTS=collections.Counter()

@app.post("/api/inspect")
async def inspect(file: UploadFile=File(...), mode: str=Form("defect")):
    if mode not in MODES: raise HTTPException(400,"Unknown mode")
    data=await file.read(); mt=file.content_type or ""
    if mt not in ("image/jpeg","image/png","image/webp","image/gif"): raise HTTPException(400,"Upload a JPG, PNG, WEBP or GIF image")
    if len(data)>5_000_000: raise HTTPException(413,"Image exceeds 5 MB")
    if not os.getenv("ANTHROPIC_API_KEY"): return {"message":"Image analysis needs ANTHROPIC_API_KEY set on the backend."}
    try: txt=await _claude([{"type":"image","source":{"type":"base64","media_type":mt,"data":base64.b64encode(data).decode()}},{"type":"text","text":"Analyse."}],MODES[mode]+" Report only what is visible; do not claim certainty.",700)
    except Exception as e: raise HTTPException(502,f"Vision call failed: {type(e).__name__}")
    try: d=_json.loads(re.search(r"\{.*\}",txt,re.S).group(0))
    except Exception: return {"verdict":"REVIEW","note":txt[:400]}
    if mode=="defect":
        for x in d.get("defects",[]): DEFECTS[str(x.get("type","other"))]+=1
        d["pareto"]=dict(DEFECTS.most_common())
    if mode=="retail":
        tot=0; un=[]
        for it in d.get("items",[]):
            p=next((v for k,v in CAT.items() if k in str(it.get("name","")).lower()),None)
            if p is None: un.append(str(it.get("name")))
            else: tot+=p*int(it.get("qty",1) or 1)
        d["bill"]={"total":tot,"unmatched":un}
    return d


# ================= v7: reproducible judge-mode evaluation =================
@app.get("/api/evaluate")
def evaluate():
    """Small deterministic retrieval smoke-test suite. This is a benchmark harness, not a certified accuracy claim."""
    cases = [
        {"query": "bearing vibration high and noise", "expected": "CNC_Maintenance_v3.pdf"},
        {"query": "motor overheating garam at 88C", "expected": "Motor_SOP_v2.pdf"},
        {"query": "hydraulic oil leak", "expected": "Hydraulic_SOP_v1.pdf"},
        {"query": "conveyor belt drifting off centre", "expected": "Conveyor_SOP_v3.pdf"},
        {"query": "gearbox whine oil temperature", "expected": "Gearbox_SOP_v2.pdf"},
        {"query": "VFD overcurrent trip", "expected": "Drive_SOP_v2.pdf"},
        {"query": "pneumatic air pressure drop", "expected": "Pneumatic_SOP_v1.pdf"},
        {"query": "quality surface scratch defect", "expected": "Quality_SOP_v4.pdf"},
        {"query": "safety PPE before maintenance", "expected": "Safety_SOP_v1.pdf"},
    ]
    results = []
    hits = 0
    reciprocal = 0.0
    for case in cases:
        matches = retrieve(case["query"], 3)
        rank = next((i + 1 for i, (_, chunk) in enumerate(matches)
                     if chunk["doc"] == case["expected"]), None)
        if rank:
            hits += 1
            reciprocal += 1 / rank
        results.append({
            "query": case["query"],
            "expected_source": case["expected"],
            "matched_source": matches[0][1]["doc"] if matches else None,
            "expected_source_rank": rank,
            "pass_at_3": rank is not None,
        })
    total = len(cases)
    return {
        "suite": "INDUX-OS SOP retrieval smoke test v1",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "method": "BM25-style keyword retrieval over currently indexed PDF chunks",
        "test_cases": total,
        "source_recall_at_3_pct": round(100 * hits / total, 1),
        "mean_reciprocal_rank": round(reciprocal / total, 3),
        "results": results,
        "limitations": [
            "Small curated smoke-test set, not an independent evaluation",
            "Scores measure source retrieval only, not answer correctness or safety",
            "Upload the actual approved SOP library and build a representative held-out test set before reporting accuracy"
        ]
    }
