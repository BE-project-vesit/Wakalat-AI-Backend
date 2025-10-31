# Firecrawl Precedent Search Setup

## ✅ What Changed

The `precedent_search` tool has been simplified to use **Firecrawl API** to scrape IndianKanoon for legal precedents.

## 🚀 Quick Setup (2 Steps)

### Step 1: Get Firecrawl API Key

1. Go to **https://firecrawl.dev**
2. Sign up for a free account
3. Copy your API key

### Step 2: Add to .env File

Open your `.env` file and add:

```bash
# Firecrawl API (for web scraping)
FIRECRAWL_API_KEY=your_actual_api_key_here
```

**That's it!** No databases, no embeddings, no complex setup.

## 🎯 How It Works

1. User asks: _"Search for precedents about Section 420 IPC"_
2. Tool builds IndianKanoon search URL
3. Firecrawl scrapes the search results page
4. Returns the content to Claude in markdown format

## 📝 Example Usage in Claude

Once connected to Claude Desktop:

- _"Search for precedents related to breach of contract"_
- _"Find Supreme Court precedents about Section 420 IPC"_
- _"Search for High Court cases on property disputes"_

Claude will automatically use the `search_precedents` tool.

## 🔧 Parameters

- **`query`**: What to search for (e.g., "Section 420 IPC")
- **`jurisdiction`**: Filter by court
  - `"all"` - All courts (default)
  - `"supreme_court"` - Supreme Court only
  - `"high_court"` - High Courts only
- **`max_results`**: Number of results (default: 5)
- **`year_from`** / **`year_to`**: Year filters (optional)

## 📊 Response Format

```json
{
  "query": "Section 420 IPC",
  "jurisdiction": "all",
  "source": "IndianKanoon via Firecrawl",
  "search_url": "https://indiankanoon.org/search/?formInput=...",
  "content": "...scraped search results...",
  "full_content_length": 5432
}
```

## ⚡ Why This Is Better

- ✅ **No timeouts** - Firecrawl handles the scraping
- ✅ **No embeddings** - No model loading delays
- ✅ **No databases** - No vector DB setup needed
- ✅ **Always fresh** - Real-time data from IndianKanoon
- ✅ **Simple** - Just one API key needed

## 🐛 Troubleshooting

### "FIRECRAWL_API_KEY not found"

→ Add your key to `.env` file

### "Firecrawl API error: 401"

→ Check your API key is correct

### "Request timeout"

→ Try a more specific query or check your internet connection

### "No results found"

→ Try rephrasing your query or use broader terms

## 💰 Firecrawl Pricing

- **Free tier**: 500 credits/month
- Each scrape = 1 credit
- Upgrade if needed: https://firecrawl.dev/pricing

## 🔄 Testing

After adding your API key:

1. **Restart Claude Desktop**
2. Ask: _"Search for precedents about contract law"_
3. Should return IndianKanoon search results

---

**No complex setup, no databases, just works!** 🎉
