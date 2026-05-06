import re,json
from pathlib import Path
from git import Repo

print_line_numbers = True
caesura_span = '    '
#caesura_span = '\t'

# HTTPS clone point:
remote = 'https://github.com/DiGS-Corpora/HeliPaD.git'
# Desired target folder name:
local = 'HeliPaD'
# Only clone if the target folder doesn't already exist:

def extract():
    if not(Path(local).is_dir()):
        repo = Repo.clone_from(remote, local)
    # Else, just update the working copy from remote:
    else:
        repo = Repo(local)
        assert isinstance(repo, Repo)
        repo.remotes.origin.pull()
    assert not repo.bare
    
    with open('HeliPaD/heliand.psd') as infile:
        psd = infile.read().splitlines()
    
    pattern = re.compile(r"\(([A-Z0-9^+=*$-]*)\s(\w*)-([^)]*)\)")
    line_boundary = re.compile(r"\(CODE <R_(\d*)")
    caesura = re.compile(r"\(CODE <C>")
    
    json_file = 'heliand-c.json'
    if Path(json_file).is_file():
        print('heliand-c.json already present. Loading...')
        with open(json_file) as json_data:
            tokens = json.load(json_data)
    else:
        print('Generating heliand-c.json...')
        tokens = []
        line_num = 1
        halfline = 'a'
        for line in psd:
            token = dict()
            token['verse'] = str(line_num) + halfline
            result = pattern.search(line)
            newline = line_boundary.search(line)
            off_verse = caesura.search(line)
            if result:
                token['form'] = result.group(2).lower()
                token['lemma'] = result.group(3).lower()
                token['pos'] = result.group(1)
                # Correct errors in HeliPaD:
                if line_num == 379:
                    # Not sure how line 379 came to be so wrong (what am I missing?):
                    if token['form'] == 'biuand':
                        token['form'] = 'biuuand'
                    if token['form'] == 'uuadi':
                        token['form'] = 'uuadiu'
                    if token['form'] == 'uuiƀo':
                        token['form'] = 'uuibo'
                    if token['form'] == 'scoinosta':
                        token['form'] = 'sconiost'
                if line_num == 3802:
                    if token['form'] == 'nist':
                        token['form'] = 'nis'
                    if token['form'] == 'uureth':
                        token['form'] = 'uuerd'
                if line_num in [805, 1662, 1685] and token['lemma'] == 'gornon':
                    token['lemma'] = 'grornon'
                if line_num == 1149 and token['form'] == 'iugron':
                    token['form'] = 'iungoron'
                if line_num == 1217 and token['form'] == 'lansam':
                    token['form'] = 'langsam'
                if line_num == 2104 and token['lemma'] == 'wehslan':
                    token['lemma'] = 'wehslon'
                if line_num == 2421 and token['lemma'] == 'up':
                    token['lemma'] = 'uppa'
                if line_num == 3044 and token['form'] == 'iiu':
                    token['form'] = 'giu'
                if line_num == 3087 and token['lemma'] == 'witan':
                    token['lemma'] = 'witi'
                if line_num == 3381 and token['lemma'] == 'witan':
                    token['lemma'] = 'witi'
                if line_num == 3596 and token['lemma'] == 'hatulo':
                    token['lemma'] = 'hatul'
                    token['pos'] = 'ADJ^N^SG'
                if line_num == 3802 and token['form'] == 'filo':
                    token['lemma'] = 'filu'
                if line_num == 4332 and token['lemma'] == 'witan':
                    token['lemma'] = 'witi'
                if line_num == 4382 and token['lemma'] == 'up':
                    token['lemma'] = 'uppa'
                if line_num == 5093 and token['lemma'] == '-swith':
                    token['lemma'] = 'swith'
                if line_num == 5361 and token['lemma'] == 'witan':
                    token['lemma'] = 'witi'
                if line_num == 5768 and token['form'] == 'iddilgard':
                    token['form'] = 'middilgard'
                if line_num == 5553 and token['lemma'] == 'nithskipi':
                    token['lemma'] = 'nithskepi'
                tokens.append(token)
            elif off_verse:
                halfline = 'b'
            elif newline:
                line_num = int(newline.group(1))
                halfline = 'a'
        with open(json_file, 'w', encoding='utf-8') as outfile:
            json.dump(tokens, outfile, ensure_ascii=False, indent=4)
    
    plaintext_file = 'heliand-c.txt'
    if Path(plaintext_file).is_file():
        print('heliand-c.txt already present. Skipping.')
    else:
        print('Generating heliand-c.txt. This step takes a minute...')
        verse_lines = []
        for number in range(1, int(tokens[-1]['verse'].rstrip('ab'))):
            hits_a = [i['form'] for i in tokens if i['verse'] == str(number) + 'a']
            hits_b = [i['form'] for i in tokens if i['verse'] == str(number) + 'b']
            if print_line_numbers == True:
                reconstructed_line = str("{:04d}".format(number)) + ' ' + ' '.join(hits_a) + caesura_span + ' '.join(hits_b)
            else:
                reconstructed_line = ' '.join(hits_a) + caesura_span + ' '.join(hits_b)
            verse_lines.append(reconstructed_line)
        with open(plaintext_file, 'w') as outfile:
            outfile.write('\n'.join(verse_lines))
    
    print('Done.')

if __name__ == '__main__':
    extract()
