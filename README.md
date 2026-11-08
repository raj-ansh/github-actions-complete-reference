# GitHub Actions: The Complete Reference — companion code

This repository holds the working code for the book *GitHub Actions: The
Complete Reference* by Rajkumar Panda. Every workflow, script and test the book
builds on lives here, so you can read it, run it and copy it into your own
projects.

## What is here

| Path | What it is | Chapters |
| --- | --- | --- |
| `src/`, `tests/`, `pyproject.toml` | **ShelfWise**, a small inventory API for independent bookshops (Python 3.14, FastAPI, SQLite) | 6–7, 16 |
| `.github/workflows/ci.yml` | Lint, type-check, test and package on every push and pull request | 6, 16 |
| `.github/workflows/security.yml` | CodeQL, dependency review, Trivy scans | 8–9, 16 |
| `.github/workflows/release.yml` | Multi-platform image build, provenance attestation, staged deploys | 10–11, 16 |
| `.github/workflows/deploy-environment.yml` | Reusable deploy workflow with OIDC and environments | 11, 13 |
| `.github/workflows/infrastructure.yml` | OpenTofu plan and apply | 15 |
| `.github/workflows/load-test.yml` | k6 smoke test against staging | 7 |
| `.github/actions/setup-python-env/` | Composite action shared by the workflows | 13 |
| `Dockerfile`, `deploy/`, `infra/`, `loadtest/` | Container image, Kubernetes manifest, OpenTofu, k6 script | 7, 10–11, 15 |
| `scripts/pipeline_stats.py` | Pipeline metrics from the GitHub API | 20 |
| `check-changelog-action/` | The JavaScript action built in Chapter 19 | 19 |
| `.github/workflows/action-ci.yml` | Chapter 19's "Action CI", adapted to the action's subfolder | 19 |

## Run it locally

```bash
python3.14 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest --cov
SHELFWISE_API_KEY=local-dev-key uvicorn shelfwise.main:app --reload
```

For the action:

```bash
cd check-changelog-action
npm ci
npm test
```

## Use it in your own repository

Fork the repository or copy the files you need. The CI and Security workflows
run without any setup. The others need accounts and settings described in the
book:

- **Release and deploy** need GitHub environments (`staging`, `production`) and
  an AWS role for OIDC (Chapters 11–12).
- **Infrastructure** needs an AWS role and an S3 state bucket. Replace the
  `your-org-...` bucket names in `infra/main.tf` (Chapter 15). Until then this
  workflow cannot plan or apply.
- **CODEOWNERS** uses the placeholder team `@your-org/platform`. Replace it
  with your own team.

Workflows pin every third-party action to a full commit SHA, with the version
in a comment, as Chapter 9 recommends. Dependabot keeps those pins current.

## Differences from the printed listings

Book listings show major version tags such as `actions/checkout@v7` so they are
easy to read. The files here pin full SHAs instead. Where code changed after the
book went to print, this repository is the more current version.

## License

The code is released under the MIT License. See [LICENSE](LICENSE). The book's
text is not covered by this license.
