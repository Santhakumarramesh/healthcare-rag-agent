"use client";
import { useState, useRef } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { reportsApi } from "@/lib/api";
import { formatDate, getStatusColor } from "@/lib/utils";
import Link from "next/link";
import toast from "react-hot-toast";

export default function RecordsPage() {
  const qc = useQueryClient();
  const fileRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);
  const [search, setSearch] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["reports"],
    queryFn: () => reportsApi.list().then((r) => r.data),
  });

  const { mutate: analyze } = useMutation({
    mutationFn: (id: string) => reportsApi.analyze(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["reports"] });
      toast.success("Analysis started!");
    },
    onError: () => toast.error("Could not start analysis"),
  });

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const form = new FormData();
    form.append("file", file);
    setUploading(true);
    try {
      await reportsApi.upload(form);
      await qc.invalidateQueries({ queryKey: ["reports"] });
      toast.success("Report uploaded successfully!");
    } catch {
      toast.error("Upload failed. Check file type and size.");
    } finally {
      setUploading(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  };

  const reports = (data?.reports ?? data ?? []).filter((r: { report_type?: string; file_name?: string }) =>
    !search ||
    r.report_type?.toLowerCase().includes(search.toLowerCase()) ||
    r.file_name?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="max-w-2xl mx-auto px-5 py-8 space-y-6">
      <div>
        <h1 className="text-2xl font-extrabold text-primary font-headline">Medical Records</h1>
        <p className="text-sm text-on-surface-variant">Upload and analyze your health reports</p>
      </div>

      {/* Upload area */}
      <div
        className="border-2 border-dashed border-outline-variant hover:border-primary rounded-2xl p-8 text-center cursor-pointer transition-colors group"
        onClick={() => fileRef.current?.click()}
      >
        <div className="w-14 h-14 rounded-2xl bg-primary-fixed/30 flex items-center justify-center mx-auto mb-3 group-hover:bg-primary-fixed/50 transition-colors">
          {uploading ? (
            <div className="w-6 h-6 border-2 border-primary/30 border-t-primary rounded-full animate-spin" />
          ) : (
            <span className="material-symbols-outlined text-3xl text-primary">upload_file</span>
          )}
        </div>
        <p className="font-semibold text-on-surface">{uploading ? "Uploading…" : "Upload Report"}</p>
        <p className="text-xs text-on-surface-variant mt-1">PDF, JPG, PNG, DICOM up to 20MB</p>
        <input ref={fileRef} type="file" className="hidden" accept=".pdf,.jpg,.jpeg,.png,.dcm" onChange={handleUpload} />
      </div>

      {/* Search */}
      <div className="relative">
        <span className="absolute left-3 top-1/2 -translate-y-1/2 material-symbols-outlined text-on-surface-variant text-sm">search</span>
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="input-field pl-9"
          placeholder="Search reports…"
        />
      </div>

      {/* List */}
      {isLoading ? (
        <div className="space-y-3">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="card animate-pulse">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-surface-container" />
                <div className="flex-1 space-y-2">
                  <div className="h-4 bg-surface-container rounded w-2/3" />
                  <div className="h-3 bg-surface-container rounded w-1/3" />
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : reports.length === 0 ? (
        <div className="card text-center py-12">
          <span className="material-symbols-outlined text-5xl text-on-surface-variant">folder_open</span>
          <p className="font-semibold text-on-surface mt-3">No reports yet</p>
          <p className="text-sm text-on-surface-variant">Upload your first medical report above</p>
        </div>
      ) : (
        <div className="space-y-3">
          {reports.map((report: {
            id: string;
            report_type?: string;
            file_name?: string;
            status: string;
            created_at: string;
            file_size_mb?: number;
          }) => (
            <div key={report.id} className="card group">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-primary-fixed/20 flex items-center justify-center shrink-0">
                  <span className="material-symbols-outlined text-primary">description</span>
                </div>
                <div className="flex-1 min-w-0">
                  <Link href={`/patient/records/${report.id}`}>
                    <p className="font-semibold text-on-surface hover:text-primary transition-colors truncate cursor-pointer">
                      {report.report_type || report.file_name || "Report"}
                    </p>
                  </Link>
                  <div className="flex items-center gap-2 mt-0.5">
                    <p className="text-xs text-on-surface-variant">{formatDate(report.created_at)}</p>
                    {report.file_size_mb && (
                      <p className="text-xs text-on-surface-variant">· {report.file_size_mb.toFixed(1)} MB</p>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`badge ${getStatusColor(report.status)}`}>{report.status}</span>
                  {report.status === "uploaded" && (
                    <button
                      onClick={() => analyze(report.id)}
                      className="text-xs font-semibold text-secondary hover:underline"
                    >
                      Analyze
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
