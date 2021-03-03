'''
Test the speed of worker backend.
'''

# %%
import time
import pandas as pd
from tqdm.auto import tqdm
from IMServer.test_speed import generate_random_pinYin, query, suggest

# %%
# How many testing samples we used
num = 100

# %%
report = pd.DataFrame(columns=['Name', 'Cost', 'Num', 'Start', 'Stop'])
# %%
# Generate [num] pinYins
pinYins = [generate_random_pinYin() for _ in range(num)]

# %%
# Test query speed
t0 = time.time()

for py in tqdm(pinYins):
    query(py)

report = report.append({
    'Name': 'Query',
    'Cost': (time.time() - t0),
    'Num': num,
    'Start': t0,
    'Stop': time.time(),
}, ignore_index=True)

# %%
# Generate [num] ciZus
# If there are not enough samples,
# just re-run the script.
ciZus = []
for py in pinYins:
    df = query(py)
    for czs in df['ciZus']:
        [ciZus.append(e) for e in czs]
    if len(ciZus) > num:
        break

assert(len(ciZus) > num)
ciZus = ciZus[:num]

# %%
# Test suggest speed
t0 = time.time()

for cz in tqdm(ciZus):
    suggest(cz)

report = report.append({
    'Name': 'Suggest',
    'Cost': (time.time() - t0),
    'Num': num,
    'Start': t0,
    'Stop': time.time(),
}, ignore_index=True)

# %%
report['It/s'] = report['Num'] / report['Cost']
for c in ['Start', 'Stop']:
    report[c] = report[c].map(time.ctime)
report.to_html('speed_report.html')

# %%
print('All Done.')
