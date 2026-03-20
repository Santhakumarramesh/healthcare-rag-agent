"use client";
import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { trackingApi } from "@/lib/api";
import toast from "react-hot-toast";

type Tab = "symptoms" | "vitals" | "medications" | "hydration" | "sleep" | "activity";

const TABS: { id: Tab; label: string; icon: string }[] = [
  { id: "symptoms",    label: "Symptoms",   icon: "sick" },
  { id: "vitals",      label: "Vitals",     icon: "monitor_heart" },
  { id: "medications", label: "Meds",       icon: "medication" },
  { id: "hydration",   label: "Hydration",  icon: "water_drop" },
  { id: "sleep",       label: "Sleep",      icon: "bedtime" },
  { id: "activity",    label: "Activity",   icon: "directions_walk" },
];

export default function TrackingPage() {
  const [activeTab, setActiveTab] = useState<Tab>("symptoms");
  const qc = useQueryClient();

  const { data: summary } = useQuery({
    queryKey: ["tracking-summary"],
    queryFn: () => trackingApi.getSummary().then((r) => r.data),
  });

  const { mutate: logSymptom, isPending: loggingSymptom } = useMutation({
    mutationFn: (data: object) => trackingApi.logSymptom(data),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["tracking-summary"] }); toast.success("Symptom logged"); },
    onError: () => toast.error("Failed to log symptom"),
  });

  const { mutate: logVitals, isPending: loggingVitals } = useMutation({
    mutationFn: (data: object) => trackingApi.logVitals(data),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["tracking-summary"] }); toast.success("Vitals saved"); },
    onError: () => toast.error("Failed to save vitals"),
  });

  const { mutate: logHydration } = useMutation({
    mutationFn: (data: object) => trackingApi.logHydration(data),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["tracking-summary"] }); toast.success("Hydration logged"); },
  });

  const { mutate: logSleep } = useMutation({
    mutationFn: (data: object) => trackingApi.logSleep(data),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["tracking-summary"] }); toast.success("Sleep logged"); },
  });

  // ── Forms ──────────────────────────────────────────────────────────────────
  const SymptomForm = () => {
    const [form, setForm] = useState({ symptom_name: "", severity: 5, notes: "" });
    return (
      <div className="card space-y-4">
        <h3 className="font-bold text-on-surface font-headline">Log Symptom</h3>
        <div className="space-y-3">
          <input className="input-field" placeholder="Symptom (e.g. headache, fatigue)"
            value={form.symptom_name} onChange={(e) => setForm({ ...form, symptom_name: e.target.value })} />
          <div>
            <label className="text-xs font-medium text-on-surface-variant">Severity: {form.severity}/10</label>
            <input type="range" min={1} max={10} value={form.severity}
              onChange={(e) => setForm({ ...form, severity: +e.target.value })}
              className="w-full accent-primary mt-1" />
            <div className="flex justify-between text-xs text-on-surface-variant">
              <span>Mild</span><span>Severe</span>
            </div>
          </div>
          <textarea className="input-field" placeholder="Additional notes (optional)" rows={2}
            value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
          <button className="btn-primary w-full" disabled={!form.symptom_name || loggingSymptom}
            onClick={() => logSymptom(form)}>
            {loggingSymptom ? "Saving…" : "Log Symptom"}
          </button>
        </div>
      </div>
    );
  };

  const VitalsForm = () => {
    const [form, setForm] = useState({ systolic: "", diastolic: "", heart_rate: "", blood_glucose: "", temperature: "" });
    return (
      <div className="card space-y-4">
        <h3 className="font-bold text-on-surface font-headline">Log Vitals</h3>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-xs font-medium text-on-surface-variant">Systolic (mmHg)</label>
            <input type="number" className="input-field mt-1" placeholder="120"
              value={form.systolic} onChange={(e) => setForm({ ...form, systolic: e.target.value })} />
          </div>
          <div>
            <label className="text-xs font-medium text-on-surface-variant">Diastolic (mmHg)</label>
            <input type="number" className="input-field mt-1" placeholder="80"
              value={form.diastolic} onChange={(e) => setForm({ ...form, diastolic: e.target.value })} />
          </div>
          <div>
            <label className="text-xs font-medium text-on-surface-variant">Heart Rate (bpm)</label>
            <input type="number" className="input-field mt-1" placeholder="72"
              value={form.heart_rate} onChange={(e) => setForm({ ...form, heart_rate: e.target.value })} />
          </div>
          <div>
            <label className="text-xs font-medium text-on-surface-variant">Blood Glucose</label>
            <input type="number" className="input-field mt-1" placeholder="mg/dL"
              value={form.blood_glucose} onChange={(e) => setForm({ ...form, blood_glucose: e.target.value })} />
          </div>
          <div className="col-span-2">
            <label className="text-xs font-medium text-on-surface-variant">Temperature (°F)</label>
            <input type="number" className="input-field mt-1" placeholder="98.6"
              value={form.temperature} onChange={(e) => setForm({ ...form, temperature: e.target.value })} />
          </div>
        </div>
        <button className="btn-primary w-full" disabled={loggingVitals}
          onClick={() => logVitals(form)}>
          {loggingVitals ? "Saving…" : "Save Vitals"}
        </button>
      </div>
    );
  };

  const HydrationForm = () => {
    const AMOUNTS = [100, 200, 250, 350, 500];
    return (
      <div className="card space-y-4">
        <h3 className="font-bold text-on-surface font-headline">Log Hydration</h3>
        <p className="text-sm text-on-surface-variant">Tap to add water intake</p>
        <div className="grid grid-cols-3 gap-2">
          {AMOUNTS.map((ml) => (
            <button key={ml} className="btn-secondary flex flex-col items-center py-4 gap-1"
              onClick={() => logHydration({ amount_ml: ml })}>
              <span className="material-symbols-outlined text-secondary">water_drop</span>
              <span className="font-bold text-on-surface">{ml}ml</span>
            </button>
          ))}
          <button className="btn-secondary flex flex-col items-center py-4 gap-1 col-span-3">
            <span className="text-xs text-on-surface-variant">Custom amount</span>
          </button>
        </div>
        {summary?.today?.hydration_total_ml != null && (
          <div className="bg-secondary-fixed/30 rounded-xl p-3 text-center">
            <p className="text-2xl font-bold text-on-secondary-container">{summary.today.hydration_total_ml}ml</p>
            <p className="text-xs text-on-surface-variant">Today&apos;s total</p>
          </div>
        )}
      </div>
    );
  };

  const SleepForm = () => {
    const [form, setForm] = useState({ hours: 7, quality: 7, bed_time: "22:00", wake_time: "06:00" });
    return (
      <div className="card space-y-4">
        <h3 className="font-bold text-on-surface font-headline">Log Sleep</h3>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-xs font-medium text-on-surface-variant">Bedtime</label>
            <input type="time" className="input-field mt-1"
              value={form.bed_time} onChange={(e) => setForm({ ...form, bed_time: e.target.value })} />
          </div>
          <div>
            <label className="text-xs font-medium text-on-surface-variant">Wake time</label>
            <input type="time" className="input-field mt-1"
              value={form.wake_time} onChange={(e) => setForm({ ...form, wake_time: e.target.value })} />
          </div>
        </div>
        <div>
          <label className="text-xs font-medium text-on-surface-variant">Quality: {form.quality}/10</label>
          <input type="range" min={1} max={10} value={form.quality}
            onChange={(e) => setForm({ ...form, quality: +e.target.value })}
            className="w-full accent-primary mt-1" />
        </div>
        <button className="btn-primary w-full"
          onClick={() => logSleep(form)}>
          Save Sleep
        </button>
      </div>
    );
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case "symptoms":    return <SymptomForm />;
      case "vitals":      return <VitalsForm />;
      case "hydration":   return <HydrationForm />;
      case "sleep":       return <SleepForm />;
      case "medications": return (
        <div className="card text-center py-8">
          <span className="material-symbols-outlined text-4xl text-on-surface-variant">medication</span>
          <p className="font-semibold text-on-surface mt-3">Medication Tracking</p>
          <p className="text-sm text-on-surface-variant">Track your daily medications here</p>
        </div>
      );
      case "activity": return (
        <div className="card text-center py-8">
          <span className="material-symbols-outlined text-4xl text-on-surface-variant">directions_walk</span>
          <p className="font-semibold text-on-surface mt-3">Activity Tracking</p>
          <p className="text-sm text-on-surface-variant">Log your daily activity and steps</p>
        </div>
      );
    }
  };

  return (
    <div className="max-w-2xl mx-auto px-5 py-8 space-y-6">
      <div>
        <h1 className="text-2xl font-extrabold text-primary font-headline">Health Tracking</h1>
        <p className="text-sm text-on-surface-variant">Log and monitor your daily health metrics</p>
      </div>

      {/* Today summary row */}
      {summary?.today && (
        <div className="grid grid-cols-3 gap-2">
          {[
            { icon: "water_drop",  label: "Water",   value: summary.today.hydration_total_ml ? `${summary.today.hydration_total_ml}ml` : "--" },
            { icon: "bedtime",     label: "Sleep",   value: summary.today.sleep_hours ? `${summary.today.sleep_hours}h` : "--" },
            { icon: "monitor_heart", label: "BP",   value: summary.today.blood_pressure || "--" },
          ].map(({ icon, label, value }) => (
            <div key={label} className="card flex flex-col items-center gap-1 py-3">
              <span className="material-symbols-outlined text-secondary">{icon}</span>
              <span className="text-base font-bold text-on-surface">{value}</span>
              <span className="text-[10px] text-on-surface-variant">{label}</span>
            </div>
          ))}
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-1 overflow-x-auto pb-1 no-scrollbar">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
              activeTab === tab.id
                ? "bg-primary text-white"
                : "bg-surface-container text-on-surface-variant hover:bg-surface-container-high"
            }`}
          >
            <span className="material-symbols-outlined text-sm">{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </div>

      {renderTabContent()}
    </div>
  );
}
