import { test } from 'node:test';
import assert from 'node:assert/strict';
import { promises as fs } from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { root, compareTrees, packageWire, sourcePath } from './generate.mjs';
import { validate } from './validate-rules-resources.mjs';
import { parity } from './parity.mjs';
async function temporary(fn) {
  const directory = await fs.mkdtemp(path.join(os.tmpdir(), 'rules-validation-'));
  try { await fn(directory); } finally { await fs.rm(directory, { recursive: true, force: true }); }
}
test('whole-tree comparison catches missing, stale and untracked extra files', async () => temporary(async directory => {
  const expected = path.join(directory, 'expected'), actual = path.join(directory, 'actual');
  await fs.mkdir(expected); await fs.mkdir(actual);
  await fs.writeFile(path.join(expected, 'a'), 'new');
  assert.deepEqual(await compareTrees(expected, actual), ['missing: a']);
  await fs.writeFile(path.join(actual, 'a'), 'old');
  await fs.writeFile(path.join(actual, 'extra'), 'extra');
  assert.deepEqual(await compareTrees(expected, actual), ['stale: a', 'unexpected: extra']);
  await fs.writeFile(path.join(expected, 'local.json'), '{}');
  assert.deepEqual(await compareTrees(expected, actual, ['local.json']), ['stale: a', 'unexpected: extra']);
}));
test('wire packaging rejects empty and malformed protobuf', () => {
  assert.throws(() => packageWire(Buffer.alloc(0)));
  assert.throws(() => packageWire(Buffer.from([255])));
  assert.throws(() => packageWire(Buffer.from([8, 1])));
});
test('integrity gate rejects source drift, deletion, extra output and changed tool pin', async () => temporary(async directory => {
  // Keep fixtures independent of repository state and avoid copying node_modules.
  for (const name of ['ufc-config.json', 'evaluation-cases', 'rules-resources', 'schemas']) await fs.cp(path.join(root, name), path.join(directory, name), { recursive: true });
  await fs.cp(path.join(root, 'tools/ufc'), path.join(directory, 'tools/ufc'), { recursive: true, filter: file => !file.split(path.sep).includes('node_modules') });
  await validate(directory);
  const generated = path.join(directory, 'rules-resources/generated/canonical-evaluator');
  const manifest = JSON.parse(await fs.readFile(path.join(directory, 'rules-resources/generated/manifest.json')));
  const parityPath = path.join(generated, 'parity.json');
  await fs.writeFile(parityPath, '{}');
  await assert.rejects(validate(directory), /Local evaluation diagnostics changed/);
  for (const name of ['ufc.generated.json', 'report.json', 'parity.json']) {
    assert.ok(!Object.hasOwn(manifest.resources[0].artifacts, name));
    await fs.rm(path.join(generated, name), { force: true });
  }
  await validate(directory); // A fresh checkout has no local conversion diagnostics.
  for (const name of ['ufc.generated.json', 'report.json', 'parity.json']) {
    const diagnosticPath = path.join(generated, name);
    for (const value of [null, false, 0, '', [], true, 1, 'invalid']) {
      await fs.writeFile(diagnosticPath, JSON.stringify(value));
      await assert.rejects(validate(directory), /must contain a JSON object/, `${name}: ${JSON.stringify(value)}`);
    }
    await fs.rm(diagnosticPath);
  }
  await validate(directory); // Absent diagnostics still validate after rejecting malformed roots.
  // Inventories control consumer skips and must match the payload even without diagnostics.
  const manifestPath = path.join(directory, 'rules-resources/generated/manifest.json');
  for (const field of ['convertedFlagKeys', 'omittedFlagKeys']) {
    for (const mutation of ['missing', 'duplicate', 'unsorted']) {
      const changed = structuredClone(manifest);
      if (mutation === 'missing') delete changed.resources[0][field];
      if (mutation === 'duplicate') changed.resources[0][field].push(changed.resources[0][field][0]);
      if (mutation === 'unsorted') changed.resources[0][field].reverse();
      await fs.writeFile(manifestPath, JSON.stringify(changed));
      await assert.rejects(validate(directory), /flag inventory differs/, `${field}: ${mutation}`);
    }
  }
  const swapped = structuredClone(manifest);
  const resource = swapped.resources[0];
  [resource.convertedFlagKeys[0], resource.omittedFlagKeys[0]] = [resource.omittedFlagKeys[0], resource.convertedFlagKeys[0]];
  resource.convertedFlagKeys.sort(); resource.omittedFlagKeys.sort();
  await fs.writeFile(manifestPath, JSON.stringify(swapped));
  await assert.rejects(validate(directory), /Converted flag inventory differs from binary/);
  await fs.writeFile(manifestPath, JSON.stringify(manifest));
  await validate(directory);
  const source = path.join(directory, 'ufc-config.json'), original = await fs.readFile(source);
  await fs.appendFile(source, '\n'); await assert.rejects(validate(directory)); await fs.writeFile(source, original);
  const artifact = path.join(directory, 'rules-resources/generated/canonical-evaluator/ufc.pb'), bytes = await fs.readFile(artifact);
  await fs.unlink(artifact); await assert.rejects(validate(directory)); await fs.writeFile(artifact, bytes);
  const extra = path.join(directory, 'rules-resources/generated/untracked');
  await fs.writeFile(extra, 'extra'); await assert.rejects(validate(directory)); await fs.unlink(extra);
  const pin = path.join(directory, 'tools/ufc/package.json');
  await fs.appendFile(pin, '\n'); await assert.rejects(validate(directory));
}));

test('source paths cannot leave repository', async () => {
  await assert.rejects(sourcePath('../ufc-config.json'));
  await assert.rejects(sourcePath('/etc/passwd'));
});

test('parity evaluates the explicit source without requiring a root UFC file', async () => temporary(async directory => {
  await fs.cp(path.join(root, 'evaluation-cases'), path.join(directory, 'evaluation-cases'), { recursive: true });
  const source = JSON.parse(await fs.readFile(path.join(root, 'ufc-config.json')));
  const generated = path.join(root, 'rules-resources/generated/canonical-evaluator');
  const binary = await fs.readFile(path.join(generated, 'ufc.pb'));
  const wire = await fs.readFile(path.join(generated, 'configuration-wire.json'), 'utf8');
  const baseline = parity(directory, binary, wire, source, source);
  const differentSource = { ...source, flags: {} };
  const changed = parity(directory, binary, wire, source, differentSource);
  assert.ok(baseline.exercisedCases > 0);
  const originalResults = report => report.results.map(result => result.mismatches.filter(mismatch => mismatch.encoding === 'original'));
  const otherResults = report => report.results.map(result => result.mismatches.filter(mismatch => mismatch.encoding !== 'original'));
  assert.notDeepEqual(originalResults(changed), originalResults(baseline));
  assert.deepEqual(otherResults(changed), otherResults(baseline));
}));
