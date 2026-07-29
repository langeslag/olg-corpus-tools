# This script extracts what translation from the Vulgate exists in heliand-translation.txt
# and stores it as vulgate-trans.json so it can be processed e.g. by typeset*py.
# TODO: stop the script from loading each verse into EACH gospel dict
# TODO: make sure all verse duplication is now gone from the json

import re,json
from pathlib import Path
from natsort import natsorted

outfile = Path('vulgate-trans.json')

sources = [
        'Mt',
        'Mc',
        'Lc',
        'Io',
        '1Th'
        ]

translations = dict.fromkeys(sources, {})

with open('heliand-translation.txt') as f:
    plaintext = f.read().splitlines()

gospel_index = dict()
gospel_index_file = Path('gospel-index.tsv')
if gospel_index_file.is_file():
    with open(gospel_index_file) as gospel_data:
        gospel_index_raw = gospel_data.read().splitlines()
        gospel_index = dict()
        for line in gospel_index_raw:
            rubble = re.split(r"\t+", line, maxsplit=1)
            if len(rubble) == 1:
                gospel_index[rubble[0]] = None
            else:
                gospel_index[rubble[0]] = rubble[1]

plaintext_no_empties = [t for t in plaintext if len(t) > 0]
source_translation = [t for t in plaintext_no_empties if t[0] == 'X']

source_trans_dict = dict()
for line in source_translation:
    rubble = re.split(r'\s+', line, maxsplit=1)
    if re.search(r"\S+", rubble[1]):
        source_trans_dict[rubble[0][1:].lstrip('0')] = rubble[1]

line_range = dict.fromkeys([str(t) for t in range(1,4518)] + ['4517x'] + [str(t) for t in range(4518,5921)] + ['5920x'] + [str(t) for t in range(5921,5984)])

def generate():
    for line_no in line_range:
        ref_counter = 0
        catch = []
        if line_no in source_trans_dict:
            for i in 'ab':
                if gospel_index[line_no + i] is not None:
                    if re.search(r"\S+", gospel_index[line_no + i]):
                        catch.extend(gospel_index[line_no + i].split(','))
            catch = list(set([x.replace('*', '') for x in catch if x[0] != '(']))
            for ref in catch:
                bk, verse = ref.split()
                if verse not in translations[bk]:
                    if re.search(r"\S+", source_trans_dict[line_no]):
                        translations_list = source_trans_dict[line_no].split(' || ')
                        translations[bk][verse] = translations_list[ref_counter]
                ref_counter += 1

    for k,v in translations.items():
        translations[k] = dict(natsorted(v.items()))

    with open(outfile, 'w') as f:
        json.dump(translations, f, ensure_ascii=False, indent=4)
                
if __name__ == '__main__':
    generate()
