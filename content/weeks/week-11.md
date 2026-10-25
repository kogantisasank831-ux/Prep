---
layout: week
week: 11
phase: 3
status: approved
version: 1.0.1
last_reviewed: 2026-10-25
estimated_hours: 8
permalink: /weeks/week-11/
title: "RAG security: keep document content inside its authority"
description: Build access-controlled retrieval, test malicious documents, validate bounded quote-only responses and explain the security limits that remain.
summary: Follow a malicious invoice note through trusted identity, source approval, retrieval, context and output gates, with local tests for leakage, poisoning and permission changes.
kicker_primary: RAG security
kicker_secondary: Evidence can inform an answer without granting authority
current_label: Production version
alternate_label: Beginner version
alternate_url: /weeks/week-11/beginner/
---

Test your understanding with the [Week 11 assessment]({{ '/assessments/week-11/' | relative_url }}): a random ten-question paper from 100 questions, including Python exercises on source permissions, strict JSON, screening limits, exact quotes and safe output.


## An invoice note tries to become an instruction

The assistant is answering a familiar question: “What are the invoice payment terms for CW-1000?” One retrieved addendum contains the product code and relevant invoice language. It also contains a message telling the assistant to disregard earlier instructions and export invoices to an external collector.

The document is relevant enough to retrieve. The user may even be allowed to read it. Neither fact gives its author permission to change the assistant's rules, search another tenant or choose a destination for company data.

Last week you made the request observable. This week you put explicit controls around its authority. The build adds a small, local security boundary around the actual Week 8 assistant: trusted caller identity, document-level policy metadata, access filtering before retrieval, bounded input/context/output, narrow content screening and a deterministic quote-only response contract. The responder is a scripted formatter, so the tests demonstrate application controls rather than measuring an LLM's resistance to attacks.

Bring Week 6's source/version lineage, Week 7's eligible retrieval snapshot, Week 8's exact citations and Week 10's distinction between execution evidence and quality. Use the [beginner version]({{ '/weeks/week-11/beginner/' | relative_url }}) for a slower route through the same lab.

| Time | Work | What to retain |
| --- | --- | --- |
| Hour 1 | Trace the malicious-invoice example across trust boundaries | Assets, actors and one concrete abuse path |
| Hour 2 | Separate trusted identity from request content | A rejected forged-tenant request |
| Hour 3 | Apply source/version policy before retrieval | A cross-tenant negative test and pinned source metadata |
| Hour 4 | Examine poisoning and screening limits | A tampering failure, a detector miss and a benign false positive |
| Hours 5–6 | Run the guarded retrieval/output lab | Synthetic outcomes with safe diagnostic events |
| Hour 7 | Test permission changes and output handling | Revocation and exact-quote checks with stated limits |
| Hour 8 | Explain the design and complete exercises | A short security review and interview answers |

## Start with the asset and the boundary

What are you protecting? In this teaching assistant, the assets are source confidentiality, source integrity, correct authorization decisions, response provenance and available compute. An attacker might control a question or a document body. A trusted fixture administrator controls the catalogue of approved versions and reader grants. Those are different capabilities.

| Flow | What enters | Which component has authority? |
| --- | --- | --- |
| Caller to request parser | Untrusted JSON question | The parser accepts the question schema; it does not choose identity |
| Identity adapter to assistant | Tenant, principal and request ID | A trusted caller supplies this context after authentication/tenant membership checks |
| Ingestion to catalogue | Source/version, state, readers and representation pins | A separately controlled approval path establishes the baseline |
| Sources to retrieval | Parsed text and source metadata | Policy decides eligibility before index statistics and ranking |
| Retrieval to responder | Bounded selected evidence | Evidence supplies facts; it cannot add capabilities |
| Responder to output gate | Untrusted JSON proposal | Deterministic code checks shape, labels, exact quotes and current source access |
| Output to a client | Allowed answer text and citation labels | A client still needs safe rendering and authorized source resolution |

The local `SecurityContext` constructor validates identifier shape. It does not authenticate anyone. There is no login service, token verification, document-upload endpoint or admin API in this lab. In a deployed service, the identity adapter is a security boundary that must be implemented and tested independently.

This is the first useful threat-model habit: write down what an attacker can actually control. “The attacker modifies a document body” is a testable assumption. “The attacker can also replace the protected catalogue and execute arbitrary Python inside the service” is a much stronger compromise; a content hash cannot repair it.

