/**
 * Hook for managing user credit state.
 */

import { useState, useCallback } from "react";

interface CreditState {
  balance: number;
  isLoading: boolean;
  error: string | null;
}

export function useCredits(initialBalance: number = 0) {
  const [state, setState] = useState<CreditState>({
    balance: initialBalance,
    isLoading: false,
    error: null,
  });

  const fetchBalance = useCallback(async (token: string) => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }));
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_URL || "/api/backend"}/api/v1/credits/balance`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (!response.ok) throw new Error("Failed to fetch balance");

      const data = await response.json();
      setState({ balance: data.credits_balance, isLoading: false, error: null });
    } catch (error) {
      setState((prev) => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : "Unknown error",
      }));
    }
  }, []);

  const deductCredits = useCallback((amount: number) => {
    setState((prev) => ({
      ...prev,
      balance: Math.max(0, prev.balance - amount),
    }));
  }, []);

  const addCredits = useCallback((amount: number) => {
    setState((prev) => ({
      ...prev,
      balance: prev.balance + amount,
    }));
  }, []);

  return {
    ...state,
    fetchBalance,
    deductCredits,
    addCredits,
  };
}
