# Workflow Checkpoints, Conditional Execution, and Partial Recovery

Sustainable Catalyst Lab v0.32.1 extends the typed workflow engine without introducing executable workflow code.

## Declarative conditions

A node condition may inspect only `run.inputs`, `run.context`, or prior `nodes.<id>` status and result values. Conditions support nested `all`, `any`, and `not` groups and a bounded set of operators: existence, truthiness, equality, ordered comparison, membership, and containment. A false condition records a durable `skipped` state and explanation rather than silently removing the node.

## Checkpoint history

Checkpoint records are immutable, ordered per node, content-hashed, and stored separately from final results. The orchestrator tracks the latest checkpoint on each node, can capture checkpoint payloads returned by the dispatcher, and retains checkpoint artifact references for later execution.

## Partial recovery

Recovery never rewrites the source run. It creates a new run and records the source run, source nodes, generation, operator, reason, restart set, reused nodes, and checkpoint choices. Successful nodes outside the restart closure are reused. Failed or selected nodes and their downstream dependents are reset to waiting and scheduled through the dispatcher. Eligible checkpoint state is inserted into the resumed workload context.

## Safety boundaries

- No arbitrary Python, JavaScript, shell commands, or callback URLs.
- Conditions are normalized and evaluated by an allowlisted interpreter.
- Recovery requires a terminal source run.
- Recovery and checkpoint mutations require authenticated administrative access through WordPress.
- Original runs, results, checkpoints, and timelines remain immutable and auditable.
