"use client";

// Organiser route content. Three subsections are toggled with local state
// (showPackages, showInbox) — that's UI, not domain state, so it stays
// local rather than going into the demo store.

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useDemoStore } from "@/lib/demo-store";
import {
  AUDIENCE_SIZES,
  EVENT_TYPES,
  PKG_DETAILS,
} from "@/lib/constants";
import type { EventPkg } from "@/lib/types";

export function OrganiserScreen() {
  const router = useRouter();
  const {
    event,
    setEvent,
    inbox,
    brand,
    setBrand,
    selectedPackage,
    setSelectedPackage,
    setDeal,
    showToast,
  } = useDemoStore();

  const [showPackages, setShowPackages] = useState(false);
  const [showInbox, setShowInbox] = useState(false);

  return (
    <section className="screen active">
      <div className="rightHeader">
        <div>
          <div className="cardTitle">Create / manage an event</div>
          <div className="meta">Fill the basics. Save. Add packages. Done.</div>
        </div>
      </div>

      <div className="card">
        <div className="split">
          <div className="field">
            <label>Event name</label>
            <input
              value={event.name}
              onChange={(e) => setEvent({ ...event, name: e.target.value })}
              placeholder="e.g., Afro Vibes Night"
            />
          </div>
          <div className="field">
            <label>City</label>
            <input
              value={event.city}
              onChange={(e) => setEvent({ ...event, city: e.target.value })}
              placeholder="e.g., Glasgow"
            />
          </div>
        </div>
        <div className="split">
          <div className="field">
            <label>Date</label>
            <input
              type="date"
              value={event.date}
              onChange={(e) => setEvent({ ...event, date: e.target.value })}
            />
          </div>
          <div className="field">
            <label>Audience size</label>
            <select
              value={event.size}
              onChange={(e) => setEvent({ ...event, size: e.target.value })}
            >
              {AUDIENCE_SIZES.map((s) => (
                <option key={s}>{s}</option>
              ))}
            </select>
          </div>
        </div>
        <div className="field">
          <label>Vibe / type</label>
          <select
            value={event.type}
            onChange={(e) => setEvent({ ...event, type: e.target.value })}
          >
            {EVENT_TYPES.map((t) => (
              <option key={t}>{t}</option>
            ))}
          </select>
        </div>
        <div className="field">
          <label>Quick pitch</label>
          <textarea
            value={event.pitch}
            onChange={(e) => setEvent({ ...event, pitch: e.target.value })}
            placeholder="Why should a sponsor care?"
          ></textarea>
        </div>
        <div className="btnRow">
          <button
            className="primary"
            onClick={() => showToast("Saved", "Event listing updated.")}
          >
            Save event
          </button>
          <button className="good" onClick={() => setShowPackages(true)}>
            Add packages
          </button>
          <button
            className="btn"
            onClick={() => setShowInbox((v) => !v)}
            style={{ marginLeft: "auto" }}
          >
            {showInbox ? "Hide inbox" : `Inbox (${inbox.length})`}
          </button>
        </div>
      </div>

      {showPackages && (
        <div className="card" style={{ marginTop: 12 }}>
          <div className="cardTop">
            <div>
              <div className="cardTitle">Sponsorship packages</div>
              <div className="meta">Give sponsors clear tiers.</div>
            </div>
          </div>
          <div className="split" style={{ marginTop: 10 }}>
            {(Object.entries(PKG_DETAILS) as [EventPkg, typeof PKG_DETAILS["Bronze"]][]).map(
              ([pkg, details]) => (
                <div className="card" key={pkg}>
                  <div className="cardTitle">
                    {pkg} {pkg !== "Custom" && `- £${details.price}`}
                  </div>
                  <div className="meta">{details.benefits}</div>
                  {pkg === "Custom" && (
                    <div className="field" style={{ marginTop: 10 }}>
                      <label>Custom package text</label>
                      <input placeholder="e.g., Drinks partnership" />
                    </div>
                  )}
                  <div className="btnRow">
                    <button
                      className="btn good"
                      onClick={() => {
                        setSelectedPackage(pkg);
                        if (!event.packages.includes(pkg)) {
                          setEvent({
                            ...event,
                            packages: [...event.packages, pkg],
                          });
                        }
                        showToast("Selected", `Package set to ${pkg}.`);
                      }}
                    >
                      Use
                    </button>
                  </div>
                </div>
              ),
            )}
          </div>
        </div>
      )}

      {showInbox && (
        <div className="card" style={{ marginTop: 12 }}>
          <div className="cardTop">
            <div>
              <div className="cardTitle">Inbox</div>
              <div className="meta">Sponsor enquiries land here.</div>
            </div>
          </div>
          <div className="list" style={{ marginTop: 10 }}>
            {inbox.map((m) => (
              <div className="card" key={m.id}>
                <div className="cardTop">
                  <div>
                    <div className="cardTitle">{m.from}</div>
                    <div className="meta">
                      About: {m.about} • Package: {m.package} • Offer: £
                      {m.amount}
                    </div>
                  </div>
                  <button
                    className="btn primary"
                    onClick={() => {
                      setBrand({ ...brand, name: m.from });
                      setSelectedPackage(m.package);
                      setDeal({ status: "PENDING", notes: "" });
                      showToast("Deal opened", "Ready to accept / decline.");
                      router.push("/deal");
                    }}
                  >
                    Open deal
                  </button>
                </div>
                <div className="meta" style={{ marginTop: 10 }}>
                  {m.note}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
