type RiskBadgeProps = {
  score: number;
};

export default function RiskBadge({ score }: RiskBadgeProps) {
  let color = "#9ca3af"; // gray
  let label = "Low";

  if (score >= 80) {
    color = "#ef4444"; // red
    label = "High";
  } else if (score >= 50) {
    color = "#f97316"; // orange
    label = "Medium";
  }

  return (
    <span
      style={{
        display: "inline-block",
        padding: "4px 10px",
        borderRadius: 999,
        backgroundColor: color,
        color: "white",
        fontSize: 12,
        fontWeight: 600,
        marginLeft: 8,
      }}
    >
      {label} ({score})
    </span>
  );
}
