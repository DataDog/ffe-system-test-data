from pathlib import Path
import hashlib, json, shutil, subprocess, tarfile, xml.etree.ElementTree as ET

root=Path('/home/bits/.ffe-ai/workspaces/opt-out-finish-20261022-java-evidence')
sdk=Path('/home/bits/.ffe-ai/workspaces/opt-out-finish-20261022-java')
harness=Path('/home/bits/.ffe-ai/workspaces/opt-out-finish-20261022-system-tests')
out=root/'compact-final-export'
out.mkdir(exist_ok=True)
sha='a4d3dfb21cec0658417d4f3842dc8c8465a27371'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=sdk,text=True).strip()==sha
assert not subprocess.check_output(['git','status','--porcelain'],cwd=sdk,text=True).strip()

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,value):
 p=out/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,indent=2)+'\n')
def copy(source,name):
 p=out/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,p)

for name in ['signed-source-compare.json','negative-controls.json']:
 copy(root/name,name)
copy(root/'final-native/receipt.json','final-native/receipt.json')
operations={}
for variant,module,prefix in [
 ('standalone','dd-openfeature','com.datadog.openfeature.internal.evaluation'),
 ('legacy','products/feature-flagging/feature-flagging-api','datadog.trace.api.openfeature')]:
 xml=sdk/module/'build/test-results/test'/('TEST-'+prefix+'.ExperimentationOptOutOperationProbeTest.xml')
 tree=ET.parse(xml).getroot()
 assert tree.get('tests')=='36' and tree.get('failures')=='0' and tree.get('errors')=='0'
 observed=[]
 for line in (tree.findtext('system-out') or '').splitlines():
  if line.startswith('OPTOUT_OBSERVATION '):observed.append(json.loads(line.split(' ',1)[1]))
 assert len(observed)==36,len(observed)
 operations[variant]=observed
 copy(xml,'final-native/'+xml.name)
 probe=list((root/'operation-probes'/variant).rglob('ExperimentationOptOutOperationProbeTest.java'))
 assert len(probe)==1
 copy(probe[0],'adapters/'+variant+'/ExperimentationOptOutOperationProbeTest.java')
for xmlname in ['TEST-com.datadog.openfeature.ExperimentationOptOutConformanceTest.xml','TEST-datadog.trace.api.openfeature.ExperimentationOptOutConformanceTest.xml']:
 copy(root/'final-native'/xmlname,'final-native/'+xmlname)
copy(root/'inactive-path.jsonl','adapters/inactive-path.jsonl')
copy(root/'operations.init.gradle','adapters/operations.init.gradle')
copy(root/'negative_controls.py','adapters/negative_controls.py')
save('operation-observations.json',{'sdk_commit':sha,'adapter':'ByteBuddy advice records actual excludes calls and results; expected assertions run afterward','cases_sha256':digest(root/'inactive-path.jsonl'),'implementations':operations})

runtime_summary={}
for variant in ['legacy','standalone']:
 src=root/('runtime-'+variant)
 receipt=json.loads((src/'receipt.json').read_text())
 assert receipt['sdk_commit']==sha and receipt['exit_code']==0 and receipt['tests']=={'tests':5,'failures':0,'errors':0,'skipped':0}
 assert receipt['embedded_provider_matches'] and receipt['installed_agent_matches']
 rows=[]
 for name in ['receipt.json','junit.xml','harness.patch','intake-False.json','intake-True.json']:
  copy(src/name,'runtime/'+variant+'/'+name)
 for mode in ['disabled','immediate','future_experiments_only']:
  p=src/('policy-'+mode+'.json');observations=json.loads(p.read_text());assert len(observations)==30
  rows+=observations
  copy(p,'runtime/'+variant+'/'+p.name)
 assert len({x['id'] for x in rows})==90
 retained=[]
 for suppressed in [False,True]:
  intake=json.loads((src/('intake-'+str(suppressed)+'.json')).read_text())
  exposures=intake['exposures']; evaluations=intake['evaluations']
  retained_count=sum(x['evaluation_count'] for x in evaluations if x['flag']['key']=='retained')
  control_count=sum(x['evaluation_count'] for x in evaluations if x['flag']['key']=='control')
  assert len(exposures)==1 and retained_count==(0 if suppressed else 3) and control_count==1
  retained.append({'telemetry_suppressed':suppressed,'retained_value':'experiment','evaluations_performed':3,'captured_exposures':1,'captured_retained_evaluation_count':retained_count,'captured_control_evaluation_count':control_count})
 runtime_summary[variant]={'source':receipt['configuration_source'],'policy_cases':90,'test_counts':receipt['tests'],'retained_delivery':retained}
