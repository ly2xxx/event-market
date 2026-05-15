"use client";

// Demo state shared across routes.
//
// Why a client Context (and not server-fetched data, Zustand, Redux, etc.)?
//
//   * Zero deps — keeps the wireframe stage lean.
//   * Survives client-side route changes (the Provider lives in app/layout.tsx
//     so navigating /organiser → /sponsor preserves state).
//   * One swap-out point: when Supabase lands, replace the in-memory state
//     with TanStack Query / RSC-fetched data. The component API doesn't
//     change.

import { createContext, useCallback, useContext, useMemo, useState } from "react";
import type { ReactNode } from "react";
import type {
  Approval,
  Brand,
  Deal,
  EventListing,
  EventPkg,
  InboxMessage,
  Offer,
  Toast,
} from "./types";

interface DemoStore {
  // Data
  event: EventListing;
  brand: Brand;
  selectedPackage: EventPkg;
  offers: Offer[];
  inbox: InboxMessage[];
  deal: Deal;
  approvals: Approval[];

  // Setters
  setEvent: (e: EventListing) => void;
  setBrand: (b: Brand) => void;
  setSelectedPackage: (p: EventPkg) => void;
  setOffers: (o: Offer[]) => void;
  setInbox: (i: InboxMessage[]) => void;
  setDeal: (d: Deal) => void;
  setApprovals: (a: Approval[]) => void;

  // Toast (rendered by ToastHost in the layout)
  toast: Toast | null;
  showToast: (title: string, msg: string) => void;
}

const DemoStoreContext = createContext<DemoStore | null>(null);

export function DemoStoreProvider({ children }: { children: ReactNode }) {
  const [event, setEvent] = useState<EventListing>({
    name: "Afro Vibes Night",
    city: "Glasgow",
    date: "",
    size: "200-500",
    type: "Afrobeats",
    pitch:
      "High-energy Afro night. 70% students + young professionals. Heavy IG content.",
    packages: ["Bronze", "Silver", "Gold"],
  });

  const [brand, setBrand] = useState<Brand>({
    name: "Pulse Drinks",
    budget: "£300-£1,000",
    industry: "Beverage",
  });

  const [selectedPackage, setSelectedPackage] = useState<EventPkg>("Silver");

  const [offers, setOffers] = useState<Offer[]>([
    {
      id: "off_1",
      event: "Afro Vibes Night",
      sponsor: "Pulse Drinks",
      package: "Silver",
      amount: 500,
      status: "SENT",
    },
  ]);

  const [inbox, setInbox] = useState<InboxMessage[]>([
    {
      id: "msg_1",
      from: "Pulse Drinks",
      about: "Afro Vibes Night",
      package: "Silver",
      amount: 500,
      note: "We can sponsor + provide free cans for VIP.",
    },
    {
      id: "msg_2",
      from: "Streetwear Co",
      about: "Afro Vibes Night",
      package: "Bronze",
      amount: 250,
      note: "Logo + giveaway collab?",
    },
  ]);

  const [deal, setDeal] = useState<Deal>({ status: "PENDING", notes: "" });

  const [approvals, setApprovals] = useState<Approval[]>([
    { id: "ap_1", type: "Event", name: "Afro Vibes Night", status: "PENDING" },
    { id: "ap_2", type: "Sponsor", name: "Pulse Drinks", status: "PENDING" },
  ]);

  const [toast, setToast] = useState<Toast | null>(null);

  const showToast = useCallback((title: string, msg: string) => {
    setToast({ title, msg });
    // Single timer; not racing other showToast calls because each replaces the toast object.
    window.setTimeout(() => setToast(null), 2400);
  }, []);

  const value = useMemo<DemoStore>(
    () => ({
      event,
      brand,
      selectedPackage,
      offers,
      inbox,
      deal,
      approvals,
      setEvent,
      setBrand,
      setSelectedPackage,
      setOffers,
      setInbox,
      setDeal,
      setApprovals,
      toast,
      showToast,
    }),
    [event, brand, selectedPackage, offers, inbox, deal, approvals, toast, showToast],
  );

  return (
    <DemoStoreContext.Provider value={value}>{children}</DemoStoreContext.Provider>
  );
}

export function useDemoStore(): DemoStore {
  const ctx = useContext(DemoStoreContext);
  if (!ctx) {
    throw new Error("useDemoStore must be used inside <DemoStoreProvider>");
  }
  return ctx;
}
