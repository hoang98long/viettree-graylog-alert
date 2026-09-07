import { apiClient } from "./client";
import type { EventsPage, SecurityEventDetail } from "../types/event";

export async function getEvents(): Promise<EventsPage> {
  return (await apiClient.get<EventsPage>("/api/events")).data;
}

export async function getEvent(eventId: string): Promise<SecurityEventDetail> {
  return (await apiClient.get<SecurityEventDetail>(`/api/events/${encodeURIComponent(eventId)}`)).data;
}
