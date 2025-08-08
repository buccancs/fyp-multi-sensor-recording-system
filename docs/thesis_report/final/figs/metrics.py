import json, csv, re, pathlib as p
import numpy as np, pandas as pd

def load_sync_log(fp):
    t,o,q=[],[],[]
    for ln in p.Path(fp).read_text().splitlines():
        m=re.search(r"t=(\d+\.?\d*), offset_ms=(-?\d+\.?\d*), q=(\d+\.?\d*)", ln)
        if m: t.append(float(m.group(1))); o.append(float(m.group(2))); q.append(float(m.group(3)))
    return pd.DataFrame({"t":t,"off":o,"q":q})

def load_frames_csv(fp):
    t=[]
    with open(fp) as f:
        r=csv.DictReader(f)
        for row in r: t.append(float(row["ts_ms"]))
    t=np.array(t)/1000.0
    dt=np.diff(t)
    fps=pd.Series(1.0/np.clip(dt,1e-6,1e9), index=t[1:])
    return pd.DataFrame({"t":fps.index, "fps":fps.values})

def load_gsr_csv(fp):
    t=[]
    with open(fp) as f:
        r=csv.DictReader(f)
        for row in r: t.append(float(row["Timestamp_ms"]))
    t=np.array(t)/1000.0
    dt=np.diff(t)
    hz=1.0/np.clip(dt,1e-6,1e9)
    return pd.DataFrame({"t":t[1:], "hz":hz})

def load_events(fp):
    ev=[]
    for ln in p.Path(fp).read_text().splitlines():
        m=re.search(r"(\d+\.?\d*)\s+(UI_FREEZE|DISC_FAIL|RECONNECT|HEARTBEAT_MISS)", ln)
        if m: ev.append((float(m.group(1)), m.group(2)))
    return pd.DataFrame(ev, columns=["t","ev"])

def completeness(exp_n, got_n):
    return {"exp":exp_n, "got":got_n, "pct":100.0*got_n/max(exp_n,1)}