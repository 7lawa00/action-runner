import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { toast } from "@/hooks/use-toast";
import { 
  Code, 
  Plus, 
  Copy, 
  Trash2, 
  Search,
  BookOpen,
  Zap,
  Globe
} from "lucide-react";

interface CodeSnippet {
  id: string;
  name: string;
  description: string;
  category: 'pre-request' | 'post-request' | 'action' | 'validation' | 'utility';
  language: 'javascript' | 'python' | 'json';
  code: string;
  tags: string[];
}

export const SnippetLibrary = () => {
  const [snippets, setSnippets] = useState<CodeSnippet[]>([
    {
      id: '1',
      name: 'Set Environment Variable',
      description: 'Extract value from response and set as environment variable',
      category: 'post-request',
      language: 'javascript',
      code: `// Extract and set environment variable
const responseData = pm.response.json();
pm.environment.set("user_id", responseData.id);
pm.environment.set("auth_token", responseData.token);`,
      tags: ['environment', 'response', 'extraction']
    },
    {
      id: '2',
      name: 'Generate Random Data',
      description: 'Generate random test data for requests',
      category: 'pre-request',
      language: 'javascript',
      code: `// Generate random test data
const randomEmail = \`user_\${Math.random().toString(36).substr(2, 9)}@example.com\`;
const randomName = \`User \${Math.floor(Math.random() * 1000)}\`;

pm.environment.set("random_email", randomEmail);
pm.environment.set("random_name", randomName);`,
      tags: ['random', 'data', 'generation']
    },
    {
      id: '3',
      name: 'Validate Response Status',
      description: 'Common response validation checks',
      category: 'validation',
      language: 'javascript',
      code: `// Validate response
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response time is less than 2000ms", function () {
    pm.expect(pm.response.responseTime).to.be.below(2000);
});

pm.test("Response has required fields", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('id');
    pm.expect(jsonData).to.have.property('name');
});`,
      tags: ['validation', 'testing', 'response']
    },
    {
      id: '4',
      name: 'Selenium Login Action',
      description: 'Automated browser login using Selenium',
      category: 'action',
      language: 'python',
      code: `from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def siebel_login(username, password, url):
    driver = webdriver.Chrome()
    try:
        # Navigate to login page
        driver.get(url)
        
        # Wait for login form
        wait = WebDriverWait(driver, 10)
        
        # Fill credentials
        username_field = wait.until(EC.presence_of_element_located((By.ID, "username")))
        password_field = driver.find_element(By.ID, "password")
        
        username_field.send_keys(username)
        password_field.send_keys(password)
        
        # Submit login
        login_button = driver.find_element(By.ID, "login-button")
        login_button.click()
        
        # Wait for dashboard
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dashboard")))
        
        return {"status": "success", "message": "Login successful"}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        driver.quit()`,
      tags: ['selenium', 'automation', 'login', 'browser']
    },
    {
      id: '5',
      name: 'JSON Schema Validation',
      description: 'Validate JSON response against schema',
      category: 'validation',
      language: 'javascript',
      code: `// JSON Schema validation
const schema = {
    "type": "object",
    "properties": {
        "id": {"type": "number"},
        "name": {"type": "string"},
        "email": {"type": "string", "format": "email"},
        "created_at": {"type": "string", "format": "date-time"}
    },
    "required": ["id", "name", "email"]
};

pm.test("Response matches schema", function () {
    const responseJson = pm.response.json();
    pm.expect(tv4.validate(responseJson, schema)).to.be.true;
});`,
      tags: ['json', 'schema', 'validation']
    }
  ]);

  const [selectedSnippet, setSelectedSnippet] = useState<CodeSnippet | null>(snippets[0]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterCategory, setFilterCategory] = useState<string>('all');

  const filteredSnippets = snippets.filter(snippet => {
    const matchesSearch = snippet.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         snippet.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         snippet.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesCategory = filterCategory === 'all' || snippet.category === filterCategory;
    return matchesSearch && matchesCategory;
  });

  const addNewSnippet = () => {
    const newSnippet: CodeSnippet = {
      id: Date.now().toString(),
      name: 'New Snippet',
      description: 'Description of your code snippet',
      category: 'utility',
      language: 'javascript',
      code: '// Your code here',
      tags: []
    };
    setSnippets([...snippets, newSnippet]);
    setSelectedSnippet(newSnippet);
  };

  const copySnippet = (snippet: CodeSnippet) => {
    navigator.clipboard.writeText(snippet.code);
    toast({
      title: "Snippet Copied",
      description: `${snippet.name} copied to clipboard`,
    });
  };

  const deleteSnippet = (snippetId: string) => {
    setSnippets(prev => prev.filter(s => s.id !== snippetId));
    if (selectedSnippet?.id === snippetId) {
      setSelectedSnippet(snippets[0] || null);
    }
    toast({
      title: "Snippet Deleted",
      description: "Code snippet has been removed",
    });
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'action': return <Zap className="h-3 w-3" />;
      case 'validation': return <BookOpen className="h-3 w-3" />;
      case 'pre-request': 
      case 'post-request': return <Globe className="h-3 w-3" />;
      default: return <Code className="h-3 w-3" />;
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'pre-request': return 'default';
      case 'post-request': return 'secondary';
      case 'action': return 'outline';
      case 'validation': return 'destructive';
      default: return 'outline';
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[calc(100vh-200px)]">
      {/* Snippet List */}
      <Card className="bg-gradient-card border-border shadow-lg">
        <CardHeader className="flex flex-row items-center justify-between pb-4">
          <div>
            <CardTitle className="flex items-center space-x-2">
              <Code className="h-5 w-5" />
              <span>Snippets</span>
            </CardTitle>
            <CardDescription>Reusable code library</CardDescription>
          </div>
          <Button onClick={addNewSnippet} size="sm" className="bg-gradient-primary hover:opacity-90">
            <Plus className="h-4 w-4" />
          </Button>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Search and Filter */}
          <div className="space-y-2">
            <div className="relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search snippets..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <Select value={filterCategory} onValueChange={setFilterCategory}>
              <SelectTrigger>
                <SelectValue placeholder="Filter by category" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Categories</SelectItem>
                <SelectItem value="pre-request">Pre-request</SelectItem>
                <SelectItem value="post-request">Post-request</SelectItem>
                <SelectItem value="action">Action</SelectItem>
                <SelectItem value="validation">Validation</SelectItem>
                <SelectItem value="utility">Utility</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Snippet List */}
          <div className="space-y-2 max-h-[60vh] overflow-y-auto">
            {filteredSnippets.map((snippet) => (
              <div
                key={snippet.id}
                onClick={() => setSelectedSnippet(snippet)}
                className={`p-3 rounded-lg border cursor-pointer transition-all hover:border-primary/50 ${
                  selectedSnippet?.id === snippet.id 
                    ? 'border-primary bg-primary/5' 
                    : 'border-border/50 hover:bg-muted/30'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-sm">{snippet.name}</span>
                  <Badge variant={getCategoryColor(snippet.category)} className="text-xs">
                    {getCategoryIcon(snippet.category)}
                    <span className="ml-1">{snippet.category}</span>
                  </Badge>
                </div>
                <p className="text-xs text-muted-foreground mb-2 line-clamp-2">{snippet.description}</p>
                <div className="flex items-center space-x-2">
                  <Badge variant="outline" className="text-xs">
                    {snippet.language}
                  </Badge>
                  <div className="flex items-center space-x-1">
                    {snippet.tags.slice(0, 2).map(tag => (
                      <Badge key={tag} variant="outline" className="text-xs px-1 py-0">
                        {tag}
                      </Badge>
                    ))}
                    {snippet.tags.length > 2 && (
                      <span className="text-xs text-muted-foreground">+{snippet.tags.length - 2}</span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Snippet Editor */}
      <Card className="bg-gradient-card border-border shadow-lg lg:col-span-2">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center space-x-2">
                <span>{selectedSnippet?.name || 'Select a Snippet'}</span>
                {selectedSnippet && (
                  <Badge variant={getCategoryColor(selectedSnippet.category)}>
                    {getCategoryIcon(selectedSnippet.category)}
                    <span className="ml-1">{selectedSnippet.category}</span>
                  </Badge>
                )}
              </CardTitle>
              <CardDescription>
                {selectedSnippet?.description || 'Choose a snippet to view and edit'}
              </CardDescription>
            </div>
            {selectedSnippet && (
              <div className="flex space-x-2">
                <Button 
                  onClick={() => copySnippet(selectedSnippet)}
                  variant="outline" 
                  size="sm"
                >
                  <Copy className="h-4 w-4 mr-2" />
                  Copy
                </Button>
                <Button 
                  onClick={() => deleteSnippet(selectedSnippet.id)}
                  variant="outline" 
                  size="sm"
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  Delete
                </Button>
              </div>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {selectedSnippet && (
            <div className="space-y-6">
              {/* Snippet Details */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="snippetName">Snippet Name</Label>
                  <Input
                    id="snippetName"
                    value={selectedSnippet.name}
                    onChange={(e) => setSelectedSnippet({...selectedSnippet, name: e.target.value})}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="snippetCategory">Category</Label>
                  <Select 
                    value={selectedSnippet.category} 
                    onValueChange={(value: any) => setSelectedSnippet({...selectedSnippet, category: value})}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="pre-request">Pre-request</SelectItem>
                      <SelectItem value="post-request">Post-request</SelectItem>
                      <SelectItem value="action">Action</SelectItem>
                      <SelectItem value="validation">Validation</SelectItem>
                      <SelectItem value="utility">Utility</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="snippetDesc">Description</Label>
                <Input
                  id="snippetDesc"
                  value={selectedSnippet.description}
                  onChange={(e) => setSelectedSnippet({...selectedSnippet, description: e.target.value})}
                  placeholder="What does this snippet do?"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="snippetLanguage">Language</Label>
                  <Select 
                    value={selectedSnippet.language} 
                    onValueChange={(value: any) => setSelectedSnippet({...selectedSnippet, language: value})}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="javascript">JavaScript</SelectItem>
                      <SelectItem value="python">Python</SelectItem>
                      <SelectItem value="json">JSON</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="snippetTags">Tags (comma-separated)</Label>
                  <Input
                    id="snippetTags"
                    value={selectedSnippet.tags.join(', ')}
                    onChange={(e) => setSelectedSnippet({
                      ...selectedSnippet, 
                      tags: e.target.value.split(',').map(tag => tag.trim()).filter(Boolean)
                    })}
                    placeholder="tag1, tag2, tag3"
                  />
                </div>
              </div>

              {/* Code Editor */}
              <div className="space-y-2">
                <Label htmlFor="snippetCode">Code</Label>
                <Textarea
                  id="snippetCode"
                  value={selectedSnippet.code}
                  onChange={(e) => setSelectedSnippet({...selectedSnippet, code: e.target.value})}
                  placeholder="Enter your code here..."
                  className="h-64 font-mono text-sm"
                />
              </div>

              {/* Tags Display */}
              {selectedSnippet.tags.length > 0 && (
                <div className="space-y-2">
                  <Label>Tags</Label>
                  <div className="flex flex-wrap gap-2">
                    {selectedSnippet.tags.map(tag => (
                      <Badge key={tag} variant="outline" className="text-xs">
                        {tag}
                      </Badge>
                    ))}
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