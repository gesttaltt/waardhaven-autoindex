import Link from "next/link";

export default function Landing() {
  return (
    <main className="min-h-screen">
      <section className="max-w-5xl mx-auto px-6 py-24 text-center">
        <h1 className="text-5xl font-bold tracking-tight">Smarter Long‑Term Investing.<br/>Fully Automated.</h1>
        <p className="mt-6 text-lg text-neutral-300">
          Waardhaven Autoindex dynamically rebalances a diversified portfolio using daily data.
          Transparent performance. No day trading. No noise.
        </p>
        <div className="mt-10 flex items-center justify-center gap-4">
          <Link href="/register" className="btn">Sign Up</Link>
          <Link href="/login" className="btn">Log In</Link>
        </div>

        <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="card">
            <h3 className="font-semibold text-xl">Daily Rebalancing</h3>
            <p className="mt-2 text-neutral-300">Removes weak assets and equal‑weights the rest.</p>
          </div>
          <div className="card">
            <h3 className="font-semibold text-xl">Clear Performance</h3>
            <p className="mt-2 text-neutral-300">Compare the Autoindex against S&P 500.</p>
          </div>
          <div className="card">
            <h3 className="font-semibold text-xl">Long‑Term Focus</h3>
            <p className="mt-2 text-neutral-300">No intraday signals, only daily closes.</p>
          </div>
        </div>
      </section>
    </main>
  );
}
