# Reuse Research Matrix

## Scopo

Valutare soluzioni esistenti per il sistema affettivo di Matrix Engine privilegiando semplicità, verificabilità, licenze chiare, offline/Android e riuso reale.

| Sistema | Area utile | Stato iniziale | Criterio principale |
|---|---|---|---|
| FAtiMA Toolkit | appraisal, emotional state, social importance, decision support | ADAPT candidate | alta aderenza al problema Matrix |
| ALMA | emotion/mood/personality separation | REIMPLEMENT/REFERENCE | modello temporale semplice e utile |
| EMA | appraisal dinamico, coping | REIMPLEMENT/REFERENCE | buona causalità evento→appraisal→risposta |
| OCC | tassonomia delle emozioni | REFERENCE_ONLY | troppo ampia se implementata integralmente |

## Criteri obbligatori

Ogni candidato deve essere valutato su:

- licenza e obblighi;
- maturità/manutenzione;
- dipendenze;
- facilità di port Android/offline;
- determinismo e testabilità;
- capacità di spiegare la causa di ogni variazione affettiva;
- costo CPU/RAM/storage;
- rischio di accoppiamento con Memory, NLU o GGUF;
- quantità di codice che elimina rispetto a una soluzione custom;
- capacità di gestire eventi, target/entity, appraisal, emotion decay, mood e persistent affect.

## Gate di adozione

Una soluzione entra nell'architettura solo se:

1. elimina più complessità di quanta ne introduca;
2. non richiede server esterni;
3. non rende il GGUF arbitro dello stato emotivo canonico;
4. consente causal trace;
5. è compatibile con la futura integrazione `AffectiveMemoryCandidate → Memory Admission`;
6. non duplica responsabilità già appartenenti a World/App o Matrix-NLU.

## Output della ricerca

Per ogni candidato produrre:

- componenti realmente riusabili;
- componenti da reimplementare;
- componenti da scartare;
- contratto input/output minimo per Matrix;
- test cases importabili/adattabili;
- stima costo di integrazione;
- decisione finale ADOPT / ADAPT / REIMPLEMENT / REFERENCE_ONLY / REJECT.
