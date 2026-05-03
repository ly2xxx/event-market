"use client";

import { useState, useEffect } from "react";

// --- Types ---
type EventPkg = "Bronze" | "Silver" | "Gold" | "Custom";
type DealStatus = "PENDING" | "ACCEPTED" | "DECLINED";
type ApprovalStatus = "PENDING" | "APPROVED";

interface Event {
  id?: string;
  name: string;
  city: string;
  date: string;
  size: string;
  type: string;
  pitch: string;
  packages: EventPkg[];
}

interface Brand {
  name: string;
  budget: string;
  industry: string;
}

interface Offer {
  id: string;
  event: string;
  sponsor: string;
  package: EventPkg;
  amount: number;
  status: string;
}

interface Message {
  id: string;
  from: string;
  about: string;
  package: EventPkg;
  amount: number;
  note: string;
}

interface Approval {
  id: string;
  type: "Event" | "Sponsor";
  name: string;
  status: ApprovalStatus;
}

// --- Constants ---
const PKG_DETAILS = {
  Bronze: { price: 250, benefits: "Logo on flyer • 1 IG story mention" },
  Silver: { price: 500, benefits: "Logo on flyer • MC shoutout • 1 post tag" },
  Gold: { price: 1000, benefits: "Booth • content bundle • headline mention" },
  Custom: { price: 750, benefits: "Custom deliverables (as agreed)" },
};

