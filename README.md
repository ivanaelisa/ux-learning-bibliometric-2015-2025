# UX Design in Digital Learning Platforms, 2015–2025: Data and Coding Rules

Supporting data for the paper:

> [Author names]. "From Aesthetics to Learning: A Bibliometric and Conceptual Review of User Experience Design in Digital Learning Platforms (2015–2025)." In *[Conference name]*, 2026.

DOI of this dataset: [Zenodo DOI]

The repository contains the record-level coding output, the full rule set that produced it, the manual validation sample, and a short script that rebuilds every table and figure value reported in the paper.

## Folder layout

```
data/
  records_flags.csv      one row per record (6,697 rows): EID, DOI, and a 0/1 flag for every coded construct
  columns.csv            what each column in records_flags.csv means
coding/
  coding_dictionary.csv  pattern behind every column, exactly as applied
  domain_rules.csv       primary-domain rules in priority order
validation/
  validation_setA_topcited.csv     100 most-cited records + 12 full-chain records (n = 112)
  validation_setB_stratified.csv   stratified by domain and year period (n = 100)
results/
  summary tables (output of scripts/reproduce_tables.py)
  fig1_keyword_cooccurrence_nodes.csv   Biblioshiny output for Fig. 1
figures/
  fig1_keyword_cooccurrence_network.png
scripts/
  reproduce_tables.py
supplementary/
  Supplementary_Material.pdf
```

## Source and scope

Records were retrieved from Scopus (search closed on 31 December 2025): English-language journal articles and conference papers published 2015–2025, matching

```
("user experience" OR "user interface" OR "usability") AND
("e-learning" OR "online learning" OR "digital learning" OR
 "learning platform" OR "learning management system")
```

Of the 6,697 processed records, 293 were flagged as off-topic (`Likely_FalsePositive = 1`). They stay in the file so the exclusion can be checked, but all results use the remaining 6,404 records.

## What is not included

Titles, abstracts, keywords and other Scopus metadata of the full corpus are not redistributed, in line with the Scopus terms of use. Each record is identified by its Scopus `eid` and, where one exists, its `doi` (576 records have no DOI), so the corpus can be rebuilt by anyone with Scopus access. `record_id` is the row number in our processed export and links records across files. The two validation files also include titles.

## How the coding works

Each record was coded by case-insensitive pattern matching on one lower-case text field (title + abstract + author keywords + index keywords). The same rules apply to every record, and no manual decision enters the counts. `coding/coding_dictionary.csv` lists, for each column:

- `match_type`: `regex`, `substring` (any listed term), `derived` (built from other columns), or a multi-step rule
- `patterns`: the terms or regular expression
- `full_rule`: the original spreadsheet formula, with cell references replaced by column names

A few notes that affect interpretation:

- **Technology vs pedagogy.** `Technology_Signal` and `Pedagogy_Signal` are independent flags, so one record can carry both. Overall, 1,606 records have both, 4,221 only technology, 159 only pedagogy, and 418 neither (`results/rq1_tech_pedagogy_by_year.csv`). A pedagogy flag means pedagogical terms appear in the indexed record. It does not show that a pedagogical theory was applied.
- **Evidence chain.** The five stages are counted two ways in `results/rq3_evidence_funnel.csv`: on their own (`individual_n`) and cumulatively, where a record counts at stage *k* only if it also meets stages 1 to *k*−1. `results/rq3_stage_cooccurrence.csv` gives pairwise counts that ignore stage order (for example, 790 records show both a UX response and a learning outcome).
- **Abstract-level coding.** A study may report an outcome in its full text without mentioning it in the abstract. The evidence-chain shares describe what is visible in the indexed record, not in the full paper.
- **Earlier versions.** Columns described in `coding_dictionary.csv` as "earlier version" are kept for transparency but are not used in any reported result.

## Validation

Automated codes for six categories were compared with manual coding of 212 records by one coder. Where the abstract was ambiguous, the coder read the full text; these cases are marked in `manual_notes`. Agreement, precision, recall and F1 per category and per set are in `results/validation_agreement.csv`. Across the six categories in the pooled set, mean agreement is 0.90 and mean F1 is 0.88.

## Reproducing the tables

```
pip install pandas
python scripts/reproduce_tables.py
```

The script reads `data/` and `validation/` and rewrites the summary tables in `results/` (the Fig. 1 file is left as is).

| Value in the paper | File |
|---|---|
| Fig. 1 PageRank values and clusters | `fig1_keyword_cooccurrence_nodes.csv` (not script output) |
| Domain distribution (N = 6,404) | `rq1_domain_distribution.csv` |
| Technology 91.0%, pedagogy 27.6% | `rq1_tech_pedagogy_by_year.csv`, last row |
| Usability 53.0%; app vs user aspect 73.36% / 26.64% | `rq2a_ux_attributes_22.csv` |
| UX attributes by domain | `rq2b_attributes_by_domain_top10.csv`, `..._full22.csv` |
| Evidence funnel, 14 records (0.22%) | `rq3_evidence_funnel.csv` |
| Sensitivity range 0%–0.31% | `rq3_sensitivity.csv` |
| Effect of removing flagged records | `corpus_noise_robustness.csv` |
| Validation 0.90 / 0.88 | `validation_agreement.csv` |

## Keyword co-occurrence network (Fig. 1)

Fig. 1 was produced in Biblioshiny (bibliometrix) from the full Scopus export of 6,697 records: the 50 most frequent keywords with at least 20 occurrences, Louvain clustering, and node size by PageRank. Because it needs the full keyword metadata, the script does not regenerate it. Instead, `results/fig1_keyword_cooccurrence_nodes.csv` stores the network as Biblioshiny exported it, with cluster, PageRank, betweenness and closeness for each keyword. `figures/fig1_keyword_cooccurrence_network.png` is the exported plot.

The two clusters:

| Cluster (Biblioshiny id) | Keywords | Mean PageRank | Highest PageRank |
|---|---|---|---|
| E-learning, usability and UX (2) | 23 | 0.0233 | e-learning 0.0969, usability 0.0816, user experience 0.0748 |
| VR and educational technology (1) | 27 | 0.0171 | virtual reality 0.0828, education 0.0539, educational technology 0.0388 |

Fig. 2 (topic trends) was also made in Biblioshiny and is not included.

## Citation

If you use these data, please cite the paper above and this dataset:

> [Author names] (2026). *UX Design in Digital Learning Platforms, 2015–2025: Data and Coding Rules* (Version 1.0) [Data set]. Zenodo. [DOI]

## License

Data, coding rules and documents: CC BY 4.0. Script: MIT. See `LICENSE`.

## Contact

[Corresponding author name, affiliation, email]
