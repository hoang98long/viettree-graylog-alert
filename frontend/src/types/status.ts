export interface SystemStatus {
  status: string;
  graylog: string;
  graylog_connected: boolean;
  telegram: string;
  telegram_enabled: boolean;
  polling: string;
  firewall_label: string;
  graylog_url: string;
  poll_interval: number;
  last_poll: string | null;
  last_message_at: string | null;
  events_today: number;
  events_count: number;
}
