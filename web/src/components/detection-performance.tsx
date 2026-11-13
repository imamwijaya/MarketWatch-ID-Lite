
"use client";

import { useEffect, useState } from "react";

// ========================================
// TYPES
// ========================================

type ConfusionMatrix = {
  tp: number;
  fp: number;
  fn: number;
  tn: number;
};

type EvaluationResponse = {
  observations: number;
  evaluable_observations: number;
  injected_anomalies: number;
  predicted_alerts: number;
  precision: number;
  recall: number;
  f1_score: number;
  correct_types: number;
  total_labeled: number;
  confusion_matrix: ConfusionMatrix;
};

// ========================================
// HELPERS
// ========================================

function formatPercent(value: number) {
  return `${(value * 100).toFixed(2)}%`;
}

function isValidEvaluation(
  data: EvaluationResponse
): boolean {
  if (!data || typeof data !== "object") {
    return false;
  }

  const numericFields = [
    data.observations,
    data.evaluable_observations,
    data.injected_anomalies,
    data.predicted_alerts,
    data.precision,
    data.recall,
    data.f1_score,
    data.correct_types,
    data.total_labeled,
  ];

  if (!numericFields.every(
    (value) =>
      typeof value === "number" &&
      Number.isFinite(value)
  )) {
    return false;
  }

  const matrix = data.confusion_matrix;

  if (!matrix || typeof matrix !== "object") {
    return false;
  }

  return [
    matrix.tp,
    matrix.fp,
    matrix.fn,
    matrix.tn,
  ].every(
    (value) =>
      typeof value === "number" &&
      Number.isFinite(value)
  );
}

// ========================================
// COMPONENT
// ========================================

