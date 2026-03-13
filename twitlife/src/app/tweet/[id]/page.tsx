"use client";
import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, MessageCircle, Repeat2, Heart, BarChart2, CheckCircle, MoreHorizontal, Share } from "lucide-react";

const API = "http://127.0.0.1:8000";

function timeAgo(ts: number): string {
    if (!ts) return "Now";
    const diff = Math.floor(Date.now() / 1000 - ts);
    if (diff < 60) return `${Math.max(1, diff)}s`;
    if (diff < 3600) return `${Math.floor(diff / 60)}m`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h`;
    return `${Math.floor(diff / 86400)}d`;
}

function fullDate(ts: number): string {
    if (!ts) return "";
    const d = new Date(ts * 1000);
    return d.toLocaleString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true, month: 'short', day: 'numeric', year: 'numeric' });
}

function stableViews(id: string): number {
    let hash = 0;
    for (let i = 0; i < id.length; i++) { hash = ((hash << 5) - hash) + id.charCodeAt(i); hash |= 0; }
    return Math.abs(hash) % 5000 + 50;
}

const getAvatar = (handle: string) => {
    const seed = handle?.toLowerCase() || "default";
    if (seed.startsWith("user") || seed.startsWith("bot_")) return `https://api.dicebear.com/7.x/bottts/svg?seed=${seed}&backgroundColor=0f172a`;
    return `https://api.dicebear.com/7.x/avataaars/svg?seed=${seed}&backgroundColor=1e293b`;
};

