import type { Severity } from "../../types/event";

const severityStyles: Record<Severity, string> = { INFO: "bg-slate-700 text-slate-200", WARNING: "bg-amber-400/15 text-amber-300", CRITICAL: "bg-red-500/15 text-red-300" };
export function SeverityBadge({ severity }: { severity: Severity }) { return <span className={`rounded px-2 py-1 text-xs font-semibold ${severityStyles[severity]}`}>{severity}</span>; }
export function TelegramBadge({ sent, error }: { sent: boolean; error: string | null }) { const label = sent ? "SENT" : error ? "FAILED" : "PENDING"; const color = sent ? "text-emerald-300" : error ? "text-red-300" : "text-slate-400"; return <span className={`text-xs font-semibold ${color}`}>{label}</span>; }
