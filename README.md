# Instant Docs

Official public documentation for [Instant](https://instantsubnet.com).

This repository is a standalone static site. It is built and versioned independently from the
platform, then served seamlessly at `https://instantsubnet.com/docs/` and linked from the website
navigation/footer.

## Repository boundary

This repository owns only public product documentation:

- [Overview](site/index.html) — what Instant does and how an inference request moves;
- [About](site/about/index.html) — the public architecture and responsibility boundaries;
- [Miner guide](site/miners/index.html) — installation, UID/hotkey onboarding, and limitations;
- [Validator guide](site/validators/index.html) — PM2 setup, production burn, shadow scoring, and gated direct weights;
- [Troubleshooting](site/troubleshooting/index.html) — public, non-sensitive recovery checks.

It contains no platform runtime, UI application source, miner or validator service, H200 verifier,
chain infrastructure, internal launch plan, incident evidence, or private operations material.

## Phase status

Phase 0 makes the docs artifact standalone and fixes repository ownership. The existing guide
content remains a preview until Phase 5, when every page and command will be revised against the
implemented Finney/46 miner, verifier, platform, and validator workflows. Do not publish the Phase
0 branch as launch documentation.

## Publishing contract

`site/` is the complete artifact. Every stylesheet, script, icon, link, and canonical route is
rooted at `/docs/`; it has no runtime dependency on platform-owned assets.

The platform owns only:

- the stable `/docs/` reverse-proxy/static mount;
- the Docs navigation/footer link.

A deployment stages and validates a versioned docs tree, then atomically changes the active
release. Cloudflare may provide DNS, TLS, and caching for the apex domain, but is not required to
build the site. `docs.instantsubnet.com` may redirect to the canonical `/docs/` path later.

## Local preview

Serve this repository so `site/` is mounted at `/docs/`. No platform checkout or platform assets
are required.

```bash
python -m unittest discover -s tests -v
```

## Public-content rules

- Never publish credentials, seeds, private keys, wallet files, customer data, prompts, or output.
- Never publish host addresses, private topology, local test endpoints, operator identities,
  incident logs, deployment snapshots, or production cutover instructions.
- Finney and subnet 46 are the production defaults. Custom/local chains are explicit private
  overrides, not the public base workflow.
- Describe only released behavior. Mark unavailable work plainly and remove stale claims when the
  implementation changes.
- Test every published command from a clean supported environment.

Private design and phase records belong in the workspace `internal-docs/` directory, outside all
public repositories.
