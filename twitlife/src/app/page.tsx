"use client";
import React, { useState, useEffect, useRef, useCallback } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { MessageCircle, Repeat2, Heart, BarChart2, Sparkles, CheckCircle, Home, Search, Bell, Mail, Landmark, User, Zap, MoreHorizontal, X, Image as ImageIcon } from 'lucide-react';


const API = 'http://127.0.0.1:8000';

function stableViews(id: string): number {
  let hash = 0;
  for (let i = 0; i < id.length; i++) { hash = ((hash << 5) - hash) + id.charCodeAt(i); hash |= 0; }
  return Math.abs(hash) % 5000 + 50;
}

function timeAgo(ts: number): string {
  if (!ts) return 'Now';
  const diff = Math.floor(Date.now() / 1000 - ts);
  if (diff < 60) return `${Math.max(1, diff)}s`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h`;
  return `${Math.floor(diff / 86400)}d`;
}

type Identity = { handle: string; name: string; desc: string; profile_image_url?: string; is_verified?: boolean; unlocked_premium_avatars?: boolean };

export default function TwitLife() {
  const router = useRouter();
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [events, setEvents] = useState<any[]>([]);
  const [postContent, setPostContent] = useState("");
  const [identity, setIdentity] = useState<Identity | null>(null);
  const [activeTab, setActiveTab] = useState('Home');
  const [playerAura, setPlayerAura] = useState(1500);
  const [playerCredits, setPlayerCredits] = useState(0);
  const [isDogpiled, setIsDogpiled] = useState(false);
  const [loading, setLoading] = useState(false);
  const [postStatus, setPostStatus] = useState<string | null>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [notifications, setNotifications] = useState<any[]>([]);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [messages, setMessages] = useState<any[]>([]);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [trending, setTrending] = useState<any[]>([]);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [activePulse, setActivePulse] = useState<any>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [neighborhoodFeed, setNeighborhoodFeed] = useState<any[]>([]);
  const [selectedHood, setSelectedHood] = useState<string | null>(null);
  const [hoodDesc, setHoodDesc] = useState("");
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [playerProfile, setPlayerProfile] = useState<any>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [playerVibe, setPlayerVibe] = useState<any[]>([]);
  const [currentDay, setCurrentDay] = useState(1);
  const [lastPaydayDay, setLastPaydayDay] = useState(0);
  const [isAdvancingDay, setIsAdvancingDay] = useState(false);

  // Gamification (Phase 22)
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [quests, setQuests] = useState<any[]>([]);
  const [influenceRank, setInfluenceRank] = useState<number>(1);
  const [achievements, setAchievements] = useState<string[]>([]);

  const [setupHandle, setSetupHandle] = useState("");
  const [setupName, setSetupName] = useState("");
  const [setupDesc, setSetupDesc] = useState("");
  const [feedTab, setFeedTab] = useState<'foryou' | 'following'>('foryou');
  const [hasHydrated, setHasHydrated] = useState(false);
  const [attachMedia, setAttachMedia] = useState(false);

  // Phase 23: Crucible & Cancellation
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [activeEvent, setActiveEvent] = useState<any>(null);
  const [crisisResponse, setCrisisResponse] = useState("");
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [verdictResult, setVerdictResult] = useState<any>(null);

  // Phase 24: Strategy
  const [playerWealth, setPlayerWealth] = useState(0);
  const [playerHeat, setPlayerHeat] = useState(0);
  const [playerAuraPeak, setPlayerAuraPeak] = useState(1500);
  const [playerToxicityFatigue, setPlayerToxicityFatigue] = useState(0);
  const [playerStans, setPlayerStans] = useState(0);
  const [playerNeutrals, setPlayerNeutrals] = useState(0);
  const [playerHaters, setPlayerHaters] = useState(0);
  const [playerAuraDebt, setPlayerAuraDebt] = useState(0);
  const [isGriefingAccount, setIsGriefingAccount] = useState(false);
  const [selectedNiche, setSelectedNiche] = useState("general");
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [nicheKings, setNicheKings] = useState<any[]>([]);
  const [vanguardTab, setVanguardTab] = useState<'global' | 'niche'>('global');
  const [playerNicheRank, setPlayerNicheRank] = useState(0);
  const [playerGlobalRank, setPlayerGlobalRank] = useState(0);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [vanguard, setVanguard] = useState<any[]>([]);
  const [simulationEra, setSimulationEra] = useState("Peace");
  const [isChaosMode, setIsChaosMode] = useState(false);

  useEffect(() => {
    // Phase 25: Support entity_id from URL to override localStorage
    const params = new URLSearchParams(window.location.search);
    const urlEntityId = params.get('entity_id');

    if (urlEntityId) {
      // Don't set identity yet; wait for verifyIdentity to check if profile exists
      verifyIdentity(urlEntityId);
    } else {
      const stored = localStorage.getItem("twitlife_identity");
      if (stored) {
        try { setIdentity(JSON.parse(stored)); } catch { }
      }
    }
    setHasHydrated(true);
  }, []);

  const verifyIdentity = async (handle: string) => {
    try {
      const resp = await fetch(`${API}/api/timeline?entity_id=${handle}`);
      if (resp.ok) {
        setIdentity({ handle, name: handle, desc: "" });
      } else {
        setIdentity(null);
      }
    } catch {
      setIdentity(null);
    }
  };
  const [likedPosts, setLikedPosts] = useState<Set<string>>(new Set());
  const [retweetedPosts, setRetweetedPosts] = useState<Set<string>>(new Set());
  const composeRef = useRef<HTMLTextAreaElement>(null);

  // === ALL HOOKS (preserved from game logic) ===
  useEffect(() => {
    if (!identity) return;

    const fetchTimeline = async () => {
      setLoading(true);
      try {
        const res = await fetch(`${API}/api/timeline?entity_id=${identity.handle}`);
        if (res.status === 404) {
          console.error("Identity not found in backend. Resetting session.");
          localStorage.removeItem("twitlife_identity");
          setIdentity(null);
          return;
        }
        if (!res.ok) throw new Error("Backend unreachable");
        const data = await res.json();
        const timeline = data.timeline || data;
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        setEvents(Array.isArray(timeline) ? timeline.filter((e: any) => e !== null) : []);

        if (data.player_aura !== undefined) setPlayerAura(data.player_aura);
        if (data.simulated_credits !== undefined) setPlayerCredits(data.simulated_credits);
        if (data.player_wealth !== undefined) setPlayerWealth(data.player_wealth);
        if (data.player_heat !== undefined) setPlayerHeat(data.player_heat);
        if (data.is_dogpiled !== undefined) setIsDogpiled(data.is_dogpiled);
        if (data.player_vibe) setPlayerVibe(data.player_vibe);
        if (data.simulation_day !== undefined) setCurrentDay(data.simulation_day);
        if (data.simulation_era) setSimulationEra(data.simulation_era);
        if (data.player_aura_peak !== undefined) setPlayerAuraPeak(data.player_aura_peak);
        if (data.player_toxicity_fatigue !== undefined) setPlayerToxicityFatigue(data.player_toxicity_fatigue);
        if (data.player_stans !== undefined) setPlayerStans(data.player_stans);
        if (data.player_neutrals !== undefined) setPlayerNeutrals(data.player_neutrals);
        if (data.player_haters !== undefined) setPlayerHaters(data.player_haters);
        if (data.player_aura_debt !== undefined) setPlayerAuraDebt(data.player_aura_debt);
        if (data.is_griefing_account !== undefined) setIsGriefingAccount(data.is_griefing_account);
        if (data.last_payday_day !== undefined) setLastPaydayDay(data.last_payday_day);
        if (data.monthly_income_breakdown) {
          setPlayerProfile((prev: any) => ({ ...prev, monthly_income_breakdown: data.monthly_income_breakdown }));
        }
      } catch (e) {
        console.error("Simulation offline or fetch error:", e);
      } finally {
        setLoading(false);
      }
    };

    fetchTimeline();

    const wsUrl = "ws://127.0.0.1:8000/ws/timeline";
    const ws = new WebSocket(wsUrl);
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === "new_event") {
          setEvents(prev => {
            if (prev.some(p => p.id === data.payload.id)) return prev;
            return [data.payload, ...prev];
          });
        }
      } catch (e) {
        console.error("WS parse error", e);
      }
    };
    ws.onerror = (err) => console.error("WS connection error:", err);
    return () => { ws.close(); };
  }, [identity]);

  useEffect(() => {
    if (!identity) return;
    const heartbeat = setInterval(async () => {
      try {
        const r = await fetch(`${API}/api/heartbeat`, { method: 'POST' });
        const data = await r.json();
        if (data.quests) setQuests(data.quests);
        if (data.influence_rank) setInfluenceRank(data.influence_rank);
        if (data.achievements) setAchievements(data.achievements);
        if (data.player_wealth !== undefined) setPlayerWealth(data.player_wealth);
        if (data.player_heat !== undefined) setPlayerHeat(data.player_heat);
        if (data.simulation_era) setSimulationEra(data.simulation_era);
        if (data.player_aura_peak !== undefined) setPlayerAuraPeak(data.player_aura_peak);
        if (data.player_toxicity_fatigue !== undefined) setPlayerToxicityFatigue(data.player_toxicity_fatigue);
        if (data.player_stans !== undefined) setPlayerStans(data.player_stans);
        if (data.player_neutrals !== undefined) setPlayerNeutrals(data.player_neutrals);
        if (data.player_haters !== undefined) setPlayerHaters(data.player_haters);
        if (data.player_aura_debt !== undefined) setPlayerAuraDebt(data.player_aura_debt);
        if (data.is_griefing_account !== undefined) setIsGriefingAccount(data.is_griefing_account);
        if (data.chaos_mode_enabled !== undefined) setIsChaosMode(data.chaos_mode_enabled);
        if (data.last_payday_day !== undefined) setLastPaydayDay(data.last_payday_day);
      } catch { }
    }, 45000);
    return () => { clearInterval(heartbeat); };
  }, [identity]);

  useEffect(() => {
    if (!identity || activeTab !== 'Vanguard') return;
    const fetchLeaderboards = async () => {
      try {
        const r = await fetch(`${API}/api/leaderboards?player_handle=${identity.handle}`);
        const d = await r.json();
        setVanguard(d.global_vanguard || []);
        setNicheKings(d.niche_kings || []);
        setPlayerGlobalRank(d.player_global_rank || 0);
        setPlayerNicheRank(d.player_niche_rank || 0);
        setSelectedNiche(d.player_niche || "general");
      } catch (e) { console.error("Leaderboard fetch failed", e); }
    };
    fetchLeaderboards();
  }, [identity, activeTab]);

  useEffect(() => {
    if (!identity) return;
    const f = async () => { try { const r = await fetch(`${API}/api/trending`); const d = await r.json(); setTrending(d.trending || []); } catch { } };
    f(); const i = setInterval(f, 30000); return () => { clearInterval(i); };
  }, [identity]);

  useEffect(() => {
    if (!identity) return;
    const f = async () => { try { const r = await fetch(`${API}/api/active_pulse`); const d = await r.json(); setActivePulse(d.active_pulse); } catch { } };
    f(); const i = setInterval(f, 15000); return () => { clearInterval(i); };
  }, [identity]);

  useEffect(() => {
    if (!identity || activeTab !== 'Notifications') return;
    const f = async () => { try { const r = await fetch(`${API}/api/notifications?entity_id=${identity.handle}`); const d = await r.json(); setNotifications(d.notifications || []); } catch { } };
    f(); const i = setInterval(f, 10000); return () => { clearInterval(i); };
  }, [identity, activeTab]);

  useEffect(() => {
    if (!identity || activeTab !== 'Messages') return;
    const f = async () => { try { const r = await fetch(`${API}/api/messages?entity_id=${identity.handle}`); const d = await r.json(); setMessages(d.messages || []); } catch { } };
    f(); const i = setInterval(f, 10000); return () => clearInterval(i);
  }, [identity, activeTab]);

  useEffect(() => {
    if (!identity || activeTab !== 'Profile') return;
    const f = async () => { try { const r = await fetch(`${API}/api/profile/${identity.handle}`); const d = await r.json(); setPlayerProfile(d); } catch { } };
    f();
  }, [identity, activeTab]);

  const fetchNeighborhood = useCallback(async (name: string) => {
    setSelectedHood(name); setLoading(true);
    try { const r = await fetch(`${API}/api/neighborhood/${encodeURIComponent(name)}`); const d = await r.json(); setNeighborhoodFeed(d.feed || []); setHoodDesc(d.hub_description || ""); } catch { }
    setLoading(false);
  }, []);

  const getAvatar = (handle: string, faction?: string, isCeleb?: boolean) => {
    // This is now mostly for fallback or onboarding, as the backend provides urls
    const seed = handle?.toLowerCase() || 'default';
    if (seed.startsWith('user') || seed.startsWith('bot_')) {
      const colors = {
        "The Delco Troll": "5e0000",
        "The Main Line Influencer": "ffd700",
        "The Global Doomer": "000080",
        "The Subversive Troll": "FF0000",
        "The Heritage Influencer": "FFD700"
      };
      const bg = colors[faction as keyof typeof colors] || "b6e3f4";
      return `https://api.dicebear.com/7.x/adventurer/svg?seed=${seed}&backgroundColor=${bg}`;
    }
    return `https://unavatar.io/twitter/${seed}`;
  };

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const Avatar = ({ src, handle, aura, auraDebt, isVerified, size = "w-10 h-10", className = "" }: any) => {
    const ringClass = aura > 5000 ? "aura-ring-gold" : auraDebt > 0 ? "aura-ring-red animate-pulse" : "";
    const shapeClass = isVerified ? "hexagon-clip" : "rounded-full";

    return (
      <div className={`relative shrink-0 ${size} ${className}`}>
        {ringClass && <div className={`aura-ring ${ringClass}`} />}
        <img
          src={src || getAvatar(handle)}
          className={`w-full h-full object-cover transition hover:opacity-80 ${shapeClass}`}
          alt=""
        />
      </div>
    );
  };

  // === ACTIONS ===
  const handlePost = async () => {
    if (!postContent.trim()) return;
    const tempMediaUrl = attachMedia ? `https://image.pollinations.ai/prompt/${encodeURIComponent(postContent + " realistic photograph cinematic lighting")}` : null;
    const tempPost = { id: Math.random().toString(), initiator_id: identity?.handle || "player", initiator_name: identity?.name || "Player", content: postContent, timestamp: Date.now() / 1000, likes_count: 0, retweets_count: 0, replies_count: 0, media_url: tempMediaUrl };
    setEvents([tempPost, ...events]);
    setPostContent("");
    setAttachMedia(false);
    setPostStatus("posting");
    try { await fetch(`${API}/api/post_tweet`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ initiator_id: identity?.handle, content: tempPost.content, media_url: tempMediaUrl }) }); setPostStatus("success"); } catch { setPostStatus("error"); }
    setTimeout(() => { setPostStatus(null); }, 3000);
  };

  const handleInteraction = async (eventId: string, type: 'like' | 'retweet') => {
    if (type === 'like') {
      if (likedPosts.has(eventId)) return;
      setLikedPosts(new Set([...likedPosts, eventId]));
    }
    if (type === 'retweet') {
      if (retweetedPosts.has(eventId)) return;
      setRetweetedPosts(new Set([...retweetedPosts, eventId]));
    }
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    setEvents(events.map((ev: any) => {
      if (ev.id === eventId) {
        const newEv = { ...ev };
        if (type === 'like') newEv.likes_count = (newEv.likes_count || 0) + 1;
        if (type === 'retweet') newEv.retweets_count = (newEv.retweets_count || 0) + 1;
        return newEv;
      }
      return ev;
    }));
    try { await fetch(`${API}/api/${type}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ entity_id: identity?.handle || 'player_1', event_id: eventId }) }); } catch { }
  };

  const handleMonetize = async () => {
    try {
      const r = await fetch(`${API}/api/monetize`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ initiator_id: identity?.handle || "player_1" }) });
      const d = await r.json(); if (r.ok) { setPlayerCredits(d.credits); setPlayerAura(d.aura); } else { alert(d.detail || "Failed"); }
    } catch { }
  };

  const handleBuyBots = async () => {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const latestPost = events.find((ev: any) => ev.initiator_id === identity?.handle);
    if (!latestPost) { alert("Post something first!"); return; }
    try {
      const r = await fetch(`${API}/api/buy_bots`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ initiator_id: identity?.handle || "player_1", event_id: latestPost.id }) });
      const d = await r.json(); if (r.ok) { setPlayerCredits(d.credits); alert(`🚨 Swarm Deployed`); } else { alert(d.detail || "Failed"); }
    } catch { }
  };

  const handleAdvanceDay = async () => {
    setIsAdvancingDay(true);
    try {
      const r = await fetch(`${API}/api/advance_day`, { method: 'POST' });
      const d = await r.json();
      if (r.ok) {
        setCurrentDay(d.day || currentDay + 1);
        if (d.daily_event) {
          setActiveEvent(d.daily_event);
        } else {
          setPostStatus('success');
        }
      }
    } catch { }
    setTimeout(() => { setIsAdvancingDay(false); }, 2000); // Fake delay for UX weight
  };

  const submitCrisisResponse = async () => {
    if (!crisisResponse.trim() && activeEvent.type !== 'offline') return;
    setLoading(true);
    try {
      const r = await fetch(`${API}/api/resolve_event`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          player_id: identity?.handle,
          event_id: activeEvent.event_id,
          description: activeEvent.description,
          response: crisisResponse,
          type: activeEvent.type,
          risk_multiplier: activeEvent.risk_multiplier || 1.0
        })
      });
      const res = await r.json();
      setVerdictResult(res);
      // Update aura/followers locally if possible, or wait for heartbeat
      if (res.aura_change) setPlayerAura(prev => prev + res.aura_change);
    } catch { }
    setLoading(false);
  };

  // === DATA ===
  const navItems = [
    { name: 'Home', icon: Home },
    { name: 'Explore', icon: Search },
    { name: 'Vanguard', icon: Sparkles },
    { name: 'Market', icon: Zap },
    { name: 'Notifications', icon: Bell },
    { name: 'Messages', icon: Mail },
    { name: 'Quests', icon: CheckCircle },
    { name: 'Bank', icon: Landmark },
    { name: 'Profile', icon: User },
  ];
  const neighborhoods = [
    { name: 'The Gallery District', emoji: '🎨', vibe: 'Creative & DIY' },
    { name: 'The Industrial Hub', emoji: '🏭', vibe: 'Legacy Industry' },
    { name: 'The Financial Plaza', emoji: '🏛️', vibe: 'Elite Wealth' },
  ];

  const charPercent = Math.min(100, (postContent.length / 280) * 100);
  const charColor = postContent.length > 260 ? '#F4212E' : postContent.length > 240 ? '#FFD400' : '#1D9BF0';

  // === COMPONENTS ===
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const PostCard = ({ post }: { post: any }) => {
    const isLiked = likedPosts.has(post.id);
    const isRetweeted = retweetedPosts.has(post.id);
    return (
      <div className="tweet-hover flex gap-3 px-4 py-3 border-b border-[#2F3336] cursor-pointer animate-fadeIn" onClick={() => { router.push(`/tweet/${post.id}`); }}>
        <Link href={`/profile/${post.initiator_id}`} onClick={e => e.stopPropagation()}>
          <Avatar
            src={post.initiator_profile_image_url}
            handle={post.initiator_id}
            aura={post.initiator_aura}
            auraDebt={post.initiator_aura_debt}
            isVerified={post.is_verified}
          />
        </Link>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-1 text-[15px] leading-5">
            <Link href={`/profile/${post.initiator_id}`} onClick={e => e.stopPropagation()} className="font-bold text-[#E7E9EA] hover:underline truncate">{post.initiator_name || post.initiator_id}</Link>
            {post.is_verified && <CheckCircle className="w-[18px] h-[18px] text-[#1D9BF0] fill-[#1D9BF0] shrink-0" />}
            <span className="text-[#71767B] truncate">@{post.initiator_id}</span>
            <span className="text-[#71767B]">·</span>
            <span className="text-[#71767B] text-sm shrink-0 hover:underline">{timeAgo(post.timestamp)}</span>
            <button onClick={e => { e.stopPropagation(); }} className="ml-auto p-1.5 rounded-full hover:bg-[#1D9BF0]/10 hover:text-[#1D9BF0] text-[#71767B] transition shrink-0">
              <MoreHorizontal className="w-[18px] h-[18px]" />
            </button>
          </div>
          {post.reply_to_id && (
            <p className="text-[13px] text-[#71767B] mt-0.5">Replying to <span className="text-[#1D9BF0] hover:underline cursor-pointer">@{post.initiator_id}</span></p>
          )}
          <p className="text-[#E7E9EA] text-[15px] leading-5 mt-1 whitespace-pre-wrap break-words">{post.content}</p>
          {post.media_url && (
            <div className="mt-3 rounded-2xl overflow-hidden border border-[#2F3336]">
              <img src={post.media_url} className="w-full h-auto max-h-[500px] object-cover" alt="Post attached media" />
            </div>
          )}
          {/* Actions */}
          <div className="flex justify-between items-center mt-3 max-w-[425px] -ml-2">
            <button onClick={e => { e.stopPropagation(); router.push(`/tweet/${post.id}`); }} className="action-reply flex items-center gap-0.5 group text-[#71767B] transition-colors">
              <div className="action-icon p-2 rounded-full transition"><MessageCircle className="w-[18px] h-[18px]" /></div>
              <span className="text-[13px] min-w-[20px]">{post.replies_count || ''}</span>
            </button>
            <button onClick={e => { e.stopPropagation(); handleInteraction(post.id, 'retweet'); }} className={`action-retweet flex items-center gap-0.5 group transition-colors ${isRetweeted ? 'active text-[#00BA7C]' : 'text-[#71767B]'}`}>
              <div className="action-icon p-2 rounded-full transition"><Repeat2 className="w-[18px] h-[18px]" /></div>
              <span className="text-[13px] min-w-[20px]">{post.retweets_count || ''}</span>
            </button>
            <button onClick={e => { e.stopPropagation(); handleInteraction(post.id, 'like'); }} className={`action-like flex items-center gap-0.5 group transition-colors ${isLiked ? 'active text-[#F91880]' : 'text-[#71767B]'}`}>
              <div className="action-icon p-2 rounded-full transition"><Heart className={`w-[18px] h-[18px] ${isLiked ? 'fill-[#F91880] animate-heart' : ''}`} /></div>
              <span className="text-[13px] min-w-[20px]">{post.likes_count || ''}</span>
            </button>
            <button className="action-views flex items-center gap-0.5 group text-[#71767B] transition-colors">
              <div className="action-icon p-2 rounded-full transition"><BarChart2 className="w-[18px] h-[18px]" /></div>
              <span className="text-[13px] min-w-[20px]">{stableViews(post.id)}</span>
            </button>
          </div>
        </div>
      </div>
    );
  };

  const SkeletonPost = () => (
    <div className="flex gap-3 px-4 py-3 border-b border-[#2F3336] animate-pulse">
      <div className="w-10 h-10 rounded-full bg-[#2F3336] shrink-0" />
      <div className="flex-1 space-y-2.5">
        <div className="flex gap-2"><div className="h-3.5 bg-[#2F3336] rounded w-24" /><div className="h-3.5 bg-[#2F3336] rounded w-16" /></div>
        <div className="h-3.5 bg-[#2F3336] rounded w-full" />
        <div className="h-3.5 bg-[#2F3336] rounded w-3/4" />
      </div>
    </div>
  );

  // === ONBOARDING ===
  if (!hasHydrated) return <div className="min-h-screen bg-black" />;

  if (!identity) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center p-4">
        <div className="w-full max-w-[400px] animate-fadeIn">
          <div className="flex justify-center mb-8">
            <Sparkles className="w-10 h-10 text-[#1D9BF0]" />
          </div>
          <h1 className="text-[31px] font-extrabold text-[#E7E9EA] text-center tracking-tight mb-2">Join TwitLife</h1>
          <p className="text-[#71767B] text-[15px] text-center mb-8">Create your account to enter the AI social simulation.</p>
          <div className="space-y-4">
            <div className="relative">
              <input value={setupName} onChange={e => { setSetupName(e.target.value); }} placeholder=" "
                className="peer w-full bg-black border border-[#333639] rounded text-[17px] text-[#E7E9EA] px-3 pt-6 pb-2 outline-none focus:border-[#1D9BF0] focus:ring-1 focus:ring-[#1D9BF0] transition" />
              <label className="absolute left-3 top-2 text-[13px] text-[#71767B] peer-placeholder-shown:top-4 peer-placeholder-shown:text-[17px] peer-focus:top-2 peer-focus:text-[13px] peer-focus:text-[#1D9BF0] transition-all pointer-events-none">Display Name</label>
            </div>
            <div className="relative">
              <input value={setupHandle} onChange={e => { setSetupHandle(e.target.value); }} placeholder=" "
                className="peer w-full bg-black border border-[#333639] rounded text-[17px] text-[#E7E9EA] px-3 pt-6 pb-2 outline-none focus:border-[#1D9BF0] focus:ring-1 focus:ring-[#1D9BF0] transition" />
              <label className="absolute left-3 top-2 text-[13px] text-[#71767B] peer-placeholder-shown:top-4 peer-placeholder-shown:text-[17px] peer-focus:top-2 peer-focus:text-[13px] peer-focus:text-[#1D9BF0] transition-all pointer-events-none">@handle</label>
            </div>
            <p className="text-[12px] text-[#536471] mt-1.5 px-1">This generates your hidden 500-trait personality vector.</p>
          </div>

          {/* Niche Selection (Phase 24.2) */}
          <div className="space-y-3">
            <label className="text-[15px] font-bold text-[#E7E9EA] px-1">Choose Your Niche</label>
            <div className="grid grid-cols-2 gap-2">
              {[
                { id: 'streamer', name: 'Streamer', icon: '📽️', desc: 'MRR Pyramid' },
                { id: 'tech', name: 'Tech & AI', icon: '🤖', desc: 'High wealth' },
                { id: 'gaming', name: 'Console Gaming', icon: '🎮', desc: 'Stan shields' },
                { id: 'artist', name: 'Artist', icon: '🎨', desc: 'Patron MRR' },
                { id: 'music', name: 'Musician', icon: '🎸', desc: 'Streaming rev' },
                { id: 'combat_sports', name: 'Combat Sports', icon: '🥊', desc: 'PPV points' }
              ].map((n) => (
                <button
                  key={n.id}
                  onClick={() => { setSelectedNiche(n.id); }}
                  className={`flex flex-col items-start p-3 rounded-xl border transition ${selectedNiche === n.id ? 'border-[#1D9BF0] bg-[#1D9BF0]/10' : 'border-[#333639] hover:bg-[#1D9BF0]/5'}`}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xl">{n.icon}</span>
                    <span className="text-[14px] font-bold">{n.name}</span>
                  </div>
                  <span className="text-[11px] text-[#71767B]">{n.desc}</span>
                </button>
              ))}
            </div>
          </div>

          <button
            onClick={async () => {
              const handle = setupHandle || 'player_1'; const name = setupName || 'Player';
              try {
                await fetch(`${API}/api/register`, {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({ handle, name, description: setupDesc, primary_niche: selectedNiche })
                });
              } catch { }
              const newIdentity = { handle, name, desc: setupDesc, niche: selectedNiche };
              setIdentity(newIdentity);
              localStorage.setItem("twitlife_identity", JSON.stringify(newIdentity));
            }}
            disabled={!setupName.trim()}
            className="w-full bg-[#E7E9EA] hover:bg-[#D7DBDC] disabled:opacity-40 text-[#0F1419] font-bold text-[17px] py-3 rounded-full mt-4 transition-colors"
          >
            Enter Simulation
          </button>
        </div>
      </div>
    );
  }

  // === MAIN LAYOUT ===
  return (
    <div className="min-h-screen bg-black text-[#E7E9EA] flex justify-center">

      {/* LEFT SIDEBAR */}
      <header className="hidden sm:flex flex-col items-end xl:items-start w-[68px] xl:w-[275px] sticky top-0 h-screen px-2 xl:px-3 py-1">
        <Link href="/" className="p-3 mb-0.5 hover:bg-[#E7E9EA]/10 rounded-full transition w-fit">
          <Sparkles className="w-7 h-7 text-[#E7E9EA]" />
        </Link>
        <nav className="mt-0.5 space-y-0.5 w-full">
          {navItems.map(({ name, icon: Icon }) => (
            <button key={name} onClick={() => { setActiveTab(name); }}
              className={`nav-pill flex items-center gap-5 w-fit xl:pr-6 ${activeTab === name ? 'font-bold' : 'font-normal text-[#E7E9EA]'}`}>
              <Icon className="w-[26px] h-[26px]" strokeWidth={activeTab === name ? 2.5 : 1.5} />
              <span className="hidden xl:inline text-xl">{name}</span>
            </button>
          ))}
        </nav>
        <button onClick={() => { setActiveTab('Home'); setTimeout(() => composeRef.current?.focus(), 100); }}
          className="mt-4 bg-[#1D9BF0] hover:bg-[#1A8CD8] text-white font-bold py-3.5 rounded-full w-12 xl:w-[90%] transition-colors shadow-md text-[17px]">
          <span className="hidden xl:inline">Post</span>
          <span className="xl:hidden text-2xl leading-none">+</span>
        </button>
        <Link href="/admin" className="fixed bottom-4 right-4 bg-maroon-600 w-10 h-10 rounded-full flex items-center justify-center text-white shadow-lg hover:scale-110 transition active:scale-95 z-40">
          <Zap className="w-5 h-5" />
        </Link>
        {/* Mini Profile */}
        <button onClick={() => { setActiveTab('Profile'); }} className="mt-auto mb-3 flex items-center gap-3 p-3 rounded-full hover:bg-[#E7E9EA]/10 transition w-full xl:w-auto">
          <Avatar
            src={playerProfile?.profile_image_url}
            handle={identity.handle}
            aura={playerAura}
            auraDebt={playerAuraDebt}
            isVerified={playerProfile?.is_verified}
          />
          <div className="flex-1 min-w-0 hidden xl:block text-left">
            <p className="font-bold text-[15px] truncate">{identity.name}</p>
            <p className="text-[#71767B] text-[15px] truncate">@{identity.handle}</p>
          </div>
          <MoreHorizontal className="w-5 h-5 text-[#71767B] hidden xl:block shrink-0" />
        </button>
      </header>

      {/* CENTER FEED */}
      <main className="w-full max-w-[600px] border-x border-[#2F3336] min-h-screen">
        {/* World Pulse */}
        {activePulse && (
          <div className="pulse-banner px-4 py-2 flex items-center gap-2 animate-fadeIn">
            <Zap className="w-3.5 h-3.5 text-[#7856FF]" />
            <span className="text-[13px] font-bold text-[#7856FF] uppercase tracking-wider">World Pulse: {activePulse.topic}</span>
          </div>
        )}
        {isChaosMode && (
          <div className="bg-[#7856FF]/10 border-b border-[#7856FF]/30 px-4 py-1.5 text-center">
            <span className="text-[11px] font-black text-[#7856FF] uppercase tracking-[0.2em] flex items-center justify-center gap-2">
              <span className="w-1.5 h-1.5 bg-[#7856FF] rounded-full animate-ping" />
              Chaos Mode Active — Autonomous Network Activity Live
            </span>
          </div>
        )}

        {isDogpiled && (
          <div className="bg-[#F4212E]/10 border-b border-[#F4212E]/30 px-4 py-2 text-center animate-pulse">
            <span className="text-[13px] font-bold text-[#F4212E]">⚠️ You are being dogpiled — incoming hostility detected</span>
          </div>
        )}
        {isGriefingAccount && (
          <div className="bg-[#FFD400]/10 border-b border-[#FFD400]/30 px-4 py-3 text-center animate-pulse">
            <span className="text-[13px] font-black text-[#FFD400] uppercase tracking-wider">⚠️ Labeled as Griefing Account — Aura Ceiling Permanently Capped</span>
            <p className="text-[11px] text-[#FFD400]/70 mt-0.5">Mix in domain-aligned posts to reduce Toxicity Fatigue.</p>
          </div>
        )}

        {/* Sticky Header */}
        <div className="sticky top-0 z-20 sticky-header border-b border-[#2F3336]">
          {activeTab === 'Home' ? (
            <div>
              <div className="flex items-center justify-between px-4 pt-3 pb-0">
                <h1 className="text-xl font-bold">Home</h1>
                <div className="flex items-center gap-3">
                  <span className="text-[#71767B] text-sm font-bold tracking-widest uppercase">Day {currentDay}</span>
                  <button
                    onClick={handleAdvanceDay}
                    disabled={isAdvancingDay}
                    className={`nav-pill text-[14px] font-bold py-1.5 px-4 bg-[#E7E9EA] text-black hover:bg-[#D7DBDC] transition ${isAdvancingDay ? 'opacity-50 cursor-not-allowed' : ''}`}
                  >
                    {isAdvancingDay ? 'Simulating...' : 'Next Day ⏭'}
                  </button>
                </div>
              </div>
              <div className="flex mt-1">
                <button onClick={() => { setFeedTab('foryou'); }} className={`flex-1 py-3 text-[15px] font-bold text-center hover:bg-[#E7E9EA]/10 transition relative ${feedTab === 'foryou' ? 'text-[#E7E9EA] tab-active' : 'text-[#71767B]'}`}>For you</button>
                <button onClick={() => { setFeedTab('following'); }} className={`flex-1 py-3 text-[15px] font-bold text-center hover:bg-[#E7E9EA]/10 transition relative ${feedTab === 'following' ? 'text-[#E7E9EA] tab-active' : 'text-[#71767B]'}`}>Following</button>
              </div>
            </div>
          ) : (
            <div className="px-4 py-3 flex items-center justify-between">
              <h1 className="text-xl font-bold">{activeTab}</h1>
              {activeTab === 'Explore' && selectedHood && (
                <button onClick={() => { setSelectedHood(null); setNeighborhoodFeed([]); }} className="text-[15px] text-[#71767B] hover:text-[#E7E9EA] transition flex items-center gap-1">
                  <X className="w-4 h-4" /> Back
                </button>
              )}
            </div>
          )}
        </div>

        {/* Toast */}
        {
          postStatus && (
            <div className={`text-center text-[13px] py-2 font-bold tracking-wider animate-fadeIn ${postStatus === 'success' ? 'text-[#00BA7C] bg-[#00BA7C]/10' : postStatus === 'error' ? 'text-[#F4212E] bg-[#F4212E]/10' : 'text-[#1D9BF0] bg-[#1D9BF0]/10'}`}>
              {postStatus === 'posting' ? '📡 Transmitting...' : postStatus === 'success' ? '✅ Posted to the simulation' : '❌ Failed to post'}
            </div>
          )
        }

        {/* === HOME TAB === */}
        {
          activeTab === 'Home' && (
            <div>
              {/* Compose */}
              <div className="flex gap-3 px-4 pt-3 pb-2 border-b border-[#2F3336]">
                <Avatar
                  src={playerProfile?.profile_image_url}
                  handle={identity.handle}
                  aura={playerAura}
                  auraDebt={playerAuraDebt}
                  isVerified={playerProfile?.is_verified}
                />
                <div className="flex-1 min-w-0">
                  <textarea ref={composeRef} value={postContent} onChange={e => { setPostContent(e.target.value); }}
                    placeholder="What is happening?!" rows={2}
                    className="w-full bg-transparent text-xl text-[#E7E9EA] outline-none resize-none py-2 placeholder-[#536471] leading-6"
                    onKeyDown={e => { if (e.key === 'Enter' && e.metaKey) handlePost(); }} />
                  <div className="flex items-center justify-between pt-2 border-t border-[#2F3336]">
                    <div className="flex items-center gap-2">
                      <button onClick={() => setAttachMedia(!attachMedia)} className={`p-2 rounded-full hover:bg-[#1D9BF0]/10 transition ${attachMedia ? 'text-[#1D9BF0] bg-[#1D9BF0]/10' : 'text-[#1D9BF0]'}`} title="Generate AI Image">
                        <ImageIcon className="w-5 h-5" />
                      </button>
                      {postContent.length > 0 && (
                        <>
                          <svg className="w-7 h-7" viewBox="0 0 32 32">
                            <circle cx="16" cy="16" r="14" fill="none" stroke="#2F3336" strokeWidth="2" />
                            <circle cx="16" cy="16" r="14" fill="none" stroke={charColor} strokeWidth="2" strokeDasharray={`${charPercent * 0.88} 100`}
                              strokeLinecap="round" transform="rotate(-90 16 16)" className="char-ring" />
                          </svg>
                          <span className={`text-[13px] ${postContent.length > 260 ? 'text-[#F4212E]' : 'text-[#71767B]'}`}>{280 - postContent.length}</span>
                          <div className="w-px h-6 bg-[#2F3336] mx-1" />
                        </>
                      )}
                    </div>
                    <button onClick={handlePost} disabled={!postContent.trim() || postContent.length > 280}
                      className="bg-[#1D9BF0] hover:bg-[#1A8CD8] disabled:opacity-50 text-white font-bold py-1.5 px-5 rounded-full text-[15px] transition-colors">
                      Post
                    </button>
                  </div>
                </div>
              </div>

              {/* Timeline */}
              <div className="pb-20">
                {loading ? (
                  <><SkeletonPost /><SkeletonPost /><SkeletonPost /><SkeletonPost /></>
                ) : events.length === 0 ? (
                  <div className="p-8 text-center bg-[#16181C] m-4 rounded-xl border border-[#2F3336]">
                    <Sparkles className="w-8 h-8 text-[#7856FF] mx-auto mb-3 opacity-50" />
                    <h3 className="text-[#E7E9EA] font-bold">The city is quiet...</h3>
                    <p className="text-[#71767B] text-sm mt-1">Autonomous activity will begin shortly.</p>
                  </div>
                ) : (
                  events.filter(p => !p.reply_to_id || feedTab === 'following').map((post: any) => <PostCard key={post.id} post={post} />)
                )}
              </div>
            </div>
          )
        }

        {/* === NOTIFICATIONS TAB === */}
        {
          activeTab === 'Notifications' && (
            <div className="animate-fadeIn">
              {notifications.length === 0 ? (
                <div className="p-12 text-center"><Bell className="w-10 h-10 mx-auto mb-3 text-[#2F3336]" /><p className="text-xl font-bold text-[#E7E9EA] mb-1">Nothing to see here — yet</p><p className="text-[15px] text-[#71767B]">Likes, reposts, and mentions will show up here.</p></div>
              ) : (
                notifications.map((n: any) => (
                  <div key={n.id} className="tweet-hover flex items-start gap-3 px-4 py-3 border-b border-[#2F3336]">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 mt-0.5 ${n.type === 'like' ? 'text-[#F91880]' : n.type === 'retweet' ? 'text-[#00BA7C]' : 'text-[#1D9BF0]'}`}>
                      {n.type === 'like' ? <Heart className="w-5 h-5 fill-current" /> : n.type === 'retweet' ? <Repeat2 className="w-5 h-5" /> : <MessageCircle className="w-5 h-5" />}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-[15px]"><span className="font-bold">{n.actor_name}</span> <span className="text-[#71767B]">{n.type === 'like' ? 'liked your post' : n.type === 'retweet' ? 'reposted your post' : 'mentioned you'}</span></p>
                      <p className="text-[15px] text-[#71767B] mt-1 line-clamp-2">{n.content}</p>
                    </div>
                  </div>
                ))
              )}
            </div>
          )
        }

        {/* === MESSAGES TAB === */}
        {
          activeTab === 'Messages' && (
            <div className="animate-fadeIn">
              {messages.length === 0 ? (
                <div className="p-12 text-center"><Mail className="w-10 h-10 mx-auto mb-3 text-[#2F3336]" /><p className="text-xl font-bold text-[#E7E9EA] mb-1">Welcome to your inbox</p><p className="text-[15px] text-[#71767B]">DMs appear when NPCs have extreme vibe friction with you.</p></div>
              ) : (
                messages.map((dm: any) => (
                  <div key={dm.id} className={`tweet-hover px-4 py-3 border-b border-[#2F3336] ${dm.is_hate ? 'border-l-2 border-l-[#F4212E]' : ''}`}>
                    <div className="flex items-center gap-2 mb-2">
                      <Avatar src={dm.from_profile_image_url} handle={dm.from_handle} size="w-8 h-8" />
                      <span className="font-bold text-[15px]">@{dm.from_handle}</span>
                      {dm.is_hate && <span className="text-[11px] bg-[#F4212E]/20 text-[#F4212E] px-2 py-0.5 rounded-full font-bold">Flagged</span>}
                      <span className="text-[13px] text-[#71767B] ml-auto">{timeAgo(dm.timestamp)}</span>
                    </div>
                    <p className="text-[15px] text-[#E7E9EA] leading-5">{dm.content}</p>
                  </div>
                ))
              )}
            </div>
          )
        }

        {/* === EXPLORE TAB === */}
        {
          activeTab === 'Explore' && (
            <div className="animate-fadeIn">
              {!selectedHood ? (
                <div className="p-4">
                  <p className="text-[#71767B] text-[15px] mb-4">Select a neighborhood to explore its local feed.</p>
                  <div className="space-y-2">
                    {neighborhoods.map(h => (
                      <button key={h.name} onClick={() => fetchNeighborhood(h.name)}
                        className="game-card w-full p-4 text-left hover:bg-[#E7E9EA]/[0.03] transition group flex items-center gap-4">
                        <span className="text-3xl">{h.emoji}</span>
                        <div><div className="font-bold text-[17px] group-hover:text-[#1D9BF0] transition-colors">{h.name}</div><div className="text-[15px] text-[#71767B]">{h.vibe}</div></div>
                      </button>
                    ))}
                  </div>
                </div>
              ) : (
                <div>
                  <div className="px-4 py-3 border-b border-[#2F3336] bg-[#16181C]/50"><h2 className="font-bold text-[17px]">{selectedHood}</h2><p className="text-[15px] text-[#71767B]">{hoodDesc}</p></div>
                  {loading ? <><SkeletonPost /><SkeletonPost /></> : neighborhoodFeed.length === 0 ? <div className="p-12 text-center text-[#71767B] text-[15px]">No posts in this neighborhood yet.</div> : neighborhoodFeed.map((p: any) => <PostCard key={p.id} post={p} />)}
                </div>
              )}
            </div>
          )
        }

        {/* === QUESTS TAB === */}
        {
          activeTab === 'Quests' && (
            <div className="p-4 animate-fadeIn">
              <div className="mb-6">
                <h2 className="text-[23px] font-extrabold mb-1">Influence Rank: {influenceRank}</h2>
                <div className="w-full bg-[#2F3336] rounded-full h-2.5 mt-2">
                  <div className="bg-gradient-to-r from-[#1D9BF0] to-[#7856FF] h-2.5 rounded-full" style={{ width: `${influenceRank}%` }}></div>
                </div>
              </div>

              <h3 className="text-[19px] font-bold mb-3 border-b border-[#2F3336] pb-2">Daily Quests</h3>
              <div className="space-y-3 mb-8">
                {quests.length === 0 ? <p className="text-[#71767B] text-[15px]">No active quests.</p> : quests.map(q => (
                  <div key={q.id} className="game-card p-4 flex justify-between items-center bg-[#16181C] rounded-xl border border-[#2F3336]">
                    <div>
                      <div className="font-bold text-[15px]">{q.desc}</div>
                      <div className="text-[#1D9BF0] text-[13px] mt-1">Reward: {q.reward} Credits</div>
                    </div>
                    <button className="px-4 py-1.5 border border-[#536471] hover:bg-[#E7E9EA]/10 rounded-full text-[14px] font-bold transition">Claim</button>
                  </div>
                ))}
              </div>

              <h3 className="text-[19px] font-bold mb-3 border-b border-[#2F3336] pb-2">Unlocked Achievements</h3>
              <div className="space-y-2">
                {achievements.length === 0 ? <p className="text-[#71767B] text-[15px]">Keep posting to unlock achievements.</p> : achievements.map(a => (
                  <div key={a} className="flex gap-3 items-center p-3">
                    <div className="w-10 h-10 rounded-full bg-[#FFD400]/20 text-[#FFD400] flex items-center justify-center shrink-0">
                      <Sparkles className="w-5 h-5" />
                    </div>
                    <div>
                      <div className="font-bold text-[15px] capitalize">{a.replace('_', ' ')}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )
        }

        {/* === VANGUARD LEADERBOARD (Phase 24) === */}
        {
          activeTab === 'Vanguard' && (
            <div className="animate-fadeIn">
              <div className="p-4 border-b border-[#2F3336] bg-[#16181C]/50 flex justify-between items-center">
                <div>
                  <h2 className="text-[20px] font-black tracking-tight">The Vanguard</h2>
                  <p className="text-[13px] text-[#71767B] font-medium uppercase tracking-widest italic">Era: {simulationEra}</p>
                </div>
                <Sparkles className="text-[#FFD400] w-5 h-5 animate-pulse" />
              </div>

              {/* Leaderboard Toggle (Phase 24.2) */}
              <div className="flex border-b border-[#2F3336]">
                <button
                  onClick={() => { setVanguardTab('global'); }}
                  className={`flex-1 py-3.5 text-[15px] font-bold hover:bg-[#E7E9EA]/10 transition relative ${vanguardTab === 'global' ? 'text-[#E7E9EA]' : 'text-[#71767B]'}`}
                >
                  Global Top 100
                  {vanguardTab === 'global' && <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-14 h-1 bg-[#1D9BF0] rounded-full" />}
                </button>
                <button
                  onClick={() => { setVanguardTab('niche'); }}
                  className={`flex-1 py-3.5 text-[15px] font-bold hover:bg-[#E7E9EA]/10 transition relative ${vanguardTab === 'niche' ? 'text-[#E7E9EA]' : 'text-[#71767B]'}`}
                >
                  {selectedNiche.replace('_', ' ').toUpperCase()} Kings
                  {vanguardTab === 'niche' && <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-14 h-1 bg-[#1D9BF0] rounded-full" />}
                </button>
              </div>

              {/* Rank Callout */}
              <div className="px-4 py-2 bg-[#1D9BF0]/5 border-b border-[#2F3336] flex justify-between items-center text-[13px]">
                <span className="text-[#71767B]">Your Global Rank: <span className="text-[#E7E9EA] font-bold">#{playerGlobalRank}</span></span>
                <span className="text-[#71767B]">Niche Rank: <span className="text-[#1D9BF0] font-bold">#{playerNicheRank}</span></span>
              </div>

              <div className="divide-y divide-[#2F3336]">
                {(vanguardTab === 'global' ? vanguard : nicheKings).length === 0 ? (
                  <div className="p-12 text-center text-[#71767B]">Ascending the ranks...</div>
                ) : (
                  // eslint-disable-next-line @typescript-eslint/no-explicit-any
                  (vanguardTab === 'global' ? vanguard : nicheKings).map((entry: any, idx: number) => (
                    <div key={idx} className={`flex items-center gap-4 px-4 py-4 hover:bg-[#E7E9EA]/[0.02] transition-colors ${entry.handle === identity?.handle || entry.id === identity?.handle ? 'bg-[#1D9BF0]/5 border-l-2 border-l-[#1D9BF0]' : ''}`}>
                      <div className="w-8 text-center font-black text-[#536471] text-lg">
                        {entry.rank || idx + 1}
                      </div>
                      <Avatar
                        src={entry.profile_image_url}
                        handle={entry.handle || entry.id}
                        aura={entry.aura}
                        auraDebt={0}
                        isVerified={entry.is_verified}
                      />
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-1">
                          <span className="font-bold text-[15px] truncate">{entry.name}</span>
                          <span className="text-[#71767B] text-[14px]">@{entry.handle || entry.id}</span>
                        </div>
                        <div className="text-[12px] text-[#71767B] font-bold uppercase tracking-wider">{entry.niche || entry.faction}</div>
                      </div>
                      <div className="text-right">
                        <div className="text-[15px] font-black text-[#E7E9EA]">{entry.followers.toLocaleString()}</div>
                        <div className={`text-[11px] font-bold ${entry.aura >= 0 ? 'text-[#00BA7C]' : 'text-[#F4212E]'}`}>
                          AURA: {entry.aura >= 0 ? '+' : ''}{entry.aura}
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )
        }

        {/* === SHADOW MARKET (Phase 24) === */}
        {
          activeTab === 'Market' && (
            <div className="p-4 animate-fadeIn">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-[23px] font-extrabold">Shadow Market</h2>
                <div className="bg-[#FFD400]/10 text-[#FFD400] px-3 py-1 rounded-full text-[13px] font-black tracking-widest uppercase">
                  Wealth: {playerWealth}
                </div>
              </div>

              <div className="grid grid-cols-1 gap-4 mb-8">
                <button
                  onClick={() => {
                    fetch(`${API}/api/monetize?player_id=${identity?.handle}`, { method: 'POST' })
                      .then(r => r.json())
                      .then(d => { if (d.status === 'success') { setPlayerWealth(d.wealth); setPlayerAura(d.aura); setPostStatus(d.message); } });
                  }}
                  className="w-full text-left p-5 rounded-2xl border-2 border-dashed border-[#2F3336] hover:border-[#FFD400]/50 hover:bg-[#FFD400]/5 transition group"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-black flex items-center justify-center text-[#FFD400] border border-[#2F3336]">
                      <Landmark className="w-6 h-6" />
                    </div>
                    <div>
                      <div className="font-bold text-lg text-[#E7E9EA] group-hover:text-[#FFD400]">Accept Promoted Post</div>
                      <p className="text-[14px] text-[#71767B]">Earn 250 Wealth. Costs -150 Aura.</p>
                    </div>
                  </div>
                </button>

                {[
                  { id: 'bot_net', name: 'Bot Net', desc: 'Add 5,000 followers instantly.', cost: 500, heat: '+20 Heat' },
                  { id: 'engagement_pod', name: 'Engagement Pod', desc: 'Boost next post viral chances.', cost: 300, heat: '+10 Heat' },
                  { id: 'smear_campaign', name: 'Smear Campaign', desc: 'Tank a rival\'s Aura.', cost: 1000, heat: '+30 Heat' },
                  { id: 'premium_avatar', name: 'Premium Character', desc: 'Unlock clean high-end aesthetics.', cost: 50000, heat: '0 Heat', aura: '+100 Aura' }
                ].map(item => (
                  <button
                    key={item.id}
                    onClick={() => {
                      fetch(`${API}/api/market/buy`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ player_id: identity?.handle, item_id: item.id, target_id: '' })
                      }).then(r => r.json()).then(d => { setPostStatus(d.message); });
                    }}
                    className="game-card w-full p-5 text-left bg-[#16181C] border border-[#2F3336] rounded-2xl hover:border-[#1D9BF0]/50 transition"
                  >
                    <div className="flex justify-between items-start mb-2">
                      <span className="font-black text-xl text-[#E7E9EA]">{item.name}</span>
                      <span className="text-[#FFD400] font-black">{item.cost} Wealth</span>
                    </div>
                    <p className="text-[#71767B] text-[15px] mb-3">{item.desc}</p>
                    <span className="text-[12px] font-black text-[#F4212E] uppercase tracking-widest">{item.heat}</span>
                  </button>
                ))}
              </div>
            </div>
          )
        }

        {/* === BANK TAB === */}
        {
          activeTab === 'Bank' && (
            <div className="p-6 animate-fadeIn">
              <div className="text-center mb-8">
                <h2 className="text-[23px] font-extrabold mb-1">God Mode Bank</h2>
                <p className="text-[15px] text-[#71767B]">Convert Aura into algorithmic influence.</p>
              </div>
              <div className="grid grid-cols-2 gap-3 mb-6">
                <div className="game-card p-5 text-center">
                  <div className="text-[13px] font-bold text-[#71767B] uppercase tracking-wider mb-2">Aura</div>
                  <div className="text-3xl font-extrabold text-[#1D9BF0]">{playerAura.toLocaleString()}</div>
                </div>
                <div className="game-card p-5 text-center">
                  <div className="text-[13px] font-bold text-[#71767B] uppercase tracking-wider mb-2">Credits</div>
                  <div className="text-3xl font-extrabold text-[#FFD400]">₵ {playerCredits}</div>
                </div>
              </div>
              <div className="space-y-3">
                <button onClick={handleMonetize} className="w-full bg-[#1D9BF0] hover:bg-[#1A8CD8] text-white font-bold py-3.5 rounded-full transition-colors text-[15px]">Convert 500 Aura → 50 Credits</button>
                <button onClick={handleBuyBots} className="w-full border border-[#536471] hover:bg-[#E7E9EA]/10 text-[#E7E9EA] font-bold py-3.5 rounded-full transition text-[15px]">Deploy Swarm Attack (100 Credits)</button>
              </div>
            </div>
          )
        }

        {/* === PROFILE TAB === */}
        {
          activeTab === 'Profile' && (
            <div className="animate-fadeIn">
              <div className="h-[200px] bg-gradient-to-br from-[#1D9BF0]/30 via-[#7856FF]/20 to-[#1D9BF0]/30" />
              <div className="px-4 -mt-[68px]">
                <div className="flex justify-between items-end mb-3">
                  <Avatar
                    src={playerProfile?.profile_image_url}
                    handle={identity.handle}
                    aura={playerAura}
                    auraDebt={playerAuraDebt}
                    isVerified={playerProfile?.is_verified}
                    size="w-[134px] h-[134px]"
                    className="border-4 border-black bg-black"
                  />
                  <Link href="/settings" className="px-4 py-1.5 border border-[#536471] rounded-full text-[15px] font-bold text-[#E7E9EA] hover:bg-[#E7E9EA]/10 transition mb-3">Edit profile</Link>
                </div>
                <h2 className="text-xl font-extrabold">{playerProfile?.name || identity.name}</h2>
                <p className="text-[15px] text-[#71767B]">@{identity.handle}</p>
                <p className="text-[15px] mt-3 leading-5">{playerProfile?.bio || identity.desc || "No bio set."}</p>
                <div className="flex gap-5 mt-3 text-[15px] text-[#71767B]">
                  <span><strong className="text-[#E7E9EA]">{playerProfile?.recent_posts?.length || 0}</strong> Posts</span>
                  <span><strong className="text-[#E7E9EA]">{playerProfile?.followers?.toLocaleString() || playerAura.toLocaleString()}</strong> Followers</span>
                </div>

                {/* Tabs */}
                <div className="flex mt-4 border-b border-[#2F3336]">
                  {['Posts', 'Replies', 'Likes'].map(t => (
                    <button key={t} className={`flex-1 py-3 text-[15px] font-bold text-center hover:bg-[#E7E9EA]/10 transition relative ${t === 'Posts' ? 'text-[#E7E9EA] tab-active' : 'text-[#71767B]'}`}>{t}</button>
                  ))}
                </div>

                {/* Vibe Vector */}
                {playerVibe.length > 0 && (
                  <div className="mt-4 mb-6 game-card p-4">
                    <h3 className="text-[13px] font-bold text-[#71767B] uppercase tracking-wider mb-3">Vibe Vector</h3>
                    <div className="space-y-2.5">
                      {playerVibe.map((v: any) => (
                        <div key={v.trait_name} className="flex items-center gap-3">
                          <span className="text-[13px] text-[#71767B] w-32 truncate capitalize">{v.trait_name.replace(/_/g, ' ')}</span>
                          <div className="flex-1 bg-[#2F3336] rounded-full h-1.5 overflow-hidden">
                            <div className={`h-full rounded-full transition-all duration-500 ${v.score > 0 ? 'bg-[#1D9BF0]' : 'bg-[#F91880]'}`}
                              style={{ width: `${Math.min(100, Math.abs(v.score))}%`, marginLeft: v.score < 0 ? 'auto' : undefined }} />
                          </div>
                          <span className="text-[13px] font-mono text-[#71767B] w-8 text-right">{v.score > 0 ? '+' : ''}{v.score.toFixed(0)}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Recent Posts */}
                {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
                {playerProfile?.recent_posts?.map((p: any) => (
                  <div key={p.id} className="tweet-hover px-0 py-3 border-b border-[#2F3336] cursor-pointer" onClick={() => { router.push(`/tweet/${p.id}`); }}>
                    <p className="text-[15px] leading-5">{p.content}</p>
                    <span className="text-[13px] text-[#71767B] mt-1 block">{timeAgo(p.timestamp)}</span>
                  </div>
                ))}
              </div>
            </div>
          )
        }
      </main >

      {/* RIGHT SIDEBAR */}
      < aside className="hidden lg:block w-[350px] pl-7 pr-5 py-2 space-y-4 sticky top-0 h-screen overflow-y-auto" >
        {/* Search */}
        < div className="bg-[#16181C] rounded-full px-4 py-2.5 flex items-center gap-3 border border-transparent focus-within:border-[#1D9BF0] focus-within:bg-black transition-colors mt-1" >
          <Search className="w-[18px] h-[18px] text-[#71767B] shrink-0" />
          <input type="text" placeholder="Search" className="bg-transparent outline-none w-full text-[15px] text-[#E7E9EA] placeholder-[#71767B]" />
        </div >

        {/* Financial Terminal / Supporter Pyramid (Phase 26) */}
        <div className="game-card bg-gradient-to-br from-[#16181C] to-black border-[#2F3336]">
          <div className="px-4 py-3 border-b border-[#2F3336] flex justify-between items-center">
            <h2 className="text-[17px] font-black uppercase tracking-widest text-[#71767B]">Financial Terminal</h2>
            <Landmark className="w-4 h-4 text-[#FFD400]" />
          </div>
          <div className="px-4 py-4 space-y-5">
            <div className="flex justify-between items-end">
              <div>
                <div className="text-[11px] font-bold text-[#71767B] uppercase mb-1">Total Wealth</div>
                <div className="text-3xl font-black text-[#E7E9EA] tracking-tighter">
                  <span className="text-[#FFD400] mr-1">₵</span>
                  {playerWealth.toLocaleString()}
                </div>
              </div>
              <div className="text-right">
                <div className="text-[11px] font-bold text-[#71767B] uppercase mb-1">Aura Rank</div>
                <div className="text-xl font-black text-[#1D9BF0]">{playerAura.toLocaleString()}</div>
              </div>
            </div>

            {/* Supporter Pyramid Breakdown */}
            {playerProfile?.monthly_income_breakdown?.segments && (
              <div className="space-y-2 pt-2 border-t border-[#2F3336]">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-[11px] font-black text-[#71767B] uppercase">Supporter Pyramid</span>
                  <span className="text-[11px] font-bold text-[#00BA7C]">
                    Next Payout: Day {lastPaydayDay + 30}
                  </span>
                </div>
                <div className="space-y-1.5">
                  {Object.entries(playerProfile.monthly_income_breakdown.segments).map(([label, value]: [string, any]) => (
                    <div key={label} className="flex justify-between items-center text-[13px]">
                      <span className="text-[#71767B]">{label}</span>
                      <span className="font-mono font-bold text-[#E7E9EA]">
                        {typeof value === 'number' && (label.includes('Subs') || label.includes('Patrons') || label.includes('Collectors') || label.includes('Whales') || label.includes('Users') || label.includes('Clients') || label.includes('Followers'))
                          ? value.toLocaleString()
                          : value > 1000 ? `$${(value / 1000).toFixed(1)}k` : `$${value}`}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="w-full bg-[#2F3336] h-1 rounded-full overflow-hidden">
              <div className="bg-gradient-to-r from-[#FFD400] to-[#00BA7C] h-full" style={{ width: '45%' }} />
            </div>
          </div>
        </div>

        {/* Heat Meter (Phase 24) */}
        < div className="game-card" >
          <div className="px-4 py-3 border-b border-[#2F3336] flex justify-between items-center">
            <h2 className="text-[17px] font-extrabold text-[#E7E9EA]">Algorithmic Heat</h2>
            <Zap className={`w-4 h-4 ${playerHeat > 50 ? 'text-[#F4212E] animate-pulse' : 'text-[#71767B]'}`} />
          </div>
          <div className="px-4 py-4">
            <div className="w-full bg-[#2F3336] rounded-full h-1.5 mb-2">
              <div
                className={`h-full rounded-full transition-all duration-1000 ${playerHeat > 70 ? 'bg-[#F4212E]' : playerHeat > 40 ? 'bg-[#FFD400]' : 'bg-[#00BA7C]'}`}
                style={{ width: `${playerHeat}%` }}
              />
            </div>
            <div className="flex justify-between items-center text-[12px] font-bold uppercase tracking-wider">
              <span className={playerHeat > 70 ? 'text-[#F4212E]' : playerHeat > 40 ? 'text-[#FFD400]' : 'text-[#71767B]'}>
                {playerHeat > 70 ? 'Critical' : playerHeat > 40 ? 'Elevated' : 'Low Risk'}
              </span>
              <span className="text-[#71767B]">{playerHeat}/100</span>
            </div>
          </div>
        </div >

        {/* Trending */}
        < div className="game-card" >
          <div className="px-4 py-3 border-b border-[#2F3336]">
            <h2 className="text-xl font-extrabold">Trends for you</h2>
          </div>
          {
            trending.length === 0 ? (
              <div className="px-4 py-4 text-[15px] text-[#71767B]">Scanning vibe vectors...</div>
            ) : (
              trending.map((t: any, i: number) => (
                <div key={i} className="trend-item">
                  <div className="text-[13px] text-[#71767B]">Trending Globally</div>
                  <div className="font-bold text-[15px] capitalize">{(t.trait || `Topic ${i + 1}`).replace(/_/g, ' ')}</div>
                  <div className="text-[13px] text-[#71767B]">{t.count || '—'} posts</div>
                </div>
              ))
            )
          }
          <div className="trend-item text-[15px] text-[#1D9BF0]">Show more</div>
        </div >

        {/* Who to follow (NPCs) */}
        < div className="game-card" >
          <div className="px-4 py-3 border-b border-[#2F3336]">
            <h2 className="text-xl font-extrabold">Who to follow</h2>
          </div>
          {
            ['Taylor Swift', 'Cherelle Parker', 'SEPTA'].map(name => {
              const handle = name.replace(/\s/g, '_').toLowerCase();
              return (
                <Link key={name} href={`/profile/${handle}`} className="follow-card">
                  <Avatar handle={handle} isVerified={true} aura={6000} />
                  <div className="flex-1 min-w-0">
                    <div className="font-bold text-[15px] truncate flex items-center gap-1">{name} <CheckCircle className="w-4 h-4 text-[#1D9BF0] fill-[#1D9BF0] shrink-0 inline" /></div>
                    <div className="text-[15px] text-[#71767B] truncate">@{handle}</div>
                  </div>
                  <button className="bg-[#E7E9EA] text-[#0F1419] font-bold text-[15px] px-4 py-1.5 rounded-full hover:bg-[#D7DBDC] transition shrink-0">Follow</button>
                </Link>
              );
            })
          }
          <div className="trend-item text-[15px] text-[#1D9BF0]">Show more</div>
        </div >
      </aside >

      {/* MOBILE BOTTOM NAV */}
      < nav className="sm:hidden fixed bottom-0 left-0 right-0 bg-black/95 backdrop-blur-md border-t border-[#2F3336] flex justify-around py-2 z-50" >
        {
          navItems.slice(0, 5).map(({ name, icon: Icon }) => (
            <button key={name} onClick={() => setActiveTab(name)} className={`p-2.5 rounded-full transition-colors ${activeTab === name ? 'text-[#E7E9EA]' : 'text-[#71767B]'}`}>
              <Icon className="w-[26px] h-[26px]" strokeWidth={activeTab === name ? 2.5 : 1.5} />
            </button>
          ))
        }
      </nav >
      {/* Crucible Modal - Phase 23 */}
      {
        activeEvent && (
          <div className="fixed inset-0 bg-black/90 z-[100] flex items-center justify-center p-4 backdrop-blur-sm animate-fadeIn">
            <div className="bg-[#16181C] border-2 border-[#F4212E] rounded-2xl p-6 max-w-lg w-full shadow-2xl overflow-hidden relative">
              {!verdictResult ? (
                <>
                  <div className="flex items-center gap-2 mb-4">
                    <div className="bg-[#F4212E]/20 text-[#F4212E] px-3 py-1 rounded-full text-[12px] font-black tracking-widest uppercase animate-pulse">
                      Crucible Triggered
                    </div>
                    <span className="text-[#71767B] text-xs font-mono">ID: {activeEvent.event_id}</span>
                  </div>

                  <h2 className="text-[#E7E9EA] text-2xl font-black mb-3 leading-tight tracking-tight">
                    {activeEvent.title}
                  </h2>

                  <p className="text-[#8B98A5] mb-6 font-medium text-[15px] underline-offset-4 decoration-[#F4212E]/30 underline decoration-2">
                    {activeEvent.description}
                  </p>

                  {activeEvent.type === 'offline' ? (
                    <div className="space-y-3">
                      {activeEvent.options.map((opt: any, idx: number) => (
                        <button
                          key={idx}
                          onClick={() => { setCrisisResponse(opt.label); setTimeout(submitCrisisResponse, 100); }}
                          className="w-full text-left p-4 rounded-xl border border-[#2F3336] hover:bg-[#E7E9EA]/5 transition-colors group"
                        >
                          <div className="font-bold text-[#E7E9EA] group-hover:text-[#1D9BF0]">{opt.label}</div>
                        </button>
                      ))}
                    </div>
                  ) : (
                    <>
                      <textarea
                        className="w-full bg-black border border-[#2F3336] rounded-xl p-4 text-[#E7E9EA] focus:border-[#1D9BF0] focus:ring-1 focus:ring-[#1D9BF0] outline-none resize-none mb-4 text-[16px] placeholder-[#536471]"
                        rows={4}
                        placeholder="Type your public response (carefully)..."
                        value={crisisResponse}
                        onChange={(e) => setCrisisResponse(e.target.value)}
                      />

                      <button
                        onClick={submitCrisisResponse}
                        disabled={loading || !crisisResponse.trim()}
                        className="w-full bg-[#E7E9EA] hover:bg-[#D7DBDC] disabled:opacity-40 text-black font-black py-4 rounded-full transition-all active:scale-95 text-[17px] shadow-lg shadow-[#E7E9EA]/10"
                      >
                        {loading ? 'Consulting the Algorithm...' : 'Commit to Life & Post'}
                      </button>
                    </>
                  )}
                </>
              ) : (
                <div className="text-center py-6 animate-fadeIn">
                  <div className="mb-6">
                    <div className={`text-[13px] font-black uppercase tracking-widest mb-1 ${verdictResult.aura_change >= 0 ? 'text-[#00BA7C]' : 'text-[#F4212E]'}`}>
                      {verdictResult.aura_change >= 0 ? 'Verdict: Survived' : 'Verdict: Rationed'}
                    </div>
                    <h2 className="text-[#E7E9EA] text-xl font-bold leading-7">
                      {verdictResult.verdict}
                    </h2>
                  </div>

                  <div className="grid grid-cols-2 gap-4 mb-8">
                    <div className="bg-black/40 p-4 rounded-xl border border-[#2F3336]">
                      <div className="text-[#71767B] text-[11px] font-bold uppercase mb-1">Aura Shift</div>
                      <div className={`text-2xl font-black ${verdictResult.aura_change >= 0 ? 'text-[#00BA7C]' : 'text-[#F4212E]'}`}>
                        {verdictResult.aura_change >= 0 ? '+' : ''}{verdictResult.aura_change}
                      </div>
                    </div>
                    <div className="bg-black/40 p-4 rounded-xl border border-[#2F3336]">
                      <div className="text-[#71767B] text-[11px] font-bold uppercase mb-1">Followers</div>
                      <div className={`text-2xl font-black ${verdictResult.follower_change >= 0 ? 'text-[#00BA7C]' : 'text-[#F4212E]'}`}>
                        {verdictResult.follower_change >= 0 ? '+' : ''}{verdictResult.follower_change}
                      </div>
                    </div>
                  </div>

                  <button
                    onClick={() => { setActiveEvent(null); setVerdictResult(null); setCrisisResponse(""); }}
                    className="w-full border border-[#536471] text-[#E7E9EA] font-bold py-3.5 rounded-full hover:bg-[#E7E9EA]/5 transition"
                  >
                    Return to the Swarm
                  </button>
                </div>
              )}
            </div>
          </div>
        )
      }
    </div >
  );
}
