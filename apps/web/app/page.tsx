"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { useInView } from "react-intersection-observer";
import { useEffect, useState } from "react";

export default function Landing() {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [featuresRef, featuresInView] = useInView({ threshold: 0.1, triggerOnce: true });

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
    };
    window.addEventListener("mousemove", handleMouseMove);
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, []);

  return (
    <main className="min-h-screen overflow-hidden relative">
      {/* Animated background gradient */}
      <div className="fixed inset-0 gradient-bg opacity-10" />
      
      {/* Interactive cursor follower */}
      <div 
        className="fixed w-96 h-96 rounded-full opacity-20 pointer-events-none"
        style={{
          background: `radial-gradient(circle, rgba(102, 126, 234, 0.3) 0%, transparent 70%)`,
          left: mousePosition.x - 192,
          top: mousePosition.y - 192,
          transition: 'all 0.3s ease-out'
        }}
      />

      <section className="max-w-5xl mx-auto px-6 py-24 text-center relative">
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
        >
          {/* Floating badge */}
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2, duration: 0.6 }}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 backdrop-blur-md border border-white/10 mb-8"
          >
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
            </span>
            <span className="text-sm text-neutral-300">Live Trading Active</span>
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.8 }}
            className="text-5xl md:text-6xl font-bold tracking-tight"
          >
            <span className="gradient-text">Smarter Long-Term Investing.</span>
            <br/>
            <span className="text-white">Fully Automated.</span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5, duration: 0.8 }}
            className="mt-6 text-lg text-neutral-300 max-w-2xl mx-auto"
          >
            Waardhaven Autoindex dynamically rebalances a diversified portfolio using daily data.
            Transparent performance. No day trading. No noise.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7, duration: 0.8 }}
            className="mt-10 flex items-center justify-center gap-4"
          >
            <Link href="/register">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="btn"
              >
                Sign Up
              </motion.button>
            </Link>
            <Link href="/login">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="px-6 py-3 rounded-xl bg-white/5 backdrop-blur-md border border-white/10 hover:bg-white/10 transition-all"
              >
                Log In
              </motion.button>
            </Link>
          </motion.div>
        </motion.div>

        <div ref={featuresRef} className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-6">
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={featuresInView ? { opacity: 1, y: 0 } : {}}
            transition={{ delay: 0.2, duration: 0.6 }}
            whileHover={{ scale: 1.05, rotateY: 5 }}
            className="card"
            style={{ transformStyle: 'preserve-3d' }}
          >
            <h3 className="font-semibold text-xl gradient-text">Daily Rebalancing</h3>
            <p className="mt-2 text-neutral-300">Removes weak assets and equal-weights the rest.</p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={featuresInView ? { opacity: 1, y: 0 } : {}}
            transition={{ delay: 0.4, duration: 0.6 }}
            whileHover={{ scale: 1.05, rotateY: 5 }}
            className="card"
            style={{ transformStyle: 'preserve-3d' }}
          >
            <h3 className="font-semibold text-xl gradient-text">Clear Performance</h3>
            <p className="mt-2 text-neutral-300">Compare the Autoindex against S&P 500.</p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={featuresInView ? { opacity: 1, y: 0 } : {}}
            transition={{ delay: 0.6, duration: 0.6 }}
            whileHover={{ scale: 1.05, rotateY: 5 }}
            className="card"
            style={{ transformStyle: 'preserve-3d' }}
          >
            <h3 className="font-semibold text-xl gradient-text">Long-Term Focus</h3>
            <p className="mt-2 text-neutral-300">No intraday signals, only daily closes.</p>
          </motion.div>
        </div>
      </section>
    </main>
  );
}