export default function App() {
  const [activeScreen, setActiveScreen] = useState("home");
  const [toast, setToast] = useState<{ title: string; msg: string } | null>(null);

  const [event, setEvent] = useState<Event>({
    name: "Afro Vibes Night",
    city: "Glasgow",
    date: "",
    size: "200-500",
    type: "Afrobeats",
    pitch: "High-energy Afro night. 70% students + young professionals. Heavy IG content.",
    packages: ["Bronze", "Silver", "Gold"],
  });

  const [brand, setBrand] = useState<Brand>({
    name: "Pulse Drinks",
    budget: "£300-£1,000",
    industry: "Beverage",
  });

  const [selectedPackage, setSelectedPackage] = useState<EventPkg>("Silver");

  const [offers, setOffers] = useState<Offer[]>([
    { id: "off_1", event: "Afro Vibes Night", sponsor: "Pulse Drinks", package: "Silver", amount: 500, status: "SENT" },
  ]);

  const [inbox, setInbox] = useState<Message[]>([
    { id: "msg_1", from: "Pulse Drinks", about: "Afro Vibes Night", package: "Silver", amount: 500, note: "We can sponsor + provide free cans for VIP." },
    { id: "msg_2", from: "Streetwear Co", about: "Afro Vibes Night", package: "Bronze", amount: 250, note: "Logo + giveaway collab?" },
  ]);

  const [deal, setDeal] = useState<{ status: DealStatus; notes: string }>({ status: "PENDING", notes: "" });

  const [approvals, setApprovals] = useState<Approval[]>([
    { id: "ap_1", type: "Event", name: "Afro Vibes Night", status: "PENDING" },
    { id: "ap_2", type: "Sponsor", name: "Pulse Drinks", status: "PENDING" },
  ]);

  // UI state toggles
  const [showPackages, setShowPackages] = useState(false);
  const [showInbox, setShowInbox] = useState(false);
  const [showBrand, setShowBrand] = useState(false);
  const [showOffers, setShowOffers] = useState(false);

  // Filters
  const [filterCity, setFilterCity] = useState("");
  const [filterType, setFilterType] = useState("");
  const [filterSize, setFilterSize] = useState("");

  const showToast = (title: string, msg: string) => {
    setToast({ title, msg });
    setTimeout(() => setToast(null), 2400);
  };

  const nav = (route: string) => {
    setActiveScreen(route);
  };

  // Render left panel based on active screen
  const renderLeftPanel = () => {
    const titles: Record<string, [string, string]> = {
      home: ["Quick actions", "Pick a role"],
      organiser: ["Organiser actions", "Build your listing"],
      sponsor: ["Sponsor actions", "Filter + offer"],
      deal: ["Deal actions", "Confirm the bag"],
      admin: ["Admin actions", "Keep it clean"],
    };
    const [title, sub] = titles[activeScreen] || titles.home;

    return (
      <div className="panel">
        <div className="panelHeader">
          <h2>{title}</h2>
          <small>{sub}</small>
        </div>
        <div className="panelBody">
          {activeScreen === "home" && (
            <>
              <div className="kpiRow">
                <div className="kpi">
                  <div className="label">Events live</div>
                  <div className="val">6</div>
                </div>
                <div className="kpi">
                  <div className="label">Sponsor leads</div>
                  <div className="val">{inbox.length}</div>
                </div>
              </div>
              <div className="hint">
                This is a <b>clickable wireframe</b> (no backend). You're testing the flow: organiser lists an event, sponsor sends offer, organiser accepts.
              </div>
              <div className="btnRow">
                <button className="primary" onClick={() => nav("organiser")}>+ Create event</button>
                <button className="good" onClick={() => nav("sponsor")}>Browse events</button>
                <button className="warn" onClick={() => nav("deal")}>Make offer</button>
              </div>
              <div className="divider"></div>
              <div className="tiny">Tip: use the top pills to jump screens. Everything is fake data but feels real.</div>
            </>
          )}

          {activeScreen === "organiser" && (
            <>
              <div className="kpiRow">
                 <div className="kpi" style={{minWidth:'100%'}}>
                    <div className="label">Current Event</div>
                    <div className="val" style={{fontSize: '14px'}}>{event.name}</div>
                    <div className="hint" style={{marginTop:'4px'}}>{event.city} • {event.packages.join(', ')}</div>
                 </div>
              </div>
              <div className="divider"></div>
              <div className="btnRow" style={{flexDirection: 'column'}}>
                <button className="btn" style={{width:'100%'}} onClick={() => setShowInbox(!showInbox)}>Inbox ({inbox.length})</button>
                <button className="btn primary" style={{width:'100%'}} onClick={() => nav("sponsor")}>Preview as Sponsor</button>
                <button className="btn bad" style={{width:'100%'}}>Reset demo</button>
              </div>
            </>
          )}

          {activeScreen === "sponsor" && (
            <>
              <div className="kpiRow">
                 <div className="kpi" style={{minWidth:'100%'}}>
                    <div className="label">Current Brand</div>
                    <div className="val" style={{fontSize: '14px'}}>{brand.name}</div>
                    <div className="hint" style={{marginTop:'4px'}}>{brand.budget} • {brand.industry}</div>
                 </div>
              </div>
              <div className="divider"></div>
              <div className="btnRow" style={{flexDirection: 'column'}}>
                <button className="btn" style={{width:'100%'}} onClick={() => setShowBrand(!showBrand)}>Brand profile</button>
                <button className="btn warn" style={{width:'100%'}} onClick={() => setShowOffers(!showOffers)}>My offers ({offers.length})</button>
                <button className="btn primary" style={{width:'100%'}} onClick={() => nav("deal")}>Go to Deal view</button>
              </div>
            </>
          )}

          {activeScreen === "deal" && (
            <>
              <div className="kpiRow">
                 <div className="kpi" style={{minWidth:'100%'}}>
                    <div className="label">Deal Status</div>
                    <div className="val" style={{fontSize: '14px'}}>
                      <span className="tag" style={{
                        background: deal.status === "ACCEPTED" ? "rgba(57,217,138,.16)" : deal.status === "DECLINED" ? "rgba(255,92,122,.14)" : "rgba(255,204,102,.14)",
                        borderColor: deal.status === "ACCEPTED" ? "rgba(57,217,138,.35)" : deal.status === "DECLINED" ? "rgba(255,92,122,.35)" : "rgba(255,204,102,.35)"
                      }}>{deal.status}</span>
                    </div>
                 </div>
              </div>
              <div className="divider"></div>
              <div className="btnRow" style={{flexDirection: 'column'}}>
                <button className="btn good" style={{width:'100%'}} onClick={() => { setDeal({ ...deal, status: "ACCEPTED" }); showToast("Accepted", "Deal confirmed (demo)."); }}>✅ Accept deal</button>
                <button className="btn warn" style={{width:'100%'}} onClick={() => { setDeal({ ...deal, status: "PENDING" }); showToast("Pending", "Deal set to pending."); }}>⏳ Set pending</button>
                <button className="btn bad" style={{width:'100%'}} onClick={() => { setDeal({ ...deal, status: "DECLINED" }); showToast("Declined", "Deal declined."); }}>❌ Decline</button>
              </div>
              <div className="divider"></div>
              <button className="btn" style={{width:'100%'}} onClick={() => nav("admin")}>View in Admin</button>
            </>
          )}

          {activeScreen === "admin" && (
            <>
              <div className="kpiRow">
                <div className="kpi">
                  <div className="label">Pending</div>
                  <div className="val">{approvals.filter(a => a.status === "PENDING").length}</div>
                </div>
                <div className="kpi">
                  <div className="label">Approved</div>
                  <div className="val">{approvals.filter(a => a.status === "APPROVED").length}</div>
                </div>
              </div>
              <div className="divider"></div>
              <div className="btnRow" style={{flexDirection: 'column'}}>
                <button className="btn good" style={{width:'100%'}} onClick={() => {
                  setApprovals(approvals.map(a => ({ ...a, status: "APPROVED" })));
                  showToast("Approved", "All approvals cleared.");
                }}>✅ Approve all</button>
                <button className="btn bad" style={{width:'100%'}} onClick={() => showToast("Flagged", "Spam flagged (demo).")}>🚩 Flag spam</button>
              </div>
            </>
          )}
        </div>
      </div>
    );
  };

  const getCatalogue = () => [
    { id: "e1", ...event, date: event.date || "TBA" },
    { id: "e2", name: "Amapiano Terrace", city: "Edinburgh", type: "Amapiano", size: "100-200", date: "TBA", pitch: "Sunset terrace vibe + content-heavy crowd.", packages: ["Bronze", "Silver", "Gold"] },
    { id: "e3", name: "Culture & Community Market", city: "Glasgow", type: "Culture / Community", size: "500-1000", date: "TBA", pitch: "Family friendly, diaspora brands, strong community presence.", packages: ["Bronze", "Silver"] },
    { id: "e4", name: "Corporate Afterhours", city: "London", type: "Corporate", size: "200-500", date: "TBA", pitch: "Young professionals, high spending power.", packages: ["Gold", "Silver"] },
  ];

  return (
    <div className="wrap">
      {/* Topbar */}
      <div className="topbar">
        <div className="brand">
          <div className="logo" aria-hidden="true"></div>
          <div className="title">
            <b>Event Sponsor Marketplace</b>
            <span>Next.js Port</span>
          </div>
        </div>
        <div className="nav">
          {["home", "organiser", "sponsor", "deal", "admin"].map(p => (
            <button
              key={p}
              className={`chip ${activeScreen === p ? "active" : ""}`}
              onClick={() => nav(p)}
            >
              {p.charAt(0).toUpperCase() + p.slice(1)}
            </button>
          ))}
        </div>
      </div>

      <div className="grid">
        {/* Left Action Panel */}
        {renderLeftPanel()}

        {/* Right Screens */}
        <div className="panel">
          <div className="panelHeader">
            <h2 style={{ textTransform: "capitalize" }}>{activeScreen}</h2>
            <small>MVP Flow</small>
          </div>
          <div className="panelBody">
            {/* HOME */}
            {activeScreen === "home" && (
              <section className="screen active">
                <div className="rightHeader">
                  <div>
                    <div className="tag">Goal</div>
                    <div className="meta" style={{ marginTop: 8 }}>Match <b>events</b> with <b>sponsors</b> without IG DMs + WhatsApp chaos.</div>
                  </div>
                </div>
                <div className="split" style={{ marginTop: 14 }}>
                  <div className="card">
                    <div className="cardTop">
                      <div>
                        <div className="cardTitle">I'm an Organiser</div>
                        <div className="meta">List your event + packages, receive sponsor offers, accept deals.</div>
                      </div>
                    </div>
                    <div className="btnRow" style={{ marginTop: 12 }}>
                      <button className="btn primary" onClick={() => nav("organiser")}>Go to Organiser</button>
                    </div>
                  </div>
                  <div className="card">
                    <div className="cardTop">
                      <div>
                        <div className="cardTitle">I'm a Sponsor</div>
                        <div className="meta">Filter events, view packages, send an offer in 30 seconds.</div>
                      </div>
                    </div>
                    <div className="btnRow" style={{ marginTop: 12 }}>
                      <button className="btn primary" onClick={() => nav("sponsor")}>Go to Sponsor</button>
                    </div>
                  </div>
                </div>
                <div className="divider"></div>
                <div className="card">
                  <div className="cardTop">
                    <div>
                      <div className="cardTitle">What's inside this prototype</div>
                      <div className="meta">Minimal, but end-to-end clickable.</div>
                    </div>
                  </div>
                  <div className="pillRow">
                    {["Create event", "Add packages", "Browse events + filters", "Send offer", "Accept deal", "Admin approve"].map(f => (
                      <span key={f} className="pill">{f}</span>
                    ))}
                  </div>
                </div>
              </section>
            )}

            {/* ORGANISER */}
            {activeScreen === "organiser" && (
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
                      <input value={event.name} onChange={e => setEvent({ ...event, name: e.target.value })} placeholder="e.g., Afro Vibes Night" />
                    </div>
                    <div className="field">
                      <label>City</label>
                      <input value={event.city} onChange={e => setEvent({ ...event, city: e.target.value })} placeholder="e.g., Glasgow" />
                    </div>
                  </div>
                  <div className="split">
                    <div className="field">
                      <label>Date</label>
                      <input type="date" value={event.date} onChange={e => setEvent({ ...event, date: e.target.value })} />
                    </div>
                    <div className="field">
                      <label>Audience size</label>
                      <select value={event.size} onChange={e => setEvent({ ...event, size: e.target.value })}>
                        <option>100-200</option>
                        <option>200-500</option>
                        <option>500-1000</option>
                        <option>1000+</option>
                      </select>
                    </div>
                  </div>
                  <div className="field">
                    <label>Vibe / type</label>
                    <select value={event.type} onChange={e => setEvent({ ...event, type: e.target.value })}>
                      <option>Afrobeats</option>
                      <option>Amapiano</option>
                      <option>Culture / Community</option>
                      <option>Corporate</option>
                      <option>Festival</option>
                    </select>
                  </div>
                  <div className="field">
                    <label>Quick pitch</label>
                    <textarea value={event.pitch} onChange={e => setEvent({ ...event, pitch: e.target.value })} placeholder="Why should a sponsor care?"></textarea>
                  </div>
                  <div className="btnRow">
                    <button className="primary" onClick={() => showToast("Saved", "Event listing updated.")}>Save event</button>
                    <button className="good" onClick={() => setShowPackages(true)}>Add packages</button>
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
                      {Object.entries(PKG_DETAILS).map(([pkg, details]) => (
                        <div className="card" key={pkg}>
                          <div className="cardTitle">{pkg} {pkg !== "Custom" && `- £${details.price}`}</div>
                          <div className="meta">{details.benefits}</div>
                          {pkg === "Custom" && (
                            <div className="field" style={{ marginTop: 10 }}>
                              <label>Custom package text</label>
                              <input placeholder="e.g., Drinks partnership" />
                            </div>
                          )}
                          <div className="btnRow">
                            <button className="btn good" onClick={() => {
                              setSelectedPackage(pkg as EventPkg);
                              if (!event.packages.includes(pkg as EventPkg)) {
                                setEvent({ ...event, packages: [...event.packages, pkg as EventPkg] });
                              }
                              showToast("Selected", `Package set to ${pkg}.`);
                            }}>Use</button>
                          </div>
                        </div>
                      ))}
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
                      {inbox.map(m => (
                        <div className="card" key={m.id}>
                          <div className="cardTop">
                            <div>
                              <div className="cardTitle">{m.from}</div>
                              <div className="meta">About: {m.about} • Package: {m.package} • Offer: £{m.amount}</div>
                            </div>
                            <button className="btn primary" onClick={() => {
                              setBrand({ ...brand, name: m.from });
                              setSelectedPackage(m.package);
                              setDeal({ status: "PENDING", notes: "" });
                              showToast("Deal opened", "Ready to accept / decline.");
                              nav("deal");
                            }}>Open deal</button>
                          </div>
                          <div className="meta" style={{ marginTop: 10 }}>{m.note}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </section>
            )}

            {/* SPONSOR */}
            {activeScreen === "sponsor" && (
              <section className="screen active">
                <div className="rightHeader">
                  <div>
                    <div className="cardTitle">Browse events</div>
                    <div className="meta">Find the right crowd fast.</div>
                  </div>
                </div>
                <div className="card">
                  <div className="searchbar">
                    <input placeholder="Filter by city" value={filterCity} onChange={e => setFilterCity(e.target.value)} />
                    <select value={filterType} onChange={e => setFilterType(e.target.value)}>
                      <option value="">All types</option>
                      <option>Afrobeats</option>
                      <option>Amapiano</option>
                      <option>Culture / Community</option>
                      <option>Corporate</option>
                      <option>Festival</option>
                    </select>
                    <select value={filterSize} onChange={e => setFilterSize(e.target.value)}>
                      <option value="">Any size</option>
                      <option>100-200</option>
                      <option>200-500</option>
                      <option>500-1000</option>
                      <option>1000+</option>
                    </select>
                    <button className="primary" onClick={() => showToast("Filtered", "Showing matches.")}>Apply</button>
                  </div>
                </div>

                <div className="list" style={{ marginTop: 12 }}>
                  {getCatalogue().filter(e => {
                    if (filterCity && !e.city.toLowerCase().includes(filterCity.toLowerCase())) return false;
                    if (filterType && e.type !== filterType) return false;
                    if (filterSize && e.size !== filterSize) return false;
                    return true;
                  }).map(e => (
                    <div className="card" key={e.id}>
                      <div className="cardTop">
                        <div>
                          <div className="cardTitle">{e.name}</div>
                          <div className="meta">{e.city} • {e.type} • Audience {e.size} • Date: {e.date}</div>
                        </div>
                        <button className="btn primary" onClick={() => nav("deal")}>View</button>
                      </div>
                      <div className="meta" style={{ marginTop: 10 }}>{e.pitch}</div>
                      <div className="pillRow">
                        <span className="pill">Packages: {e.packages.join(", ")}</span>
                      </div>
                      <div className="btnRow" style={{ marginTop: 10 }}>
                        <button className="btn warn" onClick={() => {
                          const amount = PKG_DETAILS[selectedPackage].price;
                          setOffers([{
                            id: `off_${Math.random()}`,
                            event: e.name,
                            sponsor: brand.name,
                            package: selectedPackage,
                            amount,
                            status: "SENT"
                          }, ...offers]);
                          showToast("Offer sent", `Sent ${selectedPackage} offer for £${amount}.`);
                          setShowOffers(true);
                        }}>Send offer ({selectedPackage})</button>
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
                        <input value={brand.name} onChange={e => setBrand({ ...brand, name: e.target.value })} />
                      </div>
                      <div className="field">
                        <label>Budget range</label>
                        <select value={brand.budget} onChange={e => setBrand({ ...brand, budget: e.target.value })}>
                          <option>£100-£300</option>
                          <option>£300-£1,000</option>
                          <option>£1,000-£5,000</option>
                          <option>£5,000+</option>
                        </select>
                      </div>
                    </div>
                    <div className="field">
                      <label>Industry</label>
                      <input value={brand.industry} onChange={e => setBrand({ ...brand, industry: e.target.value })} />
                    </div>
                    <div className="btnRow">
                      <button className="good" onClick={() => showToast("Saved", "Brand updated.")}>Save</button>
                      <button className="btn" onClick={() => setShowBrand(false)}>Close</button>
                    </div>
                  </div>
                )}

                {showOffers && (
                  <div className="card" style={{ marginTop: 12 }}>
                    <div className="cardTop">
                      <div>
                        <div className="cardTitle">My offers</div>
                        <div className="meta">Offers you've sent.</div>
                      </div>
                    </div>
                    <div className="list" style={{ marginTop: 10 }}>
                      {offers.map(o => (
                        <div className="card" key={o.id}>
                          <div className="cardTop">
                            <div>
                              <div className="cardTitle">{o.event}</div>
                              <div className="meta">Sponsor: {o.sponsor} • Package: {o.package} • £{o.amount} • Status: {o.status}</div>
                            </div>
                            <button className="btn" onClick={() => nav("deal")}>View</button>
                          </div>
                        </div>
                      ))}
                    </div>
                    <div className="btnRow">
                      <button className="btn" onClick={() => setShowOffers(false)}>Close</button>
                    </div>
                  </div>
                )}
              </section>
            )}

            {/* DEAL */}
            {activeScreen === "deal" && (
              <section className="screen active">
                <div className="card">
                  <div className="cardTop">
                    <div>
                      <div className="cardTitle">{event.name} x {brand.name}</div>
                      <div className="meta">Package: {selectedPackage} - £{PKG_DETAILS[selectedPackage].price} • City: {event.city}</div>
                    </div>
                    <div className="tag" style={{
                        background: deal.status === "ACCEPTED" ? "rgba(57,217,138,.16)" : deal.status === "DECLINED" ? "rgba(255,92,122,.14)" : "rgba(255,204,102,.14)",
                        borderColor: deal.status === "ACCEPTED" ? "rgba(57,217,138,.35)" : deal.status === "DECLINED" ? "rgba(255,92,122,.35)" : "rgba(255,204,102,.35)"
                      }}>{deal.status}</div>
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
                    <textarea value={deal.notes} onChange={e => setDeal({ ...deal, notes: e.target.value })} placeholder="Add logistics..."></textarea>
                  </div>
                  <div className="btnRow">
                    <button className="primary" onClick={() => showToast("Saved", "Deal notes updated.")}>Save notes</button>
                  </div>
                </div>
              </section>
            )}

            {/* ADMIN */}
            {activeScreen === "admin" && (
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
                      {approvals.map(a => (
                        <div className="card" key={a.id}>
                          <div className="cardTop">
                            <div>
                              <div className="cardTitle">{a.type}: {a.name}</div>
                              <div className="meta">{a.status}</div>
                            </div>
                            {a.status === "PENDING" ? (
                               <button className="btn primary" onClick={() => {
                                 setApprovals(approvals.map(app => app.id === a.id ? { ...app, status: "APPROVED" } : app));
                                 showToast("Approved", `${a.type} approved.`);
                               }}>Approve</button>
                            ) : (
                               <div className="tag" style={{background:'rgba(57,217,138,.16)', borderColor:'rgba(57,217,138,.35)'}}>✓</div>
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
                             <div className="cardTitle">{event.name} x {brand.name}</div>
                             <div className="meta">Package: {selectedPackage} • Status: {deal.status}</div>
                           </div>
                           <button className="btn" onClick={() => nav("deal")}>Open</button>
                         </div>
                      </div>
                    </div>
                  </div>
                </div>
              </section>
            )}

          </div>
        </div>
      </div>

      {toast && (
        <div className="toast show" role="status">
          <b>{toast.title}</b>
          <span>{toast.msg}</span>
        </div>
      )}
    </div>
  );
}
