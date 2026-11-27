# Flutter Android online-precomputed SDK gaps

CONTROL-032. Source-backed full02 audit, November 27, 2026. Actual run:24passed/40failed/1skipped,2317.41seconds. All65fresh reports independently audited. SDK pin71ad97b687f164cde9f43de5d6b42f48b791b9fd, runtime identifies dd-sdk-dart1.2.0; resolved clean package checkout matches pinned source byte-for-byte. Flutter iOS and later modes are untested.

“Paired” below means the base ID and its obfuscation- companion. Preserve canonical expected results.

| Gap | Affected cases | Count | Investigated behaviour |
| --- | --- | --- | --- |
| FLUTTER-001 | Paired numeric-float, numeric-integer, numeric-number, numeric-boundaries-float, numeric-boundaries-integer, type-mismatch-all-types |12| Lossless numeric reads incorrectly rejected as TYPE_MISMATCH because getters restrict wire labels/runtime types. |
| FLUTTER-002 | Paired numeric-boundaries-number, numeric-decimal-float, numeric-decimal-number |6| Inexact9007199254740993 Double conversion accepted instead of TYPE_MISMATCH. |
| FLUTTER-003 | Paired numeric-decimal-integer |2| Integer-labelled decimal assignment is dropped during decoding; expected Double1.2 becomes FLAG_NOT_FOUND. |
| FLUTTER-004 | Paired defaults-and-emission-gates |2| Invalid per-flag variation is discarded; expected PARSE_ERROR becomes FLAG_NOT_FOUND. |
| FLUTTER-005 | Paired dependent-flags |2| Dependent failure/error records are not preserved; expected GENERAL becomes FLAG_NOT_FOUND. |
| FLUTTER-006 | Sixteen obfuscation-reject cases below |16| Malformed payload is rejected, but typed invalid-response reason is lost through repository/provider status propagation and reaches FIT as generic UNKNOWN/general. |

FLUTTER-006 suffixes after obfuscation-reject-: false-with-descriptor, missing-descriptor, missing-marker, missing-salt, nonhex-digest, nonhex-salt, null-descriptor, null-marker, null-salt, plaintext, short-digest, short-salt, string-marker, unknown-scheme, uppercase-digest, uppercase-salt. Do not map every generic initialization error to INVALID_RESPONSE: network failures would be misclassified.

All64executed cases launched and received HTTP200 configuration;64request contexts exactly matched their fixtures.24passes include22plain/encoded cases and the two encoded hash/salt cases.70exposures and84evaluation events were recorded on passing cases. Failures stop before flush, so their zero counts do not prove suppression or full evaluation coverage. Individual evaluation RPC and diagnostic telemetry counts were not recorded.

WS-08 is preparing exact-case Android-host exclusions at the FIT layer because corpus platform filters cannot distinguish Flutter Android from iOS. Review and actual rerun remain required. The existing unsupported-consumer case is the single pre-execution platform-filter skip. No SDK fix, conformance claim, ticket filing or activation PR is implied. Detailed reports/source traces remain in coordinator-private evidence; no internal FIT source is published here.
