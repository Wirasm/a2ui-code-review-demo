"use client";

import { CopilotKitProvider, CopilotChat } from "@copilotkit/react-core/v2";
import { createA2UIMessageRenderer } from "@copilotkit/a2ui-renderer";
import "@copilotkit/react-core/v2/styles.css";
import { theme } from "./theme";

const A2UIRenderer = createA2UIMessageRenderer({ theme });
const activityRenderers = [A2UIRenderer];

export default function Home() {
  return (
    <CopilotKitProvider
      runtimeUrl="/api/copilotkit"
      showDevConsole="auto"
      renderActivityMessages={activityRenderers}
    >
      <main
        style={{
          height: "100dvh",
          width: "100vw",
          overflow: "auto",
          display: "flex",
          flexDirection: "column",
        }}
      >
        <CopilotChat
          labels={{
            chatInputPlaceholder:
              "Paste a GitHub PR URL to start a review...",
          }}
        />
      </main>
    </CopilotKitProvider>
  );
}
