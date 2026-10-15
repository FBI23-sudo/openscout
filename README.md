# OpenScout

OpenScout is a small, beginner-friendly Python command-line tool that checks a username against a curated list of public profile URLs and saves results in JSON and CSV.

> **Important limitation:** an HTTP response is not proof that an account exists, is active, or belongs to a particular person. A `200` may be a generic page, login page, or anti-bot page. Review results manually.

## Features

- Curated allowlist of public profile URL templates
- JSON and CSV reports
- Request timeout and minimum delay between sites
- Username validation to prevent malformed URL input
- Conservative result labels for HTTP responses
- Unit tests and GitHub Actions workflow
- No API keys required for the initial version

## Requirements

- Python 3.10 or newer
- Internet access
- Respect each site's terms, robots guidance, and rate limits

## Installation

```bash
git clone https://github.com/YOUR-GITHUB-USERNAME/openscout.git
cd openscout

python -m venv .venv
```

Activate the environment:

**Windows PowerShell**
```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux**
```bash
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Usage

Check all configured sites:

```bash
python -m openscout.cli example_username
```

Check only GitHub and GitLab:

```bash
python -m openscout.cli example_username --platforms github gitlab
```

Change output directory and request spacing:

```bash
python -m openscout.cli example_username --output-dir reports --delay 2 --timeout 8
```

The program writes timestamped `.json` and `.csv` files into `reports/`.

## Result labels

| Label | Meaning |
| --- | --- |
| `http_200_review_needed` | Server returned 200; manually review the page |
| `http_404_not_found` | Server returned 404; not definitive on every platform |
| `blocked_or_rate_limited` | Server returned 401, 403, or 429 |
| `redirect` | Redirect response category |
| `http_response` | Other HTTP response |
| `error` | Timeout or request failure |

## Add or remove a platform

Edit `DEFAULT_PLATFORMS` in `openscout/profiles.py`. Use only public profile URL patterns that are permitted by the platform. Keep the list curated; do not accept arbitrary target URLs from command-line input.

## Run tests

```bash
python -m unittest discover -s tests -v
```

## Privacy and responsible use

- Use this tool only for legitimate, lawful research and public-interest purposes.
- Do not use results to harass, stalk, dox, discriminate against, or target people.
- Do not attempt authentication, CAPTCHA bypass, access controls, or private content.
- Do not scrape at high volume. The default delay is 1.5 seconds between sites; increase it when a service asks you to slow down.
- Sites can prohibit automated access even when pages are publicly viewable. Check and follow each site's terms and applicable laws.
- The tool only records the username supplied and the public profile URL/HTTP response metadata; inspect reports before sharing them.
- Reports may still contain personal data in the username or URLs. Keep them local unless you have a lawful reason to publish them.
- Never commit API tokens, credentials, private datasets, or reports containing personal data.
- Use an honest User-Agent and replace the example repository URL with your actual project URL before publishing.

## GitHub setup

1. Create a new empty GitHub repository named `openscout`.
2. Do not add a README on GitHub if you already have this one locally.
3. Replace `YOUR-GITHUB-USERNAME` in this README with your GitHub username.
4. Initialize and push:

```bash
git init
git add .
git commit -m "Initial OpenScout implementation"
git branch -M main
git remote add origin https://github.com/YOUR-GITHUB-USERNAME/openscout.git
git push -u origin main
```

5. Check the **Actions** tab to confirm tests run successfully.
6. Consider adding a license (MIT is a permissive option) after reviewing what open-source license suits your goals.

## Scope

OpenScout is a simple URL-response checker, not a people-search engine, identity verification system, or guarantee that a username is unique across services.
