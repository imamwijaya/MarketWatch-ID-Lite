
import Image from "next/image";
import PriceChart from "@/components/price-chart";
import VolumeChart from "@/components/volume-chart";
import AnomalyEvents from "@/components/anomaly-events";
import AlertBreakdown from "@/components/alert-breakdown";
import DetectionPerformance from "@/components/detection-performance";
import { Suspense } from "react";
import MarketMetrics from "@/components/market-metrics";


export default function Home() {
  return (
    <main className="min-h-screen bg-[#DEDEE1] p-4 text-[#18221E] md:p-8">
      <div className="mx-auto min-h-[calc(100vh-4rem)] max-w-[1440px] rounded-[24px] bg-[#F3F3F1] p-4 md:p-6">


        {/* RESPONSIVE NAVBAR */}
        <header className="rounded-[22px] bg-white px-4 py-4 md:flex md:items-center md:justify-between md:gap-5 md:rounded-full md:px-7">

          {/* Logo and mobile demo indicator */}
          <div className="flex items-center justify-between gap-3">
            <Image
              src="/brand/logo-horizontal.svg"
              alt="MarketWatch-ID Lite"
              width={230}
              height={50}
              className="h-9 w-auto max-w-[175px] object-contain md:max-w-[230px]"
              priority
            />

            <span className="shrink-0 rounded-full bg-[#E4F3EB] px-3 py-2 text-[10px] font-semibold text-[#087A50] md:hidden">
              DEMO
            </span>
          </div>

          {/* Responsive navigation */}
          <nav
            aria-label="Dashboard navigation"
            className="mt-4 flex w-full items-center gap-1 overflow-x-auto border-t border-[#ECEEEC] pt-3 text-xs whitespace-nowrap md:mt-0 md:w-auto md:border-0 md:pt-0 md:text-sm"
          >
            {[
              { label: "Overview", href: "#overview" },
              { label: "Analytics", href: "#analytics" },
              { label: "Alerts", href: "#alerts" },
              { label: "Evaluation", href: "#evaluation" },
            ].map((item) => (
              <a
                key={item.href}
                href={item.href}
                className="rounded-full px-3 py-2 text-[#65716A] transition-colors hover:bg-[#F1F2F0] hover:text-[#18221E] focus-visible:outline-2 focus-visible:outline-[#11835D] md:px-4"
              >
                {item.label}
              </a>
            ))}
          </nav>

          {/* Desktop demo indicator */}
          <span className="hidden shrink-0 rounded-full bg-[#E4F3EB] px-4 py-2 text-xs font-semibold text-[#087A50] md:inline-flex">
            SYNTHETIC DEMO
          </span>
        </header>


        {/* PAGE HEADING */}
        <section id="overview" className="scroll-mt-6 pb-9 pt-14 md:px-10">
          <p className="mb-3 text-xs font-semibold tracking-[0.14em] text-[#15845D]">
            EQUITY MARKET MONITORING
          </p>

          <h1 className="text-3xl font-semibold tracking-tight md:text-5xl">
            Market surveillance overview
          </h1>

          <p className="mt-4 max-w-2xl text-sm leading-7 text-[#7B837E]">
            Price movement, trading volume, and anomaly detection
            for the BBCA_DEMO synthetic dataset.
          </p>
        </section>

        {/* SUMMARY METRICS */}
        <Suspense
          fallback={
            <div
              role="status"
              className="rounded-[20px] bg-white p-6 text-sm text-[#7B837E]"
            >
              Loading market metrics...
            </div>
          }
        >
          <MarketMetrics />
        </Suspense>


        {/* PRIMARY ANALYTICS BENTO */}
       <section id="analytics" className="mt-5 grid scroll-mt-6 grid-cols-1 gap-5 xl:grid-cols-12">
          <div className="min-w-0 xl:col-span-8">
            <PriceChart />
          </div>

          <div className="min-w-0 xl:col-span-4">
            <Suspense
              fallback={
                <div className="rounded-[24px] bg-white p-7 text-sm text-[#7B837E]">
                  Loading alert breakdown...
                </div>
              }
            >
              <AlertBreakdown />
            </Suspense>
          </div>
        </section>

        {/* VOLUME ANALYTICS */}
        <div className="mt-5">
          <VolumeChart />
        </div>

        {/* ANOMALY EVENTS */}
        <div id="alerts" className="mt-5 scroll-mt-6">
          <AnomalyEvents />
        </div>

        {/* DETECTION PERFORMANCE */}
        <div id="evaluation" className="mt-5 scroll-mt-6">
          <DetectionPerformance />
        </div>


        <p className="mt-6 text-xs leading-5 text-[#7B837E]">
          Portfolio prototype. Synthetic records only.
          Not affiliated with the Indonesia Stock Exchange.
        </p>

      </div>
    </main>
  );
}
