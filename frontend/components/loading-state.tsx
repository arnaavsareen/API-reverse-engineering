// Loading indicator component

import { Loader2 } from "lucide-react";

export function LoadingState() {
  return (
    <div className="flex flex-col items-center justify-center p-8 space-y-4">
      <Loader2 className="h-8 w-8 animate-spin text-primary" />
      <div className="text-center">
        <h3 className="text-lg font-semibold">Analyzing HAR File</h3>
        <p className="text-sm text-muted-foreground">
          Using AI to identify the best matching API request...
        </p>
      </div>
    </div>
  );
}
