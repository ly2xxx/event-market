import { AdminScreen } from "@/components/screens/AdminScreen";
import { PanelHeader } from "@/components/layout/PanelHeader";

export default function AdminPage() {
  return (
    <div className="panel">
      <PanelHeader title="Admin" />
      <div className="panelBody">
        <AdminScreen />
      </div>
    </div>
  );
}
