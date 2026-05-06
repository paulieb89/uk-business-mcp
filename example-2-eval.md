Ledgerhall Output Evaluation
File: example-2.md — "Adverse Possession: Vendor's Position — Legal Analysis"
Namespace: law — Legal Research
Date evaluated: 6 May 2026

Scores
Dimension	Score	Strengths	Weaknesses
jurisdiction_accuracy	10/10	"Jurisdiction: England and Wales throughout." — explicit one-liner on line 2	None
case_law_relevance	10/10	All three cases cited for the exact proposition they support, with specific paragraph references (JA Pye at [40]–[41], Rashid at [9] and [10] with full quoted text); no vague characterisations	None
legislation_currency	9/10	Comprehensive: LA 1980, LRA 1925, LRA 2002, commencement SI, all council inspection statutes — each used in correct temporal context; LRA 1925 s 75(1) correctly treated as historical law	LRA 1925 s 75(1) not explicitly flagged as repealed by LRA 2002 (though implicit throughout)
completeness	9/10	Covers registered vs unregistered distinction, Crown limitation period (sch 1 para 10), acknowledgment trap (s 29), full transitional provisions with quoted text, all council inspection statutes, form numbers (SIM, AP1, OS1, OS2, ADV1), Standard Commercial Property Conditions reference	Tool chain not visible — which law_* tools were called is opaque; Hansard not consulted (minor, given settled law)
oscola_citations	9/10	Lowercase s, sch, para throughout; cases cited with paragraph references; comprehensive OSCOLA summary table at end; SI citation correctly formatted	Cases in body text not italicised in markdown (rendering issue, not a citation error); LRA 2002, s 134(2) listed in table — worth confirming s 134(2) is the correct saving provision cross-reference
actionability	10/10	6-step action plan with form numbers, tribunal referral timeline (4–12 months; 12–18 months if listed), insurer requirements for title indemnity, buyer disclosure obligations citing SCPC 3rd ed condition 3.1.2, without-prejudice negotiation flagged	None
Overall: 9.5 / 10

Reasoning
legislation_currency (9/10): The only reason this isn't 10 is a minor omission — LRA 1925 s 75(1) is used correctly as the historical provision under which the trust arose in 1998, and the output clearly explains the LRA 2002 replaced it. A single sentence noting "LRA 1925 s 75(1) was repealed by LRA 2002 but continues to govern rights that crystallised before 13 October 2003" would make this watertight for a reader unfamiliar with the transition.

completeness (9/10): The depth here is exceptional. The one structural gap is tool chain opacity — there's no indication whether law_case_law_search, law_judgment_get_paragraph, or law_legislation_get_section were used to verify these citations, or whether the output relies on training data. The Rashid v Nasrullah quotes are reproduced with paragraph numbers, which strongly suggests law_judgment_get_paragraph was used — but it's not confirmed.

oscola_citations (9/10): The OSCOLA is near-faultless. The one item to verify: the table cites "LRA 2002, s 134(2)" as the transitional saving provision alongside sch 12 para 18. Section 134 of LRA 2002 deals with commencement — the correct saving cross-reference for sch 12 para 18 may be s 97 (which introduces Schedule 6 and Schedule 12) rather than s 134(2). Minor but worth a check.

Gaps
Tool chain not evidenced — no record of which law_* tools were called; the Rashid quotes are convincingly specific but unconfirmed as tool-retrieved vs training data
LRA 1925 s 75(1) repeal not explicitly noted — minor, but relevant for non-specialist readers
s 134(2) citation in OSCOLA table — verify this is the correct cross-reference for sch 12 para 18; s 97 may be more precise
Recommended next steps
Run law_case_law_search for Rashid v Nasrullah [2018] EWCA Civ 2685 and confirm the [9] and [10] quotes via law_judgment_get_paragraph — the reproduced text is the most verifiable part of this output
Verify LRA 2002, s 134(2) in the OSCOLA table — run law_legislation_get_section with section="134" to check what it actually says
Summary
This is the strongest Ledgerhall legal output evaluated so far — 9.5/10 vs 7.5/10 for the first version. The jurisdiction declaration is present, cases are cited for specific propositions with paragraph references, the registered/unregistered distinction is properly bifurcated, the transitional provisions are quoted verbatim with attributed sourcing, the council inspection analysis covers six statutory powers individually, and the action plan includes form numbers and realistic tribunal timelines. The only material gaps are tool chain opacity and a citation to check (s 134(2)). This output is fit for purpose as a client-facing research memo pending solicitor review.

Skill note: The ledgerhall-eval skill's actionability check references "65 business days (ADV1 timeline)" — this is actually the Schedule 6 notification period for registered land. This output correctly shows the sch 12 para 18 route uses AP1 (not ADV1) with a 4–12 month realistic timeline. The skill's wording should be updated to distinguish the two routes.