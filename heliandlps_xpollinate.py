# This script normalizes the L, P, and S plaintext transcriptions,
# stores them as plaintext and JSON, then transfers lemma and POS
# metadata from HeliPaD to additional, "rich" JSON files.
import json,re
from pathlib import Path
from Levenshtein import distance
from prettytable import PrettyTable
import helipad_extract

print_line_numbers = True
caesura_span = '    '
#caesura_span = '\t'

normalization = {
    'á': 'a',
    'é': 'e',
    'í': 'i',
    'ó': 'o',
    'ú': 'u',
    'ū': 'un',
    'ā': 'am',
    '.': '',
    ' ·': '',
    '·': '',
    ',': '',
    ';': '',
    '[': '',
    ']': ''
#    '\\': '',
#    '/': ''
}

def normalize(token):
    token = token.lower()
    for k,v in normalization.items():
        token = token.replace(k,v)
    return token

def xfer(witness):
    plaintext_infile = f"heliand-{witness}_raw.txt"
    plaintext_outfile = f"heliand-{witness}.txt"
    json_outfile_raw = f"heliand-{witness}.json"
    json_outfile_rich = f"heliand-{witness}_rich.json"
    mismatchfile = f"_proofread-{witness}.txt"

    with open(plaintext_infile) as infile:
        lines = infile.read().splitlines()

    c_json_file = 'heliand-c.json'
    if not(Path(c_json_file).is_file()):
        helipad_extract.extract()
        
    with open(c_json_file) as c_json_data:
        c_tokens = json.load(c_json_data)

    heliand = dict()
    caesura = '   '
    for line in lines:
        stripped = line.split(' ', 1)
        number = stripped[0]
        if caesura in stripped[1]:
            onverse = stripped[1].split(caesura)[0]
            offverse = stripped[1].split(caesura)[1]
            onverse_tokens = normalize(onverse).split()
            offverse_tokens = normalize(offverse).split()
            heliand[number + 'a'] = onverse_tokens
            heliand[number + 'b'] = offverse_tokens
        else:
            onverse = stripped[1]
            onverse_tokens = normalize(onverse).split()
            heliand[number + 'a'] = onverse_tokens

    print(f'Generating {plaintext_outfile}...')
    verse_lines = []
    for k,v in heliand.items():
        tokens = [token for token in v if len(v) > 0]
        text_string = ' '.join(tokens)
        if 'a' in k:
            if print_line_numbers == True:
                line_no = k.rstrip('a') + ' '
            else:
                line_no = ''
            if not(re.search(r'\w', text_string)):
                reconstructed_line = line_no + '                    '
            else:
                reconstructed_line = line_no + text_string
            verse_lines.append(reconstructed_line)
        else:
            verse_lines[-1] = verse_lines[-1] + caesura_span + text_string
            
    with open(plaintext_outfile, 'w') as outfile:
        outfile.write('\n'.join(verse_lines))

    heliand_stripped_numbers = dict()
    for k,v in heliand.items():
        stripped_number = k.lstrip('0')
        heliand_stripped_numbers[stripped_number] = v
    
    print(f'Generating {json_outfile_raw}...')
    with open(json_outfile_raw, 'w', encoding='utf-8') as outfile:
        json.dump(heliand_stripped_numbers, outfile, ensure_ascii=False, indent=4)

    # Moving on to xfer operation:           
    data = []
    mismatches = []
    for verse,tokens in heliand_stripped_numbers.items():
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
                                'form': token,
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
                                'form': token,
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
                                'form': token,
                                'c_form': c_verse[idx+1]['form'],
                                'lemma': c_verse[idx+1]['lemma']
                                }
                            mismatches.append(mismatch)
                        token_data['lemma'] = c_verse[idx+1]['lemma']
                        token_data['pos'] = c_verse[idx+1]['pos']
            data.append(token_data)

    print(f'Printing edge cases to {mismatchfile} for inspection...')
    table = PrettyTable()
    table.align = 'l'
    table.field_names = ['Verse', 'C Form', f'{witness} Form', 'Lemma']
    for row in mismatches:
        table.add_row([row['verse'], row['c_form'], row['form'], row['lemma']])
    table_string = table.get_string()
    with open(mismatchfile, 'w') as inspect_file:
        inspect_file.write(table_string)
    print(f'Generating {json_outfile_rich}...')
    with open(json_outfile_rich, 'w', encoding='utf-8') as outfile:
        json.dump(data, outfile, ensure_ascii=False, indent=4)
    print('Done.')
    
if __name__ == '__main__':
    xfer('l')
    xfer('p')
    xfer('s')
