# Data_LTR.py

This script is used to generate LTR data-set.

1. Read tokens from summaries and stories

2. Compute similarities and rank

$ embedding(phrase_i) = \Sigma_{word_k\ in\ phrase_i}(embedding(word_k)) / |phrase_i| $

$ similarity(phrase_i, phrase_j) = cos(embedding(phrase_i), embedding(phrase_j)) $

3. Select samples

: Exclude samples in questionnaires
: have high similarity candidates (>=0.8)

4. Feature set

: *chapter_id* number
: *sentence_id* number
: $ embedding(phrase) $ 64
: postag_phrase
: $ embedding(word_before) $ 64
: postag_before
: $ embedding(word_after) $ 64
: postag_after
: count number
