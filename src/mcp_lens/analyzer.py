def check_ambiguous_customer(trace):
    """
    Detect when a customer search returns multiple matches.
    """

    if trace["tool"] != "search_customer":
        return None

    result = trace.get("result", {})
    customers = result.get("result", [])

    if len(customers) > 1:
        return {
            "type": "AMBIGUOUS_RESULT",
            "severity": "warning",
            "message": (
                f"Search returned {len(customers)} customers "
                "with the same name."
            ),
            "recommendation": (
                "Ask the user to clarify which customer "
                "they mean before accessing customer data."
            ),
        }

    return None

def check_unsafe_followup(search_trace, followup_trace):
    """Detect selecting a customer after an ambiguous search."""

    if search_trace["tool"] != "search_customer":
        return None

    result = search_trace.get("result", {})
    customers = result.get("result", [])

    if len(customers) <= 1:
        return None

    selected_id = followup_trace.get("arguments", {}).get("customer_id")

    valid_ids = {
        customer["id"]
        for customer in customers
    }

    if selected_id in valid_ids:
        return {
            "type": "AMBIGUOUS_SELECTION",
            "severity": "high",
            "message": (
                f"The search returned {len(customers)} "
                f"customers, but the next tool call selected "
                f"{selected_id} without clarification."
            ),
            "recommendation": (
                "Require disambiguation before accessing "
                "customer-specific information."
            ),
        }

    return None