save('runtime/summary.json',{'sdk_commit':sha,'environment':'Linux amd64, Docker, JDK 21 application','harness_commit':'abe62eb21f53adba0d8ac038fe0539f8f05fb124','harness_has_external_uncommitted_adapters':True,'implementations':runtime_summary})

for source,name in [
 (harness/'tests/parametric/test_ffe/test_java_optout_contract.py','test_java_optout_contract.py'),
 (root/'run_runtime.py','run_runtime.py'),
 (root/'optout_backend.py','optout_backend.py'),
 (root/'test-agent-build/add_test_agent_capture.py','add_test_agent_capture.py'),
 (root/'test-agent-build/Dockerfile','capture-agent.Dockerfile'),
 (root/'standalone-backend-build/Dockerfile','standalone-backend.Dockerfile'),
 (root/'standalone-backend-build/server-cert.pem','standalone-test-certificate.pem'),
 (harness/'utils/build/docker/java/parametric/maven-settings.xml','maven-settings.xml')]:
 copy(source,'runtime/adapters/'+name)
assert digest(out/'runtime/adapters/test_java_optout_contract.py')==json.loads((out/'runtime/legacy/receipt.json').read_text())['adapter_sha256']
assert digest(out/'runtime/adapters/test_java_optout_contract.py')==json.loads((out/'runtime/standalone/receipt.json').read_text())['adapter_sha256']

attempts=[]
for folder,diagnosis in [
 ('runtime-legacy-stock-agent','Stock test agent lacks flagevaluation capture route; SDK policy and exposure assertions passed.'),
 ('runtime-legacy-source-only-agent-patch','Capture patch targeted unused /src module; installed module still lacked route.'),
 ('runtime-standalone-rc-unavailable','Standalone base has AgentBridges.detect()==NONE and no compatible RC bridge in this agent; inherited capability boundary.'),
 ('runtime-standalone-raw-configuration-envelope','HTTP fixture used raw RC payload; public CDN source requires JSON:API envelope.')]:
 p=root/folder/'receipt.json'
 receipt=json.loads(p.read_text())
 if 'tests' not in receipt:
  junit=ET.parse(root/folder/'junit.xml').getroot()
  suites=[junit] if junit.tag=='testsuite' else junit.findall('testsuite')
  receipt['tests']={key:sum(int(s.get(key,'0')) for s in suites) for key in ['tests','failures','errors','skipped']}
 attempts.append({'folder':folder,'receipt_sha256':digest(p),'tests':receipt['tests'],'diagnosis':diagnosis,'production_changes':False})
save('runtime/earlier-attempts.json',attempts)
logs=[]
for p in sorted(root.glob('*.log'))+sorted(root.glob('runtime-*/run.log')):
 logs.append({'relative_path':str(p.relative_to(root)),'bytes':p.stat().st_size,'sha256':digest(p)})
save('logs-retained-manifest.json',{'remote_root':str(root),'logs':logs})
files={str(p.relative_to(out)):digest(p) for p in sorted(out.rglob('*')) if p.is_file() and p.name!='manifest.json'}
save('manifest.json',{'sdk_commit':sha,'central_commit':'0520866bedb8c059df9c493cfe27ad294390c603','central_manifest_sha256':'078465ba0a37f193e65c3641197ac859c375c9d114d0d131ccc330d0c28dfa31','sha256':files})
with tarfile.open(root/'compact-final-export.tar.gz','w:gz') as archive:
 archive.add(out,arcname='compact-final-export')
print(json.dumps({'files':len(files),'bytes':(root/'compact-final-export.tar.gz').stat().st_size,'sha256':digest(root/'compact-final-export.tar.gz'),'runtime':runtime_summary},indent=2))
