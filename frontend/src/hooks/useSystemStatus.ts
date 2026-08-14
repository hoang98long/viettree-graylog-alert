import { useQuery } from "@tanstack/react-query";
import { getSystemStatus } from "../api/status";

export const useSystemStatus = () => useQuery({ queryKey: ["system-status"], queryFn: getSystemStatus, refetchInterval: 5_000 });
