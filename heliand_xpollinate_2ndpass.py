# Transfers POS and lemma metadata from Sievers to Behaghel
# where the corresponding or adjacent token, or its lemma, is similar in form.
import json
from pathlib import Path
from Levenshtein import distance
from prettytable import PrettyTable
import wikisource_extract
import helipad_extract
import lemma2pos

def xfer():
    target = 'heliand-m_rich_2ndpass.json'
    if Path(target).is_file():
        print('heliand-m_rich_2ndpass.json already present. Skipping.')
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

        firstpass_file = 'heliand-m_rich.json'
        with open(firstpass_file) as firstpass_json_data:
                firstpass = json.load(firstpass_json_data)
        
        corrections_file = 'lemmas_inverted_corrected.json'
        with open(corrections_file) as corrections_json_data:
                approved = json.load(corrections_json_data)

        pos_file = 'heliand-c_pos.json'
        if not(Path(pos_file).is_file()):
            lemma2pos.generate()

        with open(pos_file) as pos_data:
                c_pos = json.load(pos_data)
        
        m_2ndpass = []
        mismatches = []
        for verse,tokens in m_verses.items():
            c_verse = [token for token in c_tokens if token['verse'] == verse]
            for idx,token in enumerate(tokens):
                token_data = dict.fromkeys(['verse', 'form', 'lemma', 'pos'])
                token_data['verse'] = verse
                token_data['form'] = token
                if len(approved[token]) == 1:
                    lemma = approved[token][0]
                    token_data['lemma'] = lemma
                    if lemma in c_pos.keys():
                        if len(c_pos[lemma]) == 1:
                            token_data['pos'] = c_pos[lemma][0]
                        else:
                            base_labels = list(set([i.split('^')[0] for i in c_pos[lemma]]))
                            if len(base_labels) == 1:
                                token_data['pos'] = base_labels[0]
                # I am resisting an elif here, just because verse-specific data may be better esp. for POS:
                if len(c_verse) > idx:
                    if c_verse[idx]['form'] == token or c_verse[idx]['lemma'] in [v for k,v in approved.items() if k == token][0]:
                        token_data['lemma'] = c_verse[idx]['lemma']
                        token_data['pos'] = c_verse[idx]['pos']
                    if token_data['lemma'] is None and idx > 0:
                        if c_verse[idx-1]['form'] == token or c_verse[idx-1]['lemma'] in [v for k,v in approved.items() if k == token][0]:
                            token_data['lemma'] = c_verse[idx-1]['lemma']
                            token_data['pos'] = c_verse[idx-1]['pos']
                    if token_data['lemma'] is None and len(c_verse) - idx > 1:
                        if c_verse[idx+1]['form'] == token or c_verse[idx+1]['lemma'] in [v for k,v in approved.items() if k == token][0]:
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
                        # Disabling Levenshtein assignments for the time being:
                        #token_data['lemma'] = c_verse[idx]['lemma']
                        #token_data['pos'] = c_verse[idx]['pos']
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
                            #token_data['lemma'] = c_verse[idx-1]['lemma']
                            #token_data['pos'] = c_verse[idx-1]['pos']
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
                            #token_data['lemma'] = c_verse[idx+1]['lemma']
                            #token_data['pos'] = c_verse[idx+1]['pos']
                m_2ndpass.append(token_data)
    
        print('Printing edge cases to _proofread_2ndpass.txt for inspection...')
        table = PrettyTable()
        table.align = 'l'
        table.field_names = ['Verse', 'C Form', 'M Form', 'Lemma']
        for row in mismatches:
            table.add_row([row['verse'], row['c_form'], row['m_form'], row['lemma']])
        table_string = table.get_string()
        with open('_proofread_2ndpass.txt', 'w') as inspect_file:
            inspect_file.write(table_string)
        print('Generating heliand-m_rich_2ndpass.json...')
        with open('heliand-m_rich_2ndpass.json', 'w', encoding='utf-8') as outfile:
            json.dump(m_2ndpass, outfile, ensure_ascii=False, indent=4)
        print('Done.')
    
if __name__ == '__main__':
    xfer()
