# This script converts the Wikisource text
# of the Heliand into JSON and plaintext.

import json
from mediawiki import MediaWiki
from pathlib import Path
from bs4 import BeautifulSoup

print_line_numbers = True
caesura_span = '    '
#caesura_span = '\t'

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
for line in plaintext:
    if caesura in line:
        line = (line.split(' ', 1)[0], line.split(' ', 1)[1].split(caesura))
        heliand.append((int(line[0].rstrip('ab')), line[1][0], line[1][1].rstrip()))

json_file = 'heliand-m.json'
if not(Path(json_file).is_file()):
    print('Generating heliand-m.json...')
    with open(json_file, 'w', encoding='utf-8') as outfile:
        json.dump(heliand, outfile, ensure_ascii=False, indent=4)

plaintext_file = 'heliand-m.txt'
if Path(plaintext_file).is_file():
    print('heliand-m.txt already present. Skipping.')
else:
    print('Generating heliand-m.txt...')
    verse_lines = []
    for line in heliand:
        if print_line_numbers == True:
            reconstructed_line = str("{:04d}".format(int(line[0]))) + ' ' + line[1] + caesura_span + line[2]
        else:
            reconstructed_line = line[1] + caesura_span + line[2]
        verse_lines.append(reconstructed_line)
    with open(plaintext_file, 'w') as outfile:
        outfile.write('\n'.join(verse_lines))

print('Done.')
