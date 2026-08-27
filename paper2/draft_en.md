# One Encoder, Three Registers: Extending Korean Braille Infrastructure across Public-Safety Catalogues, and What Only a Narrative Domain Reveals

Yuyong Kim
University of Wisconsin-Madison, Madison, WI 53706, USA
Email: ykim288@wisc.edu
ORCID: 0009-0006-4842-666X

---

## Abstract

**Purpose.** Earlier work released 48,966 chemical safety data sheets converted to Korean braille under the 2017 revised rules [1]. Whether that was an achievement about one catalogue or an infrastructure that serves other public-safety documents is a question that paper could not answer. This study answers it by applying the same encoder to three national registers whose documents are shaped differently.

**Methods.** The encoder is left untouched; each register gets a thin adapter whose only job is to decide reading order. The registers are pharmaceutical approvals and patient leaflets (MFDS), pesticide registrations (Korea Food Safety portal), and domestic industrial accident cases (KOSHA). The first two are records with named fields; the third is free prose written by an investigator. Expansion ratio, round-trip accuracy, and 2017 rule compliance are measured per domain. Round-trip is reported three ways: exact match against the source, a near match folding case and whitespace, and **fixed-point stability** — whether a second round trip changes anything.

**Results.** 10,887 records were collected and encoded across the three registers. Median record length spans more than two orders of magnitude, from 154 to 539 characters, while cells per source character stay between 1.64 and 1.78. Rule violations were zero in all three domains. Exact match diverged sharply — 9.5% for pesticides, 44.0% for drugs, 43.6% for incidents — while stability was 100%, 100%, and 99.8%. That gap is itself the result: what exact match counts as failure is transformation the rules require, chiefly the space 제38항 [다만] mandates between a digit and an initial that shares its cell, which appears in almost every pesticide row. **The narrative domain surfaced two defects the record domains never would.** A decoder that misread the roman terminator as a period and turned the Korean after it back into roman, and an encoder that silently dropped subscript digits, rendering H₂S as "H S".

**Conclusions.** One encoder does serve catalogues of differing shape, and the cost of a new domain is one adapter. But that claim only holds if it is tested against material that is genuinely shaped differently. Had the measurement stopped at the two record domains, neither defect would have appeared and the encoder would have looked sturdier than it is. Extensibility of accessibility infrastructure should be judged not by whether a new domain can be attached, but by what attaching it reveals.

**Keywords:** Korean braille; accessibility infrastructure; open government data; domain adapters; occupational safety; medication information; round-trip validation

---

## 1. Introduction

Information access is infrastructure, not a service. Like tactile paving, platform screen doors, and captioning, its justification is not settled by counting who uses it. No transit authority decides whether to install platform doors by first measuring the share of blind passengers.

Earlier work [1] took that view and released 48,966 safety data sheets in Korean braille. Section VIII of that paper listed pharmaceutical labels and first-aid protocols as **prospective** extensions. Prospective is not validated. An encoder that works on one catalogue is not thereby known to work on another, particularly when the other catalogue's documents are shaped differently.

The question here is narrow. **What happens when the same encoder is applied to three national registers whose documents are shaped differently?**

The narrowness is deliberate. A claim of extensibility is not supported merely by attaching a new domain. If the three catalogues turn out to be the same document with different field names, then covering all three with one encoder says nothing. So this paper first establishes that the shapes really do differ (§6, Fig. 3), and only then reports the result.

The three domains were chosen along distinct axes of access. Pharmaceuticals concern citizen self-medication; pesticides concern rural populations where the prevalence of visual impairment is highest; incident cases concern occupational safety training. The last closes a loop with the earlier work: if a safety data sheet describes what a substance can do, an accident case records what it did, and joining them through one braille system yields prevention material.

The contributions are four:

1. A common-encoder plus domain-adapter structure, with the cost of adding a domain measured
2. A braille dataset of 10,887 records across three public-safety registers
3. Per-shape validation, and the reason round-trip accuracy must be read three ways
4. Two encoder and decoder defects surfaced by narrative material, and their repair

