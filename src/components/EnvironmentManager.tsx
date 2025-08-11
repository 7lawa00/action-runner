import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { toast } from "@/hooks/use-toast";
import { 
  Settings, 
  Plus, 
  Trash2, 
  Copy, 
  Globe,
  Lock,
  Unlock,
  Eye,
  EyeOff
} from "lucide-react";

interface EnvironmentVariable {
  key: string;
  value: string;
  isSecret: boolean;
}

interface Environment {
  id: string;
  name: string;
  description: string;
  variables: EnvironmentVariable[];
  isActive: boolean;
}

export const EnvironmentManager = () => {
  const [environments, setEnvironments] = useState<Environment[]>([
    {
      id: '1',
      name: 'Development',
      description: 'Local development environment',
      isActive: true,
      variables: [
        { key: 'base_url', value: 'https://jsonplaceholder.typicode.com', isSecret: false },
        { key: 'api_key', value: 'dev_key_12345', isSecret: true },
        { key: 'user_name', value: 'John Doe', isSecret: false },
        { key: 'user_email', value: 'john.doe@example.com', isSecret: false }
      ]
    },
    {
      id: '2',
      name: 'Production',
      description: 'Live production environment',
      isActive: false,
      variables: [
        { key: 'base_url', value: 'https://api.production.com', isSecret: false },
        { key: 'api_key', value: 'prod_key_67890', isSecret: true },
        { key: 'user_name', value: 'Admin User', isSecret: false }
      ]
    },
    {
      id: '3',
      name: 'Trello Integration',
      description: 'Trello API configuration',
      isActive: false,
      variables: [
        { key: 'trello_api_key', value: 'your_trello_api_key', isSecret: true },
        { key: 'trello_token', value: 'your_trello_token', isSecret: true },
        { key: 'board_id', value: 'your_board_id', isSecret: false }
      ]
    }
  ]);

  const [selectedEnvironment, setSelectedEnvironment] = useState<Environment | null>(environments[0]);
  const [showSecrets, setShowSecrets] = useState<Record<string, boolean>>({});

  const addNewEnvironment = () => {
    const newEnvironment: Environment = {
      id: Date.now().toString(),
      name: 'New Environment',
      description: 'Environment description',
      isActive: false,
      variables: []
    };
    setEnvironments([...environments, newEnvironment]);
    setSelectedEnvironment(newEnvironment);
  };

  const addVariable = () => {
    if (!selectedEnvironment) return;
    
    const updatedEnvironment = {
      ...selectedEnvironment,
      variables: [
        ...selectedEnvironment.variables,
        { key: 'new_variable', value: '', isSecret: false }
      ]
    };
    setSelectedEnvironment(updatedEnvironment);
    updateEnvironment(updatedEnvironment);
  };

  const updateEnvironment = (updatedEnv: Environment) => {
    setEnvironments(prev => prev.map(env => env.id === updatedEnv.id ? updatedEnv : env));
  };

  const deleteVariable = (index: number) => {
    if (!selectedEnvironment) return;
    
    const updatedEnvironment = {
      ...selectedEnvironment,
      variables: selectedEnvironment.variables.filter((_, i) => i !== index)
    };
    setSelectedEnvironment(updatedEnvironment);
    updateEnvironment(updatedEnvironment);
  };

  const setActiveEnvironment = (envId: string) => {
    const updatedEnvironments = environments.map(env => ({
      ...env,
      isActive: env.id === envId
    }));
    setEnvironments(updatedEnvironments);
    
    const activeEnv = updatedEnvironments.find(env => env.id === envId);
    if (activeEnv) {
      toast({
        title: "Environment Activated",
        description: `${activeEnv.name} is now the active environment`,
      });
    }
  };

  const toggleSecretVisibility = (key: string) => {
    setShowSecrets(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Environment List */}
      <Card className="bg-gradient-card border-border shadow-lg">
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle className="flex items-center space-x-2">
              <Settings className="h-5 w-5" />
              <span>Environments</span>
            </CardTitle>
            <CardDescription>Manage configuration environments</CardDescription>
          </div>
          <Button onClick={addNewEnvironment} size="sm" className="bg-gradient-primary hover:opacity-90">
            <Plus className="h-4 w-4" />
          </Button>
        </CardHeader>
        <CardContent className="space-y-3">
          {environments.map((environment) => (
            <div
              key={environment.id}
              onClick={() => setSelectedEnvironment(environment)}
              className={`p-4 rounded-lg border cursor-pointer transition-all hover:border-primary/50 ${
                selectedEnvironment?.id === environment.id 
                  ? 'border-primary bg-primary/5' 
                  : 'border-border/50 hover:bg-muted/30'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium text-sm">{environment.name}</span>
                <div className="flex items-center space-x-2">
                  {environment.isActive && (
                    <Badge variant="default" className="bg-gradient-primary">
                      <Globe className="h-3 w-3 mr-1" />
                      Active
                    </Badge>
                  )}
                </div>
              </div>
              <p className="text-xs text-muted-foreground mb-2">{environment.description}</p>
              <div className="flex items-center text-xs text-muted-foreground">
                <span>{environment.variables.length} variables</span>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Environment Editor */}
      <Card className="bg-gradient-card border-border shadow-lg lg:col-span-2">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center space-x-2">
                <span>{selectedEnvironment?.name || 'Select an Environment'}</span>
                {selectedEnvironment?.isActive && (
                  <Badge variant="default" className="bg-gradient-primary">
                    Active
                  </Badge>
                )}
              </CardTitle>
              <CardDescription>
                {selectedEnvironment?.description || 'Choose an environment to edit'}
              </CardDescription>
            </div>
            {selectedEnvironment && !selectedEnvironment.isActive && (
              <Button 
                onClick={() => setActiveEnvironment(selectedEnvironment.id)}
                variant="outline"
              >
                <Globe className="h-4 w-4 mr-2" />
                Set Active
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {selectedEnvironment && (
            <div className="space-y-6">
              {/* Environment Details */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="envName">Environment Name</Label>
                  <Input
                    id="envName"
                    value={selectedEnvironment.name}
                    onChange={(e) => {
                      const updated = {...selectedEnvironment, name: e.target.value};
                      setSelectedEnvironment(updated);
                      updateEnvironment(updated);
                    }}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="envDesc">Description</Label>
                  <Input
                    id="envDesc"
                    value={selectedEnvironment.description}
                    onChange={(e) => {
                      const updated = {...selectedEnvironment, description: e.target.value};
                      setSelectedEnvironment(updated);
                      updateEnvironment(updated);
                    }}
                  />
                </div>
              </div>

              {/* Variables */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold">Variables</h3>
                  <Button onClick={addVariable} variant="outline" size="sm">
                    <Plus className="h-4 w-4 mr-2" />
                    Add Variable
                  </Button>
                </div>

                <div className="space-y-3">
                  {selectedEnvironment.variables.map((variable, index) => (
                    <div
                      key={index}
                      className="grid grid-cols-12 gap-2 items-center p-3 border border-border/50 rounded-lg hover:bg-muted/30 transition-colors"
                    >
                      <div className="col-span-4">
                        <Input
                          value={variable.key}
                          onChange={(e) => {
                            const updated = {...selectedEnvironment};
                            updated.variables[index].key = e.target.value;
                            setSelectedEnvironment(updated);
                            updateEnvironment(updated);
                          }}
                          placeholder="Variable name"
                          className="font-mono text-sm"
                        />
                      </div>
                      <div className="col-span-5 relative">
                        <Input
                          type={variable.isSecret && !showSecrets[variable.key] ? "password" : "text"}
                          value={variable.value}
                          onChange={(e) => {
                            const updated = {...selectedEnvironment};
                            updated.variables[index].value = e.target.value;
                            setSelectedEnvironment(updated);
                            updateEnvironment(updated);
                          }}
                          placeholder="Variable value"
                          className="font-mono text-sm pr-10"
                        />
                        {variable.isSecret && (
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            className="absolute right-1 top-1 h-6 w-6 p-0"
                            onClick={() => toggleSecretVisibility(variable.key)}
                          >
                            {showSecrets[variable.key] ? (
                              <EyeOff className="h-3 w-3" />
                            ) : (
                              <Eye className="h-3 w-3" />
                            )}
                          </Button>
                        )}
                      </div>
                      <div className="col-span-2 flex items-center justify-center space-x-1">
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-8 w-8 p-0"
                          onClick={() => {
                            const updated = {...selectedEnvironment};
                            updated.variables[index].isSecret = !updated.variables[index].isSecret;
                            setSelectedEnvironment(updated);
                            updateEnvironment(updated);
                          }}
                        >
                          {variable.isSecret ? (
                            <Lock className="h-3 w-3 text-warning" />
                          ) : (
                            <Unlock className="h-3 w-3 text-muted-foreground" />
                          )}
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-8 w-8 p-0"
                          onClick={() => deleteVariable(index)}
                        >
                          <Trash2 className="h-3 w-3 text-destructive" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>

                {selectedEnvironment.variables.length === 0 && (
                  <div className="text-center py-8 text-muted-foreground">
                    <Settings className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>No variables defined</p>
                    <p className="text-sm">Add variables to store configuration values</p>
                  </div>
                )}
              </div>

              {/* Usage Example */}
              <Card className="border-border/50">
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg">Usage Example</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="bg-muted/50 p-4 rounded-lg font-mono text-sm">
                    <div className="text-muted-foreground mb-2">// In your requests, use:</div>
                    {selectedEnvironment.variables.slice(0, 3).map((variable) => (
                      <div key={variable.key} className="mb-1">
                        <span className="text-accent">{`{{${variable.key}}}`}</span>
                        <span className="text-muted-foreground"> → </span>
                        <span>{variable.isSecret ? '***' : variable.value}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};