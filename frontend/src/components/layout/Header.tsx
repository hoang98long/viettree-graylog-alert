import { Activity } from "lucide-react";
import type { SystemStatus } from "../../types/status";

export function Header({ status }: { status?: SystemStatus }) {
  const online = status?.graylog === "connected";
  const label = !status ? "CHECKING" : online ? "SYSTEM ONLINE" : "SYSTEM DEGRADED";
  return <header className="flex items-center justify-between border-b border-slate-800 bg-slate-950 px-5 py-4 lg:px-8"><div><h1 className="text-lg font-semibold text-slate-100">ASA Configuration Monitor</h1><p className="text-sm text-slate-400">Security event monitoring</p></div><div className={`flex items-center gap-2 text-xs font-semibold ${online ? "text-emerald-400" : "text-amber-400"}`}><Activity size={16}/>{label}</div></header>;
}
