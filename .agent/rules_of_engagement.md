# Rules of Engagement: Antigravity Orchestrator

This document defines the operational boundaries for AI agents working on this codebase.

## 🚀 Proactive Actions (No Approval Required)
The agent is authorized to proceed with the following without prior intervention:
- **Documentation Updates**: Improving comments, READMEs, or system reports.
- **Minor Housekeeping**: Fixing typos, improving variable naming for clarity, or adding logging.
- **Verification**: Running tests, checking service status, or performing diagnostic searches.

## 🛑 Guardrails (Approval Required)
The agent **MUST** present an `implementation_plan.md` and wait for explicit user approval (e.g., "LGTM") before:
- **Executing Plans**: Any multi-file logic changes or functional code modifications.
- **Architectural Changes**: Modifying service communication, database schemas, or core engine logic.
- **System Destabilization**: Terminating processes, deleting significant code, or changing primary entry points.

## 📝 Planning Protocol
1. **Research**: Thoroughly analyze the existing state.
2. **Design**: Draft an `implementation_plan.md` detailing the "Why" and "How".
3. **Approval**: Use `notify_user` to request review.
4. **Execution**: Proceed only after user confirmation.
