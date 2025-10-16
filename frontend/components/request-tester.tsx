// Request testing component with response display

"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Play, Clock, CheckCircle, XCircle, Copy, Check } from "lucide-react";
import { testRequest, TestRequestResponse } from "@/lib/api";

interface RequestTesterProps {
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
}

export function RequestTester({ requestInfo }: RequestTesterProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [testResult, setTestResult] = useState<TestRequestResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState<string | null>(null);

  // 1️⃣ Handle test request
  const handleTestRequest = async () => {
    setIsLoading(true);
    setError(null);
    setTestResult(null);

    try {
      const result = await testRequest(requestInfo);
      setTestResult(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to test request");
    } finally {
      setIsLoading(false);
    }
  };

  // 2️⃣ Handle copy to clipboard
  const handleCopy = async (text: string, type: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(type);
      setTimeout(() => setCopied(null), 2000);
    } catch (error) {
      console.error("Failed to copy:", error);
    }
  };

  // 3️⃣ Format response body
  const formatResponseBody = (body: unknown, bodyType: string) => {
    if (bodyType === "json") {
      try {
        return JSON.stringify(body, null, 2);
      } catch {
        return String(body);
      }
    }
    return String(body);
  };

  // 4️⃣ Get status color
  const getStatusColor = (statusCode: number) => {
    if (statusCode >= 200 && statusCode < 300) return "bg-green-100 text-green-800";
    if (statusCode >= 300 && statusCode < 400) return "bg-blue-100 text-blue-800";
    if (statusCode >= 400 && statusCode < 500) return "bg-yellow-100 text-yellow-800";
    if (statusCode >= 500) return "bg-red-100 text-red-800";
    return "bg-gray-100 text-gray-800";
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Test Request</CardTitle>
          <Button
            onClick={handleTestRequest}
            disabled={isLoading}
            className="flex items-center gap-2"
          >
            {isLoading ? (
              <>
                <Clock className="h-4 w-4 animate-spin" />
                Testing...
              </>
            ) : (
              <>
                <Play className="h-4 w-4" />
                Test Request
              </>
            )}
          </Button>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* 5️⃣ Request summary */}
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="font-medium">Method:</span>
            <Badge variant="outline" className="ml-2">
              {requestInfo.method}
            </Badge>
          </div>
          <div>
            <span className="font-medium">URL:</span>
            <span className="ml-2 text-muted-foreground font-mono text-xs">
              {requestInfo.url}
            </span>
          </div>
        </div>

        {/* 6️⃣ Error display */}
        {error && (
          <Alert variant="destructive">
            <XCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* 7️⃣ Test results */}
        {testResult && (
          <div className="space-y-4">
            <Alert>
              <CheckCircle className="h-4 w-4" />
              <AlertDescription>
                Request executed successfully in {testResult.execution_time}s
              </AlertDescription>
            </Alert>

            {/* 8️⃣ Response status */}
            <div className="grid grid-cols-3 gap-4">
              <div>
                <span className="font-medium">Status:</span>
                <Badge 
                  className={`ml-2 ${getStatusColor(testResult.status_code)}`}
                >
                  {testResult.status_code} {testResult.status_text}
                </Badge>
              </div>
              <div>
                <span className="font-medium">Size:</span>
                <span className="ml-2 text-sm text-muted-foreground">
                  {testResult.size_bytes} bytes
                </span>
              </div>
              <div>
                <span className="font-medium">Time:</span>
                <span className="ml-2 text-sm text-muted-foreground">
                  {testResult.execution_time}s
                </span>
              </div>
            </div>

            {/* 9️⃣ Response headers */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium">Response Headers</span>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleCopy(
                    JSON.stringify(testResult.headers, null, 2),
                    "headers"
                  )}
                >
                  {copied === "headers" ? (
                    <Check className="h-4 w-4" />
                  ) : (
                    <Copy className="h-4 w-4" />
                  )}
                </Button>
              </div>
              <div className="max-h-32 overflow-y-auto">
                {Object.entries(testResult.headers).map(([key, value]) => (
                  <div key={key} className="flex justify-between text-sm py-1 border-b">
                    <span className="font-medium">{key}:</span>
                    <span className="text-muted-foreground font-mono text-xs">
                      {value}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* 🔟 Response body */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium">Response Body</span>
                <div className="flex gap-2">
                  <Badge variant="outline">
                    {testResult.body_type}
                  </Badge>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleCopy(
                      formatResponseBody(testResult.body, testResult.body_type),
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
              <div className="relative">
                <pre className="bg-muted p-4 rounded-lg overflow-x-auto text-sm max-h-64">
                  <code>
                    {formatResponseBody(testResult.body, testResult.body_type)}
                  </code>
                </pre>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
