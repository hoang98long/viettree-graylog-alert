export type Severity = "INFO" | "WARNING" | "CRITICAL";

export interface SecurityEvent {
  event_id: string;
  timestamp: string;
  source_ip: string;
  event_type: string;
  severity: Severity;
  message: string;
  telegram_sent: boolean;
  telegram_error: string | null;
  raw_data: string;
}

export type SecurityEventDetail = SecurityEvent;
