export type RiskLevel = "High" | "Medium" | "Low";

export type SecurityEvent = {
  id: string;
  type: string;
  playerId: string;
  riskScore: number;
  riskLevel: RiskLevel;
  detectedAt: string;
};
