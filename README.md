# Czech Parcel Eval

An LLM prompt and evaluation harness for checking Czech land parcels before a buyout.
The model gets data about one parcel copied from public registries (KN, LPIS, AOPK, flood maps, zoning plans) and returns a structured verdict on whether the parcel can be bought, who could be a potential buyer, and what data is missing to be certain.

## Tech Stack

- **Language:** Python 3.11
- **Model:** Claude (`claude-sonnet-5-5` by default due to speed/lower costs) through the Anthropic API with structured outputs
- **Schemas:** JSON schema for the model output, a JSON template for the input
- **Validation:** `jsonschema` plus custom consistency and evidence checks
- **Data sources:** Inspection of **Katastr Nemovitostí (KN), Mapy.com, LPIS, AOPK, NATURA 2000, flood maps, municipal zoning plans**
- **Tooling:** uv, ruff

## How it works

1. **Input (`input/template.json`):** each parcel is one JSON file with data from public sources and from KN through a logged-in account. Every source in the file says whether it was checked, so the model can tell "nothing was found" from "nobody looked".
2. **Prompt (`prompts/v0.md`):** the model checks the parcel in a fixed order. First whether there is enough data, then whether anything is halting the purchase, then whether someone else must be offered the parcel first, and finally who could be a potential buyer. The full rules are in `docs/decision_table.md`.
3. **Output (`output/schema.json`):** the model returns its decision, the problems it found, the potential buyers, the missing data and a short explanation of its reasoning. Always in the same format.
4. **Run (`run.py`):** sends each test parcel to the model several times and saves the answers in `runs/<prompt>/`.
5. **Evaluation (`evaluate.py`):** checks that each answer is consistent, that it is based on real values from the input, and that it matches the expected answer. The results are saved to `runs/<prompt>/report.md`.

## Decisions and assumptions

- **The model only evaluates the potential of a parcel purchase** - a person still checks all the data about a parcel before anything is bought.
- **An unchecked source is never treated as clean** - if it could change the result, the model has to say that this data is missing.
- **Every conclusion must point to the input** - the model names the field it based each conclusion on, so the evaluation can catch anything it made up.
- **The model does not work with prices** - it decides whether the parcel is worth buying and names how it could be sold later (for example, a road to the municipality, or a field to a farmer). The prices for each option, the fixed costs and the minimum margin are in `config/pricing.yaml` and can be changed without touching the prompt.
- **Things that only lower the price are ignored** - a mortgage or a lease does not change whether the parcel is worth buying, and the person checking it sees them in KN anyway.
- **KN data comes from a logged-in account** - the KN website shows owners only to logged-in users and does not allow automated downloads. Large-scale use would need the paid KN services.
- **Some facts are not in any source** - for example, some rights to buy a parcel first are not written in KN. Facts that only the seller knows are therefore outside of the scope of this agent.

## Quickstart guide

### Prerequisites
- Python 3.11 or newer
- [uv](https://docs.astral.sh/uv/)
- Git
- Anthropic API key

### Setup

```bash
git clone https://github.com/Jpoker01/czech-parcel-eval.git
cd czech-parcel-eval
uv sync
```

Copy `.env.example` to `.env` and add your API key:

```txt
ANTHROPIC_API_KEY=sk-ant-...
```

### Test data

```bash
uv run python tests/build_synthetic_cases.py
```

All cases are roads so far. Fields, forests, co-ownership shares and land under a third-party building still need real parcels.

### Running the evaluation

**Substitute `PROMPT` with the prompt version, e.g. `v0`.**

```bash
uv run python run.py --prompt PROMPT --repeats 3
uv run python evaluate.py --prompt PROMPT
```

The report in `runs/PROMPT/report.md` shows per-case match rates (decision, legal flags, exits, risky missing data), run-to-run consistency and every rule violation. The model can be changed with `--model` or the `PARCEL_EVAL_MODEL` environment variable.

## Project structure

* **run.py** - Runs a prompt version on the test cases
* **evaluate.py** - Scores the runs against the expected outputs
* **/prompts** - Versioned prompts
  * **v0.md** - First version, derived from the decision table
  * **iterations.md** - What changed between versions and why
* **/input**
  * **template.json** - Empty input form, one section per source
  * **/examples** - Filled inputs, one file per test case
* **/output**
  * **schema.json** - Output JSON schema, passed to the API as the structured output format
* **/tests**
  * **/expected** - Hand-written expected outputs
  * **build_synthetic_cases.py** - Generates rule-isolating variants of a real parcel
* **/config**
  * **pricing.yaml** - Exit prices and fixed costs, kept out of the model
* **/src/parcel_eval** - Importable package
  * **llm.py** - API call with the output schema as a structured output format
  * **checks.py** - Schema, consistency and evidence checks
  * **paths.py** - Project paths
* **/docs**
  * **decision_table.md** - Order of steps, signals and codes the prompt is built from
  * **output_schema.md** - Output fields and consistency rules
  * **signal_map.md** - Which source and field each signal comes from
  * **template_reference.md** - Allowed values for the input fields
* **/runs** - Raw model outputs and reports - **not included in git**

## Disclaimer

Not legal advice. Data from Katastr Nemovitostí is informative only, and a current LV extract is needed before any purchase.
