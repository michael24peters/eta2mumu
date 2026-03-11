# README

To run, make sure you are in the base directory (`etaMuMu/`) and type: `lb-run DaVinci/v45r8 ipython src/ana.py`. There are three boolean values in `ana.py` that allow you to set the data type (MC vs real), data source (local vs analysis production), and decay type (eta -> mu+ mu- (gamma)).

A `.root` file will be generated in the `ntuples/` directory, which is broken into the `tag`, `prt`, and `mc`. `tag` and `prt` are reconstruction-level events; `mc` contains generator-level events. There are a series of indexes which match reco-level events to gen-level events for the purposes of background analysis.

`plots/` contains scripts to plot values int the ntuple, e.g. `mc_pid`. These plots should be stored in `figs/`.

`src/` contains the scripts used to perform this analysis (fill the ntuple and other accessory operations).

`data/` contains the dec files used to request new MC samples. This is not strictly necessary to run this code and exists as reference material in the event one's decay of interest is not available on DIRAC.

---

## Bidirectional GitHub ↔ CERN GitLab sync

This repository is kept in sync between GitHub and CERN GitLab:

- **GitHub → GitLab**: a GitHub Actions workflow (`.github/workflows/mirror.yml`) mirrors every GitHub push to `gitlab.cern.ch/michael24peters/eta2mumu`.
- **GitLab → GitHub**: a GitLab CI pipeline (`.gitlab-ci.yml`) mirrors every GitLab push back to `github.com/michael24peters/eta2mumu`.

### One-time admin setup

Both sync directions each require a secret token. Follow **both** sections below.

---

#### Part A – GitHub → GitLab (mirror on every GitHub push)

This direction is handled by `.github/workflows/mirror.yml`. It authenticates to CERN GitLab using a CERN GitLab Personal Access Token stored as a GitHub Actions secret.

> **2FA / SSO note:** CERN GitLab accounts are protected by CERN Single Sign-On. When 2FA is active on your account you **cannot** use your CERN password for HTTPS git operations — you must use a Personal Access Token instead. The steps below create that token.

**Step A1 – Create a CERN GitLab Personal Access Token**

1. Log in to [gitlab.cern.ch](https://gitlab.cern.ch) with your CERN credentials.
2. Click your avatar (top-right) → **Edit profile**.
3. In the left sidebar click **Access Tokens**.
4. Click **Add new token**.
5. Fill in the form:
   | Field | Value |
   |---|---|
   | Token name | `github-mirror` (or any descriptive name) |
   | Expiration date | Set a date that suits your workflow (or leave blank for no expiry) |
   | Scopes | ✅ **`write_repository`** (grants push access) |
6. Click **Create personal access token**.
7. **Copy the token value immediately** — GitLab only shows it once.

**Step A2 – Add the CERN GitLab PAT as a GitHub Actions secret**

1. Open the GitHub repository: `https://github.com/michael24peters/eta2mumu`.
2. Click **Settings** → **Secrets and variables** → **Actions**.
3. Click **New repository secret**.
4. Fill in the form:
   | Field | Value |
   |---|---|
   | Name | `GITLAB_TOKEN` |
   | Secret | *(paste the token from Step A1)* |
5. Click **Add secret**.

Once this secret is in place the `mirror` GitHub Actions job will authenticate successfully and push all branches and tags to `gitlab.cern.ch/michael24peters/eta2mumu`.

---

#### Part B – GitLab → GitHub (mirror on every GitLab push)

This direction is handled by `.gitlab-ci.yml`. It authenticates to GitHub using a GitHub Personal Access Token stored as a GitLab CI/CD variable.

**Step B1 – Create a GitHub Personal Access Token**

1. Log in to [github.com](https://github.com).
2. Click your avatar → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**.
3. Click **Generate new token (classic)**.
4. Give it a descriptive name (e.g. `gitlab-to-github-mirror`).
5. Set an expiration that suits your workflow (or "No expiration").
6. Under **Select scopes**, tick **`repo`** (full control of private repositories).
7. Click **Generate token** and **copy the token value** – you will not be able to see it again.

**Step B2 – Add the GitHub PAT as a CI/CD variable on CERN GitLab**

1. Open the CERN GitLab project page: `https://gitlab.cern.ch/michael24peters/eta2mumu`.
2. In the left sidebar go to **Settings** → **CI/CD**.
3. Expand the **Variables** section and click **Add variable**.
4. Fill in the form:
   | Field | Value |
   |---|---|
   | Key | `GITHUB_PAT` |
   | Value | *(paste the PAT from Step B1)* |
   | Type | Variable |
   | Environment scope | `All` |
   | Flags | ✅ **Mask variable** · ✅ **Protect variable** |
5. Click **Add variable**.

**Step B3 – Enable GitLab CI/CD pipelines (if not already on)**

1. In the left sidebar go to **Settings** → **General**.
2. Expand **Visibility, project features, permissions**.
3. Make sure **Pipelines** is toggled **on**.
4. Click **Save changes**.

The `.gitlab-ci.yml` file already exists in the repository and will be picked up automatically once CI/CD is enabled.

---

### Developer workflow (clone from GitLab, develop, push back)

Once the one-time admin setup above is complete, any collaborator with access to the CERN GitLab project can use the following workflow:

```bash
# 1. Clone from CERN GitLab (use your CERN username / SSH key as normal)
git clone https://gitlab.cern.ch/michael24peters/eta2mumu.git
cd eta2mumu

# 2. Create a feature branch (recommended)
git checkout -b my-feature

# 3. Make your changes, then commit
git add .
git commit -m "Describe your changes"

# 4. Push to CERN GitLab
git push origin my-feature
```

After the push, a GitLab CI pipeline named **`mirror-to-github`** runs automatically (visible under **CI/CD → Pipelines** on the GitLab project page). When it succeeds, the changes are reflected on GitHub.

> **Loop prevention:** when GitHub Actions mirrors to GitLab it passes `-o ci.skip`, so GitLab will not start a new pipeline for that push — preventing an infinite mirror loop.
