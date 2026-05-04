"use client";

import { useRouter } from "next/navigation";

const PROTOTYPE_FEATURES = [
  "Create event",
  "Add packages",
  "Browse events + filters",
  "Send offer",
  "Accept deal",
  "Admin approve",
];

export function HomeScreen() {
  const router = useRouter();
  return (
    <section className="screen active">
      <div className="rightHeader">
        <div>
          <div className="tag">Goal</div>
          <div className="meta" style={{ marginTop: 8 }}>
            Match <b>events</b> with <b>sponsors</b> without IG DMs + WhatsApp
            chaos.
          </div>
        </div>
      </div>
      <div className="split" style={{ marginTop: 14 }}>
        <div className="card">
          <div className="cardTop">
            <div>
              <div className="cardTitle">I&apos;m an Organiser</div>
              <div className="meta">
                List your event + packages, receive sponsor offers, accept
                deals.
              </div>
            </div>
          </div>
          <div className="btnRow" style={{ marginTop: 12 }}>
            <button
              className="btn primary"
              onClick={() => router.push("/organiser")}
            >
              Go to Organiser
            </button>
          </div>
        </div>
        <div className="card">
          <div className="cardTop">
            <div>
              <div className="cardTitle">I&apos;m a Sponsor</div>
              <div className="meta">
                Filter events, view packages, send an offer in 30 seconds.
              </div>
            </div>
          </div>
          <div className="btnRow" style={{ marginTop: 12 }}>
            <button
              className="btn primary"
              onClick={() => router.push("/sponsor")}
            >
              Go to Sponsor
            </button>
          </div>
        </div>
      </div>
      <div className="divider"></div>
      <div className="card">
        <div className="cardTop">
          <div>
            <div className="cardTitle">What&apos;s inside this prototype</div>
            <div className="meta">Minimal, but end-to-end clickable.</div>
          </div>
        </div>
        <div className="pillRow">
          {PROTOTYPE_FEATURES.map((f) => (
            <span key={f} className="pill">
              {f}
            </span>
          ))}
        </div>
      </div>
    </section>
  );
}
