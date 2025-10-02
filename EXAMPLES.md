# Wakalat-AI Usage Examples

This document provides practical examples of using the Wakalat-AI MCP Server.

## Example 1: Searching for Precedents

### Query
```json
{
  "tool": "search_precedents",
  "arguments": {
    "query": "breach of employment contract and damages",
    "jurisdiction": "supreme_court",
    "year_from": 2015,
    "year_to": 2024,
    "max_results": 5
  }
}
```

### Use Case
A lawyer is preparing arguments for a case involving breach of employment contract and wants to find Supreme Court precedents from the last 9 years.

---

## Example 2: Finding a Specific Case Law

### Query
```json
{
  "tool": "find_case_laws",
  "arguments": {
    "citation": "AIR 2021 SC 4312",
    "include_summary": true
  }
}
```

### Use Case
Need the full details and AI-generated summary of a specific Supreme Court judgment.

---

## Example 3: Checking Limitation Period

### Query
```json
{
  "tool": "check_limitation",
  "arguments": {
    "case_type": "suit_for_money_lent",
    "cause_of_action_date": "2021-03-15",
    "special_circumstances": "Borrower was out of country"
  }
}
```

### Use Case
Client wants to file a suit for money lent. Check if it's within the limitation period.

### Response (Example)
```json
{
  "case_type": "suit_for_money_lent",
  "limitation_period": "3 years",
  "limitation_expires_on": "2024-03-15",
  "days_remaining": 45,
  "is_within_limitation": true,
  "status": "Within limitation period"
}
```

---

## Example 4: Analyzing a Legal Document

### Query
```json
{
  "tool": "analyze_document",
  "arguments": {
    "document_path": "/path/to/contract.pdf",
    "document_type": "contract",
    "analysis_type": "full"
  }
}
```

### Use Case
Client has received an employment contract and wants it reviewed for potential issues and compliance.

---

## Example 5: Conducting Legal Research

### Query
```json
{
  "tool": "legal_research",
  "arguments": {
    "research_query": "What is the liability of an employer for acts of employees under vicarious liability in Indian tort law?",
    "research_depth": "comprehensive",
    "include_statutes": true,
    "include_case_laws": true
  }
}
```

### Use Case
Preparing for a tort case and need comprehensive research on vicarious liability principles in India.

---

## Example 6: Drafting a Legal Notice

### Query
```json
{
  "tool": "draft_legal_notice",
  "arguments": {
    "notice_type": "demand",
    "facts": "On June 15, 2023, our client engaged the services of your company for software development. The project was completed on August 30, 2023. Despite multiple reminders, the payment of Rs. 5,00,000 remains outstanding.",
    "relief_sought": "Payment of Rs. 5,00,000 along with interest at 18% per annum from the due date, within 15 days of receipt of this notice.",
    "sender_details": {
      "name": "Advocate Rajesh Kumar",
      "address": "123 Court Road, Mumbai"
    },
    "recipient_details": {
      "name": "XYZ Software Pvt. Ltd.",
      "address": "456 Tech Park, Bangalore"
    }
  }
}
```

### Use Case
Client needs to send a formal legal notice for recovery of payment.

---

## Example 7: Complex Precedent Search with Multiple Filters

### Query
```json
{
  "tool": "search_precedents",
  "arguments": {
    "query": "Section 138 Negotiable Instruments Act dishonour of cheque",
    "jurisdiction": "all",
    "year_from": 2018,
    "max_results": 20
  }
}
```

### Use Case
Building a case for cheque bounce under NI Act and need comprehensive precedents.

---

## Example 8: Research on Specific Legal Provision

### Query
```json
{
  "tool": "find_case_laws",
  "arguments": {
    "legal_provision": "Section 420 IPC",
    "include_summary": true
  }
}
```

### Use Case
Understanding how Section 420 (Cheating) has been interpreted by courts.

---

## Integration with MCP Clients

### Using with Claude Desktop

1. Add to your Claude Desktop config:
```json
{
  "mcpServers": {
    "wakalat-ai": {
      "command": "python",
      "args": ["-m", "src.server"],
      "cwd": "/path/to/Wakalat-AI-Backend",
      "env": {
        "OPENAI_API_KEY": "your-key"
      }
    }
  }
}
```

2. Then in Claude, you can ask:
```
"Search for Supreme Court precedents on workplace sexual harassment cases from 2015 onwards"
```

### Using with Custom Python Client

```python
import asyncio
from mcp.client import Client

async def main():
    async with Client() as client:
        # Connect to server
        await client.connect("python", ["-m", "src.server"])
        
        # List available tools
        tools = await client.list_tools()
        print("Available tools:", [t.name for t in tools])
        
        # Call a tool
        result = await client.call_tool(
            "search_precedents",
            {
                "query": "breach of contract",
                "max_results": 5
            }
        )
        print("Results:", result)

asyncio.run(main())
```

---

## Common Workflows

### Workflow 1: Case Preparation
1. **Research the legal issue** → `legal_research`
2. **Find relevant precedents** → `search_precedents`
3. **Get specific case details** → `find_case_laws`
4. **Check limitation** → `check_limitation`
5. **Draft notice/petition** → `draft_legal_notice`

### Workflow 2: Contract Review
1. **Analyze contract** → `analyze_document`
2. **Research specific clauses** → `legal_research`
3. **Find precedents on similar issues** → `search_precedents`

### Workflow 3: Due Diligence
1. **Check limitation periods** → `check_limitation`
2. **Find relevant case laws** → `find_case_laws`
3. **Analyze existing documents** → `analyze_document`

---

## Tips for Best Results

1. **Be Specific in Queries**: Include relevant legal terms and provisions
2. **Use Filters**: Narrow down results with jurisdiction and year filters
3. **Combine Tools**: Use multiple tools in sequence for comprehensive analysis
4. **Verify Results**: Always verify AI-generated content with original sources
5. **Include Context**: Provide relevant context in research queries

---

## Troubleshooting

### Tool Not Found
- Ensure the feature flag is enabled in `.env`
- Check that the server is running correctly

### No Results
- Try broader search terms
- Adjust year filters
- Check jurisdiction filters

### Timeout
- Reduce `max_results` parameter
- Use more specific queries
- Check API rate limits

---

For more examples and updates, see the [GitHub repository](https://github.com/BE-project-vesit/Wakalat-AI-Backend).
