# ProjectX-Ray Methodology

ProjectX-Ray evaluates a software project idea using structured, explainable dimensions instead of returning an unexplained single verdict.

## Analysis dimensions

### 1. Feasibility

Estimates how practical the idea appears from the supplied description, scope signals, and technology stack.

### 2. Technical risk

Looks for implementation and domain signals that can introduce substantial engineering, reliability, privacy, safety, or validation challenges.

### 3. Originality

Screens for generic/common project patterns and rewards clear differentiators. This is a heuristic screening signal, not a proof of uniqueness.

### 4. Scope clarity

Checks whether the project has a sufficiently clear action, implementation direction, and manageable MVP boundary.

### 5. Target-user fit

Checks whether the intended users are specific enough to support meaningful validation and product decisions.

## Explainability

Every dimension returns a score, level, and reasons. The system can also return risk flags and prioritized recommendations.

This makes it possible for a user to challenge a result, improve the project description, or narrow the scope instead of simply accepting a final verdict.

## Recommendation logic

Recommendations are contextual. Examples include:

- student/final-year project ideas → personalization, ranking criteria, MVP boundaries, milestones, project knowledge base, and pilot validation
- healthcare/medical → privacy, consent, safety, validation, and regulatory boundaries
- financial/payment → authentication, auditability, idempotency, fraud controls, and failure recovery
- biometric/face recognition → accuracy, bias, consent, data minimization, and deletion
- real-time systems → latency, concurrency, failure handling, and load testing
- IoT → connectivity, offline behavior, firmware, telemetry, and secure authentication
- ML/prediction/detection → representative data, baselines, evaluation metrics, and false-positive/false-negative analysis

## Important limitation

The current engine is deterministic and transparent. Its output should be treated as project-screening guidance, not as proof that a project will succeed, be original, or satisfy production requirements.
