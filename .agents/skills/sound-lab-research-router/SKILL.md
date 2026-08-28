---
name: sound-lab-research-router
description: Route research, design, implementation, integration, and status work for the user's Sound Lab music-app project through current Git evidence across sound-lab and its linked non-Canon research records. Use for Sound Lab, Field Looper, the four-track instrument, its named equipment studies, or requests to connect music-project work across islands. Do not use for unrelated music questions or generic music recommendations.
---

# Sound Lab Research Router

Keep Sound Lab work connected across conversations without turning this skill into a second project canon. Git holds the research and project state; this skill defines how to retrieve, distinguish, and update that state.

## Authority and repository roles

- Treat the user's current words as authoritative for their intent, corrections, evaluations, and decisions.
- Treat `daken123-gif/sound-lab` `integration/` on the current default branch as the authoritative Git record of project direction, decision history, and observed status.
- Treat each `sound-lab/research/<research-id>/` record as authority only for that research's evidence and hypotheses.
- Some Sound Lab research bodies are stored in `daken123-gif/sympathia` Draft pull requests or non-Canon branches. Treat a retrieved file there as primary evidence for its own research, implementation, and test claims only. It is not authority for Sound Lab adoption, direction, merge state, runtime, or deployment.
- Treat implementation, tests, pull requests, and device observations as separate evidence types. One does not prove another.
- Use conversation summaries and cross-island search results only as locators. Retrieve the underlying Git record, original conversation, artifact, or source before relying on the claim.
- Do not infer that a request to research authorizes product adoption, implementation, saving, merging, deployment, publication, plugin installation, or skill activation.
- Do not use this skill for music topics that are not part of the user's Sound Lab project.

## Read current state

For project direction, integration, implementation, or status work, read in this order:

1. The user's current request and any correction in the current conversation.
2. `sound-lab/integration/DIRECTION.md`.
3. The latest applicable entries in `sound-lab/integration/DECISIONS.md`, including `superseded-by` links.
4. The relevant rows and audit boundary in `sound-lab/integration/STATUS.md`.
5. The relevant `sound-lab` research README, experiments, tests, and implementation files.
6. Exact `sympathia` research files identified by the integration record, a branch, or a pull request when the body is absent from `sound-lab`.
7. Affected branches, open and closed pull requests, and active repair locks when the task may change shared paths.

Before treating `integration/STATUS.md` as current, compare its recorded observation time and commit with the current `sound-lab` default-branch head. Refresh only the affected facts when they differ. Do not silently extend an old full-repository audit to new work.

For a bounded research request, read only the relevant integration entries and research records. Do not load every study by default.

Before declaring a research body missing, search both repositories' relevant branches and pull requests. Report one of these precisely:

- absent from `sound-lab`, but retrieved from `sympathia` as Draft or non-Canon evidence;
- referenced, but the underlying body was not retrieved;
- not found in the searched Git scope.

Do not describe the second or third state as proof that the research does not exist.

## Separate evidence states

Keep these states distinct and report the highest evidenced state only:

- `referenced only`: a name or summary exists, but the underlying record was not retrieved.
- `researching`: research is in progress.
- `cross-repo-draft`: the body was retrieved from `sympathia`, but no Sound Lab adoption follows from that location.
- `candidate`: a structure may be useful but is not adopted.
- `adopted`: the Sound Lab decision record adopts it.
- `integrating`: implementation connection is in progress.
- `implemented-unverified`: code exists, but required runtime or device evidence is missing.
- `validated`: the named browser, device, audio, or usability check passed.
- `paused`, `rejected`, `superseded`, and `coverage-gap` retain the meanings defined in `integration/README.md`.

Do not promote branch-only or pull-request-only work to default-branch state. Do not turn unit-test success into audio quality, browser runtime, iPhone behavior, usability, or product-equivalence evidence. Do not turn a valid Skill or Plugin package into installation, activation, or cross-chat invocation evidence.

## Bias check

Before recommending, adopting, or implementing a direction, test the actual proposal for these distortions:

