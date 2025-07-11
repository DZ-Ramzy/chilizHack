# AI Agent Workflow Patterns - Mermaid Diagrams

## 1. Augmented LLM Building Block

```mermaid
graph TD
    A[Input] --> B[LLM Core]
    B --> C[Retrieval]
    B --> D[Tool Usage]
    B --> E[Memory Generation]
    C --> F[Output]
    D --> F
    E --> F
```

## 2. Prompt Chaining Pattern

```mermaid
graph LR
    A[Initial Input] --> B[LLM Step 1]
    B --> C{Gate Check?}
    C -->|Pass| D[LLM Step 2]
    C -->|Fail| G[Error Handler]
    D --> E{Gate Check?}
    E -->|Pass| F[LLM Step 3]
    E -->|Fail| G
    F --> H[Final Output]
    G --> I[Retry/Alternative]
```

## 3. Routing Pattern

```mermaid
graph TD
    A[Input] --> B[Classifier LLM]
    B --> C{Input Type}
    C -->|Type A| D[Specialist LLM A]
    C -->|Type B| E[Specialist LLM B]
    C -->|Type C| F[Specialist LLM C]
    D --> G[Output A]
    E --> H[Output B]
    F --> I[Output C]
```

## 4. Parallelization Patterns

### 4a. Sectioning
```mermaid
graph TD
    A[Complex Task] --> B[Task Decomposer]
    B --> C[Subtask 1]
    B --> D[Subtask 2]
    B --> E[Subtask 3]
    C --> F[LLM Worker 1]
    D --> G[LLM Worker 2]
    E --> H[LLM Worker 3]
    F --> I[Result Synthesizer]
    G --> I
    H --> I
    I --> J[Final Output]
```

### 4b. Voting
```mermaid
graph TD
    A[Input Task] --> B[LLM Instance 1]
    A --> C[LLM Instance 2]
    A --> D[LLM Instance 3]
    B --> E[Output 1]
    C --> F[Output 2]
    D --> G[Output 3]
    E --> H[Voting Mechanism]
    F --> H
    G --> H
    H --> I[Best/Consensus Output]
```

## 5. Orchestrator-Workers Pattern

```mermaid
graph TD
    A[Complex Request] --> B[Orchestrator LLM]
    B --> C{Task Analysis}
    C --> D[Worker Assignment]
    D --> E[Worker LLM 1]
    D --> F[Worker LLM 2]
    D --> G[Worker LLM 3]
    E --> H[Result 1]
    F --> I[Result 2]
    G --> J[Result 3]
    H --> K[Orchestrator Synthesis]
    I --> K
    J --> K
    K --> L[Final Response]
```

## 6. Evaluator-Optimizer Pattern

```mermaid
graph LR
    A[Input] --> B[Generator LLM]
    B --> C[Initial Response]
    C --> D[Evaluator LLM]
    D --> E{Quality Check}
    E -->|Good| F[Final Output]
    E -->|Needs Improvement| G[Feedback]
    G --> B
    D --> H[Optimization Suggestions]
    H --> B
```

## 7. Autonomous Agent Pattern

```mermaid
graph TD
    A[Initial Human Instruction] --> B[Autonomous Agent]
    B --> C[Environment Interaction]
    C --> D[Action Execution]
    D --> E[Environment Feedback]
    E --> F{Ground Truth Verification}
    F -->|Valid| G[Continue to Next Action]
    F -->|Invalid| H[Error Correction]
    G --> C
    H --> I[Strategy Adjustment]
    I --> C
    E --> J[Learning/Memory Update]
    J --> B
```

## 8. Sports Quest AI System - Applied Pattern

```mermaid
graph TD
    A[Sports Event Trigger] --> B[Orchestrator Agent]
    B --> C[Team Existence Checker]
    B --> D[User Preference Analyzer]
    B --> E[Quest Generator]
    
    C --> F{Teams Exist?}
    F -->|Both Exist| G[Clash Quest Creator]
    F -->|One Exists| H[Single Team Quest Creator]
    
    D --> I[Community Segmentation]
    
    G --> J[Quest Distribution Engine]
    H --> J
    E --> J
    
    J --> K[Parallel Validation]
    K --> L[o3 mini Image Validator]
    K --> M[Content Quality Checker]
    K --> N[Preference Consistency Validator]
    
    L --> O[Validation Synthesizer]
    M --> O
    N --> O
    
    O --> P{All Valid?}
    P -->|Yes| Q[Mass Distribution]
    P -->|No| R[Rejection/Retry]
    
    Q --> S[Community Engagement Tracking]
    S --> T[Collective Progress Monitoring]
    T --> U[Real-time Metrics]
    
    R --> E
```