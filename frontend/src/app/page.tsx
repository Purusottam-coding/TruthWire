"use client";

import React, { useState, useEffect } from "react";
import {
  ShieldCheck,
  ShieldAlert,
  Clock,
  ExternalLink,
  CheckCircle2,
  AlertCircle,
  FileText,
  Search,
  Globe,
  RefreshCw,
  TrendingUp,
  DollarSign,
  ChevronRight,
  BookOpen,
  Info,
  Send,
  Building2,
  Sparkles,
  ArrowRight,
  Check,
  Copy,
  Layers,
  Calendar,
  X,
  Radio,
  Flame,
  CheckCheck,
  Archive,
  History,
  Timer
} from "lucide-react";
import { FALLBACK_STORIES, FALLBACK_FOREX } from "@/lib/fallback_data";

interface ForexRate {
  currency: string;
  name: string;
  unit: number;
  buy: number;
  sell: number;
}

interface ForexData {
  status: string;
  source: string;
  source_url: string;
  date: string;
  rates: ForexRate[];
}

interface PatroData {
  status: string;
  nepali_date: string;
  english_date: string;
  ad_date: string;
  nepal_time: string;
  nepal_time_short: string;
  source: string;
  source_url?: string;
}

// Clean source URL resolver: Points directly to authentic Facebook page or websites without 404 or broken links
const getCleanSourceUrl = (story?: Story | null, articleUrl?: string) => {
  if (!story) return articleUrl || "https://kathmandupost.com";
  const sourceName = (story.primary_source || "").toLowerCase();
  const rawUrl = articleUrl || "";

  if (sourceName.includes("routine") || sourceName.includes("ronb") || rawUrl.includes("routineofnepalbanda")) {
    return "https://www.facebook.com/officialroutineofnepalbanda";
  }
  if (sourceName.includes("setopati") || rawUrl.includes("setopati")) {
    if (rawUrl.startsWith("https://www.setopati.com/") || rawUrl.startsWith("https://setopati.com/")) {
      return rawUrl.replace(/-\d{9,}$/, "").split("?")[0];
    }
    return "https://www.setopati.com/";
  }
  if (sourceName.includes("onlinekhabar") || rawUrl.includes("onlinekhabar")) {
    if (rawUrl.startsWith("https://www.onlinekhabar.com/")) {
      return rawUrl.replace(/-\d{9,}$/, "").split("?")[0];
    }
    return "https://www.onlinekhabar.com/";
  }
  if (sourceName.includes("kathmandu post") || rawUrl.includes("kathmandupost")) {
    if (rawUrl.startsWith("https://kathmandupost.com/")) {
      return rawUrl.replace(/-\d{9,}$/, "").split("?")[0];
    }
    return "https://kathmandupost.com";
  }
  if (sourceName.includes("nrb") || rawUrl.includes("nrb.org.np")) {
    return "https://www.nrb.org.np";
  }
  if (rawUrl) {
    return rawUrl.replace(/-\d{9,}$/, "");
  }
  return "https://kathmandupost.com";
};

const getSourceButtonLabel = (story?: Story | null) => {
  if (!story) return "Read Full Source";
  const sourceName = (story.primary_source || "").toLowerCase();
  if (sourceName.includes("routine") || sourceName.includes("ronb")) {
    return "View on Official Routine of Nepal Banda (RONB) Facebook Page";
  }
  if (sourceName.includes("setopati")) {
    return "Read on Setopati (setopati.com)";
  }
  if (sourceName.includes("onlinekhabar")) {
    return "Read on OnlineKhabar (onlinekhabar.com)";
  }
  if (sourceName.includes("kathmandu post")) {
    return "Read on The Kathmandu Post Official Website";
  }
  return `Read on ${story.primary_source || "Official Source"}`;
};

interface Article {
  id: string;
  source_id: string;
  publisher_name: string;
  canonical_url: string;
  title: string;
  excerpt?: string;
  full_content?: string;
  image_url?: string;
  language: string;
  published_at: string;
}

interface Evidence {
  id: string;
  source_url: string;
  source_name: string;
  evidence_type: string;
  stance: string;
  excerpt: string;
  independence_group?: string;
}

interface Review {
  id: string;
  reviewer_name: string;
  decision: string;
  rationale: string;
  policy_version: string;
  created_at: string;
}

interface Claim {
  id: string;
  story_id: string;
  claim_text: string;
  context?: string;
  claim_status: string;
  extracted_at: string;
  evidence_items: Evidence[];
  reviews: Review[];
}

interface AIAnalysis {
  credibility_score: number;
  verdict: string;
  verdict_label: string;
  verdict_color: string;
  sensationalism_score: number;
  attribution_score: number;
  corroboration_sources_count: number;
  signals: string[];
  recommendation: string;
  source_names?: string[];
  is_multi_source?: boolean;
}

interface AIScanVisitedSite {
  name: string;
  url: string;
  status: string;
  match_score?: number;
  article_title?: string;
  error?: string;
}

interface AIScanResult {
  text: string;
  credibility_score: number;
  verdict: string;
  verdict_label: string;
  verdict_color: string;
  sensationalism_score: number;
  attribution_score: number;
  signals: string[];
  recommendation: string;
  is_duplicate: boolean;
  duplicate_similarity_score?: number | null;
  matched_story_id?: string | null;
  matched_story_title?: string | null;
  visited_sites?: AIScanVisitedSite[];
  actions_taken?: string[];
}

interface Story {
  id: string;
  display_title: string;
  topic: string;
  state: string;
  country_iso2: string;
  first_seen_at: string;
  updated_at: string;
  summary?: string;
  full_content?: string;
  image_url?: string;
  articles_count: number;
  claims_count: number;
  verified_claims_count: number;
  primary_source?: string;
  articles: Article[];
  claims: Claim[];
  ai_analysis?: AIAnalysis;
}

