"use client";
import React, { useState, useEffect } from "react";
import Link from "next/link";

type EntityInfo = {
    id: string;
    name: string;
    archetype: string;
    faction_tags: string[];
    follower_count: number;
    is_verified: boolean;
    is_player: boolean;
    is_rising_star: boolean;
    total_engagement: number;
    grudges: string[];
    top_traits: Record<string, number>;
    hostility: number;
};

export default function AdminPanel() {
    const [entities, setEntities] = useState<EntityInfo[]>([]);
    const [selectedEntity, setSelectedEntity] = useState<string | null>(null);
    const [scandalText, setScandalText] = useState("");
    const [traitKey, setTraitKey] = useState("");
    const [traitValue, setTraitValue] = useState(0);
    const [statusLog, setStatusLog] = useState<string[]>([]);
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const [exportData, setExportData] = useState<any>(null);

    const log = (msg: string) => setStatusLog((prev) => [`[${new Date().toLocaleTimeString()}] ${msg}`, ...prev.slice(0, 19)]);

    const fetchEntities = async () => {
        try {
            const res = await fetch("http://127.0.0.1:8000/api/admin/entities");
            const data = await res.json();
            setEntities(data.entities || []);
            log(`Loaded ${data.total_count} entities.`);
        } catch (e) {
            log("Failed to load entities.");
        }
    };

    useEffect(() => {
        fetchEntities();
    }, []);

    const forcePulse = async () => {
        try {
            const res = await fetch("http://127.0.0.1:8000/api/admin/force_pulse", { method: "POST" });
            const data = await res.json();
            log(`PULSE FIRED: ${data.active_pulse?.topic || "Unknown"}`);
        } catch (e) {
            log("Force Pulse failed.");
        }
    };

    const injectScandal = async () => {
        if (!selectedEntity || !scandalText.trim()) return;
        try {
            const res = await fetch("http://127.0.0.1:8000/api/admin/inject_scandal", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ target_id: selectedEntity, scandal_text: scandalText }),
            });
            const data = await res.json();
            log(`SCANDAL: ${data.message}`);
            setScandalText("");
        } catch (e) {
            log("Scandal injection failed.");
        }
    };

    const editTrait = async () => {
        if (!selectedEntity || !traitKey.trim()) return;
        try {
            const res = await fetch("http://127.0.0.1:8000/api/admin/edit_traits", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ entity_id: selectedEntity, traits: { [traitKey]: traitValue } }),
            });
            const data = await res.json();
            if (data.changes) {
                // eslint-disable-next-line @typescript-eslint/no-explicit-any
                log(`TRAIT EDIT on ${data.entity}: ${data.changes.map((c: any) => `${c.trait}: ${c.old} → ${c.new}`).join(", ")}`);
                fetchEntities();
            }
        } catch (e) {
            log("Trait edit failed.");
        }
    };

    const exportState = async () => {
        try {
            const res = await fetch("http://127.0.0.1:8000/api/admin/export_state");
            const data = await res.json();
            setExportData(data);
            log(`EXPORT: ${data.total_entities} entities, ${data.total_events} events.`);
        } catch (e) {
            log("Export failed.");
        }
    };

    const selected = entities.find((e) => e.id === selectedEntity);

    return (
        <div className="min-h-screen bg-navy text-text-main">
            {/* Header */}
            <div className="border-b border-maroon bg-maroon/10 p-4 flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <span className="text-2xl">⚡</span>
                    <h1 className="text-2xl font-black tracking-widest uppercase text-maroon">God Mode</h1>
                    <span className="text-[10px] bg-maroon text-text-main px-2 py-0.5 rounded-full font-bold uppercase animate-pulse">
                        Admin
                    </span>
                </div>
                <Link href="/" className="text-text-muted hover:text-white text-sm transition">
                    ← Back to TwitLife
                </Link>
            </div>

            <div className="max-w-7xl mx-auto p-6 flex gap-6">
                {/* Left Panel: Controls */}
                <div className="flex-1 space-y-6">
                    {/* Quick Actions */}
                    <section className="bg-navy-light rounded-2xl border border-border-dark p-6 space-y-4">
                        <h2 className="text-lg font-bold flex items-center gap-2">
                            <span>🌐</span> World Controls
                        </h2>
                        <div className="flex gap-3">
                            <button onClick={forcePulse} className="bg-maroon hover:bg-maroon-hover text-text-main font-bold py-2.5 px-6 rounded-lg transition text-sm">
                                ⚡ Force Pulse
                            </button>
                            <button onClick={exportState} className="bg-deep-green hover:bg-deep-green-hover text-text-main font-bold py-2.5 px-6 rounded-lg transition text-sm">
                                📊 Export City State
                            </button>
                            <button onClick={fetchEntities} className="bg-border-dark hover:bg-navy text-text-muted font-bold py-2.5 px-6 rounded-lg transition text-sm">
                                🔄 Refresh Roster
                            </button>
                        </div>
                    </section>

                    {/* Entity Selector */}
                    <section className="bg-navy-light rounded-2xl border border-border-dark p-6 space-y-4">
                        <h2 className="text-lg font-bold flex items-center gap-2">
                            <span>👤</span> Entity Selector
                        </h2>
                        <select
                            onChange={(e) => setSelectedEntity(e.target.value || null)}
                            value={selectedEntity || ""}
                            className="w-full bg-navy border border-border-dark rounded-lg p-3 text-text-main outline-none focus:border-deep-green transition"
                        >
                            <option value="">Select an entity...</option>
                            {entities.map((e) => (
                                <option key={e.id} value={e.id}>
                                    {e.name} — {e.archetype} ({e.follower_count.toLocaleString()} followers)
                                    {e.is_verified ? " ✓" : ""}
                                    {e.is_rising_star ? " ⭐" : ""}
                                </option>
                            ))}
                        </select>

                        {selected && (
                            <div className="bg-navy rounded-xl p-4 border border-border-dark space-y-3">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <span className="font-bold text-lg">{selected.name}</span>
                                        {selected.is_verified && <span className="text-blue-400 ml-1">✓</span>}
                                        {selected.is_rising_star && <span className="text-yellow-400 ml-1">⭐</span>}
                                    </div>
                                    <span className="text-[10px] uppercase bg-border-dark px-2 py-0.5 rounded-full text-text-muted">{selected.archetype}</span>
                                </div>
                                <div className="grid grid-cols-3 gap-2 text-xs">
                                    <div className="bg-navy-light rounded-lg p-2 text-center">
                                        <div className="text-text-muted">Followers</div>
                                        <div className="font-bold text-deep-green">{selected.follower_count.toLocaleString()}</div>
                                    </div>
                                    <div className="bg-navy-light rounded-lg p-2 text-center">
                                        <div className="text-text-muted">Engagement</div>
                                        <div className="font-bold">{selected.total_engagement}</div>
                                    </div>
                                    <div className="bg-navy-light rounded-lg p-2 text-center">
                                        <div className="text-text-muted">Hostility</div>
                                        <div className={`font-bold ${selected.hostility > 50 ? "text-maroon" : "text-text-main"}`}>{selected.hostility}</div>
                                    </div>
                                </div>
                                <div className="text-xs text-text-muted">
                                    <span className="font-bold">Tags:</span> {selected.faction_tags.join(", ")}
                                </div>
                                {selected.grudges.length > 0 && (
                                    <div className="text-xs text-maroon">
                                        <span className="font-bold">⚠ Grudges:</span> {selected.grudges.join(", ")}
                                    </div>
                                )}
                                <div className="text-xs">
                                    <span className="font-bold text-text-muted">Top Traits:</span>
                                    <div className="mt-1 space-y-1">
                                        {Object.entries(selected.top_traits).map(([k, v]) => (
                                            <div key={k} className="flex items-center gap-2">
                                                <span className="text-text-muted w-40 truncate">{k.replace(/_/g, " ")}</span>
                                                <div className="flex-1 bg-border-dark rounded-full h-2 overflow-hidden">
                                                    <div
                                                        className={`h-full rounded-full ${Number(v) > 0 ? "bg-deep-green" : "bg-maroon"}`}
                                                        style={{ width: `${Math.abs(Number(v)) / 2}%`, marginLeft: Number(v) < 0 ? "auto" : undefined }}
                                                    />
                                                </div>
                                                <span className="font-mono text-[10px] w-8 text-right">{v}</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        )}
                    </section>

                    {/* Scandal Injector */}
                    {selectedEntity && (
                        <section className="bg-navy-light rounded-2xl border border-border-dark p-6 space-y-4">
                            <h2 className="text-lg font-bold flex items-center gap-2">
                                <span>💣</span> Inject Scandal
                            </h2>
                            <textarea
                                className="w-full bg-navy border border-border-dark rounded-lg p-3 text-sm outline-none focus:border-maroon resize-none transition"
                                placeholder="Describe the scandal..."
                                rows={2}
                                value={scandalText}
                                onChange={(e) => setScandalText(e.target.value)}
                            />
                            <button
                                onClick={injectScandal}
                                disabled={!scandalText.trim()}
                                className="bg-maroon hover:bg-maroon-hover text-text-main font-bold py-2 px-6 rounded-lg transition text-sm disabled:opacity-50"
                            >
                                💥 Inject Scandal against {selected?.name || "..."}
                            </button>
                        </section>
                    )}

                    {/* Trait Editor */}
                    {selectedEntity && (
                        <section className="bg-navy-light rounded-2xl border border-border-dark p-6 space-y-4">
                            <h2 className="text-lg font-bold flex items-center gap-2">
                                <span>🧬</span> Edit Internal Truth
                            </h2>
                            <div className="flex gap-3">
                                <input
                                    className="flex-1 bg-navy border border-border-dark rounded-lg p-3 text-sm outline-none focus:border-deep-green transition"
                                    placeholder="Trait key (e.g. wawa_vs_sheetz)"
                                    value={traitKey}
                                    onChange={(e) => setTraitKey(e.target.value)}
                                />
                                <div className="flex items-center gap-2">
                                    <input
                                        type="range"
                                        min="-100"
                                        max="100"
                                        value={traitValue}
                                        onChange={(e) => setTraitValue(Number(e.target.value))}
                                        className="w-32"
                                    />
                                    <span className="font-mono text-sm w-10 text-right">{traitValue}</span>
                                </div>
                            </div>
                            <button
                                onClick={editTrait}
                                disabled={!traitKey.trim()}
                                className="bg-deep-green hover:bg-deep-green-hover text-text-main font-bold py-2 px-6 rounded-lg transition text-sm disabled:opacity-50"
                            >
                                ✏️ Apply Trait Change
                            </button>
                        </section>
                    )}
                </div>

                {/* Right Panel: Activity Log + Export */}
                <div className="w-[380px] space-y-6">
                    {/* Activity Log */}
                    <section className="bg-navy-light rounded-2xl border border-border-dark p-4">
                        <h2 className="text-sm font-bold text-text-muted uppercase tracking-widest mb-3 flex items-center gap-2">
                            <span className="w-2 h-2 bg-deep-green rounded-full animate-pulse" />
                            Activity Log
                        </h2>
                        <div className="space-y-1 max-h-[300px] overflow-y-auto">
                            {statusLog.length === 0 && <div className="text-text-muted text-xs">No actions yet.</div>}
                            {statusLog.map((msg, i) => (
                                <div key={i} className="text-[11px] font-mono text-text-muted border-b border-border-dark/50 py-1 last:border-0">
                                    {msg}
                                </div>
                            ))}
                        </div>
                    </section>

                    {/* Export Report */}
                    {exportData && (
                        <section className="bg-navy-light rounded-2xl border border-border-dark p-4 space-y-3">
                            <h2 className="text-sm font-bold text-text-muted uppercase tracking-widest mb-2">📊 State of the City</h2>
                            <div className="grid grid-cols-2 gap-2 text-xs">
                                <div className="bg-navy rounded-lg p-2 text-center">
                                    <div className="text-text-muted">Entities</div>
                                    <div className="font-bold text-lg">{exportData.total_entities}</div>
                                </div>
                                <div className="bg-navy rounded-lg p-2 text-center">
                                    <div className="text-text-muted">Events</div>
                                    <div className="font-bold text-lg">{exportData.total_events}</div>
                                </div>
                                <div className="bg-navy rounded-lg p-2 text-center">
                                    <div className="text-text-muted">Verified</div>
                                    <div className="font-bold text-blue-400">{exportData.verified_accounts}</div>
                                </div>
                                <div className="bg-navy rounded-lg p-2 text-center">
                                    <div className="text-text-muted">API Calls</div>
                                    <div className="font-bold">{exportData.api_usage?.total_requests || 0}</div>
                                </div>
                            </div>

                            {/* Ideology Landscape */}
                            <div>
                                <h3 className="text-xs font-bold text-text-muted mb-2">Top Ideological Traits</h3>
                                <div className="space-y-1">
                                    {Object.entries(exportData.ideology_landscape || {}).slice(0, 8).map(([trait, data]: [string, any]) => (
                                        <div key={trait} className="flex items-center gap-2 text-[10px]">
                                            <span className="w-28 truncate text-text-muted">{trait.replace(/_/g, " ")}</span>
                                            <div className="flex-1 bg-border-dark rounded-full h-1.5 overflow-hidden">
                                                <div
                                                    className={`h-full rounded-full ${data.average_score > 0 ? "bg-deep-green" : "bg-maroon"}`}
                                                    style={{ width: `${Math.min(100, Math.abs(data.average_score))}%` }}
                                                />
                                            </div>
                                            <span className="font-mono w-8 text-right">{data.average_score}</span>
                                            <span className={`w-16 text-right ${data.lean.includes("Left") ? "text-blue-400" : data.lean.includes("Right") ? "text-red-400" : "text-text-muted"}`}>
                                                {data.lean.split("/")[0]}
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {/* Faction Populations */}
                            <div>
                                <h3 className="text-xs font-bold text-text-muted mb-2">Faction Populations</h3>
                                <div className="flex flex-wrap gap-1">
                                    {Object.entries(exportData.faction_populations || {}).map(([fac, count]: [string, any]) => (
                                        <span key={fac} className="text-[9px] bg-border-dark px-2 py-0.5 rounded-full text-text-muted">
                                            {fac}: {count}
                                        </span>
                                    ))}
                                </div>
                            </div>

                            {/* Rising Stars */}
                            {exportData.rising_star_arcs?.length > 0 && (
                                <div>
                                    <h3 className="text-xs font-bold text-text-muted mb-1">⭐ Promoted Stars</h3>
                                    {exportData.rising_star_arcs.map((star: any, i: number) => (
                                        <div key={i} className="text-[10px] text-text-muted">
                                            {star.name} → {star.archetype} ({star.followers} followers)
                                        </div>
                                    ))}
                                </div>
                            )}

                            {/* Download JSON */}
                            <button
                                onClick={() => {
                                    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: "application/json" });
                                    const url = URL.createObjectURL(blob);
                                    const a = document.createElement("a");
                                    a.href = url;
                                    a.download = "twitlife_city_state.json";
                                    a.click();
                                    URL.revokeObjectURL(url);
                                }}
                                className="w-full bg-deep-green hover:bg-deep-green-hover text-text-main font-bold py-2 rounded-lg transition text-xs"
                            >
                                💾 Download Full JSON Report
                            </button>
                        </section>
                    )}
                </div>
            </div>
        </div>
    );
}
