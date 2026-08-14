export interface SystemStatus {
  graylog: string;
  telegram: string;
  asa_ip: string;
  graylog_url: string;
  poll_interval: number;
  last_poll: string | null;
  events_today: number;
}
