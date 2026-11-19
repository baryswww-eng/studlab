"use client";

import { useEffect, useState } from "react";
import { type Dashboard, getDashboard } from "@/services/me";

export type DashboardState =
  | { status: "loading" }
  | { status: "error" }
  | { status: "ready"; data: Dashboard };

export function useDashboard(): DashboardState {
  const [state, setState] = useState<DashboardState>({ status: "loading" });
  useEffect(() => {
    let cancelled = false;
    getDashboard()
      .then((data) => !cancelled && setState({ status: "ready", data }))
      .catch(() => !cancelled && setState({ status: "error" }));
    return () => {
      cancelled = true;
    };
  }, []);
  return state;
}
