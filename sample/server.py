from mcp.server.mcpserver import MCPServer

mcp = MCPServer("Customer Support Server")

# sample customer data
# Demo customer database
CUSTOMERS = [
    {
        "id": "C001",
        "name": "Alice",
        "email": "alice1@example.com",
        "history": "3 purchases, 1 support ticket",
        "risk": "Low",
    },
    {
        "id": "C002",
        "name": "Bob",
        "email": "bob@example.com",
        "history": "7 purchases, 0 support tickets",
        "risk": "Medium",
    },
    {
        "id": "C003",
        "name": "Charlie",
        "email": "charlie@example.com",
        "history": "2 purchases, 4 support tickets",
        "risk": "High",
    },
    {
        "id": "C004",
        "name": "Alice",
        "email": "alice2@example.com",
        "history": "5 purchases, 2 support tickets",
        "risk": "Medium",
    },
]

@mcp.tool()
def search_customer(name: str) -> list[dict]:
    """
    Search customer by name

    Only non-densitive info is returned to handle the case of identical customers
    """
    # TODO: Need to main case sensitivity for names

    return [
        {
            "id": customer["id"],
            "name": customer["name"],
        }

        for customer in CUSTOMERS
        if name.lower() in customer["name"].lower()
    ]

@mcp.tool()
def get_customer_history(customer_id: str) -> str:
    """
    Get customer history by ID
    """

    for customer in CUSTOMERS:
        if customer["id"] == customer_id:
            return customer["history"]

    return "Customer not found"

@mcp.tool()
def calculate_risk(customer_id: str) -> str:
    """
    Calculated churn risk for a specific customer
    """

    for customer in CUSTOMERS:
        if customer["id"] == customer_id:
            return customer["risk"]

    return "Customer details not found!!"


if __name__ == "__main__":
    mcp.run()
