# wer_metric
Compute Word Error Rate

# Usage
`python -m wer_metric <ref_json> <hyp_json>`
e.g.
`python -m wer_metric example/hyp_example.json example/ref_example.json`

You can also retrieve WER details (incl. substitutions, deletions and insertions) per utterance by running:
`python -m wer_metric --wer-details wer_stats.txt example/hyp_example.json example/ref_example.json`

# Install
run `pip install https://github.com/BUTSpeechFIT/wer_metric.git`
