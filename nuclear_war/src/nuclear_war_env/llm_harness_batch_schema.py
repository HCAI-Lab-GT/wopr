"""Schema fields for no-press LLM batch artifacts."""

BATCH_FIELDS = (
    "mode",
    "players",
    "seed_start",
    "runs",
    "max_turns",
    "config",
    "seat_config",
    "results",
    "summary",
)
RESULT_FIELDS = (
    "seed",
    "winner",
    "turns",
    "termination_reason",
    "elimination_order",
    "win_loss",
    "invalid_action_count",
    "retry_count",
    "trace_count",
    "player_decision_metrics",
    "replay_path",
    "trace_path",
)
OPTIONAL_RESULT_FIELDS = (
    "provider_latency_ms",
    "provider_cost",
)
RESULT_INT_FIELDS = (
    "seed",
    "turns",
    "invalid_action_count",
    "retry_count",
    "trace_count",
)
SUMMARY_FIELDS = (
    "runs",
    "agent_outcomes",
    "agent_decision_metrics",
    "winner_counts",
    "termination_counts",
    "average_turns",
    "total_eliminations",
    "total_invalid_action_count",
    "total_retry_count",
    "total_trace_count",
)
OPTIONAL_SUMMARY_FIELDS = (
    "total_provider_latency_ms",
    "total_provider_cost",
)
SUMMARY_INT_FIELDS = (
    "runs",
    "total_eliminations",
    "total_invalid_action_count",
    "total_retry_count",
    "total_trace_count",
)

__all__ = [
    "BATCH_FIELDS",
    "OPTIONAL_RESULT_FIELDS",
    "OPTIONAL_SUMMARY_FIELDS",
    "RESULT_FIELDS",
    "RESULT_INT_FIELDS",
    "SUMMARY_FIELDS",
    "SUMMARY_INT_FIELDS",
]
