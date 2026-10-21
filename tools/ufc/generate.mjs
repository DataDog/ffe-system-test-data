import { isDeepStrictEqual } from 'node:util';
import { createRequire } from 'node:module';
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { promises as fs } from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { parity } from './parity.mjs';
import { fileURLToPath } from 'node:url';
const require = createRequire(import.meta.url);
const { configurationFromRulesBinary, configurationFromString, configurationToString } = require('@datadog/flagging-core/rules-based');
export const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
export const sha256 = data => createHash('sha256').update(data).digest('hex');
const json = value => JSON.stringify(value, null, 2) + '\n';
const stable = value => JSON.stringify(value, (_, item) => item && typeof item === 'object' && !Array.isArray(item) ? Object.fromEntries(Object.entries(item).sort(([a], [b]) => a.localeCompare(b))) : item);
export async function sourcePath(relative, base = root) {
  if (typeof relative !== 'string' || path.isAbsolute(relative) || relative.split(/[\\/]/).includes('..')) throw new Error(`Unsafe source path: ${relative}`);
  const resolved = await fs.realpath(path.join(base, relative));
  if (!resolved.startsWith(await fs.realpath(base) + path.sep)) throw new Error(`Source escapes repository: ${relative}`);
  return resolved;
}
export function packageWire(binary) {
  if (!binary.length) throw new Error('Empty protobuf artifact');
  const configuration = configurationFromRulesBinary(binary);
  const validate = value => {
    if (!value || value.configurationError || value.rulesError || !value.rules?.response || !Object.keys(value.rules.response.flags ?? {}).length) throw new Error('SDK parser did not produce a nonempty rules configuration');
  };
  validate(configuration);
  const wire = configurationToString(configuration);
  const decoded = configurationFromString(wire);
  validate(decoded);
  if (!isDeepStrictEqual(decoded.rules.response, configuration.rules.response)) throw new Error('Wire parser changed rules configuration');
  if (configurationToString(decoded) !== wire) throw new Error('Wire serialization is not stable');
  // The public serializer may canonicalize protobuf map order; preserve the same semantic payload.
  const embedded = Buffer.from(JSON.parse(wire).rules.response, 'base64');
  if (!isDeepStrictEqual(configurationFromRulesBinary(embedded).rules.response, configuration.rules.response)) throw new Error('Wire payload differs from raw protobuf');
  return wire;
}
async function filesUnder(directory, ignoreDependencies = false) {
  let entries;
  try { entries = await fs.readdir(directory, { withFileTypes: true }); } catch (error) { if (error.code === 'ENOENT') return []; throw error; }
  const result = [];
  for (const entry of entries.sort((a, b) => a.name.localeCompare(b.name))) {
    if (ignoreDependencies && entry.name === 'node_modules') continue;
    if (entry.isSymbolicLink()) throw new Error(`Generated artifacts must not be symlinks: ${entry.name}`);
    if (entry.isDirectory()) for (const nested of await filesUnder(path.join(directory, entry.name), ignoreDependencies)) result.push(`${entry.name}/${nested}`);
    else if (entry.isFile()) result.push(entry.name);
    else throw new Error(`Unsupported generated entry: ${entry.name}`);
  }
  return result;
}
export async function compareTrees(expected, actual, ignored = []) {
  const expectedFiles = (await filesUnder(expected)).filter(file => !ignored.includes(file)), actualFiles = (await filesUnder(actual)).filter(file => !ignored.includes(file));
  const differences = [];
  for (const file of [...new Set([...expectedFiles, ...actualFiles])].sort()) {
    if (!expectedFiles.includes(file)) differences.push(`unexpected: ${file}`);
    else if (!actualFiles.includes(file)) differences.push(`missing: ${file}`);
    else if (!(await fs.readFile(path.join(expected, file))).equals(await fs.readFile(path.join(actual, file)))) differences.push(`stale: ${file}`);
  }
  return differences;
}
export async function converterIdentity(converterSource) {
  const codecRoot = await fs.realpath(converterSource);
  const sourceIdentity = { revision: execFileSync('git', ['-C', codecRoot, 'rev-parse', 'HEAD'], { encoding: 'utf8' }).trim(), files: {} };
  for (const directory of ['domains/ffe/libs/flagging/ufc', 'domains/ffe/libs/flagging/core/model', 'domains/ffe/tools/ufc-fixtures']) {
    for (const relative of await filesUnder(path.join(codecRoot, directory))) {
      if ((relative.endsWith('.go') && !relative.endsWith('_test.go')) || relative.endsWith('.proto')) {
        const file = `${directory}/${relative}`;
        sourceIdentity.files[file] = sha256(await fs.readFile(path.join(codecRoot, file)));
      }
    }
  }
  if (!Object.keys(sourceIdentity.files).length) throw new Error('Converter source tree is missing production codec files');
  return sourceIdentity;
}
export async function generate({ converter, converterSha256, converterSource, check = false, base = root } = {}) {
  if (!converter || !/^[a-f0-9]{64}$/.test(converterSha256 ?? '')) throw new Error('Provide --converter PATH --converter-sha256 SHA256. A published immutable converter distribution is not yet configured.');
  const executable = await fs.realpath(converter);
  if (sha256(await fs.readFile(executable)) !== converterSha256) throw new Error('Converter binary SHA256 does not match expected identity');
  if (!converterSource) throw new Error('Provide --converter-source PATH to record the local production codec source provenance');
  const sourceIdentity = await converterIdentity(converterSource);
  const lockedIdentity = JSON.parse(await fs.readFile(await sourcePath('tools/ufc/converter-lock.json', base)));
  if (stable(sourceIdentity) !== stable(lockedIdentity)) throw new Error('Converter source does not match tools/ufc/converter-lock.json');
  const identity = JSON.parse(execFileSync(executable, ['--version'], { encoding: 'utf8' }));
  const catalogBytes = await fs.readFile(await sourcePath('rules-resources/catalog.json', base));
  const catalog = JSON.parse(catalogBytes);
  if (catalog.schemaVersion !== 1 || !Array.isArray(catalog.resources) || !catalog.resources.length) throw new Error('Catalog must contain resources');
  const staging = await fs.mkdtemp(path.join(os.tmpdir(), 'ffe-ufc-'));
  const output = path.join(staging, 'generated');
  await fs.mkdir(output);
  try {
    const manifest = { schemaVersion: 1, catalogSha256: sha256(catalogBytes), converter: { ...identity, source: sourceIdentity }, generatorInputs: {}, serializer: '@datadog/flagging-core@3.0.1', resources: [] };
    for (const directory of ['tools/ufc', 'schemas', 'evaluation-cases']) {
      for (const relative of await filesUnder(path.join(base, directory), true)) {
        if (relative.startsWith('node_modules/')) continue;
        const file = `${directory}/${relative}`;
        manifest.generatorInputs[file] = sha256(await fs.readFile(await sourcePath(file, base)));
      }
    }
    const seen = new Set();
    for (const resource of catalog.resources) {
      if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(resource.id) || seen.has(resource.id)) throw new Error(`Invalid or duplicate resource id: ${resource.id}`);
      seen.add(resource.id);
      const source = await sourcePath(resource.source, base);
      const sourceBytes = await fs.readFile(source);
      manifest.generatorInputs[resource.source] = sha256(sourceBytes);
      const directory = path.join(output, resource.id);
      const input = source;
      try {
        execFileSync(executable, ['--input', input, '--output-dir', directory], { stdio: 'pipe' });
      } catch (error) {
        let diagnostic = '';
        try { diagnostic = await fs.readFile(path.join(directory, 'report.json'), 'utf8'); } catch {}
        throw new Error(`Conversion failed for ${resource.id}: ${error.stderr?.toString() ?? error.message}\n${diagnostic}`);
      }
      const report = JSON.parse(await fs.readFile(path.join(directory, 'report.json')));
      if (report.sourceSha256 !== sha256(sourceBytes)) throw new Error(`Converter source digest mismatch for ${resource.id}`);
      for (const flag of report.flags ?? []) if (flag.status === 'omitted') console.warn(`Omitted ${flag.key}: ${flag.error}`);
      const binary = await fs.readFile(path.join(directory, 'ufc.pb'));
      const wire = packageWire(binary);
      await fs.writeFile(path.join(directory, 'configuration-wire.json'), wire);
      const convertedFlagKeys = Object.keys(configurationFromRulesBinary(binary).rules.response.flags).sort();
      const omittedFlagKeys = Object.keys(JSON.parse(sourceBytes).flags).filter(key => !convertedFlagKeys.includes(key)).sort();
      const proof = parity(base, binary, wire, JSON.parse(await fs.readFile(path.join(directory, 'ufc.generated.json'))));
      await fs.writeFile(path.join(directory, 'parity.json'), json(proof));
      if (proof.failures.length) console.warn(`${resource.id}: ${proof.failures.length} evaluation cases differ; see parity.json (diagnostic, not a generation filter)`);
      const artifacts = {};
      for (const name of (await filesUnder(directory)).filter(name => !['ufc.generated.json', 'report.json', 'parity.json'].includes(name))) artifacts[name] = { sha256: sha256(await fs.readFile(path.join(directory, name))) };
      manifest.resources.push({ id: resource.id, source: resource.source, sourceSha256: sha256(sourceBytes), convertedFlagKeys, omittedFlagKeys, artifacts });
    }
    await fs.writeFile(path.join(output, 'manifest.json'), json(manifest));
    const destination = path.join(base, 'rules-resources/generated');
    const ignored = catalog.resources.flatMap(resource => ['ufc.generated.json', 'report.json', 'parity.json'].map(name => `${resource.id}/${name}`));
    const differences = await compareTrees(output, destination, ignored);
    if (check && differences.length) throw new Error(`Generated artifacts differ:\n${differences.join('\n')}\nRun npm --prefix tools/ufc run generate -- --converter PATH --converter-sha256 SHA256 --converter-source DD_SOURCE_PATH`);
    if (!check) {
      // Prepare on the destination filesystem before replacing the accepted set.
      const replacement = await fs.mkdtemp(path.join(path.dirname(destination), '.replacement-'));
      const candidate = path.join(replacement, 'candidate');
      const previous = path.join(replacement, 'previous');
      let backedUp = false, installed = false;
      try {
        await fs.cp(output, candidate, { recursive: true });
        try { await fs.rename(destination, previous); backedUp = true; }
        catch (error) { if (error.code !== 'ENOENT') throw error; }
        try { await fs.rename(candidate, destination); installed = true; }
        catch (error) { if (backedUp) { await fs.rename(previous, destination); backedUp = false; } throw error; }
      } finally { if (installed || !backedUp) await fs.rm(replacement, { recursive: true, force: true }); }
    }
    return manifest;
  } finally { await fs.rm(staging, { recursive: true, force: true }); }
}
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    const options = {};
    for (let i = 2; i < process.argv.length; i++) {
      const argument = process.argv[i];
      if (argument === '--check') options.check = true;
      else if (argument === '--converter' || argument === '--converter-sha256' || argument === '--converter-source') options[argument === '--converter' ? 'converter' : argument === '--converter-source' ? 'converterSource' : 'converterSha256'] = process.argv[++i];
      else throw new Error(`Unknown argument: ${argument}`);
    }
    const result = await generate(options);
    console.log(`${options.check ? 'Checked' : 'Generated'} ${result.resources.length} rules resource(s)`);
  } catch (error) { console.error(error.message); if (error.stderr) console.error(error.stderr.toString()); process.exitCode = 1; }
}
