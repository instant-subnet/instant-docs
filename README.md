# Instant Docs

Official public documentation for [Instant](https://instantsubnet.com).

This repository is a standalone static site. It is built and versioned independently from the
platform, then served seamlessly at `https://docs.instantsubnet.com/` and linked from the website
navigation/footer.

## Repository boundary

This repository owns only public product documentation:

- [Overview](site/index.html) — what Instant does and how an inference request moves;
- [About](site/about/index.html) — the public architecture and responsibility boundaries;
- [Miner guide](site/miners/index.html) — installation, UID/hotkey onboarding, SSH/localhost operations, manual updates, and limitations;
- [Validator guide](site/validators/index.html) — installation, daily operation, scoring, routing, updates, and limitations;
- [Troubleshooting](site/troubleshooting/index.html) — public, non-sensitive recovery checks.

It contains no runtime code, private deployment data, incident evidence, or secret material.

## Publishing contract

`site/` is the complete artifact. Every stylesheet, script, icon, link, and canonical route is
rooted at `/`; it has no runtime dependency on platform-owned assets.

The hosting machine owns only:

- the `docs.instantsubnet.com` Nginx virtual host rooted at `/srv/instant-docs/site`;
- the website's Docs navigation link.

The normal checkout is the live static artifact. The updater follows the established Instant
deployment pattern: every five minutes it runs `git pull --rebase --autostash`, detects a changed
commit, and validates the complete site. The canonical documentation path is
`https://docs.instantsubnet.com/`.

## Local preview

Serve this repository so `site/` is mounted at `/`. No platform checkout or platform assets
are required.

```bash
python -m unittest discover -s tests -v
```

## Production updater

Clone this repository normally at `/srv/instant-docs`, then let PM2 supervise the updater:

```bash
cd /srv/instant-docs
pm2 start config/ecosystem.config.cjs
pm2 save
```

The updater checks `main` every five minutes. To run the same pull-and-validation cycle
immediately:

```bash
cd /srv/instant-docs
python3 scripts/start_docs.py --once
```

Nginx serves `/srv/instant-docs/site` directly. No Docs source is copied into the Platform
checkout or document root.

## Public-content rules

- Never publish credentials, seeds, private keys, wallet files, customer data, prompts, or output.
- Never publish host addresses, private topology, local test endpoints, operator identities,
  incident logs, deployment snapshots, or private operations instructions.
- Validator network and netuid settings must match the operator's intended subnet.
- Describe only released behavior. Mark unavailable work plainly and remove stale claims when the
  implementation changes.
- Test every published command from a clean supported environment.
