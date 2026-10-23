from pathlib import Path
import subprocess, hashlib, json, shutil, xml.etree.ElementTree as ET
root=Path('/home/bits/.ffe-ai/workspaces/opt-out-finish-20261022-java')
evidence=Path('/home/bits/.ffe-ai/workspaces/opt-out-finish-20261022-java-evidence')
evaluators=[root/'dd-openfeature/src/main/java/com/datadog/openfeature/internal/evaluation/FlagEvaluator.java',root/'products/feature-flagging/feature-flagging-api/src/main/java/datadog/trace/api/openfeature/DDEvaluator.java']
helpers=[root/'dd-openfeature/src/main/java/com/datadog/openfeature/internal/evaluation/ExperimentationOptOut.java',root/'products/feature-flagging/feature-flagging-api/src/main/java/datadog/trace/api/openfeature/ExperimentationOptOut.java']
base=['./gradlew','--max-workers=2','--continue','-PmavenRepositoryProxy=https://maven-central.storage-download.googleapis.com/maven2']
modules=['dd-openfeature','products/feature-flagging/feature-flagging-api']
changes=[('D004-scope',evaluators,'experimentationCutoff != null\n          && experimentationOptOutMode == ExperimentationOptOutMode.FUTURE_EXPERIMENTS_ONLY\n          && ExperimentationOptOut.hasInvalidActivation','ExperimentationOptOut.hasInvalidActivation','*ExperimentationOptOutConformanceTest',[]),('doLog-compatibility',helpers,'!Boolean.TRUE.equals(allocation.doLog)','Boolean.FALSE.equals(allocation.doLog)','*ExperimentationOptOutConformanceTest',[]),('D017-call-site',evaluators,'experimentationCutoff != null\n            && ExperimentationOptOut.excludes','ExperimentationOptOut.excludes','*ExperimentationOptOutOperationProbeTest',['-I',str(evidence/'operations.init.gradle')])]
receipts=[]
for name,paths,old,new,selector,extra in changes:
 out=evidence/name;out.mkdir(exist_ok=True)
 originals={p:p.read_bytes() for p in paths}
 try:
  for p in paths:
   source=p.read_text();assert source.count(old)==1,(name,p);p.write_text(source.replace(old,new))
  command=base+extra
  for module in modules:command+=[':'+module.replace('/',':')+':test','--tests',selector]
  with (out/'gradle.log').open('w') as log:result=subprocess.run(command,cwd=root,stdout=log,stderr=subprocess.STDOUT)
  receipt={'control':name,'exit_code':result.returncode,'modules':{},'original_hashes':{str(p.relative_to(root)):hashlib.sha256(data).hexdigest() for p,data in originals.items()}}
  for module in modules:
   xmls=list((root/module/'build/test-results/test').glob('TEST-*.xml'))
   stats={k:sum(int(ET.parse(p).getroot().get(k,'0')) for p in xmls) for k in ['tests','failures','errors','skipped']}
   for p in xmls:shutil.copy(p,out/p.name)
   receipt['modules'][module]=stats
  assert result.returncode!=0 and all(v['failures']>0 for v in receipt['modules'].values()),receipt
  receipts.append(receipt);(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
 finally:
  for p,data in originals.items():p.write_bytes(data)
(evidence/'negative-controls.json').write_text(json.dumps(receipts,indent=2)+'\n')