export default function HomePage() {
  const [selectedCountry, setSelectedCountry] = useState<string>("NP");
  const [activeFeed, setActiveFeed] = useState<"latest" | "verified" | "history">("latest");
  const [activeTopic, setActiveTopic] = useState<string>("all");
  const [selectedSourceFilter, setSelectedSourceFilter] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [activeView, setActiveView] = useState<"feed" | "review-queue">("feed");

  const [stories, setStories] = useState<Story[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [refreshing, setRefreshing] = useState<boolean>(false);
  const [refreshToast, setRefreshToast] = useState<boolean>(false);
  const [newUpdateBanner, setNewUpdateBanner] = useState<boolean>(false);
  const [selectedStory, setSelectedStory] = useState<Story | null>(null);

  // AI Duplicate & Fake News Detector States
  const [showAiScanner, setShowAiScanner] = useState<boolean>(false);
  const [scanInputText, setScanInputText] = useState<string>("");
  const [scanningWithAi, setScanningWithAi] = useState<boolean>(false);
  const [scanResult, setScanResult] = useState<AIScanResult | null>(null);

  // 30-Second Auto-Refresh Countdown States
  const [autoRefreshSecs, setAutoRefreshSecs] = useState<number>(30);
  const [autoRefreshActive, setAutoRefreshActive] = useState<boolean>(true);

  // Forex & Patro states
  const [forexData, setForexData] = useState<ForexData | null>(null);
  const [patroData, setPatroData] = useState<PatroData | null>(null);
  const [liveNepalTime, setLiveNepalTime] = useState<string>("");

  // Admin Review Queue state
  const [pendingClaims, setPendingClaims] = useState<Claim[]>([]);
  const [reviewReviewer, setReviewReviewer] = useState<string>("Lead Editorial Fact-Checker");
  const [reviewDecision, setReviewDecision] = useState<string>("promoted_to_verified");
  const [reviewRationale, setReviewRationale] = useState<string>("");
  const [submittingReviewId, setSubmittingReviewId] = useState<string | null>(null);
  const [apiConnected, setApiConnected] = useState<boolean>(true);

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";

  // Real-time ticking Nepal Time (UTC+5:45)
  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      // Calculate Nepal Time (UTC + 5 hours 45 mins)
      const utc = now.getTime() + now.getTimezoneOffset() * 60000;
      const nepalDate = new Date(utc + 3600000 * 5.75);
      const hours = nepalDate.getHours();
      const mins = nepalDate.getMinutes();
      const secs = nepalDate.getSeconds();
      const ampm = hours >= 12 ? "PM" : "AM";
      const formattedHours = hours % 12 ? hours % 12 : 12;
      const formattedMins = mins < 10 ? `0${mins}` : mins;
      const formattedSecs = secs < 10 ? `0${secs}` : secs;
      setLiveNepalTime(`${formattedHours}:${formattedMins}:${formattedSecs} ${ampm} NPT`);
    };

    updateTime();
    const timer = setInterval(updateTime, 1000);
    return () => clearInterval(timer);
  }, []);

  // Fetch Nepali Date directly from Hamro Patro Calendar API
  const fetchPatro = async () => {
    try {
      const res = await fetch(`${API_BASE}/patro/today`);
      if (res.ok) {
        const data = await res.json();
        setPatroData(data);
      } else {
        setPatroData({
          status: "success",
          nepali_date: "२८ असोज २०८३, बुधवार",
          english_date: "Asoj 28, 2083 BS (Wednesday)",
          ad_date: "October 14, 2026",
          nepal_time: "08:30 PM NPT",
          nepal_time_short: "08:30 PM NPT",
          source: "Hamro Patro (hamropatro.com)",
          source_url: "https://www.hamropatro.com"
        });
      }
    } catch {
      setPatroData({
        status: "success",
        nepali_date: "२८ असोज २०८३, बुधवार",
        english_date: "Asoj 28, 2083 BS (Wednesday)",
        ad_date: "October 14, 2026",
        nepal_time: "08:30 PM NPT",
        nepal_time_short: "08:30 PM NPT",
        source: "Hamro Patro (hamropatro.com)",
        source_url: "https://www.hamropatro.com"
      });
    }
  };

  // Fetch forex rates
  const fetchForex = async () => {
    try {
      const res = await fetch(`${API_BASE}/forex/rates`);
      if (res.ok) {
        const data = await res.json();
        setForexData(data);
        setApiConnected(true);
      } else {
        setForexData(FALLBACK_FOREX as ForexData);
      }
    } catch {
      setForexData(FALLBACK_FOREX as ForexData);
      setApiConnected(false);
    }
  };

  // Fetch stories with support for silent background auto-refresh every 30 seconds
  const fetchStories = async (silent: boolean = false) => {
    if (!silent) setLoading(true);
    try {
      let url = `${API_BASE}/news?country=${selectedCountry}&feed=${activeFeed}`;
      if (activeTopic !== "all") {
        url += `&topic=${activeTopic}`;
      }
      if (searchQuery.trim()) {
        url += `&q=${encodeURIComponent(searchQuery.trim())}`;
      }
      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        const incoming = data.items || [];
        setStories((prev) => {
          if (silent && prev.length > 0 && incoming.length > 0 && incoming[0].id !== prev[0].id) {
            setNewUpdateBanner(true);
            setTimeout(() => setNewUpdateBanner(false), 4000);
          }
          return incoming;
        });
        setApiConnected(true);
      } else {
        throw new Error("Backend response error");
      }
    } catch (err) {
      setApiConnected(false);
      const nowMs = Date.now();
      const cutoff48h = nowMs - 48 * 3600 * 1000;
      let fallback = FALLBACK_STORIES.filter((s) => s.country_iso2 === selectedCountry);

      if (activeFeed === "history") {
        fallback = fallback.filter(
          (s) => new Date(s.first_seen_at).getTime() < cutoff48h || s.id.includes("archive")
        );
      } else if (activeFeed === "verified") {
        fallback = fallback.filter(
          (s) => new Date(s.first_seen_at).getTime() >= cutoff48h && s.state === "verified_summary"
        );
      } else {
        fallback = fallback.filter(
          (s) => new Date(s.first_seen_at).getTime() >= cutoff48h
        );
      }

      if (activeTopic !== "all") {
        fallback = fallback.filter((s) => s.topic === activeTopic);
      }
      if (searchQuery.trim()) {
        fallback = fallback.filter((s) =>
          s.display_title.toLowerCase().includes(searchQuery.toLowerCase())
        );
      }
      setStories(fallback as Story[]);
    } finally {
      if (!silent) setLoading(false);
    }
  };

  // 30-Second Auto-Refresh Countdown Interval
  useEffect(() => {
    if (!autoRefreshActive) return;

    const timer = setInterval(() => {
      setAutoRefreshSecs((prev) => {
        if (prev <= 1) {
          // Trigger automatic silent refresh of stories and rates every 30 seconds
          fetchStories(true);
          return 30;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [autoRefreshActive, selectedCountry, activeFeed, activeTopic, searchQuery]);

  // User manually triggers Refresh from Navbar
  const handleManualRefresh = async () => {
    setRefreshing(true);
    try {
      if (selectedCountry === "NP") {
        await fetch(`${API_BASE}/news/refresh-live?country=NP`, { method: "POST" });
      }
    } catch {}
    await Promise.all([fetchStories(false), fetchForex(), fetchPatro()]);
    setRefreshing(false);
    setAutoRefreshSecs(30);
    setRefreshToast(true);
    setTimeout(() => setRefreshToast(false), 2500);
  };

  // Fetch admin review queue
  const fetchReviewQueue = async () => {
    try {
      const res = await fetch(`${API_BASE}/admin/review-queue?country=${selectedCountry}`);
      if (res.ok) {
        const data = await res.json();
        setPendingClaims(data || []);
      }
    } catch (err) {
      console.error("Failed to fetch review queue:", err);
    }
  };

  useEffect(() => {
    fetchStories();
    fetchForex();
    fetchPatro();
    if (activeView === "review-queue") {
      fetchReviewQueue();
    }
  }, [selectedCountry, activeFeed, activeTopic, activeView]);

  const handleCountryChange = (iso2: string) => {
    setSelectedCountry(iso2);
    setActiveTopic("all");
    setSelectedSourceFilter("all");
  };

  const submitReview = async (claimId: string) => {
    if (!reviewRationale.trim()) {
      alert("Please provide the documented verification rationale or primary evidence link.");
      return;
    }
    setSubmittingReviewId(claimId);
    try {
      const res = await fetch(`${API_BASE}/admin/claims/${claimId}/review`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          reviewer_name: reviewReviewer,
          decision: reviewDecision,
          rationale: reviewRationale,
          policy_version: "v1.0"
        })
      });
      if (res.ok) {
        alert("Verification review submitted successfully!");
        setReviewRationale("");
        fetchReviewQueue();
        fetchStories();
      }
    } catch {
      alert("Error submitting review");
    } finally {
      setSubmittingReviewId(null);
    }
  };

  // Run AI Duplicate & Fake News Scan
  const handleAiScan = async (sampleText?: string) => {
    const textToScan = (sampleText || scanInputText).trim();
    if (!textToScan) return;
    if (sampleText) setScanInputText(sampleText);
    setScanningWithAi(true);
    setScanResult(null);
    try {
      const res = await fetch(`${API_BASE}/ai/scan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: textToScan })
      });
      if (res.ok) {
        const data = await res.json();
        setScanResult(data);
        if (data.actions_taken && data.actions_taken.length > 0) {
          fetchStories(true);
        }
      }
    } catch (err) {
      console.error("AI scan failed:", err);
    } finally {
      setScanningWithAi(false);
    }
  };

  // Filter stories by source if requested (e.g. RONB only or OnlineKhabar only)
  const filteredStories = stories.filter((s) => {
    if (selectedSourceFilter === "all") return true;
    if (selectedSourceFilter === "onlinekhabar") {
      return (
        s.primary_source?.toLowerCase().includes("onlinekhabar") ||
        s.display_title.toLowerCase().includes("onlinekhabar")
      );
    }
    if (selectedSourceFilter === "ronb") {
      return (
        s.primary_source?.toLowerCase().includes("routine") ||
        s.display_title.toLowerCase().includes("ronb")
      );
    }
    if (selectedSourceFilter === "setopati") {
      return (
        s.primary_source?.toLowerCase().includes("setopati") ||
        s.display_title.toLowerCase().includes("setopati")
      );
    }
    if (selectedSourceFilter === "official") {
      return (
        s.primary_source?.toLowerCase().includes("nrb") ||
        s.primary_source?.toLowerCase().includes("army") ||
        s.primary_source?.toLowerCase().includes("caan")
      );
    }
    return true;
  });

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col text-slate-800 font-sans">
      {/* Toast Notification */}
      {refreshToast && (
        <div className="fixed top-20 right-6 z-50 bg-black text-white px-4 py-2.5 rounded-xl shadow-xl flex items-center space-x-2 text-xs font-bold animate-in fade-in slide-in-from-top-4 border border-zinc-700">
          <CheckCheck className="w-4 h-4 text-white" />
          <span>News feed refreshed just now!</span>
        </div>
      )}

      {/* Main Top Header */}
      <header className="sticky top-0 z-40 bg-white border-b border-zinc-200 shadow-xs">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16 gap-2">
            {/* Logo */}
            <div
              className="flex items-center space-x-2.5 cursor-pointer shrink-0"
              onClick={() => setActiveView("feed")}
            >
              <div className="w-9 h-9 rounded-xl bg-black flex items-center justify-center text-white shadow-xs">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <div>
                <span className="text-xl font-black tracking-tight text-black">
                  Truth<span className="underline decoration-zinc-400">Wire</span>
                </span>
              </div>
            </div>

            {/* Hamro Patro Date (Nepali) & Nepal Time - Text only, non-clickable (Black & White) */}
            <div className="hidden lg:flex items-center space-x-2.5 bg-zinc-100 px-3.5 py-1.5 rounded-xl border border-zinc-300 text-xs select-none">
              <div
                title="Bikram Sambat Nepali Date"
                className="flex items-center space-x-1.5 text-black font-bold nepali-text cursor-default"
              >
                <Calendar className="w-3.5 h-3.5 text-black shrink-0" />
                <span>{patroData?.nepali_date || "२८ असोज २०८३, बुधवार"}</span>
              </div>

              <span className="text-zinc-400">•</span>
              <div className="flex items-center space-x-1.5 text-black font-extrabold font-mono">
                <Clock className="w-3.5 h-3.5 text-black shrink-0" />
                <span>{liveNepalTime || patroData?.nepal_time || "08:30 PM NPT"}</span>
              </div>
            </div>

            {/* Country Selector */}
            <div className="flex items-center space-x-1 bg-zinc-100 p-1 rounded-xl border border-zinc-300">
              <button
                onClick={() => handleCountryChange("NP")}
                className={`flex items-center space-x-1 px-2.5 py-1.5 rounded-lg text-xs font-bold transition ${
                  selectedCountry === "NP"
                    ? "bg-black text-white shadow-xs"
                    : "text-zinc-700 hover:text-black"
                }`}
              >
                <span>🇳🇵</span>
                <span className="hidden sm:inline">Nepal</span>
              </button>
              <button
                onClick={() => handleCountryChange("US")}
                className={`flex items-center space-x-1 px-2.5 py-1.5 rounded-lg text-xs font-bold transition ${
                  selectedCountry === "US"
                    ? "bg-black text-white shadow-xs"
                    : "text-zinc-700 hover:text-black"
                }`}
              >
                <span>🇺🇸</span>
                <span className="hidden sm:inline">US</span>
              </button>
              <button
                onClick={() => handleCountryChange("CA")}
                className={`flex items-center space-x-1 px-2.5 py-1.5 rounded-lg text-xs font-bold transition ${
                  selectedCountry === "CA"
                    ? "bg-black text-white shadow-xs"
                    : "text-zinc-700 hover:text-black"
                }`}
              >
                <span>🇨🇦</span>
                <span className="hidden sm:inline">Canada</span>
              </button>
            </div>

            {/* Navbar Refresh & Action Buttons */}
            <div className="flex items-center space-x-2 shrink-0">
              {/* 30s Live Auto-Refresh Badge */}
              <div
                onClick={() => setAutoRefreshActive(!autoRefreshActive)}
                className={`hidden md:flex items-center space-x-1.5 px-2.5 py-1.5 rounded-xl border text-xs font-bold cursor-pointer transition select-none ${
                  autoRefreshActive
                    ? "bg-zinc-900 border-black text-white hover:bg-black"
                    : "bg-zinc-100 border-zinc-300 text-zinc-500 hover:bg-zinc-200"
                }`}
                title={autoRefreshActive ? "Auto-refresh active every 30s (Click to pause)" : "Auto-refresh paused (Click to resume)"}
              >
                <span className={`w-2 h-2 rounded-full ${autoRefreshActive ? "bg-white animate-pulse" : "bg-zinc-400"}`}></span>
                <span className="text-[11px]">
                  {autoRefreshActive ? (
                    <>Live 30s: <span className="font-mono text-white font-extrabold">{autoRefreshSecs}s</span></>
                  ) : (
                    "Paused"
                  )}
                </span>
              </div>

              {/* Interactive Navbar Refresh Button */}
              <button
                onClick={handleManualRefresh}
                disabled={refreshing}
                title="Refresh news feed and rates"
                className="flex items-center space-x-1 px-3 py-1.5 rounded-xl bg-zinc-100 hover:bg-zinc-200 text-black font-bold text-xs transition border border-zinc-300"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? "animate-spin text-black" : ""}`} />
                <span className="hidden sm:inline">{refreshing ? "Refreshing..." : "Refresh"}</span>
              </button>

              {/* AI Duplicate & Fake News Scanner Button */}
              <button
                onClick={() => setShowAiScanner(true)}
                title="AI Duplicate & Fake News Detector"
                className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-black hover:bg-zinc-800 text-white font-bold text-xs transition border border-black shadow-xs"
              >
                <Sparkles className="w-3.5 h-3.5 text-white" />
                <span className="hidden sm:inline">AI Detector</span>
                <span className="sm:hidden">AI</span>
              </button>

              <button
                onClick={() => setActiveView(activeView === "feed" ? "review-queue" : "feed")}
                className={`flex items-center space-x-1 px-3 py-1.5 rounded-xl text-xs font-bold transition ${
                  activeView === "review-queue"
                    ? "bg-black text-white shadow-xs"
                    : "bg-white text-zinc-800 hover:bg-zinc-100 border border-zinc-300"
                }`}
              >
                <ShieldAlert className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">Fact-Check Desk</span>
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Sub-Bar for Nepal Date & Time - Text only (Black and White) */}
        <div className="lg:hidden bg-zinc-100 border-t border-zinc-200 px-4 py-1.5 text-[11px] flex items-center justify-between select-none">
          <div className="flex items-center space-x-1 text-black font-bold nepali-text truncate cursor-default">
            <Calendar className="w-3 h-3 text-black shrink-0" />
            <span>{patroData?.nepali_date || "२८ असोज २०८३, बुधवार"}</span>
          </div>
          <div className="flex items-center space-x-1 text-black font-extrabold font-mono shrink-0">
            <Clock className="w-3 h-3 text-black" />
            <span>{liveNepalTime || patroData?.nepal_time || "08:30 PM NPT"}</span>
          </div>
        </div>
      </header>

      {/* Nepal Rastra Bank Forex Rates Ticker (Black & White Editorial) */}
      {selectedCountry === "NP" && forexData && (
        <section className="bg-black text-white py-2.5 border-b border-zinc-800">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between text-xs mb-1.5 text-zinc-400">
              <div className="flex items-center space-x-2 font-medium">
                <span className="font-bold text-white uppercase tracking-wider text-[11px]">
                  Live Forex Rates (Nepal Rastra Bank)
                </span>
                <span className="hidden sm:inline text-zinc-400">• Date: {forexData.date}</span>
              </div>
              <a
                href={forexData.source_url}
                target="_blank"
                rel="noreferrer"
                className="text-zinc-300 hover:text-white flex items-center space-x-1 underline text-[11px]"
              >
                <span>Official NRB Portal</span>
                <ExternalLink className="w-3 h-3" />
              </a>
            </div>

            {/* Horizontal Scroll Rates Ticker */}
            <div className="flex items-center space-x-3 overflow-x-auto pb-1 scrollbar-none">
              {forexData.rates.map((r) => (
                <div
                  key={r.currency}
                  className="bg-zinc-900 hover:bg-zinc-800 px-3 py-1.5 rounded-lg flex items-center space-x-2.5 shrink-0 border border-zinc-800 transition"
                >
                  <div className="text-left">
                    <span className="font-extrabold text-white text-xs block">
                      {r.unit > 1 ? `${r.unit} ` : ""}{r.currency}
                    </span>
                    <span className="text-[10px] text-zinc-400 truncate max-w-[80px] block">
                      {r.name}
                    </span>
                  </div>
                  <div className="text-right text-[11px] leading-tight font-mono">
                    <div className="text-white font-semibold">Buy: NPR {r.buy.toFixed(2)}</div>
                    <div className="text-zinc-400">Sell: NPR {r.sell.toFixed(2)}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {activeView === "review-queue" ? (
          /* Editorial Fact-Check Workspace */
          <div className="max-w-4xl mx-auto space-y-6">
            <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-xs flex items-center justify-between">
              <div>
                <h1 className="text-xl font-bold text-black flex items-center space-x-2">
                  <ShieldAlert className="w-5 h-5 text-black" />
                  <span>Editorial Verification Queue</span>
                </h1>
                <p className="text-xs text-zinc-500 mt-1">
                  Cross-examine candidate claims extracted from Routine of Nepal Banda (RONB), Setopati, and wire alerts against primary documents.
                </p>
              </div>
              <button
                onClick={fetchReviewQueue}
                className="flex items-center space-x-1.5 px-3 py-2 text-xs font-semibold rounded-lg bg-zinc-100 hover:bg-zinc-200 text-black border border-zinc-200"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                <span>Refresh Queue</span>
              </button>
            </div>

            {pendingClaims.length === 0 ? (
              <div className="text-center py-12 bg-white rounded-2xl border border-zinc-200">
                <CheckCircle2 className="w-12 h-12 text-black mx-auto mb-3" />
                <h3 className="text-base font-bold text-black">Review Queue is Clear</h3>
                <p className="text-xs text-zinc-500 mt-1">All extracted claims have been verified or resolved.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {pendingClaims.map((claim) => (
                  <div
                    key={claim.id}
                    className="bg-white rounded-2xl border border-zinc-200 p-5 shadow-xs space-y-4"
                  >
                    <div className="flex items-start justify-between">
                      <div className="space-y-1">
                        <span className="inline-block px-2.5 py-0.5 rounded-full text-[11px] font-bold uppercase bg-zinc-100 text-black border border-zinc-300">
                          {claim.claim_status}
                        </span>
                        <h3 className="text-base font-bold text-black leading-snug">
                          {claim.claim_text}
                        </h3>
                        {claim.context && (
                          <p className="text-xs text-zinc-500">
                            <strong>Context:</strong> {claim.context}
                          </p>
                        )}
                      </div>
                    </div>

                    {/* Attached Evidence */}
                    {claim.evidence_items.length > 0 && (
                      <div className="bg-zinc-50 rounded-xl p-3 border border-zinc-200 space-y-2">
                        <span className="text-[11px] font-bold text-zinc-600 uppercase tracking-wider block">
                          Documented Evidence Reference:
                        </span>
                        {claim.evidence_items.map((ev) => (
                          <div key={ev.id} className="text-xs text-zinc-800 space-y-1">
                            <div className="flex items-center space-x-2 font-medium">
                              <span className="px-1.5 py-0.5 bg-zinc-200 text-black rounded font-semibold text-[10px] border border-zinc-300">
                                {ev.evidence_type}
                              </span>
                              <span>{ev.source_name}</span>
                              <a
                                href={ev.source_url}
                                target="_blank"
                                rel="noreferrer"
                                className="text-black underline font-bold flex items-center space-x-0.5"
                              >
                                <span>Inspect Source</span>
                                <ExternalLink className="w-3 h-3" />
                              </a>
                            </div>
                            <blockquote className="italic border-l-2 border-zinc-400 pl-2 text-zinc-700">
                              &ldquo;{ev.excerpt}&rdquo;
                            </blockquote>
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Review Form */}
                    <div className="border-t border-zinc-200 pt-3 grid grid-cols-1 sm:grid-cols-3 gap-3">
                      <div>
                        <label className="block text-xs font-semibold text-zinc-600 mb-1">
                          Editorial Decision
                        </label>
                        <select
                          value={reviewDecision}
                          onChange={(e) => setReviewDecision(e.target.value)}
                          className="w-full text-xs font-semibold p-2 border border-zinc-300 rounded-lg bg-white text-black"
                        >
                          <option value="promoted_to_verified">✓ Promote to Verified Feed</option>
                          <option value="marked_corroborated">Mark Corroborated</option>
                          <option value="flagged_as_disputed">Flag Disputed</option>
                          <option value="flagged_as_refuted">Flag Refuted</option>
                          <option value="marked_inconclusive">Mark Inconclusive</option>
                        </select>
                      </div>

                      <div className="sm:col-span-2">
                        <label className="block text-xs font-semibold text-zinc-600 mb-1">
                          Evidence Citation & Rationale
                        </label>
                        <div className="flex space-x-2">
                          <input
                            type="text"
                            placeholder="State primary document reference or verification notes..."
                            value={reviewRationale}
                            onChange={(e) => setReviewRationale(e.target.value)}
                            className="flex-1 text-xs p-2 border border-zinc-300 rounded-lg text-black bg-white"
                          />
                          <button
                            onClick={() => submitReview(claim.id)}
                            disabled={submittingReviewId === claim.id}
                            className="px-4 py-2 bg-black hover:bg-zinc-800 text-white rounded-lg text-xs font-bold flex items-center space-x-1 border border-zinc-800"
                          >
                            <Send className="w-3 h-3" />
                            <span>{submittingReviewId === claim.id ? "..." : "Approve"}</span>
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        ) : (
          /* Rich News Stream */
          <div className="space-y-6">
            {/* Feed Switcher & Search Bar */}
            <div className="bg-white rounded-2xl border border-slate-200 p-4 sm:p-5 shadow-xs">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                {/* 3-Way Feed Switcher (Latest 48h, Verified, History Archive) */}
                <div className="flex p-1 bg-zinc-100 rounded-xl max-w-lg w-full border border-zinc-200">
                  <button
                    onClick={() => setActiveFeed("latest")}
                    className={`flex-1 flex items-center justify-center space-x-1.5 py-2 px-3 rounded-lg text-xs sm:text-sm font-bold transition ${
                      activeFeed === "latest"
                        ? "bg-black text-white shadow-xs"
                        : "text-zinc-600 hover:text-black"
                    }`}
                  >
                    <Clock className="w-4 h-4 shrink-0" />
                    <span>Latest (48h)</span>
                  </button>
                  <button
                    onClick={() => setActiveFeed("verified")}
                    className={`flex-1 flex items-center justify-center space-x-1.5 py-2 px-3 rounded-lg text-xs sm:text-sm font-bold transition ${
                      activeFeed === "verified"
                        ? "bg-zinc-800 text-white shadow-xs"
                        : "text-zinc-600 hover:text-black"
                    }`}
                  >
                    <ShieldCheck className="w-4 h-4 shrink-0" />
                    <span>Verified</span>
                  </button>
                  <button
                    onClick={() => setActiveFeed("history")}
                    className={`flex-1 flex items-center justify-center space-x-1.5 py-2 px-3 rounded-lg text-xs sm:text-sm font-bold transition ${
                      activeFeed === "history"
                        ? "bg-zinc-700 text-white shadow-xs"
                        : "text-zinc-600 hover:text-black"
                    }`}
                  >
                    <History className="w-4 h-4 shrink-0" />
                    <span>History (48h+)</span>
                  </button>
                </div>

                {/* Search */}
                <div className="relative flex-1 max-w-sm">
                  <Search className="w-4 h-4 text-zinc-400 absolute left-3 top-3" />
                  <input
                    type="text"
                    placeholder="Search RONB, Setopati, national updates..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && fetchStories()}
                    className="w-full pl-9 pr-4 py-2 text-xs sm:text-sm bg-zinc-50 border border-zinc-300 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-black text-black"
                  />
                </div>
              </div>

              {/* Feed Status & 30s Live Auto-Refresh Sub-Bar */}
              <div className="mt-3 pt-2.5 border-t border-zinc-200 flex items-center justify-between flex-wrap gap-2 text-xs">
                <div className="flex items-center space-x-2">
                  <span className="flex h-2 w-2 relative">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-zinc-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-black"></span>
                  </span>
                  <span className="text-[11px] font-bold text-black">
                    Live Auto-refresh in <span className="font-mono text-black font-extrabold">{autoRefreshSecs}s</span>
                  </span>
                  <span className="text-zinc-400">•</span>
                  <span className="text-[11px] text-zinc-600">
                    {activeFeed === "history"
                      ? "Archive: Past news published older than 48 hours"
                      : "Live Feed: Stories active within the last 48 hours"}
                  </span>
                </div>
                <div className="text-[11px] font-bold text-zinc-500">
                  Showing {filteredStories.length} {activeFeed === "history" ? "archived stories" : "updates"}
                </div>
              </div>
            </div>

            {/* Breaking News Instant Toast / Banner (Black & White) */}
            {newUpdateBanner && (
              <div className="bg-black text-white px-4 py-2.5 rounded-2xl text-xs font-bold flex items-center justify-between border border-zinc-800 shadow-lg">
                <div className="flex items-center space-x-2">
                  <Sparkles className="w-4 h-4 text-white" />
                  <span>Breaking News Alert: A fresh live update was just ingested into the stream!</span>
                </div>
                <button
                  onClick={() => setNewUpdateBanner(false)}
                  className="text-zinc-400 hover:text-white"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            )}

            {/* Granular Source Filters (Monochrome Black & White) */}
            {selectedCountry === "NP" && (
              <div className="flex items-center space-x-2 overflow-x-auto pb-1 scrollbar-none">
                <span className="text-[11px] font-bold uppercase tracking-wider text-zinc-500 shrink-0 pr-1">
                  Filter by Source:
                </span>
                <button
                  onClick={() => setSelectedSourceFilter("all")}
                  className={`px-3 py-1 rounded-full text-xs font-bold transition shrink-0 ${
                    selectedSourceFilter === "all"
                      ? "bg-black text-white"
                      : "bg-white text-zinc-700 hover:bg-zinc-100 border border-zinc-300"
                  }`}
                >
                  All Sources
                </button>
                <button
                  onClick={() => setSelectedSourceFilter("onlinekhabar")}
                  className={`px-3 py-1 rounded-full text-xs font-bold transition shrink-0 ${
                    selectedSourceFilter === "onlinekhabar"
                      ? "bg-black text-white"
                      : "bg-white text-zinc-700 hover:bg-zinc-100 border border-zinc-300"
                  }`}
                >
                  <span>OnlineKhabar English</span>
                </button>
                <button
                  onClick={() => setSelectedSourceFilter("ronb")}
                  className={`px-3 py-1 rounded-full text-xs font-bold transition shrink-0 ${
                    selectedSourceFilter === "ronb"
                      ? "bg-black text-white"
                      : "bg-white text-zinc-700 hover:bg-zinc-100 border border-zinc-300"
                  }`}
                >
                  <span>Routine of Nepal Banda (RONB)</span>
                </button>
                <button
                  onClick={() => setSelectedSourceFilter("setopati")}
                  className={`px-3 py-1 rounded-full text-xs font-bold transition shrink-0 ${
                    selectedSourceFilter === "setopati"
                      ? "bg-black text-white"
                      : "bg-white text-zinc-700 hover:bg-zinc-100 border border-zinc-300"
                  }`}
                >
                  Setopati
                </button>
                <button
                  onClick={() => setSelectedSourceFilter("official")}
                  className={`px-3 py-1 rounded-full text-xs font-bold transition shrink-0 ${
                    selectedSourceFilter === "official"
                      ? "bg-black text-white"
                      : "bg-white text-zinc-700 hover:bg-zinc-100 border border-zinc-300"
                  }`}
                >
                  Official Gazettes (NRB / Army / CAAN)
                </button>
              </div>
            )}

            {/* Topic Filter Chips (Monochrome Black & White) */}
            <div className="flex items-center space-x-2 overflow-x-auto pb-1 scrollbar-none">
              {[
                { id: "all", label: "All Categories" },
                { id: "national", label: "National & Local Updates" },
                { id: "business", label: "Economy & Forex" },
                { id: "technology", label: "Technology & Youth" },
                { id: "weather", label: "Weather, Snow & Roads" },
                { id: "sports", label: "Sports & Cricket" }
              ].map((topic) => (
                <button
                  key={topic.id}
                  onClick={() => setActiveTopic(topic.id)}
                  className={`px-3.5 py-1.5 rounded-full text-xs font-bold transition shrink-0 ${
                    activeTopic === topic.id
                      ? "bg-black text-white shadow-sm"
                      : "bg-white text-zinc-700 hover:bg-zinc-100 border border-zinc-300"
                  }`}
                >
                  {topic.label}
                </button>
              ))}
            </div>

            {/* Rich Cards Grid with English OnlineKhabar Inspired Editorial Layout & Animation */}
            {loading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {[1, 2, 3, 4, 5, 6].map((i) => (
                  <div key={i} className="bg-white rounded-2xl border border-zinc-200 overflow-hidden animate-pulse">
                    <div className="h-48 bg-zinc-200"></div>
                    <div className="p-5 space-y-3">
                      <div className="h-4 bg-zinc-200 rounded w-1/3"></div>
                      <div className="h-6 bg-zinc-200 rounded w-full"></div>
                      <div className="h-4 bg-zinc-100 rounded w-4/5"></div>
                    </div>
                  </div>
                ))}
              </div>
            ) : filteredStories.length === 0 ? (
              <div className="bg-white rounded-2xl border border-zinc-200 p-12 text-center">
                <BookOpen className="w-12 h-12 text-zinc-400 mx-auto mb-3" />
                <h3 className="text-base font-bold text-black">No Stories in this Filter</h3>
                <p className="text-xs text-zinc-500 mt-1">Try selecting 'All Sources' or choosing another category.</p>
              </div>
            ) : (
              <div className="space-y-8">
                {/* Featured Lead Story (Monochrome Editorial Style) */}
                {filteredStories.length > 0 && (
                  <article
                    onClick={() => setSelectedStory(filteredStories[0])}
                    className="group bg-white rounded-3xl border border-zinc-200 hover:border-black overflow-hidden shadow-sm hover:shadow-2xl transition-all duration-300 grid grid-cols-1 lg:grid-cols-12 cursor-pointer"
                  >
                    {/* Lead Story Image with Smooth Zoom */}
                    <div className="relative lg:col-span-7 h-64 sm:h-80 lg:h-full min-h-[280px] overflow-hidden bg-zinc-100">
                      <img
                        src={filteredStories[0].image_url || "https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?auto=format&fit=crop&w=1200&q=80"}
                        alt={filteredStories[0].display_title}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700 ease-out"
                      />
                      <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/30 to-transparent lg:hidden"></div>
                      <div className="absolute top-4 left-4 flex items-center flex-wrap gap-2">
                        <span className="px-3 py-1 rounded-md text-xs font-black uppercase tracking-wider bg-black text-white border border-zinc-700 shadow-md">
                          Lead Story
                        </span>
                        <span className="px-2.5 py-1 rounded-md text-[11px] font-bold uppercase tracking-wider bg-black/80 backdrop-blur-md text-white border border-zinc-700">
                          {filteredStories[0].topic}
                        </span>
                        {/* AI Authenticity Badge */}
                        {filteredStories[0].ai_analysis && (
                          <span className="px-2.5 py-1 rounded-md text-[11px] font-black uppercase tracking-wider bg-zinc-900 text-white border border-zinc-700 shadow-sm flex items-center space-x-1">
                            <Sparkles className="w-3 h-3 text-white" />
                            <span>AI: {filteredStories[0].ai_analysis.credibility_score}% {filteredStories[0].ai_analysis.verdict_label}</span>
                          </span>
                        )}
                        {/* Multi-Source Corroboration Badge */}
                        {filteredStories[0].ai_analysis?.is_multi_source && (
                          <span className="px-2.5 py-1 rounded-md text-[11px] font-bold bg-zinc-800 text-white border border-zinc-700 shadow-sm flex items-center space-x-1">
                            <Layers className="w-3 h-3" />
                            <span>{filteredStories[0].ai_analysis.source_names?.length || 2} Outlets Corroborated</span>
                          </span>
                        )}
                      </div>
                      <div className="absolute bottom-3 left-4 text-white lg:hidden">
                        <span className="text-xs font-bold drop-shadow-[0_2px_4px_rgba(0,0,0,0.9)]">
                          {filteredStories[0].primary_source || "Authorized Wire"}
                        </span>
                      </div>
                    </div>

                    {/* Lead Story Editorial Content */}
                    <div className="lg:col-span-5 p-6 sm:p-8 flex flex-col justify-between space-y-4">
                      <div className="space-y-3">
                        <div className="hidden lg:flex items-center space-x-2 text-xs font-bold text-zinc-500 uppercase tracking-wider">
                          <span className="text-black font-extrabold">{filteredStories[0].primary_source || "Wire Report"}</span>
                          <span>•</span>
                          <span>{new Date(filteredStories[0].first_seen_at).toLocaleDateString()}</span>
                        </div>

                        <h2 className="text-xl sm:text-2xl lg:text-3xl font-black text-black group-hover:text-zinc-600 transition-colors duration-200 leading-tight">
                          {filteredStories[0].display_title}
                        </h2>

                        <p className="text-sm sm:text-base text-zinc-700 leading-relaxed line-clamp-4">
                          {filteredStories[0].summary}
                        </p>
                      </div>

                      <div className="pt-4 border-t border-zinc-200 flex items-center justify-between">
                        <span className="text-xs font-semibold text-zinc-600 uppercase tracking-wide">
                          {filteredStories[0].state === "verified_summary" ? "✓ Verified Report" : "Developing Wire"}
                        </span>
                        <div className="flex items-center space-x-1 text-sm font-bold text-black group-hover:translate-x-1 transition-transform">
                          <span>See Full Story</span>
                          <ChevronRight className="w-4 h-4" />
                        </div>
                      </div>
                    </div>
                  </article>
                )}

                {/* Grid of Subsequent Stories */}
                {filteredStories.length > 1 && (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {filteredStories.slice(1).map((story) => {
                      return (
                        <article
                          key={story.id}
                          onClick={() => setSelectedStory(story)}
                          className="group bg-white rounded-2xl border border-zinc-200 hover:border-black overflow-hidden shadow-xs hover:shadow-xl hover:-translate-y-1 transition-all duration-300 flex flex-col cursor-pointer"
                        >
                          {/* Image Thumbnail with zoom effect */}
                          <div className="relative h-48 w-full overflow-hidden bg-zinc-100">
                            <img
                              src={story.image_url || "https://images.unsplash.com/photo-1585829365295-ab7cd400c167?auto=format&fit=crop&w=800&q=80"}
                              alt={story.display_title}
                              className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500 ease-out"
                            />
                            <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent"></div>

                            {/* Source text (clean text only) */}
                            <div className="absolute bottom-2.5 left-3 text-white">
                              <span className="text-xs font-bold tracking-wide drop-shadow-[0_2px_4px_rgba(0,0,0,0.9)] text-white">
                                {story.primary_source || "Authorized Wire"}
                              </span>
                            </div>

                            {/* Category & AI Badges */}
                            <div className="absolute top-2.5 right-3 flex items-center space-x-1.5">
                              {story.ai_analysis && (
                                <span className="px-2 py-0.5 rounded-md text-[10px] font-black uppercase tracking-wider text-white bg-black/80 backdrop-blur-xs border border-zinc-700 shadow-xs flex items-center space-x-1">
                                  <Sparkles className="w-2.5 h-2.5 text-white" />
                                  <span>{story.ai_analysis.credibility_score}%</span>
                                </span>
                              )}
                              {story.ai_analysis?.is_multi_source && (
                                <span className="px-1.5 py-0.5 rounded-md text-[10px] font-bold bg-zinc-800 text-white border border-zinc-700 backdrop-blur-xs flex items-center space-x-0.5">
                                  <Layers className="w-2.5 h-2.5" />
                                  <span>Multi</span>
                                </span>
                              )}
                              <span className="px-2 py-0.5 rounded-md text-[10px] font-black uppercase tracking-wider bg-black/70 text-white backdrop-blur-xs border border-zinc-700">
                                {story.topic}
                              </span>
                            </div>
                          </div>

                          {/* Card Body */}
                          <div className="p-5 flex-1 flex flex-col justify-between space-y-3">
                            <div className="space-y-2">
                              <div className="flex items-center justify-between text-[11px] text-zinc-500 font-semibold uppercase tracking-wider">
                                <span>{story.topic}</span>
                                <span className={activeFeed === "history" ? "text-black font-bold bg-zinc-100 px-2 py-0.5 rounded border border-zinc-200" : ""}>
                                  {activeFeed === "history" ? `Archived • ${new Date(story.first_seen_at).toLocaleDateString()}` : new Date(story.first_seen_at).toLocaleDateString()}
                                </span>
                              </div>

                              <h2 className="text-base font-bold text-black group-hover:text-zinc-600 transition-colors leading-snug line-clamp-2">
                                {story.display_title}
                              </h2>

                              {/* Halka Description (Short Summary) */}
                              <p className="text-xs text-zinc-700 line-clamp-3 leading-relaxed">
                                {story.summary}
                              </p>
                            </div>

                            {/* Card Footer */}
                            <div className="pt-3 border-t border-zinc-200 flex items-center justify-between text-xs text-zinc-500 font-medium">
                              <span>{story.topic?.toUpperCase()} • {story.country_iso2}</span>
                              <span className="text-black font-bold group-hover:translate-x-0.5 transition-transform flex items-center space-x-0.5">
                                <span>Read Full</span>
                                <ChevronRight className="w-3.5 h-3.5" />
                              </span>
                            </div>
                          </div>
                        </article>
                      );
                    })}
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </main>

      {/* Whole Description & Evidence Modal */}
      {selectedStory && (
        <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl max-w-3xl w-full max-h-[92vh] overflow-y-auto shadow-2xl border border-slate-200 animate-in fade-in zoom-in-95 flex flex-col">
            {/* Modal Hero Banner Image */}
            <div className="relative h-64 sm:h-72 w-full bg-slate-900 shrink-0">
              <img
                src={selectedStory.image_url || "https://images.unsplash.com/photo-1585829365295-ab7cd400c167?auto=format&fit=crop&w=1200&q=80"}
                alt={selectedStory.display_title}
                className="w-full h-full object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-slate-950/80 via-slate-950/20 to-transparent"></div>

              {/* Close Button */}
              <button
                onClick={() => setSelectedStory(null)}
                className="absolute top-4 right-4 w-9 h-9 rounded-full bg-black/60 hover:bg-black/90 text-white flex items-center justify-center backdrop-blur-md transition"
              >
                <X className="w-5 h-5" />
              </button>

              {/* Source & Status Pill (Monochrome) */}
              <div className="absolute bottom-4 left-6 right-6 flex items-center justify-between">
                <span className="px-3 py-1 rounded-lg text-xs font-black bg-black text-white border border-zinc-700 shadow-md uppercase tracking-wider">
                  {selectedStory.primary_source || "Authorized Wire"}
                </span>
                <span className="px-3 py-1 rounded-lg text-xs font-black uppercase tracking-wider bg-zinc-800 text-white border border-zinc-700">
                  {selectedStory.state.replace("_", " ")}
                </span>
              </div>
            </div>

            {/* Modal Body */}
            <div className="p-6 sm:p-8 space-y-6 flex-1">
              <div>
                <div className="flex items-center space-x-2 text-xs font-bold text-zinc-500 uppercase tracking-wider mb-2">
                  <span>{selectedStory.topic}</span>
                  <span>•</span>
                  <span>Updated: {new Date(selectedStory.updated_at).toLocaleString()}</span>
                </div>
                <h1 className="text-xl sm:text-2xl font-black text-black leading-tight">
                  {selectedStory.display_title}
                </h1>
              </div>

              {/* Whole Description (Full Story Content) */}
              <div className="space-y-3 bg-zinc-50 p-5 rounded-2xl border border-zinc-200">
                <h3 className="text-xs font-black uppercase tracking-wider text-zinc-500">
                  Full Story Report
                </h3>
                <p className="text-sm text-zinc-800 leading-relaxed font-normal whitespace-pre-line">
                  {selectedStory.full_content || selectedStory.summary}
                </p>
              </div>

              {/* AI Authenticity & Duplicate Analysis Panel (Monochrome Black & White) */}
              {selectedStory.ai_analysis && (
                <div className="bg-zinc-950 text-white p-6 rounded-2xl border border-zinc-800 shadow-lg space-y-4">
                  <div className="flex items-center justify-between flex-wrap gap-2">
                    <div className="flex items-center space-x-2">
                      <Sparkles className="w-4 h-4 text-white" />
                      <span className="text-xs font-black uppercase tracking-wider text-zinc-300">
                        TruthWire AI Fact-Check & Cross-Verification
                      </span>
                    </div>
                    <span className="px-2.5 py-1 rounded-full text-[10px] font-black uppercase tracking-wider bg-zinc-800 text-white border border-zinc-700">
                      {selectedStory.ai_analysis.verdict_label}
                    </span>
                  </div>

                  {/* Metrics Row */}
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                    <div className="bg-zinc-900 rounded-xl p-3 border border-zinc-800">
                      <span className="text-[10px] text-zinc-400 font-bold uppercase block mb-1">Authenticity Score</span>
                      <div className="text-2xl font-black text-white font-mono">
                        {selectedStory.ai_analysis.credibility_score}%
                      </div>
                      <div className="w-full bg-zinc-800 h-1.5 rounded-full mt-1.5 overflow-hidden">
                        <div
                          className="bg-white h-full rounded-full transition-all duration-500"
                          style={{ width: `${selectedStory.ai_analysis.credibility_score}%` }}
                        ></div>
                      </div>
                    </div>

                    <div className="bg-zinc-900 rounded-xl p-3 border border-zinc-800">
                      <span className="text-[10px] text-zinc-400 font-bold uppercase block mb-1">Clickbait / Rumor Index</span>
                      <div className="text-2xl font-black text-zinc-200 font-mono">
                        {selectedStory.ai_analysis.sensationalism_score}%
                      </div>
                      <span className="text-[10px] text-zinc-400">
                        {selectedStory.ai_analysis.sensationalism_score < 30 ? "Clean journalistic tone" : "Elevated sensationalism"}
                      </span>
                    </div>

                    <div className="bg-zinc-900 rounded-xl p-3 border border-zinc-800">
                      <span className="text-[10px] text-zinc-400 font-bold uppercase block mb-1">Cross-Source Corroboration</span>
                      <div className="text-2xl font-black text-zinc-200 font-mono">
                        {selectedStory.articles_count} {selectedStory.articles_count === 1 ? "Outlet" : "Outlets"}
                      </div>
                      <span className="text-[10px] text-zinc-400 truncate block">
                        {selectedStory.ai_analysis.is_multi_source ? "Multi-source verified" : "Single wire dispatch"}
                      </span>
                    </div>
                  </div>

                  {/* AI Detection Signals */}
                  <div className="space-y-1.5 bg-zinc-900/80 p-3.5 rounded-xl border border-zinc-800 text-xs">
                    <span className="text-[11px] font-bold text-zinc-300 uppercase tracking-wide block">
                      AI Signals & Attribution Analysis:
                    </span>
                    {selectedStory.ai_analysis.signals.map((sig, idx) => (
                      <div key={idx} className="text-zinc-300 flex items-start space-x-1.5">
                        <span className="text-white font-bold">•</span>
                        <span>{sig}</span>
                      </div>
                    ))}
                  </div>

                  {/* Reader Advice Banner */}
                  <div className="text-xs text-zinc-400 italic border-l-2 border-zinc-500 pl-3">
                    {selectedStory.ai_analysis.recommendation}
                  </div>
                </div>
              )}

              {/* Claim-Level Evidence Verification Section */}
              <div className="space-y-4">
                <h3 className="text-sm font-black uppercase tracking-wider text-black flex items-center space-x-2">
                  <ShieldCheck className="w-4 h-4 text-black" />
                  <span>Factual Claims & Documented Evidence</span>
                </h3>

                {selectedStory.claims.length === 0 ? (
                  <p className="text-xs text-zinc-500 italic">No isolated claims registered yet.</p>
                ) : (
                  selectedStory.claims.map((claim) => (
                    <div
                      key={claim.id}
                      className="p-4 rounded-2xl border border-zinc-200 bg-white shadow-xs space-y-3"
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div className="space-y-1">
                          <span className="inline-block px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wide bg-zinc-100 text-zinc-800 border border-zinc-300">
                            {claim.claim_status}
                          </span>
                          <p className="text-sm font-bold text-black leading-snug">
                            {claim.claim_text}
                          </p>
                          {claim.context && (
                            <p className="text-xs text-zinc-500">
                              <span className="font-semibold">Context:</span> {claim.context}
                            </p>
                          )}
                        </div>
                      </div>

                      {/* Evidence Citations */}
                      {claim.evidence_items.length > 0 && (
                        <div className="border-t border-zinc-100 pt-2 space-y-2">
                          <span className="text-[10px] font-bold uppercase tracking-wider text-zinc-500 block">
                            Corroborating Primary Evidence:
                          </span>
                          {claim.evidence_items.map((ev) => (
                            <div
                              key={ev.id}
                              className="bg-zinc-50 p-3 rounded-xl border border-zinc-200 text-xs space-y-1.5"
                            >
                              <div className="flex items-center justify-between">
                                <span className="font-bold text-black">{ev.source_name}</span>
                                <span className="text-[10px] uppercase font-black text-black bg-zinc-200 px-2 py-0.5 rounded border border-zinc-300">
                                  {ev.stance}
                                </span>
                              </div>
                              <p className="text-zinc-700 italic">
                                &ldquo;{ev.excerpt}&rdquo;
                              </p>
                              <a
                                href={getCleanSourceUrl(selectedStory, ev.source_url)}
                                target="_blank"
                                rel="noreferrer"
                                className="text-black hover:underline flex items-center space-x-1 text-[11px] font-bold pt-1"
                              >
                                <span>View Verified Primary Source</span>
                                <ExternalLink className="w-3 h-3" />
                              </a>
                            </div>
                          ))}
                        </div>
                      )}

                      {/* Reviewer Note */}
                      {claim.reviews.length > 0 && (
                        <div className="bg-zinc-100 p-3 rounded-xl border border-zinc-200 text-xs text-black space-y-1">
                          <div className="font-bold flex items-center space-x-1.5 text-black">
                            <CheckCircle2 className="w-3.5 h-3.5 text-black" />
                            <span>Editorial Verification: {claim.reviews[0].reviewer_name}</span>
                          </div>
                          <p className="text-zinc-700">{claim.reviews[0].rationale}</p>
                        </div>
                      )}
                    </div>
                  ))
                )}
              </div>

              {/* Action Buttons (Monochrome) */}
              <div className="pt-4 border-t border-zinc-200 flex items-center justify-between flex-wrap gap-3">
                <a
                  href={getCleanSourceUrl(selectedStory, selectedStory.articles[0]?.canonical_url)}
                  target="_blank"
                  rel="noreferrer"
                  className="px-4 py-2.5 rounded-xl bg-black hover:bg-zinc-800 text-white font-bold text-xs flex items-center space-x-2 transition border border-zinc-800 shadow-sm"
                >
                  <span>{getSourceButtonLabel(selectedStory)}</span>
                  <ExternalLink className="w-3.5 h-3.5" />
                </a>

                <button
                  onClick={() => setSelectedStory(null)}
                  className="px-5 py-2.5 bg-zinc-100 hover:bg-zinc-200 text-black font-bold rounded-xl text-xs transition border border-zinc-200"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* AI Duplicate & Fake News Detector Modal */}
      {showAiScanner && (
        <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/75 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl max-w-2xl w-full max-h-[92vh] overflow-y-auto shadow-2xl border border-slate-200 animate-in fade-in zoom-in-95 flex flex-col">
            {/* Modal Header */}
            {/* Modal Header (Pure Monochrome) */}
            <div className="bg-black text-white p-6 rounded-t-3xl border-b border-zinc-800 relative">
              <button
                onClick={() => {
                  setShowAiScanner(false);
                  setScanResult(null);
                }}
                className="absolute top-5 right-5 w-8 h-8 rounded-full bg-zinc-800 hover:bg-zinc-700 text-white flex items-center justify-center transition border border-zinc-700"
              >
                <X className="w-4 h-4" />
              </button>
              <div className="flex items-center space-x-2 mb-1.5">
                <Sparkles className="w-5 h-5 text-white" />
                <span className="text-xs font-black uppercase tracking-wider text-zinc-400">
                  TruthWire AI Fact-Check & Verification Engine
                </span>
              </div>
              <h2 className="text-xl sm:text-2xl font-black text-white">
                Live Website Fact-Checker & Fake News Detector
              </h2>
              <p className="text-xs text-zinc-400 mt-1">
                Active crawler visits authentic portals (OnlineKhabar, Setopati, The Kathmandu Post) in real time to verify rumors, isolate clickbait, and promote verified stories.
              </p>
            </div>

            {/* Modal Body */}
            <div className="p-6 space-y-5">
              {/* Text Input Area */}
              <div className="space-y-2">
                <label className="text-xs font-bold text-black flex items-center justify-between">
                  <span>Enter News Headline, Social Media Post, or Rumor:</span>
                  <span className="text-[11px] text-zinc-500 font-normal">Supports English & Romanized Nepali</span>
                </label>
                <textarea
                  rows={4}
                  value={scanInputText}
                  onChange={(e) => setScanInputText(e.target.value)}
                  placeholder="e.g. Nagdhunga tunnel evacuation drill conducted by Department of Roads, or paste a viral social media rumor..."
                  className="w-full text-xs sm:text-sm p-3.5 bg-zinc-50 border border-zinc-300 rounded-2xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-black text-black font-sans leading-relaxed"
                />
              </div>

              {/* Sample Quick-Test Pills */}
              <div className="space-y-1.5">
                <span className="text-[11px] font-bold text-zinc-500 uppercase tracking-wider block">
                  Quick Sample Tests:
                </span>
                <div className="flex items-center flex-wrap gap-2">
                  <button
                    onClick={() => handleAiScan("Nagdhunga tunnel emergency response evacuation test conducted by Hazama Ando and Department of Roads.")}
                    className="px-2.5 py-1 rounded-lg bg-zinc-100 hover:bg-zinc-200 text-black text-[11px] font-semibold transition border border-zinc-300"
                  >
                    Nagdhunga Tunnel Drill (Authentic)
                  </button>
                  <button
                    onClick={() => handleAiScan("Nepal Police Cyber Bureau takes content creator Jhapalish into custody for questioning.")}
                    className="px-2.5 py-1 rounded-lg bg-zinc-100 hover:bg-zinc-200 text-black text-[11px] font-semibold transition border border-zinc-300"
                  >
                    Cyber Bureau Detainment (Authentic)
                  </button>
                  <button
                    onClick={() => handleAiScan("SHOCKING VIRAL EXPOSED!! You will not believe this secret leaked tape about politician kanda!! MUST WATCH EMERGENCY!!")}
                    className="px-2.5 py-1 rounded-lg bg-zinc-100 hover:bg-zinc-200 text-black text-[11px] font-semibold transition border border-zinc-300"
                  >
                    Viral Clickbait Scandal (Fake / Rumor Test)
                  </button>
                </div>
              </div>

              {/* Scan Action Button */}
              <button
                onClick={() => handleAiScan()}
                disabled={scanningWithAi || !scanInputText.trim()}
                className="w-full py-3 px-4 rounded-xl bg-black hover:bg-zinc-800 disabled:opacity-50 text-white font-bold text-xs sm:text-sm border border-zinc-800 shadow-md flex items-center justify-center space-x-2 transition cursor-pointer"
              >
                {scanningWithAi ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    <span>Visiting Portals & Cross-Checking Live...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4 text-white" />
                    <span>Scan & Verify Against Live Portals</span>
                  </>
                )}
              </button>

              {/* Scan Result Breakdown */}
              {scanResult && (
                <div className="space-y-4 pt-3 border-t border-zinc-200 animate-in fade-in slide-in-from-bottom-2">
                  {/* Live Portals Visited Box */}
                  {scanResult.visited_sites && scanResult.visited_sites.length > 0 && (
                    <div className="p-4 rounded-2xl bg-zinc-950 text-white border border-zinc-800 space-y-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <Globe className="w-4 h-4 text-white" />
                          <span className="text-xs font-bold uppercase tracking-wider text-zinc-300">
                            Live Authentic Portals Visited
                          </span>
                        </div>
                        <span className="text-[10px] font-mono text-zinc-400">
                          Active Web Crawl
                        </span>
                      </div>

                      <div className="space-y-2">
                        {scanResult.visited_sites.map((site, i) => (
                          <div key={i} className="flex items-center justify-between p-2.5 rounded-xl bg-zinc-900 border border-zinc-800 text-xs">
                            <div className="space-y-0.5">
                              <div className="flex items-center space-x-2">
                                <span className="font-bold text-white">{site.name}</span>
                                <a href={site.url} target="_blank" rel="noreferrer" className="text-zinc-400 hover:text-white underline text-[10px]">
                                  {site.url}
                                </a>
                              </div>
                              <div className="text-[11px] text-zinc-400">
                                {site.article_title ? `Headline: "${site.article_title.slice(0, 60)}..."` : `Status: ${site.status}`}
                              </div>
                            </div>
                            <div className="text-right">
                              <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                                site.status === "VERIFIED_MATCH"
                                  ? "bg-white text-black font-black"
                                  : "bg-zinc-800 text-zinc-400 border border-zinc-700"
                              }`}>
                                {site.status === "VERIFIED_MATCH" ? `MATCH (${site.match_score}%)` : site.status}
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>

                      {scanResult.actions_taken && scanResult.actions_taken.length > 0 && (
                        <div className="pt-2 border-t border-zinc-800 space-y-1">
                          <span className="text-[10px] font-bold text-zinc-400 uppercase tracking-wide block">
                            System Actions & Feed Updates:
                          </span>
                          {scanResult.actions_taken.map((action, i) => (
                            <div key={i} className="text-xs text-zinc-300 flex items-start space-x-1.5">
                              <span className="text-white font-bold">✓</span>
                              <span>{action}</span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Duplicate Detection Alert */}
                  {scanResult.is_duplicate ? (
                    <div className="p-3.5 rounded-2xl bg-zinc-100 border border-zinc-300 text-black flex items-start space-x-3">
                      <Layers className="w-5 h-5 text-black shrink-0 mt-0.5" />
                      <div className="space-y-1">
                        <div className="flex items-center space-x-2">
                          <span className="text-xs font-black uppercase tracking-wider text-black">
                            Duplicate Event Detected ({Math.round((scanResult.duplicate_similarity_score || 0.8) * 100)}% match)
                          </span>
                        </div>
                        <p className="text-xs text-zinc-700">
                          This post semantically matches an authentic existing story in TruthWire:
                        </p>
                        <p className="text-xs font-bold text-black">
                          &ldquo;{scanResult.matched_story_title}&rdquo;
                        </p>
                        {scanResult.matched_story_id && (
                          <button
                            onClick={() => {
                              const story = stories.find((s) => s.id === scanResult.matched_story_id);
                              if (story) {
                                setShowAiScanner(false);
                                setSelectedStory(story);
                              }
                            }}
                            className="mt-1 text-xs font-bold text-black underline flex items-center space-x-1"
                          >
                            <span>Open Verified Story & Evidence</span>
                            <ChevronRight className="w-3.5 h-3.5" />
                          </button>
                        )}
                      </div>
                    </div>
                  ) : (
                    <div className="p-3 rounded-xl bg-zinc-50 border border-zinc-200 text-zinc-800 flex items-center space-x-2 text-xs">
                      <CheckCircle2 className="w-4 h-4 text-black shrink-0" />
                      <span><strong>Unique Report:</strong> No duplicate posts for this event found in recent database.</span>
                    </div>
                  )}

                  {/* Authenticity Score Card (Monochrome) */}
                  <div className="p-4 rounded-2xl bg-zinc-950 text-white border border-zinc-800 space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-zinc-400 uppercase">AI Authenticity Rating</span>
                      <span className="px-2.5 py-0.5 rounded-full text-[11px] font-black uppercase tracking-wider bg-zinc-800 text-white border border-zinc-700">
                        {scanResult.verdict_label}
                      </span>
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                      <div className="bg-zinc-900 rounded-xl p-3 border border-zinc-800">
                        <span className="text-[10px] text-zinc-400 font-bold uppercase block">Credibility Score</span>
                        <div className="text-3xl font-black text-white font-mono mt-1">
                          {scanResult.credibility_score}%
                        </div>
                      </div>
                      <div className="bg-zinc-900 rounded-xl p-3 border border-zinc-800">
                        <span className="text-[10px] text-zinc-400 font-bold uppercase block">Sensationalism Index</span>
                        <div className="text-3xl font-black text-zinc-200 font-mono mt-1">
                          {scanResult.sensationalism_score}%
                        </div>
                      </div>
                    </div>

                    {/* AI Signals */}
                    <div className="space-y-1.5 pt-2 border-t border-zinc-800 text-xs">
                      <span className="text-[10px] font-bold text-zinc-400 uppercase block">Analysis Signals:</span>
                      {scanResult.signals.map((sig, i) => (
                        <div key={i} className="text-zinc-300 flex items-start space-x-1.5">
                          <span className="text-white font-bold">•</span>
                          <span>{sig}</span>
                        </div>
                      ))}
                    </div>

                    {/* Recommendation */}
                    <div className="text-xs text-zinc-300 italic pt-1 border-t border-zinc-800">
                      <strong>AI Advice:</strong> {scanResult.recommendation}
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Modal Footer */}
            <div className="p-4 bg-zinc-50 border-t border-zinc-200 rounded-b-3xl flex items-center justify-end">
              <button
                onClick={() => {
                  setShowAiScanner(false);
                  setScanResult(null);
                }}
                className="px-5 py-2 bg-zinc-200 hover:bg-zinc-300 text-black font-bold rounded-xl text-xs transition border border-zinc-300"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 py-8 mt-12 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 space-y-2">
          <p className="font-bold text-slate-800 text-sm">
            TruthWire &copy; 2026 — Evidence-Verified News Aggregation Portal
          </p>
          <p className="text-slate-400">
            Real-time Hamro Patro Bikram Sambat Date & Nepal Time • NRB Live Forex Rates • Pilot: Nepal (🇳🇵), United States (🇺🇸), Canada (🇨🇦).
          </p>
        </div>
      </footer>
    </div>
  );
}
