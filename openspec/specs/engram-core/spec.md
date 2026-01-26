# engram-core

## Requirements

### Requirement: Hyper-connection Branching
The system SHALL support branching hidden states.

#### Scenario: Forward pass
- **WHEN** hidden states are provided
- **THEN** it must maintain dimensions

### Requirement: N-gram Hash Mapping
The system SHALL implement deterministic hashing using primes and bitwise XOR.

#### Scenario: Hashing tokens
- **WHEN** tokens are processed
- **THEN** it must generate unique, deterministic prime-weighted XOR hashes

#### Scenario: Project Context Integration
- **WHEN** project files are scanned
- **THEN** the system must generate a "Neural Fingerprint" for the codebase

### Requirement: Context Resilience
The system SHALL maintain context awareness for up to 8192 tokens.

#### Scenario: Long-range memory
- **WHEN** tokens exceed standard attention windows
- **THEN** it must utilize Neural Engram Memory for retrieval
