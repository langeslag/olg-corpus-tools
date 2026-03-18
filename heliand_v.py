# This script converts the plaintext transcription of Heliand V
# based on Zangemeister and Braune into unlemmatized JSON data.

import json
from pathlib import Path

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
    '.': '',
    ',': '',
    ';': ''
}

def normalize(token):
    token = token.lower()
    for k,v in normalization.items():
        token = token.replace(k,v)
    return token

def extract():
    with open('heliand-v_zangemeister.txt') as infile:
        lines = infile.read().splitlines()

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

    plaintext_file = 'heliand-v.txt'
    print('Generating heliand-v.txt...')
    verse_lines = []
    for k,v in heliand.items():
        tokens = [token for token in v if len(v) > 0]
        if 'a' in k:
            if print_line_numbers == True:
                line_no = k.rstrip('a') + ' '
            else:
                line_no = ''
            reconstructed_line = line_no + ' '.join(tokens)
            verse_lines.append(reconstructed_line)
        else:
            verse_lines[-1] = verse_lines[-1] + caesura_span + ' '.join(tokens)
            
    with open(plaintext_file, 'w') as outfile:
        outfile.write('\n'.join(verse_lines))
    
    json_file = 'heliand-v.json'
    print('Generating heliand-v.json...')
    with open(json_file, 'w', encoding='utf-8') as outfile:
        json.dump(heliand, outfile, ensure_ascii=False, indent=4)

    print('Done.')

if __name__ == '__main__':
    extract()
