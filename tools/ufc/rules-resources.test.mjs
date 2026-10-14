import { test } from 'node:test';
import assert from 'node:assert/strict';
import { promises as fs } from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { root, compareTrees, packageWire, sourcePath } from './generate.mjs';
import { validate } from './validate-rules-resources.mjs';
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
  assert.ok(!Object.hasOwn(manifest.resources[0].artifacts, 'ufc.generated.json'));
  assert.ok(!Object.hasOwn(manifest.resources[0].artifacts, 'report.json'));
  await fs.rm(path.join(generated, 'ufc.generated.json'), {force:true});
  await fs.rm(path.join(generated, 'report.json'), {force:true});
  await validate(directory); // A fresh checkout has no local conversion diagnostics.
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
