// Drag-and-drop file upload component for HAR files

"use client";

import { useCallback, useState } from "react";
import { Card } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Upload, FileText, AlertCircle } from "lucide-react";

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  selectedFile: File | null;
}

export function FileUpload({ onFileSelect, selectedFile }: FileUploadProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 1️⃣ Handle file validation
  const validateFile = (file: File): boolean => {
    if (!file.name.endsWith(".har")) {
      setError("Please select a .har file");
      return false;
    }
    
    if (file.size > 50 * 1024 * 1024) { // 50MB limit
      setError("File size must be less than 50MB");
      return false;
    }
    
    setError(null);
    return true;
  };

  // 2️⃣ Handle file selection
  const handleFileSelect = useCallback((file: File) => {
    if (validateFile(file)) {
      onFileSelect(file);
    }
  }, [onFileSelect]);

  // 3️⃣ Handle drag events
  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  }, [handleFileSelect]);

  // 4️⃣ Handle file input
  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  return (
    <div className="space-y-4">
      <Card
        className={`border-2 border-dashed transition-colors ${
          isDragOver
            ? "border-primary bg-primary/5"
            : "border-muted-foreground/25 hover:border-primary/50"
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <div className="flex flex-col items-center justify-center p-8 text-center">
          <Upload className="h-12 w-12 text-muted-foreground mb-4" />
          
          <div className="space-y-2">
            <h3 className="text-lg font-semibold">
              Upload HAR File
            </h3>
            <p className="text-sm text-muted-foreground">
              Drag and drop your .har file here, or click to browse
            </p>
          </div>
          
          <input
            type="file"
            accept=".har"
            onChange={handleFileInput}
            className="hidden"
            id="file-upload"
          />
          
          <label
            htmlFor="file-upload"
            className="mt-4 cursor-pointer text-sm text-primary hover:underline"
          >
            Choose file
          </label>
        </div>
      </Card>

      {/* 5️⃣ Show selected file */}
      {selectedFile && (
        <div className="flex items-center space-x-2 p-3 bg-muted rounded-lg">
          <FileText className="h-5 w-5 text-primary" />
          <span className="text-sm font-medium">{selectedFile.name}</span>
          <span className="text-xs text-muted-foreground">
            ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)
          </span>
        </div>
      )}

      {/* 6️⃣ Show error */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}
    </div>
  );
}