export default function DetectionPerformance() {
  const [evaluation, setEvaluation] =
    useState<EvaluationResponse | null>(null);

  const [loading, setLoading] = useState(true);

  const [error, setError] =
    useState<string | null>(null);

  // ========================================
  // FETCH EVALUATION FROM API
  // ========================================

  useEffect(() => {
    const controller = new AbortController();

    async function loadEvaluation() {
      try {
        const response = await fetch("/api/evaluation", {
          cache: "no-store",
          signal: controller.signal,
        });

        if (!response.ok) {
          throw new Error(
            `API returned HTTP ${response.status}`
          );
        }

        const payload =
          (await response.json()) as EvaluationResponse;

        if (!isValidEvaluation(payload)) {
          throw new Error("Invalid evaluation response");
        }

        if (!controller.signal.aborted) {
          setEvaluation(payload);
          setError(null);
        }
      } catch {
        if (!controller.signal.aborted) {
          setError(
            "Unable to load detection performance."
          );
        }
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    }

    void loadEvaluation();

    return () => controller.abort();
  }, []);

  // ========================================
  // LOADING AND ERROR STATES
  // ========================================

  if (loading || error || !evaluation) {
    return (
      <section className="rounded-[24px] bg-white p-5 md:p-7">
        <h2 className="text-lg font-semibold tracking-tight">
          Detection performance
        </h2>

        <p
          className="mt-4 text-sm text-[#7B837E]"
          role={error ? "alert" : "status"}
        >
          {error ??
            (loading
              ? "Loading detection performance..."
              : "Evaluation data is unavailable.")}
        </p>
      </section>
    );
  }

  // ========================================
  // PERFORMANCE DATA
  // ========================================

  const metrics = [
    {
      label: "Precision",
      value: evaluation.precision,
      description:
        "Share of alerts matching synthetic labels",
    },
    {
      label: "Recall",
      value: evaluation.recall,
      description:
        "Share of injected anomalies detected",
    },
    {
      label: "F1-score",
      value: evaluation.f1_score,
      description:
        "Balance of precision and recall",
    },
  ];

  const { tp, fp, fn, tn } =
    evaluation.confusion_matrix;

  // ========================================
  // MAIN UI
  // ========================================

  return (
    <section className="rounded-[24px] bg-white p-5 md:p-7">
      {/* HEADER */}
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold tracking-tight">
            Detection performance
          </h2>

          <p className="mt-1 text-sm text-[#7B837E]">
            Evaluation against injected synthetic anomalies
          </p>
        </div>

        <span className="rounded-full bg-[#F1F2F0] px-3 py-2 text-xs font-medium">
          {evaluation.evaluable_observations} evaluable records
        </span>
      </div>

      {/* PERFORMANCE METRICS */}
      <div className="mt-7 grid grid-cols-1 gap-3 sm:grid-cols-3">
        {metrics.map((metric) => (
          <div
            key={metric.label}
            className="rounded-[16px] bg-[#F5F6F4] p-5"
          >
            <p className="text-sm text-[#65716A]">
              {metric.label}
            </p>

            <p className="mt-3 text-3xl font-semibold tracking-tight tabular-nums">
              {formatPercent(metric.value)}
            </p>

            <p className="mt-3 text-xs leading-5 text-[#8B938E]">
              {metric.description}
            </p>
          </div>
        ))}
      </div>

      {/* CONFUSION MATRIX */}
      <div className="mt-8 grid grid-cols-1 gap-8 lg:grid-cols-2">
        <div>
          <h3 className="text-sm font-semibold">
            Confusion matrix
          </h3>

          <p className="mt-1 text-xs leading-5 text-[#7B837E]">
            Binary evaluation: anomaly versus normal
          </p>

          <div className="mt-5 overflow-x-auto">
            <table className="w-full border-collapse text-sm">
              <thead>
                <tr className="text-xs text-[#7B837E]">
                  <th className="pb-3 text-left font-medium">
                    Actual / Predicted
                  </th>

                  <th className="pb-3 text-center font-medium">
                    Normal
                  </th>

                  <th className="pb-3 text-center font-medium">
                    Anomaly
                  </th>
                </tr>
              </thead>

              <tbody>
                <tr className="border-t border-[#ECEEEC]">
                  <th className="py-4 text-left text-xs font-medium text-[#65716A]">
                    Normal
                  </th>

                  <td className="py-4 text-center font-semibold tabular-nums">
                    {tn}
                  </td>

                  <td className="py-4 text-center font-semibold tabular-nums text-[#B87513]">
                    {fp}
                  </td>
                </tr>

                <tr className="border-t border-[#ECEEEC]">
                  <th className="py-4 text-left text-xs font-medium text-[#65716A]">
                    Anomaly
                  </th>

                  <td className="py-4 text-center font-semibold tabular-nums">
                    {fn}
                  </td>

                  <td className="py-4 text-center font-semibold tabular-nums text-[#11835D]">
                    {tp}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* EVALUATION CONTEXT */}
        <div className="border-t border-[#ECEEEC] pt-6 lg:border-l lg:border-t-0 lg:pl-8 lg:pt-0">
          <h3 className="text-sm font-semibold">
            Evaluation coverage
          </h3>

          <div className="mt-5 space-y-4">
            <div className="flex items-center justify-between gap-4">
              <span className="text-sm text-[#65716A]">
                Total observations
              </span>

              <span className="font-semibold tabular-nums">
                {evaluation.observations}
              </span>
            </div>

            <div className="flex items-center justify-between gap-4">
              <span className="text-sm text-[#65716A]">
                Evaluable observations
              </span>

              <span className="font-semibold tabular-nums">
                {evaluation.evaluable_observations}
              </span>
            </div>

            <div className="flex items-center justify-between gap-4">
              <span className="text-sm text-[#65716A]">
                Injected anomalies
              </span>

              <span className="font-semibold tabular-nums">
                {evaluation.injected_anomalies}
              </span>
            </div>

            <div className="flex items-center justify-between gap-4">
              <span className="text-sm text-[#65716A]">
                Correct anomaly categories
              </span>

              <span className="font-semibold tabular-nums">
                {evaluation.correct_types}/{evaluation.total_labeled}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* DISCLAIMER */}
      <p className="mt-8 border-t border-[#ECEEEC] pt-4 text-xs leading-5 text-[#8B938E]">
        Results are based on synthetic data and injected labels.
        They do not establish real-world market surveillance
        performance or indicate confirmed market manipulation.
      </p>
    </section>
  );
}
