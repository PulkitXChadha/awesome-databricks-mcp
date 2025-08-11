import { useQuery } from "@tanstack/react-query";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { McpService } from "@/fastapi_client";
import {
  Code,
  ExternalLink,
  FileText,
  Play,
  Wrench,
  User,
  Sparkles,
  Bot,
  Terminal,
} from "lucide-react";

interface UserInfo {
  userName: string;
  displayName?: string;
  active: boolean;
  emails: string[];
}

async function fetchUserInfo(): Promise<UserInfo> {
  const response = await fetch("/api/user/me");
  if (!response.ok) {
    throw new Error("Failed to fetch user info");
  }
  return response.json();
}

export function WelcomePage() {
  const { data: userInfo } = useQuery({
    queryKey: ["userInfo"],
    queryFn: fetchUserInfo,
    retry: false,
  });

  const { data: mcpInfo } = useQuery({
    queryKey: ["mcpInfo"],
    queryFn: () => McpService.getMcpInfoApiMcpInfoInfoGet(),
    retry: false,
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex justify-center items-center gap-3 mb-4">
            <Sparkles className="h-10 w-10 text-blue-600" />
            <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Welcome to your Databricks FastAPI app!
            </h1>
          </div>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            A modern, full-stack application template with Python FastAPI
            backend and React TypeScript frontend
          </p>
        </div>

        {/* User Info Card */}
        {userInfo && (
          <Card className="mb-8 border-blue-200 bg-blue-50/50 dark:border-blue-800 dark:bg-blue-950/50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <User className="h-5 w-5" />
                Current User
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-4">
                <div>
                  <p className="font-semibold">
                    {userInfo.displayName || userInfo.userName}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    {userInfo.emails[0] || userInfo.userName}
                  </p>
                </div>
                <Badge variant={userInfo.active ? "default" : "secondary"}>
                  {userInfo.active ? "Active" : "Inactive"}
                </Badge>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Main Content Grid - First Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Getting Started */}
          <Card className="h-fit">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Play className="h-5 w-5" />
                Getting Started
              </CardTitle>
              <CardDescription>
                Everything you need to know to start developing
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h4 className="font-semibold mb-2">Development Commands</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between items-center">
                    <code className="bg-muted px-2 py-1 rounded text-xs">
                      ./setup.sh
                    </code>
                    <span className="text-muted-foreground">
                      Setup environment & dependencies
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <code className="bg-muted px-2 py-1 rounded text-xs">
                      ./watch.sh
                    </code>
                    <span className="text-muted-foreground">
                      Start dev servers (background)
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <code className="bg-muted px-2 py-1 rounded text-xs">
                      ./fix.sh
                    </code>
                    <span className="text-muted-foreground">
                      Format code (Python + TS)
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <code className="bg-muted px-2 py-1 rounded text-xs">
                      ./deploy.sh
                    </code>
                    <span className="text-muted-foreground">
                      Deploy to Databricks Apps
                    </span>
                  </div>
                </div>
              </div>

              <div>
                <h4 className="font-semibold mb-2">Development Ports</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between items-center">
                    <span>Frontend (React + Vite)</span>
                    <Badge variant="outline">:5173</Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span>Backend (FastAPI)</span>
                    <Badge variant="outline">:8000</Badge>
                  </div>
                </div>
              </div>

              <Button asChild className="w-full">
                <a
                  href="http://localhost:8000/docs"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <ExternalLink className="h-4 w-4 mr-2" />
                  Explore API Documentation
                </a>
              </Button>
            </CardContent>
          </Card>

          {/* Claude Commands */}
          <Card className="h-fit">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bot className="h-5 w-5" />
                Claude Commands
              </CardTitle>
              <CardDescription>
                Natural language commands for development workflow
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h4 className="font-semibold mb-2">Development</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between items-center">
                    <code className="bg-muted px-2 py-1 rounded text-xs">
                      "start the devserver"
                    </code>
                    <span className="text-muted-foreground">
                      Runs ./watch.sh
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <code className="bg-muted px-2 py-1 rounded text-xs">
                      "kill the devserver"
                    </code>
                    <span className="text-muted-foreground">
                      Stops background processes
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <code className="bg-muted px-2 py-1 rounded text-xs">
                      "fix the code"
                    </code>
                    <span className="text-muted-foreground">Runs ./fix.sh</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <code className="bg-muted px-2 py-1 rounded text-xs">
                      "deploy the app"
                    </code>
                    <span className="text-muted-foreground">
                      Runs ./deploy.sh
                    </span>
                  </div>
                </div>
              </div>

              <div>
                <h4 className="font-semibold mb-2">Development Tasks</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between items-center">
                    <code className="bg-muted px-2 py-1 rounded text-xs">
                      "add a new API endpoint"
                    </code>
                    <span className="text-muted-foreground">
                      Creates FastAPI routes
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <code className="bg-muted px-2 py-1 rounded text-xs">
                      "create a new React component"
                    </code>
                    <span className="text-muted-foreground">
                      Builds UI components
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <code className="bg-muted px-2 py-1 rounded text-xs">
                      "debug this error"
                    </code>
                    <span className="text-muted-foreground">
                      Analyzes and fixes issues
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <code className="bg-muted px-2 py-1 rounded text-xs">
                      "open the UI in playwright"
                    </code>
                    <span className="text-muted-foreground">
                      Opens app in browser
                    </span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* MCP Configuration */}
        {mcpInfo && (
          <Card className="mb-8 border-purple-200 bg-purple-50/50 dark:border-purple-800 dark:bg-purple-950/50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Terminal className="h-5 w-5" />
                MCP (Model Context Protocol) Server
              </CardTitle>
              <CardDescription>
                This app includes an MCP server that exposes prompts and tools to Claude Code
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h4 className="font-semibold mb-2">MCP Server URL</h4>
                <code className="bg-muted px-3 py-2 rounded block text-sm font-mono">
                  {mcpInfo.mcp_url}
                </code>
              </div>
              
              <div>
                <h4 className="font-semibold mb-2">Claude Code Configuration</h4>
                <p className="text-sm text-muted-foreground mb-2">
                  To use this MCP server with Claude Code, run:
                </p>
                <code className="bg-muted px-3 py-2 rounded block text-sm font-mono">
                  claude mcp add {mcpInfo.server_name || 'mcp-commands'} {mcpInfo.client_path || 'python mcp_databricks_client.py'}
                </code>
              </div>

              <div className="flex items-center gap-4">
                <Badge variant="outline">
                  Transport: {mcpInfo.transport}
                </Badge>
                {mcpInfo.capabilities?.prompts && (
                  <Badge variant="outline">Prompts ✓</Badge>
                )}
                {mcpInfo.capabilities?.tools && (
                  <Badge variant="outline">Tools ✓</Badge>
                )}
              </div>

              <Button asChild className="w-full">
                <a href="/prompts">
                  <ExternalLink className="h-4 w-4 mr-2" />
                  View Available Prompts & Tools
                </a>
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Second Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
          {/* Tech Stack */}
          <Card className="h-fit">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Code className="h-5 w-5" />
                Tech Stack
              </CardTitle>
              <CardDescription>
                Modern tools and frameworks for rapid development
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h4 className="font-semibold mb-3 text-blue-600">Backend</h4>
                  <ul className="space-y-2 text-sm">
                    <li className="flex items-center gap-2">
                      <Badge variant="secondary" className="text-xs">
                        Python
                      </Badge>
                      <span>FastAPI + uvicorn</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <Badge variant="secondary" className="text-xs">
                        Package
                      </Badge>
                      <span>uv for dependencies</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <Badge variant="secondary" className="text-xs">
                        SDK
                      </Badge>
                      <span>Databricks SDK</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <Badge variant="secondary" className="text-xs">
                        Quality
                      </Badge>
                      <span>ruff for linting</span>
                    </li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold mb-3 text-purple-600">
                    Frontend
                  </h4>
                  <ul className="space-y-2 text-sm">
                    <li className="flex items-center gap-2">
                      <Badge variant="secondary" className="text-xs">
                        React
                      </Badge>
                      <span>TypeScript + Vite</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <Badge variant="secondary" className="text-xs">
                        UI
                      </Badge>
                      <span>shadcn/ui + Tailwind</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <Badge variant="secondary" className="text-xs">
                        Data
                      </Badge>
                      <span>React Query</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <Badge variant="secondary" className="text-xs">
                        Package
                      </Badge>
                      <span>bun for speed</span>
                    </li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Project Structure */}
          <Card className="h-fit">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5" />
                Project Structure
              </CardTitle>
              <CardDescription>
                Understanding the codebase layout and key files
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-4 font-mono text-sm">
                <pre className="text-muted-foreground leading-relaxed">
                  {`├── server/                    # FastAPI backend
│   ├── app.py                 # Main application
│   ├── routers/               # API route handlers
│   │   ├── user.py           # User endpoints
│   │   └── insights.py       # Insights endpoints
│   └── models.py             # Data models
│
├── client/                    # React frontend
│   ├── src/
│   │   ├── pages/            # React pages
│   │   ├── components/       # UI components
│   │   ├── lib/             # Utilities
│   │   └── client/          # Generated API client
│   ├── package.json         # Frontend dependencies
│   └── vite.config.ts       # Vite configuration
│
├── scripts/                   # Development automation
│   ├── setup.sh             # Environment setup
│   ├── watch.sh             # Development server
│   ├── fix.sh               # Code formatting
│   └── deploy.sh            # Deployment
│
├── pyproject.toml            # Python dependencies
├── app.yaml                  # Databricks Apps config
└── CLAUDE.md                 # Development guide`}
                </pre>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Features */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Wrench className="h-5 w-5" />
              Key Features
            </CardTitle>
            <CardDescription>
              Built-in capabilities to accelerate your development
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <Badge className="mt-1">Auto</Badge>
                  <div>
                    <h5 className="font-semibold">
                      TypeScript Client Generation
                    </h5>
                    <p className="text-sm text-muted-foreground">
                      Automatically generates TypeScript API client from FastAPI
                      OpenAPI spec
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <Badge className="mt-1">Hot</Badge>
                  <div>
                    <h5 className="font-semibold">Hot Reloading</h5>
                    <p className="text-sm text-muted-foreground">
                      Instant updates for both Python backend and React frontend
                      changes
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <Badge className="mt-1">Auth</Badge>
                  <div>
                    <h5 className="font-semibold">Databricks Authentication</h5>
                    <p className="text-sm text-muted-foreground">
                      Integrated with Databricks SDK for seamless workspace
                      integration
                    </p>
                  </div>
                </div>
              </div>
              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <Badge className="mt-1">Deploy</Badge>
                  <div>
                    <h5 className="font-semibold">Databricks Apps Ready</h5>
                    <p className="text-sm text-muted-foreground">
                      Pre-configured for deployment to Databricks Apps platform
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <Badge className="mt-1">Quality</Badge>
                  <div>
                    <h5 className="font-semibold">Code Quality Tools</h5>
                    <p className="text-sm text-muted-foreground">
                      Automated formatting with ruff (Python) and prettier
                      (TypeScript)
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <Badge className="mt-1">Logs</Badge>
                  <div>
                    <h5 className="font-semibold">Background Development</h5>
                    <p className="text-sm text-muted-foreground">
                      Development servers run in background with comprehensive
                      logging
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Footer */}
        <div className="text-center mt-12 pt-8 border-t">
          <p className="text-muted-foreground">
            Ready to build something amazing? Check out the{" "}
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:underline"
            >
              API documentation
            </a>{" "}
            to get started with your endpoints.
          </p>
        </div>
      </div>
    </div>
  );
}
