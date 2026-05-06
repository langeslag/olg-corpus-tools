# The goal is for this script to do bitext word mapping so I have easy
# access to what terms I have previously used to translate the same forms/stems.
# TODO: adjacent lines etc.

import re,json,sys,string
from collections import Counter
from pathlib import Path
import wikisource_extract
import helipad_extract
import heliand_v
import heliandlps_xpollinate

def generate():
    c_json_file = 'heliand-c.json'
    if not(Path(c_json_file).is_file()):
        helipad_extract.extract()
    
    with open(c_json_file) as c_json_data:
        c_tokens = json.load(c_json_data)
 
    m_json_file = 'heliand-m.json'
    if not(Path(m_json_file).is_file()):
        wikisource_extract.extract()
    
    with open(m_json_file) as m_json_data:
            m_tokens = json.load(m_json_data)

    with open('lemmas_inverted_corrected.json') as lemma_file:
        lemmas = json.load(lemma_file)
        forms = lemmas.keys()

    with open('heliand-lemma-list.json') as lemma_list_file:
        lemma_list = json.load(lemma_list_file)

    c_lines = dict.fromkeys(range(1,5968))
    m_lines = dict.fromkeys(range(1,5983))
    t_lines = dict.fromkeys(range(1,5983))
    for k,v in m_tokens.items():
        if k[-1] == 'a':
            m_lines[k[:-1]] = v + m_tokens[k[:-1] + 'b']
   
    if Path('heliand-translation.txt').is_file():
        print('Found heliand-translation.txt.')
        plaintext = open('heliand-translation.txt').read().splitlines()
        plaintext_no_empties = [t for t in plaintext if len(t) > 0]
        translation = [t for t in plaintext_no_empties if t[0] == 'T']
        for t in translation:
            line_ref = t.split(' ', 1)[0].lstrip('T0')
            line_content = t.split(' ', 1)[1].lstrip()
            for character in string.punctuation:
                line_content = line_content.replace(character, '')
            t_lines[line_ref] = line_content.split()
    else:
        print('heliand-translation.txt not found.')
        print('You can generate it, but you would have to write your own translation into it.')
        print('Aborting.')
        sys.exit()

    trends = dict()
    c_range = range(1,5968)
    if not(Path('lemma-line-matches.json').is_file()):
        c_line_lemmas = dict()
        for ln in c_range:
            # using strings rather than integers because I have yet to fit those 'x' lines back in:
            c_line_lemmas[str(ln)] = [token['lemma'] for token in c_tokens if token['verse'].rstrip('ab') == str(ln)]

        with open('lemma-line-matches.json', 'w', encoding='utf-8') as outfile:
            json.dump(c_line_lemmas, outfile, ensure_ascii=False, indent=4)
    else:
        with open('lemma-line-matches.json') as c_line_lemma_data:
            c_line_lemmas = json.load(c_line_lemma_data)

    for lemma in lemma_list:
        trans_terms = []
        matching_lines = [k for k,v in c_line_lemmas.items() if lemma in v]
        for line in matching_lines:
            if len(t_lines[line]) > 0:
                trans_terms.extend(t_lines[line])
        frequencies = Counter(trans_terms)
        print(f'{lemma}: {frequencies.most_common()}')

    # TODO: PICK UP HERE
    # Now add adjacent line content, assign double the frequency for matching lines, remove stop words etc.

            
    #print('Generating translation-trends.json...')
    #with open('translation-trends.json', 'w', encoding='utf-8') as outfile:
    #    json.dump(trends, outfile, ensure_ascii=False, indent=4)
    print('Done.')

if __name__ == '__main__':
    generate()
