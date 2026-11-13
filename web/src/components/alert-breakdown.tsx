
import { getObservations } from "@/lib/server-observations";

const categories = [
  {
    key: "PRICE_ONLY",
    label: "Price only",
    color: "#D97706",
  },
  {
    key: "VOLUME_ONLY",
    label: "Volume only",
    color: "#11835D",
  },
  {
    key: "COMBINED",
    label: "Combined",
    color: "#DC2626",
  },
] as const;

export default async function AlertBreakdown() {
  let data: Awaited<ReturnType<typeof getObservations>>;

  try {
    data = await getObservations();
  } catch {
    return (
      <section
        role="alert"
        className="rounded-[24px] bg-white p-5 text-sm text-[#9A650B] md:p-7"
      >
        Alert breakdown is unavailable.
        Check the FastAPI backend.
      </section>
    );
  }

  const counts = categories.map((category) => ({
    ...category,
    count: data.observations.filter(
      (row) => row.alert_type === category.key
    ).length,
  }));

  const totalAlerts = counts.reduce(
    (sum, category) => sum + category.count,
    0
  );

  const evaluableCount = data.observations.filter(
    (row) => row.evaluable === true
  ).length;

  return (
    <section className="flex h-full flex-col rounded-[24px] bg-white p-5 md:p-7">
      {/* HEADER */}
      <div>
        <h2 className="text-lg font-semibold tracking-tight">
          Alert breakdown
        </h2>

        <p className="mt-1 text-sm text-[#7B837E]">
          Distribution by detection category
        </p>
      </div>

      {/* TOTAL ALERTS */}
      <div className="mt-9">
        <p className="text-xs text-[#7B837E]">
          Unique flagged observations
        </p>

        <p className="mt-2 text-5xl font-semibold tracking-tight tabular-nums">
          {totalAlerts}
        </p>
      </div>

      {/* ALERT CATEGORIES */}
      <div className="mt-8 divide-y divide-[#ECEEEC]">
        {counts.map((category) => (
          <div
            key={category.key}
            className="flex items-center justify-between py-4"
          >
            <div className="flex items-center gap-3">
              <span
                className="h-2.5 w-2.5 rounded-full"
                style={{
                  backgroundColor: category.color,
                }}
              />

              <span className="text-sm text-[#65716A]">
                {category.label}
              </span>
            </div>

            <span className="text-lg font-semibold tabular-nums">
              {category.count}
            </span>
          </div>
        ))}
      </div>

      {/* DETECTION COVERAGE */}
      <div className="mt-auto border-t border-[#ECEEEC] pt-5">
        <p className="text-xs font-medium text-[#18221E]">
          Detection coverage
        </p>

        <p className="mt-2 text-sm text-[#65716A]">
          <span className="font-semibold tabular-nums text-[#18221E]">
            {evaluableCount}
          </span>
          {" / "}
          {data.count} observations with complete baselines
        </p>

        <p className="mt-3 text-xs leading-5 text-[#8B938E]">
          Price threshold: |Z| ≥ 3
          <br />
          Volume threshold: ratio ≥ 3×
        </p>
      </div>
    </section>
  );
}
