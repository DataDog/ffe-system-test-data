"""Materialize pinned system-test inputs and expected outputs for the real C API."""
import argparse, hashlib, json
from pathlib import Path

parser=argparse.ArgumentParser()
parser.add_argument('fixture_root', type=Path)
parser.add_argument('output', type=Path)
a=parser.parse_args()
p=a.fixture_root
manifest=json.loads((p/'SOURCE.json').read_text())
for name in ['runtime-cases.json','lookup-cases.json']:
    assert hashlib.sha256((p/name).read_bytes()).hexdigest()==manifest['files'][name]
cases=json.loads((p/'runtime-cases.json').read_text())+json.loads((p/'lookup-cases.json').read_text())
assert len(cases)==261
q=lambda x: 'NULL' if x is None else json.dumps(x)
rows=[];excluded=[];entry_count=0
for c in cases:
    attrs=c['attributes']; value=attrs.get('dd_experimentation_opt_out_at'); present=bool(attrs)
    if present and (value is None or isinstance(value,(list,dict))):
        excluded.append({'id':c['id'],'reason':'C AttributeValue has no null, array, or object variant; wrapper conversion is a separate obligation.'})
        continue
    e=c['expected'];mode={'disabled':0,'immediate':1,'future_experiments_only':2}[c['mode']]
    doc={'createdAt':'2026-01-01T00:00:00Z','environment':{'name':'test'},'flags':{c['flag']:c['configuration']} if 'configuration' in c else {}}
    if not present: attr='{0}'
    elif isinstance(value,str): attr='{.tag=DDOG_FFE_ATTRIBUTE_VALUE_STRING,.string='+q(value)+'}'
    elif isinstance(value,bool): attr='{.tag=DDOG_FFE_ATTRIBUTE_VALUE_BOOLEAN,.boolean='+str(value).lower()+'}'
    else: attr='{.tag=DDOG_FFE_ATTRIBUTE_VALUE_NUMBER,.number='+str(value)+'}'
    error='OK' if e['errorCode'] is None else e['errorCode']
    rows.append('{'+','.join([q(c['id']),q(json.dumps(doc,separators=(',',':'))),q(c['flag']),q(c['subject']),str(mode),str(present).lower(),attr,q(e['value']),q(e['variant']),q(e['allocationKey']),'DDOG_FFE_ERROR_CODE_'+error,'DDOG_FFE_REASON_'+e['reason'],str(e['exposure']).lower()])+'}')
    entry_count += 3 if mode==0 else (2 if mode==1 else 1)
