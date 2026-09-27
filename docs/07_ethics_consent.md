# Ethics, consent & safety

This project records children's voices and produces a risk indicator about a
learning disability. Treat that seriously — and say so in your report. It is
also, practically, one of the things that most distinguishes a serious submission.

## Hard rules

1. **Screening, never diagnosis.** Output is a band (`low_indicator` / `monitor` /
   `refer_for_assessment`) with an explicit statement that only a qualified
   professional can diagnose dyslexia. The word "diagnosis" appears nowhere in the UI.
2. **Guardian consent before any recording.** Written, informed, revocable.
   A consent record id is stored with every session.
3. **Data minimisation.** Store derived features (WPM, error rates), not raw audio,
   unless consent explicitly covers retention. Delete temp audio after processing.
4. **No child-visible scoring.** Children see progress and encouragement. Risk
   bands go to the teacher or guardian dashboard only. A 7-year-old should never
   see a number telling them they are behind.
5. **The model is not neutral.** It was trained largely on synthetic errors and on
   Indian children reading English as a second language. It will behave differently
   on other accents and first languages. State this limitation explicitly.

## Fairness checks to run and report

- Per-accent / per-L1 error rates, if the metadata supports it
- Performance split by reading level — the model must not simply flag every slow reader
- Check M2 does not conflate "second-language pronunciation" with "dyslexia indicator".
  This is the central confound of the whole project and NNCES makes it unavoidable.
  Address it head-on rather than hoping nobody asks.

## What to write in your paper's limitations section

- Test set is small and self-collected
- Bulk of training data is synthetic; the synthetic→real gap is reported, not hidden
- No clinical ground truth — labels are behavioural, not diagnostic
- Single-language, single-script
- No longitudinal validation that the adaptive coach improves reading over months
