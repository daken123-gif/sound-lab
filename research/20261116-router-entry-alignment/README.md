# 20261116-router-entry-alignment

Authority research/review: https://github.com/daken123-gif/sympathia/pull/2536 at ff1e6f14d50f7ea83d05bb1cfb5e0a3e7742e61f. Coordination: sympathia#2535. This downstream record is a locator, not a second research/decision authority.

Question: align 3 entry files omitted by PR55 with Sympathia-first SKILL/Governance. Observed source main36cd887c66305ee196ee5fb4a8d7511614714aa5; two YAML default_prompt copies and plugin manifest defaultPrompt/longDescription still started with sound-lab. Proposed interpretation: fix entry wording only; preserve version, capabilities, implicit invocation and all unrelated fields.

Paths: .agents/skills/sound-lab-research-router/agents/openai.yaml; plugins/sound-lab-research/skills/sound-lab-research-router/agents/openai.yaml; plugins/sound-lab-research/.codex-plugin/plugin.json.

Evidence: source blob verification and JSON/YAML parse PASS in authority record; separate semantic reviewer found narrow candidate consistent. Existing quick_validate PASS is restricted to unchanged SKILL frontmatter/TODO, not changed plugin fields. Package schema/runtime validation NOT DONE; no validator located in fixed repo or installed CLI help. No real-user evaluation claimed.

Adoption: NOT ADOPTED, branch/PR only. No Field Looper behavior change intended. No audio generation, merge, deployment, activation, Actions run or installation. CURRENT.json is intentionally not updated until an authorized integration; this draft must not imply main research/adoption state changed. Previous sound-lab-first prompt is proposed for supersession only, not yet main.

Remaining: formal review/merge authorization, package validation gap; existing SKILL adopted/CURRENT ambiguity is separate repair. Updated 2026-11-16 UTC.
