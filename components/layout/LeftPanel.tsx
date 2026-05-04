"use client";

// Left "actions" panel. Picks its content from the URL, not local state.
// Each route's quick actions live in one branch of the switch — easy to
// move into per-route files later if any branch grows.

import { useRouter, usePathname } from "next/navigation";
import { useDemoStore } from "@/lib/demo-store";
import type { Screen } from "@/lib/types";

const PANEL_TITLES: Record<Screen, [string, string]> = {
  home: ["Quick actions", "Pick a role"],
  organiser: ["Organiser actions", "Build your listing"],
  sponsor: ["Sponsor actions", "Filter + offer"],
  deal: ["Deal actions", "Confirm the bag"],
  admin: ["Admin actions", "Keep it clean"],
};

function screenFromPath(pathname: string): Screen {
  if (pathname.startsWith("/organiser")) return "organiser";
  if (pathname.startsWith("/sponsor")) return "sponsor";
  if (pathname.startsWith("/deal")) return "deal";
  if (pathname.startsWith("/admin")) return "admin";
  return "home";
}

export function LeftPanel() {
  const pathname = usePathname();
  const router = useRouter();
  const screen = screenFromPath(pathname);
  const [title, sub] = PANEL_TITLES[screen];
  const store = useDemoStore();

  return (
    <div className="panel">
      <div className="panelHeader">
        <h2>{title}</h2>
        <small>{sub}</small>
      </div>
      <div className="panelBody">
        {screen === "home" && <HomeActions />}
        {screen === "organiser" && <OrganiserActions />}
        {screen === "sponsor" && <SponsorActions />}
        {screen === "deal" && <DealActions />}
        {screen === "admin" && <AdminActions />}
      </div>
    </div>
  );

  function HomeActions() {
    return (
      <>
        <div className="kpiRow">
          <div className="kpi">
            <div className="label">Events live</div>
            <div className="val">6</div>
          </div>
          <div className="kpi">
            <div className="label">Sponsor leads</div>
            <div className="val">{store.inbox.length}</div>
          </div>
        </div>
        <div className="hint">
          This is a <b>clickable wireframe</b> (no backend). You&apos;re testing the
          flow: organiser lists an event, sponsor sends offer, organiser accepts.
        </div>
        <div className="btnRow">
          <button className="primary" onClick={() => router.push("/organiser")}>
            + Create event
          </button>
          <button className="good" onClick={() => router.push("/sponsor")}>
            Browse events
          </button>
          <button className="warn" onClick={() => router.push("/deal")}>
            Make offer
          </button>
        </div>
        <div className="divider"></div>
        <div className="tiny">
          Tip: use the top pills to jump screens. Everything is fake data but
          feels real.
        </div>
      </>
    );
  }

  function OrganiserActions() {
    return (
      <>
        <div className="kpiRow">
          <div className="kpi" style={{ minWidth: "100%" }}>
            <div className="label">Current Event</div>
            <div className="val" style={{ fontSize: "14px" }}>
              {store.event.name}
            </div>
            <div className="hint" style={{ marginTop: "4px" }}>
              {store.event.city} • {store.event.packages.join(", ")}
            </div>
          </div>
        </div>
        <div className="divider"></div>
        <div className="btnRow" style={{ flexDirection: "column" }}>
          <button
            className="btn primary"
            style={{ width: "100%" }}
            onClick={() => router.push("/sponsor")}
          >
            Preview as Sponsor
          </button>
          <button className="btn bad" style={{ width: "100%" }}>
            Reset demo
          </button>
        </div>
      </>
    );
  }

  function SponsorActions() {
    return (
      <>
        <div className="kpiRow">
          <div className="kpi" style={{ minWidth: "100%" }}>
            <div className="label">Current Brand</div>
            <div className="val" style={{ fontSize: "14px" }}>
              {store.brand.name}
            </div>
            <div className="hint" style={{ marginTop: "4px" }}>
              {store.brand.budget} • {store.brand.industry}
            </div>
          </div>
        </div>
        <div className="divider"></div>
        <div className="btnRow" style={{ flexDirection: "column" }}>
          <button
            className="btn primary"
            style={{ width: "100%" }}
            onClick={() => router.push("/deal")}
          >
            Go to Deal view
          </button>
        </div>
      </>
    );
  }

  function DealActions() {
    const { deal, setDeal, showToast } = store;
    const tone =
      deal.status === "ACCEPTED"
        ? { background: "rgba(57,217,138,.16)", borderColor: "rgba(57,217,138,.35)" }
        : deal.status === "DECLINED"
          ? { background: "rgba(255,92,122,.14)", borderColor: "rgba(255,92,122,.35)" }
          : { background: "rgba(255,204,102,.14)", borderColor: "rgba(255,204,102,.35)" };

    return (
      <>
        <div className="kpiRow">
          <div className="kpi" style={{ minWidth: "100%" }}>
            <div className="label">Deal Status</div>
            <div className="val" style={{ fontSize: "14px" }}>
              <span className="tag" style={tone}>
                {deal.status}
              </span>
            </div>
          </div>
        </div>
        <div className="divider"></div>
        <div className="btnRow" style={{ flexDirection: "column" }}>
          <button
            className="btn good"
            style={{ width: "100%" }}
            onClick={() => {
              setDeal({ ...deal, status: "ACCEPTED" });
              showToast("Accepted", "Deal confirmed (demo).");
            }}
          >
            ✅ Accept deal
          </button>
          <button
            className="btn warn"
            style={{ width: "100%" }}
            onClick={() => {
              setDeal({ ...deal, status: "PENDING" });
              showToast("Pending", "Deal set to pending.");
            }}
          >
            ⏳ Set pending
          </button>
          <button
            className="btn bad"
            style={{ width: "100%" }}
            onClick={() => {
              setDeal({ ...deal, status: "DECLINED" });
              showToast("Declined", "Deal declined.");
            }}
          >
            ❌ Decline
          </button>
        </div>
        <div className="divider"></div>
        <button
          className="btn"
          style={{ width: "100%" }}
          onClick={() => router.push("/admin")}
        >
          View in Admin
        </button>
      </>
    );
  }

  function AdminActions() {
    const { approvals, setApprovals, showToast } = store;
    const pending = approvals.filter((a) => a.status === "PENDING").length;
    const approved = approvals.filter((a) => a.status === "APPROVED").length;

    return (
      <>
        <div className="kpiRow">
          <div className="kpi">
            <div className="label">Pending</div>
            <div className="val">{pending}</div>
          </div>
          <div className="kpi">
            <div className="label">Approved</div>
            <div className="val">{approved}</div>
          </div>
        </div>
        <div className="divider"></div>
        <div className="btnRow" style={{ flexDirection: "column" }}>
          <button
            className="btn good"
            style={{ width: "100%" }}
            onClick={() => {
              setApprovals(approvals.map((a) => ({ ...a, status: "APPROVED" })));
              showToast("Approved", "All approvals cleared.");
            }}
          >
            ✅ Approve all
          </button>
          <button
            className="btn bad"
            style={{ width: "100%" }}
            onClick={() => showToast("Flagged", "Spam flagged (demo).")}
          >
            🚩 Flag spam
          </button>
        </div>
      </>
    );
  }
}
