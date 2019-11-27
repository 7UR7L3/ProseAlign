# ProseAlign
Efficient global word-level sequence alignment approximation via (recursive) Aho-Corasick prepass(es).

---

Word-level diffing algorithms were found to be insufficient for aligning/diffing prose.

This currently aligns a Vietnamese translation of Harry Potter with a Google speech-to-text transcription of its corresponding Audiobook because for some ungodly reason the voice actor did not faithfully record the translation (minor phrasing differences / insertions / deletions). This is required to create a faithful punctuated transcription of the Audiobook while also correcting the stt transcription's errors.

Global char-level sequence alignment (Needleman-Wunsch) is too slow for texts of ~26k character sequences.

A custom word-level Needleman-Wunsch _may_ have sufficed. It will need to be implemented for the resulting mismatch sections (after a few levels of recursive Aho-Corasick) anyway, so we will see if all this has been a waste of time.

---

TODO:
- rewrite to be one self-contained function
- implement recursion
- implement custom Needleman-Wunsch