export default function TweetDetail() {
    const params = useParams();
    const router = useRouter();
    const tweetId = params.id as string;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const [tweet, setTweet] = useState<any>(null);
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const [replies, setReplies] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [replyContent, setReplyContent] = useState("");
    const [posting, setPosting] = useState(false);
    const [likedPosts, setLikedPosts] = useState<Set<string>>(new Set());
    const [retweetedPosts, setRetweetedPosts] = useState<Set<string>>(new Set());
    const [identity, setIdentity] = useState<{ handle: string, name: string, desc: string } | null>(null);
    const [hasHydrated, setHasHydrated] = useState(false);

    useEffect(() => {
        const stored = localStorage.getItem("twitlife_identity");
        if (stored) {
            try { setIdentity(JSON.parse(stored)); } catch { }
        }
        setHasHydrated(true);
    }, []);

    const fetchTweet = async () => {
        try {
            const res = await fetch(`${API}/api/tweet/${tweetId}`);
            if (!res.ok) throw new Error("Not found");
            const data = await res.json();
            setTweet(data.tweet);
            setReplies(data.replies || []);
        } catch { console.error("Failed to fetch tweet"); }
        setLoading(false);
    };

    useEffect(() => { fetchTweet(); const i = setInterval(fetchTweet, 8000); return () => clearInterval(i); }, [tweetId]);

    const handleLike = async (eventId: string) => {
        if (likedPosts.has(eventId)) return;
        setLikedPosts(new Set([...likedPosts, eventId]));
        if (tweet?.id === eventId) setTweet({ ...tweet, likes_count: tweet.likes_count + 1 });
        setReplies(replies.map(r => r.id === eventId ? { ...r, likes_count: r.likes_count + 1 } : r));
        try { await fetch(`${API}/api/like`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ entity_id: identity?.handle || "player_1", event_id: eventId }) }); } catch { }
    };

    const handleRetweet = async (eventId: string) => {
        if (retweetedPosts.has(eventId)) return;
        setRetweetedPosts(new Set([...retweetedPosts, eventId]));
        if (tweet?.id === eventId) setTweet({ ...tweet, retweets_count: tweet.retweets_count + 1 });
        setReplies(replies.map(r => r.id === eventId ? { ...r, retweets_count: r.retweets_count + 1 } : r));
        try { await fetch(`${API}/api/retweet`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ entity_id: identity?.handle || "player_1", event_id: eventId }) }); } catch { }
    };

    const handlePostReply = async () => {
        if (!replyContent.trim()) return;
        setPosting(true);
        try {
            await fetch(`${API}/api/post_tweet`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ initiator_id: identity?.handle || "player_1", content: replyContent, reply_to_id: tweetId }) });
            setReplyContent(""); setTimeout(fetchTweet, 1000);
        } catch { }
        setPosting(false);
    };

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const ReplyActions = ({ post }: { post: any }) => {
        const isLiked = likedPosts.has(post.id);
        const isRT = retweetedPosts.has(post.id);
        return (
            <div className="flex justify-between items-center mt-2 max-w-[425px] -ml-2">
                <button onClick={() => { router.push(`/tweet/${post.id}`); }} className="action-reply flex items-center gap-0.5 text-[#71767B] transition-colors">
                    <div className="action-icon p-2 rounded-full transition"><MessageCircle className="w-[18px] h-[18px]" /></div>
                    <span className="text-[13px]">{post.replies_count || ''}</span>
                </button>
                <button onClick={() => handleRetweet(post.id)} className={`action-retweet flex items-center gap-0.5 transition-colors ${isRT ? 'active text-[#00BA7C]' : 'text-[#71767B]'}`}>
                    <div className="action-icon p-2 rounded-full transition"><Repeat2 className="w-[18px] h-[18px]" /></div>
                    <span className="text-[13px]">{post.retweets_count || ''}</span>
                </button>
                <button onClick={() => handleLike(post.id)} className={`action-like flex items-center gap-0.5 transition-colors ${isLiked ? 'active text-[#F91880]' : 'text-[#71767B]'}`}>
                    <div className="action-icon p-2 rounded-full transition"><Heart className={`w-[18px] h-[18px] ${isLiked ? 'fill-[#F91880] animate-heart' : ''}`} /></div>
                    <span className="text-[13px]">{post.likes_count || ''}</span>
                </button>
                <button className="action-views flex items-center gap-0.5 text-[#71767B] transition-colors">
                    <div className="action-icon p-2 rounded-full transition"><BarChart2 className="w-[18px] h-[18px]" /></div>
                    <span className="text-[13px]">{stableViews(post.id)}</span>
                </button>
            </div>
        );
    };

    if (!hasHydrated) return <div className="min-h-screen bg-black" />;

    if (loading) return (
        <div className="min-h-screen bg-black text-[#E7E9EA] flex justify-center">
            <div className="w-full max-w-[600px] border-x border-[#2F3336]">
                <div className="sticky top-0 z-10 sticky-header border-b border-[#2F3336] px-4 py-3 flex items-center gap-6">
                    <button onClick={() => router.back()} className="p-2 -ml-2 rounded-full hover:bg-[#E7E9EA]/10 transition"><ArrowLeft className="w-5 h-5" /></button>
                    <h1 className="text-xl font-bold">Post</h1>
                </div>
                <div className="p-8 text-center text-[#71767B]">Loading...</div>
            </div>
        </div>
    );

    if (!tweet) return (
        <div className="min-h-screen bg-black text-[#E7E9EA] flex justify-center">
            <div className="w-full max-w-[600px] border-x border-[#2F3336]">
                <div className="sticky top-0 z-10 sticky-header border-b border-[#2F3336] px-4 py-3 flex items-center gap-6">
                    <button onClick={() => router.back()} className="p-2 -ml-2 rounded-full hover:bg-[#E7E9EA]/10 transition"><ArrowLeft className="w-5 h-5" /></button>
                    <h1 className="text-xl font-bold">Post</h1>
                </div>
                <div className="p-12 text-center">
                    <p className="text-xl font-bold mb-1">This post doesn&apos;t exist</p>
                    <p className="text-[#71767B] text-[15px]">Try searching for something else.</p>
                </div>
            </div>
        </div>
    );

    const mainLiked = likedPosts.has(tweet.id);
    const mainRT = retweetedPosts.has(tweet.id);

    return (
        <div className="min-h-screen bg-black text-[#E7E9EA] flex justify-center">
            <div className="w-full max-w-[600px] border-x border-[#2F3336]">
                {/* Header */}
                <div className="sticky top-0 z-10 sticky-header border-b border-[#2F3336] px-4 py-3 flex items-center gap-6">
                    <button onClick={() => router.back()} className="p-2 -ml-2 rounded-full hover:bg-[#E7E9EA]/10 transition"><ArrowLeft className="w-5 h-5" /></button>
                    <h1 className="text-xl font-bold">Post</h1>
                </div>

                {/* Main Tweet (expanded) */}
                <article className="px-4 pt-3 border-b border-[#2F3336]">
                    <div className="flex items-center gap-3 mb-3">
                        <Link href={`/profile/${tweet.initiator_id}`}>
                            <img src={getAvatar(tweet.initiator_id)} className="w-10 h-10 rounded-full hover:opacity-80 transition" alt="" />
                        </Link>
                        <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-1">
                                <Link href={`/profile/${tweet.initiator_id}`} className="font-bold text-[15px] hover:underline truncate">{tweet.initiator_name}</Link>
                                {tweet.is_verified && <CheckCircle className="w-[18px] h-[18px] text-[#1D9BF0] fill-[#1D9BF0] shrink-0" />}
                            </div>
                            <span className="text-[15px] text-[#71767B]">@{tweet.initiator_id}</span>
                        </div>
                        <button className="p-2 rounded-full hover:bg-[#1D9BF0]/10 hover:text-[#1D9BF0] text-[#71767B] transition"><MoreHorizontal className="w-5 h-5" /></button>
                    </div>

                    {/* Tweet text — larger in detail view */}
                    <p className="text-[17px] leading-6 whitespace-pre-wrap break-words">{tweet.content}</p>

                    {tweet.media_url && (
                        <div className="mt-4 mb-2 rounded-2xl overflow-hidden border border-[#2F3336]">
                            <img src={tweet.media_url} className="w-full h-auto max-h-[600px] object-cover" alt="Post attached media" />
                        </div>
                    )}

                    {/* Timestamp */}
                    <div className="py-4 text-[15px] text-[#71767B] border-b border-[#2F3336]">
                        {fullDate(tweet.timestamp)}
                    </div>

                    {/* Stats bar */}
                    {(tweet.retweets_count > 0 || tweet.likes_count > 0) && (
                        <div className="py-3 border-b border-[#2F3336] flex gap-5 text-[15px]">
                            {tweet.retweets_count > 0 && <span><strong className="text-[#E7E9EA]">{tweet.retweets_count}</strong> <span className="text-[#71767B]">Reposts</span></span>}
                            {tweet.likes_count > 0 && <span><strong className="text-[#E7E9EA]">{tweet.likes_count}</strong> <span className="text-[#71767B]">Likes</span></span>}
                        </div>
                    )}

                    {/* Action bar */}
                    <div className="flex justify-around py-1 border-b border-[#2F3336]">
                        <button className="action-reply p-2 rounded-full text-[#71767B] transition"><div className="action-icon p-2 rounded-full transition"><MessageCircle className="w-[22px] h-[22px]" /></div></button>
                        <button onClick={() => handleRetweet(tweet.id)} className={`action-retweet p-2 rounded-full transition ${mainRT ? 'active text-[#00BA7C]' : 'text-[#71767B]'}`}><div className="action-icon p-2 rounded-full transition"><Repeat2 className="w-[22px] h-[22px]" /></div></button>
                        <button onClick={() => handleLike(tweet.id)} className={`action-like p-2 rounded-full transition ${mainLiked ? 'active text-[#F91880]' : 'text-[#71767B]'}`}><div className="action-icon p-2 rounded-full transition"><Heart className={`w-[22px] h-[22px] ${mainLiked ? 'fill-[#F91880] animate-heart' : ''}`} /></div></button>
                        <button className="action-views p-2 rounded-full text-[#71767B] transition"><div className="action-icon p-2 rounded-full transition"><BarChart2 className="w-[22px] h-[22px]" /></div></button>
                        <button className="p-2 rounded-full text-[#71767B] hover:text-[#1D9BF0] hover:bg-[#1D9BF0]/10 transition"><div className="p-2 rounded-full transition"><Share className="w-[22px] h-[22px]" /></div></button>
                    </div>
                </article>

                {/* Reply Compose */}
                <div className="flex gap-3 px-4 py-3 border-b border-[#2F3336]">
                    <img src={getAvatar(identity?.handle || "player_1")} className="w-10 h-10 rounded-full shrink-0 mt-1" alt="" />
                    <div className="flex-1">
                        <p className="text-[15px] text-[#71767B] mb-1">Replying to <span className="text-[#1D9BF0]">@{tweet.initiator_id}</span></p>
                        <textarea value={replyContent} onChange={e => { setReplyContent(e.target.value); }} placeholder="Post your reply"
                            className="w-full bg-transparent text-[17px] text-[#E7E9EA] outline-none resize-none py-2 placeholder-[#536471]" rows={2} />
                        <div className="flex justify-end pt-1">
                            <button onClick={handlePostReply} disabled={!replyContent.trim() || posting}
                                className="bg-[#1D9BF0] hover:bg-[#1A8CD8] disabled:opacity-50 text-white font-bold py-1.5 px-5 rounded-full text-[15px] transition-colors">Reply</button>
                        </div>
                    </div>
                </div>

                {/* Replies */}
                <div className="pb-20">
                    {replies.length === 0 ? (
                        <div className="p-12 text-center text-[#71767B] text-[15px]">No replies yet. Be the first to respond!</div>
                    ) : (
                        replies.map(reply => (
                            <div key={reply.id} className="tweet-hover flex gap-3 px-4 py-3 border-b border-[#2F3336] cursor-pointer" onClick={() => { router.push(`/tweet/${reply.id}`); }}>
                                <div className="shrink-0">
                                    <Link href={`/profile/${reply.initiator_id}`} onClick={e => e.stopPropagation()}>
                                        <img src={getAvatar(reply.initiator_id)} className="w-10 h-10 rounded-full hover:opacity-80 transition" alt="" />
                                    </Link>
                                </div>
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-1 text-[15px] leading-5">
                                        <Link href={`/profile/${reply.initiator_id}`} onClick={e => e.stopPropagation()} className="font-bold hover:underline truncate">{reply.initiator_name}</Link>
                                        {reply.is_verified && <CheckCircle className="w-[18px] h-[18px] text-[#1D9BF0] fill-[#1D9BF0] shrink-0" />}
                                        <span className="text-[#71767B] truncate">@{reply.initiator_id}</span>
                                        <span className="text-[#71767B]">·</span>
                                        <span className="text-[#71767B] text-sm shrink-0">{timeAgo(reply.timestamp)}</span>
                                    </div>
                                    <p className="text-[#71767B] text-[13px]">Replying to <span className="text-[#1D9BF0]">@{tweet.initiator_id}</span></p>
                                    <p className="text-[15px] leading-5 mt-1 whitespace-pre-wrap break-words">{reply.content}</p>
                                    {reply.media_url && (
                                        <div className="mt-3 mb-1 rounded-2xl overflow-hidden border border-[#2F3336]">
                                            <img src={reply.media_url} className="w-full h-auto max-h-[500px] object-cover" alt="Attached media" />
                                        </div>
                                    )}
                                    <ReplyActions post={reply} />
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </div>
        </div>
    );
}
