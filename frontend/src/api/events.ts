import { apiClient } from "./client";
import type { SecurityEvent, SecurityEventDetail } from "../types/event";

export async function getEvents(): Promise<SecurityEvent[]> {
  return (await apiClient.get<SecurityEvent[]>("/api/events")).data;
}

export async function getEvent(eventId: string): Promise<SecurityEventDetail> {
  return (await apiClient.get<SecurityEventDetail>(`/api/events/${encodeURIComponent(eventId)}`)).data;
}