## 2. Related Work

Automatic braille conversion has been treated as a character-level mapping problem [1,2]. For Korean, the 2017 revised rules [3] are the normative standard, and a tool that checks compliance automatically was released with the earlier work [1].

Literature on accessibility and open government data concentrates on the accessibility of web interfaces (WCAG conformance); delivering the data itself in braille is not addressed. Reconstructing regulatory catalogues as braille material appears to have only one prior instance [1].

The legal grounding is UN CRPD Article 9 (accessibility) and Article 21 of the Korean Anti-Discrimination Against and Remedies for Persons with Disabilities Act. Neither conditions the obligation on the size of the demand.

## 3. Three Registers

### 3.1 Sources and units

**Table 1. The three catalogues**

| | Pharmaceutical | Pesticide | Industrial accident |
|---|---|---|---|
| Authority | MFDS | MFDS | KOSHA |
| Portal | data.go.kr | Korea Food Safety | data.go.kr |
| Service | DrugPrdtPrmsnInfoService07 + DrbEasyDrugInfoService | I1910 | disaster_api02 |
| Record unit | one product | one approved **use** | one case |
| Document shape | prose (patient-facing) | table (crop × pest) | narrative (investigator) |
| Register size | — | 95,912 | 6,362 |
| Collected | 1,525 | 3,000 | 6,362 (all) |

The differing record unit matters. The pesticide register stores one row per approved *use*, not per product: the same pesticide appears once for apples and aphids, again for pears and mites, each with its own dilution and application window. That is the right shape for a database and the wrong shape for a label, because a grower holding a bottle wants the one row that matches the crop in front of them.

The incident board was collected in full: 6,362 cases, of which 4,191 are construction, 1,448 manufacturing, 378 shipbuilding, and 345 services.

### 3.2 Why this third domain is necessary

Pharmaceuticals and pesticides are both **records**. Somebody filled in fields, and an adapter for either is mostly a decision about which field to read first. Reporting that a single encoder covers "differently shaped catalogues" on the strength of those two invites the obvious objection that the shapes are not that different.

Accident cases are not records. The `contents` field is a paragraph an investigator wrote:

> 2026. 2. 27.(금) 20:57 경북 울진군 조명시설 설치 현장에서 차량탑재형 고소작업대에 탑승하여 조명기구 조정 작업 후 작업자를 지면으로 내려주기 위해 붐을 선회 및 하강하던 중 아웃트리거를 펼치지 않은 쪽으로 장비가 전도되어 작업대에 탑승하고 있던 작업자들이 떨어짐

A date, a time, and measurements sit mid-sentence, and clause follows clause with no field boundary to lean on. This is where the 2017 rules actually bite. Records let an encoder off lightly: field values are short, punctuation is scarce, and the boundaries do the work that grammar would.

### 3.3 Two access findings worth recording

Every direct call to data.go.kr failed with `SERVICE_KEY_IS_NOT_REGISTERED_ERROR` for an extended period. The message names the key, so it reads as an authorisation problem. The actual cause was that the key in `.env` was stored quoted and split across two lines, and a parser reading one line at a time and splitting on the first `=` handed the portal a value that opened with a quote and was missing its tail.

That misdiagnosis produced a wrong remedy: routing the fetcher through a separate service that already held the same key. That service runs on the same machine and therefore leaves from the same address, so the hypothesis that "the portal is blocking this host" could never have been true. The detour was avoidance rather than diagnosis, and it incidentally loaded a service with live users.

The incident endpoint held one more obstacle. The dataset page lists `callApiId` as a "mandatory fixed value" without giving the value. The value `1060` appears only in the activity guide attached to that page. Guessing from the parameter list yields nothing but repeated `APICODE_ERROR`.

Both bear directly on the reproducibility of accessibility work built on open government data, and are recorded so that a later researcher does not spend the same hours in the same place.

## 4. Common Encoder, Domain Adapters

### 4.1 Structure

