# Transfers POS and lemma metadata from Sievers to Behaghel
# where the corresponding or adjacent token, or its lemma, is similar in form.
import json
from pathlib import Path
from Levenshtein import distance
import wikisource_extract
import helipad_extract

def xfer():
    target = 'heliand-m_rich.json'
    if Path(target).is_file():
        print('heliand-m_rich.json already present. Skipping.')
    else:
        c_json_file = 'heliand-c.json'
        if not(Path(c_json_file).is_file()):
            helipad_extract.extract()
        
        with open(c_json_file) as c_json_data:
            c_tokens = json.load(c_json_data)
            
        m_json_file = 'heliand-m.json'
        if not(Path(m_json_file).is_file()):
            wikisource_extract.extract()
        
        with open(m_json_file) as m_json_data:
                m_verses = json.load(m_json_data)
        
        m_data = []
        for verse,tokens in m_verses.items():
            c_verse = [token for token in c_tokens if token['verse'] == verse]
            for idx,token in enumerate(tokens):
                token_data = dict.fromkeys(['verse', 'form', 'lemma', 'pos'])
                token_data['verse'] = verse
                token_data['form'] = token
                if len(c_verse) > idx:
                    if c_verse[idx]['form'] == token or c_verse[idx]['lemma'] == token:
                        token_data['lemma'] = c_verse[idx]['lemma']
                        token_data['pos'] = c_verse[idx]['pos']
                    if token_data['lemma'] is None and idx > 0:
                        if c_verse[idx-1]['form'] == token or c_verse[idx-1]['lemma'] == token:
                            token_data['lemma'] = c_verse[idx-1]['lemma']
                            token_data['pos'] = c_verse[idx-1]['pos']
                    if token_data['lemma'] is None and len(c_verse) - idx > 1:
                        if c_verse[idx+1]['form'] == token or c_verse[idx+1]['lemma'] == token:
                            token_data['lemma'] = c_verse[idx+1]['lemma']
                            token_data['pos'] = c_verse[idx+1]['pos']
                    if token_data['lemma'] is None and distance(token, c_verse[idx]['form']) < 4 or distance(token, c_verse[idx]['lemma']) < 4:
                        token_data['lemma'] = c_verse[idx]['lemma']
                        token_data['pos'] = c_verse[idx]['pos']
                    if token_data['lemma'] is None and idx > 0:
                        if distance(token, c_verse[idx-1]['form']) < 4 or distance(token, c_verse[idx-1]['lemma']) < 4:
                            token_data['lemma'] = c_verse[idx-1]['lemma']
                            token_data['pos'] = c_verse[idx-1]['pos']
                    if token_data['lemma'] is None and len(c_verse) - idx > 1:
                        if distance(token, c_verse[idx+1]['form']) < 4 or distance(token, c_verse[idx+1]['lemma']) < 4:
                            token_data['lemma'] = c_verse[idx+1]['lemma']
                            token_data['pos'] = c_verse[idx+1]['pos']
                m_data.append(token_data)
    
        print('Generating heliand-m_rich.json...')
        with open('heliand-m_rich.json', 'w', encoding='utf-8') as outfile:
            json.dump(m_data, outfile, ensure_ascii=False, indent=4)
        print('Done.')
    
if __name__ == '__main__':
    xfer()
