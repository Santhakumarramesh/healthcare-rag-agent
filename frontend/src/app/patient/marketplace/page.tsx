"use client";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

export default function MarketplacePage() {
  const { data, isLoading } = useQuery({
    queryKey: ["marketplace"],
    queryFn: () => api.get("/marketplace/products").then((r) => r.data),
  });

  const products = data?.products ?? data ?? [];

  return (
    <div className="max-w-3xl mx-auto px-5 py-8 space-y-6">
      <div>
        <h1 className="text-2xl font-extrabold text-primary font-headline">Care Marketplace</h1>
        <p className="text-sm text-on-surface-variant">Medications, supplements, and wellness products</p>
      </div>

      {/* Categories */}
      <div className="flex gap-2 overflow-x-auto pb-1">
        {["All", "Medications", "Supplements", "Devices", "Wellness"].map((cat) => (
          <button key={cat}
            className="px-4 py-2 rounded-xl text-xs font-semibold whitespace-nowrap bg-surface-container text-on-surface-variant hover:bg-surface-container-high transition-all first:bg-primary first:text-white">
            {cat}
          </button>
        ))}
      </div>

      {/* Products */}
      {isLoading ? (
        <div className="grid grid-cols-2 gap-4">
          {[...Array(6)].map((_, i) => <div key={i} className="card animate-pulse h-48" />)}
        </div>
      ) : products.length === 0 ? (
        <div className="card text-center py-12">
          <span className="material-symbols-outlined text-5xl text-on-surface-variant">store</span>
          <p className="font-semibold text-on-surface mt-3">Marketplace coming soon</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-4">
          {products.map((p: {
            id: string;
            name: string;
            description?: string;
            price: number;
            category?: string;
            requires_prescription: boolean;
          }) => (
            <div key={p.id} className="card space-y-3">
              <div className="w-full h-24 bg-surface-container rounded-xl flex items-center justify-center">
                <span className="material-symbols-outlined text-3xl text-on-surface-variant">medication</span>
              </div>
              <div>
                <p className="font-semibold text-on-surface text-sm">{p.name}</p>
                {p.description && <p className="text-xs text-on-surface-variant mt-0.5 line-clamp-2">{p.description}</p>}
              </div>
              <div className="flex items-center justify-between">
                <p className="font-bold text-primary">${p.price.toFixed(2)}</p>
                {p.requires_prescription && (
                  <span className="badge badge-warning text-[10px]">Rx</span>
                )}
              </div>
              <button className="btn-primary w-full text-xs py-2">Add to Cart</button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
