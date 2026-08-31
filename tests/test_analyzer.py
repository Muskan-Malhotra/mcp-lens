from mcp_lens.analyzer import (
    check_ambiguous_customer,
    check_unsafe_followup,
)


def test_unique_customer_is_not_ambiguous():
    trace = {
        "tool": "search_customer",
        "result": {
            "result": [
                {"id": "C002", "name": "Bob"}
            ]
        },
    }

    finding = check_ambiguous_customer(trace)

    assert finding is None


def test_duplicate_customer_is_detected():
    trace = {
        "tool": "search_customer",
        "result": {
            "result": [
                {"id": "C001", "name": "Alice"},
                {"id": "C004", "name": "Alice"},
            ]
        },
    }

    finding = check_ambiguous_customer(trace)

    assert finding is not None
    assert finding["type"] == "AMBIGUOUS_RESULT"
    assert finding["severity"] == "warning"


def test_agent_selecting_from_ambiguous_results_is_detected():
    search_trace = {
        "tool": "search_customer",
        "result": {
            "result": [
                {"id": "C001", "name": "Alice"},
                {"id": "C004", "name": "Alice"},
            ]
        },
    }

    followup_trace = {
        "tool": "get_customer_history",
        "arguments": {
            "customer_id": "C001"
        },
    }

    finding = check_unsafe_followup(
        search_trace,
        followup_trace,
    )

    assert finding is not None
    assert finding["type"] == "AMBIGUOUS_SELECTION"
    assert finding["severity"] == "high"


def test_no_unsafe_selection_when_search_is_unique():
    search_trace = {
        "tool": "search_customer",
        "result": {
            "result": [
                {"id": "C002", "name": "Bob"}
            ]
        },
    }

    followup_trace = {
        "tool": "get_customer_history",
        "arguments": {
            "customer_id": "C002"
        },
    }

    finding = check_unsafe_followup(
        search_trace,
        followup_trace,
    )

    assert finding is None