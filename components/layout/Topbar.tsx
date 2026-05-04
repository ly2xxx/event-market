"use client";

// Sticky top bar with brand + nav. Uses usePathname so the active pill
// follows the URL — no local "activeScreen" state.

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { Screen } from "@/lib/types";

const NAV: { href: string; label: string; key: Screen }[] = [
  { href: "/", label: "Home", key: "home" },
  { href: "/organiser", label: "Organiser", key: "organiser" },
  { href: "/sponsor", label: "Sponsor", key: "sponsor" },
  { href: "/deal", label: "Deal", key: "deal" },
  { href: "/admin", label: "Admin", key: "admin" },
];

export function Topbar() {
  const pathname = usePathname();

  return (
    <div className="topbar">
      <div className="brand">
        <div className="logo" aria-hidden="true"></div>
        <div className="title">
          <b>Event Sponsor Marketplace</b>
          <span>Next.js Port</span>
        </div>
      </div>
      <nav className="nav" aria-label="Primary">
        {NAV.map((item) => {
          const isActive =
            item.href === "/"
              ? pathname === "/"
              : pathname.startsWith(item.href);
          return (
            <Link
              key={item.key}
              href={item.href}
              className={`chip ${isActive ? "active" : ""}`}
              aria-current={isActive ? "page" : undefined}
            >
              {item.label}
            </Link>
          );
        })}
      </nav>
    </div>
  );
}
