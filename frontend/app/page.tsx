"use client";

import type { FormEvent } from "react";
import { useState } from "react";

import { analyzeText } from "@/lib/api";
import type { AnalysisResult, RiskLevel } from "@/types/analysis";

const SAMPLE_SCAM_MESSAGE = `This is urgent. We will send you a check.
Deposit the check and reply immediately with your banking information.`;

const SAMPLE_NORMAL_MESSAGE = `Our computer science study group will meet
in the library tomorrow afternoon.`;

function getRiskStyles(riskLevel: RiskLevel): string {
  switch (riskLevel) {
    case "critical":
      return "border-red-500 bg-red-950/40 text-red-200";
    case "high":
      return "border-orange-500 bg-orange-950/40 text-orange-200";
    case "moderate":
      return "border-yellow-500 bg-yellow-950/40 text-yellow-100";
    case "low":
      return "border-emerald-500 bg-emerald-950/40 text-emerald-200";
  }
}

function formatCategory(category: string): string {
  return category
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

export default function HomePage() {
  const [text, setText] = useState("");
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ): Promise<void> {
    event.preventDefault();

    const cleanedText = text.trim();

    if (cleanedText.length < 10) {
      setError("Enter at least 10 characters before analyzing.");
      setResult(null);
      return;
    }

    setIsAnalyzing(true);
    setError("");
    setResult(null);

    try {
      const analysisResult = await analyzeText(cleanedText);
      setResult(analysisResult);
    } catch (requestError) {
      if (requestError instanceof Error) {
        setError(requestError.message);
      } else {
        setError("An unexpected error occurred.");
      }
    } finally {
      setIsAnalyzing(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-950 px-5 py-10 text-slate-100">
      <div className="mx-auto max-w-5xl">
        <header className="mb-10">
          <p className="mb-3 text-sm font-semibold uppercase tracking-[0.25em] text-cyan-400">
            Explainable scam analysis
          </p>

          <h1 className="text-4xl font-bold tracking-tight sm:text-6xl">
            ScamLens
          </h1>

          <p className="mt-5 max-w-2xl text-lg leading-8 text-slate-300">
            Paste a suspicious message to identify warning signs, understand
            the risk score, and receive safer next steps.
          </p>
        </header>

        <section className="rounded-2xl border border-slate-800 bg-slate-900 p-5 shadow-xl sm:p-7">
          <form onSubmit={handleSubmit}>
            <div className="flex flex-col justify-between gap-2 sm:flex-row">
              <label
                htmlFor="suspicious-text"
                className="font-semibold text-slate-100"
              >
                Suspicious message
              </label>

              <span className="text-sm text-slate-400">
                {text.length.toLocaleString()}/20,000
              </span>
            </div>

            <textarea
              id="suspicious-text"
              value={text}
              onChange={(event) => setText(event.target.value)}
              placeholder="Paste a suspicious email, job offer, marketplace message, or text message..."
              maxLength={20_000}
              disabled={isAnalyzing}
              className="mt-3 min-h-64 w-full resize-y rounded-xl border border-slate-700 bg-slate-950 p-4 leading-7 text-slate-100 outline-none transition focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20 disabled:cursor-not-allowed disabled:opacity-60"
            />

            <div className="mt-4 flex flex-wrap gap-3">
              <button
                type="button"
                onClick={() => {
                  setText(SAMPLE_SCAM_MESSAGE);
                  setResult(null);
                  setError("");
                }}
                disabled={isAnalyzing}
                className="rounded-lg border border-slate-700 px-4 py-2 text-sm font-semibold text-slate-200 transition hover:border-cyan-400 hover:text-cyan-300 disabled:opacity-50"
              >
                Load scam example
              </button>

              <button
                type="button"
                onClick={() => {
                  setText(SAMPLE_NORMAL_MESSAGE);
                  setResult(null);
                  setError("");
                }}
                disabled={isAnalyzing}
                className="rounded-lg border border-slate-700 px-4 py-2 text-sm font-semibold text-slate-200 transition hover:border-cyan-400 hover:text-cyan-300 disabled:opacity-50"
              >
                Load normal example
              </button>

              <button
                type="button"
                onClick={() => {
                  setText("");
                  setResult(null);
                  setError("");
                }}
                disabled={isAnalyzing}
                className="rounded-lg border border-slate-700 px-4 py-2 text-sm font-semibold text-slate-200 transition hover:border-cyan-400 hover:text-cyan-300 disabled:opacity-50"
              >
                Clear
              </button>
            </div>

            {error && (
              <div
                role="alert"
                className="mt-5 rounded-xl border border-red-800 bg-red-950/50 p-4 text-red-200"
              >
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={isAnalyzing || text.trim().length < 10}
              className="mt-6 w-full rounded-xl bg-cyan-400 px-6 py-3 font-bold text-slate-950 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-400 sm:w-auto"
            >
              {isAnalyzing ? "Analyzing..." : "Analyze message"}
            </button>
          </form>
        </section>

        {result && (
          <section className="mt-8 space-y-6" aria-live="polite">
            <article
              className={`rounded-2xl border p-6 ${getRiskStyles(
                result.risk_level,
              )}`}
            >
              <p className="text-sm font-semibold uppercase tracking-wider">
                Estimated scam risk
              </p>

              <div className="mt-3 flex flex-wrap items-end gap-4">
                <p className="text-6xl font-bold">{result.risk_score}</p>

                <div className="pb-1">
                  <p className="text-2xl font-bold capitalize">
                    {result.risk_level}
                  </p>
                  <p className="text-sm opacity-80">out of 100</p>
                </div>
              </div>

              <p className="mt-5 leading-7">{result.summary}</p>

              <p className="mt-3 text-sm opacity-80">
                Primary category:{" "}
                <strong>{formatCategory(result.primary_category)}</strong>
              </p>
            </article>

            <article className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <h2 className="text-2xl font-bold">Warning signs</h2>

              {result.findings.length === 0 ? (
                <div className="mt-5 rounded-xl border border-slate-700 bg-slate-950 p-5 text-slate-300">
                  No currently supported warning patterns were found. A low
                  score does not guarantee that the message is safe.
                </div>
              ) : (
                <div className="mt-5 space-y-4">
                  {result.findings.map((finding) => (
                    <div
                      key={finding.rule_id}
                      className="rounded-xl border border-slate-700 bg-slate-950 p-5"
                    >
                      <div className="flex flex-col justify-between gap-2 sm:flex-row">
                        <div>
                          <h3 className="text-lg font-bold">
                            {finding.title}
                          </h3>

                          <p className="mt-1 text-sm capitalize text-slate-400">
                            {finding.severity} severity ·{" "}
                            {formatCategory(finding.category)}
                          </p>
                        </div>

                        <span className="h-fit rounded-full bg-slate-800 px-3 py-1 text-sm font-bold text-cyan-300">
                          +{finding.score_contribution} points
                        </span>
                      </div>

                      <blockquote className="mt-4 border-l-4 border-cyan-400 bg-slate-900 px-4 py-3 text-slate-200">
                        “{finding.evidence}”
                      </blockquote>

                      <p className="mt-4 leading-7 text-slate-300">
                        {finding.explanation}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </article>

            <article className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <h2 className="text-2xl font-bold">Score breakdown</h2>

              {result.score_breakdown.length === 0 ? (
                <p className="mt-4 text-slate-400">
                  No score contributions were recorded.
                </p>
              ) : (
                <div className="mt-5 divide-y divide-slate-800">
                  {result.score_breakdown.map((item) => (
                    <div
                      key={item.signal}
                      className="flex justify-between gap-4 py-3"
                    >
                      <span className="text-slate-300">{item.signal}</span>
                      <strong className="text-cyan-300">
                        +{item.points}
                      </strong>
                    </div>
                  ))}
                </div>
              )}
            </article>

            <article className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <h2 className="text-2xl font-bold">Recommended actions</h2>

              <ul className="mt-5 space-y-3">
                {result.recommended_actions.map((action) => (
                  <li
                    key={action}
                    className="flex gap-3 rounded-xl bg-slate-950 p-4 text-slate-300"
                  >
                    <span
                      aria-hidden="true"
                      className="font-bold text-cyan-400"
                    >
                      ✓
                    </span>
                    <span>{action}</span>
                  </li>
                ))}
              </ul>
            </article>
          </section>
        )}

        <footer className="mt-10 border-t border-slate-800 pt-6 text-sm leading-6 text-slate-500">
          ScamLens provides an estimated risk assessment, not a guarantee.
          Independently verify important requests before sending money,
          credentials, or personal information.
        </footer>
      </div>
    </main>
  );
}