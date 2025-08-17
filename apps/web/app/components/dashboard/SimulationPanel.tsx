"use client";

import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CurrencyMap } from '../../types/api';
import { SimulationResult } from '../../types/portfolio';
import { portfolioService } from '../../services/api/portfolio';

interface SimulationPanelProps {
  amount: number;
  setAmount: (amount: number) => void;
  currency: string;
  setCurrency: (currency: string) => void;
  startDate: string;
  setStartDate: (date: string) => void;
  simResult: SimulationResult | null;
  simulating: boolean;
  onSimulate: () => void;
}

export function SimulationPanel({
  amount,
  setAmount,
  currency,
  setCurrency,
  startDate,
  setStartDate,
  simResult,
  simulating,
  onSimulate,
}: SimulationPanelProps) {
  const [currencies, setCurrencies] = useState<CurrencyMap>({});

  useEffect(() => {
    portfolioService.getCurrencies()
      .then(setCurrencies)
      .catch(console.error);
  }, []);

  return (
    <motion.section
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.5 }}
      className="card mb-6"
    >
      <h2 className="text-xl font-semibold mb-4 gradient-text">Investment Simulator</h2>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label className="text-sm text-neutral-300">Amount</label>
          <input 
            className="input mt-1" 
            type="number" 
            value={amount} 
            onChange={e => setAmount(parseFloat(e.target.value))} 
          />
        </div>
        <div>
          <label className="text-sm text-neutral-300">Currency</label>
          <select 
            className="input mt-1" 
            value={currency} 
            onChange={e => setCurrency(e.target.value)}
          >
            {Object.entries(currencies).map(([code, name]) => (
              <option key={code} value={code}>{code} - {name}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="text-sm text-neutral-300">Start date</label>
          <input 
            className="input mt-1" 
            type="date" 
            value={startDate} 
            onChange={e => setStartDate(e.target.value)} 
          />
        </div>
        <div className="flex items-end">
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="btn w-full relative"
            onClick={onSimulate}
            disabled={simulating}
          >
            {simulating ? (
              <span className="flex items-center justify-center gap-2">
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                  className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full"
                />
                Simulating...
              </span>
            ) : (
              "Run Simulation"
            )}
          </motion.button>
        </div>
      </div>

      <AnimatePresence>
        {simResult && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="mt-6 p-6 rounded-xl bg-gradient-to-br from-purple-500/10 via-blue-500/10 to-pink-500/10 border border-purple-500/20 backdrop-blur-sm"
          >
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="text-center">
                <p className="text-sm text-neutral-400 mb-1">Initial Investment</p>
                <p className="text-xl font-bold text-white">
                  {simResult.currency} {amount.toLocaleString('en-US', { 
                    minimumFractionDigits: 2, 
                    maximumFractionDigits: 2 
                  })}
                </p>
              </div>
              
              <div className="text-center">
                <p className="text-sm text-neutral-400 mb-1">Final Amount</p>
                <p className="text-xl font-bold gradient-text">
                  {simResult.currency} {simResult.amount_final.toLocaleString('en-US', { 
                    minimumFractionDigits: 2, 
                    maximumFractionDigits: 2 
                  })}
                </p>
              </div>
              
              <div className="text-center">
                <p className="text-sm text-neutral-400 mb-1">Total Return</p>
                <p className={`text-xl font-bold ${simResult.roi_pct >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {simResult.roi_pct > 0 ? '+' : ''}{simResult.roi_pct.toFixed(2)}%
                </p>
              </div>
              
              <div className="text-center">
                <p className="text-sm text-neutral-400 mb-1">Profit/Loss</p>
                <p className={`text-xl font-bold ${simResult.amount_final >= amount ? 'text-green-400' : 'text-red-400'}`}>
                  {simResult.amount_final >= amount ? '+' : ''}{simResult.currency} {(simResult.amount_final - amount).toLocaleString('en-US', { 
                    minimumFractionDigits: 2, 
                    maximumFractionDigits: 2 
                  })}
                </p>
              </div>
            </div>
            
            {/* Growth visualization bar */}
            <div className="mt-4">
              <div className="flex justify-between text-xs text-neutral-400 mb-2">
                <span>Growth Timeline</span>
                <span>{startDate} → Today</span>
              </div>
              <div className="w-full bg-white/10 rounded-full h-2 overflow-hidden">
                <motion.div 
                  className={`h-full rounded-full ${simResult.roi_pct >= 0 ? 'bg-gradient-to-r from-green-500 to-emerald-400' : 'bg-gradient-to-r from-red-500 to-orange-400'}`}
                  initial={{ width: 0 }}
                  animate={{ width: `${Math.min(Math.abs(simResult.roi_pct), 100)}%` }}
                  transition={{ duration: 1, delay: 0.5 }}
                />
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.section>
  );
}