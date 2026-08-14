import { useQuery } from "@tanstack/react-query";
import { getEvents } from "../api/events";

export const useEvents = () => useQuery({ queryKey: ["security-events"], queryFn: getEvents, refetchInterval: 5_000 });
