# This script engages in a crude form of bitext word mapping so I have easy
# access to what terms I have previously used to translate the same lemmas.
# TODO: further weight the scores by relative token index
# TODO: make the frequency/score cutoff dependent on the length of the list
# TODO: add those last lines from M where C doesn't have them
# TODO: add lines ending in x
# TODO: allow MnE queries and return OS equivalents

import re,json,sys,argparse,time
from pathlib import Path
from collections import Counter
from nltk import download
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from prettytable import PrettyTable
#import wikisource_extract
import helipad_extract

start = time.time()

# Uncomment for first run:
#download('wordnet', quiet=True)    
#download('omw-1.4', quiet=True) 
#download('averaged_perceptron_tagger_eng', quiet=True)

argparser = argparse.ArgumentParser()
argparser.add_argument("query", nargs='+')
argparser.add_argument("-f", "--fresh", action="store_true", help="refresh the database")
args = argparser.parse_args()
query = args.query
refresh = args.fresh

lemma_line_matches = Path('lemma-line-matches.json')
translation_trends = Path('translation-trends.json')

with open('lemmas_inverted_corrected.json') as lemma_file:
    lemmas = json.load(lemma_file)

if refresh:
    print('Purging databases...')
    if lemma_line_matches.is_file():
        lemma_line_matches.unlink()
    if translation_trends.is_file():
        translation_trends.unlink()

def generate():
    c_range = range(1,5969)
    t_range = range(1,5984)
    c_lines = dict.fromkeys(c_range)
    t_lines = dict.fromkeys(t_range)
   
    trends = dict()
    translated_lines = 0
    if not(lemma_line_matches.is_file()):
        if Path('heliand-translation.txt').is_file():
            print('Lemmatizing translated tokens...')
            lemmatizer = WordNetLemmatizer()
            plaintext = open('heliand-translation.txt').read().splitlines()
            plaintext_no_empties = [t for t in plaintext if len(t) > 0]
            translation = [t for t in plaintext_no_empties if t[0] == 'T']
            for t in translation:
                line_ref = t.split(' ', 1)[0].lstrip('T0')
                line_content = t.split(' ', 1)[1].lstrip().lower()
                for character in """.,:;'"?!–""":
                    line_content = line_content.replace(character, '')
                t_tokens = line_content.split()
                if len(t_tokens) > 0:
                    translated_lines += 1
                t_lemmas = [lemmatizer.lemmatize(token) for token in t_tokens]
                t_lines[line_ref] = t_lemmas
            print(f'{translated_lines} lines of translation found ({round(((translated_lines / len(t_range)) * 100), 2)}% complete)')
        else:
            print('heliand-translation.txt not found.')
            print('You can generate it, but you would have to write your own translation into it.')
            print('Aborting.')
            sys.exit()

        print('Generating lemma-line-matches.json...')
        c_json_file = 'heliand-c.json'
        if not(Path(c_json_file).is_file()):
            helipad_extract.extract()
    
        with open(c_json_file) as c_json_data:
            c_tokens = json.load(c_json_data)

        c_line_lemmas = dict()
        for ln in c_range:
            # using strings rather than integers because I have yet to fit those 'x' lines back in:
            c_line_lemmas[str(ln)] = [token['lemma'] for token in c_tokens if token['verse'].rstrip('ab') == str(ln)]

        with open('lemma-line-matches.json', 'w', encoding='utf-8') as outfile:
            json.dump(c_line_lemmas, outfile, ensure_ascii=False, indent=4)
    else:
        with open('lemma-line-matches.json') as c_line_lemma_data:
            c_line_lemmas = json.load(c_line_lemma_data)

    if not(translation_trends.is_file()):
        stops = stopwords.words('english')
        stops.extend(
            [
                'according',
                'go',
                'well',
                'would'
            ])
        with open('heliand-lemma-list.json') as lemma_list_file:
            lemma_list = json.load(lemma_list_file)
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
    results = dict()
    if query in trends:
        results[query] = trends[query]
    elif query in lemmas:
        headwords = lemmas[query]
        for headword in headwords:
            if headword in trends:
                results[headword] = trends[headword]
    return results

if __name__ == '__main__':
    trends = generate()
    for subquery in query:
        matches = retrieve(subquery)
        if matches is None:
            print(f'No returns for "{subquery}"')
        else:
            for lemma,match in matches.items():
                if len(match) > 0:
                    terms = [i[0] for i in match]
                    counts = [i[1] for i in match]
                    table = PrettyTable()
                    table.add_column('Near OS "' + lemma + '"', terms)
                    table.add_column('Score', counts)
                    table.align = 'l'
                    print(table)

    end = time.time()
    print(f'Execution time {round(end-start, 2)} seconds.')
