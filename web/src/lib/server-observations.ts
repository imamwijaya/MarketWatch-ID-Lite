
import { cache } from "react";

export type AlertType =
  | "NORMAL"
  | "PRICE_ONLY"
  | "VOLUME_ONLY"
  | "COMBINED";

export type Observation = {
  date: string;
  symbol: string;
  close: number;
  volume: number;
  price_zscore: number | null;
  volume_ratio: number | null;
  alert_type: AlertType;
  evaluable: boolean;
};

export type ObservationsResponse = {
  dataset: string;
  count: number;
  observations: Observation[];
};

export const getObservations = cache(
  async (): Promise<ObservationsResponse> => {
    const backendUrl =
      process.env.FASTAPI_URL ??
      "http://127.0.0.1:8000";

    const response = await fetch(
      `${backendUrl}/api/observations`,
      {
        cache: "no-store",
        signal: AbortSignal.timeout(10000),
      }
    );

    if (!response.ok) {
      throw new Error(
        `FastAPI returned HTTP ${response.status}`
      );
    }

    const data: unknown = await response.json();

    if (
      typeof data !== "object" ||
      data === null ||
      !("dataset" in data) ||
      typeof data.dataset !== "string" ||
      !("count" in data) ||
      typeof data.count !== "number" ||
      !("observations" in data) ||
      !Array.isArray(data.observations) ||
      data.count !== data.observations.length
    ) {
      throw new Error("Invalid observations response");
    }

    return data as ObservationsResponse;
  }
);
