import type { AnalysisResult, ScreenshotAnalysisResponse } from "@/types/analysis";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

interface ValidationErrorItem {
  msg?: string;
}

interface ErrorResponse {
  detail?: string | ValidationErrorItem[];
}

export async function analyzeText(text: string): Promise<AnalysisResult> {
  const response = await fetch(`${API_BASE_URL}/api/v1/analyses/text`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ text }),
  });

  if (!response.ok) {
    let message = "ScamLens could not analyze the message.";

    try {
      const errorBody = (await response.json()) as ErrorResponse;

      if (typeof errorBody.detail === "string") {
        message = errorBody.detail;
      } else if (
        Array.isArray(errorBody.detail) &&
        typeof errorBody.detail[0]?.msg === "string"
      ) {
        message = errorBody.detail[0].msg;
      }
    } catch {
      // Keep the default message when the backend response is not JSON.
    }

    throw new Error(message);
  }

  return (await response.json()) as AnalysisResult;
}
export async function analyzeScreenshot(
  file: File,
): Promise<ScreenshotAnalysisResponse> {
  const apiUrl =
    process.env.NEXT_PUBLIC_API_URL ??
    "http://127.0.0.1:8000";

  const formData = new FormData(); //not maually add the data, the browser should automatically create the required multipart boundary

  formData.append("file", file);

  const response = await fetch(
    `${apiUrl}/api/v1/analyses/screenshot`,
    {
      method: "POST",
      body: formData,
    },
  );

  if (!response.ok) {
    let message = "Screenshot analysis failed.";

    try {
      const body = await response.json();

      if (typeof body.detail === "string") {
        message = body.detail;
      }
    } catch {
      // Keep the fallback message.
    }

    throw new Error(message);
  }

  return response.json();
}