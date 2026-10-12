"""
Rebuilds every summary table in results/ from the record-level flags.

Usage (from the repository root):
    python scripts/reproduce_tables.py

Needs only pandas. The analytic ("clean") corpus is every record with
Likely_FalsePositive == 0 (N = 6,404).
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"
RES.mkdir(exist_ok=True)

full = pd.read_csv(ROOT / "data" / "records_flags.csv")
clean = full[full["Likely_FalsePositive"] == 0].copy()
N = len(clean)


def pct(x, n):
    return round(100 * x / n, 2) if n else None


# ---------------------------------------------------------------- RQ1
dom = clean["PrimaryDomain"].value_counts().rename_axis("domain").reset_index(name="n")
dom["pct"] = dom["n"].apply(lambda x: pct(x, N))
dom.to_csv(RES / "rq1_domain_distribution.csv", index=False)


def orientation(d, label):
    t, p = d["Technology_Signal"], d["Pedagogy_Signal"]
    n = len(d)
    return {
        "year": label, "n_records": n,
        "technology_n": int(t.sum()), "technology_pct": pct(t.sum(), n),
        "pedagogy_n": int(p.sum()), "pedagogy_pct": pct(p.sum(), n),
        "both_n": int(((t == 1) & (p == 1)).sum()),
        "technology_only_n": int(((t == 1) & (p == 0)).sum()),
        "pedagogy_only_n": int(((t == 0) & (p == 1)).sum()),
        "neither_n": int(((t == 0) & (p == 0)).sum()),
    }


rows = [orientation(g, y) for y, g in clean.groupby("year")]
rows.append(orientation(clean, "2015-2025"))
pd.DataFrame(rows).to_csv(RES / "rq1_tech_pedagogy_by_year.csv", index=False)

# ---------------------------------------------------------------- RQ2
# 22 UX attributes, grouped into app vs user aspect (Alshammare et al., 2025)
ATTR = [
    ("Usability", "App aspect", "Usability"),
    ("Effectiveness", "App aspect", "Usability__Effectiveness"),
    ("Efficiency", "App aspect", "Usability__Efficiency"),
    ("Ease of Use", "App aspect", "Usability__Ease_of_Use"),
    ("Functionality", "App aspect", "Functionality"),
    ("Quality of interaction", "App aspect", "Quality_of_interaction"),
    ("Pragmatic Quality", "App aspect", "Pragmatic_Quality"),
    ("Perspicuity", "App aspect", "Perspicuity"),
    ("Dependability", "App aspect", "Dependability"),
    ("Usefulness", "App aspect", "Usefulness"),
    ("Responsiveness", "App aspect", "Responsiveness"),
    ("Novelty", "App aspect", "Novelty"),
    ("Aesthetics", "App aspect", "Aesthetics"),
    ("Attractiveness", "App aspect", "Aesthetics_Immersion__Attractiveness"),
    ("Stimulation", "App aspect", "Stimulation"),
    ("Engagement", "User aspect", "UX_Satisfaction_Engagement__Engagement"),
    ("Satisfaction", "User aspect", "UX_Satisfaction_Engagement__Satisfaction"),
    ("Emotional", "User aspect", "Emotional"),
    ("Enjoyment", "User aspect", "UX_Satisfaction_Engagement__Enjoyment"),
    ("Cognitive", "User aspect", "Cognitive"),
    ("Subjective Quality", "User aspect", "Subjective_Quality"),
    ("Hedonic Quality", "User aspect", "Hedonic_Quality"),
]
a = pd.DataFrame(ATTR, columns=["attribute", "orientation", "source_column"])
a["n"] = [int(clean[c].sum()) for c in a["source_column"]]
a["pct_of_records"] = a["n"].apply(lambda x: pct(x, N))
a = a.sort_values("n", ascending=False)
mentions = a["n"].sum()
a["pct_of_mentions"] = a["n"].apply(lambda x: pct(x, mentions))
tot = a.groupby("orientation", as_index=False)["n"].sum()
tot["attribute"] = tot["orientation"] + " total"
tot["pct_of_mentions"] = tot["n"].apply(lambda x: pct(x, mentions))
a = pd.concat([a, tot], ignore_index=True)
a.to_csv(RES / "rq2a_ux_attributes_22.csv", index=False)

top10 = a.dropna(subset=["source_column"]).head(10)
by_dom = []
for d, g in clean.groupby("PrimaryDomain"):
    row = {"domain": d, "n_records": len(g)}
    for _, r in a.dropna(subset=["source_column"]).iterrows():
        row[r["attribute"]] = pct(g[r["source_column"]].sum(), len(g))
    by_dom.append(row)
by_dom = pd.DataFrame(by_dom).sort_values("n_records", ascending=False)
by_dom.to_csv(RES / "rq2b_attributes_by_domain_full22.csv", index=False)
by_dom[["domain", "n_records"] + top10["attribute"].tolist()].to_csv(
    RES / "rq2b_attributes_by_domain_top10.csv", index=False)

# ---------------------------------------------------------------- RQ3
STAGES = [
    ("1. Design Feature", "DesignFeature_V8"),
    ("2. UX Response", "UX_Response_Signal"),
    ("3. Behavioral Interaction", "Behavioral_EvidenceSignal"),
    ("4. Learning Process", "LearningProcess_Signal"),
    ("5. Learning Outcome", "LearningOutcome_Signal"),
]


def funnel(d):
    out, mask = [], pd.Series(True, index=d.index)
    for name, col in STAGES:
        mask &= d[col] == 1
        out.append({"stage": name, "column": col,
                    "individual_n": int(d[col].sum()), "individual_pct": pct(d[col].sum(), len(d)),
                    "cumulative_n": int(mask.sum()), "cumulative_pct": pct(mask.sum(), len(d))})
    return pd.DataFrame(out)


funnel(clean).to_csv(RES / "rq3_evidence_funnel.csv", index=False)

# pairwise co-occurrence of stages, ignoring order
cols = [c for _, c in STAGES]
names = [s for s, _ in STAGES]
co = pd.DataFrame(0, index=names, columns=names)
for i, ci in enumerate(cols):
    for j, cj in enumerate(cols):
        co.iloc[i, j] = int(((clean[ci] == 1) & (clean[cj] == 1)).sum())
co.index.name = "stage"
co.to_csv(RES / "rq3_stage_cooccurrence.csv")

# sensitivity: strict / original / broad keyword lists x citation subsets
VARIANTS = [
    ("Strict", "LearningProcess_Strict", "LearningOutcome_Strict"),
    ("Original", "LearningProcess_Signal", "LearningOutcome_Signal"),
    ("Broad", "LearningProcess_Broad", "LearningOutcome_Broad"),
]
ranked = clean.sort_values(["cited_by", "record_id"], ascending=[False, True])
subsets = [
    ("All records (clean)", clean),
    ("Top 10% most-cited", ranked.head(round(0.10 * N))),
    ("Top 5% most-cited", ranked.head(round(0.05 * N))),
]
sens = []
for sname, d in subsets:
    base = (d["DesignFeature_V8"] == 1) & (d["UX_Response_Signal"] == 1) & (d["Behavioral_EvidenceSignal"] == 1)
    for vname, lp, lo in VARIANTS:
        p = base & (d[lp] == 1)
        o = p & (d[lo] == 1)
        sens.append({"subset": sname, "keyword_list": vname, "n": len(d),
                     "behavioral_cum_n": int(base.sum()),
                     "learning_process_cum_n": int(p.sum()), "learning_process_cum_pct": pct(p.sum(), len(d)),
                     "full_chain_n": int(o.sum()), "full_chain_pct": pct(o.sum(), len(d))})
pd.DataFrame(sens).to_csv(RES / "rq3_sensitivity.csv", index=False)

# effect of removing the 293 flagged records
fo, co_ = orientation(full, "full"), orientation(clean, "clean")
noise = [
    {"metric": "N records", "full": len(full), "clean": N, "diff_pp": None},
    {"metric": "Technology-oriented %", "full": fo["technology_pct"], "clean": co_["technology_pct"],
     "diff_pp": round(co_["technology_pct"] - fo["technology_pct"], 2)},
    {"metric": "Pedagogy-oriented %", "full": fo["pedagogy_pct"], "clean": co_["pedagogy_pct"],
     "diff_pp": round(co_["pedagogy_pct"] - fo["pedagogy_pct"], 2)},
]
ff, fc = funnel(full), funnel(clean)
for i in range(len(STAGES)):
    noise.append({"metric": f"Cumulative % - {STAGES[i][0]}", "full": ff.loc[i, "cumulative_pct"],
                  "clean": fc.loc[i, "cumulative_pct"],
                  "diff_pp": round(fc.loc[i, "cumulative_pct"] - ff.loc[i, "cumulative_pct"], 2)})
pd.DataFrame(noise, dtype=object).to_csv(RES / "corpus_noise_robustness.csv", index=False)

# ---------------------------------------------------------------- study type
st = []
for k, v in clean["ResearchType"].value_counts().items():
    st.append({"table": "Research type", "category": k, "n": int(v), "denominator": N, "pct": pct(v, N)})
emp = clean[clean["ResearchType"] == "Empirical"]
for k, v in emp["MethodologicalApproach"].value_counts().items():
    st.append({"table": "Approach (empirical studies only)", "category": k, "n": int(v),
               "denominator": len(emp), "pct": pct(v, len(emp))})
for k, v in clean["SpecificMethod"].value_counts().items():
    st.append({"table": "Dominant method (first match)", "category": k, "n": int(v), "denominator": N, "pct": pct(v, N)})
pd.DataFrame(st).to_csv(RES / "study_type_and_methods.csv", index=False)

# ---------------------------------------------------------------- validation
VSTAGES = ["DesignFeature", "PragmaticUX", "ExperientialUX", "BehavioralData", "LearningProcess", "LearningOutcome"]
va = pd.read_csv(ROOT / "validation" / "validation_setA_topcited.csv")
vb = pd.read_csv(ROOT / "validation" / "validation_setB_stratified.csv")


def agreement(v, label):
    out = []
    for s in VSTAGES:
        auto, man = v[f"Automated_{s}"].eq("Yes"), v[f"ManualCheck_{s}"].eq("Yes")
        coded = v[f"ManualCheck_{s}"].isin(["Yes", "No"])
        auto, man = auto[coded], man[coded]
        tp, fp = int((auto & man).sum()), int((auto & ~man).sum())
        fn, tn = int((~auto & man).sum()), int((~auto & ~man).sum())
        n = tp + fp + fn + tn
        prec = tp / (tp + fp) if tp + fp else None
        rec = tp / (tp + fn) if tp + fn else None
        f1 = 2 * prec * rec / (prec + rec) if prec and rec else None
        out.append({"set": label, "stage": s, "n": n, "TP": tp, "FP": fp, "FN": fn, "TN": tn,
                    "agreement": round((tp + tn) / n, 4), "precision": round(prec, 4) if prec else prec,
                    "recall": round(rec, 4) if rec else rec, "f1": round(f1, 4) if f1 else f1})
    return out


val = pd.DataFrame(agreement(va, "A (top-cited, n=112)") + agreement(vb, "B (stratified, n=100)")
                   + agreement(pd.concat([va, vb]), "A+B pooled (n=212)"))
pooled = val[val["set"].str.startswith("A+B")]
val = pd.concat([val, pd.DataFrame([{"set": "A+B pooled (n=212)", "stage": "Mean over stages",
                                     "agreement": round(pooled["agreement"].mean(), 4),
                                     "precision": round(pooled["precision"].mean(), 4),
                                     "recall": round(pooled["recall"].mean(), 4),
                                     "f1": round(pooled["f1"].mean(), 4)}])], ignore_index=True)
for c in ["n", "TP", "FP", "FN", "TN"]:
    val[c] = val[c].astype("Int64")
val.to_csv(RES / "validation_agreement.csv", index=False)

print(f"Done. Clean corpus N = {N}. Tables written to {RES}")
