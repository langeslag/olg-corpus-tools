# Generate a dictionary linking each form to all matching lemmas.
import json
from pathlib import Path
import heliand_xpollinate

def generate():
    c_json_file = 'heliand-c.json'
    m_json_file = 'heliand-m_rich.json'
    v_json_file = 'heliand-v_rich_corrected.json'
    if not(Path(m_json_file).is_file()):
        helipad_xpollinate.xfer()
    if not(Path(v_json_file).is_file()):
        helipad_xpollinatev.xfer()
        
    with open(c_json_file) as c_json_data:
        c_tokens = json.load(c_json_data)
       
    with open(m_json_file) as m_json_data:
            m_tokens = json.load(m_json_data)
        
    with open(v_json_file) as v_json_data:
            v_tokens = json.load(v_json_data)
        
    forms = sorted(list(set([c['form'] for c in c_tokens if len(c['form']) > 0] + [m['form'] for m in m_tokens if len(m['form']) > 0] + [v['form'] for v in v_tokens if len(v['form']) > 0])))
    data = dict.fromkeys(forms, [])
    forms_without_lemmas = []
    for k,v in data.items():
        lemmas_c = [c['lemma'] for c in c_tokens if c['form'] == k]
        lemmas_m = [m['lemma'] for m in m_tokens if m['form'] == k]
        lemmas_v = [v['lemma'] for v in v_tokens if v['form'] == k]
        lemmas = list(set(lemmas_c + lemmas_m + lemmas_v))
        if len(lemmas) == 0:
            forms_without_lemmas.append(k)
        #else:
        #    lemmas = sorted(lemmas)
        data[k] = lemmas

    print('Generating heliand-lemmas_inverted.json...')
    with open('heliand-lemmas_inverted.json', 'w', encoding='utf-8') as outfile:
        json.dump(data, outfile, ensure_ascii=False, indent=4)
    print('Done.')
    
if __name__ == '__main__':
    generate()
