
"use client";

import {
  useObservations,
  type ApiObservation,
} from "@/lib/use-observations";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
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
  volume: number;
  volumeRatio: number | null;
  alertType: ApiObservation["alert_type"];
};

// ========================================
// HELPERS
// ========================================

function formatMonth(date: string) {
  return new Date(`${date}T00:00:00`).toLocaleDateString(
    "en-US",
    { month: "short", year: "2-digit" }
  );
}

function getBarColor(
  alertType: ApiObservation["alert_type"]
) {
  if (alertType === "COMBINED") return "#DC2626";
  if (alertType === "VOLUME_ONLY") return "#D97706";
  return "#CADBD0";
}

// ========================================
// COMPONENT
// ========================================

export default function VolumeChart() {
  const { observations, loading, error } =
    useObservations();

  // Prepare chart data
  const data: ChartPoint[] = observations.map((row) => ({
    date: row.date,
    volume: row.volume,
    volumeRatio: row.volume_ratio,
    alertType: row.alert_type,
  }));

  // Monthly axis ticks
  const monthTicks = data
    .filter(
      (row, index) =>
        index === 0 ||
        row.date.slice(0, 7) !==
          data[index - 1].date.slice(0, 7)
    )
    .map((row) => row.date);

  // Loading and error states
  if (loading || error) {
    return (
      <section className="rounded-[24px] bg-white p-5 md:p-7">
        <h2 className="text-lg font-semibold">
          Trading volume
        </h2>

        <p
          className="mt-4 text-sm text-[#7B837E]"
          role={error ? "alert" : "status"}
        >
          {error ?? "Loading volume data..."}
        </p>
      </section>
    );
  }

  return (
    <section className="rounded-[24px] bg-white p-5 md:p-7">
      {/* HEADER */}
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold tracking-tight">
            Trading volume
          </h2>

          <p className="mt-1 text-sm text-[#7B837E]">
            Daily volume and detected unusual activity
          </p>
        </div>

        <span className="rounded-full bg-[#F1F2F0] px-3 py-2 text-xs font-medium">
          BBCA_DEMO
        </span>
      </div>

      {/* VOLUME CHART */}
      <div className="mt-7 h-[290px] w-full min-w-0 overflow-x-clip">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={data}
            margin={{
              top: 14,
              right: 12,
              left: 0,
              bottom: 4,
            }}
          >
            <CartesianGrid
              vertical={false}
              stroke="#E8EBE9"
              strokeDasharray="3 5"
            />

            <XAxis
              dataKey="date"
              ticks={monthTicks}
              tickFormatter={formatMonth}
              tickLine={false}
              axisLine={false}
              tick={{ fill: "#7B837E", fontSize: 11 }}
              tickMargin={12}
            />

            <YAxis
              tickLine={false}
              axisLine={false}
              width={58}
              tick={{ fill: "#7B837E", fontSize: 11 }}
              tickFormatter={(value: number) =>
                `${(value / 1_000_000).toFixed(0)}M`
              }
            />

            {/* TOOLTIP */}
            <Tooltip
              cursor={{ fill: "#F1F4F1" }}
              content={({ active, payload }) => {
                if (!active || !payload?.length) {
                  return null;
                }

                const point =
                  payload[0].payload as ChartPoint;

                return (
                  <div className="rounded-xl border border-[#E8EBE9] bg-white px-4 py-3 shadow-sm">
                    <p className="text-xs font-medium text-[#18221E]">
                      {point.date}
                    </p>

                    <p className="mt-2 text-sm text-[#18221E]">
                      Volume:{" "}
                      {point.volume.toLocaleString("en-US")}
                    </p>

                    {point.volumeRatio !== null && (
                      <p className="mt-1 text-xs text-[#69756D]">
                        Volume ratio:{" "}
                        {point.volumeRatio.toFixed(2)}×
                      </p>
                    )}

                    {point.alertType !== "NORMAL" && (
                      <p className="mt-2 text-xs font-medium text-[#A65D13]">
                        {point.alertType}
                      </p>
                    )}
                  </div>
                );
              }}
            />

            {/* VOLUME BARS */}
            <Bar
              dataKey="volume"
              maxBarSize={14}
              radius={[2, 2, 0, 0]}
              isAnimationActive={false}
            >
              {data.map((point) => (
                <Cell
                  key={point.date}
                  fill={getBarColor(point.alertType)}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* LEGEND */}
      <div className="mt-4 flex flex-wrap items-center gap-x-6 gap-y-2 border-t border-[#ECEEEC] pt-4 text-xs text-[#65716A]">
        <span className="flex items-center gap-2">
          <span className="h-2.5 w-2.5 rounded-sm bg-[#CADBD0]" />
          Regular volume
        </span>

        <span className="flex items-center gap-2">
          <span className="h-2.5 w-2.5 rounded-sm bg-[#D97706]" />
          Volume spike
        </span>

        <span className="flex items-center gap-2">
          <span className="h-2.5 w-2.5 rounded-sm bg-[#DC2626]" />
          Combined anomaly
        </span>
      </div>

      {/* FOOTNOTE */}
      <p className="mt-4 text-xs text-[#8B938E]">
        Synthetic daily volume. Spike threshold: 3× the
        median of the previous 20 observations.
      </p>
    </section>
  );
}
