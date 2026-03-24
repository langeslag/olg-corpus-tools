# Generate a dictionary linking each form to all matching lemmas.
import json
from pathlib import Path
import heliand_xpollinate
import heliandv_xpollinate

def generate():
    c_json_file = 'heliand-c.json'
    m_json_file = 'heliand-m_rich.json'
    v_json_file = 'heliand-v_rich.json'
    if not(Path(m_json_file).is_file()):
        helipad_xpollinate.xfer()
        
    with open(c_json_file) as c_json_data:
        c_tokens = json.load(c_json_data)
       
    with open(m_json_file) as m_json_data:
        m_tokens = json.load(m_json_data)
        
    with open(v_json_file) as v_json_data:
        v_tokens = json.load(v_json_data)

    lemmas = sorted(list(set([c['lemma'] for c in c_tokens if len(c['lemma']) > 0] + [m['lemma'] for m in m_tokens if m['lemma'] is not None] + [v['lemma'] for v in v_tokens if len(v['lemma']) > 0])))

    print('Generating heliand-lemma-list.json...')
    with open('heliand-lemma-list.json', 'w', encoding='utf-8') as outfile:
        json.dump(lemmas, outfile, ensure_ascii=False, indent=4)
    print('Generating heliand-lemma-list.txt...')
    with open('heliand-lemma-list.txt', 'w') as outfile:
        outfile.write('\n'.join(lemmas))
    print('Done.')
    
if __name__ == '__main__':
    generate()
