import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

import { DemoStoreProvider } from "@/lib/demo-store";
import { LeftPanel } from "@/components/layout/LeftPanel";
import { ToastHost } from "@/components/layout/ToastHost";
import { Topbar } from "@/components/layout/Topbar";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Event Sponsor Marketplace",
  description: "Next.js port of the Event Sponsor Marketplace MVP",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">
        {/*
          The layout itself is a server component. Only the Provider, Topbar,
          LeftPanel, and ToastHost cross into the client — everything else
          server-renders. Each route page owns its own right-panel chrome.
        */}
        <DemoStoreProvider>
          <div className="wrap">
            <Topbar />
            <div className="grid">
              <LeftPanel />
              {children}
            </div>
          </div>
          <ToastHost />
        </DemoStoreProvider>
      </body>
    </html>
  );
}
