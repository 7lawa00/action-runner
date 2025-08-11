import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { RequestManager } from "./RequestManager";
import { ScenarioBuilder } from "./ScenarioBuilder";
import { EnvironmentManager } from "./EnvironmentManager";
import { SnippetLibrary } from "./SnippetLibrary";
import { Badge } from "@/components/ui/badge";
import { 
  Zap, 
  Send, 
  Layers, 
  Settings, 
  Code, 
  Activity,
  Globe,
  FileText,
  Play
} from "lucide-react";

export const AutomationDashboard = () => {
  const [activeTab, setActiveTab] = useState("requests");

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-4 mb-8">
          <div className="flex items-center justify-center space-x-3">
            <div className="p-3 bg-gradient-primary rounded-xl shadow-glow">
              <Zap className="h-8 w-8 text-white" />
            </div>
            <h1 className="text-4xl font-bold bg-gradient-primary bg-clip-text text-transparent">
              AutoFlow Pro
            </h1>
          </div>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Advanced web automation tool for HTTP requests, scenarios, and API testing
          </p>
          
          {/* Quick Stats */}
          <div className="flex items-center justify-center space-x-6">
            <Badge variant="secondary" className="px-4 py-2">
              <Activity className="h-4 w-4 mr-2" />
              5 Active Requests
            </Badge>
            <Badge variant="secondary" className="px-4 py-2">
              <Layers className="h-4 w-4 mr-2" />
              3 Scenarios
            </Badge>
            <Badge variant="secondary" className="px-4 py-2">
              <Globe className="h-4 w-4 mr-2" />
              2 Environments
            </Badge>
          </div>
        </div>

        {/* Main Dashboard */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid grid-cols-5 w-full max-w-2xl mx-auto h-12">
            <TabsTrigger value="requests" className="flex items-center space-x-2">
              <Send className="h-4 w-4" />
              <span>Requests</span>
            </TabsTrigger>
            <TabsTrigger value="scenarios" className="flex items-center space-x-2">
              <Layers className="h-4 w-4" />
              <span>Scenarios</span>
            </TabsTrigger>
            <TabsTrigger value="environments" className="flex items-center space-x-2">
              <Settings className="h-4 w-4" />
              <span>Environments</span>
            </TabsTrigger>
            <TabsTrigger value="snippets" className="flex items-center space-x-2">
              <Code className="h-4 w-4" />
              <span>Snippets</span>
            </TabsTrigger>
            <TabsTrigger value="docs" className="flex items-center space-x-2">
              <FileText className="h-4 w-4" />
              <span>Docs</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="requests" className="animate-fade-in">
            <RequestManager />
          </TabsContent>

          <TabsContent value="scenarios" className="animate-fade-in">
            <ScenarioBuilder />
          </TabsContent>

          <TabsContent value="environments" className="animate-fade-in">
            <EnvironmentManager />
          </TabsContent>

          <TabsContent value="snippets" className="animate-fade-in">
            <SnippetLibrary />
          </TabsContent>

          <TabsContent value="docs" className="animate-fade-in">
            <Card className="bg-gradient-card border-border shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <FileText className="h-5 w-5" />
                  <span>Documentation</span>
                </CardTitle>
                <CardDescription>
                  Quick reference and examples for using AutoFlow Pro
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Card className="border-border/50">
                    <CardHeader className="pb-3">
                      <CardTitle className="text-lg">Quick Start</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2">
                      <p className="text-sm text-muted-foreground">
                        1. Create an environment with your API credentials
                      </p>
                      <p className="text-sm text-muted-foreground">
                        2. Build HTTP requests using the Request Manager
                      </p>
                      <p className="text-sm text-muted-foreground">
                        3. Chain requests together in Scenarios
                      </p>
                      <p className="text-sm text-muted-foreground">
                        4. Save reusable code in Snippets
                      </p>
                    </CardContent>
                  </Card>
                  <Card className="border-border/50">
                    <CardHeader className="pb-3">
                      <CardTitle className="text-lg">Environment Variables</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2">
                      <p className="text-sm text-muted-foreground">
                        Use {`{{variable_name}}`} syntax in requests
                      </p>
                      <p className="text-sm text-muted-foreground">
                        Example: {`{{base_url}}/api/users`}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        Variables are replaced at runtime
                      </p>
                    </CardContent>
                  </Card>
                </div>
                <Button className="w-full" variant="outline">
                  <Play className="h-4 w-4 mr-2" />
                  Try Demo Scenario
                </Button>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};