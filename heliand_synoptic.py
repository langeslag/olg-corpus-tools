# Generates synoptic heliand_synoptic.json and heliand_synoptic.txt.
import re,json
from pathlib import Path
import wikisource_extract
import helipad_extract

def reconstruct(line_no):
    on_verse_ref = line_no + 'a'
    off_verse_ref = line_no + 'b'
    c_a = ' '.join([token['form'] for token in c_tokens if token['verse'] == str(line_no)+'a'])
    c_b = ' '.join([token['form'] for token in c_tokens if token['verse'] == str(line_no)+'b'])
    c = '     '.join([c_a, c_b])
    if on_verse_ref in m_tokens.keys():
        m_a = ' '.join(m_tokens[on_verse_ref])
        m_b = ' '.join(m_tokens[off_verse_ref])
        m = '     '.join([m_a, m_b])
    else:
        m = ''
    result = {
        'c': c,
        'm': m
        }
    return result

c_json_file = 'heliand-c.json'
if not(Path(c_json_file).is_file()):
    helipad_extract.extract()

with open(c_json_file) as c_json_data:
    c_tokens = json.load(c_json_data)
    
m_json_file = 'heliand-m.json'
if not(Path(m_json_file).is_file()):
    wikisource_extract.extract()

with open(m_json_file) as m_json_data:
        m_tokens = json.load(m_json_data)

poem = dict()
x = [4517, 5920]
for i in range(1, 5983):
    poem[str(i)] = reconstruct(str(i))
    if i in x:
        xline = str(i) + 'x'
        poem[xline] = reconstruct(xline)

with open('heliand-synoptic.json', 'w', encoding='utf-8') as outfile:
    json.dump(poem, outfile, ensure_ascii=False, indent=4)

    

with open('heliand-synoptic.txt', 'w') as outfile:
    for k,v in poem.items():
        line_no = str("{:04d}".format(int(k.rstrip('x'))))
        if re.search(r"\w", v['c']):
            outfile.write('C' + line_no + '  ' + v['c'] + '\nM' + line_no + '  ' + v['m'] + '\n\n')
        else:
            if 'x' in k:
                line_no = line_no + 'x'
                outfile.write('M' + line_no + ' ' + v['m'] + '\n\n')
            else:
                outfile.write('M' + line_no + '  ' + v['m'] + '\n\n')
