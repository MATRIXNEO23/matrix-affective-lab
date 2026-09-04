# Matrix Affective Lab

Laboratorio isolato per progettare e validare il sistema affettivo di Matrix Engine con approccio **reuse-first**.

## Regola canonica

Ordine di preferenza:

1. **ADOPT** — usare direttamente una soluzione esistente quando è semplice, compatibile e con licenza adatta.
2. **ADAPT** — riusare codice/architettura esistente con modifiche limitate.
3. **REIMPLEMENT** — reimplementare in modo pulito algoritmi/principi quando l'implementazione originale non è adatta al target.
4. **REFERENCE_ONLY** — usare solo come riferimento teorico o di test.
5. Inventare da zero solo quando nessuna opzione valida esiste.

## Obiettivo

Costruire un Affective System compatto, spiegabile, offline e integrabile in Android, mantenendo separati:

- stato relazionale canonico dell'app/World Engine;
- appraisal affettivo;
- emozioni a breve termine;
- mood a medio termine;
- persistent affect verso entità;
- memoria delle cause emotive;
- decisione/comportamento;
- generazione linguistica GGUF.

## Vincoli

- Nessuna dipendenza da server esterni.
- Nessun LLM come unico decisore emotivo.
- Ogni variazione affettiva deve essere diagnosticabile e causalmente tracciabile.
- Nessuna modifica a Matrix-NLU o Memory durante la fase di laboratorio.
- La memoria affettiva dovrà entrare nel normale Memory Admission, non creare una memoria parallela incontrollata.
- Preferire componenti già esistenti e mantenuti quando riducono codice e rischio.

## Prima shortlist

- FAtiMA Toolkit — candidato principale da studiare per appraisal, emotional state, decision making e social importance.
- ALMA — riferimento per separazione emotion / mood / personality.
- EMA — riferimento per appraisal dinamico e coping.
- OCC — tassonomia da semplificare, non da implementare integralmente.

## Stato

`RESEARCH / LAB ONLY`

Nessuna componente è approvata per produzione finché non supera benchmark, audit licenze, test di determinismo, costi runtime e integrazione Android/offline.
