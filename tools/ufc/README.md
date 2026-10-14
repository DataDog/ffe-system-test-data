# Rules fixture artifacts

Install the locked serializer with `npm ci --prefix tools/ufc --ignore-scripts`.

```sh
npm --prefix tools/ufc run generate -- --converter /absolute/path/to/ufc-fixtures --converter-sha256 EXPECTED_SHA256 --converter-source /absolute/path/to/dd-source
npm --prefix tools/ufc run check -- --converter /absolute/path/to/ufc-fixtures --converter-sha256 EXPECTED_SHA256 --converter-source /absolute/path/to/dd-source
node tools/ufc/validate-rules-resources.mjs
node --test tools/ufc/rules-resources.test.mjs
python3 tools/ufc/validate-rules-schema.py
```

The catalog sends the complete original `ufc-config.json` directly to the production
Go converter. There is no authored flag selection or normalization. The converter
attempts every flag and reports included or omitted with an explicit error reason.
Generated JSON retains original metadata and included flag definitions; only
reported failed flags are removed. Canonical JSON and evaluation cases never change.

Each resource contains filtered `ufc.generated.json`, raw `ufc.pb`, the conversion
`report.json`, and `configuration-wire.json`. The wire file is the UTF-8 portable
wire string itself, without extra JSON quoting. Public pinned
`@datadog/flagging-core@3.0.1` APIs decode protobuf, serialize wire, and parse it
again. Parser failure, empty configurations, changed semantic payload and unstable
wire serialization fail generation. No timestamps, ETags or split reasons are added.

`parity.json` is diagnostic: existing expectations are compared with original JSON,
filtered JSON, binary and wire for cases whose flags were converted. It records
mismatches and cases whose flags are absent from generated configuration.
SDK mismatches never filter flags, rewrite expectations, or block artifact generation.
A successful generation is serialization evidence, not a green evaluation suite or
browser offline initialization proof. The evaluation clock is fixed in the diagnostic.

Generation stages the whole artifact set before replacing it. Check mode writes
nothing in the repository and detects stale, missing and unexpected artifacts.
The manifest hashes source, catalog, tooling, schemas, cases and all generated files.
The source lock records exact production codec/CLI sources. The supplied executable
must match its expected SHA256. Source correspondence is declared build provenance,
not a cryptographic build attestation. No immutable published converter distribution
is configured; local generation uses the companion dd-source CLI. No CI added.

`ufc.generated.json` and `report.json` are local diagnostics: gitignored and excluded from the committed artifact manifest. Regenerate them locally when inspecting conversion. The report includes a structural JSON comparison (ignoring whitespace/object-key order): exact source equality, equality after only reported omissions, and the omitted flag keys. With omitted flags, exact equality is false even when all retained content is unchanged.
