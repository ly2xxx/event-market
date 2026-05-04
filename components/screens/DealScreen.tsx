"use client";

import { useDemoStore } from "@/lib/demo-store";
import { PKG_DETAILS } from "@/lib/constants";
import type { DealStatus } from "@/lib/types";

const STATUS_TONE: Record<DealStatus, { background: string; borderColor: string }> = {
  ACCEPTED: {
    background: "rgba(57,217,138,.16)",
    borderColor: "rgba(57,217,138,.35)",
  },
  DECLINED: {
    background: "rgba(255,92,122,.14)",
    borderColor: "rgba(255,92,122,.35)",
  },
  PENDING: {
    background: "rgba(255,204,102,.14)",
    borderColor: "rgba(255,204,102,.35)",
  },
};

export function DealScreen() {
  const { event, brand, selectedPackage, deal, setDeal, showToast } = useDemoStore();

  return (
    <section className="screen active">
      <div className="card">
        <div className="cardTop">
          <div>
            <div className="cardTitle">
              {event.name} x {brand.name}
            </div>
            <div className="meta">
              Package: {selectedPackage} - £{PKG_DETAILS[selectedPackage].price} •
              City: {event.city}
            </div>
          </div>
          <div className="tag" style={STATUS_TONE[deal.status]}>
            {deal.status}
          </div>
        </div>
        <div className="divider"></div>
        <div className="split">
          <div className="card">
            <div className="cardTitle">What sponsor gets</div>
            <div className="meta">{PKG_DETAILS[selectedPackage].benefits}</div>
          </div>
          <div className="card">
            <div className="cardTitle">What organiser needs</div>
            <div className="meta">Payment confirmed + deliverables agreed.</div>
          </div>
        </div>
        <div className="divider"></div>
        <div className="field">
          <label>Notes (shared)</label>
          <textarea
            value={deal.notes}
            onChange={(e) => setDeal({ ...deal, notes: e.target.value })}
            placeholder="Add logistics..."
          ></textarea>
        </div>
        <div className="btnRow">
          <button
            className="primary"
            onClick={() => showToast("Saved", "Deal notes updated.")}
          >
            Save notes
          </button>
        </div>
      </div>
    </section>
  );
}
