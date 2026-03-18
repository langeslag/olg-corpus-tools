# Transfers POS and lemma metadata from Sievers to Zangemeister--Braune (V)
# where the corresponding or adjacent token, or its lemma, is similar in form.
import json
from pathlib import Path
from Levenshtein import distance
from prettytable import PrettyTable
import heliand_v
import helipad_extract

def xfer():
    target = 'heliand-v_rich.json'
    if Path(target).is_file():
        print('heliand-m_rich.json already present. Skipping.')
    else:
        c_json_file = 'heliand-c.json'
        if not(Path(c_json_file).is_file()):
            helipad_extract.extract()
        
        with open(c_json_file) as c_json_data:
            c_tokens = json.load(c_json_data)
            
        v_json_file = 'heliand-v.json'
        
        with open(v_json_file) as v_json_data:
                v_verses = json.load(v_json_data)
        
        v_data = []
        mismatches = []
        for verse,tokens in v_verses.items():
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
                        if distance(token, c_verse[idx]['form']) > 2:
                            mismatch = {
                                    'verse': verse,
                                    'm_form': token,
                                    'c_form': c_verse[idx]['form'],
                                    'lemma': c_verse[idx]['lemma']
                                    }
                            mismatches.append(mismatch)
                        token_data['lemma'] = c_verse[idx]['lemma']
                        token_data['pos'] = c_verse[idx]['pos']
                    if token_data['lemma'] is None and idx > 0:
                        if distance(token, c_verse[idx-1]['form']) < 4 or distance(token, c_verse[idx-1]['lemma']) < 4:
                            if distance(token, c_verse[idx]['form']) > 2:
                                mismatch = {
                                    'verse': verse,
                                    'm_form': token,
                                    'c_form': c_verse[idx-1]['form'],
                                    'lemma': c_verse[idx-1]['lemma']
                                    }
                            mismatches.append(mismatch)
                            token_data['lemma'] = c_verse[idx-1]['lemma']
                            token_data['pos'] = c_verse[idx-1]['pos']
                    if token_data['lemma'] is None and len(c_verse) - idx > 1:
                        if distance(token, c_verse[idx+1]['form']) < 4 or distance(token, c_verse[idx+1]['lemma']) < 4:
                            if distance(token, c_verse[idx]['form']) > 2:
                                mismatch = {
                                    'verse': verse,
                                    'm_form': token,
                                    'c_form': c_verse[idx+1]['form'],
                                    'lemma': c_verse[idx+1]['lemma']
                                    }
                                mismatches.append(mismatch)
                            token_data['lemma'] = c_verse[idx+1]['lemma']
                            token_data['pos'] = c_verse[idx+1]['pos']
                v_data.append(token_data)
    
        print('Printing edge cases to _proofreadv.txt for inspection...')
        table = PrettyTable()
        table.align = 'l'
        table.field_names = ['Verse', 'C Form', 'V Form', 'Lemma']
        for row in mismatches:
            table.add_row([row['verse'], row['c_form'], row['m_form'], row['lemma']])
        table_string = table.get_string()
        with open('_proofreadv.txt', 'w') as inspect_file:
            inspect_file.write(table_string)
        print('Generating heliand-v_rich.json...')
        with open('heliand-v_rich.json', 'w', encoding='utf-8') as outfile:
            json.dump(v_data, outfile, ensure_ascii=False, indent=4)
        print('Done.')
    
if __name__ == '__main__':
    xfer()
