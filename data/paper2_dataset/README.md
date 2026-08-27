---
language:
- ko
license: cc-by-4.0
size_categories:
- 10K<n<100K
task_categories:
- translation
- text-generation
tags:
- braille
- accessibility
- korean
- public-safety
- pharmaceutical
- pesticide
- occupational-safety
- inconvenience-series
configs:
- config_name: drug
  data_files: drug.jsonl
- config_name: pesticide
  data_files: pesticide.jsonl
- config_name: incident
  data_files: incident.jsonl
---

# inconvenience-public-safety

Three Korean public-safety registers converted to Korean braille under the 2017
revised rules (문화체육관광부 고시 제2017-15호), with one config per register.

The registers are here because their documents are shaped differently, not
because three is more than one. A pesticide row is a filled-in form; a patient
leaflet is prose; an accident case is a paragraph an investigator wrote. Median
record length spans more than two orders of magnitude across them.

## Configs

| Config | Register | Records | Cells | Cells per character |
|---|---|---|---|---|
| `drug` | 의약품 허가정보 및 복약정보 (식품의약품안전처) | 3,052 | 3,298,594 | 1.63 |
| `pesticide` | 농약 등록정보 (식품의약품안전처, 식품안전나라) | 3,000 | 880,605 | 1.79 |
| `incident` | 국내재해사례 (한국산업안전보건공단) | 6,362 | 5,424,329 | 1.66 |

## Fields

| Field | Meaning |
|---|---|
| `domain` | `drug`, `pesticide`, or `incident` |
| `record_id` | the register's own identifier |
| `name` | product or case name |
| `sections` | titled blocks **in reading order**, each with its own braille |
| `text` | the whole record as one Korean string |
| `braille` | the whole record in Unicode braille |
| `text_chars`, `braille_cells` | lengths, for embosser planning |
| `meta` | per-domain identifiers kept out of the reading flow |

`sections` is kept alongside `text` because the reading order is the part that
carries judgement. A record has no inherent order — the API returns whatever the
database stores — while a braille reader traverses linearly with no way to skim
back. Collapsing the sections into one string would make that order
unrecoverable.

## What is not here

The source records. All three registers are public APIs and the fetchers in the
repository name the endpoints and parameters, so a reader can collect the same
material with their own key. Redistributing government text this project merely
passed through is neither necessary nor ours to do.

## Known limits

- Round-trip reaches a fixed point for 100.0% of drug records, 100.0% of pesticide records, 99.7% of incident records. The remainder sits where the
  Rule 30 roman terminator shares a cell with the period and the cell stream
  genuinely does not distinguish the readings.
- Composed unit characters (㎡, ℃, ㎥) have no cell and pass through unchanged.
  They round-trip by accident but are not braille.
- Pesticides are a sample of a much larger register; only the accident board is
  complete.

## Source

Built by `scripts/export_paper2_dataset.py` in the KOSHA-Braille repository.
Companion to `Yuyongkim/inconvenience-msds`, which carries the chemical safety
data sheets the encoder was first validated on.
