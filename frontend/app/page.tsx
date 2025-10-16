// Main page with file upload and results display

"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { FileUpload } from "@/components/file-upload";
import { CurlDisplay } from "@/components/curl-display";
import { LoadingState } from "@/components/loading-state";
import { ApiInfoDisplay } from "@/components/api-info-display";
import { RequestTester } from "@/components/request-tester";
import { CodeGenerator } from "@/components/code-generator";
import { DocExporter } from "@/components/doc-exporter";
import { analyzeHarFile, AnalyzeResponse } from "@/lib/api";
import { AlertCircle, CheckCircle } from "lucide-react";

export default function HomePage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [description, setDescription] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeResultTab, setActiveResultTab] = useState("curl");

  // 1️⃣ Handle file selection
  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
    setError(null);
    setResult(null);
  };

  // 2️⃣ Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedFile || !description.trim()) {
      setError("Please select a file and enter a description");
      return;
    }

    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await analyzeHarFile(selectedFile, description);
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setIsLoading(false);
    }
  };

  // 3️⃣ Check if form is valid
  const isFormValid = selectedFile && description.trim().length > 0;

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <div className="space-y-8">
          {/* 4️⃣ Header */}
          <div className="text-center space-y-4">
            <h1 className="text-4xl font-bold tracking-tight">
              API Reverse Engineering
            </h1>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Upload a HAR file, describe the API you want to reverse-engineer, 
              and get a cURL command to replicate the request.
            </p>
          </div>

          {/* 5️⃣ Main form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-4">
              <h2 className="text-2xl font-semibold">Upload HAR File</h2>
              <FileUpload
                onFileSelect={handleFileSelect}
                selectedFile={selectedFile}
              />
            </div>

            <div className="space-y-4">
              <h2 className="text-2xl font-semibold">Describe the API</h2>
              <Textarea
                placeholder="e.g., 'Return the API that fetches the weather of San Francisco'"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="min-h-[100px]"
              />
            </div>

            <Button
              type="submit"
              disabled={!isFormValid || isLoading}
              className="w-full"
              size="lg"
            >
              {isLoading ? "Analyzing..." : "Analyze HAR File"}
            </Button>
          </form>

          {/* 6️⃣ Error display */}
          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* 7️⃣ Loading state */}
          {isLoading && <LoadingState />}

          {/* 8️⃣ Results display */}
          {result && (
            <div className="space-y-4">
              <Alert>
                <CheckCircle className="h-4 w-4" />
                <AlertDescription>
                  Successfully identified the best matching API request!
                </AlertDescription>
              </Alert>
              
              {/* 9️⃣ Result tabs */}
              <div className="border rounded-lg">
                <div className="flex border-b">
                  {[
                    { id: "curl", label: "cURL" },
                    { id: "info", label: "API Info" },
                    { id: "test", label: "Test" },
                    { id: "code", label: "Code" },
                    { id: "docs", label: "Export" },
                  ].map((tab) => (
                    <button
                      key={tab.id}
                      onClick={() => setActiveResultTab(tab.id)}
                      className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                        activeResultTab === tab.id
                          ? "border-primary text-primary"
                          : "border-transparent text-muted-foreground hover:text-foreground"
                      }`}
                    >
                      {tab.label}
                    </button>
                  ))}
                </div>

                <div className="p-6">
                  {activeResultTab === "curl" && (
                    <CurlDisplay
                      curlCommand={result.curl_command}
                      requestDetails={result.request_details}
                    />
                  )}
                  
                  {activeResultTab === "info" && (
                    <ApiInfoDisplay
                      requestInfo={result.request_info}
                      authInfo={result.auth_info}
                      parameters={result.parameters}
                    />
                  )}
                  
                  {activeResultTab === "test" && (
                    <RequestTester
                      requestInfo={result.request_info}
                    />
                  )}
                  
                  {activeResultTab === "code" && (
                    <CodeGenerator
                      requestInfo={result.request_info}
                    />
                  )}
                  
                  {activeResultTab === "docs" && (
                    <DocExporter
                      requestInfo={result.request_info}
                      authInfo={result.auth_info}
                    />
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}