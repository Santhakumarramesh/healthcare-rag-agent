"use client";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { doctorsApi } from "@/lib/api";
import toast from "react-hot-toast";

const DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
const HOURS = Array.from({ length: 17 }, (_, i) => {
  const h = i + 7;
  const label = h < 12 ? `${h}:00 AM` : h === 12 ? "12:00 PM" : `${h - 12}:00 PM`;
  return { value: `${h.toString().padStart(2, "0")}:00`, label };
});

export default function DoctorAvailabilityPage() {
  const qc = useQueryClient();
  const [schedule, setSchedule] = useState<Record<string, { enabled: boolean; start: string; end: string }>>({
    Monday: { enabled: true, start: "09:00", end: "17:00" },
    Tuesday: { enabled: true, start: "09:00", end: "17:00" },
    Wednesday: { enabled: true, start: "09:00", end: "17:00" },
    Thursday: { enabled: true, start: "09:00", end: "17:00" },
    Friday: { enabled: true, start: "09:00", end: "13:00" },
    Saturday: { enabled: false, start: "09:00", end: "12:00" },
    Sunday: { enabled: false, start: "09:00", end: "12:00" },
  });

  const { data } = useQuery({
    queryKey: ["doctor-availability"],
    queryFn: () => doctorsApi.getAvailability().then((r) => r.data),
    onSuccess: (d: unknown) => {
      if (d && typeof d === 'object') setSchedule(d as typeof schedule);
    },
  });

  const { mutate: saveAvailability, isPending } = useMutation({
    mutationFn: () => doctorsApi.setAvailability(schedule),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["doctor-availability"] }); toast.success("Availability saved!"); },
    onError: () => toast.error("Failed to save availability"),
  });

  const toggle = (day: string) => setSchedule((s) => ({
    ...s,
    [day]: { ...s[day], enabled: !s[day].enabled },
  }));

  const update = (day: string, field: "start" | "end", val: string) => setSchedule((s) => ({
    ...s,
    [day]: { ...s[day], [field]: val },
  }));

  return (
    <div className="max-w-2xl mx-auto px-6 py-8 space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-extrabold text-primary font-headline">Availability</h1>
          <p className="text-sm text-on-surface-variant">Set your weekly consultation schedule</p>
        </div>
        <button onClick={() => saveAvailability()} disabled={isPending} className="btn-primary text-sm flex items-center gap-2">
          {isPending ? (
            <><div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> Saving…</>
          ) : (
            <><span className="material-symbols-outlined text-sm">save</span> Save</>
          )}
        </button>
      </div>

      <div className="space-y-2">
        {DAYS.map((day) => {
          const slot = schedule[day];
          return (
            <div key={day} className={`card flex items-center gap-4 ${!slot.enabled ? "opacity-50" : ""}`}>
              {/* Toggle */}
              <button onClick={() => toggle(day)}
                className={`w-11 h-6 rounded-full relative transition-colors flex-shrink-0 ${slot.enabled ? "bg-primary" : "bg-outline-variant"}`}>
                <div className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-transform shadow ${slot.enabled ? "translate-x-6" : "translate-x-1"}`} />
              </button>

              {/* Day label */}
              <span className="w-24 text-sm font-semibold text-on-surface">{day}</span>

              {/* Time range */}
              {slot.enabled ? (
                <div className="flex items-center gap-2 flex-1">
                  <select value={slot.start} onChange={(e) => update(day, "start", e.target.value)}
                    className="input-field text-xs py-2 flex-1">
                    {HOURS.map((h) => <option key={h.value} value={h.value}>{h.label}</option>)}
                  </select>
                  <span className="text-xs text-on-surface-variant">to</span>
                  <select value={slot.end} onChange={(e) => update(day, "end", e.target.value)}
                    className="input-field text-xs py-2 flex-1">
                    {HOURS.map((h) => <option key={h.value} value={h.value}>{h.label}</option>)}
                  </select>
                </div>
              ) : (
                <span className="text-sm text-on-surface-variant">Not available</span>
              )}
            </div>
          );
        })}
      </div>

      <div className="card bg-secondary-fixed/20 border border-secondary/10">
        <div className="flex items-start gap-3">
          <span className="material-symbols-outlined text-on-secondary-container">info</span>
          <p className="text-sm text-on-secondary-container">
            Patients can book consultations during your available hours. Changes take effect immediately.
          </p>
        </div>
      </div>
    </div>
  );
}
