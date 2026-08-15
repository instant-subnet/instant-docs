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
- [Validator guide](site/validators/index.html) — PM2 setup, burn behavior, requirements, and limitations;
- [Troubleshooting](site/troubleshooting/index.html) — public, non-sensitive recovery checks.

It contains no runtime code, private deployment data, incident evidence, or secret material.

## Publishing contract

`site/` is the complete artifact. Every stylesheet, script, icon, link, and canonical route is
rooted at `/docs/`; it has no runtime dependency on platform-owned assets.

The platform owns only:

- the stable `/docs/` reverse-proxy/static mount;
- the Docs navigation/footer link.

A deployment validates a versioned docs tree, then atomically changes the active release. The
canonical documentation path is `https://instantsubnet.com/docs/`.

## Local preview

Serve this repository so `site/` is mounted at `/docs/`. No platform checkout or platform assets
are required.

```bash
python -m unittest discover -s tests -v
```

## Public-content rules

- Never publish credentials, seeds, private keys, wallet files, customer data, prompts, or output.
- Never publish host addresses, private topology, local test endpoints, operator identities,
  incident logs, deployment snapshots, or private operations instructions.
- Finney and subnet 46 are the production defaults. Custom/local chains are explicit private
  overrides, not the public base workflow.
- Describe only released behavior. Mark unavailable work plainly and remove stale claims when the
  implementation changes.
- Test every published command from a clean supported environment.
