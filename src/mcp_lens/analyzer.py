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