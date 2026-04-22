# ffe-system-test-data

Canonical test data for Datadog's Feature Flags & Experimentation (FFE) SDK implementations.

## Overview

This repository contains the canonical set of flag configurations and evaluation test cases used to validate FFE SDK implementations across multiple languages. It serves as a single source of truth consumed via git submodules by:

- [system-tests](https://github.com/DataDog/system-tests) - Parametric tests
- [dd-trace-py](https://github.com/DataDog/dd-trace-py) - Python tracer
- [dd-trace-java](https://github.com/DataDog/dd-trace-java) - Java tracer
- [dd-trace-dotnet](https://github.com/DataDog/dd-trace-dotnet) - .NET tracer

## Directory Structure

```
ffe-system-test-data/
├── config/
│   └── ufc-config.json          # Master flag configuration (UFC format)
└── evaluation-cases/
    └── test-*.json              # Evaluation test case files
```

## Usage

### As a Git Submodule

Add this repository as a submodule to your project:

```bash
git submodule add https://github.com/DataDog/ffe-system-test-data path/to/ffe-data
```

Initialize and update submodules when cloning:

```bash
git clone --recurse-submodules <your-repo>
# or after cloning:
git submodule update --init --recursive
```

### File Formats

#### UFC Config (`config/ufc-config.json`)

The UFC (Unified Flag Configuration) file contains flag definitions in the format used by Datadog's Remote Configuration:

```json
{
  "flag-key": {
    "key": "flag-key",
    "enabled": true,
    "variationType": "STRING|BOOLEAN|INTEGER|NUMERIC|JSON",
    "variations": { ... },
    "allocations": [ ... ]
  }
}
```

#### Evaluation Test Cases (`evaluation-cases/test-*.json`)

Each test case file contains an array of evaluation scenarios:

```json
[
  {
    "flag": "flag-key",
    "variationType": "STRING",
    "defaultValue": "default",
    "targetingKey": "user-123",
    "attributes": { "country": "US" },
    "result": { "value": "expected-value" }
  }
]
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on adding or modifying test cases.

## License

Unless explicitly stated otherwise, all files in this repository are licensed under the Apache 2.0 License.

This product includes software developed at Datadog (https://www.datadoghq.com/). Copyright 2026 Datadog, Inc.

See [LICENSE](LICENSE) for the full license text.
