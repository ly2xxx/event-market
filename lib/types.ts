// Shared type definitions for the marketplace demo.
//
// Kept platform-agnostic (no React imports) so server components,
// client components, and any future API routes can all use them.

export type EventPkg = "Bronze" | "Silver" | "Gold" | "Custom";
export type DealStatus = "PENDING" | "ACCEPTED" | "DECLINED";
export type ApprovalStatus = "PENDING" | "APPROVED";
export type Screen = "home" | "organiser" | "sponsor" | "deal" | "admin";

export interface EventListing {
  id?: string;
  name: string;
  city: string;
  date: string;
  size: string;
  type: string;
  pitch: string;
  packages: EventPkg[];
}

export interface CatalogueEvent extends EventListing {
  id: string;
}

export interface Brand {
  name: string;
  budget: string;
  industry: string;
}

export interface Offer {
  id: string;
  event: string;
  sponsor: string;
  package: EventPkg;
  amount: number;
  status: string;
}

export interface InboxMessage {
  id: string;
  from: string;
  about: string;
  package: EventPkg;
  amount: number;
  note: string;
}

export interface Approval {
  id: string;
  type: "Event" | "Sponsor";
  name: string;
  status: ApprovalStatus;
}

export interface Deal {
  status: DealStatus;
  notes: string;
}

export interface Toast {
  title: string;
  msg: string;
}
