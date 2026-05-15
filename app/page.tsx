// Server component. Imports a single client component for the interactive
// content. The right-panel chrome is rendered server-side.

import { HomeScreen } from "@/components/screens/HomeScreen";
import { PanelHeader } from "@/components/layout/PanelHeader";

export default function HomePage() {
  return (
    <div className="panel">
      <PanelHeader title="Home" />
      <div className="panelBody">
        <HomeScreen />
      </div>
    </div>
  );
}
