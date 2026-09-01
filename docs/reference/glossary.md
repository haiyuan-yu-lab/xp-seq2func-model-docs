# Glossary

Canonical sequence-to-function terms for exact release **v0.1.0a8**. Prefer
these names in configuration discussion and documentation.

## Prediction head

A named model output that represents one prediction task. Its caller-defined
head key is its canonical identity across configuration, labels, losses, and
attribution requests.

Avoid: output head, predictor name (as a synonym for this concept).

## Profile prediction head

A prediction head containing one or more position-wise signal channels and a
paired profile count for each channel. Its tracks share geometry, output
domain, and loss semantics.

Avoid: profile output, track head.

## Profile track

One position-wise signal channel within a profile prediction head.

Avoid: profile, output channel (when referring to this concept).

## Profile distribution

The normalized allocation of a profile track's signal across its positions.

Avoid: profile probabilities, normalized track.

## Profile bin

One position in a profile distribution, representing a contiguous interval of
retained sequence positions.

Avoid: output position, pooled position.

## Profile count

The nonnegative total signal magnitude paired with one profile track.

Avoid: track count, scalar profile.

## Attribution target

The scalar prediction whose dependence on an input sequence an attribution
explains. An explicit attribution target has one meaning shared by every input
row.

Avoid: attribution class, target output.

## Output domain

The mathematical representation of an attribution target, such as a class
probability, class logit, or difference between class logits.

Avoid: output type, attribution mode.

## Predicted-class attribution

Attribution whose target class is selected independently for each input row
from that row's prediction. It is a legacy mode and does not represent one
shared target across the resulting array.

Avoid: fixed attribution (as a synonym for this legacy mode).

## Positional validity mask

A boolean annotation aligned to the retained sequence positions for a
prediction head, where `true` marks a position as eligible for position-wise
losses and metrics.

Avoid: mappability mask, positional mask.

## RC-aware predictor counterpart

A separately catalogued prediction head that preserves an existing head's
external role while adding reverse-complement-aware behavior defined for that
head. The category does not imply one universal output transform or restrict
which encoder family the head may consume.

`RCClassPredictor` is the RC-aware counterpart to `ClassPredictor`.
`RCRegressPredictor` is the RC-aware counterpart to `RegressPredictor`.
`RCProfilePredictor` is the RC-aware counterpart to `ProfilePredictor`.
`track_transform: preserve` reverses profile bins under embedding RC while
keeping track order; counts are invariant. `track_transform: swap_pair`
requires exactly two tracks and couples strand orientation (profile bins
reverse and track slots swap; counts swap track slots only).

Avoid: RCE predictor, equivariant predictor, invariant predictor (as generic
synonyms for this catalog entry).

## Regular embedding

A length-preserving latent representation whose channels are organized in
reverse-complement pairs.

Avoid: equivariant tensor (when referring to this specific representation).

## Embedding reverse-complement transform

On channel-first `(B, C, L)` tensors, reverse both the channel axis and the
sequence-length axis. Used by RC-aware modules to relate an embedding to its
reverse-complement partner.

Avoid: sequence RC (when referring to this channel-first embedding operation).
