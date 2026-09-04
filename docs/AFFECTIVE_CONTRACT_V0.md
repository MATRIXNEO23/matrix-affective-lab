# Matrix Affective Contract v0

Status: EXPERIMENTAL / LAB ONLY

## Scope
Define the first stable boundary between semantic understanding and the affective system. Memory retrieval/storage is intentionally out of scope until this contract is validated.

## Canonical flow

Input -> Matrix-NLU/Understanding -> TypedClaim or WorldEvent -> AffectiveStimulus -> Appraisal -> EmotionalImpulse -> EmotionState -> Mood -> PersistentAffect(entity) -> Behavior/Decision

World/App relationship state remains canonical and external to the affective system.

## Reuse-first sources

### FAtiMA-derived concepts
- explicit appraisal rules
- OCC-style affect derivation
- per-emotion disposition: threshold + decay
- reappraisal keyed to the same cause/event
- explicit cause -> emotion linkage
- mood influence on emotion

### Cognitiv-derived concepts
- saturating impulse integration
- exponential decay using per-emotion half-life
- slow mood baseline
- derived valence/arousal/dominance representation
- persistent attitude/affect toward a specific entity

## Matrix-owned contracts

### AffectiveStimulus
Must be produced from a validated TypedClaim or canonical WorldEvent. Minimum fields:
- id
- sourceType: TYPED_CLAIM | WORLD_EVENT
- actorId
- targetIds
- category
- predicate/action
- polarity
- timestamp
- confidence
- canonicalWorldTruth flag/source when applicable

### AppraisalResult
Explainable result. Minimum dimensions:
- relevance
- goalCongruence
- agency/accountability
- controllability
- novelty
- target entity
- rule/source used
- confidence

### EmotionalImpulse
- emotionType
- intensity [0,1]
- causeId
- targetId optional
- timestamp
- appraisalTraceId

### EmotionState
Short-lived state. Multiple emotions may coexist. Integration must saturate rather than sum without bound. Each type may have its own threshold and half-life/decay.

### Mood
Slow baseline derived from accumulated emotional state. Mood may bias appraisal of ambiguous stimuli but must never override canonical World/App truth.

### PersistentAffect
Per-entity long-lived affect, separate from App relationship state. Initial candidate dimensions:
- trust
- attachment
- affection
- attraction
- resentment
- respect
- admiration
- aversion

This list is provisional and must be reduced/validated before production.

## Hard boundaries
- Affective system cannot change relationshipState directly.
- Affective system cannot create World Truth.
- GGUF cannot directly mutate affective state without a validated event/claim path.
- Mood cannot turn an explicit negative fact into a positive fact or vice versa.
- PersistentAffect is not Memory and is not the App relationship state.
- Memory integration is deferred until affective semantics are stable.

## Required diagnostics
Every update must be traceable:
Event/Claim -> Appraisal variables -> Emotional impulses -> Emotion state diff -> Mood diff -> Persistent affect diff -> downstream behavior signal.

## First validation targets
1. Same event + same initial state => deterministic same result.
2. Reappraisal of same cause does not double-count blindly.
3. Repeated small impulses saturate.
4. Emotions decay with configured half-life.
5. Mood changes slower than emotion.
6. Positive/negative mood only biases ambiguous appraisal.
7. Persistent affect changes slower than immediate emotion.
8. Affect remains entity-scoped.
9. App relationship state remains unchanged by affective processing.
10. Causal trace is complete and serializable.
