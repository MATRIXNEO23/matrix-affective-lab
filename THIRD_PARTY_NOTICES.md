# Third-party source provenance

This lab contains modified/adapted source-derived implementations. Matrix-specific adapters and extensions are marked in code and are not claimed as upstream behavior.

## FAtiMA Toolkit

- Repository: `GAIPS/FAtiMA-Toolkit`
- Source commit: `56b7cbd992f953cfe21a7b12cb1a0e6cdf6ccf9f`
- License: Apache License 2.0
- Copyright notice in upstream license: Copyright 2016 GAIPS/INESC-ID
- Ported/adapted source:
  - `Assets/EmotionalAppraisal/ActiveEmotion.cs`
  - `Assets/EmotionalAppraisal/Mood.cs`
  - `Assets/EmotionalAppraisal/ConcreteEmotionalState.cs`
  - `Assets/EmotionalAppraisal/EmotionalAppraisalConfiguration.cs`
  - `Assets/EmotionalAppraisal/OCCModel/OCCAffectDerivationComponent.cs`
  - `Assets/EmotionalAppraisal/OCCModel/OCCEmotionType.cs`
- Matrix modifications include normalization from FAtiMA's 0..10 emotion scale to 0..1, stable Matrix appraisal-slot identity, duplicate-event idempotence, semantic zero cancellation, and Matrix data-contract adaptation.
- Full license copy: `third_party/LICENSE_FATIMA_APACHE_2.txt`.

## Cognitiv

- Repository: `swamprabbitlabs-dot/Cognitiv`
- Source commit: `f3aad875a77a3c7c522781e03acbb1944c3ab25c`
- License: MIT
- Copyright: Copyright (c) 2026 SwampRabbit Labs
- Ported/adapted source:
  - `cognitiv/emotion.py`
- Retained mechanism: saturating integration of independent active contributions (`current + impulse * (1-current)`, equivalently `1-product(1-i)`).
- Matrix modifications adapt this operation to FAtiMA-derived active contributions and cause/channel identities.
- Full license copy: `third_party/LICENSE_COGNITIV_MIT.txt`.

## Alma.Net

- Repository: `prbarcelon/Alma.Net`
- Source commit: `55b0475abdd077f145ed90575b435111c288454e`
- License: MIT
- Copyright: Copyright (c) 2021 prbarcelon
- Ported/adapted source:
  - `src/AlmaNet/Alma.cs`
  - `src/AlmaNet/Personality/OceanModel.cs`
- Retained mechanisms: exact emotion-to-PAD coordinate table, Virtual Emotion Center aggregation semantics, and OCEAN-to-PAD coefficients.
- Matrix modifications adapt C# value types/naming to Python and Matrix emotion IDs.
- Full license copy: `third_party/LICENSE_ALMANET_MIT.txt`.

## Matrix-owned experimental extensions

These are not represented as upstream FAtiMA/Cognitiv/Alma.Net behavior: persistent affect toward an entity, Matrix relationship-state boundary, semantic duplicate-event guard, semantic-zero cancellation, and explicit habituation-key adapter.