The encoder is the earlier work's `pipeline.ko_braille`, unmodified. An adapter knows one register's field names and reading order and produces plain Korean text; the encoder does not know which catalogue that text came from (Fig. 1).

The judgement in this split sits in the adapter's **reading order**. A record has no inherent order — the API returns whatever the database stores — while a braille reader traverses linearly with no way to skim back. So each adapter fixes an order and records why.

### 4.2 The cost of a domain

**Table 2. What adding one domain requires**

| Component | Nature | Size |
|---|---|---|
| Fetcher | per domain | 100–150 lines |
| Adapter | per domain | 60–110 lines |
| Encoder | shared, unmodified | — |
| Rule checker | shared, unmodified | — |
| Validation | shared, 3 lines added | — |

## 5. Reading Order, Domain by Domain

### 5.1 Pharmaceutical

Active ingredient → prescription/OTC → therapeutic class → manufacturer → indications → dosage → warnings → precautions → interactions → adverse effects → storage.

Warnings precede adverse effects deliberately. A warning states the conditions under which this drug must not be taken; an adverse effect states what may follow having taken it. Reversing the order puts the information that decides whether to take the drug after the information that only matters once it has been taken.

### 5.2 Pesticide

Brand and formulation → purpose → crop → pest or weed → application method → application window → dilution → quantity → frequency → toxicity → registration status.

Placing toxicity last runs against the usual safety convention of leading with the warning. A row existing in the register already implies approval for this crop; what actually decides whether the substance is used safely is the dilution and the frequency, and those numbers are useless if the reader has stopped listening. The toxicity grade is short, so it lands better as a closing statement than as an opening one the reader must hold through four fields of numbers.

Company name and address are dropped. They fill a third of the record and answer a question nobody asks while spraying.

### 5.3 Industrial accident

Sector → summary → narrative.

The board's title precedes the paragraph. The title is one line — "외벽 도장 작업 중 추락" (fall during exterior wall painting) — and a braille reader cannot skim ahead. A reader deciding whether this is the case they want should not have to sit through a paragraph to find out. The paragraph then repeats what the title said; that redundancy is a cost worth paying in print and worth more in braille.

The attachment count is dropped. It is a number about the web page, not about the accident, and a reader holding an embossed page cannot open an attachment.

### 5.4 What the three adapters share

Two issues arise in every domain and so live in the shared layer rather than in one adapter.

**The space after a comma.** A comma and the initial ㄹ are the same cell (⠐). Print gets away with "현장에서,달비계에" because the eye sees the comma sitting low; braille cannot, and the decoder reads a stray ㄹ. The two are genuinely indistinguishable in the cell stream. Written Korean would have used a space anyway — its absence is an artefact of typing into a database field.

**Subscript and superscript digits.** They have no cell (§7.2).

## 6. Dataset and Document Shape

### 6.1 Scale

**Table 3. Dataset statistics** (800-record sample per domain, drawn at an even stride through the corpus)

| Domain | Records | Source chars | Braille cells | Ratio | Median record |
|---|---|---|---|---|---|
| Pharmaceutical | 1,525 | 532,120 | 874,549 | 1.64 | 539 chars |
| Pesticide | 3,000 | 125,037 | 223,092 | 1.78 | 154 chars |
| Industrial accident | 6,362 | 407,522 | 676,126 | 1.66 | 200 chars |

Sampling at an even stride rather than taking the first 800 is not a methodological detail; it changes the numbers. All three corpora arrive ordered, and the order correlates with length. The first 800 records of the incident board average 128 characters against the corpus's 514, because the most recent postings are the shortest. Taking the head reports the sampling rather than the domain.

### 6.2 The shapes differ; the cost does not

Figure 3 carries both the paper's premise and its result. Median record length runs from 154 to 539 characters, and the distributions span more than two orders of magnitude. The pesticide distribution is narrow and sharp: one approved use has fixed fields, so its length barely varies. The incident distribution is the widest, because some cases are a single sentence and some are a full report with a numbered preamble.

