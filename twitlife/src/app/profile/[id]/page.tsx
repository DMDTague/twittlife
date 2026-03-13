"use client";
import React, { useEffect, useState } from 'react';
import Link from 'next/link';

interface TopicData {
    trait: string;
    value: number;
}

export default function ProfilePage({ params }: { params: { id: string } }) {
    const [user, setUser] = useState<any>(null);

    useEffect(() => {
        fetch(`http://127.0.0.1:8000/api/profile/${params.id}`)
            .then(res => res.json())
            .then(data => setUser(data))
            .catch(e => console.error(e));
    }, [params.id]);

    if (!user) return <div className="min-h-screen bg-navy flex items-center justify-center text-text-muted">Loading God Mode Data...</div>;

    return (
        <div className="min-h-screen bg-navy text-text-main pb-20">
            {/* Banner */}
            <div className="h-40 bg-navy-light border-b border-border-dark" />

            <div className="max-w-2xl mx-auto px-6 -mt-16 bg-navy min-h-screen border-l border-r border-border-dark">
                <div className="flex justify-between items-end">
                    <img
                        src={user.profile_image_url || `https://source.boringavatars.com/beam/120/${user.handle}?colors=maroon,navy,gold`}
                        className="w-32 h-32 rounded-full border-4 border-navy bg-navy-light shadow-2xl"
                        alt="Profile Avatar"
                    />
                    <div className="flex gap-2">
                        <Link href="/" className="px-6 py-2 border border-border-dark rounded-full text-sm font-bold text-text-muted hover:bg-navy-light hidden md:block">
                            Back to Feed
                        </Link>
                        <button className="p-2 border border-border-dark rounded-full hover:bg-navy-light" title="Mute">🔇</button>
                        <button className="bg-white text-black px-6 py-2 rounded-full font-bold hover:bg-gray-200">Follow</button>
                    </div>
                </div>

                <div className="mt-6 border-b border-border-dark pb-6">
                    <h1 className="text-2xl font-black flex items-center gap-2">
                        {user.name}
                        {user.is_verified && <span className="text-blue-400 text-sm">☑</span>}
                    </h1>
                    <p className="text-text-muted">{user.handle}</p>
                    <p className="mt-4 text-text-main leading-relaxed">{user.bio}</p>
                    <div className="flex gap-4 mt-4 text-sm text-text-muted">
                        <span><strong className="text-text-main">1,240</strong> Following</span>
                        <span><strong className="text-text-main">{(user.followers / 1000).toFixed(1)}K</strong> Followers</span>
                    </div>
                </div>

                {/* Exposed Vibe Radar */}
                <div className="mt-8">
                    <h3 className="text-xs font-bold uppercase tracking-widest text-text-muted mb-6">Internal Truth Matrix (God Mode)</h3>

                    <div className="bg-navy-light rounded-2xl border border-border-dark flex flex-col mb-8 overflow-hidden">
                        <div className="p-4">
                            <div className="flex justify-between text-xs text-text-muted mb-2 font-bold uppercase">
                                <span>Core Programming Trait</span>
                                <span>Vector Strength</span>
                            </div>

                            {user.traits_preview.map((vibe: TopicData, index: number) => (
                                <div key={index} className="flex flex-col py-3 border-b border-border-dark last:border-0 relative">
                                    <div className="flex justify-between items-center z-10">
                                        <span className="font-bold text-sm tracking-wide capitalize">{vibe.trait}</span>
                                        <span className="font-mono text-xs">{vibe.value > 0 ? '+' : ''}{(vibe.value).toFixed(1)}</span>
                                    </div>
                                    <div className="absolute bottom-0 left-0 h-1 bg-maroon opacity-50" style={{ width: `${Math.min(Math.abs(vibe.value), 100)}%` }}></div>
                                </div>
                            ))}
                        </div>
                    </div>

                    <h3 className="text-xs font-bold uppercase tracking-widest text-text-muted mb-4">Recent Neural Output</h3>
                    <div className="space-y-4">
                        {user.recent_posts.map((post: any) => (
                            <div key={post.id} className="p-4 bg-navy-light rounded-xl border border-border-dark text-sm">
                                <p>{post.content}</p>
                                <div className="text-[10px] text-text-muted mt-2 text-right">
                                    {new Date(post.timestamp * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                </div>
                            </div>
                        ))}
                        {user.recent_posts.length === 0 && <div className="text-text-muted text-sm pb-10">No recent activity on the database.</div>}
                    </div>

                    {/* Deep Gameplay Stats Card */}
                    <div className="mt-8 mb-10">
                        <h3 className="text-xs font-bold uppercase tracking-widest text-text-muted mb-4">God Mode Analytics</h3>
                        <div className="bg-navy-light rounded-xl border border-border-dark p-4 grid grid-cols-2 gap-4">
                            <div>
                                <div className="text-text-muted text-xs uppercase mb-1">Ratio'd Others</div>
                                <div className="text-xl font-bold font-mono">{user.ratio_count || 0} times</div>
                            </div>
                            <div>
                                <div className="text-text-muted text-xs uppercase mb-1">Grudges Held</div>
                                <div className="text-xl font-bold text-red-500 font-mono">{user.grudges_count || 0} active</div>
                            </div>
                            <div className="col-span-2 mt-2">
                                <div className="flex justify-between text-xs mb-1">
                                    <span className="text-text-muted uppercase">Rising Star Progress</span>
                                    <span className="font-bold">{user.rising_star_progress || 0}%</span>
                                </div>
                                <div className="w-full bg-[#2F3336] rounded-full h-1.5">
                                    <div className="bg-blue-500 h-1.5 rounded-full" style={{ width: `${user.rising_star_progress || 0}%` }}></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
