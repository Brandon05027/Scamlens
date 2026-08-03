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

export interface RedactionCount {
  pii_type: string;
  count: number;
}

export interface PrivacyAnalysis {
  redacted_text: string;
  total_redactions: number;
  redactions: RedactionCount[];
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
  ai_analysis: AIAnalysis;
  privacy_analysis: PrivacyAnalysis;
}
export interface AIEvidence {
  text: string;
  reason: string;
}

export interface AIAnalysis {
  status: string;
  provider: string;
  category: string | null;
  confidence: number | null;
  summary: string;
  evidence: AIEvidence[];
  limitations: string[];
  privacy_applied: boolean;
  
}