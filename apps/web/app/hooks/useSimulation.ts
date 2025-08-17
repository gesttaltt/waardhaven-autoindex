import { useState } from 'react';
import { SimulationRequest, SimulationResult } from '../types/portfolio';
import { portfolioService } from '../services/api/portfolio';
import { DEFAULT_CURRENCY, DEFAULT_SIMULATION_AMOUNT, DEFAULT_START_DATE } from '../constants/config';

export interface UseSimulationReturn {
  amount: number;
  setAmount: (amount: number) => void;
  currency: string;
  setCurrency: (currency: string) => void;
  startDate: string;
  setStartDate: (date: string) => void;
  simResult: SimulationResult | null;
  simulating: boolean;
  error: string | null;
  runSimulation: () => Promise<void>;
  resetSimulation: () => void;
}

export function useSimulation(): UseSimulationReturn {
  const [amount, setAmount] = useState(DEFAULT_SIMULATION_AMOUNT);
  const [currency, setCurrency] = useState(DEFAULT_CURRENCY);
  const [startDate, setStartDate] = useState(DEFAULT_START_DATE);
  const [simResult, setSimResult] = useState<SimulationResult | null>(null);
  const [simulating, setSimulating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const runSimulation = async () => {
    setSimulating(true);
    setError(null);
    
    try {
      const request: SimulationRequest = {
        amount,
        startDate,
        currency,
      };
      
      const result = await portfolioService.runSimulation(request);
      setSimResult(result);
    } catch (err: any) {
      console.error('Simulation failed:', err);
      setError(err.message || 'Failed to run simulation. Please try again.');
    } finally {
      setSimulating(false);
    }
  };

  const resetSimulation = () => {
    setSimResult(null);
    setError(null);
  };

  return {
    amount,
    setAmount,
    currency,
    setCurrency,
    startDate,
    setStartDate,
    simResult,
    simulating,
    error,
    runSimulation,
    resetSimulation,
  };
}