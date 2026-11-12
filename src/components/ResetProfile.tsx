import { RotateCcw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { DEFAULT_PROFILE } from "@/lib/matching";
import { profileStore } from "@/lib/store";
import { useI18n } from "@/lib/i18n";

export function ResetProfile({ onReset }: { onReset?: () => void }) {
  const { t } = useI18n();
  return (
    <Button type="button" variant="outline" size="sm" className="font-mono" onClick={() => {
      profileStore.set({ ...DEFAULT_PROFILE, interests: [...DEFAULT_PROFILE.interests] });
      onReset?.();
    }}>
      <RotateCcw /> {t.reset_profile}
    </Button>
  );
}