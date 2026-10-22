# TruthLens Empathy Map and Research Plan

## Purpose
Design TruthLens around the needs of people who encounter potentially manipulated or misleading images, videos, audio, or text online. The current dashboard prototype analyses image/video technical properties and checks SHA-256 matches against locally registered references. It does not yet provide a trained deepfake classifier or live blockchain verification.

## Target user (initial hypothesis)
A general digital-media user who sees a suspicious post, forwarded clip, or image and wants to assess it before trusting or sharing it. Other possible users (journalists, students, educators, moderators) should be studied separately rather than assumed to have identical needs.

## Four empathy-map quadrants

### Says
- “Is this image or video genuine?”
- “Can you show me why it needs review?”
- “Where did this file come from?”

### Thinks
- Could this be AI-generated or edited?
- How reliable is this result, and what are its limitations?
- Does this file match a trusted original?

### Does
- Uploads suspicious media for review.
- Searches for the original source or context.
- Compares available evidence before sharing.

### Feels
- Confused by conflicting claims.
- Worried about being misled or misleading others.
- Frustrated by technical tools or unexplained scores.

> **Evidence status:** Every statement above is an example hypothesis created for design planning. These are not direct participant quotes, interview findings, or statistically validated conclusions.

## User need statement
“When I encounter suspicious digital content, I need a clear and understandable way to inspect available signals and source integrity, so I can make a more informed decision without being given false certainty.”

## Design responses
| User insight | Design response | Caution |
|---|---|---|
| Wants a simple answer | Put a concise summary before technical detail | Do not label content definitively real/fake without validated evidence |
| Wants to understand why | Show measured signals, findings, and limitations | Explain that technical anomalies are not proof of manipulation |
| Wants to know source integrity | Offer SHA-256 comparison with a trusted registered reference | A hash match proves byte identity with that reference, not factual truth |
| Feels overwhelmed | Use plain language and clear next steps | Avoid alarmist colors, accusations, and unsupported accuracy claims |
| Needs confidence in the tool | State model scope and uncertainty clearly | Current prototype uses basic heuristics, not a trained deepfake detector |

## Suggested validation method
1. Recruit 5–8 intended users where feasible; explain the study and obtain consent.
2. Ask participants to describe how they currently decide whether suspicious media is trustworthy.
3. Ask them to use the prototype on a sample file and narrate what they expect each result to mean.
4. Record anonymized observations and exact quotes only with permission.
5. Cluster repeated observations into Says, Thinks, Does, and Feels. Separate observed evidence from researcher assumptions.
6. Update this map and record what changed, why, and how many participants supported the theme.

## Interview prompts
- Tell me about the last time you were unsure whether a photo or video online was genuine.
- What did you do to check it?
- What made the task difficult or frustrating?
- What would you need to see before deciding to trust or share a result?
- After seeing a review-priority score, what do you think it means?
- What do you understand a matching file hash to prove? What does it not prove?
- Which explanation or next step would be most useful?

## Success indicators for a later usability test
- Users can explain, in their own words, what the review-priority score does and does not mean.
- Users understand that a hash match means the same file bytes as a registered reference, not proof of truth.
- Users can locate findings and limitations without assistance.
- Users can identify a sensible next step when the tool is inconclusive.

Do not claim these indicators have been achieved until usability testing is conducted and results are recorded.
