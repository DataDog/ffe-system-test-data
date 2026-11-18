//! Evaluates every case of evaluation-suites/regex with the Rust `regex` crate and fails on the
//! first difference in value, reason, or error code.
//!
//! The regex suite uses one shape: each flag has one allocation with one rule of one MATCHES or
//! NOT_MATCHES condition on a string attribute, and one split without shards. This evaluator
//! supports only that shape and fails on anything else, so a new shape cannot pass unchecked.
//!
//! Usage: cargo run --locked -- <suite directory> <expected case count>

use regex::Regex;
use serde_json::Value;
use std::collections::BTreeMap;
use std::path::Path;
use std::{env, fs, process};

/// A flag's one condition and the value it returns when the condition holds.
struct Flag {
    attribute: String,
    negated: bool,
    /// None when the pattern does not compile: every evaluation of the flag is a PARSE_ERROR.
    pattern: Option<Regex>,
    value: Value,
}

fn fail(message: String) -> ! {
    eprintln!("{message}");
    process::exit(1);
}

fn read(path: &Path) -> Value {
    let text = fs::read_to_string(path).unwrap_or_else(|e| fail(format!("{}: {e}", path.display())));
    serde_json::from_str(&text).unwrap_or_else(|e| fail(format!("{}: {e}", path.display())))
}

fn one<'a>(value: &'a Value, field: &str, key: &str) -> &'a Value {
    match value[field].as_array().map(Vec::as_slice) {
        Some([only]) => only,
        _ => fail(format!("{key}: expected exactly one entry in {field}")),
    }
}

fn parse_flag(key: &str, flag: &Value) -> Flag {
    if flag["enabled"] != Value::Bool(true) || flag["variationType"] != "STRING" {
        fail(format!("{key}: expected an enabled STRING flag"));
    }
    let allocation = one(flag, "allocations", key);
    if allocation.get("startAt").is_some() || allocation.get("endAt").is_some() {
        fail(format!("{key}: time windows are not supported"));
    }
    let condition = one(one(allocation, "rules", key), "conditions", key);
    let split = one(allocation, "splits", key);
    if split["shards"].as_array().map_or(true, |shards| !shards.is_empty()) {
        fail(format!("{key}: splits with shards are not supported"));
    }
    let negated = match condition["operator"].as_str() {
        Some("MATCHES") => false,
        Some("NOT_MATCHES") => true,
        other => fail(format!("{key}: unsupported operator {other:?}")),
    };
    let pattern = condition["value"].as_str().unwrap_or_else(|| fail(format!("{key}: pattern is not a string")));
    let variation = split["variationKey"].as_str().unwrap_or_else(|| fail(format!("{key}: no variationKey")));
    Flag {
        attribute: condition["attribute"].as_str().unwrap_or_else(|| fail(format!("{key}: no attribute"))).to_owned(),
        negated,
        pattern: Regex::new(pattern).ok(),
        value: flag["variations"][variation]["value"].clone(),
    }
}

/// Returns the expected result object for one case: value, reason, and an optional errorCode.
fn evaluate(flag: &Flag, case: &Value) -> Value {
    let default = case["defaultValue"].clone();
    let Some(pattern) = &flag.pattern else {
        return serde_json::json!({"value": default, "reason": "ERROR", "errorCode": "PARSE_ERROR"});
    };
    // A missing attribute fails the condition, for NOT_MATCHES too.
    let holds = match &case["attributes"][flag.attribute.as_str()] {
        Value::Null => false,
        Value::String(text) => pattern.is_match(text) != flag.negated,
        other => fail(format!("{}: unsupported attribute value {other}", case["flag"])),
    };
    if holds {
        serde_json::json!({"value": flag.value, "reason": "TARGETING_MATCH"})
    } else {
        serde_json::json!({"value": default, "reason": "DEFAULT"})
    }
}

fn main() {
    let args: Vec<String> = env::args().collect();
    let [_, suite, expected_count] = args.as_slice() else {
        fail("usage: regex-conformance <suite directory> <expected case count>".to_owned());
    };
    let expected_count: usize = expected_count.parse().unwrap_or_else(|e| fail(format!("case count: {e}")));
    let suite = Path::new(suite);

    let config = read(&suite.join("ufc-config.json"));
    let flags: BTreeMap<&str, Flag> = config["flags"]
        .as_object()
        .unwrap_or_else(|| fail("ufc-config.json: no flags object".to_owned()))
        .iter()
        .map(|(key, flag)| (key.as_str(), parse_flag(key, flag)))
        .collect();

    let mut files: Vec<_> = fs::read_dir(suite.join("cases"))
        .unwrap_or_else(|e| fail(format!("cases: {e}")))
        .map(|entry| entry.unwrap_or_else(|e| fail(format!("cases: {e}"))).path())
        .filter(|path| path.extension().is_some_and(|ext| ext == "json"))
        .collect();
    files.sort();

    let mut count = 0;
    let mut differences = Vec::new();
    for path in &files {
        let cases = read(path);
        let cases = cases.as_array().unwrap_or_else(|| fail(format!("{}: not an array", path.display())));
        for (i, case) in cases.iter().enumerate() {
            let key = case["flag"].as_str().unwrap_or_else(|| fail(format!("{}[{i}]: no flag", path.display())));
            let flag = flags.get(key).unwrap_or_else(|| fail(format!("{}[{i}]: unknown flag {key}", path.display())));
            let actual = evaluate(flag, case);
            if actual != case["result"] {
                differences.push(format!("{}[{i}] {key}: expected {}, the regex crate gives {actual}",
                                         path.file_name().unwrap().to_string_lossy(), case["result"]));
            }
            count += 1;
        }
    }
    if !differences.is_empty() {
        fail(format!("{} of {count} regex cases differ:\n  {}", differences.len(), differences.join("\n  ")));
    }
    if count != expected_count {
        fail(format!("evaluated {count} regex cases, expected {expected_count}: update the count in the workflow"));
    }
    println!("All {count} regex cases in {} files match the Rust regex crate.", files.len());
}
