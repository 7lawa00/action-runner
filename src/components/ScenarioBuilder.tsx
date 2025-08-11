import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { toast } from "@/hooks/use-toast";
import { 
  Layers, 
  Plus, 
  Play, 
  Pause, 
  RotateCcw, 
  ChevronRight,
  Clock,
  CheckCircle,
  AlertCircle
} from "lucide-react";

interface ScenarioStep {
  id: string;
  name: string;
  type: 'request' | 'action';
  status: 'pending' | 'running' | 'completed' | 'failed';
  duration?: number;
}

interface Scenario {
  id: string;
  name: string;
  description: string;
  steps: ScenarioStep[];
  status: 'idle' | 'running' | 'completed' | 'failed';
}

export const ScenarioBuilder = () => {
  const [scenarios, setScenarios] = useState<Scenario[]>([
    {
      id: '1',
      name: 'User Management Flow',
      description: 'Complete user lifecycle testing',
      status: 'idle',
      steps: [
        { id: '1', name: 'Get All Users', type: 'request', status: 'pending' },
        { id: '2', name: 'Create New User', type: 'request', status: 'pending' },
        { id: '3', name: 'Update User Profile', type: 'request', status: 'pending' },
        { id: '4', name: 'Delete User', type: 'request', status: 'pending' }
      ]
    },
    {
      id: '2',
      name: 'Trello Integration Demo',
      description: 'Sync data with Trello boards',
      status: 'idle',
      steps: [
        { id: '1', name: 'Get Boards', type: 'request', status: 'pending' },
        { id: '2', name: 'Create Card', type: 'request', status: 'pending' },
        { id: '3', name: 'Update Card Status', type: 'action', status: 'pending' }
      ]
    }
  ]);

  const [selectedScenario, setSelectedScenario] = useState<Scenario | null>(scenarios[0]);
  const [isRunning, setIsRunning] = useState(false);

  const runScenario = async (scenario: Scenario) => {
    if (isRunning) return;
    
    setIsRunning(true);
    
    // Create a working copy
    const workingScenario: Scenario = { ...scenario, status: 'running' };
    setSelectedScenario(workingScenario);
    setScenarios(prev => prev.map(s => s.id === scenario.id ? workingScenario : s));

    for (let i = 0; i < scenario.steps.length; i++) {
      // Update step to running
      workingScenario.steps[i] = { ...workingScenario.steps[i], status: 'running' };
      setSelectedScenario({ ...workingScenario });
      
      // Simulate step execution
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Complete step
      const success = Math.random() > 0.1; // 90% success rate
      workingScenario.steps[i] = { 
        ...workingScenario.steps[i], 
        status: success ? 'completed' : 'failed',
        duration: Math.floor(Math.random() * 2000) + 500
      };
      setSelectedScenario({ ...workingScenario });
      
      if (!success) {
        workingScenario.status = 'failed';
        break;
      }
    }
    
    if (workingScenario.status === 'running') {
      workingScenario.status = 'completed';
    }
    
    setSelectedScenario({ ...workingScenario });
    setScenarios(prev => prev.map(s => s.id === scenario.id ? workingScenario : s));
    setIsRunning(false);
    
    toast({
      title: "Scenario Completed",
      description: `${scenario.name} finished ${workingScenario.status === 'completed' ? 'successfully' : 'with errors'}`,
      variant: workingScenario.status === 'completed' ? 'default' : 'destructive'
    });
  };

  const addNewScenario = () => {
    const newScenario: Scenario = {
      id: Date.now().toString(),
      name: 'New Scenario',
      description: 'Description of your scenario',
      status: 'idle',
      steps: []
    };
    setScenarios([...scenarios, newScenario]);
    setSelectedScenario(newScenario);
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Scenario List */}
      <Card className="bg-gradient-card border-border shadow-lg">
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle className="flex items-center space-x-2">
              <Layers className="h-5 w-5" />
              <span>Scenarios</span>
            </CardTitle>
            <CardDescription>Automated test scenarios</CardDescription>
          </div>
          <Button onClick={addNewScenario} size="sm" className="bg-gradient-primary hover:opacity-90">
            <Plus className="h-4 w-4" />
          </Button>
        </CardHeader>
        <CardContent className="space-y-3">
          {scenarios.map((scenario) => (
            <div
              key={scenario.id}
              onClick={() => setSelectedScenario(scenario)}
              className={`p-4 rounded-lg border cursor-pointer transition-all hover:border-primary/50 ${
                selectedScenario?.id === scenario.id 
                  ? 'border-primary bg-primary/5' 
                  : 'border-border/50 hover:bg-muted/30'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium text-sm">{scenario.name}</span>
                <Badge variant={
                  scenario.status === 'completed' ? 'default' :
                  scenario.status === 'running' ? 'secondary' :
                  scenario.status === 'failed' ? 'destructive' : 'outline'
                }>
                  {scenario.status}
                </Badge>
              </div>
              <p className="text-xs text-muted-foreground mb-2">{scenario.description}</p>
              <div className="flex items-center text-xs text-muted-foreground">
                <span>{scenario.steps.length} steps</span>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Scenario Details */}
      <Card className="bg-gradient-card border-border shadow-lg lg:col-span-2">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center space-x-2">
                <span>{selectedScenario?.name || 'Select a Scenario'}</span>
                {selectedScenario && (
                  <Badge variant={
                    selectedScenario.status === 'completed' ? 'default' :
                    selectedScenario.status === 'running' ? 'secondary' :
                    selectedScenario.status === 'failed' ? 'destructive' : 'outline'
                  }>
                    {selectedScenario.status}
                  </Badge>
                )}
              </CardTitle>
              <CardDescription>
                {selectedScenario?.description || 'Choose a scenario to view details'}
              </CardDescription>
            </div>
            {selectedScenario && (
              <div className="flex space-x-2">
                <Button 
                  onClick={() => runScenario(selectedScenario)}
                  disabled={isRunning}
                  className="bg-gradient-primary hover:opacity-90"
                >
                  {isRunning ? (
                    <Pause className="h-4 w-4 mr-2" />
                  ) : (
                    <Play className="h-4 w-4 mr-2" />
                  )}
                  {isRunning ? 'Running' : 'Run Scenario'}
                </Button>
                <Button variant="outline" size="sm">
                  <RotateCcw className="h-4 w-4 mr-2" />
                  Reset
                </Button>
              </div>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {selectedScenario && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                <div className="space-y-2">
                  <Label htmlFor="scenarioName">Scenario Name</Label>
                  <Input
                    id="scenarioName"
                    value={selectedScenario.name}
                    onChange={(e) => setSelectedScenario({...selectedScenario, name: e.target.value})}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="scenarioDesc">Description</Label>
                  <Input
                    id="scenarioDesc"
                    value={selectedScenario.description}
                    onChange={(e) => setSelectedScenario({...selectedScenario, description: e.target.value})}
                  />
                </div>
              </div>

              {/* Steps */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold">Steps</h3>
                  <Button variant="outline" size="sm">
                    <Plus className="h-4 w-4 mr-2" />
                    Add Step
                  </Button>
                </div>
                
                <div className="space-y-2">
                  {selectedScenario.steps.map((step, index) => (
                    <div
                      key={step.id}
                      className="flex items-center space-x-4 p-3 border border-border/50 rounded-lg hover:bg-muted/30 transition-colors"
                    >
                      <div className="flex items-center justify-center w-8 h-8 rounded-full border-2 border-border">
                        <span className="text-sm font-medium">{index + 1}</span>
                      </div>
                      
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <span className="font-medium">{step.name}</span>
                          <Badge variant={step.type === 'request' ? 'default' : 'secondary'}>
                            {step.type}
                          </Badge>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        {step.duration && (
                          <span className="text-xs text-muted-foreground">
                            {step.duration}ms
                          </span>
                        )}
                        {step.status === 'running' && (
                          <Clock className="h-4 w-4 text-info animate-spin" />
                        )}
                        {step.status === 'completed' && (
                          <CheckCircle className="h-4 w-4 text-success" />
                        )}
                        {step.status === 'failed' && (
                          <AlertCircle className="h-4 w-4 text-destructive" />
                        )}
                      </div>
                      
                      {index < selectedScenario.steps.length - 1 && (
                        <ChevronRight className="h-4 w-4 text-muted-foreground" />
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Progress Bar */}
              {selectedScenario.status === 'running' && (
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Progress</span>
                    <span>
                      {selectedScenario.steps.filter(s => s.status === 'completed').length} / {selectedScenario.steps.length}
                    </span>
                  </div>
                  <div className="w-full bg-muted rounded-full h-2">
                    <div
                      className="bg-gradient-primary h-2 rounded-full transition-all duration-500"
                      style={{
                        width: `${(selectedScenario.steps.filter(s => s.status === 'completed').length / selectedScenario.steps.length) * 100}%`
                      }}
                    />
                  </div>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};