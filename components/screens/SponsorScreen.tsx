"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useDemoStore } from "@/lib/demo-store";
import {
  AUDIENCE_SIZES,
  BUDGET_RANGES,
  EVENT_TYPES,
  PKG_DETAILS,
} from "@/lib/constants";
import { buildCatalogue } from "@/lib/catalogue";

export function SponsorScreen() {
  const router = useRouter();
  const {
    event,
    brand,
    setBrand,
    offers,
    setOffers,
    selectedPackage,
    showToast,
  } = useDemoStore();

  const [filterCity, setFilterCity] = useState("");
  const [filterType, setFilterType] = useState("");
  const [filterSize, setFilterSize] = useState("");
  const [showBrand, setShowBrand] = useState(false);
  const [showOffers, setShowOffers] = useState(false);

  const catalogue = buildCatalogue(event).filter((e) => {
    if (filterCity && !e.city.toLowerCase().includes(filterCity.toLowerCase()))
      return false;
    if (filterType && e.type !== filterType) return false;
    if (filterSize && e.size !== filterSize) return false;
    return true;
  });

  return (
    <section className="screen active">
      <div className="rightHeader">
        <div>
          <div className="cardTitle">Browse events</div>
          <div className="meta">Find the right crowd fast.</div>
        </div>
        <div className="btnRow">
          <button className="btn" onClick={() => setShowBrand((v) => !v)}>
            Brand profile
          </button>
          <button
            className="btn warn"
            onClick={() => setShowOffers((v) => !v)}
          >
            My offers ({offers.length})
          </button>
        </div>
      </div>

      <div className="card">
        <div className="searchbar">
          <input
            placeholder="Filter by city"
            value={filterCity}
            onChange={(e) => setFilterCity(e.target.value)}
          />
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
          >
            <option value="">All types</option>
            {EVENT_TYPES.map((t) => (
              <option key={t}>{t}</option>
            ))}
          </select>
          <select
            value={filterSize}
            onChange={(e) => setFilterSize(e.target.value)}
          >
            <option value="">Any size</option>
            {AUDIENCE_SIZES.map((s) => (
              <option key={s}>{s}</option>
            ))}
          </select>
          <button
            className="primary"
            onClick={() => showToast("Filtered", "Showing matches.")}
          >
            Apply
          </button>
        </div>
      </div>

      <div className="list" style={{ marginTop: 12 }}>
        {catalogue.map((e) => (
          <div className="card" key={e.id}>
            <div className="cardTop">
              <div>
                <div className="cardTitle">{e.name}</div>
                <div className="meta">
                  {e.city} • {e.type} • Audience {e.size} • Date: {e.date}
                </div>
              </div>
              <button className="btn primary" onClick={() => router.push("/deal")}>
                View
              </button>
            </div>
            <div className="meta" style={{ marginTop: 10 }}>
              {e.pitch}
            </div>
            <div className="pillRow">
              <span className="pill">Packages: {e.packages.join(", ")}</span>
            </div>
            <div className="btnRow" style={{ marginTop: 10 }}>
              <button
                className="btn warn"
                onClick={() => {
                  const amount = PKG_DETAILS[selectedPackage].price;
                  setOffers([
                    {
                      id: `off_${crypto.randomUUID().slice(0, 8)}`,
                      event: e.name,
                      sponsor: brand.name,
                      package: selectedPackage,
                      amount,
                      status: "SENT",
                    },
                    ...offers,
                  ]);
                  showToast(
                    "Offer sent",
                    `Sent ${selectedPackage} offer for £${amount}.`,
                  );
                  setShowOffers(true);
                }}
              >
                Send offer ({selectedPackage})
              </button>
            </div>
          </div>
        ))}
      </div>

      {showBrand && (
        <div className="card" style={{ marginTop: 12 }}>
          <div className="cardTop">
            <div>
              <div className="cardTitle">Brand profile</div>
              <div className="meta">Just enough info to match you correctly.</div>
            </div>
          </div>
          <div className="split" style={{ marginTop: 10 }}>
            <div className="field">
              <label>Brand name</label>
              <input
                value={brand.name}
                onChange={(e) => setBrand({ ...brand, name: e.target.value })}
              />
            </div>
            <div className="field">
              <label>Budget range</label>
              <select
                value={brand.budget}
                onChange={(e) => setBrand({ ...brand, budget: e.target.value })}
              >
                {BUDGET_RANGES.map((b) => (
                  <option key={b}>{b}</option>
                ))}
              </select>
            </div>
          </div>
          <div className="field">
            <label>Industry</label>
            <input
              value={brand.industry}
              onChange={(e) =>
                setBrand({ ...brand, industry: e.target.value })
              }
            />
          </div>
          <div className="btnRow">
            <button
              className="good"
              onClick={() => showToast("Saved", "Brand updated.")}
            >
              Save
            </button>
            <button className="btn" onClick={() => setShowBrand(false)}>
              Close
            </button>
          </div>
        </div>
      )}

      {showOffers && (
        <div className="card" style={{ marginTop: 12 }}>
          <div className="cardTop">
            <div>
              <div className="cardTitle">My offers</div>
              <div className="meta">Offers you&apos;ve sent.</div>
            </div>
          </div>
          <div className="list" style={{ marginTop: 10 }}>
            {offers.map((o) => (
              <div className="card" key={o.id}>
                <div className="cardTop">
                  <div>
                    <div className="cardTitle">{o.event}</div>
                    <div className="meta">
                      Sponsor: {o.sponsor} • Package: {o.package} • £{o.amount}{" "}
                      • Status: {o.status}
                    </div>
                  </div>
                  <button className="btn" onClick={() => router.push("/deal")}>
                    View
                  </button>
                </div>
              </div>
            ))}
          </div>
          <div className="btnRow">
            <button className="btn" onClick={() => setShowOffers(false)}>
              Close
            </button>
          </div>
        </div>
      )}
    </section>
  );
}
