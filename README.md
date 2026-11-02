# czech-parcel-triage

LLM triage of Czech land parcels for buyout decisions. The model gets data about one parcel copied from public registries (cadastre, LPIS, AOPK, flood maps, zoning plans) and returns a structured verdict: can the parcel be bought, who would buy it afterwards and what is missing to be sure.

NOTE: This is a work in progress. Prompt v0, the eval harness and a first test set are in place; no evaluation results yet.

## WHAT IT DOES

- One parcel in, one JSON verdict out: `BLOCKED`, `CONDITIONAL`, `BUY_CANDIDATE`, `NOT_WORTH_IT` or `INSUFFICIENT_DATA`.
- The verdict is triage for a human, not a final decision. Every `BUY_CANDIDATE` and `CONDITIONAL` still goes to a person who opens the LV.
- The model never outputs a price. It names the exit (`road_class_3`, `field_arable`, `building_owner` etc.) and the price is looked up in `config/pricing.yaml`.

## DESIGN DECISIONS

**Unchecked is not the same as empty**

- Every source in the input has `status`: `checked`, `not_checked` or `not_available`.
- An empty list in a checked source means "verified, nothing there". A `not_checked` source means nothing, and the model has to report it in `missing_data` instead of assuming the favourable value.

**Every conclusion carries evidence**

- Each flag and exit includes `evidence` in the form `input.path = value`, e.g. `cadastre.owners[0].name = Liberecký kraj`.
- The eval resolves the path in the input and compares the value, so an invented restriction or buyer is caught automatically.

**Fixed order of evaluation**

1. Basic cadastre data missing - `INSUFFICIENT_DATA`.
2. Seal, execution, insolvency, alienation ban etc. - `BLOCKED`.
3. Pre-emption right or authority consent (§ 61 of 114/1992 Sb., § 3056 NOZ, § 1124 NOZ etc.) - caps the result at `CONDITIONAL`.
4. Find exits (who buys), then kill the ones that do not survive (owner is already the buyer, clear-cut forest, no LPIS user etc.).
5. Risky missing data or an unconfirmed buyer - `CONDITIONAL`, otherwise `BUY_CANDIDATE`.

The full table is in `docs/decision_table.md`.

## REPOSITORY LAYOUT

```txt
prompts/                 versioned prompts (v0.md) and iteration notes
input/template.json      empty input form, one section per source
input/examples/          filled inputs, one file per test case
output/schema.json       output JSON schema, used as forced tool input
tests/expected/          hand-written expected outputs
tests/build_synthetic_cases.py   generates rule-isolating variants from a real parcel
config/pricing.yaml      exit prices and fixed costs, kept out of the model
src/parcel_eval/         API call, schema/consistency/evidence checks
docs/                    decision table, signal map, field reference
run.py                   runs a prompt version on the test cases
evaluate.py              scores runs against expected outputs
```

## USAGE

```txt
pip install -e .
export ANTHROPIC_API_KEY=...
python run.py --prompt v0 --repeats 3
python evaluate.py --prompt v0
```

- `run.py` calls the model with `temperature=0` and forces the output through a tool whose input schema is `output/schema.json`.
- `evaluate.py` writes `runs/<prompt>/report.md` with per-case match rates (decision, legal flags, exits, risky missing data), run-to-run consistency and every rule violation.
- The default model is `claude-sonnet-5-5`, override with `--model` or `PARCEL_TRIAGE_MODEL`.

## TEST SET

- `zalesni_lhota_1292-2` is a real parcel (land under a road already owned by Liberecký kraj), copied from Nahlížení do KN on 2026-11-02.
- `syn_*` cases are generated from it and each one isolates a single rule (seal, execution, national park, prompt injection in `notes`, unchecked sources etc.).
- All cases are roads so far. Fields, forests, co-ownership shares and land under a third-party building need real parcels.

## KNOWN LIMITATIONS

- Input is copied by hand. Nahlížení do KN shows owners only after login and forbids automated scraping; bulk use would need the paid cadastre web services (WSDP) and WMS/WFS layers for LPIS, AOPK and flood maps.
- Restriction types on the LV are free text matched by substring rules in the prompt, so an unusual wording can slip through.
- Statutory pre-emption rights (§ 3056, § 1124 NOZ, § 61 of 114/1992 Sb.) are not always visible in the cadastre and partly depend on facts from the seller (`seller_facts`).
- Consent with public use of a road (Constitutional Court I. ÚS 2541/25) cannot be detected from any of the sources.
- Prices in `config/pricing.yaml` are public reference points (2026 state subsidy caps for road buyouts, Farmy.cz 2025 farmland averages) and rough guesses for costs, not a valuation model.

## DISCLAIMER

Not legal advice. Data from Nahlížení do KN is informative only; a current LV extract is needed before any purchase.
