
import { getObservations } from "@/lib/server-observations";

export default async function MarketMetrics() {
  let data: Awaited<ReturnType<typeof getObservations>>;

  try {
    data = await getObservations();
  } catch {
    return (
      <section
        role="alert"
        className="rounded-[20px] bg-white p-6 text-sm text-[#9A650B]"
      >
        Market metrics are unavailable. Check the FastAPI backend.
      </section>
    );
  }

  const observations = data.observations;

  const metrics = [
    {
      label: "Observations",
      value: data.count,
    },
    {
      label: "Unique Alerts",
      value: observations.filter(
        (row) => row.alert_type !== "NORMAL"
      ).length,
    },
    {
      label: "Price Alerts",
      value: observations.filter(
        (row) =>
          row.alert_type === "PRICE_ONLY" ||
          row.alert_type === "COMBINED"
      ).length,
    },
    {
      label: "Volume Alerts",
      value: observations.filter(
        (row) =>
          row.alert_type === "VOLUME_ONLY" ||
          row.alert_type === "COMBINED"
      ).length,
    },
  ];

  return (
    <section
      aria-label="Market summary"
      className="grid grid-cols-2 gap-4 md:grid-cols-4"
    >
      {metrics.map((metric) => (
        <div
          key={metric.label}
          className="rounded-[20px] bg-white p-6"
        >
          <p className="text-sm text-[#7B837E]">
            {metric.label}
          </p>

          <p className="mt-4 text-4xl font-semibold tracking-tight tabular-nums">
            {metric.value}
          </p>
        </div>
      ))}
    </section>
  );
}
