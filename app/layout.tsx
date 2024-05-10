import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
    title: "Groningen Prayer Times",
    description: "Time table generator for prayer times for Masjid Al-Rahma in Groningen, Netherlands",
};

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html lang="en">
            <head>
                <link rel="icon" type="image/png" href="logo.png" />
            </head>
            <body>{children}</body>
        </html>
    );
}
