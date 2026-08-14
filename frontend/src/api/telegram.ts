import { apiClient } from "./client";

export async function testTelegram(): Promise<void> { await apiClient.post("/api/test/telegram"); }
