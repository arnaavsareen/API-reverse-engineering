// Display curl command with syntax highlighting and copy functionality

"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Copy, Check } from "lucide-react";

interface CurlDisplayProps {
  curlCommand: string;
  requestDetails: {
    method: string;
    url: string;
    index: number;
    total_api_requests: number;
  };
}

export function CurlDisplay({ curlCommand, requestDetails }: CurlDisplayProps) {
  const [copied, setCopied] = useState(false);

  // 1️⃣ Handle copy to clipboard
  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(curlCommand);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error("Failed to copy:", error);
    }
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Generated cURL Command</CardTitle>
          <Button
            variant="outline"
            size="sm"
            onClick={handleCopy}
            className="flex items-center space-x-2"
          >
            {copied ? (
              <>
                <Check className="h-4 w-4" />
                <span>Copied!</span>
              </>
            ) : (
              <>
                <Copy className="h-4 w-4" />
                <span>Copy</span>
              </>
            )}
          </Button>
        </div>
        
        <div className="text-sm text-muted-foreground">
          Found {requestDetails.total_api_requests} API requests, selected request #{requestDetails.index + 1}
        </div>
      </CardHeader>
      
      <CardContent>
        <div className="space-y-4">
          {/* 2️⃣ Request details */}
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="font-medium">Method:</span> {requestDetails.method}
            </div>
            <div>
              <span className="font-medium">URL:</span> {requestDetails.url}
            </div>
          </div>
          
          {/* 3️⃣ Curl command */}
          <div className="relative">
            <pre className="bg-muted p-4 rounded-lg overflow-x-auto text-sm">
              <code>{curlCommand}</code>
            </pre>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
