# Generates synoptic heliand_synoptic.json and heliand_synoptic.txt.
import re,json
from pathlib import Path
import wikisource_extract
import helipad_extract
import heliand_v

def generate():
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
        result = {
            'c': c,
            'm': m,
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
    
    print('Generating heliand-synoptic.txt...')
    with open('heliand-synoptic.txt', 'w') as outfile:
        for k,v in poem.items():
            line_no = str("{:04d}".format(int(k.rstrip('x'))))
            if v['c'] is not None:
                if v['v'] is not None:
                    outfile.write('C' + line_no + '  ' + v['c'] + '\nM' + line_no + '  ' + v['m'] + '\nV' + line_no + '  ' + v['v'] + '\n\n')
                else:
                    outfile.write('C' + line_no + '  ' + v['c'] + '\nM' + line_no + '  ' + v['m'] + '\n\n')
            else:
                if 'x' in k:
                    line_no = line_no + 'x'
                    outfile.write('M' + line_no + ' ' + v['m'] + '\n\n')
                else:
                    outfile.write('M' + line_no + '  ' + v['m'] + '\n\n')
    print('Done.')

if __name__ == '__main__':
    generate()
