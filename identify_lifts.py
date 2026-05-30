# Attempt to identify the lifts in Old Low German verse.
# TODO: if still < 3, promite adv/vb AFTER initial stave
import json,re
from pathlib import Path
from collections import Counter

c_range = 5969
c_json_file = Path('heliand-c.json')
c_verses_file = Path('heliand-c-verses.json')
json_out = Path('heliand-c-scansion.json')
plaintext_out = Path('heliand-c-lifts.txt')

stress_words = [
        'N',
        'NR',
        'NPR',
        'ADJ',
        'ADJR',
        'ADJS',
        'NUM',
        'VB',
        'VAG',
        'VBN',
        'VN',
        'VNI',
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

stress_words_or_particles = [
        'ADV',
        'ADR',
        'ADS',
        'PRO',
        'PRO$'
        ]

finite = [
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

particles = finite + [
        'MAN',
        'C'
        ]

proclitics = [
        'D',
        'P',
        'CONJ',
        'NEG'
        ]

exceptionally_proclitics = [
        'sulic'
        ]

def alliterates(token, stave):
    stem = re.sub(r"^gi", "", token)
    if len(stem) > 0:
        if stem[0].lower() in 'aeioy':
            initial = 'a'
        else:
            initial = stem[0]
        if initial == stave.lower():
            return True

def scan(line):
    data = []
    formatted = []
    line_type = ''
    line_tokens = []
    line_no = str(0)
    if line['a'] is not None and len(line['a']) > 0:
        line_type = 'a'
        line_no = line['a'][0]['verse'].rstrip('ax')
    if line['b'] is not None and len(line['b']) > 0:
        line_type = line_type + 'b'
        line_no = line['b'][0]['verse'].rstrip('bx')
    for halfline in line_type:
        for idx,token in enumerate(line[halfline]):
            token['lift'] = None
            stripped_pos = token['pos'].split('^', 1)[0]
            if '+' in stripped_pos:
                stripped_pos = stripped_pos.split('+', 1)[1]
                # experiment with length/coda measures here:
            if stripped_pos in stress_words or (stripped_pos in stress_words_or_particles and len(token['form']) > 5):
                token['lift'] = True
                formatted.append(token['form'].upper())
            # also the last word in the offverse usually accommodates a lift:
            elif halfline == 'b':
                if idx == len(line[halfline]) - 1:
                    token['lift'] = True
                    formatted.append(token['form'].upper())
                else:
                    formatted.append(token['form'])
            else:
                formatted.append(token['form'])
            if halfline == 'a' and idx == len(line['a']) - 1:
                formatted[-1] = formatted[-1] + '    '
            data.append(token)
    lift_count = len([token for token in data if token['lift'] == True])
    if len(data) > 3 and lift_count < 4:
        initials = [re.sub(r"^gi", "", token['form'])[0] for token in data if token['lift'] == True]
        for idx,i in enumerate(initials):
            if i in 'aeioy':
                initials[idx] = 'a'
        counter = Counter(initials)
        stave = counter.most_common(1)[0][0]
        for idx,token in enumerate(data):
            if token['lift'] != True and alliterates(token['form'], stave):
                data[idx]['lift'] = True
                formatted[idx] = formatted[idx].upper()
        #if (data[0]['pos'] in finite or data[0]['pos'] in stress_words_or_particles) and data[0]['lift'] != True:
        #    data[0]['lift'] = True
        #    formatted[0] = formatted[0].upper()

    formatted = str("{:04d}".format(int(line_no))) + ' ' + ' '.join(formatted)

    return data,formatted

if not(c_json_file.is_file()):
    helipad_extract.extract()
with open(c_json_file) as c_json_data:
    c_tokens = json.load(c_json_data)
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

new_db = []
plaintext = ''
for i in range(1, c_range):
    findings,plaintext_line = scan(c_verses[str(i)])
    if findings is not None:
        new_db.extend(findings)
        plaintext = plaintext + plaintext_line + '\n'

with open(json_out, 'w') as f:
    json.dump(new_db, f, ensure_ascii=False, indent=4)

with open(plaintext_out, 'w') as f:
    f.write(plaintext)
