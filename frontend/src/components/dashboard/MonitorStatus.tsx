import { Clock, Timer, TriangleAlert } from "lucide-react";
import type { SystemStatus } from "../../types/status";
import { formatTime } from "../../utils/formatDate";
import { StatusCard } from "./StatusCard";
export function MonitorStatus({ status }: { status: SystemStatus }) { return <section className="grid gap-4 md:grid-cols-3"><StatusCard title="LAST POLL" status={formatTime(status.last_poll)} icon={<Clock size={19}/>}/><StatusCard title="POLL INTERVAL" status={`${status.poll_interval} seconds`} icon={<Timer size={19}/>}/><StatusCard title="EVENTS TODAY" status={String(status.events_today)} icon={<TriangleAlert size={19}/>}/></section>; }
