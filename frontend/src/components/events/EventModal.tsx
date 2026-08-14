import { useEffect } from "react";
import { X } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { getEvent } from "../../api/events";
import { Loading } from "../common/Loading";
import { EventDetail } from "./EventDetail";

export function EventModal({ eventId, onClose }: { eventId: string | null; onClose: () => void }) { useEffect(() => { const close = (event: KeyboardEvent) => { if (event.key === "Escape") onClose(); }; window.addEventListener("keydown", close); return () => window.removeEventListener("keydown", close); }, [onClose]); const detail = useQuery({ queryKey: ["event", eventId], queryFn: () => getEvent(eventId ?? ""), enabled: Boolean(eventId) }); if (!eventId) return null; return <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 p-4" onMouseDown={onClose}><section className="max-h-[90vh] w-full max-w-2xl overflow-auto rounded-xl border border-slate-700 bg-slate-900 p-6 shadow-2xl" onMouseDown={event => event.stopPropagation()}><div className="mb-6 flex items-center justify-between"><h2 className="text-lg font-semibold text-white">Event Details</h2><button onClick={onClose} className="rounded p-1 text-slate-400 hover:bg-slate-800 hover:text-white" aria-label="Close"><X/></button></div>{detail.isLoading ? <Loading label="Loading event details..."/> : detail.data ? <EventDetail event={detail.data}/> : <p className="text-red-300">Unable to load event details.</p>}</section></div>; }
