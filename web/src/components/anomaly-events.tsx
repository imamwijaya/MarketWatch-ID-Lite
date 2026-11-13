
"use client";

import { useEffect, useState } from "react";

// ========================================
// TYPES
// ========================================

type AlertType =
  | "PRICE_ONLY"
  | "VOLUME_ONLY"
  | "COMBINED";

type FilterType = "ALL" | AlertType;

type ApiAlert = {
  date: string;
  symbol: string;
  close: number;
  volume: number;
  price_zscore: number | null;
  volume_ratio: number | null;
  alert_type: AlertType;
};

type AlertsResponse = {
  dataset: string;
  count: number;
  alerts: ApiAlert[];
};

// ========================================
// CONFIGURATION
// ========================================

const filters: { label: string; value: FilterType }[] = [
  { label: "All alerts", value: "ALL" },
  { label: "Price", value: "PRICE_ONLY" },
  { label: "Volume", value: "VOLUME_ONLY" },
  { label: "Combined", value: "COMBINED" },
];

const labels: Record<AlertType, string> = {
  PRICE_ONLY: "Price only",
  VOLUME_ONLY: "Volume only",
  COMBINED: "Combined",
};

const typeStyles: Record<AlertType, string> = {
  PRICE_ONLY: "bg-amber-50 text-amber-800",
  VOLUME_ONLY: "bg-emerald-50 text-emerald-800",
  COMBINED: "bg-red-50 text-red-700",
};

const numberFormatter = new Intl.NumberFormat("en-US", {
  maximumFractionDigits: 2,
});

// ========================================
// COMPONENT
// ========================================

export default function AnomalyEvents() {
  const [activeFilter, setActiveFilter] =
    useState<FilterType>("ALL");

  const [alerts, setAlerts] = useState<ApiAlert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // ========================================
  // FETCH DATA FROM API
  // ========================================

  useEffect(() => {
    const controller = new AbortController();

    async function loadAlerts() {
      try {
        const response = await fetch("/api/alerts", {
          cache: "no-store",
          signal: controller.signal,
        });

        if (!response.ok) {
          throw new Error(
            `API returned HTTP ${response.status}`
          );
        }

        const payload =
          (await response.json()) as AlertsResponse;

        if (
          !Array.isArray(payload.alerts) ||
          payload.count !== payload.alerts.length
        ) {
          throw new Error("Invalid alerts response");
        }

        const sortedAlerts = [...payload.alerts].sort(
          (a, b) => b.date.localeCompare(a.date)
        );

        if (!controller.signal.aborted) {
          setAlerts(sortedAlerts);
          setError(null);
        }
      } catch {
        if (!controller.signal.aborted) {
          setError("Unable to load anomaly events.");
        }
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    }

    void loadAlerts();

    return () => controller.abort();
  }, []);

  // ========================================
  // FILTER DATA
  // ========================================

  const filteredAlerts = alerts.filter(
    (row) =>
      activeFilter === "ALL" ||
      row.alert_type === activeFilter
  );

  // ========================================
  // LOADING AND ERROR STATES
  // ========================================

  if (loading || error) {
    return (
      <section className="w-full rounded-[24px] bg-white p-5 md:p-7">
        <h2 className="text-lg font-semibold tracking-tight">
          Anomaly events
        </h2>

        <p
          className="mt-4 text-sm text-[#7B837E]"
          role={error ? "alert" : "status"}
        >
          {error ?? "Loading anomaly events..."}
        </p>
      </section>
    );
  }

  // ========================================
  // MAIN UI
  // ========================================

  return (
    <section className="w-full min-w-0 max-w-full overflow-hidden rounded-[24px] bg-white p-5 md:p-7">

      {/* HEADER */}
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold tracking-tight">
            Anomaly events
          </h2>

          <p className="mt-1 text-sm text-[#7B837E]">
            {filteredAlerts.length} flagged observations
          </p>
        </div>

        <span className="rounded-full bg-[#F1F2F0] px-3 py-2 text-xs font-medium">
          BBCA_DEMO
        </span>
      </div>

      {/* FILTER BUTTONS */}
      <div
        className="mt-6 flex flex-wrap gap-2"
        role="group"
        aria-label="Filter anomaly type"
      >
        {filters.map((filter) => {
          const isActive = activeFilter === filter.value;

          return (
            <button
              key={filter.value}
              type="button"
              aria-pressed={isActive}
              onClick={() => setActiveFilter(filter.value)}
              className={`rounded-full px-4 py-2 text-xs font-medium transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#11835D] ${
                isActive
                  ? "bg-[#11835D] text-white"
                  : "bg-[#F1F2F0] text-[#65716A] hover:bg-[#E6EBE7]"
              }`}
            >
              {filter.label}
            </button>
          );
        })}
      </div>

      {/* TABLE CONTAINER */}
      <div
        className="mt-6 w-full min-w-0 max-w-full overflow-x-auto overscroll-x-contain"
        role="region"
        aria-label="Anomaly events table"
        tabIndex={0}
      >
        <table className="w-full min-w-[720px] border-collapse text-left text-sm">
          <thead>
            <tr className="border-b border-[#E8EBE9] text-xs text-[#7B837E]">
              <th className="pb-4 pr-4 font-medium">
                Date
              </th>

              <th className="pb-4 pr-4 font-medium">
                Classification
              </th>

              <th className="pb-4 pr-4 text-right font-medium">
                Closing price
              </th>

              <th className="pb-4 pr-4 text-right font-medium">
                Z-score
              </th>

              <th className="pb-4 pr-4 text-right font-medium">
                Volume
              </th>

              <th className="pb-4 text-right font-medium">
                Vol. ratio
              </th>
            </tr>
          </thead>

          <tbody>
            {filteredAlerts.map((row) => {
              const type = row.alert_type;

              return (
                <tr
                  key={`${row.symbol}-${row.date}`}
                  className="border-b border-[#EFF1EF] last:border-0"
                >
                  <td className="py-4 pr-4 font-medium tabular-nums">
                    {row.date}
                  </td>

                  <td className="py-4 pr-4">
                    <span
                      className={`inline-flex whitespace-nowrap rounded-full px-3 py-1 text-xs font-medium ${typeStyles[type]}`}
                    >
                      {labels[type]}
                    </span>
                  </td>

                  <td className="py-4 pr-4 text-right tabular-nums">
                    {numberFormatter.format(row.close)}
                  </td>

                  <td className="py-4 pr-4 text-right tabular-nums">
                    {row.price_zscore === null
                      ? "—"
                      : row.price_zscore.toFixed(2)}
                  </td>

                  <td className="py-4 pr-4 text-right tabular-nums">
                    {numberFormatter.format(row.volume)}
                  </td>

                  <td className="py-4 text-right tabular-nums">
                    {row.volume_ratio === null
                      ? "—"
                      : `${row.volume_ratio.toFixed(2)}×`}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>

        {filteredAlerts.length === 0 && (
          <p className="py-10 text-center text-sm text-[#7B837E]">
            No events match the selected filter.
          </p>
        )}
      </div>

      {/* FOOTNOTE */}
      <p className="mt-5 border-t border-[#ECEEEC] pt-4 text-xs text-[#8B938E]">
        Rule-based statistical alerts from synthetic data.
        Events are not evidence of market manipulation.
      </p>
    </section>
  );
}
