from pathlib import Path
import sysconfig

paths = {Path('/src/ddapm_test_agent/agent.py'), Path(sysconfig.get_paths()['purelib']) / 'ddapm_test_agent/agent.py'}
for path in sorted(paths):
    lines = path.read_text().splitlines(keepends=True)
    output = []
    count = 0
    for line in lines:
        output.append(line)
        if '"/evp_proxy/v2/api/v2/exposures"' in line:
            output.append(line.replace('"/evp_proxy/v2/api/v2/exposures"', '"/evp_proxy/v2/api/v2/flagevaluation"'))
            count += 1
    assert count == 3, (path, count)
    path.write_text(''.join(output))
