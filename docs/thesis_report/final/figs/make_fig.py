import matplotlib.pyplot as plt
from pathlib import Path
from metrics import load_sync_log, load_frames_csv, load_gsr_csv, load_events, completeness

def f_clock_offset(sync_fp, out_fp):
    df=load_sync_log(sync_fp)
    fig,ax=plt.subplots()
    ax.plot(df.t, df.off)
    ax.set_xlabel("time (s)"); ax.set_ylabel("offset (ms)")
    fig.savefig(out_fp, dpi=300, bbox_inches="tight")

def f_jitter(sync_fp, out_fp):
    df=load_sync_log(sync_fp); j=(df.off-df.off.mean()).abs()
    fig,ax=plt.subplots()
    ax.hist(j, bins=40)
    ax.set_xlabel("|offset-mean| (ms)"); ax.set_ylabel("count")
    fig.savefig(out_fp, dpi=300, bbox_inches="tight")

def f_fps(rgb_fp, th_fp, out_fp):
    dr=load_frames_csv(rgb_fp); dt=load_frames_csv(th_fp)
    fig,ax=plt.subplots()
    ax.plot(dr.t, dr.fps, label="rgb")
    ax.plot(dt.t, dt.fps, label="thermal")
    ax.set_xlabel("time (s)"); ax.set_ylabel("fps"); ax.legend()
    fig.savefig(out_fp, dpi=300, bbox_inches="tight")

def f_gsr_rate(gsr_fp, out_fp):
    dg=load_gsr_csv(gsr_fp)
    fig,ax=plt.subplots()
    ax.plot(dg.t, dg.hz)
    ax.set_xlabel("time (s)"); ax.set_ylabel("Hz")
    fig.savefig(out_fp, dpi=300, bbox_inches="tight")

def f_events(ev_fp, out_fp):
    de=load_events(ev_fp)
    fig,ax=plt.subplots()
    for e in de.ev.unique():
        t=de[de.ev==e].t
        ax.scatter(t, [e]*len(t))
    ax.set_xlabel("time (s)"); ax.set_ylabel("event")
    fig.savefig(out_fp, dpi=300, bbox_inches="tight")

if __name__=="__main__":
    out=Path("out"); out.mkdir(exist_ok=True)
    f_clock_offset("sessions/s1/pc_sync.log", out/"F5_clock_offset.png")
    f_jitter("sessions/s1/pc_sync.log", out/"F6_sync_jitter.png")
    f_fps("sessions/s1/rgb_frames.csv", "sessions/s1/th_frames.csv", out/"F7_fps.png")
    f_gsr_rate("sessions/s1/gsr.csv", out/"F8_gsr_rate.png")
    f_events("sessions/s1/events.log", out/"F14_events.png")