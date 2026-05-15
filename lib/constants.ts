import type { CatalogueEvent, EventPkg } from "./types";

export const PKG_DETAILS: Record<EventPkg, { price: number; benefits: string }> = {
  Bronze: { price: 250, benefits: "Logo on flyer • 1 IG story mention" },
  Silver: { price: 500, benefits: "Logo on flyer • MC shoutout • 1 post tag" },
  Gold: { price: 1000, benefits: "Booth • content bundle • headline mention" },
  Custom: { price: 750, benefits: "Custom deliverables (as agreed)" },
};

export const EVENT_TYPES = [
  "Afrobeats",
  "Amapiano",
  "Culture / Community",
  "Corporate",
  "Festival",
] as const;

export const AUDIENCE_SIZES = ["100-200", "200-500", "500-1000", "1000+"] as const;

export const BUDGET_RANGES = [
  "£100-£300",
  "£300-£1,000",
  "£1,000-£5,000",
  "£5,000+",
] as const;

export const STATIC_EVENTS: CatalogueEvent[] = [
  {
    id: "e2",
    name: "Amapiano Terrace",
    city: "Edinburgh",
    type: "Amapiano",
    size: "100-200",
    date: "TBA",
    pitch: "Sunset terrace vibe + content-heavy crowd.",
    packages: ["Bronze", "Silver", "Gold"],
  },
  {
    id: "e3",
    name: "Culture & Community Market",
    city: "Glasgow",
    type: "Culture / Community",
    size: "500-1000",
    date: "TBA",
    pitch: "Family friendly, diaspora brands, strong community presence.",
    packages: ["Bronze", "Silver"],
  },
  {
    id: "e4",
    name: "Corporate Afterhours",
    city: "London",
    type: "Corporate",
    size: "200-500",
    date: "TBA",
    pitch: "Young professionals, high spending power.",
    packages: ["Gold", "Silver"],
  },
];
