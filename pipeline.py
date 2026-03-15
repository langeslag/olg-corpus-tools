# Runs all the generative processes in the repository, replacing any files
# already in place. See requirements.txt for required libraries.

import os
import helipad_extract
import wikisource_extract
import heliand_forms
import heliand_synoptic
import heliand_xpollinate

for file in [
    'heliand-c.json',
    'heliand-m.json',
    'heliand-m_behaghel.json',
    'heliand-forms.json',
    'heliand-synoptic.json',
    'heliand-c.txt',
    'heliand-m.txt',
    'heliand-m_behaghel.txt',
    'heliand-synoptic.txt',
    'heliand-c_rich.json'
    ]:
    if os.path.exists(file):
        os.remove(file)

helipad_extract.extract()
wikisource_extract.extract()
heliand_forms.generate()
heliand_synoptic.generate()
heliand_xpollinate.xfer()
