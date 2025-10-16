// Code generation component with language selector

"use client";

import { useState, useEffect, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Copy, Check, Download } from "lucide-react";
import { generateCode, GenerateCodeResponse } from "@/lib/api";

interface CodeGeneratorProps {
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

const languages = [
  { value: "python", label: "Python", extension: "py" },
  { value: "javascript", label: "JavaScript", extension: "js" },
  { value: "go", label: "Go", extension: "go" },
];

export function CodeGenerator({ requestInfo }: CodeGeneratorProps) {
  const [selectedLanguage, setSelectedLanguage] = useState("python");
  const [generatedCode, setGeneratedCode] = useState<string>("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  // 2️⃣ Generate code for selected language
  const generateCodeForLanguage = useCallback(async (language: string) => {
    setIsLoading(true);
    setError(null);

    // Debug: Log what we're sending
    console.log("DEBUG: requestInfo being sent to code generator:", requestInfo);
    console.log("DEBUG: URL in requestInfo:", requestInfo.url);

    try {
      const result: GenerateCodeResponse = await generateCode(requestInfo, language);
      setGeneratedCode(result.code);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to generate code");
      setGeneratedCode("");
    } finally {
      setIsLoading(false);
    }
  }, [requestInfo]);

  // 1️⃣ Generate code when language changes
  useEffect(() => {
    generateCodeForLanguage(selectedLanguage);
  }, [selectedLanguage, generateCodeForLanguage]);

  // 3️⃣ Handle copy to clipboard
  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(generatedCode);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error("Failed to copy:", error);
    }
  };

  // 4️⃣ Handle download
  const handleDownload = () => {
    const currentLang = languages.find(lang => lang.value === selectedLanguage);
    const filename = `api_request.${currentLang?.extension || 'txt'}`;
    
    const blob = new Blob([generatedCode], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  // 5️⃣ Get syntax highlighting class
  const getSyntaxClass = (language: string) => {
    switch (language) {
      case "python":
        return "language-python";
      case "javascript":
        return "language-javascript";
      case "go":
        return "language-go";
      default:
        return "language-text";
    }
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Code Generation</CardTitle>
          <div className="flex items-center gap-2">
            <Select value={selectedLanguage} onValueChange={setSelectedLanguage}>
              <SelectTrigger className="w-40">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {languages.map((lang) => (
                  <SelectItem key={lang.value} value={lang.value}>
                    {lang.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* 6️⃣ Language info */}
        <div className="flex items-center gap-2">
          <Badge variant="outline">
            {languages.find(lang => lang.value === selectedLanguage)?.label}
          </Badge>
          <span className="text-sm text-muted-foreground">
            Generated code for {requestInfo.method} {requestInfo.path}
          </span>
        </div>

        {/* 7️⃣ Error display */}
        {error && (
          <div className="p-3 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
            {error}
          </div>
        )}

        {/* 8️⃣ Loading state */}
        {isLoading && (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
            <span className="ml-2 text-sm text-muted-foreground">
              Generating {languages.find(lang => lang.value === selectedLanguage)?.label} code...
            </span>
          </div>
        )}

        {/* 9️⃣ Generated code */}
        {generatedCode && !isLoading && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="font-medium">Generated Code</span>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleCopy}
                  className="flex items-center gap-2"
                >
                  {copied ? (
                    <>
                      <Check className="h-4 w-4" />
                      Copied!
                    </>
                  ) : (
                    <>
                      <Copy className="h-4 w-4" />
                      Copy
                    </>
                  )}
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleDownload}
                  className="flex items-center gap-2"
                >
                  <Download className="h-4 w-4" />
                  Download
                </Button>
              </div>
            </div>

            <div className="relative">
              <pre className="bg-muted p-4 rounded-lg overflow-x-auto text-sm">
                <code className={getSyntaxClass(selectedLanguage)}>
                  {generatedCode}
                </code>
              </pre>
            </div>
          </div>
        )}

        {/* 🔟 No code state */}
        {!generatedCode && !isLoading && !error && (
          <div className="text-center py-8 text-muted-foreground">
            Select a language to generate code
          </div>
        )}
      </CardContent>
    </Card>
  );
}
