// Server component (no "use client") — pure markup.

import type { ReactNode } from "react";

interface PanelHeaderProps {
  title: string;
  subtitle?: ReactNode;
}

export function PanelHeader({ title, subtitle = "MVP Flow" }: PanelHeaderProps) {
  return (
    <div className="panelHeader">
      <h2 style={{ textTransform: "capitalize" }}>{title}</h2>
      <small>{subtitle}</small>
    </div>
  );
}
