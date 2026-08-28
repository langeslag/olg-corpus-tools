# Runs all the generative processes in the repository, replacing any files
# already in place. See requirements.txt for required libraries.
# Note that the most important files in the repository are NOT generated
# by this pipeline, as they are the `*corrected` files that have been
# proofread and manually corrected.

import os
import helipad_extract
import wikisource_extract
import heliandv
import heliand_forms
import heliand_synoptic
import heliand_xpollinate
import heliandv_xpollinate
import verses_of_different_length
import heliand_xpollinate_2ndpass
import heliandlps_xpollinate
import add_fragments_to_inverted_lemmas
import translation_crib

#for file in [
#    'heliand-c.json',
#    'heliand-m.json',
#    'heliand-v.json',
#    'heliand-m_behaghel.json',
#    'heliand-forms.json',
#    'heliand-synoptic.json',
#    'heliand-c.txt',
#    'heliand-m.txt',
#    'heliand-m_behaghel.txt',
#    'heliand-synoptic.txt',
#    'heliand-m_rich.json',
#    'heliand-m_rich_2ndpass.json',
#    'heliand-v_rich.json'
#    ]:
#    if os.path.exists(file):
#        os.remove(file)

helipad_extract.extract()
wikisource_extract.extract()
heliandv.extract()
heliand_synoptic.generate()
heliand_xpollinate.xfer()
heliandv_xpollinate.xfer()
verses_of_different_length.generate()
heliand_xpollinate_2ndpass.xfer()
heliandlps_xpollinate.xfer('l')
heliandlps_xpollinate.xfer('p')
heliandlps_xpollinate.xfer('s')
add_fragments_to_inverted_lemmas.generate()
translation_crib.generate()
