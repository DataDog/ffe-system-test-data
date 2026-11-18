# Documentation map

Read [repository instructions](../AGENTS.md) before you change this
repository. This map lists the current contract and contributor routes.

| Reader need | Document |
| --- | --- |
| Contract overview and ownership | [README](../README.md) |
| How to change the contract | [Contributing](../CONTRIBUTING.md) |
| Precomputed assignment fixtures | [Precomputed fixture guide](../precomputed-assignments/README.md) |
| Response signing fixtures | [Response signing fixtures](../response-signing/README.md) |
| Flag selection vectors | [Flag selection](../flag-selection/README.md) |
| UFC tooling | [UFC tools](../tools/ufc/README.md) |
| Verification procedures | [Verification](VERIFICATION.md) |

## Contract decisions

Downstream SDKs and services must conform to this contract. Before you change
an expected result, search the FFE LEAN KB for the affected decision and cite
its key and revision in the PR. Record a new decision with the
`lean-kb-sheets` skill. The FactoryKit contract nudge gives this reminder when
contract paths change.

## FactoryKit runtime

This repository is a FactoryKit POC. Follow the canonical
[Install FactoryKit procedure](https://github.com/ddoghq/factorykit/blob/main/docs/USER-GUIDE.md#install-factorykit).
Record the absolute command path as `factorykit_executable`.

From the repository root, run the Foundation gate:

```bash
"$factorykit_executable" --root . foundation gate --factoryspec factoryspec.yaml \
  --entry-point scripts/foundation_check.py --snapshot worktree --against HEAD
```

If no runtime is available, report the command as not run.
