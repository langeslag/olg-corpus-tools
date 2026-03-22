# Generates selective synoptic verses for quicker review
# of halflines with different token counts.
# Mostly so I can review which word pairs to merge.
import re,json
from pathlib import Path
import wikisource_extract
import helipad_extract

def generate():
    c_json_file = 'heliand-c.json'
    if not(Path(c_json_file).is_file()):
        helipad_extract.extract()
    
    with open(c_json_file) as c_json_data:
        c_tokens = json.load(c_json_data)
        
    m_json_file = 'heliand-m_rich.json'
    if not(Path(m_json_file).is_file()):
        wikisource_extract.extract()
    
    with open(m_json_file) as m_json_data:
        m_tokens = json.load(m_json_data)
    
    uneven_verses = dict()
    for line_no in range(1, 5968):
        on_verse_ref = str(line_no) + 'a'
        off_verse_ref = str(line_no) + 'b'
        c_a = [token['form'] for token in c_tokens if token['verse'] == on_verse_ref and token['form'] != '']
        c_b = [token['form'] for token in c_tokens if token['verse'] == off_verse_ref and token['form'] != '']
        m_a = [token['form'] for token in m_tokens if token['verse'] == on_verse_ref and token['form'] != '']
        m_b = [token['form'] for token in m_tokens if token['verse'] == off_verse_ref and token['form'] != '']
        if len(c_a) != len(m_a):
            uneven_verses[on_verse_ref] = {'c': ' '.join(c_a), 'm': ' '.join(m_a)}
        if len(c_b) != len(m_b):
            uneven_verses[on_verse_ref] = {'c': ' '.join(c_b), 'm': ' '.join(m_b)}

    print('Generating verses-of-different-length.txt...')
    with open('verses-of-different-length.txt', 'w') as outfile:
        for k,v in uneven_verses.items():
            suffix = k[-1]
            verse = str("{:04d}".format(int(k[:-1]))) + suffix
            outfile.write('M' + verse + ' ' + v['m'] + '\n' + 'C' + verse + ' ' + v['c'] + '\n\n')
        print('Done.')

if __name__ == '__main__':
    generate()
