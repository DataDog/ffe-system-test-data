#!/usr/bin/env python3
"""Validate provenance references and render the linked decision/test history."""
import json
from pathlib import Path
import re

PR_URL = re.compile(r'https://github\.com/[^/]+/[^/]+/pull/[1-9][0-9]*$')


def validate(root, decisions, history):
    by_decision = {d['id']: d for d in decisions['decisions']}
    entries = {e['id']: e for e in history['entries']}
    if len(entries) != len(history['entries']):
        raise ValueError('Duplicate validation history ID')
    for decision in by_decision.values():
        source = decision['latest_setting']
        if not PR_URL.fullmatch(source['pr_url']):
            raise ValueError('Decision needs a PR provenance URL')
        thread = source['thread_url']
        if thread:
            if not re.fullmatch(re.escape(source['pr_url']) + r'#(?:discussion_r|pullrequestreview-)[0-9]+', thread):
                raise ValueError('Decision thread must belong to its provenance PR')
        elif not source['gap'] or source['kind'] not in {'local-decision', 'local-proposal', 'source-observation'}:
            raise ValueError('Missing decision-setting thread needs an explicit provenance gap')
        linked = decision['validation_history_ids']
        expected = {e['id'] for e in entries.values() if decision['id'] in e['decision_revisions']}
        if len(set(linked)) != len(linked) or set(linked) != expected or not linked:
            raise ValueError('Decision/history links are missing or inconsistent')
    for entry in entries.values():
        if not PR_URL.fullmatch(entry['pr_url']) or not (
            entry['evidence_url'] == entry['pr_url'] or entry['evidence_url'].startswith(entry['pr_url'] + '#')
        ):
            raise ValueError('History needs linked PR evidence')
        if not entry['decision_revisions'] or not set(entry['decision_revisions']) <= set(by_decision):
            raise ValueError('Unknown decision in validation history')
        for key, revision in entry['decision_revisions'].items():
            if revision is not None and (type(revision) is not int or not 1 <= revision <= by_decision[key]['revision']):
                raise ValueError('Invalid historical decision revision')
        if not entry['expectation_profile'] or not entry['limits']:
            raise ValueError('History needs tested expectations and evidence limits')
        evidence = Path(entry['evidence_file'])
        if evidence.is_absolute() or '..' in evidence.parts or not (root / evidence).is_file():
            raise ValueError('History evidence file is missing or outside the bundle')


def cell(value):
    return str(value).replace('|', '&#124;').replace('\n', ' ')


def render(decisions, history):
    lines = [
        '# Decision sources and validation history', '',
        'Generated from [decisions.json](decisions.json) and [validation-history.json](validation-history.json) with `python3 decision_history.py`.', '',
        'The current source points to the latest recorded decision-setting statement in its stated scope. A later test, approval or proposal does not replace it. PR-only links below explicitly mark missing public decision-setting provenance; any local acceptance is recorded separately. See each decision for its adoption and implementation status.', '',
        '## Current decision sources', '',
        '| Decision | Current rule | Latest setting / scope | Historical checks |',
        '| --- | --- | --- | --- |',
    ]
    for d in decisions['decisions']:
        source = d['latest_setting']
        url = source['thread_url'] or source['pr_url']
        label = 'Decision thread' if source['thread_url'] else 'PR context only'
        setting = f'[{label}]({url}) — {source["kind"]}. {source["scope_note"]}'
        if source['gap']:
            setting += ' ' + source['gap']
        if source.get('last_public_setting'):
            setting += f' [Prior public setting]({source["last_public_setting"]["thread_url"]}).'
        if source['recorded_at']:
            setting += ' Recorded ' + source['recorded_at'] + '.'
        checks = ', '.join(f'[{key}](#{key.lower()})' for key in d['validation_history_ids'])
        lines.append('| ' + ' | '.join(map(cell, [f'<a id="{d["id"].lower()}"></a>**{d["id"]} r{d["revision"]}**', d['statement'], setting, checks])) + ' |')
    lines.extend([
        '', '## Historical linked checks', '',
        'Rows preserve passing, failing and superseded evidence. Dates are report dates, not inferred execution times. “Revision unrecorded” means the check predates the numbered ledger; its original expectations are retained in JSON. Historical POC receipts were imported without rerunning native probes. Coverage-gap rows explicitly record missing tests.', '',
        '| Record / report date | Decisions tested | Target / source | Result / evidence | Check and limits |',
        '| --- | --- | --- | --- | --- |',
    ])
    for e in history['entries']:
        record = f'<a id="{e["id"].lower()}"></a>[{e["id"]}]({e["evidence_url"]}) — {e["recorded_at"] or "date unrecorded"}'
        refs = ', '.join(f'[{key}{" r"+str(rev) if rev is not None else " (revision unrecorded)"}](#{key.lower()})' for key, rev in e['decision_revisions'].items())
        target = e['target']
        if e['source_sha']:
            repo = e['pr_url'].split('/pull/')[0]
            target += f' @ [{e["source_sha"][:12]}]({repo}/commit/{e["source_sha"]})'
        else:
            target += ' — source SHA unrecorded / not applicable'
        if e['patch']:
            target += ' + patch (see receipt/comment)'
        result = f'**{e["outcome"]}**; {e["evidence_kind"]}; [saved evidence]({e["evidence_file"]})'
        lines.append('| ' + ' | '.join(map(cell, [record, refs, target, result, e['check'] + ' ' + e['limits']])) + ' |')
    return '\n'.join(lines) + '\n'


if __name__ == '__main__':
    root = Path(__file__).resolve().parent
    decisions = json.loads((root / 'decisions.json').read_text())
    history = json.loads((root / 'validation-history.json').read_text())
    validate(root, decisions, history)
    (root / 'decision-history.md').write_text(render(decisions, history))
