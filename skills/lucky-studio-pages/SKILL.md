---
name: lucky-studio-pages
description: Maintain the shared Lucky Studio GitHub Pages repository for public app pages, support, privacy, terms, and migration of existing app websites under the lucky folder. Use for app website URLs and shared Pages publishing, not game code or OTA releases.
---

# Lucky Studio Pages

Use `/Users/fkr.onsiter/lucky/lucky-studio-pages` and GitHub `vnluckystudio/lucky-studio-pages` for public pages of all Lucky Studio apps. Read [the guide](../../GUIDE.md) before editing or publishing. Read `/Users/fkr.onsiter/lucky/AGENTS.md` and applicable app instructions as well.

- Edit `content/apps.json`, then run `python3 scripts/build.py` and `python3 scripts/build.py --check` from the repo. Stage both source changes and generated `docs/` files. Only `docs/` is served.
- Use immutable IDs, preferably lowercase bundle IDs, under `apps/<id>/`, with `support/`, optional `privacy/` and `terms/`. Preserve existing routes and reviewed policy content. The intended base URL is `https://vnluckystudio.github.io/lucky-studio-pages/`; verify deployment before giving it as a live URL.
- Owner/seller is exactly `Lucky Studio`; phone is exactly `+821083312512`. Verify per-app data practices before writing privacy text. Do not invent missing required filing details or bulk publish internal app names.
- Keep old legal repos and Sites hosting intact until a requested migration has live, verified replacement pages. Creating this shared repo does not migrate existing apps or authorize store metadata changes.
- GitHub Pages deployment always runs Actions, including branch-based deployment. Without an explicit user request to run Actions, do not enable Pages, request a Pages build, dispatch/rerun workflows, or push changes that would trigger a run. Finish local work and report what remains. An ordinary website build/update request alone does not authorize Actions.
- When publishing is authorized with Actions, use `main` → `/docs`, verify deployment and HTTP content, and report actual URLs. Keep commits and pushes within the task's scope; do not change OTA or app code.

The skill source lives in this repo; the machine-wide installation is a symlink at `~/.codex/skills/lucky-studio-pages`. Keep a single maintained copy. The guide at the root of `lucky` and the shared AGENTS.md route future app tasks here.
