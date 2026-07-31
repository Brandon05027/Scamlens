export type RiskLevel = "low" | "moderate" | "high" | "critical";

export type FindingSeverity = "low" | "medium" | "high";

export interface Finding {
  rule_id: string;
  title: string;
  category: string;
  severity: FindingSeverity;
  evidence: string;
  explanation: string;
  score_contribution: number;
}

export interface ScoreBreakdownItem {
  signal: string;
  points: number;
}

export interface AnalysisResult {
  risk_score: number;
  risk_level: RiskLevel;
  primary_category: string;
  summary: string;
  findings: Finding[];
  score_breakdown: ScoreBreakdownItem[];
  recommended_actions: string[];
}