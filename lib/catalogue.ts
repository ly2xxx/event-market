import type { CatalogueEvent, EventListing } from "./types";
import { STATIC_EVENTS } from "./constants";

/**
 * The catalogue is the user's live event prepended to the seeded sample events.
 * Pure function — safe to call from server or client components.
 */
export function buildCatalogue(liveEvent: EventListing): CatalogueEvent[] {
  return [
    { id: "e1", ...liveEvent, date: liveEvent.date || "TBA" },
    ...STATIC_EVENTS,
  ];
}
