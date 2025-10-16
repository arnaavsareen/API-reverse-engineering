// Documentation export component

"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Download, FileText, Code, Copy, Check } from "lucide-react";
import { exportDocs, ExportDocsResponse } from "@/lib/api";

interface DocExporterProps {
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
}

const exportFormats = [
  { 
    value: "markdown", 
    label: "Markdown", 
    icon: FileText, 
    description: "Human-readable documentation",
    extension: "md"
  },
  { 
    value: "openapi", 
    label: "OpenAPI", 
    icon: Code, 
    description: "Machine-readable API spec",
    extension: "json"
  },
];

export function DocExporter({ requestInfo, authInfo }: DocExporterProps) {
  const [isExporting, setIsExporting] = useState<string | null>(null);
  const [exportedDocs, setExportedDocs] = useState<Record<string, ExportDocsResponse>>({});
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState<string | null>(null);

  // 1️⃣ Handle export
  const handleExport = async (format: string) => {
    setIsExporting(format);
    setError(null);

    try {
      const result: ExportDocsResponse = await exportDocs(requestInfo, authInfo, format);
      setExportedDocs(prev => ({ ...prev, [format]: result }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to export documentation");
    } finally {
      setIsExporting(null);
    }
  };

  // 2️⃣ Handle download
  const handleDownload = (format: string) => {
    const doc = exportedDocs[format];
    if (!doc) return;

    const blob = new Blob([doc.content], { 
      type: format === "markdown" ? "text/markdown" : "application/json" 
    });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = doc.filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  // 3️⃣ Handle copy
  const handleCopy = async (content: string, format: string) => {
    try {
      await navigator.clipboard.writeText(content);
      setCopied(format);
      setTimeout(() => setCopied(null), 2000);
    } catch (error) {
      console.error("Failed to copy:", error);
    }
  };

  // 4️⃣ Format content for preview
  const formatContentForPreview = (content: string, format: string) => {
    if (format === "openapi") {
      try {
        const parsed = JSON.parse(content);
        return JSON.stringify(parsed, null, 2);
      } catch {
        return content;
      }
    }
    return content;
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Export Documentation</CardTitle>
        <p className="text-sm text-muted-foreground">
          Generate API documentation in various formats
        </p>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* 5️⃣ Export format selection */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {exportFormats.map((format) => {
            const Icon = format.icon;
            const isExportingFormat = isExporting === format.value;
            const hasExported = exportedDocs[format.value];
            
            return (
              <div key={format.value} className="border rounded-lg p-4 space-y-3">
                <div className="flex items-center gap-3">
                  <Icon className="h-5 w-5 text-muted-foreground" />
                  <div>
                    <h3 className="font-medium">{format.label}</h3>
                    <p className="text-sm text-muted-foreground">
                      {format.description}
                    </p>
                  </div>
                </div>

                <div className="flex gap-2">
                  <Button
                    onClick={() => handleExport(format.value)}
                    disabled={isExportingFormat}
                    className="flex-1"
                  >
                    {isExportingFormat ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Exporting...
                      </>
                    ) : (
                      <>
                        <Download className="h-4 w-4 mr-2" />
                        Export {format.label}
                      </>
                    )}
                  </Button>
                </div>

                {/* 6️⃣ Exported content preview */}
                {hasExported && (
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Badge variant="outline">
                          {format.extension}
                        </Badge>
                        <span className="text-sm text-muted-foreground">
                          {hasExported.filename}
                        </span>
                      </div>
                      <div className="flex gap-1">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleCopy(hasExported.content, format.value)}
                        >
                          {copied === format.value ? (
                            <Check className="h-4 w-4" />
                          ) : (
                            <Copy className="h-4 w-4" />
                          )}
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDownload(format.value)}
                        >
                          <Download className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>

                    <div className="relative">
                      <pre className="bg-muted p-3 rounded text-xs overflow-x-auto max-h-32">
                        <code>
                          {formatContentForPreview(hasExported.content, format.value)}
                        </code>
                      </pre>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* 7️⃣ Error display */}
        {error && (
          <div className="p-3 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
            {error}
          </div>
        )}

        {/* 8️⃣ Usage instructions */}
        <div className="bg-gray-50 border border-gray-200 rounded p-4">
          <h4 className="font-medium text-gray-900 mb-2">How to use</h4>
          <ul className="text-sm text-gray-700 space-y-1">
            <li>• <strong>Markdown:</strong> Perfect for README files and documentation sites</li>
            <li>• <strong>OpenAPI:</strong> Import into tools like Postman, Insomnia, or API documentation generators</li>
            <li>• Click the copy button to copy content to clipboard</li>
            <li>• Click the download button to save as a file</li>
          </ul>
        </div>
      </CardContent>
    </Card>
  );
}
