# This script converts the Wikisource text
# of the Heliand into JSON and plaintext.

import re,json
from mediawiki import MediaWiki
from pathlib import Path
from bs4 import BeautifulSoup

print_line_numbers = True
caesura_span = '    '
#caesura_span = '\t'

normalization = {
    'â': 'a',
    'ê': 'e',
    'î': 'i',
    'ô': 'o',
    'û': 'u',
    '[': '',
    ']': '',
    'ʽ': '',
    'ʼ': '',
    '.': '',
    ',': '',
    ':': '',
    ';': '',
    '—': '',
    '!': '',
    '?': '',
    '*': ''
}

def normalize(token):
    token = token.lower()
    for k,v in normalization.items():
        token = token.replace(k,v)
    return token

def extract():
    wikisource = MediaWiki(url='https://secure.wikimedia.org/wikisource/de/w/api.php')
    print('Loading MediaWiki remote...')
    page = wikisource.page('Heliand')
    html = page.html
    print('Parsing BeautifulSoup object...')
    soup = BeautifulSoup(html, 'html.parser')
    poem = soup.find('div', class_='poem')
    plaintext = poem.get_text().split('\n')[1:]
    
    heliand = []
    caesura = ' · '
    previous_line = ''
    for line in plaintext:
        if re.search(r'\d', line):
            if caesura in line:
                line = (line.split(' ', 1)[0], line.split(' ', 1)[1].split(caesura))
                if not(re.search(r'(\w|.)', line[1][0])):
                    data = (heliand[-1][0], previous_line[1].split(), line[1][1].split())
                    print(data)
                    heliand.pop()
                else:
                    data =(line[0], line[1][0].split(), line[1][1].rstrip().split())
            else:
                line = (line.split(' ', 1)[0], line.split(' ', 1)[1])
                data = (line[0], line[1][0].split())
            heliand.append(data)
        previous_line = line
    
    heliand_clean = dict()
    for line in heliand:
        line_no = line[0].replace('b', 'x')
        on_verse = {
            'verse': line_no + 'a',
            'tokens': [normalize(i) for i in line[1] if normalize(i) != '']
        }
        off_verse = {
            'verse': line_no + 'b',
            'tokens': [normalize(i) for i in line[2] if normalize(i) != '']
        }
        if len(on_verse['tokens']) > 1:
            # Word division in M4368:
            if on_verse['tokens'][1] == 'sodomo' and on_verse['tokens'][2] == 'land':
                on_verse['tokens'][1] = 'sodomoland'
                on_verse['tokens'].pop()
        if len(off_verse['tokens']) > 1:
            # Error in M3802:
            if off_verse['tokens'][-1] == 'uuerðeouuiht':
                off_verse['tokens'][-1] = 'uuerð'
                off_verse['tokens'].append('eouuiht')
            # Error in M5798:
            if off_verse['tokens'][-1] == 'scian' and off_verse['tokens'][-2] == 'an':
                off_verse['tokens'][-2] = 'anscian'
                off_verse['tokens'].pop()

        heliand_clean[on_verse['verse']] = on_verse['tokens']
        heliand_clean[off_verse['verse']] = off_verse['tokens']
    
    json_file_clean = 'heliand-m.json'
    if not(Path(json_file_clean).is_file()):
        print('Generating heliand-m.json...')
        with open(json_file_clean, 'w', encoding='utf-8') as outfile:
            json.dump(heliand_clean, outfile, ensure_ascii=False, indent=4)
    
    json_file_edited = 'heliand-m_behaghel.json'
    if not(Path(json_file_edited).is_file()):
        print('Generating heliand-m_behaghel.json...')
        with open(json_file_edited, 'w', encoding='utf-8') as outfile:
            json.dump(heliand, outfile, ensure_ascii=False, indent=4)
    
    plaintext_file_edited = 'heliand-m_behaghel.txt'
    if Path(plaintext_file_edited).is_file():
        print('heliand-m_behaghel.txt already in place. Skipping.')
    else:
        print('Generating heliand-m_behaghel.txt...')
        verse_lines = []
        for line in heliand:
            if print_line_numbers == True:
                if 'b' in line[0]:
                    zusatz = 'b'
                else:
                    zusatz = ' '
                line_no = str("{:04d}".format(int(line[0].rstrip('b')))) + zusatz
                reconstructed_line = line_no + ' ' + ' '.join(line[1]) + caesura_span + ' '.join(line[2])
            else:
                reconstructed_line = ' '.join(line[1]) + caesura_span + ' '.join(line[2])
            verse_lines.append(reconstructed_line)
        with open(plaintext_file_edited, 'w') as outfile:
            outfile.write('\n'.join(verse_lines))
    
    plaintext_file_clean = 'heliand-m.txt'
    if Path(plaintext_file_clean).is_file():
        print('heliand-m.txt already in place. Skipping.')
    else:
        print('Generating heliand-m.txt...')
        verse_lines = []
        for k,v in heliand_clean.items():
            if len(v) == 1 and len(v[0]) < 1:
                empty = '                   '
            else:
                empty = ''
            tokens = [token for token in v if len(v) > 0]
            if 'a' in k:
                if print_line_numbers == True:
                    if 'x' in k:
                        zusatz = 'x'
                    else:
                        zusatz = ' '
                    line_no = str("{:04d}".format(int(k.rstrip('ax')))) + zusatz + ' '
                else:
                    line_no = ''
                reconstructed_line = line_no + empty + ' '.join(tokens)
                verse_lines.append(reconstructed_line)
            else:
                verse_lines[-1] = verse_lines[-1] + caesura_span + ' '.join(tokens)
                
        with open(plaintext_file_clean, 'w') as outfile:
            outfile.write('\n'.join(verse_lines))
    
    print('Done.')

if __name__ == '__main__':
    extract()
