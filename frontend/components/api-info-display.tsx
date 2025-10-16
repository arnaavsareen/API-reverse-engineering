// Enhanced API information display with tabbed interface

"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Eye, EyeOff, Copy, Check } from "lucide-react";

interface ApiInfoDisplayProps {
  requestInfo: {
    method: string;
    url: string;
    path: string;
    host: string;
    scheme: string;
    headers: Record<string, string>;
    query_params: Record<string, string>;
    path_params: string[];
    body: {
      type: string;
      content: unknown;
      raw: string;
    };
  };
  authInfo: {
    type: string;
    location: string;
    redacted_value: string;
    original_value: string;
  };
  parameters: {
    query_params: Record<string, string>;
    path_params: string[];
    headers: Record<string, string>;
  };
}

export function ApiInfoDisplay({ requestInfo, authInfo, parameters }: ApiInfoDisplayProps) {
  const [activeTab, setActiveTab] = useState("overview");
  const [showAuthValue, setShowAuthValue] = useState(false);
  const [copied, setCopied] = useState<string | null>(null);

  // 1️⃣ Handle copy to clipboard
  const handleCopy = async (text: string, type: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(type);
      setTimeout(() => setCopied(null), 2000);
    } catch (error) {
      console.error("Failed to copy:", error);
    }
  };

  // 2️⃣ Format auth type for display
  const formatAuthType = (type: string) => {
    return type.replace("_", " ").replace(/\b\w/g, l => l.toUpperCase());
  };

  // 3️⃣ Render overview tab
  const renderOverview = () => (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <span className="font-medium">Method:</span>
          <Badge variant="outline" className="ml-2">
            {requestInfo.method}
          </Badge>
        </div>
        <div>
          <span className="font-medium">Host:</span>
          <span className="ml-2 text-sm text-muted-foreground">
            {requestInfo.host}
          </span>
        </div>
      </div>
      
      <div>
        <span className="font-medium">URL:</span>
        <div className="mt-1 p-2 bg-muted rounded text-sm font-mono break-all">
          {requestInfo.url}
        </div>
      </div>

      {authInfo.type !== "none" && (
        <div>
          <span className="font-medium">Authentication:</span>
          <div className="mt-1 flex items-center gap-2">
            <Badge variant="secondary">
              {formatAuthType(authInfo.type)}
            </Badge>
            <span className="text-sm text-muted-foreground">
              ({authInfo.location})
            </span>
          </div>
        </div>
      )}
    </div>
  );

  // 4️⃣ Render headers tab
  const renderHeaders = () => (
    <div className="space-y-2">
      {Object.entries(parameters.headers).map(([key, value]) => (
        <div key={key} className="flex items-center justify-between p-2 border rounded">
          <div className="flex-1 min-w-0">
            <span className="font-medium text-sm">{key}</span>
            <div className="text-sm text-muted-foreground font-mono break-all">
              {value}
            </div>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => handleCopy(value, `header-${key}`)}
          >
            {copied === `header-${key}` ? (
              <Check className="h-4 w-4" />
            ) : (
              <Copy className="h-4 w-4" />
            )}
          </Button>
        </div>
      ))}
    </div>
  );

  // 5️⃣ Render parameters tab
  const renderParameters = () => (
    <div className="space-y-4">
      {parameters.query_params && Object.keys(parameters.query_params).length > 0 && (
        <div>
          <h4 className="font-medium mb-2">Query Parameters</h4>
          <div className="space-y-2">
            {Object.entries(parameters.query_params).map(([key, value]) => (
              <div key={key} className="flex items-center justify-between p-2 border rounded">
                <div className="flex-1 min-w-0">
                  <span className="font-medium text-sm">{key}</span>
                  <div className="text-sm text-muted-foreground font-mono break-all">
                    {value}
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleCopy(value, `query-${key}`)}
                >
                  {copied === `query-${key}` ? (
                    <Check className="h-4 w-4" />
                  ) : (
                    <Copy className="h-4 w-4" />
                  )}
                </Button>
              </div>
            ))}
          </div>
        </div>
      )}

      {parameters.path_params && parameters.path_params.length > 0 && (
        <div>
          <h4 className="font-medium mb-2">Path Parameters</h4>
          <div className="flex flex-wrap gap-2">
            {parameters.path_params.map((param) => (
              <Badge key={param} variant="outline">
                {param}
              </Badge>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  // 6️⃣ Render authentication tab
  const renderAuthentication = () => (
    <div className="space-y-4">
      {authInfo.type === "none" ? (
        <div className="text-center py-8 text-muted-foreground">
          No authentication detected
        </div>
      ) : (
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <span className="font-medium">Type:</span>
              <Badge variant="secondary" className="ml-2">
                {formatAuthType(authInfo.type)}
              </Badge>
            </div>
            <div>
              <span className="font-medium">Location:</span>
              <span className="ml-2 text-sm text-muted-foreground">
                {authInfo.location}
              </span>
            </div>
          </div>

          <div>
            <span className="font-medium">Value:</span>
            <div className="mt-1 flex items-center gap-2">
              <div className="flex-1 p-2 bg-muted rounded font-mono text-sm">
                {showAuthValue ? authInfo.original_value : authInfo.redacted_value}
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowAuthValue(!showAuthValue)}
              >
                {showAuthValue ? (
                  <EyeOff className="h-4 w-4" />
                ) : (
                  <Eye className="h-4 w-4" />
                )}
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleCopy(
                  showAuthValue ? authInfo.original_value : authInfo.redacted_value,
                  "auth"
                )}
              >
                {copied === "auth" ? (
                  <Check className="h-4 w-4" />
                ) : (
                  <Copy className="h-4 w-4" />
                )}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  // 7️⃣ Render body tab
  const renderBody = () => (
    <div className="space-y-4">
      {requestInfo.body.type === "none" ? (
        <div className="text-center py-8 text-muted-foreground">
          No request body
        </div>
      ) : (
        <div>
          <div className="mb-2">
            <span className="font-medium">Content Type:</span>
            <Badge variant="outline" className="ml-2">
              {requestInfo.body.type}
            </Badge>
          </div>
          
          <div className="relative">
            <pre className="bg-muted p-4 rounded-lg overflow-x-auto text-sm">
              <code>
                {requestInfo.body.type === "json" 
                  ? JSON.stringify(requestInfo.body.content, null, 2)
                  : requestInfo.body.raw
                }
              </code>
            </pre>
            <Button
              variant="outline"
              size="sm"
              className="absolute top-2 right-2"
              onClick={() => handleCopy(
                requestInfo.body.type === "json" 
                  ? JSON.stringify(requestInfo.body.content, null, 2)
                  : requestInfo.body.raw,
                "body"
              )}
            >
              {copied === "body" ? (
                <Check className="h-4 w-4" />
              ) : (
                <Copy className="h-4 w-4" />
              )}
            </Button>
          </div>
        </div>
      )}
    </div>
  );

  const tabs = [
    { id: "overview", label: "Overview" },
    { id: "headers", label: "Headers" },
    { id: "parameters", label: "Parameters" },
    { id: "authentication", label: "Authentication" },
    { id: "body", label: "Body" },
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle>API Information</CardTitle>
        <div className="flex space-x-1">
          {tabs.map((tab) => (
            <Button
              key={tab.id}
              variant={activeTab === tab.id ? "default" : "ghost"}
              size="sm"
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.label}
            </Button>
          ))}
        </div>
      </CardHeader>
      
      <CardContent>
        {activeTab === "overview" && renderOverview()}
        {activeTab === "headers" && renderHeaders()}
        {activeTab === "parameters" && renderParameters()}
        {activeTab === "authentication" && renderAuthentication()}
        {activeTab === "body" && renderBody()}
      </CardContent>
    </Card>
  );
}
