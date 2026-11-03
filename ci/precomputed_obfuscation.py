"""Generate and verify obfuscated companions of plain precomputed fixtures."""

import argparse
import copy
import hashlib
import json
from pathlib import Path

SUPPORTED_PLATFORMS = ("ios", "android", "flutter")
SALT = "000102030405060708090a0b0c0d0e0f"
DOMAIN = b"datadog.feature-flags.flag-key.v1\0"


def encode_key(key):
    return hashlib.sha256(DOMAIN + bytes.fromhex(SALT) + key.encode("utf-8")).hexdigest()


def companion(source):
    result = copy.deepcopy(source)
    attributes = result["response"]["data"]["attributes"]
    if "obfuscation" in attributes or attributes.get("obfuscated", False) is not False:
        raise ValueError("Source must contain a plain response")
    if not isinstance(attributes.get("flags"), dict):
        raise ValueError("Source must contain a flag map; document an exception if inapplicable")
    included = {entry["platform"] for entry in source.get("_include", [])}
    skipped = {entry["platform"] for entry in source.get("_skip", [])}
    platforms = [p for p in SUPPORTED_PLATFORMS
                 if ("_include" not in source or p in included) and p not in skipped]
    if not platforms:
        raise ValueError("No supported obfuscation consumer; document an exception")
    result["name"] = "obfuscation-" + source["name"]
    result["description"] = "Generated obfuscated companion: " + source["description"]
    result.pop("_skip", None)
    result["_include"] = [
        {"platform": p, "reason": "Supports obfuscation and the source fixture."}
        for p in platforms
    ]
    attributes["flags"] = {encode_key(key): value for key, value in attributes["flags"].items()}
    attributes["obfuscated"] = True
    attributes["obfuscation"] = {"scheme": "flag-key-sha256-v1", "salt": SALT}
    # Public lookup keys, results, events, and evaluation filters remain identical.
    return result


def expected_companions(cases, exceptions_path):
    sources = {p.relative_to(cases).as_posix(): p for p in sorted(cases.rglob("*.json"))
               if p.relative_to(cases).parts[0] != "obfuscation"}
    if not sources:
        raise ValueError("No plain fixtures found")
    exceptions = json.loads(exceptions_path.read_text())
    if not isinstance(exceptions, dict):
        raise ValueError("Obfuscation exceptions must map source paths to reasons")
    for path, reason in exceptions.items():
        if path not in sources:
            raise ValueError("Unknown or stale obfuscation exception: " + path)
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError("Obfuscation exception requires a reason: " + path)
    result = {}
    for path, source in sources.items():
        if path in exceptions:
            continue
        data = companion(json.loads(source.read_text()))
        relative = Path(path).with_name(data["name"] + ".json")
        result[relative] = (json.dumps(data, indent=2, ensure_ascii=False) + "\n").encode()
    return result


def synchronize(cases, exceptions_path, check=True):
    expected = expected_companions(cases, exceptions_path)
    generated = cases / "obfuscation" / "generated"
    actual = {p.relative_to(generated): p.read_bytes() for p in generated.rglob("*.json")}
    errors = []
    for path in sorted(expected.keys() | actual.keys()):
        if path not in expected:
            errors.append("Orphaned obfuscated companion: " + str(path))
        elif path not in actual:
            errors.append("Missing obfuscated companion: " + str(path))
        elif expected[path] != actual[path]:
            errors.append("Stale obfuscated companion: " + str(path))
    if not check:
        for path in actual.keys() - expected.keys():
            (generated / path).unlink()
        for path, content in expected.items():
            output = generated / path
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(content)
        return []
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Regenerate committed companions")
    parser.add_argument("--check", action="store_true", help="Verify companions without writing (default)")
    parser.add_argument("--cases", type=Path, default=Path("precomputed-assignments/cases"))
    parser.add_argument("--exceptions", type=Path,
                        default=Path("precomputed-assignments/obfuscation-exceptions.json"))
    args = parser.parse_args()
    if args.write and args.check:
        parser.error("Choose --write or --check")
    try:
        errors = synchronize(args.cases, args.exceptions, check=not args.write)
    except (ValueError, KeyError, TypeError, OSError) as error:
        parser.exit(1, str(error) + "\n")
    if errors:
        parser.exit(1, "\n".join(errors) + "\nRun python3 ci/precomputed_obfuscation.py --write\n")
    print("Obfuscated companions regenerated" if args.write else "Obfuscated companions are synchronized")


if __name__ == "__main__":
    main()
