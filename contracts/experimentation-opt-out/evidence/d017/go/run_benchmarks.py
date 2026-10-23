import hashlib,json,os,platform,re,statistics,subprocess,time
from pathlib import Path
root=Path(__file__).resolve().parent
out=root/'benchmarks';out.mkdir(exist_ok=True)
cpu=min(os.sched_getaffinity(0)); started=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())
pattern='^(BenchmarkBooleanEvaluationExclusion|BenchmarkBooleanEvaluation|BenchmarkEvaluationWithVaryingContextSize|BenchmarkEvaluationWithVaryingFlagCounts|BenchmarkConcurrentEvaluations)$'
commands=[]
for round in range(10):
 for name in (['baseline','candidate'] if round%2==0 else ['candidate','baseline']):
  cmd=['taskset','-c',str(cpu),str(root/f'{name}.test'),'-test.run=^$',f'-test.bench={pattern}','-test.benchtime=150ms','-test.cpu=1','-test.benchmem']
  result=subprocess.run(cmd,cwd='/home/bits/dd/dd-trace-go-5700-d004/openfeature',capture_output=True,text=True,check=True)
  (out/f'{round:02d}-{name}.txt').write_text(result.stdout+result.stderr)
  commands.append({'round':round,'side':name,'command':cmd,'exit_code':result.returncode})
 print('completed round',round+1,flush=True)
rows={}
for f in out.glob('*.txt'):
 side='baseline' if 'baseline' in f.name else 'candidate'
 for line in f.read_text().splitlines():
  m=re.match(r'^(Benchmark\S+)\s+\d+\s+([0-9.]+) ns/op\s+(\d+) B/op\s+(\d+) allocs/op',line)
  if m:
   rows.setdefault(m[1],{'baseline':[],'candidate':[]})[side].append({'ns':float(m[2]),'bytes':int(m[3]),'allocs':int(m[4])})
summary={}
for name,sides in sorted(rows.items()):
 assert len(sides['baseline'])==len(sides['candidate'])==10,(name,sides)
 b=statistics.median(x['ns'] for x in sides['baseline']);c=statistics.median(x['ns'] for x in sides['candidate'])
 summary[name]={'baseline_median_ns':b,'candidate_median_ns':c,'median_change_percent':100*(c/b-1),'samples':sides}
receipt={'started_at':started,'finished_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'baseline_commit':'c5fec6a009ffa29bf53f5377a21856c7c4aa5f56','candidate':'same source plus reviewed guard and identical benchmark source','cpu_affinity':cpu,'machine':platform.machine(),'toolchain':'go1.26.0 linux/amd64','rounds':10,'order':'alternating AB/BA','benchtime':'150ms','uninstrumented':True,'commands':commands,'results':summary,'raw_sha256':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(out.glob('*.txt'))},'limits':'Exploratory local medians on a shared host, no hypothesis test or universal threshold; comparison is against pre-guard child c5fec, not the PR parent. Does not establish absence of the six parent-relative CI regressions. New benchmark CI comparisons need a baseline in main.'}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:float(format(v['median_change_percent'],'.2f')) for k,v in summary.items()},indent=2))
