import { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  ChevronLeft,
  FileCode,
  Wrench,
  Terminal,
  Copy,
  ExternalLink,
} from "lucide-react";
import { PromptsService, McpService } from "@/fastapi_client";

interface Prompt {
  name: string;
  description: string;
  filename: string;
}

interface PromptDetail {
  name: string;
  content: string;
}

interface MCPItem {
  name: string;
  description: string;
}

interface MCPConfig {
  servername: string;
  databricks_host: string;
  is_databricks_app: boolean;
  client_path: string;
}

export function PromptsPage() {
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [mcpPrompts, setMcpPrompts] = useState<MCPItem[]>([]);
  const [mcpTools, setMcpTools] = useState<MCPItem[]>([]);
  const [servername, setServername] = useState<string>("");
  const [mcpConfig, setMcpConfig] = useState<MCPConfig | null>(null);
  const [selectedPrompt, setSelectedPrompt] = useState<PromptDetail | null>(
    null,
  );
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      // Fetch prompts from prompts directory
      const promptsResponse = await PromptsService.listPromptsApiPromptsGet();
      setPrompts(promptsResponse);

      // Fetch MCP discovery info
      const mcpResponse =
        await McpService.getMcpDiscoveryApiMcpInfoDiscoveryGet();
      if (mcpResponse.prompts) {
        setMcpPrompts(mcpResponse.prompts);
      }
      if (mcpResponse.tools) {
        setMcpTools(mcpResponse.tools);
      }
      if (mcpResponse.servername) {
        setServername(mcpResponse.servername);
      }

      // Fetch MCP config for setup instructions
      const configResponse = await McpService.getMcpConfigApiMcpInfoConfigGet();
      setMcpConfig(configResponse);
    } catch (err) {
      setError("Failed to load data");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchPromptDetail = async (promptName: string) => {
    try {
      const response =
        await PromptsService.getPromptApiPromptsPromptNameGet(promptName);
      setSelectedPrompt(response);
    } catch (err) {
      setError("Failed to load prompt detail");
      console.error(err);
    }
  };

  const fetchMcpPromptDetail = async (promptName: string) => {
    try {
      const response = await fetch(`/api/mcp_info/prompt/${promptName}`);
      if (!response.ok) throw new Error("Failed to fetch prompt");
      const data = await response.json();
      setSelectedPrompt(data);
    } catch (err) {
      setError("Failed to load MCP prompt detail");
      console.error(err);
    }
  };

  const handleBack = () => {
    setSelectedPrompt(null);
    setError(null);
  };

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      // You could add a toast notification here
    } catch (err) {
      console.error("Failed to copy text: ", err);
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto py-8">
        <div className="text-center">Loading prompts...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto py-8">
        <div className="text-center text-red-500">{error}</div>
      </div>
    );
  }

  if (selectedPrompt) {
    return (
      <div className="container mx-auto py-8 max-w-4xl">
        <Button variant="ghost" onClick={handleBack} className="mb-6">
          <ChevronLeft className="mr-2 h-4 w-4" />
          Back to prompts
        </Button>

        <Card>
          <CardHeader>
            <CardTitle>
              {selectedPrompt.name
                .replace(/_/g, " ")
                .replace(/\b\w/g, (l) => l.toUpperCase())}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="whitespace-pre-wrap font-mono text-sm bg-muted p-4 rounded-lg">
              {selectedPrompt.content}
            </pre>
          </CardContent>
        </Card>
      </div>
    );
  }

  const getMcpSetupCommand = () => {
    if (!mcpConfig) return "";

    // Use the current URL as the Databricks app URL
    const databricksAppUrl = window.location.origin;

    // Use the actual values from the API
    const databricksHost = mcpConfig.databricks_host;

    // Use the correct uvx command from the README with actual values
    return `claude mcp add ${mcpConfig.servername} --scope user -- \\
  uvx --from git+ssh://git@github.com/databricks-solutions/custom-mcp-databricks-app.git dba-mcp-proxy \\
  --databricks-host ${databricksHost} \\
  --databricks-app-url ${databricksAppUrl}`;
  };

  return (
    <div className="container mx-auto py-8">
      <h1 className="text-3xl font-bold mb-8">MCP Discovery</h1>

      {/* MCP Setup Instructions Section */}
      {mcpConfig && (
        <div className="mb-12">
          <h2 className="text-2xl font-semibold mb-4 flex items-center gap-2">
            <Terminal className="h-6 w-6" />
            Claude Code MCP Setup
          </h2>

          <Card>
            <CardHeader>
              <CardTitle>Add this MCP server to Claude Code</CardTitle>
              <CardDescription>
                Run this command in your terminal to add the MCP server to
                Claude Code CLI using uvx
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="bg-muted p-4 rounded-lg font-mono text-sm relative group">
                <pre className="whitespace-pre-wrap">
                  {getMcpSetupCommand()}
                </pre>
                <Button
                  variant="ghost"
                  size="sm"
                  className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity"
                  onClick={() => copyToClipboard(getMcpSetupCommand())}
                >
                  <Copy className="h-4 w-4" />
                </Button>
              </div>
              <p className="text-sm text-muted-foreground mt-3">
                This command uses uvx to run the dba-mcp-proxy from the git
                repository. After adding, restart Claude Code to enable the MCP
                integration. Then you can use slash commands like{" "}
                <code>/{servername}:ping_google</code>.
              </p>
              <div className="mt-4 pt-3 border-t">
                <a
                  href="https://github.com/databricks-solutions/custom-mcp-databricks-app"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 text-sm text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
                >
                  <ExternalLink className="h-4 w-4" />
                  View documentation and source code on GitHub
                </a>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Unified Prompts Section */}
      <div className="mb-12">
        <h2 className="text-2xl font-semibold mb-4 flex items-center gap-2">
          <FileCode className="h-6 w-6" />
          MCP Prompts (Slash Commands)
        </h2>

        {mcpPrompts.length === 0 ? (
          <div className="text-center text-muted-foreground mb-8">
            No MCP prompts found.
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 mb-8">
            {mcpPrompts.map((prompt) => (
              <Card
                key={prompt.name}
                className="cursor-pointer hover:shadow-lg transition-shadow"
                onClick={() => fetchMcpPromptDetail(prompt.name)}
              >
                <CardHeader>
                  <CardTitle className="text-lg">
                    /{servername}:{prompt.name}
                  </CardTitle>
                  <CardDescription>{prompt.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">
                    Click to view prompt content
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* MCP Tools Section */}
      <div className="mb-12">
        <h2 className="text-2xl font-semibold mb-4 flex items-center gap-2">
          <Wrench className="h-6 w-6" />
          MCP Tools
        </h2>

        {mcpTools.length === 0 ? (
          <div className="text-center text-muted-foreground mb-8">
            No MCP tools found.
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 mb-8">
            {mcpTools.map((tool) => (
              <Card key={tool.name}>
                <CardHeader>
                  <CardTitle className="text-lg">{tool.name}</CardTitle>
                  <CardDescription className="whitespace-pre-line">
                    {tool.description}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">
                    Available as MCP tool
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
