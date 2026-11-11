# AGENTS.md

Instructions for coding agents working in this repo (Claude Code, Cursor, Gemini, Copilot…). Do not duplicate the README.

## Project

Kiniela Predictor, Team 2: multiclass classification (6 classes) of the type of result of a football match. The classes are defined once in `src/kiniela/config.py` (`CLASS_NAMES`); never redefine them elsewhere.

Reusable code lives in `src/kiniela/`. Notebooks explore and call that code; they do not hold logic that the app or the tests need.

## Stack

Versions are declared in `requirements.txt` (runtime: app and model) and `requirements-dev.txt` (runtime plus tests and notebooks).

- Python 3.12, pandas, NumPy
- scikit-learn, XGBoost, LightGBM
- matplotlib, seaborn
- Streamlit (app), Docker
- pytest

## Structure

```
app/
├── streamlit_app.py   # entry point and navigation
├── resources.py       # cached model, database engine and teams; UI formatting
└── views/             # pages: predict, history (UI only, logic lives in src/)
src/kiniela/
├── config.py          # classes, N_CLASSES, RANDOM_STATE
├── data/              # loading and target labelling
├── features/          # feature engineering
├── models/            # training and prediction
├── monitoring/        # data drift
└── storage/           # predictions and feedback (SQLAlchemy; DATABASE_URL, see docs/database.md)
notebooks/             # EDA, features, modelling
data/raw/              # source data, not versioned
data/processed/        # modelling dataset, not versioned
models/                # trained artefacts, not versioned
tests/                 # pytest suite
docs/                  # Spanish docs: backlog, dailies, ai-log/
```

## Commands

From the repo root, with the virtualenv active:

- Install: `python -m venv .venv`, then `source .venv/Scripts/activate` (Git Bash) or `.venv\Scripts\Activate.ps1` (PowerShell), then `pip install -r requirements-dev.txt`.
- Tests: `pytest`.
- App: `streamlit run app/streamlit_app.py` → http://localhost:8501.
- Docker: `docker build -t kiniela-predictor .` and `docker run --rm -p 8501:8501 kiniela-predictor`.

## Workflow

One task = one issue = one branch = one PR to `dev`. A human reviews before anything is merged.

1. Read the issue: `gh issue view <number>`. Work only on that issue and its acceptance criteria.
2. Implement on that issue's branch.
3. Open the PR to `dev` with the repository template and the checks green.
4. The human reviews and merges. `main` only receives what is already reviewed in `dev`.

## Principles

- Clean, modular, commented code. DRY: no logic duplicated between notebooks, `src/` and the app.
- If a requirement, rule, or design choice is ambiguous, **stop and ask**. Never decide or invent on your own.

## ML rules

- No data leakage: historical features use only matches played before the one being predicted.
- Use `RANDOM_STATE` from `config.py` for every seed, split, and model.
- Never change the meaning of `target` or the class thresholds without the agreement of the data owner (issue #2).
- The train/validation gap must stay below 0.05 on the declared metric.

## What the agent must not do

- Never commit secrets, `.env`, datasets, or trained models (`data/raw/*`, `data/processed/*`, `models/*`).
- Never merge, and never open a PR without the human review first.
- Never skip, disable, or delete tests to make the suite pass; fix the cause instead. If a rule changes on purpose, update the test in the same PR and explain why.
- Never add dependencies, conventions, or scope that are not in the issue; if something is missing, stop and ask.
- Never rewrite pushed history (`rebase`, `--amend` + `push --force`) on shared branches.
- Never edit another person's AI log file.

## Branches

Branches come from the issue, always off `dev`, with an English slug:

```bash
gh issue develop <number> --base dev --name <number>-<english-slug> --checkout
```

Example: `9-streamlit-app`. Locally, only `git fetch` and `git checkout` for branches someone else created.

## Tasks

Board: https://github.com/orgs/IA-P1-BCN/projects/56

## Pull request to `dev`

Before opening it:

1. Compare the diff with the issue's acceptance criteria and with these rules. Report any gap and ask.
2. Run `pytest`.
3. Add your entry to your own AI log file (see below).

PRs are merged with **Squash and merge**. The PR title becomes the commit on `dev`, so it must follow the commit convention.

## Conventions

- Code, names, comments, `print` texts, branches, commits, and PR titles in **English**.
- Documentation (`docs/`, README) and the board in **Spanish**.
- Commits: [Conventional Commits](https://www.conventionalcommits.org/) with a scope, for example `feat(app): ...`, `fix(data): ...`, `test(models): ...`, `docs: ...`, `refactor: ...`, `chore: ...`.
- The first commits of the repo are in Spanish and stay as they are: the history is not rewritten. The convention applies from this file onwards.
- Dependencies: add them with a minimum version, and only when the issue needs them. `requirements.txt` only if the app needs them to predict, otherwise `requirements-dev.txt`.

## AI assistant setup

Cursor, GitHub Copilot and Codex read this file automatically. Other tools need a personal file at the repo root that points here; these files are in `.gitignore`, so each person keeps their own:

- Claude Code: `CLAUDE.md` with the line `@AGENTS.md`, plus any personal instructions.
- Gemini CLI: `GEMINI.md` with the line `@AGENTS.md`.

## AI log (one file per person)

Each person keeps **their own** AI log in `docs/ai-log/<name>.md` (`anna.md`, `cala.md`, `eva.md`, `mariana.md`). The template and the shared rules are in `docs/ai-log/README.md`.

- Write only in your own file. Never edit somebody else's.
- Add one entry per task or PR, in the same PR as the change.
- One file per person means two PRs never edit the same file, so the log causes no merge conflicts and no entry is overwritten.
