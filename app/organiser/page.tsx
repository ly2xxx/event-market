import { OrganiserScreen } from "@/components/screens/OrganiserScreen";
import { PanelHeader } from "@/components/layout/PanelHeader";

export default function OrganiserPage() {
  return (
    <div className="panel">
      <PanelHeader title="Organiser" />
      <div className="panelBody">
        <OrganiserScreen />
      </div>
    </div>
  );
}
