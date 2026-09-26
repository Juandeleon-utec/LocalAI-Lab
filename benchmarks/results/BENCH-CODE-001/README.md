# BENCH-CODE-001 Results

Formal and engineering run artifacts for BENCH-CODE-001 will be stored here after the protocol inputs are frozen.

Recommended layout:

```text
BENCH-CODE-001/
├── C001-A01/
│   ├── manifest.json
│   ├── test-results.json
│   ├── test-output.txt
│   ├── agent-summary.md
│   └── review.md
├── C001-A02/
├── C001-A03/
├── C001-B01/
├── C001-B02/
├── C001-B03/
├── C001-C01/
├── C001-C02/
├── C001-C03/
└── ...
```

Large candidate repositories, raw high-frequency telemetry and hidden evaluator archives may be stored outside normal Git when necessary. They must be checksummed and referenced from each run manifest.

Do not place the executable hidden evaluator in a participant-visible workspace.
