import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Code Review Agent",
  description: "AI-powered code review with A2UI + AG-UI + CopilotKit",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link
          href="https://fonts.googleapis.com/icon?family=Material+Icons"
          rel="stylesheet"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body style={{ margin: 0, fontFamily: "'Roboto', system-ui, sans-serif" }}>
        {children}
      </body>
    </html>
  );
}
