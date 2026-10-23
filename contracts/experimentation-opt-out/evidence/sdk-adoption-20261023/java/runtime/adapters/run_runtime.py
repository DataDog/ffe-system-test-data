from pathlib import Path
import hashlib, json, os, shutil, subprocess, sys, xml.etree.ElementTree as ET, zipfile
root=Path('/home/bits/.ffe-ai/workspaces/opt-out-finish-20261022-java')
harness=Path('/home/bits/.ffe-ai/workspaces/opt-out-finish-20261022-system-tests')
evidence=Path('/home/bits/.ffe-ai/workspaces/opt-out-finish-20261022-java-evidence')
sha='a4d3dfb21cec0658417d4f3842dc8c8465a27371'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()==sha
assert not subprocess.check_output(['git','status','--porcelain'],cwd=root,text=True).strip()
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def artifact(module,prefix):
 files=list((root/module/'build/libs').glob(prefix+'*.jar'));assert len(files)==1,files;return files[0]
agent=artifact('dd-java-agent','dd-java-agent-');api=artifact('dd-trace-api','dd-trace-api-')
controller=harness/'utils/build/docker/java/parametric/src/main/java/com/datadoghq/trace/controller/FeatureFlagEvaluatorController.java'
original=subprocess.check_output(['git','show','HEAD:'+str(controller.relative_to(harness))],cwd=harness,text=True)
for variant in sys.argv[1:] or ['legacy','standalone']:
 provider=artifact('products/feature-flagging/feature-flagging-api' if variant=='legacy' else 'dd-openfeature','dd-openfeature-')
 out=evidence/('runtime-'+variant);out.mkdir(exist_ok=True)
 for p in [agent,api,provider]:shutil.copy2(p,harness/'binaries'/p.name)
 controller.write_text(original if variant=='legacy' else original.replace('import datadog.trace.api.openfeature.Provider;','import com.datadog.openfeature.Provider;'))
 env=dict(os.environ,TEST_LIBRARY='java',JAVA_OPTOUT_VARIANT=variant,JAVA_OPTOUT_RECEIPT_DIR=str(out),PYTEST_XDIST_AUTO_NUM_WORKERS="2")
 command=['./run.sh','PARAMETRIC','tests/parametric/test_ffe/test_java_optout_contract.py','--junitxml='+str(out/'junit.xml')]
 with (out/'run.log').open('w') as log:result=subprocess.run(command,cwd=harness,env=env,stdout=log,stderr=subprocess.STDOUT)
 shutil.copy(harness/'logs_parametric/reportJunit.xml',out/'junit.xml')
 receipt={'sdk_commit':sha,'harness_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=harness,text=True).strip(),'variant':variant,'exit_code':result.returncode,'artifacts':{p.name:digest(p) for p in [agent,api,provider]},'adapter_sha256':digest(harness/'tests/parametric/test_ffe/test_java_optout_contract.py'),'policy_cases_sha256':digest(harness/'tests/parametric/test_ffe/java-policy-v1-cases.json')}
 if (out/'junit.xml').exists():
  report_root=ET.parse(out/'junit.xml').getroot()
  suites=[report_root] if report_root.tag=='testsuite' else report_root.findall('testsuite')
  receipt['tests']={key:sum(int(s.get(key,'0')) for s in suites) for key in ['tests','failures','errors','skipped']}
 receipt['configuration_source']='agentless' if variant=='standalone' else 'remote_config'
 if variant=='standalone':
  receipt['direct_intake_image']=subprocess.check_output(['docker','image','inspect','ffe-java-optout-backend:a4d3dfb','--format','{{.Id}}'],text=True).strip()
  receipt['direct_intake_adapter_sha256']=digest(evidence/'optout_backend.py')
 receipt['capture_agent_image']=subprocess.check_output(['docker','image','inspect','ffe-java-optout-test-agent:a4d3dfb-v2','--format','{{.Id}}'],text=True).strip()
 image='java-optout-contract-'+variant
 image_id=subprocess.run(['docker','image','inspect',image,'--format','{{.Id}}'],capture_output=True,text=True)
 if image_id.returncode==0:
  receipt['image_id']=image_id.stdout.strip()
  cid=subprocess.check_output(['docker','create',image],text=True).strip()
  try:
   packaged=out/'client.jar'
   subprocess.run(['docker','cp',cid+':/client/target/dd-trace-java-client-1.0.0.jar',str(packaged)],check=True,stdout=subprocess.DEVNULL)
   with zipfile.ZipFile(packaged) as jar:
    entry=[name for name in jar.namelist() if name.startswith('BOOT-INF/lib/dd-openfeature') and name.endswith('.jar')]
    assert len(entry)==1,entry
    receipt['embedded_provider_sha256']=hashlib.sha256(jar.read(entry[0])).hexdigest()
   receipt['embedded_provider_matches']=receipt['embedded_provider_sha256']==digest(provider)
   installed_agent=out/'dd-java-agent.jar'
   subprocess.run(['docker','cp',cid+':/client/tracer/dd-java-agent.jar',str(installed_agent)],check=True,stdout=subprocess.DEVNULL)
   receipt['installed_agent_sha256']=digest(installed_agent)
   receipt['installed_agent_matches']=digest(installed_agent)==digest(agent)
  finally:subprocess.run(['docker','rm',cid],check=True,stdout=subprocess.DEVNULL)
 patch=subprocess.check_output(['git','diff','--binary'],cwd=harness);(out/'harness.patch').write_bytes(patch);receipt['harness_patch_sha256']=hashlib.sha256(patch).hexdigest()
 (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
 if result.returncode!=0:sys.exit(result.returncode)
 assert receipt.get('embedded_provider_matches') and receipt.get('installed_agent_matches'),receipt
