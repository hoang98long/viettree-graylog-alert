import { apiClient } from "./client";
import type { SystemStatus } from "../types/status";

export async function getSystemStatus(): Promise<SystemStatus> {
  return (await apiClient.get<SystemStatus>("/api/status")).data;
}
