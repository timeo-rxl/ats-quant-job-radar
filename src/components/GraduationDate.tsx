import { useState } from "react";
import { format } from "date-fns";
import { enUS, fr } from "date-fns/locale";
import { CalendarIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Calendar } from "@/components/ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { useI18n } from "@/lib/i18n";

export function GraduationDate({ value, onChange }: { value: string; onChange: (value: string) => void }) {
  const { t, lang } = useI18n();
  const [open, setOpen] = useState(false);
  const locale = lang === "en" ? enUS : fr;
  const valid = /^\d{4}-(0[1-9]|1[0-2])$/.test(value);
  const date = valid ? new Date(`${value}-01T12:00:00`) : undefined;
  return (
    <div className="max-w-full space-y-2 md:w-80">
      <div className="flex gap-2">
        <Input type="text" value={value} onChange={(e) => onChange(e.target.value)}
          aria-label={t.grad_format} placeholder={t.grad_format} maxLength={7}
          className="h-12 min-w-0 bg-card font-mono text-lg" />
        <Popover open={open} onOpenChange={setOpen}>
          <PopoverTrigger asChild>
            <Button type="button" variant="outline" size="icon" className="size-12 shrink-0"
              aria-label={t.grad_calendar} title={t.grad_calendar}><CalendarIcon /></Button>
          </PopoverTrigger>
          <PopoverContent className="w-auto p-0" align="end">
            <Calendar mode="single" selected={date} {...(date ? { defaultMonth: date } : {})} locale={locale}
              captionLayout="dropdown" endMonth={new Date(Math.max(2100, date?.getFullYear() ?? 2100), 11)} className="p-3 pointer-events-auto"
              formatters={{ formatMonthDropdown: (d) => format(d, "MMMM", { locale }) }}
              onMonthChange={(d) => onChange(format(d, "yyyy-MM"))}
              onSelect={(d) => { if (d) { onChange(format(d, "yyyy-MM")); setOpen(false); } }} />
          </PopoverContent>
        </Popover>
      </div>
      {date && <p className="font-mono text-sm">{format(date, "MMMM yyyy", { locale })}</p>}
      <p className="font-mono text-xs text-muted-foreground">{t.grad_format} · {value}</p>
    </div>
  );
}