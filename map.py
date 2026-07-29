# This script engages in a crude form of bitext word mapping so I have easy
# access to what terms I have previously used to translate the same lemmas.
# TODO: build a second pass within generate() selecting (or boosting)
# from each translated line the token that scores the highest in the first
# pass (i.e. in `trends`).
# TODO: make the frequency/score cutoff dependent on the length of the list
# TODO: add those last lines from M where C doesn't have them
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
trends_2ndpass = Path('trends-2ndpass.json')

with open('lemmas_inverted_corrected.json') as lemma_file:
    lemmas = json.load(lemma_file)

if refresh:
    print('Purging databases...')
    if lemma_line_matches.is_file():
        lemma_line_matches.unlink()
    if translation_trends.is_file():
        translation_trends.unlink()
    if trends_2ndpass.is_file():
        trends_2ndpass.unlink()

def generate():
    c_range = range(1,5969)
    t_range = range(1,5984)
    t_lines = dict.fromkeys([str(t) for t in range(1,4518)] + ['4517x'] + [str(t) for t in range(4518,5921)] + ['5920x'] + [str(t) for t in range(5921,5984)])
   
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
            with open('translated-lemmas.json', 'w') as f:
                json.dump(t_lines, f, ensure_ascii=False, indent=4)
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
            # moving to integers, meaning those 'x' lines are out for now:
            c_line_lemmas[ln] = [token['lemma'] for token in c_tokens if int(token['verse'].rstrip('ab')) == ln]

        with open('lemma-line-matches.json', 'w', encoding='utf-8') as outfile:
            json.dump(c_line_lemmas, outfile, ensure_ascii=False, indent=4)
    else:
        with open('lemma-line-matches.json') as c_line_lemma_data:
            c_line_lemmas = json.load(c_line_lemma_data)
        with open('translated-lemmas.json') as t_lines_data:
            t_lines = json.load(t_lines_data)

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

    if not(translation_trends.is_file()):
        for lemma in lemma_list:
            trans_terms = []
            matching_lines = [k for k,v in c_line_lemmas.items() if lemma in v]
            for line in matching_lines:
                line = str(line)
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

    # Now this is where to build in a second pass! I'll need to document this closely since it's hard to follow...
    # Just generating a JSON for now, yet to make up my mind what to fill it with exactly...
    # The thinking: for each translated lemma, if another lemma in the same three-line window
    # scores HIGHER than the present lemma, DON'T give the current lemma any points in the second pass
    # (you can later redirect it to a list of collocations for Philip's sake)
    if True: # currently set to always true so I can build in an is_file() test later
        print('Running a second pass...')
        secondpass = dict()
        # This routine is hardly efficient, but let's get it to work first:
        for line,lemmas in c_line_lemmas.items():
            if int(line) in range(1,5982):
                for lemma in lemmas:
                    if trends[lemma] is not None:
                        pre_rankings = sorted([i for i in trends[lemma]], key=lambda x: x[1], reverse=True)
                        pre_rankings = [i[0] for i in pre_rankings]
                        tr_lemmas = t_lines[str(line)]
                        tr_line_rankings = dict()
                        if tr_lemmas is not None:
                            for tr_lemma in tr_lemmas:
                                if tr_lemma in pre_rankings:
                                    tr_lemma_idx = pre_rankings.index(tr_lemma)
                                    tr_line_rankings[tr_lemma] = pre_rankings[tr_lemma_idx]
                        if tr_line_rankings is not None:
                            if len(tr_line_rankings.items()) > 0:
                                sorted_translations = sorted([i for i in tr_line_rankings.items()], key=lambda x: x[1])[0]
                                # 0 is the highest rank, since the rankings are a list:
                                top_ranking_translation = [i[0] for i in sorted_translations][0]
                                # I think here maybe I should not 
                                if lemma in secondpass:
                                    if top_ranking_translation in [i[0] for i in secondpass[lemma]]:
                                        interim_list = [i[0] for i in secondpass[lemma]]
                                        # Is this the index I was looking for here? or do I want .index(lemma)? top ranking is always 0?
                                        existing_index = interim_list.index(top_ranking_translation)
                                        old_score = secondpass[lemma][existing_index][1]
                                        secondpass[lemma][existing_index] = (top_ranking_translation, old_score+1)
                                    # TODO: enter old data if not already entered.
                                    # but in what format again?
                                    # currently I'm just duplicating the old rankings which is pointless
                                else:
                                    secondpass[lemma] = trends[lemma]

        with open(trends_2ndpass, 'w') as f:
            json.dump(secondpass, f, ensure_ascii=False, indent=4)
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
