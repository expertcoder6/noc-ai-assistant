# Tuple format: (regex_pattern, pattern_label)
BLOCKED_PATTERNS = [
    (r"ignore\s+(previous|all|above)\s+instructions", "instruction_override"),
    (r"reveal\s+(system|your|the)\s+prompt", "prompt_extraction"),
    (r"what\s+is\s+(your|the)\s+system\s+prompt", "prompt_extraction"),
    (r"\bdrop\s+table\b", "sql_injection"),
    (r"\bdelete\s+(from|database)\b", "sql_injection"),
    (r"\btruncate\s+table\b", "sql_injection"),
    (r"\bunion\s+(all\s+)?select\b", "sql_injection"),
    (r"\binformation_schema\b", "schema_probe"),
    (r"\bpg_catalog\b", "schema_probe"),
    (r"\bpg_tables\b", "schema_probe"),
    (r"\bshow\s+(tables|schema|databases)\b", "schema_probe"),
    (r"\bbypass\s+(security|auth|validation)\b", "bypass_attempt"),
    (r"you\s+are\s+now\s+", "role_override"),
    (r";\s*(drop|delete|insert|update|truncate)", "chained_sql"),
    (r"--\s*$", "sql_comment"),
]
