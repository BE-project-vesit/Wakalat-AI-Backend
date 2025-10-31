# Connect Wakalat-AI to Claude Desktop

## Simple 3-Step Setup

### Step 1: Find Claude's Config File

Open this file in Notepad or VS Code:

```
%APPDATA%\Claude\claude_desktop_config.json
```

**Quick way to find it:**

1. Press `Win + R`
2. Type: `%APPDATA%\Claude`
3. Open `claude_desktop_config.json`

If the file doesn't exist, create it.

### Step 2: Add This Configuration

Copy and paste this into the config file:

```json
{
  "mcpServers": {
    "wakalat-ai": {
      "command": "uv",
      "args": ["run", "main.py"],
      "cwd": "D:\\projects\\python\\mcp\\wakalat\\Wakalat-AI-Backend"
    }
  }
}
```

**If you already have other servers configured**, just add the `wakalat-ai` entry inside `mcpServers`:

```json
{
  "mcpServers": {
    "existing-server": {
      "command": "...",
      "args": ["..."]
    },
    "wakalat-ai": {
      "command": "uv",
      "args": ["run", "main.py"],
      "cwd": "D:\\projects\\python\\mcp\\wakalat\\Wakalat-AI-Backend"
    }
  }
}
```

### Step 3: Restart Claude Desktop

1. Close Claude Desktop completely
2. Open it again
3. Your Wakalat-AI legal tools should now be available!

## How to Use in Claude

Once connected, you can ask Claude things like:

- "Search for precedents related to breach of contract"
- "Find case laws about Section 420 IPC"
- "Analyze this legal document for potential issues"
- "Research limitation periods for property disputes"
- "Draft a legal notice for contract breach"

Claude will automatically use your Wakalat-AI tools when needed.

## Troubleshooting

### Tools not showing up?

1. **Check if uv is installed:**
   ```powershell
   uv --version
   ```
2. **Make sure dependencies are installed:**

   ```powershell
   cd D:\projects\python\mcp\wakalat\Wakalat-AI-Backend
   uv sync
   ```

3. **Test the server manually:**

   ```powershell
   uv run main.py
   ```

   Should show: `Starting wakalat-ai-legal-assistant v1.0.0`

4. **Check Claude's logs:**
   - Look in `%APPDATA%\Claude\logs`
   - Check for connection errors

### Server starts but tools don't work?

- Make sure your `.env` file exists (copy from `.env.example`)
- Check that all required dependencies are installed
- Look for error messages in the terminal when testing manually

## Need Help?

Run the MCP Inspector to test your server:

```powershell
npx @modelcontextprotocol/inspector uv run main.py
```

This will open a web interface where you can test all tools interactively.
