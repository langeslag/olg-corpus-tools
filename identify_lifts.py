import json
from pathlib import Path

stress_words = [
        'N',
        'NR',
        'ADJ',
        'ADJR',
        'ADJS',
        'NUM',
        'VB',
        'VAG',
        'VBN',
        'BE',
        'BAG',
        'BEN',
        'HV',
        'HAG',
        'HVN',
        'AX',
        'AXG',
        'AXN',
        'MD',
        'FW',
        'Q',
        'QR',
        'QS'
        ]

particles = [
        'PRO',
        'PRO$',
        'MAN',
        'C',
        'ADV',
        'ADR',
        'ADS',
        'VBI',
        'VBPH',
        'VBPI',
        'VBPS',
        'VBP',
        'VBDI',
        'VBDS',
        'VBD',
        'BEI',
        'BEPH',
        'BEPI',
        'BEPS',
        'BEP',
        'BEDI',
        'BEDS',
        'BED',
        'HVI',
        'HVPI',
        'HVPS',
        'HVP',
        'HVDI',
        'HVDS',
        'HVD',
        'AXI',
        'AXPI',
        'AXPS',
        'AXP',
        'AXDI',
        'AXDS',
        'AXD',
        'MDI',
        'MDPI',
        'MDPS',
        'MDP',
        'MDDI',
        'MDDS',
        'MDD'
        ]

proclitics = [
        'D',
        'P',
        'NEG'
        ]

c_range = 5969
c_json_file = Path('heliand-c.json')

def scan(line):
    formatted = []
    if line['a'] is not None and line['b'] is not None:
        long_line = line['a'] + line['b']
        for token in long_line:
            if token['pos'].split('^')[0] in stress_words:
                formatted.append(token['form'].upper())
            else:
                formatted.append(token['form'])

        if sum(1 for token in formatted if token.isupper()) > 3:
            print(f"{str("{:04d}".format(int(line['a'][0]['verse'].rstrip('ax'))))} {' '.join(formatted)}")

if not(c_json_file.is_file()):
    helipad_extract.extract()
with open(c_json_file) as c_json_data:
    c_tokens = json.load(c_json_data)
c_verses_file = Path('heliand-c-verses.json')
if not(c_verses_file.is_file()):
    c_verses = dict.fromkeys(range(1, c_range))
    for i in range(1, c_range):
        onverse = [token for token in c_tokens if token['verse'] == str(i)+'a']
        offverse = [token for token in c_tokens if token['verse'] == str(i)+'b']
        c_verses[i] = {
                'a': onverse,
                'b': offverse
                }
    with open(c_verses_file, 'w') as f:
        json.dump(c_verses, f, ensure_ascii=False, indent=4)
else:
    with open(c_verses_file) as f:
        c_verses = json.load(f)

for i in range(1, c_range):
    scan(c_verses[str(i)])
