# Delivery contract: a tool the owner can use

Business task: Log transformer loads and monitor capacity against limits across Tompkins County

## Required finished product

Deliver a working, importable workflow with its real steps connected, plus a simple intake and results/review surface. An existing business app or workflow form is sufficient when it covers the whole journey; build a small browser interface only for gaps. The owner must not edit workflow nodes for each run.
These delivery requirements are mandatory; task-specific notes and component installation instructions supplement them and cannot redefine completion.
Keep the recommended agents, skills, models, connectors and safeguards behind that interface. The coding assistant builds the product; it must not become the product's only runtime. A plugin, prompt collection, agent definition, notebook, CLI-only script or one completed task is not the finished product.
Use the smallest implementation that supports the actual business task. Do not add agents or AI to a fixed-rules design. Preserve the recommended execution logic; an interface is a usability layer, not a reason to change the topology.

## Build through to a usable handoff

1. Choose the simplest suitable user surface and state that choice in one sentence. Ask only questions that block a correct implementation; choose reversible defaults for layout, file names and local setup.
2. Implement runnable application/workflow code, dependencies, input validation, task processing, output handling and recoverable error states. Adapt the supplied scaffolds; they are starting material, not an exhaustive file list. Do not stop because those files already exist.
3. Build the first complete input-to-output path with clearly labeled synthetic sample data. Let the owner use it before asking for a large evaluation dataset. Then connect the real processing and approved services; do not pass off canned output as live processing.
4. Put required human decisions in visible Review, Approve and Request changes controls. Enforce approval in the workflow/backend before the protected action, not only in prompts. Match the recommended autonomy level; omit unnecessary approval steps for other actions.
5. Handle setup once, behind a clear setup screen or short owner action. Verify supported APIs, provider model IDs and runtime availability. A chat subscription does not automatically supply API access or unattended execution. Explain any new account, hosting or running cost before enabling it; do not invent a connector or automate a chat UI as the backend.
6. Run the application and test the actual user path, including a second fresh task after restarting, missing input, processing failure and any approval bypass attempt. Record observed results, not an unexecuted checklist.
7. Leave a working local launch link or launcher and START-HERE.md with at most three everyday-use steps, plus how to reopen, stop and recover the tool. For a hosted workflow, give its actual tested entry point. Keep source/configuration details in developer documentation. Do not publish, send, purchase or modify live records without the owner's authorization.

## Completion evidence

Write DELIVERY-REPORT.md containing the launch location, files built, tests actually run and their outcomes, a sample input and saved output, setup remaining, and one of these honest statuses:
- READY: the intended processing and user journey were tested with configured services or real local processing. The owner can repeat the task independently after the coding chat ends.
- DEMO ONLY: the interface works on explicitly labeled fixtures, but real processing or integrations remain unverified. Clearly distinguish sample output from actual results everywhere relevant.
- BLOCKED: name the exact unavailable dependency or owner decision and the shortest action that resolves it. Complete independent implementation work before stopping.
Never report READY for a scaffold, an import that has not run, mocked AI output, untested credentials, or a skill that only runs when the owner types a special command into the coding assistant.
For this scheduled design: implement and test the actual scheduler outside the coding chat, display next/last run and failures, and provide a pause control. A conversational promise to run later is not a scheduler.

## Example of the intended experience

For resume tailoring, the owner opens a page, supplies a resume and job description, selects Create draft, reviews supported changes, requests edits or approves, and downloads the document. The processing, source checks and review record run behind the page. Delivering one PDF and telling the owner to type /approve in a coding chat does not meet this contract.

## About this download

This package is a build kit, not a completed or verified application. Give BUILD.md to a coding assistant with file and execution access and have it build to this contract. If you downloaded a component alone, use it with the full kit for the architecture and safeguards; do not mistake installing that component for completing the application.