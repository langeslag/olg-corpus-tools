# This script engages in a rough form of bitext word mapping so I have easy
# access to what terms I have previously used to translate the same lemmas.
# TODO: further weight the scores by relative token index

import re,json,sys,string,argparse
from pathlib import Path
from collections import Counter
from nltk.corpus import stopwords
from prettytable import PrettyTable
import wikisource_extract
import helipad_extract
import heliand_v
import heliandlps_xpollinate

argparser = argparse.ArgumentParser()
argparser.add_argument("query", nargs='+')
args = argparser.parse_args()
query = args.query

stops = stopwords.words('english')

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
    #m_lines = dict.fromkeys(range(1,5983))
    t_lines = dict.fromkeys(range(1,5983))
    #for k,v in m_tokens.items():
    #    if k[-1] == 'a':
    #        m_lines[k[:-1]] = v + m_tokens[k[:-1] + 'b']
   
    if Path('heliand-translation.txt').is_file():
        plaintext = open('heliand-translation.txt').read().splitlines()
        plaintext_no_empties = [t for t in plaintext if len(t) > 0]
        translation = [t for t in plaintext_no_empties if t[0] == 'T']
        for t in translation:
            line_ref = t.split(' ', 1)[0].lstrip('T0')
            line_content = t.split(' ', 1)[1].lstrip().lower()
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
        print('Generating lemma-line-matches.json...')
        c_line_lemmas = dict()
        for ln in c_range:
            # using strings rather than integers because I have yet to fit those 'x' lines back in:
            c_line_lemmas[str(ln)] = [token['lemma'] for token in c_tokens if token['verse'].rstrip('ab') == str(ln)]

        with open('lemma-line-matches.json', 'w', encoding='utf-8') as outfile:
            json.dump(c_line_lemmas, outfile, ensure_ascii=False, indent=4)
    else:
        with open('lemma-line-matches.json') as c_line_lemma_data:
            c_line_lemmas = json.load(c_line_lemma_data)

    if not(Path('translation-trends.json').is_file()):
        for lemma in lemma_list:
            trans_terms = []
            matching_lines = [k for k,v in c_line_lemmas.items() if lemma in v]
            for line in matching_lines:
                if len(t_lines[line]) > 0:
                    trans_terms.extend(t_lines[line])
                    # repeating that action so exact line matches count twice as much as matches in adjacent lines:
                    trans_terms.extend(t_lines[line])
                # this bit will stop working once I reinsert 'x' lines:
                if str(int(line)-1) in t_lines:
                    if t_lines[str(int(line)-1)] is not None:
                        if len(t_lines[str(int(line)-1)]) > 0:
                            trans_terms.extend(t_lines[str(int(line)-1)])
                if str(int(line)+1) in t_lines:
                    if t_lines[str(int(line)+1)] is not None:
                        if len(t_lines[str(int(line)+1)]) > 0:
                            trans_terms.extend(t_lines[str(int(line)+1)])
            trans_terms_stopped = [i for i in trans_terms if not i in stops]
            frequencies = Counter(trans_terms_stopped)
            # Setting the minimum score for inclusion here:
            trends[lemma] = [(k,v) for k,v in frequencies.most_common() if v > 3]

        print('Generating translation-trends.json...')
        with open('translation-trends.json', 'w', encoding='utf-8') as outfile:
            json.dump(trends, outfile, ensure_ascii=False, indent=4)

    else:
        with open('translation-trends.json') as trends_data:
            trends = json.load(trends_data)
    return trends

def retrieve(query):
    if query in trends:
        return trends[query]

if __name__ == '__main__':
    trends = generate()
    for subquery in query:
        matches = retrieve(subquery)
        # Best set the cutoff point in the function above?
        terms = [i[0] for i in matches]# if i[1] > 1]
        counts = [i[1] for i in matches]# if i[1] > 1]
        table = PrettyTable()
        table.add_column('Near OS "' + subquery + '"', terms)
        table.add_column('Score', counts)
        table.align = 'l'
        print(table)
        #print(matches)
