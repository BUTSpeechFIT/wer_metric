#!/bin/env python3

import numpy as np
import sys

import json


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Measure WER between references and hypothesis."
    )
    parser.add_argument(
            "ref", type=argparse.FileType("r"), help="Reference json file."
    )
    parser.add_argument(
        "hyp", type=argparse.FileType("r"), help="Hypothesis json file."
    )
    parser.add_argument(
        "--wer-details",
        type=argparse.FileType("w"),
        help="Output detail statistics to this file.",
        default=None,
    )
    args = parser.parse_args()
    print(args)

    wer_stats = WerStats()

    subs, dels, ins = {}, {}, {}
    N = 0

    refs_dict = json.load(args.ref)
    hyps_dict = json.load(args.hyp)

    for rid, ref in refs_dict.items():
        hyp = hyps_dict[rid]

        hyp = hyp.strip().split()
        ref = ref.strip().split()
        wer, (s, d, i) = compute_wer(ref, hyp)

        wer_stats.update(rid, ref, hyp, wer=wer, subs=s, dels=d, ins=i)
        subs, dels, ins = merge(subs, s), merge(dels, d), merge(ins, i)
        N += len(ref)

    S, D, I = sum(subs.values()), sum(dels.values()), sum(ins.values())
    WER = (S + D + I) / N

    print(f"%WER {WER*100:.2f} [ {S+D+I} / {N}, {I} ins, {D} del, {S} sub ]")
    if args.wer_details:
        print(wer_stats, file=args.wer_details)


def editdistance(ref, hyp):
    """Compute Levenstein edit distance between `ref` an `hyp`

    Arguments:
    _________
    ref : list
        Reference sequence
    hyp: list
        Hypothesis sequence

    Returns:
    ________
    numpy.array
        distance matrix between `ref` and `hyp`
    """
    distmat = np.zeros((len(ref) + 1, len(hyp) + 1), dtype=int)

    for i in range(len(ref) + 1):
        distmat[i, 0] = i

    for j in range(len(hyp) + 1):
        distmat[0, j] = j

    for i in range(1, len(ref) + 1):
        for j in range(1, len(hyp) + 1):
            if ref[i - 1] == hyp[j - 1]:
                distmat[i, j] = distmat[i - 1, j - 1]
            else:
                sub = distmat[i - 1, j - 1] + 1
                ins = distmat[i, j - 1] + 1
                dell = distmat[i - 1, j] + 1
                distmat[i, j] = min(sub, ins, dell)
    return distmat


def compute_wer(ref, hyp):
    distmat = editdistance(ref, hyp)

    subs, ins, dels = {}, {}, {}
    i, j = len(ref), len(hyp)

    while i > 0 or j > 0:
        if (
            i > 0
            and j > 0
            and distmat[i, j] == distmat[i - 1, j - 1]
            and ref[i - 1] == hyp[j - 1]
        ):
            i, j = (i - 1, j - 1)
        elif j > 0 and distmat[i, j] == distmat[i, j - 1] + 1:
            key = hyp[j - 1]
            val = ins.get(key, 0)
            ins[key] = val + 1
            j -= 1
        elif i > 0 and distmat[i, j] == distmat[i - 1, j] + 1:
            key = ref[i - 1]
            val = dels.get(key, 0)
            dels[key] = val + 1
            i -= 1
        elif i > 0 and j > 0 and distmat[i, j] == distmat[i - 1, j - 1] + 1:
            key = (ref[i - 1], hyp[j - 1])
            val = subs.get(key, 0)
            subs[key] = val + 1
            i, j = (i - 1, j - 1)
        else:
            raise ValueError("This should not happen!")

    S, I, D = sum(subs.values()), sum(ins.values()), sum(dels.values())
    WER = (S + I + D) / len(ref)
    return WER, (subs, dels, ins)


def merge(d1, d2):
    d3 = {}
    for k, v in d1.items() | d2.items():
        d3[k] = d3.get(k, 0) + v
    return d3


class WerStats:
    def __init__(self):
        self.utterances = []

    def update(self, uttid, ref, hyp, **wer_details):
        utt = Utterance(uttid, ref, hyp, **wer_details)
        self.utterances.append(utt)

    def __str__(self):
        return ("\n" + "+" * 80 + "\n\n").join(map(str, self.utterances))


class Utterance:
    def __init__(self, uttid, refs, hyps, wer=None, subs=None, dels=None, ins=None):
        self.id = uttid
        self.refs = refs
        self.hyps = hyps
        self.wer = wer
        self.subs = subs
        self.dels = dels
        self.ins = ins

    def __str__(self):
        return (
            f"{self.id}\n"
            + f"ref: {' '.join(self.refs)}\n"
            + f"hyp: {' '.join(self.hyps)}\n"
            + f"\n# WER: {self.wer}"
            + "\n# SUBS:"
            + " ".join(map(str, self.subs.items()))
            + "\n# DELS:"
            + " ".join(map(str, self.dels.items()))
            + "\n# INS:"
            + " ".join(map(str, self.ins.items()))
        )


if __name__ == "__main__":
    main()
