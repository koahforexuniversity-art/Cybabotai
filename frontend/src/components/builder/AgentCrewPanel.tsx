"use client";

/**
 * AgentCrewPanel - Container for all 7 agent cards.
 * Shows the crew status during strategy building.
 */

import { AgentCard, AgentStatus, AGENTS } from "./AgentCard";

interface AgentCrewPanelProps {
  agentStatuses: Record<number, AgentStatus>;
  agentMessages: Record<number, string>;
  agentProgress: Record<number, number>;
}

export function AgentCrewPanel({
  agentStatuses,
  agentMessages,
  agentProgress,
}: AgentCrewPanelProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-white">AI Agent Crew</h2>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-xs text-white/50">
            {Object.values(agentStatuses).filter((s) => s === "active").length > 0
              ? "Processing..."
              : Object.values(agentStatuses).filter((s) => s === "success").length === 7
              ? "Complete"
              : "Ready"}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-2">
        {AGENTS.map((agent) => (
          <AgentCard
            key={agent.id}
            agent={agent}
            status={agentStatuses[agent.id] || "idle"}
            message={agentMessages[agent.id]}
            progress={agentProgress[agent.id]}
          />
        ))}
      </div>
    </div>
  );
}
