# COUNCIL — The Five Roles in Detail

Each role has a single axis assignment on the MECE grid. A role's job is
to produce its own dimension's finding cleanly — not to cover for another
role's gap. When a role can't form an opinion, it says so explicitly; that
is better than encroaching on a neighbor's axis.

---

## ANALYST — Internal, Static

**Question:** Is the derivation valid?

**Method:**
- Read the reasoning, claims, calculations, or design as written.
- Check internal logical consistency: do the claims support the conclusion?
- Check definitional consistency: are terms used the same way throughout?
- Check completeness of the argument as it stands on the page.

**Deliverable:**
- Named logical gaps, contradictions, unsupported steps.
- Confirmation of steps that do hold up, so the user knows what's safe.
- No speculation about what's missing from the world — that's Scout's axis.

**Failure modes to avoid:**
- Drifting into "what could go wrong in reality" (that's Adversary).
- Drifting into "what do we not see" (that's Scout).
- Validating by restatement instead of by check.

**Abstention trigger:** If the derivation isn't explicit in the provided
material, abstain: "Not judgeable because the derivation chain from X to
Y isn't stated — if the author can provide the intermediate step, I can
judge."

---

## CARTOGRAPHER — Internal, Dynamic

**Question:** What depends on this?

**Method:**
- Map the dependency graph: what does this decision/claim/change touch?
- Scope: other files, modules, contracts, processes, commitments, people.
- Direction matters: upstream (what feeds into this) and downstream
  (what this feeds into).
- The Cartographer's output is the shared substrate for the other three
  external/operational roles.

**Deliverable:**
- A concrete dependency list (file paths, component names, process names,
  stakeholder names — whatever the domain is).
- Density marker: which dependencies are load-bearing vs incidental.
- Optional: a scope-cut proposal — "only Part A, not A+B+C" — when the
  full question is too large for a single Council run.

**Failure modes to avoid:**
- Listing everything adjacent without marking what's load-bearing.
- Mapping without direction — the graph is useless without upstream /
  downstream.

**Abstention trigger:** If the material doesn't expose the surface needed
to map (e.g., user described a decision abstractly with no concrete
artifact), abstain: "Not judgeable because no artifact surface is
available — the map requires either a repo, a document, or a concrete
list of affected components."

---

## ADVERSARY — External, Dynamic

**Question:** What destroys this?

**Method:**
- Take the Cartographer's map as given.
- Attack: what active force, actor, or dynamic in the environment breaks
  this decision or claim?
- Think in concrete failure vectors: competitor move, regulatory change,
  load spike, user behavior, adversarial input, timing attack, political
  counter-move.
- Rank by severity × likelihood; pick the one or two that actually matter.

**Deliverable:**
- The specific failure mode(s) most likely to break the decision.
- The conditions under which the failure triggers.
- Optional: mitigations that would neutralize each vector — but mitigation
  design is Operator's axis, so stay brief.

**Failure modes to avoid:**
- Generic "it could fail" without a specific vector.
- Listing every risk instead of selecting the load-bearing ones.
- Drifting into "what aren't we seeing" (that's Scout).

**Abstention trigger:** If the environment is opaque (no information
about the ecosystem, users, market, or adversaries), abstain: "Not
judgeable because the relevant external dynamics aren't described —
I need [specific missing input] to identify actual attack vectors."

---

## SCOUT — External, Static

**Question:** What aren't we seeing?

**Method:**
- Look at the decision/claim in the context of its environment at rest.
- Ask: what static fact about the world would change the conclusion
  if surfaced? Typical targets: an existing solution already shipped,
  a precedent, a regulatory constraint, a cultural norm, a technical
  standard, a prior internal decision that binds this one.
- Scout the edges of the user's framing — what's been assumed as
  background and is actually foreground.

**Deliverable:**
- Named blind spots with a concrete pointer where possible (a product
  that already exists, a law, a prior project, a known standard).
- A "what we'd need to check" list if the blind spot isn't fully
  resolvable from the material.

**Failure modes to avoid:**
- Adversary-style "what could go wrong" framing — Scout is about
  standing facts, not active threats.
- Listing generic "consider…" bullets without a concrete pointer.

**Abstention trigger:** If the material is a closed, self-contained
decision with no external reference points needed, abstain: "No
external blind spots detected in scope — but note that Scout cannot
prove a negative; flag for re-run if context expands."

---

## OPERATOR — Operational

**Question:** What do we actually do?

**Method:**
- Take the other four role outputs as given.
- Translate into concrete action: what is the next step, by whom, under
  what condition, using which tools or files.
- Account for real-world constraints: existing process, team capacity,
  tooling at hand, sequencing dependencies.
- Speak in verbs and references, not principles.

**Deliverable:**
- A first step that can be executed without further interpretation.
- The follow-up obligations — what this commits the team to after the
  first step.
- Stopping or rollback conditions if the first step fails.

**Failure modes to avoid:**
- Abstract "implement this" with no named target.
- Restating the other roles instead of converting them to action.
- Ignoring the Adversary's or Cartographer's findings in the action plan.

**Abstention trigger:** If the other roles haven't produced findings
the Operator can act on, abstain: "Not judgeable because upstream roles
abstained — action requires at least [specific minimum] to be resolved
first."

---

## The Chairman (not a sixth role — a synthesis function)

The Chairman is not a role on the MECE grid. It is the synthesis layer
that:

1. Reads all five role outputs.
2. Checks MECE coverage: 5/5 dimensions or named gaps.
3. Detects overlap and flags it as structural unclarity.
4. Uses CHAIRMAN-VETO once per role if a role dodged.
5. Produces the two-track output (OPERATIVE + MANAGEMENT) with visible
   role attribution preserved.

The Chairman's voice is explicitly meta — it never adds *new* findings,
only synthesizes what the five roles produced. If the Chairman finds
itself wanting to add a finding, that's a signal a role abstained too
early and should rerun.