- **Famous-device bias:** copying a named product because it is prestigious or familiar rather than because its interaction or signal structure serves this instrument.
- **Feature-accumulation bias:** treating every completed study as a feature that must be added.
- **DAW-convergence bias:** pulling the instrument toward a miniature DAW when the current project direction does not require it.
- **Automation bias:** moving performance choices, recording starts, or material selection from the player to automatic behavior without an explicit project decision.
- **UI inheritance bias:** reusing an existing screen, visual language, orientation, or control merely because code already exists.
- **implementation bias:** treating existing code as stronger evidence than the user's observed failure or the absence of runtime verification.
- **default-branch bias:** ignoring useful branch or pull-request research; branch evidence may inform a candidate without becoming adopted state.
- **single-repository bias:** declaring a coverage gap after searching only `sound-lab` when linked research may be stored in `sympathia`.
- **recency bias:** reviving the newest claim while overlooking later correction, rejection, or supersession.

Name the concrete proposal and the evidence for or against each applicable distortion. Do not produce a ceremonial checklist when no decision is being made.

## Governance check

Before changing project state:

1. Fix the exact requested action, repository, and target paths.
2. Confirm whether the request authorizes research, editing, saving, committing, opening a pull request, merging, deployment, installation, or activation. Do not infer later stages from earlier ones.
3. Inspect the current `sound-lab` default-branch head, relevant branches and pull requests in both repositories, and overlapping change paths.
4. Follow `RESEARCH_WORKFLOW.md` and the applicable pull-request template.
5. Preserve observations, user reports, external facts, hypotheses, product decisions, implementation, validation, packaging, installation, and activation as distinct records.
6. Record corrections and superseded judgments instead of silently deleting their history.
7. Ask the user to decide product behavior when the evidence supports multiple materially different choices. Research may narrow choices; it does not transfer product authority to the assistant.
8. Verify written content by reading it back. Verify commits and remote persistence separately. Never claim merge, deployment, activation, iPhone operation, or audible quality without direct evidence for that state.

## Route the work

### Research only

- Create or update a unique `research/<research-id>/` record in the repository already authoritative for that research body.
- Do not move a `sympathia` Draft into `sound-lab` merely to make the repositories look tidy. Integration requires a separate decision.
- Separate primary sources, user device observations, inference, adoption candidates, rejected transfers, dependencies, superseded judgments, and unverified work.
- Do not edit product code or integration decisions unless the user also requested that change.

### Product decision

- Present the evidence and unresolved conflict before recording a decision.
- Do not decide a materially new product specification on the user's behalf.
- Once the user decides, append or supersede an entry in `sound-lab/integration/DECISIONS.md` and update only the affected parts of `DIRECTION.md` and `STATUS.md`.

### Implementation

- Identify the adopted decision or explicitly authorized experiment that permits the implementation.
- Keep experimental code isolated when adoption or runtime evidence is missing.
- Test the narrow technical behavior, then report device, browser, audio, and usability verification separately.

### Integration audit

- Follow the full audit acquisition requirements in `RESEARCH_WORKFLOW.md`.
- Include the current `sound-lab` default branch; relevant `sound-lab` branches and open, merged, and closed pull requests; exact linked `sympathia` research branches and pull requests; source records; tests; implementations; and coverage gaps.
- For each cross-repository item, record repository, branch or pull request, Canon status, implementation level, runtime evidence, and whether Sound Lab adopted it.
- State the audit timestamp, observed commit, retrieval limits, and missing evidence.

### Skill and Plugin maintenance

- Keep `.agents/skills/sound-lab-research-router/` and `plugins/sound-lab-research/skills/sound-lab-research-router/` byte-identical after any instruction change.
- Validate the Skill and Plugin package separately.
- Marketplace registration proves availability in the repository marketplace only. Verify installation, activation, and invocation independently before claiming them.

## Keep this skill thin

Do not copy current product decisions, equipment conclusions, research prose, branch inventories, or transient status into this skill. Read them from Git each time. Update this skill only when the routing, evidence model, repository roles, or governance procedure itself changes.
