
"use client";

import { useEffect, useState } from "react";

export type ApiObservation = {
  date: string;
  symbol: string;
  close: number;
  volume: number;
  price_zscore: number | null;
  volume_ratio: number | null;
  alert_type:
    | "NORMAL"
    | "PRICE_ONLY"
    | "VOLUME_ONLY"
    | "COMBINED";
  evaluable: boolean;
};

type ObservationsResponse = {
  dataset: string;
  count: number;
  observations: ApiObservation[];
};

// Share one request between components that
// request observations at the same time.
let inFlightRequest: Promise<ApiObservation[]> | null = null;

function fetchObservations(): Promise<ApiObservation[]> {
  if (inFlightRequest) {
    return inFlightRequest;
  }

  inFlightRequest = (async () => {
    const response = await fetch("/api/observations", {
      cache: "no-store",
    });

    if (!response.ok) {
      throw new Error(
        `API returned HTTP ${response.status}`
      );
    }

    const payload =
      (await response.json()) as ObservationsResponse;

    if (
      !Array.isArray(payload.observations) ||
      typeof payload.count !== "number" ||
      payload.count !== payload.observations.length
    ) {
      throw new Error("Invalid observations response");
    }

    return payload.observations;
  })().finally(() => {
    inFlightRequest = null;
  });

  return inFlightRequest;
}

export function useObservations() {
  const [observations, setObservations] =
    useState<ApiObservation[]>([]);

  const [loading, setLoading] = useState(true);

  const [error, setError] =
    useState<string | null>(null);

  useEffect(() => {
    let active = true;

    void fetchObservations()
      .then((records) => {
        if (!active) return;

        setObservations(records);
        setError(null);
      })
      .catch(() => {
        if (!active) return;

        setError(
          "Unable to load observations from the API."
        );
      })
      .finally(() => {
        if (active) {
          setLoading(false);
        }
      });

    return () => {
      active = false;
    };
  }, []);

  return {
    observations,
    loading,
    error,
  };
}
