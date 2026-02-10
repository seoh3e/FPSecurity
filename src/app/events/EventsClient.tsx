"use client";

import Link from "next/link";
import RiskBadge from "../components/RiskBadge";
import type { CSSProperties, ReactNode } from "react";
import type { RiskLevel, SecurityEvent } from "../types/events";
import { useState } from "react";

const riskRank: Record<RiskLevel, number> = { High: 3, Medium: 2, Low: 1 };

type Filter = RiskLevel | "ALL";

export default function EventsClient({ events }: { events: SecurityEvent[] }) {
  const [filter, setFilter] = useState<Filter>("ALL");

  const sorted = [...events].sort((a, b) => {
    if (riskRank[b.riskLevel] !== riskRank[a.riskLevel]) {
      return riskRank[b.riskLevel] - riskRank[a.riskLevel];
    }
    return b.riskScore - a.riskScore;
  });

  const filtered =
    filter === "ALL" ? sorted : sorted.filter((e) => e.riskLevel === filter);

  return (
    <>
      {/* ✅ Filter Bar */}
      <div
        style={{
          display: "flex",
          gap: 10,
          alignItems: "center",
          marginTop: 16,
          marginBottom: 12,
        }}
      >
        <span style={{ opacity: 0.75, fontSize: 13 }}>Risk Filter:</span>

        <FilterButton active={filter === "ALL"} onClick={() => setFilter("ALL")}>
          All
        </FilterButton>
        <FilterButton
          active={filter === "High"}
          onClick={() => setFilter("High")}
        >
          High
        </FilterButton>
        <FilterButton
          active={filter === "Medium"}
          onClick={() => setFilter("Medium")}
        >
          Medium
        </FilterButton>
        <FilterButton active={filter === "Low"} onClick={() => setFilter("Low")}>
          Low
        </FilterButton>

        <span style={{ marginLeft: "auto", opacity: 0.65, fontSize: 13 }}>
          Showing <b style={{ opacity: 0.95 }}>{filtered.length}</b> events
        </span>
      </div>

      {/* ✅ Table */}
      <div
        style={{
          borderRadius: 14,
          border: "1px solid rgba(255,255,255,0.08)",
          overflow: "hidden",
          background: "rgba(255,255,255,0.03)",
        }}
      >
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ background: "rgba(255,255,255,0.04)" }}>
              <Th>탐지 유형</Th>
              <Th>Player</Th>
              <Th>Risk</Th>
              <Th>Detected At</Th>
              <Th style={{ textAlign: "right" }}>Action</Th>
            </tr>
          </thead>

          <tbody>
            {filtered.map((e) => (
              <tr
                key={e.id}
                style={{ borderTop: "1px solid rgba(255,255,255,0.06)" }}
              >
                <Td>
                  <b>{e.type}</b>
                </Td>

                <Td>
                  <Link
                    href={`/players/${e.playerId}`}
                    style={{ textDecoration: "none" }}
                  >
                    <span style={{ color: "white" }}>#{e.playerId}</span>
                  </Link>
                </Td>

                <Td>
                  <RiskBadge score={e.riskScore} />
                </Td>

                <Td style={{ opacity: 0.85 }}>{e.detectedAt}</Td>

                <Td style={{ textAlign: "right" }}>
                  <Link
                    href={`/players/${e.playerId}`}
                    style={{
                      textDecoration: "none",
                      display: "inline-block",
                      padding: "8px 12px",
                      borderRadius: 10,
                      border: "1px solid rgba(255,255,255,0.12)",
                      color: "white",
                      background: "rgba(0,0,0,0.2)",
                    }}
                  >
                    View Detail →
                  </Link>
                </Td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}

/** --- UI helpers --- */

function FilterButton({
  active,
  children,
  onClick,
}: {
  active: boolean;
  children: ReactNode;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      style={{
        cursor: "pointer",
        borderRadius: 999,
        padding: "7px 12px",
        fontSize: 13,
        border: active
          ? "1px solid rgba(255,255,255,0.28)"
          : "1px solid rgba(255,255,255,0.12)",
        background: active ? "rgba(255,255,255,0.10)" : "rgba(0,0,0,0.2)",
        color: "white",
      }}
    >
      {children}
    </button>
  );
}

function Th({
  children,
  style,
}: {
  children: ReactNode;
  style?: CSSProperties;
}) {
  return (
    <th
      style={{
        textAlign: "left",
        fontWeight: 600,
        padding: "14px 14px",
        fontSize: 13,
        opacity: 0.8,
        ...style,
      }}
    >
      {children}
    </th>
  );
}

function Td({
  children,
  style,
}: {
  children: ReactNode;
  style?: CSSProperties;
}) {
  return (
    <td
      style={{
        padding: "14px 14px",
        verticalAlign: "middle",
        ...style,
      }}
    >
      {children}
    </td>
  );
}
