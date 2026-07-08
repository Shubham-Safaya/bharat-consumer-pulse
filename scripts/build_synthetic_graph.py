#!/usr/bin/env python3
"""Mobile-first synthetic identity graph for the India ecosystem (spec 8).

Mirrors us-consumer-pulse/scripts/build_synthetic_graph.py but keys on a
synthetic PHONE-HASH as the primary identifier — the Indian reality (UPI,
banking, messaging all resolve to the number). Uses my identity-resolver
engine. 100% synthetic; no real individuals; results precomputed to JSON.

Run locally: python3 scripts/build_synthetic_graph.py [--persons 100000]
"""
import argparse, hashlib, json, os, random, string, sys, time
from collections import defaultdict

sys.path.insert(0, os.path.expanduser("~/Documents/Claude/Projects/identity-resolution-engine"))
from identity_resolver import IdentityResolver, Record
from identity_resolver.resolver import ResolverConfig

random.seed(42)

FIRST = ["arjun","rohan","vikram","raj","amit","aditya","karan","sanjay","rahul","ankit",
         "priya","neha","divya","anjali","sneha","pooja","kavya","riya","meera","aisha",
         "arun","deepak","manish","suresh","ramesh","vishal","nikhil","varun","gaurav","siddharth",
         "shreya","nisha","swati","ritu","preeti","anita","sunita","geeta","lakshmi","fatima"]
LAST = ["sharma","verma","gupta","singh","kumar","patel","reddy","nair","iyer","rao",
        "joshi","mehta","desai","shah","agarwal","malhotra","kapoor","bhat","kaul","koul",
        "das","banerjee","chatterjee","mukherjee","pillai","menon","naidu","chowdhury","mishra","tiwari"]
CITIES = ["mumbai","delhi","bangalore","hyderabad","chennai","kolkata","pune","jaipur","lucknow","srinagar"]

def phone(): return "9" + "".join(random.choice(string.digits) for _ in range(9))
def phash(p): return hashlib.sha256(("SYNTHETIC-SALT" + p).encode()).hexdigest()[:16]

def synth_population(n):
    persons, households = [], []
    pid = 0
    while pid < n:
        hh_size = random.choices([1,2,3,4,5,6],weights=[.12,.22,.24,.22,.12,.08])[0]
        hhid = f"HH{len(households):06d}"; city = random.choice(CITIES)
        pin = f"{random.randint(110000,855999)}"
        surname = random.choice(LAST); members = []
        shared_phone = phone() if random.random() < .22 else None  # shared family number (very common)
        for i in range(hh_size):
            if pid >= n: break
            first = random.choice(FIRST)
            pnum = shared_phone if (shared_phone and random.random() < .5) else phone()
            members.append({"pid":f"P{pid:06d}","first":first,"last":surname,"phone":pnum,"city":city})
            pid += 1
        households.append({"hhid":hhid,"city":city,"pin":pin,"members":members})
        persons.extend(members)
    return persons, households

def noisy(s,p=.05):
    if not s or random.random()>p: return s
    i=random.randint(0,len(s)-1); return s[:i]+random.choice(string.ascii_lowercase)+s[i+1:]

def fragment(households):
    records, truth = [], {}; rid=0
    for hh in households:
        for m in hh["members"]:
            for sysname in random.sample(["upi","telecom","ecom"], random.choices([1,2,3],weights=[.3,.45,.25])[0]):
                rrid=f"r{rid:07d}"; rid+=1; truth[rrid]=m["pid"]
                ph = m["phone"]
                # phone format noise: +91, spaces, leading 0
                if random.random()<.2: ph = "+91"+ph
                elif random.random()<.15: ph = "0"+ph
                # email is secondary/sparse in this ecosystem
                email = f"{m['first']}.{m['last']}{random.randint(1,9999)}@example-mail.test" if random.random()<.35 else None
                records.append(Record(record_id=rrid, source=sysname, phone=ph,
                    email=(email.upper() if email and random.random()<.1 else email),
                    first_name=noisy(m["first"]), last_name=noisy(m["last"]),
                    city=hh["city"], zip_code=hh["pin"]))
    return records, truth

def pairwise(clusters, truth):
    tp=fp=pred=0; groups=defaultdict(list)
    for r,p in truth.items(): groups[p].append(r)
    total=sum(len(v)*(len(v)-1)//2 for v in groups.values())
    for c in clusters:
        ids=[r.record_id for r in c.records]
        for i in range(len(ids)):
            for j in range(i+1,len(ids)):
                pred+=1
                if truth[ids[i]]==truth[ids[j]]: tp+=1
                else: fp+=1
    return (tp/pred if pred else 1.0),(tp/total if total else 1.0),tp,fp,total

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--persons",type=int,default=100000); a=ap.parse_args()
    t0=time.time()
    print(f"generating {a.persons:,} synthetic persons (mobile-first)…")
    persons, households = synth_population(a.persons)
    records, truth = fragment(households)
    print(f"  {len(households):,} households, {len(records):,} phone-keyed records")
    res = IdentityResolver(ResolverConfig(probabilistic_threshold=0.9, match_on_name_zip=False)).resolve(records)
    s = res.summary()
    p,r,tp,fp,ttp = pairwise(res.clusters, truth)
    print(f"  clusters={s['total_clusters']:,} precision={p:.3f} recall={r:.3f}")
    out={"generated":time.strftime("%Y-%m-%d"),
      "banner":"100% synthetic population; no real individuals; mobile-first methodology demonstration.",
      "engine":"identity-resolver (github.com/Shubham-Safaya/identity-resolution-engine)",
      "primary_key":"synthetic_phone_hash",
      "population":{"persons":len(persons),"households":len(households),"records":len(records)},
      "resolution":{"clusters":s["total_clusters"],"deterministic_matches":s["deterministic_matches"],
        "probabilistic_matches":s["probabilistic_matches"],
        "dedup_rate":round(1-s["total_clusters"]/len(records),4)},
      "vs_ground_truth":{"pairwise_precision":round(p,4),"pairwise_recall":round(r,4),
        "true_pairs":ttp,"false_merged_pairs":fp,
        "note":"Shared family phone numbers (a real Indian pattern) are the main false-merge source — the identifier-frequency-cap lesson, mobile edition."},
      "runtime_seconds":round(time.time()-t0,1)}
    os.makedirs("data/synthetic",exist_ok=True)
    json.dump(out,open("data/synthetic/results.json","w"),indent=2)
    print(f"wrote data/synthetic/results.json ({time.time()-t0:.1f}s)")

if __name__=="__main__": main()
