# Decision documents

Use this reference when a draft must help a non-technical reader understand a
complex proposal, compare options, approve a bounded next step, or decide not
to proceed. It is guidance, not a mandatory template.

## Start from the decision

State the reader's task in one sentence. Distinguish these common outcomes:

- **Understand:** establish a shared model; do not invent an approval request.
- **Choose:** compare real alternatives using the same decision criteria.
- **Approve:** state the bounded resource, scope, risk, or next stage being
  authorized.
- **Act:** name the owner, next step, and trigger or deadline when supplied.

“Learn about the project” is not yet a decision. When no decision is required,
the document can still end with what happens next without pretending the reader
must approve it.

## Find the load-bearing idea

Identify the one idea that makes the rest easier to understand. Express it in
plain language without losing its condition or uncertainty. Use it to organize
the explanation; do not give every implementation detail equal weight.

For a technical-to-business rewrite, translate this sequence:

`implementation mechanism -> changed workflow -> observable result -> decision value`

Do not skip directly from a mechanism to revenue, efficiency, quality, or
adoption unless evidence establishes that link.

## Design the first reading layer

A scanning reader should be able to find, near the beginning:

1. the current problem or opportunity;
2. the recommendation or current conclusion;
3. why this option is preferred now;
4. the most important limitation or uncertainty;
5. the decision or next action, if one exists.

Write the summary after the body is sound, even though it appears first. A
summary is not a teaser: it should contain the conclusion.

## Use a complete scenario

When an architecture description is too abstract, show one representative flow:

1. who begins the task and with what input;
2. what the proposed system or process does;
3. where a human reviews, changes, or rejects the result;
4. what output is produced;
5. how success and failure will be observed.

Label the scenario as an example when it is illustrative. Do not let an example
silently become a promise that every case behaves the same way.

## Layer the body by reader need

Choose only the sections the decision requires. Useful candidates include:

- current problem and why it matters now;
- proposal and representative use case;
- first-stage scope and explicit non-goals;
- alternatives and trade-offs, including the status quo when relevant;
- deliverables, owners, dependencies, and sequence;
- acceptance method and evidence needed;
- people, time, budget, and operational load;
- risks, mitigations, stop conditions, and fallback;
- requested decision or next action;
- technical appendix.

Use consistent criteria when comparing options. Do not praise one option for
speed and reject another for cost without showing both criteria for both
options.

## Keep decision-changing constraints visible

A technical fact belongs in the main body when it changes any of these:

- feasibility or supported use cases;
- cost, staffing, or operational burden;
- delivery time or dependencies;
- security, privacy, compliance, or rights;
- failure recovery or business continuity;
- acceptance thresholds or quality risk.

Explain the consequence in reader language, then place implementation mechanics
in the appendix if further detail is useful.

## Keep the evidence boundary explicit

Use the strongest accurate verb:

- **observed / verified:** directly supported by current evidence;
- **estimated:** derived from stated inputs or a model;
- **expected:** a reasoned forecast, not yet observed;
- **targeted:** an intended outcome;
- **unknown / pending confirmation:** no adequate basis yet.

If cost, duration, headcount, baseline, or success threshold is missing, retain
`待确认` and state why it matters. Smooth prose must not conceal the gap.
