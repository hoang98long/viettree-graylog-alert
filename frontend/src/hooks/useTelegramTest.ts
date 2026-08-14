import { useMutation } from "@tanstack/react-query";
import { testTelegram } from "../api/telegram";

export const useTelegramTest = () => useMutation({ mutationFn: testTelegram });
