import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { toast } from "@/hooks/use-toast";
import { Send, Plus, Copy, Trash2, Clock, CheckCircle, XCircle } from "lucide-react";

interface HttpRequest {
  id: string;
  name: string;
  method: string;
  url: string;
  headers: Record<string, string>;
  body: string;
  environment: string;
}

export const RequestManager = () => {
  const [requests, setRequests] = useState<HttpRequest[]>([
    {
      id: '1',
      name: 'Get Users',
      method: 'GET',
      url: '{{base_url}}/users',
      headers: { 'Content-Type': 'application/json' },
      body: '',
      environment: 'Development'
    },
    {
      id: '2',
      name: 'Create User',
      method: 'POST',
      url: '{{base_url}}/users',
      headers: { 'Content-Type': 'application/json' },
      body: '{\n  "name": "{{user_name}}",\n  "email": "{{user_email}}"\n}',
      environment: 'Development'
    }
  ]);

  const [selectedRequest, setSelectedRequest] = useState<HttpRequest | null>(requests[0]);
  const [response, setResponse] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleSendRequest = async () => {
    if (!selectedRequest) return;
    
    setLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const mockResponse = {
        status: 200,
        statusText: 'OK',
        headers: { 'content-type': 'application/json' },
        data: selectedRequest.method === 'GET' 
          ? [{ id: 1, name: 'John Doe', email: 'john@example.com' }]
          : { id: 123, name: 'New User', email: 'new@example.com', created: true }
      };
      
      setResponse(mockResponse);
      toast({
        title: "Request Sent",
        description: `${selectedRequest.method} request completed successfully`,
      });
    } catch (error) {
      toast({
        title: "Request Failed",
        description: "There was an error sending the request",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const addNewRequest = () => {
    const newRequest: HttpRequest = {
      id: Date.now().toString(),
      name: 'New Request',
      method: 'GET',
      url: '',
      headers: { 'Content-Type': 'application/json' },
      body: '',
      environment: 'Development'
    };
    setRequests([...requests, newRequest]);
    setSelectedRequest(newRequest);
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[calc(100vh-200px)]">
      {/* Request List */}
      <Card className="bg-gradient-card border-border shadow-lg">
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle className="flex items-center space-x-2">
              <Send className="h-5 w-5" />
              <span>Requests</span>
            </CardTitle>
            <CardDescription>Manage your HTTP requests</CardDescription>
          </div>
          <Button onClick={addNewRequest} size="sm" className="bg-gradient-primary hover:opacity-90">
            <Plus className="h-4 w-4" />
          </Button>
        </CardHeader>
        <CardContent className="space-y-2">
          {requests.map((request) => (
            <div
              key={request.id}
              onClick={() => setSelectedRequest(request)}
              className={`p-3 rounded-lg border cursor-pointer transition-all hover:border-primary/50 ${
                selectedRequest?.id === request.id 
                  ? 'border-primary bg-primary/5' 
                  : 'border-border/50 hover:bg-muted/30'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium text-sm">{request.name}</span>
                <Badge variant={
                  request.method === 'GET' ? 'default' :
                  request.method === 'POST' ? 'secondary' :
                  request.method === 'PUT' ? 'outline' : 'destructive'
                }>
                  {request.method}
                </Badge>
              </div>
              <p className="text-xs text-muted-foreground truncate">{request.url}</p>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Request Editor */}
      <Card className="bg-gradient-card border-border shadow-lg lg:col-span-2">
        <CardHeader>
          <CardTitle>Request Editor</CardTitle>
          <CardDescription>
            {selectedRequest ? `Editing: ${selectedRequest.name}` : 'Select a request to edit'}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {selectedRequest && (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Request Name</Label>
                  <Input
                    id="name"
                    value={selectedRequest.name}
                    onChange={(e) => setSelectedRequest({...selectedRequest, name: e.target.value})}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="method">Method</Label>
                  <Select value={selectedRequest.method} onValueChange={(value) => setSelectedRequest({...selectedRequest, method: value})}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="GET">GET</SelectItem>
                      <SelectItem value="POST">POST</SelectItem>
                      <SelectItem value="PUT">PUT</SelectItem>
                      <SelectItem value="DELETE">DELETE</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="url">URL</Label>
                <Input
                  id="url"
                  value={selectedRequest.url}
                  onChange={(e) => setSelectedRequest({...selectedRequest, url: e.target.value})}
                  placeholder="https://api.example.com/endpoint"
                />
              </div>

              <Tabs defaultValue="body" className="w-full">
                <TabsList className="grid w-full grid-cols-3">
                  <TabsTrigger value="body">Body</TabsTrigger>
                  <TabsTrigger value="headers">Headers</TabsTrigger>
                  <TabsTrigger value="scripts">Scripts</TabsTrigger>
                </TabsList>
                <TabsContent value="body" className="space-y-2">
                  <Label htmlFor="body">Request Body</Label>
                  <Textarea
                    id="body"
                    value={selectedRequest.body}
                    onChange={(e) => setSelectedRequest({...selectedRequest, body: e.target.value})}
                    placeholder="JSON payload"
                    className="h-32 font-mono text-sm"
                  />
                </TabsContent>
                <TabsContent value="headers" className="space-y-2">
                  <Label>Headers</Label>
                  <div className="space-y-2">
                    {Object.entries(selectedRequest.headers).map(([key, value]) => (
                      <div key={key} className="grid grid-cols-2 gap-2">
                        <Input value={key} placeholder="Header name" />
                        <Input value={value} placeholder="Header value" />
                      </div>
                    ))}
                  </div>
                </TabsContent>
                <TabsContent value="scripts" className="space-y-2">
                  <Label>Pre-request Script</Label>
                  <Textarea
                    placeholder="// JavaScript code to run before request"
                    className="h-24 font-mono text-sm"
                  />
                </TabsContent>
              </Tabs>

              <div className="flex space-x-2">
                <Button 
                  onClick={handleSendRequest}
                  disabled={loading}
                  className="bg-gradient-primary hover:opacity-90"
                >
                  {loading ? (
                    <Clock className="h-4 w-4 mr-2 animate-spin" />
                  ) : (
                    <Send className="h-4 w-4 mr-2" />
                  )}
                  Send Request
                </Button>
                <Button variant="outline" size="sm">
                  <Copy className="h-4 w-4 mr-2" />
                  Duplicate
                </Button>
                <Button variant="outline" size="sm">
                  <Trash2 className="h-4 w-4 mr-2" />
                  Delete
                </Button>
              </div>

              {/* Response */}
              {response && (
                <Card className="mt-4 border-border/50">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-lg flex items-center space-x-2">
                      {response.status < 300 ? (
                        <CheckCircle className="h-5 w-5 text-success" />
                      ) : (
                        <XCircle className="h-5 w-5 text-destructive" />
                      )}
                      <span>Response</span>
                      <Badge variant={response.status < 300 ? "default" : "destructive"}>
                        {response.status} {response.statusText}
                      </Badge>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <Tabs defaultValue="response" className="w-full">
                      <TabsList>
                        <TabsTrigger value="response">Response</TabsTrigger>
                        <TabsTrigger value="headers">Headers</TabsTrigger>
                      </TabsList>
                      <TabsContent value="response">
                        <pre className="bg-muted/50 p-4 rounded-lg text-sm overflow-auto">
                          {JSON.stringify(response.data, null, 2)}
                        </pre>
                      </TabsContent>
                      <TabsContent value="headers">
                        <pre className="bg-muted/50 p-4 rounded-lg text-sm overflow-auto">
                          {JSON.stringify(response.headers, null, 2)}
                        </pre>
                      </TabsContent>
                    </Tabs>
                  </CardContent>
                </Card>
              )}
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
};