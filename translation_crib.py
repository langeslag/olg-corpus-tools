# This file largely duplicates heliand_synoptic.py, except it outputs
# heliand-translation.txt with a line for translation. If the output file is
# present, it updates the readings but leaves the translation lines untouched.
# TODO: substitute the unnormalized Behaghel text, with length marks?

import re,json
from pathlib import Path
import wikisource_extract
import helipad_extract
import heliand_v
import heliandlps_xpollinate

lps = dict()
for witness in ['l', 'p', 's']:
    json_file = f"heliand-{witness}.json"
    if not(Path(json_file).is_file()):
        heliandlps_xpollinate.xfer(witness)

    with open(json_file) as json_data:
        tokens = json.load(json_data)
    
    lps[witness] = tokens

def generate():
    def lps_reconstruct(witness, line_no):
        on_verse_ref = line_no + 'a'
        off_verse_ref = line_no + 'b'
        if on_verse_ref in lps[witness].keys():
            if re.search(r"\w", ''.join(lps[witness][on_verse_ref])):
                a = ' '.join(lps[witness][on_verse_ref])
            else:
                a = '                   '
            if off_verse_ref in lps[witness].keys():
                b = ' '.join(lps[witness][off_verse_ref])
                line = '    '.join([a, b])
            else:
                line = a
        else:
            line = None
        return line

    def reconstruct(line_no):
        on_verse_ref = line_no + 'a'
        off_verse_ref = line_no + 'b'
        c_a = ' '.join([token['form'] for token in c_tokens if token['verse'] == str(line_no)+'a'])
        c_b = ' '.join([token['form'] for token in c_tokens if token['verse'] == str(line_no)+'b'])
        if re.search(r"\w", c_a):
            c = '    '.join([c_a, c_b])
        else:
            c = None
        if on_verse_ref in m_tokens.keys():
            if re.search(r"\w", ''.join(m_tokens[on_verse_ref])):
                m_a = ' '.join(m_tokens[on_verse_ref])
            else:
                m_a = '                   '
            m_b = ' '.join(m_tokens[off_verse_ref])
            m = '     '.join([m_a, m_b])
        else:
            m = ''
        if on_verse_ref in v_tokens.keys():
            v_a = ' '.join(v_tokens[on_verse_ref])
            if off_verse_ref in v_tokens.keys():
                v_b = ' '.join(v_tokens[off_verse_ref])
                v = '    '.join([v_a, v_b])
            else:
                v = v_a
        else:
            v = None
        l = lps_reconstruct('l', line_no)
        p = lps_reconstruct('p', line_no)
        s = lps_reconstruct('s', line_no)

        result = {
            'c': c,
            'm': m,
            'l': l,
            'p': p,
            's': s,
            'v': v
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

    v_json_file = 'heliand-v.json'
    if not(Path(v_json_file).is_file()):
        heliand_v.extract()
    
    with open(v_json_file) as v_json_data:
            v_tokens = json.load(v_json_data)
    
    poem = dict()
    x = [4517, 5920]
    for i in range(1, 5983):
        poem[str(i)] = reconstruct(str(i))
        if i in x:
            xline = str(i) + 'x'
            poem[xline] = reconstruct(xline)
    
    print('Generating heliand-synoptic.json...')
    with open('heliand-synoptic.json', 'w', encoding='utf-8') as outfile:
        json.dump(poem, outfile, ensure_ascii=False, indent=4)

    for i in range(1, 5983):
        poem[str(i)]['t'] = ''
        if i in x:
            xline = str(i) + 'x'
            poem[xline]['t'] = ''
    
    if Path('heliand-translation.txt').is_file():
        print('heliand-translation.txt exists; updating readings only!')
        plaintext = open('heliand-translation.txt').read().splitlines()
        plaintext_no_empties = [t for t in plaintext if len(t) > 0]
        translation = [t for t in plaintext_no_empties if t[0] == 'T']
        for t in translation:
            line_ref = t.split(' ', 1)[0].lstrip('T0')
            line_content = t.split(' ', 1)[1].lstrip()
            poem[line_ref]['t'] = line_content
            
    print('Generating heliand-translation.txt...')
    with open('heliand-translation.txt', 'w') as outfile:
        for k,v in poem.items():
            line_no = str("{:04d}".format(int(k.rstrip('x'))))
            for witness in v.keys():
                line = v[witness]
                if line is not None:
                    if 'x' in k:
                        outfile.write(witness.upper() + line_no + ' ' + line + '\n')
                    else:
                        outfile.write(witness.upper() + line_no + '  ' + line + '\n')
            outfile.write('\n')
    print('Done.')

if __name__ == '__main__':
    generate()
