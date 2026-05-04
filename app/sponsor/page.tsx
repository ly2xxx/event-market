import { SponsorScreen } from "@/components/screens/SponsorScreen";
import { PanelHeader } from "@/components/layout/PanelHeader";

export default function SponsorPage() {
  return (
    <div className="panel">
      <PanelHeader title="Sponsor" />
      <div className="panelBody">
        <SponsorScreen />
      </div>
    </div>
  );
}
