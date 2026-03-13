"use client";
import React, { useState } from 'react';
import Link from 'next/link';

export default function ProfileEditor() {
    const [description, setDescription] = useState("");
    const [loading, setLoading] = useState(false);
    const [successData, setSuccessData] = useState<any>(null);

    const handleSave = async () => {
        setLoading(true);
        try {
            const res = await fetch("http://127.0.0.1:8000/api/settings", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ description })
            });
            const data = await res.json();
            setSuccessData(data);
        } catch (e) {
            console.error(e);
        }
        setLoading(false);
    };

    return (
        <div className="min-h-screen bg-navy text-text-main py-10">
            <div className="max-w-2xl mx-auto space-y-6 p-8 bg-navy-light rounded-2xl border border-border-dark">
                <div className="flex justify-between items-center mb-6">
                    <h1 className="text-2xl font-black">Digital Soul Editor</h1>
                    <Link href="/" className="text-text-muted hover:text-white text-sm">Back to Feed</Link>
                </div>

                <div>
                    <label className="block text-xs font-bold text-text-muted uppercase mb-2">Profile Picture</label>
                    <div className="flex items-center gap-4">
                        <div className="w-20 h-20 bg-maroon rounded-full border-2 border-border-dark flex items-center justify-center font-bold text-xl">P1</div>
                        <button className="text-sm border border-border-dark px-4 py-2 rounded-lg text-white hover:bg-navy">
                            Upload Custom Photo
                        </button>
                    </div>
                </div>

                <div>
                    <label className="block text-xs font-bold text-text-muted uppercase mb-2">Private AI Description</label>
                    <textarea
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        placeholder="Who are you REALLY? Tell the God Mode AI your secrets... (e.g. 'I am secretly a massive Taylor Swift fan who hates public transit and loves spending money on expensive coffee.')"
                        className="w-full bg-navy border border-border-dark rounded-xl p-4 text-sm text-white h-32 focus:border-maroon outline-none"
                    />
                    <p className="text-[10px] text-text-muted mt-2 italic">
                        *This strict description is ingested by the LLM to hallucinate your hidden 500-trait dichotomy values and auto-generate your public bio.
                    </p>
                </div>

                <button
                    onClick={handleSave}
                    disabled={loading || !description}
                    className="w-full bg-white text-black py-3 rounded-xl font-bold hover:bg-gray-200 disabled:opacity-50"
                >
                    {loading ? "Synthesizing Identity..." : "Compile Soul"}
                </button>

                {successData && (
                    <div className="mt-8 p-4 bg-navy border border-deep-green rounded-xl">
                        <h3 className="text-deep-green font-bold text-sm uppercase mb-2">Identity Generated</h3>
                        <p className="text-sm mb-4"><span className="text-text-muted">Public Bio:</span> {successData.bio}</p>
                        <div className="text-xs bg-navy p-3 font-mono rounded-lg border border-border-dark break-words text-text-muted h-64 overflow-y-auto">
                            {JSON.stringify(successData.top_traits, null, 2)}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
