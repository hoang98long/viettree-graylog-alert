import type { ReactNode } from "react";
import { Header } from "../components/layout/Header";
import { Sidebar } from "../components/layout/Sidebar";
import { useSystemStatus } from "../hooks/useSystemStatus";
export function DashboardLayout({ children }: { children: ReactNode }) { const status = useSystemStatus(); return <div className="min-h-screen bg-slate-950 text-slate-100 lg:flex"><Sidebar status={status.data}/><div className="min-w-0 flex-1"><Header status={status.data}/><main className="mx-auto max-w-7xl p-5 lg:p-8">{children}</main></div></div>; }
