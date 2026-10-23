from pathlib import Path
import hashlib, json, os, subprocess
root=Path(__file__).resolve().parents[2]/'ruby'
evidence=Path(__file__).resolve().parent
ruby=root/'lib/datadog/open_feature/native_evaluator.rb'
c=root/'ext/libdatadog_api/feature_flags.c'
original={p:p.read_bytes() for p in [ruby,c]}
env=os.environ.copy()
env['BUNDLE_GEMFILE']=str(root/'gemfiles/ruby_3.4_openfeature_latest.gemfile')
env['SPEC']=str(root/'spec/datadog/open_feature/provider_spec.rb')
env['SPEC_OPTS']='--example "native opt-out string boundaries"'
command=[str(evidence/'tooling/bin/bundle'),'exec','rake','spec:open_feature']
results=[]
try:
    for name,path,old,new in [
        ('invalid-encoding',ruby,b'unless valid_native_timestamp?(timestamp)',b'unless timestamp.is_a?(String) && !timestamp.include?("\\0")'),
        ('nul-attribute-alias',c,b'  if (memchr(name, \'\\0\', RSTRING_LEN(key)) != NULL) {\n    return ST_CONTINUE;\n  }\n',b'')]:
        for p,data in original.items(): p.write_bytes(data)
        data=path.read_bytes()
        assert old in data, name
        path.write_bytes(data.replace(old,new,1))
        log=evidence/(name+'-negative-control.log')
        with log.open('w') as stream:
            result=subprocess.run(command,cwd=root,env=env,stdout=stream,stderr=subprocess.STDOUT)
        assert result.returncode != 0, (name,'negative control did not fail')
        assert 'failures' in log.read_text() and 'examples' in log.read_text(), name
        results.append({'name':name,'exit_code':result.returncode,'log':log.name})
finally:
    for p,data in original.items(): p.write_bytes(data)
    for p,data in original.items(): assert p.read_bytes()==data
(evidence/'negative-controls.json').write_text(json.dumps({'command':command,'results':results,'restored':True},indent=2)+'\n')
print(json.dumps(results))