Cells per source character, meanwhile, stay between 1.64 and 1.78. **The shapes differ; the cost of embossing them barely does.**

The pesticide ratio is highest (1.78) because of digit density. Dilution, quantity, and frequency crowd into one row, and Korean braille prefixes numbers with the number indicator (⠼), which costs an extra cell.

## 7. Validation

### 7.1 Why round-trip is read three ways

**Table 4. Per-domain validation** (800 records each)

| Domain | Exact | Near | Stable | Rule violations |
|---|---|---|---|---|
| Pharmaceutical | 44.0% | 44.0% | **100.0%** | 0 |
| Pesticide | 9.5% | 9.5% | **100.0%** | 0 |
| Industrial accident | 43.6% | 43.6% | **99.8%** | 0 |

Read by exact match alone, the pesticide domain scores 9.5% and looks broken. It is not. 제38항 [다만] of the 2017 rules requires a space where a digit is followed by an initial that shares its cell. Almost every pesticide row carries a frequency like "3회", which must be embossed as "3 회", and no decoder can put that space back. The score is measuring the writing system, not the pipeline.

**Stability** answers the correctness question. Encode, decode, encode, decode again: if the second pass equals the first, the transformation has reached a fixed point and nothing further is being lost. A pipeline that inserts a rule-mandated space scores 100% here; one that drops or corrupts a character does not, because the damage compounds on the second pass.

The gap in Fig. 2 is the result. All of it is deterministic transformation the rules impose — otherwise it would widen on the second pass.

### 7.2 What the narrative domain found

Before the incident domain was added, both existing domains scored 100% stable. The incident domain scored 99.5%, and the difference was two real defects.

**Table 5. Defects surfaced by narrative material**

| Defect | Symptom | Cause | Reachable from record data? |
|---|---|---|---|
| Roman terminator misread | `Bracket에 길이=8m` → `Bracket.n 길이=8m` | strictness meant for one word carried into the next | No |
| Subscript loss | `H₂S` → `H S` | number indicator emitted, digit discarded | Almost never |

**The roman terminator.** The 제30항 terminator (⠲) shares its cell with the period and with the final ㅍ. The decoder decides between those readings by looking ahead, and that decision was being applied past the word boundary. If an opening bracket or an unencodable character (`=`) appeared two words later, the earlier terminator reading was overturned and the Korean that followed reverted to roman. Reaching a space already means the word ended cleanly, so there is no reason to carry the strictness forward. After the repair, stability over the full 6,362-case corpus is 99.686% (20 not reaching a fixed point).

The reason this never surfaced in record data is plain: roman followed by Korean, with a bracket or an equals sign within two words, is a layout that occurs in free prose.

**Subscripts.** The encoder emitted the number indicator and then discarded subscript and superscript digits, so `H₂S` became "H S". That is silent loss in the one place these catalogues cannot afford it, since the digit is what distinguishes hydrogen sulfide from hydrogen. Braille has no raised or lowered position, so the digit is written on the line — `H2S` — which is how a chemist reads the formula aloud anyway. Script digits occur 65 times across the three corpora.

### 7.3 Rule compliance

Zero violations in all three domains, checked by the earlier work's `eval.rule_checker` across five rules. A document can round-trip perfectly and still be malformed braille, so this is measured separately.

## 8. Discussion

### 8.1 What extensibility should be judged by

This paper shows two things, and the second matters more.

First, one encoder serves three catalogues of differing shape. The cost of a domain is one adapter, and the encoder was not touched.

Second, **that claim only holds if it is tested against material that is genuinely shaped differently.** Had measurement stopped at the two record domains, stability would have read 100% and 100%, and the encoder would have looked sturdier than it is. One narrative domain surfaced two defects. Extensibility of accessibility infrastructure should be judged not by whether a new domain can be attached but by what attaching it reveals.

The same applies to the extension candidates listed in Section VIII of the earlier work. Promoting that list from prospective to validated is not accomplished by shipping catalogues; the list must include a catalogue whose shape differs.

### 8.2 Secondary readers

