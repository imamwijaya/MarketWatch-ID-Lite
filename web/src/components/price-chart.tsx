
"use client";

import {
  useObservations,
  type ApiObservation,
} from "@/lib/use-observations";

import {
  CartesianGrid,
  Line,
  LineChart,
  ReferenceDot,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

// ========================================
// TYPES
// ========================================

type ChartPoint = {
  date: string;
  close: number;
  alertType: ApiObservation["alert_type"];
  zscore: number | null;
};

// ========================================
// HELPERS
// ========================================

function formatMonth(date: string) {
  return new Date(`${date}T00:00:00`).toLocaleDateString(
    "en-US",
    {
      month: "short",
      year: "2-digit",
    }
  );
}

// ========================================
// COMPONENT
// ========================================

export default function PriceChart() {
  // Shared client-side observations
  const {
    observations,
    loading,
    error,
  } = useObservations();

  // ========================================
  // PREPARE CHART DATA
  // ========================================

  const data: ChartPoint[] = observations.map((row) => ({
    date: row.date,
    close: row.close,
    alertType: row.alert_type,
    zscore: row.price_zscore,
  }));

  // ========================================
  // DETECT PRICE ANOMALY MARKERS
  // ========================================

  const priceAnomalies = data.filter(
    (row) =>
      row.alertType === "PRICE_ONLY" ||
      row.alertType === "COMBINED"
  );

  // ========================================
  // MONTHLY X-AXIS LABELS
  // ========================================

  const monthTicks = data
    .filter(
      (row, index) =>
        index === 0 ||
        row.date.slice(0, 7) !==
          data[index - 1].date.slice(0, 7)
    )
    .map((row) => row.date);

  // ========================================
  // LOADING AND ERROR STATES
  // ========================================

  if (loading || error) {
    return (
      <section className="rounded-[24px] bg-white p-5 md:p-7">
        <h2 className="text-lg font-semibold">
          Closing price
        </h2>

        <p
          className="mt-4 text-sm text-[#7B837E]"
          role={error ? "alert" : "status"}
        >
          {error ?? "Loading price data..."}
        </p>
      </section>
    );
  }

  // ========================================
  // MAIN UI
  // ========================================

  return (
    <section className="rounded-[24px] bg-white p-5 md:p-7">

      {/* HEADER */}
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold tracking-tight">
            Closing price
          </h2>

          <p className="mt-1 text-sm text-[#7B837E]">
            Historical movement and detected price anomalies
          </p>
        </div>

        <span className="rounded-full bg-[#F1F2F0] px-3 py-2 text-xs font-medium">
          BBCA_DEMO
        </span>
      </div>

      {/* PRICE CHART */}
      <div className="mt-7 h-[330px] w-full min-w-0 overflow-x-clip">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={data}
            margin={{
              top: 14,
              right: 12,
              left: 0,
              bottom: 4,
            }}
          >
            {/* GRID */}
            <CartesianGrid
              vertical={false}
              stroke="#E8EBE9"
              strokeDasharray="3 5"
            />

            {/* X AXIS */}
            <XAxis
              dataKey="date"
              ticks={monthTicks}
              tickFormatter={formatMonth}
              tickLine={false}
              axisLine={false}
              minTickGap={30}
              tick={{
                fill: "#7B837E",
                fontSize: 11,
              }}
              tickMargin={12}
            />

            {/* Y AXIS */}
            <YAxis
              domain={[
                "dataMin - 150",
                "dataMax + 150",
              ]}
              tickLine={false}
              axisLine={false}
              width={58}
              tick={{
                fill: "#7B837E",
                fontSize: 11,
              }}
              tickFormatter={(value: number) =>
                value.toLocaleString("en-US", {
                  maximumFractionDigits: 0,
                })
              }
            />

            {/* TOOLTIP */}
            <Tooltip
              cursor={{
                stroke: "#B7C6BC",
                strokeDasharray: "4 4",
              }}
              contentStyle={{
                background: "#FFFFFF",
                border: "1px solid #E8EBE9",
                borderRadius: 12,
              }}
              labelFormatter={(label) =>
                String(label)
              }
              formatter={(value) => [
                Number(value).toLocaleString("en-US", {
                  maximumFractionDigits: 2,
                }),
                "Closing price",
              ]}
            />

            {/* CLOSING PRICE LINE */}
            <Line
              type="linear"
              dataKey="close"
              name="Close"
              stroke="#11835D"
              strokeWidth={2.5}
              dot={false}
              activeDot={{ r: 4 }}
              isAnimationActive={false}
            />

            {/* PRICE ANOMALY MARKERS */}
            {priceAnomalies.map((point) => (
              <ReferenceDot
                key={point.date}
                x={point.date}
                y={point.close}
                r={6}
                fill={
                  point.alertType === "COMBINED"
                    ? "#DC2626"
                    : "#D97706"
                }
                stroke="#FFFFFF"
                strokeWidth={2}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* LEGEND */}
      <div className="mt-4 flex flex-wrap items-center gap-x-6 gap-y-2 border-t border-[#ECEEEC] pt-4 text-xs text-[#65716A]">

        <span className="flex items-center gap-2">
          <span className="h-[3px] w-5 rounded bg-[#11835D]" />
          Closing price
        </span>

        <span className="flex items-center gap-2">
          <span className="h-2.5 w-2.5 rounded-full bg-[#D97706]" />
          Price anomaly
        </span>

        <span className="flex items-center gap-2">
          <span className="h-2.5 w-2.5 rounded-full bg-[#DC2626]" />
          Combined anomaly
        </span>
      </div>

      {/* FOOTNOTE */}
      <p className="mt-4 text-xs text-[#8B938E]">
        Synthetic closing prices. Anomaly markers are based on
        the existing Python detection results.
      </p>
    </section>
  );
}