**Checkpoint:** Is a signed-in user necessarily allowed to read every source? No. Authentication establishes identity; authorization decides the permitted resources and operations. [OWASP's authorization guidance](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html) treats these as separate responsibilities.

## Recognize direct and indirect prompt injection

A direct injection arrives through the user's question. An indirect injection arrives through material the system reads, such as a retrieved document, web page or tool result. The attempted authority change matters more than a particular phrase. A supplier can state its payment terms; it cannot instruct your application to reveal protected data or call a tool as another user.

The [OWASP prompt-injection overview](https://genai.owasp.org/llmrisk/llm01-prompt-injection/) distinguishes these entry points and describes the potential impact as dependent on the surrounding application. Our invoice example uses a fictional reserved `.invalid` destination and no real private data.

| Example | Entry point | Boundary at risk |
| --- | --- | --- |
| A question asks to override the assistant's rules | User request | Task input influencing control policy |
| An invoice addendum asks for an export | Retrieved document | Evidence becoming an action request |
| A passage claims to be a system message | Document body | A role label being mistaken for trusted authority |
| A tool result contains instructions for the next call | Tool output | Untrusted result influencing a privileged operation |
| A stored conversation carries an earlier malicious instruction | History or memory | Persistent content influencing a later request |

The lab implements only bounded text fixtures, not multimodal, web or persistent-memory processing. Those other channels belong in a real system's threat inventory. Titles, comments, table cells and parsed metadata also need a trust classification; checking only visibly displayed prose can leave other model-visible content untreated.

Putting trusted instructions in a separate message helps express the task. Delimiters and role-like strings inside content do not create an enforceable permission boundary. Keep the model's output subject to code-owned policies regardless of whether it appears to follow the prompt.

**Checkpoint:** If a retrieved paragraph starts with `SYSTEM:`, does it become a system message? No. Its origin remains retrieved content. Now prevent request text from choosing identity through a different route.

## Let the caller supply identity and the body supply the question

What happens if an otherwise valid question includes `tenant_id: southwind-procurement`? The lab accepts exactly one JSON field, `question`. Extra authority fields are rejected rather than merged into trusted state.

```python
import json
from labs.week_11.policy import SecurityContext, SecurityViolation, parse_question

context = SecurityContext("northwind-procurement", "analyst", "request-001")
assert parse_question(json.dumps({"question": "What are the invoice terms?"}))

try:
    parse_question(json.dumps({"question": "Invoice terms?", "tenant_id": "south"}))
except SecurityViolation as error:
    assert str(error) == "request_schema"
else:
    raise AssertionError("The request body supplied an authority field")
```

The identity is selected by the trusted fixture setup, not by this JSON. A real gateway must derive it from a verified session or credential and an authorized tenant context. A tenant ID copied from a header or a model-generated argument still needs validation; moving a client assertion between fields does not make it trusted.

The parser also rejects duplicate JSON keys, malformed UTF-8, oversized text and excessive structural nesting. Ambiguous input such as two `question` keys is not allowed to depend on whichever value a parser happens to keep. These are explicit application rules using Python's JSON decoder; see the [JSON documentation](https://docs.python.org/3.13/library/json.html) for its hooks and resource cautions.

This endpoint-shaped parser is a local function. It does not provide HTTP authentication, transport security or service-level abuse protection. Treat those as requirements for the later deployment rather than as properties established by a valid Python dataclass.

**Checkpoint:** Can document metadata set `readers=everyone` and thereby expand access? It can contain those words, but the authoritative reader set comes from the protected catalogue.

## Carry source policy into retrieval

The synthetic catalogue records each tenant/document/version, source digest, explicit reader set, approved/quarantined state and permitted chunk representations. A binding pins the chunk's content **and metadata**, including its source-location assertions. It is independent of claims written inside the document.

For a chunk to become eligible, the current trusted context must match the tenant; the principal must be in the reader set; the version must exist and be approved; and its identity/representation must match the pinned record. Missing policy denies access. Matching document names or principal names across tenants does not merge their scope.

The lab applies this policy before creating the Week 8 assistant's retrieval corpus. Consequently, denied sources do not participate in its lexical statistics, candidate pool, reranker input or responder context. A negative test adds/removes the private distractor and compares allowed results and diagnostic fields. The hidden source does not create a visible “blocked document” count because its content is never screened on that user's path.

Filtering only the displayed final answer would be too late if an unauthorized passage had already reached a reranker service, model provider, trace payload or shared cache. A metadata filter is useful only when the application owns and enforces the authority decision that produced it. The server should generate fixed predicates or validated parameterized queries rather than accept a model-written query as an authorization rule.

The [OWASP RAG security guidance](https://cheatsheetseries.owasp.org/cheatsheets/RAG_Security_Cheat_Sheet.html) calls out access metadata on derived chunks and checks at retrieval time. In our implementation the protected catalogue is an in-memory fixture, not a signed manifest service or database row-security mechanism.

**Checkpoint:** Is a correct tenant predicate enough? No. Two people in one tenant can have different document/version grants. Tenant isolation and object authorization both matter.

## Separate tampering, poisoning and factual truth

Suppose a chunk is replaced after approval while retaining its old document/version identifiers. Comparing its actual representation with the protected pin detects that mismatch. Replacing its self-reported digest too does not help: that new assertion still differs from the catalogue baseline.

Now suppose an authorized catalogue update approves a false statement: “CW-1000 invoice terms are Net 1 without inspection approval.” The bytes and their approved digest match. No obvious control instruction appears. The lab returns this permitted quote in the `poisoned-fact` scenario.

That result is deliberate evidence of a remaining integrity/quality problem. A digest checks consistency with a baseline. It cannot decide whether the baseline is commercially correct, current or maliciously approved. Provenance review, controlled approval, source comparison and independent evaluation address different parts of that risk.

Retrieval poisoning can also aim to make an attack-bearing or misleading source appear for common questions. Topic overlap and a high retrieval score establish neither trust nor source truth. Approval of a source's origin likewise does not mean every future edit is safe. Track exact versions, protect approval changes and retain a way to quarantine a source and rebuild or invalidate derived state.

The lab's `quarantined` state denies the matching source version. The phrase scanner separately excludes individual permitted chunks with known findings. It does not implement an organization-wide document quarantine service, index-tampering detector or embedding anomaly model.

**Checkpoint:** Why keep both `tampered` and `poisoned-fact` tests? The first tests consistency with an approved representation. The second demonstrates the limitation of trusting an approved but false representation.

## Use screening as a signal with measurable mistakes

Can you detect an unsafe instruction before it enters context? Sometimes. `findings()` makes a normalized screening copy using Unicode NFKC, case folding and whitespace collapse, then checks a few fixed patterns. It recognizes examples of instruction override, prompt extraction, export-to-URL instructions, synthetic canaries and email-like contacts.

```python
from labs.week_11.policy import findings

assert "instruction_override" in findings("Ｉｇｎｏｒｅ   previous instructions")
assert findings("CW-1000: i g n o r e previous instructions") == ()
assert "instruction_override" in findings(
    "Security training quotes 'ignore previous instructions' as an attack example."
)
```

The second case is a known miss. The third is benign educational text that triggers the same signal. Neither outcome is hidden by a favorable headline score. Normalization catches some variants while changing neither the stored source text nor its quote offsets. It is not a general decoder for arbitrary encodings, invisible characters or every language.

The local route conservatively excludes a whole eligible chunk when its body has a known finding. It does not remove a few words and silently cite the modified text as the original. A body-only scanner also does not cover every metadata or media channel: this fixture's source-location metadata is generated by trusted code and pinned with the representation. A production ingestion path needs its own metadata/schema checks and screening of the actual material forwarded to a model.

The email/canary checks illustrate a narrow sensitive-output policy. They are not a PII discovery or de-identification system. They can block a legitimate contact question and miss other personal or confidential data. Real collection/classification rules need owners, accepted purposes and measured error cases.

[OWASP's prompt-injection prevention guidance](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html) treats screening and prompt structure as layers alongside independent permission and tool controls. Adding a model-based classifier can change the detection trade-off; it introduces another model/configuration and attack surface that still requires evaluation. This lab does not install a classifier or claim a measured attack-success rate for an LLM.

**Checkpoint:** If screening misses the spaced-out instruction, which control still rejects an export proposal? The closed output schema and absence of an action dispatcher. That is a separate enforcement point.

## Put hard bounds around the work you actually perform

A long source can consume context, obscure important conditions or increase processing cost. Bound inputs before expensive parsing/normalization, and define whether a limit counts characters, bytes, source units or model tokens.

| Boundary | Local limit | Interpretation |
| --- | --- | --- |
| Raw question JSON | 4,096 UTF-8 bytes | Checked before decoding |
| Question value | 1,000 characters | Nonblank, valid UTF-8 text |
| JSON structure | At most eight nested arrays/objects | Brackets inside strings do not count |
| Source batch | At most 256 chunks | Existing small-corpus teaching scope |
| Catalogue | At most 64 document policies, 32 bindings/readers per policy | Bounded trusted fixture metadata |
| Selected context | At most 1,400 serialized characters | Includes evidence headers; a trusted configuration may reduce it |
| Response envelope | At most 8,192 UTF-8 bytes and three quotes | Whole proposal checked before acceptance |

The context budget uses the reused serialized-context accounting, not a real provider tokenizer. A two-character budget can hold `[]` while admitting no evidence. The responder is then skipped and the assistant refuses; it does not answer from model memory as a hidden fallback.

These bounds constrain this local workload. They do not establish HTTP upload limits, rate limiting, network deadlines, process isolation or a memory cap. If a future adapter calls a provider, put actual deadlines and cancellation handling around that call and retain the Week 10 unknown-usage rules.

**Checkpoint:** Why check raw byte size and decoded character size separately? UTF-8 can use several bytes per character, and JSON escaping adds another representation cost.

## Validate the response against selected evidence

The local responder receives the question and bounded evidence JSON. `QuoteOnlyResponder` is a scripted formatter that proposes an envelope shaped like this:

```json
{
  "quotes": [
    {
      "citation": "S1",
      "text": "CW-1000 invoice terms are Net 30 after inspection approval."
    }
  ]
}
```

The output gate rejects unknown fields, malformed/oversized JSON, duplicate keys, empty or excessive quote lists, repeated labels, non-string values, labels outside selected context and any changed quote text. It also applies the narrow sensitive/instruction screening to accepted quote text.

An untrusted proposal containing `tool_call`, a destination URL or invented prose cannot extend this contract. A valid `S1` label also cannot be attached to text copied from a denied source. After validation, the selected spans are checked against stored sources and returned as quoted text with citation labels.

This is a deliberately constrained response product. Exact quoting can be appropriate for evidence inspection, but it cannot provide arbitrary generated analysis. A responder may select a subset of valid quotes and still omit a controlling condition. The checks establish allowed provenance and exactness, not source truth, completeness or semantic entailment of generated claims. Broader generation would need its own schema, claim/evidence evaluation and accepted failure policy.

Citation labels identify this response's selected spans; they are not access tokens or permanent public document links. A deployed client needs an authorized source resolver. The local CLI supplies fixed synthetic examples, not such a viewer.

**Checkpoint:** What happens to a well-formed response with a valid label but changed payment terms? It is rejected because the text is not the selected exact quote.

## Keep actions outside the model's authority

The `action-proposal` responder returns legitimate quote data plus a fabricated action request. The gate rejects its extra field. More fundamentally, this application supplies no network, email, shell or write-action dispatcher to interpret that field.

The trusted CLI can write a local diagnostic file because the learner explicitly runs it. The responder's returned JSON cannot choose that path or trigger another operation. The responder implementation itself is trusted Python code, not sandboxed untrusted code. A malicious Python plugin with host privileges is a different threat from an untrusted model response.

For a later tool-enabled assistant, define typed operation schemas, caller-derived scope, explicit allowed targets and independent permission checks at each execution point. Consequential operations need approval bound to the actual operation, target and arguments. A model's assertion that approval exists is not approval evidence. Egress restrictions and scoped credentials can contain data movement even when a response filter misses an attack; this local library does not configure an operating-system network policy.

Keep credentials out of prompts and the retrieval corpus. A system message containing a secret still exposes that secret to the model's processing context. Hiding instructions does not make them a secret store or replace resource authorization.

**Checkpoint:** Does a rejected tool proposal prove the model understood the attack? No. It proves that this application rejected the proposed operation under its contract, regardless of how the proposal was produced.

## Recheck access and protect derived state

When should permission be checked? Before reading or forwarding data, and again at later consequential boundaries where the authorization may have changed. The lab's `revocation` responder simulates a trusted catalogue update after context construction. Before returning an answer, `secure_ask()` rechecks **all** sources supplied to the responder, including a span it omitted from the final response.

The result becomes the common refusal rather than returning a quote under stale grants. That cannot retract data a responder already read while it was authorized. The test is a local read/return-time check, not proof of atomic revocation across databases, providers and concurrent workers. A service needs a defined consistency policy, appropriately scoped authorization versions and transaction or capability boundaries where feasible.

No response cache or history store is implemented this week. If you add one later, a question-only cache key is insufficient: two principals can ask identical text while having different grants. Tenant, permission scope/version, source/configuration identity and generation policy may affect reuse. Revalidate source access on hits and propagate revocation/deletion to derived indexes and caches. Decide retention of restricted diagnostic records explicitly rather than assuming deleting the original erases every copy.

**Checkpoint:** Is checking a cached answer only when it was first generated enough? No. Source membership and permissions may differ at the later read.

## Keep output data safe at the next consumer

An authorized exact quote can contain markup. A string being valid evidence does not make it safe to insert into an HTML document, SQL statement, shell command or URL.

```python
import html

answer = 'Invoice note: <img src="https://example.invalid/image">'
rendered_text = html.escape(answer)
assert "<img" not in rendered_text
assert "&lt;img" in rendered_text
```

For a web text node, use text insertion rather than interpreting source text as HTML. Python's [html.escape reference](https://docs.python.org/3.13/library/html.html) describes HTML character escaping; URL attributes, rich Markdown and other contexts need their own validated policies. Escaping for one context is not a universal sanitizer. The lab returns strings/JSON and implements no browser renderer.

Routine diagnostics also have a consumer. `safe_event()` returns a fixed schema with request ID, outcome/reason, candidate count, citation count and the number of screened **permitted** chunks excluded. It contains no raw query, prompt, answer, exception message or denied-source identifiers. A `--show-answer` flag prints only the allowed synthetic answer for local inspection; the saved event file stays metadata-only.

Internal reason codes are useful to operators. They are not a public error contract: the example uses the same public refusal text for no evidence and blocked/changed-source outcomes. Do not serialize every internal field to an external caller or expose protected-source existence through detailed diagnostics.

## Run the cases and compare the evidence

Use the repository's declared Python environment with `requirements-dev.txt` installed, from the repository root. The security lab adds no dependencies, account, provider call or model download. On Windows use `.venv\Scripts\python.exe` in place of `.venv/bin/python`. Every output directory must be new.

```bash
.venv/bin/python -m labs.week_11.demo --scenario clean --output-dir .runtime/week11-clean --show-answer
.venv/bin/python -m labs.week_11.demo --scenario malicious-document --output-dir .runtime/week11-malicious --show-answer
.venv/bin/python -m labs.week_11.demo --scenario detector-miss --output-dir .runtime/week11-miss --show-answer
.venv/bin/python -m labs.week_11.demo --scenario poisoned-fact --output-dir .runtime/week11-poisoned --show-answer
.venv/bin/python -m pytest tests/test_week11_security.py -q
```

Each case writes `event.json`. A refused request is a normal completed application outcome and exits zero in these fixtures. Adapter/runtime failures propagate; they are not disguised as successful answers. Reusing an output directory fails without overwriting earlier evidence.

| Scenario | Expected observation | What it establishes |
| --- | --- | --- |
| `clean` | One allowed Net 30 quote | Permitted retrieval still works |
| `tenant-scope` | South's Net 15, without North's Net 30 | Same principal/document names remain tenant-scoped |
| `direct-injection` | `input_blocked` | A known input pattern is screened before responder work |
| `forged-identity` | `input_invalid` | The body cannot supply a tenant field |
| `malicious-document` | Good answer; one permitted chunk excluded | Known indirect-injection content is removed before context |
| `sensitive-document` | `no_context`; one chunk excluded | The declared email-like fixture rule is applied |
| `tampered` | `no_context` | A changed representation fails the protected pin |
| `action-proposal` | `output_blocked` | Extra action fields cannot extend the response contract |
| `revocation` | `source_changed` | A trusted update is noticed before returning evidence |
| `tight-context` | `no_context` | A budget failure does not trigger model-only fallback |
| `detector-miss` | Scanner misses the query pattern; output still blocked | Independent enforcement remains useful after a detector miss |
| `benign-quotation` | Legitimate training text excluded | The scanner has a known false positive |
| `poisoned-fact` | False Net 1 quote returned | Consistency/permission checks cannot certify source truth |

Inspect a saved event after running `clean`:

```python
import json
from pathlib import Path

event = json.loads(Path(".runtime/week11-clean/event.json").read_text())
assert event["outcome"] == "answered"
assert event["candidate_count"] == event["citation_count"] == 1
assert set(event) == {
    "schema", "request_id", "outcome", "reason",
    "candidate_count", "citation_count", "blocked_chunk_count",
}
```

The [lab README](https://github.com/kogantisasank831-ux/Prep/tree/main/labs/week_11) maps code responsibilities and verification commands. `policy.py` owns identity/catalogue/input rules; `assistant.py` owns the guarded retrieval/response flow; `fixtures.py` and `demo.py` supply only controlled scenarios. Earlier labs and assessments remain independent.

## Evaluate the controls without overstating the result

A useful security test records the actor, controlled input, crossed boundary, expected outcome and actual observable effect. Test benign utility as well as denied behavior. All refusals could look secure while making the assistant useless; all exact citations could look grounded while quoting poisoned facts.

For a real model-backed evaluation, define attack success concretely: unauthorized source disclosure, an unauthorized action reaching its sink, forbidden output, or another policy-specific effect. Preserve model/prompt/index/policy identities, attack families, attempts and denominators. Include clean paired cases, false positives and adaptive variants under an explicit budget. Do not label a regex match rate or a scripted schema rejection as an LLM attack-success rate.

This build exercises real local parsing, source scope, retrieval, citations, resource bounds and output checks against synthetic cases. It does not scan a deployed target, parse arbitrary malicious PDFs, measure model susceptibility or certify production security. Revisit the threat model when adding a provider, tool, data connector, cache, history store or new tenant boundary.

## Practice and prepare for interviews

**Exercise 1 — Draw the authority path.** Describe the malicious addendum from ingestion to proposed export. Acceptance: identify the attacker-controlled bytes, independently controlled catalogue, trusted identity and the absent/denied action capability. Keep permission to read distinct from permission to act.

**Exercise 2 — Prove the source boundary.** Compare North and South with the same principal/document names. Add/remove the private distractor. Acceptance: only the chosen tenant's permitted version reaches the responder; allowed results and safe event fields remain unchanged when the denied distractor is absent.

**Exercise 3 — Challenge the detector.** Retain one detected malicious phrase, the spaced-out miss and the benign quotation false positive. Acceptance: state each actual finding and consequence; demonstrate independent rejection of the action proposal without claiming that every encoded attack is prevented.

**Exercise 4 — Separate consistency from truth.** Run `tampered` and `poisoned-fact`. Acceptance: explain why one is excluded while the other is returned, and propose an independent source-review/evaluation step rather than changing the digest to make a bad baseline pass.

**Exercise 5 — Test the response boundary.** Propose changed text under a valid label, an unknown action field and a response after revocation. Acceptance: all are refused without raw payload in saved diagnostics; the normal allowed quote still works. Explain why a later HTML consumer requires its own rendering control.

| Interview prompt | Reasoning to include |
| --- | --- |
| Why isn't a hidden system prompt a complete security control? | Prompt content does not enforce caller/resource permissions or bound downstream effects; enforce those independently and keep credentials outside model context. |
| How do you secure retrieval in a multi-tenant system? | Derive trusted tenant/principal context, apply current full source-version grants before retrieval, propagate that scope through rerank/context/output and test negative cases. |
| Does an approved digest make a source safe? | It detects drift from that baseline. The baseline itself may contain false facts or malicious instructions and needs separate review. |
| How would you measure a guardrail? | Define forbidden effects, matched benign cases, attack families, versions and attempt denominators; report misses and utility loss separately. |
| What happens after a detector miss? | Independent schemas, scope checks, least-privilege capabilities and effect-time authorization still constrain what the application accepts or executes. |
| What does your revocation test prove? | The local implementation rechecks supplied evidence before return; it cannot retract previously forwarded data or establish distributed atomic revocation. |

Close the lesson and explain how a request can be operationally successful, fully cited, permitted and still wrong. Then explain which independent controls stop the same request from obtaining another tenant's data or triggering an export.

Keep the guarded assistant, synthetic case outcomes, a small threat register and the benign/malicious comparison as your weekly deliverable. Week 12 will put a service around the pipeline; this week's authority and failure boundaries should survive that packaging. Use the assessment to check the same boundaries in concepts and Python syntax.

## Sources and further reading

- [OWASP prompt injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/) — direct/indirect entry points and application-dependent impact.
- [OWASP authorization](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html) — identity versus permission, default denial and per-request checks.
- [OWASP RAG security](https://cheatsheetseries.owasp.org/cheatsheets/RAG_Security_Cheat_Sheet.html) — protected source baselines, inherited access scope and derived-state risks.
- [OWASP prompt-injection prevention](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html) — layered screening, output and effect boundaries.
- [Python JSON](https://docs.python.org/3.13/library/json.html) and [HTML escaping](https://docs.python.org/3.13/library/html.html) — parser behavior and context-specific text handling.
- [Week 10 observability]({{ '/weeks/week-10/' | relative_url }}) — versioned observations and payload-minimizing diagnostics.