These three domains do not serve blind readers alone. Incident cases released in braille and in structured form are usable by legislative staff, labour inspectors, occupational-safety lawyers, journalists, and civil-society organisations. The same holds for medication information and pesticide application guidance.

This bears on the standard objection to accessibility work — that demand is small. The observation that there are few blind chemists is a self-fulfilling prophecy: without accessible information, entry is foreclosed; with no entrants, the information is never produced. The measure of justification is not adoption volume but **parity of access**.

### 8.3 What the structure can take next

The adapter pattern separates domain knowledge from braille rules. Food allergens, cosmetic ingredients, K-REACH registered substances, and statutory text all attach the same way. What is needed is the field names of the register and a judgement about reading order.

That reading order is the part which does not automate is worth stating plainly. Which field to read first is a judgement about who hears the document and under what circumstances, and it does not follow from the data.

## 9. Limitations

**Sampling.** Pesticides are 3,000 of 95,912 rows: enough for a rate and a distribution, not a mirror of the register. The pharmaceutical register offers no listing call, only substring search on the product name, so the sweep walks dosage-form words; products whose names lack those words never enter the sample. Only the incident board is complete.

**The 20 unstable cases.** The 20 incident cases (0.31%) that do not reach a fixed point sit where roman and Korean interlock and the cell stream genuinely does not distinguish the readings. This follows from the 제30항 terminator sharing a cell with the period, and is a property of the notation.

**Unit characters.** Composed characters such as ㎡, ℃, and ㎥ have no cell and pass through unchanged. They round-trip by accident but are not braille. Unlike subscripts, the right treatment is to spell them out in Korean, which is left to a later revision.

**No user validation.** Only formal correctness of the output is measured. Whether the fixed reading orders are useful to actual braille readers is not. In particular, the pesticide adapter's decision to place toxicity last is a reasoned judgement, not a validated result.

## 10. Conclusion

10,887 records were collected from three national registers — pharmaceutical, pesticide, and industrial accident — and encoded under the 2017 revised Korean braille rules. The earlier work's encoder was not modified; each register received one adapter that fixes reading order. Rule violations were zero, and stability was 100%, 100%, and 99.8%.

Document length spans more than two orders of magnitude while cells per character stay between 1.64 and 1.78. The shapes differ; the cost of embossing them barely does.

What this paper means to leave behind, though, is the method rather than those figures. Until material of a different shape is actually put through it, an encoder does not reveal what it cannot handle. One narrative domain surfaced two defects, and one of them had been silently erasing digits from chemical formulae.

## Reproduction

Code and dataset are in the public repository.

```
python scripts/paper2_fetch_drugs.py
python scripts/paper2_fetch_pesticides.py
python scripts/paper2_fetch_incidents.py
python eval/paper2_validation.py
```

API keys are not included in the repository and are read from `.env`. `scripts/keys.py` handles quoting and line breaks and decodes data.go.kr's encoded form.

Collected source text is not redistributed; only the braille output, statistics, and conversion code are released.

## References

[1] Kim, Y. (2026). KOSHA-Braille: A Korean braille dataset for chemical safety information. *Universal Access in the Information Society*, 25:116.

[2] Ministry of Culture, Sports and Tourism (2017). Korean Braille Rules (Notification 2017-15).

[3] United Nations (2006). Convention on the Rights of Persons with Disabilities, Article 9.

[4] Act on the Prohibition of Discrimination Against Persons with Disabilities, Article 21 (Republic of Korea).

## Figures

**Fig. 1.** Where the reuse is and where it is not. Above the divider is written per domain; below it is taken unchanged from the earlier work. (`paper2/figures/Fig1.png`)

**Fig. 2.** The gap between two readings of the round trip. The light bar is exact match against the source; the dark bar is fixed-point stability. What lies between them is transformation the rules impose. (`paper2/figures/Fig2.png`)

**Fig. 3.** Left, record length distribution on a log scale; right, cells per source character. Length spans more than two orders of magnitude; the cost of embossing barely moves. (`paper2/figures/Fig3.png`)
