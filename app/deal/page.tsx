import { DealScreen } from "@/components/screens/DealScreen";
import { PanelHeader } from "@/components/layout/PanelHeader";

export default function DealPage() {
  return (
    <div className="panel">
      <PanelHeader title="Deal" />
      <div className="panelBody">
        <DealScreen />
      </div>
    </div>
  );
}
