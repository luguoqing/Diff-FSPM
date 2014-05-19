#!/bin/sh

lmax=20
epsilon=1.0
topk=100
for ((nmax=3; nmax<8; nmax++)); do
    python utility.py --lmax=$lmax --nmax=$nmax --topk=$topk --epsilon=$epsilon
done
