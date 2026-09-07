export type Severity = "INFO" | "WARNING" | "CRITICAL";

export interface SecurityEvent {
  id: number;
  event_id: string;
  graylog_message_id: string | null;
  timestamp: string;
  received_at: string;
  source: string;
  source_ip: string;
  device_name: string | null;
  device_ip: string | null;
  device_type: string | null;
  event_type: string;
  severity: Severity;
  message: string;
  detection_reason: string | null;
  matched_pattern: string | null;
  telegram_sent: boolean;
  telegram_sent_at: string | null;
  telegram_error: string | null;
  raw_data: string;
}

export type SecurityEventDetail = SecurityEvent;

export interface EventsPage { items: SecurityEvent[]; total: number; }
