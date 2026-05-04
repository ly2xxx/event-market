"use client";

// Renders the floating toast. Subscribes to the demo store, so any
// component can fire showToast() without prop-drilling.

import { useDemoStore } from "@/lib/demo-store";

export function ToastHost() {
  const { toast } = useDemoStore();
  if (!toast) return null;
  return (
    <div className="toast show" role="status">
      <b>{toast.title}</b>
      <span>{toast.msg}</span>
    </div>
  );
}
