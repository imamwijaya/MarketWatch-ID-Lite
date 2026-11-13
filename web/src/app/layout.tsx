import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});


export const metadata: Metadata = {
  title: "MarketWatch-ID Lite | Market Surveillance",
  description:
    "A portfolio prototype for rule-based equity price and volume anomaly detection using synthetic market data.",
  applicationName: "MarketWatch-ID Lite",
  icons: {
    icon: [
      {
        url: "/brand/favicon.svg",
        type: "image/svg+xml",
      },
    ],
    shortcut: "/brand/favicon.svg",
  },
};


export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
