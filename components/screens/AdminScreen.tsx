"use client";

import { useRouter } from "next/navigation";
import { useDemoStore } from "@/lib/demo-store";

export function AdminScreen() {
  const router = useRouter();
  const {
    approvals,
    setApprovals,
    showToast,
    event,
    brand,
    selectedPackage,
    deal,
  } = useDemoStore();

  return (
    <section className="screen active">
      <div className="split">
        <div className="card">
          <div className="cardTop">
            <div>
              <div className="cardTitle">Pending approvals</div>
              <div className="meta">Events / Sponsors waiting for review.</div>
            </div>
          </div>
          <div className="list" style={{ marginTop: 10 }}>
            {approvals.map((a) => (
              <div className="card" key={a.id}>
                <div className="cardTop">
                  <div>
                    <div className="cardTitle">
                      {a.type}: {a.name}
                    </div>
                    <div className="meta">{a.status}</div>
                  </div>
                  {a.status === "PENDING" ? (
                    <button
                      className="btn primary"
                      onClick={() => {
                        setApprovals(
                          approvals.map((app) =>
                            app.id === a.id
                              ? { ...app, status: "APPROVED" }
                              : app,
                          ),
                        );
                        showToast("Approved", `${a.type} approved.`);
                      }}
                    >
                      Approve
                    </button>
                  ) : (
                    <div
                      className="tag"
                      style={{
                        background: "rgba(57,217,138,.16)",
                        borderColor: "rgba(57,217,138,.35)",
                      }}
                    >
                      ✓
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
        <div className="card">
          <div className="cardTop">
            <div>
              <div className="cardTitle">Deals activity</div>
              <div className="meta">Pipeline view.</div>
            </div>
          </div>
          <div className="list" style={{ marginTop: 10 }}>
            <div className="card">
              <div className="cardTop">
                <div>
                  <div className="cardTitle">
                    {event.name} x {brand.name}
                  </div>
                  <div className="meta">
                    Package: {selectedPackage} • Status: {deal.status}
                  </div>
                </div>
                <button
                  className="btn"
                  onClick={() => router.push("/deal")}
                >
                  Open
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