prefix=r'''// Copyright 2026-Present Datadog, Inc. https://www.datadoghq.com/
// SPDX-License-Identifier: Apache-2.0
#include <stdio.h>
#include <string.h>
#include "datadog/ffe.h"
struct Case {
 const char *id, *json, *flag, *subject;
 enum ddog_ffe_ExperimentationOptOutMode mode;
 bool present;
 struct ddog_ffe_AttributeValue attribute;
 const char *value, *variant, *allocation;
 enum ddog_ffe_ErrorCode error;
 enum ddog_ffe_Reason reason;
 bool exposure;
};
static const struct Case cases[] = {
'''
suffix=r'''
};
static bool same(struct ddog_ffe_BorrowedStr actual, const char *expected) {
 if (!expected) return actual.ptr == NULL && actual.len == 0;
 return actual.len == strlen(expected) && actual.ptr && memcmp(actual.ptr, expected, actual.len) == 0;
}
static bool check(ddog_ffe_Handle_ResolutionDetails result, const struct Case *c) {
 struct ddog_ffe_VariantValue value = ddog_ffe_assignment_get_value(result);
 bool ok = ddog_ffe_assignment_get_error_code(result) == c->error &&
   ddog_ffe_assignment_get_reason(result) == c->reason &&
   ddog_ffe_assignment_get_do_log(result) == c->exposure &&
   same(ddog_ffe_assignment_get_variant(result), c->variant) &&
   same(ddog_ffe_assignment_get_allocation_key(result), c->allocation);
 // The C API leaves default selection to its caller. An absent assignment must have NONE.
 ok &= c->variant ? value.tag == DDOG_FFE_VARIANT_VALUE_STRING && same(value.string, c->value)
                  : value.tag == DDOG_FFE_VARIANT_VALUE_NONE;
 struct ddog_ffe_ArrayMap_BorrowedStr metadata = ddog_ffe_assignnment_get_flag_metadata(result);
 ok &= metadata.count == (c->allocation ? 1u : 0u);
 if (metadata.count == 1 && c->allocation) {
   ok &= same(metadata.elements[0].key, "__dd_allocation_key") && same(metadata.elements[0].value, c->allocation);
 }
 return ok;
}
int main(void) {
 unsigned passed=0, failed=0, calls=0;
 for (size_t i=0; i<sizeof(cases)/sizeof(cases[0]); ++i) {
  const struct Case *c=&cases[i];
  struct ddog_ffe_Result_HandleConfiguration parsed=ddog_ffe_configuration_new((struct ddog_ffe_BorrowedStr){.ptr=(const uint8_t*)c->json,.len=strlen(c->json)});
  if (parsed.tag != DDOG_FFE_RESULT_HANDLE_CONFIGURATION_OK_HANDLE_CONFIGURATION) {ddog_Error_drop(&parsed.err); ++failed; continue;}
  ddog_ffe_Handle_Configuration config=parsed.ok;
  struct ddog_ffe_AttributePair attribute={.name="dd_experimentation_opt_out_at",.value=c->attribute};
  ddog_ffe_Handle_EvaluationContext context=ddog_ffe_evaluation_context_new(c->subject,c->present?&attribute:NULL,c->present?1:0);
  bool ok=true;
  unsigned entries=c->mode==0?3:(c->mode==1?2:1);
  for (unsigned entry=0;entry<entries;++entry) {
   ddog_ffe_Handle_ResolutionDetails result;
   if (entry==0) result=ddog_ffe_get_assignment_with_opt_out_mode(config,c->flag,DDOG_FFE_EXPECTED_FLAG_TYPE_STRING,context,c->mode);
   else if(entry==1) result=ddog_ffe_get_assignment_with_options(config,c->flag,DDOG_FFE_EXPECTED_FLAG_TYPE_STRING,context,(struct ddog_ffe_EvaluationOptions){.experimentation_opt_out_immediate=c->mode==1});
   else result=ddog_ffe_get_assignment(config,c->flag,DDOG_FFE_EXPECTED_FLAG_TYPE_STRING,context);
   bool current=check(result,c);
   if(!current) fprintf(stderr,"FAIL %s entry=%u error=%d reason=%d\n",c->id,entry,ddog_ffe_assignment_get_error_code(result),ddog_ffe_assignment_get_reason(result));
   ok &= current; ++calls;
   ddog_ffe_assignment_drop(&result);
  }
  ddog_ffe_evaluation_context_drop(&context);
  ddog_ffe_configuration_drop(&config);
  if(ok) ++passed; else ++failed;
  printf("{\"id\":\"%s\",\"passed\":%s,\"entrypoints\":%u}\n",c->id,ok?"true":"false",entries);
 }
 fprintf(stderr,"C contract: %u passed, %u failed, %u evaluations\n",passed,failed,calls);
 return failed?1:0;
}
'''
a.output.write_text(prefix+',\n'.join(rows)+suffix)
receipt={'source_manifest':manifest,'cases':len(rows),'evaluations':entry_count,'excluded_cases':excluded,'generated_c_sha256':hashlib.sha256(a.output.read_bytes()).hexdigest(),'boundary':'Native C assignment results and exposure eligibility; no telemetry intake or wrapper lifecycle.'}
a.output.with_suffix('.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:receipt[k] for k in ['cases','evaluations','excluded_cases']},indent=2))
