import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import { formatDistanceToNow } from 'date-fns';
import { cn } from '@/lib/utils';
import { getIncidents } from '@/services/api';
import { GlassPanel } from '@/components/ui/GlassPanel';
import { RecentActivity } from '@/components/ui/RecentActivity';
import { Activity, ShieldAlert, BarChart3, Server } from 'lucide-react';
import {
    BarChart, Bar, XAxis, YAxis, Tooltip as RechartsTooltip, ResponsiveContainer, Cell
} from 'recharts';
import { useNavigate } from 'react-router-dom';

const COLORS = {
    critical: '#ef4444',
    high: '#f97316',
    medium: '#eab308',
    low: '#3b82f6',
    open: '#6366f1',
    resolved: '#10b981'
};

export const Overview = () => {
    const navigate = useNavigate();
    const { data: incidentsData, isLoading: incidentsLoading } = useQuery({
        queryKey: ['incidents', 'overview'],
        queryFn: () => getIncidents(1, 100) // Get last 100 for stats
    });

    const { data: signalsData } = useQuery({
        queryKey: ['raw_signals', 'status'],
        queryFn: async () => {
            const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
            const res = await axios.get(`${API_URL}/query/signals?limit=1`);
            return res.data;
        },
        refetchInterval: 10000 // Poll every 10s for status
    });

    const lastSignal = signalsData?.items?.[0];
    const lastSignalTime = lastSignal ? new Date(lastSignal.timestamp) : null;
    const isSystemLive = lastSignalTime && (new Date().getTime() - lastSignalTime.getTime()) < 60000;


    // Mock stats if loading or empty, otherwise calculate
    const stats = {
        total: incidentsData?.total || 0,
        critical: 0,
        avgResolution: '12m'
    };

    const severityData = [
        { name: 'Critical', value: 0, color: COLORS.critical },
        { name: 'High', value: 0, color: COLORS.high },
        { name: 'Medium', value: 0, color: COLORS.medium },
        { name: 'Low', value: 0, color: COLORS.low },
    ];

    const serviceData: Record<string, number> = {};

    if (incidentsData?.items) {
        incidentsData.items.forEach(i => {
            const sev = i.severity.toLowerCase();
            if (sev === 'critical') stats.critical++;

            const sevIndex = severityData.findIndex(s => s.name.toLowerCase() === sev);
            if (sevIndex !== -1) severityData[sevIndex].value++;

            i.affected_services.forEach(svc => {
                if (svc && svc !== 'unknown') {
                    serviceData[svc] = (serviceData[svc] || 0) + 1;
                }
            });
        });
    }

    const serviceChartData = Object.entries(serviceData)
        .map(([name, count]) => ({ name, count }))
        .sort((a, b) => b.count - a.count)
        .slice(0, 5);

    if (incidentsLoading) {
        return <div className="p-8 animate-pulse text-slate-500">Loading infrastructure metrics...</div>;
    }

    return (
        <div className="p-8 max-w-[1600px] mx-auto space-y-6">
            <header className="flex items-center justify-between">
                <h1 className="text-2xl font-bold text-white flex items-center gap-3">
                    <Activity className="text-indigo-400" />
                    System Overview
                </h1>
                <div className="flex items-center gap-3">
                    <div className={cn(
                        "flex items-center gap-2 px-3 py-1 rounded-full border text-[10px] font-bold uppercase tracking-widest transition-all",
                        isSystemLive
                            ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-500"
                            : "bg-slate-500/10 border-slate-500/20 text-slate-400"
                    )}>
                        <div className={cn(
                            "h-1.5 w-1.5 rounded-full animate-pulse",
                            isSystemLive ? "bg-emerald-500" : "bg-slate-500"
                        )} />
                        {isSystemLive ? 'Live Connection' : 'System Standby'}
                    </div>

                    {lastSignalTime && (
                        <span className="text-[10px] text-slate-500 font-medium">
                            Last Signal: {formatDistanceToNow(lastSignalTime, { addSuffix: true })}
                        </span>
                    )}
                </div>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
                {/* Main Stats Column */}
                <div className="lg:col-span-8 space-y-6">
                    {/* KPI Cards */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <GlassPanel className="p-6 flex items-center justify-between">
                            <div>
                                <p className="text-slate-400 text-sm">Active Incidents</p>
                                <p className="text-3xl font-bold text-white mt-1">{stats.total}</p>
                            </div>
                            <div className="p-3 bg-indigo-500/10 rounded-xl text-indigo-400">
                                <BarChart3 size={24} />
                            </div>
                        </GlassPanel>

                        <GlassPanel className="p-6 flex items-center justify-between">
                            <div>
                                <p className="text-slate-400 text-sm">Critical Events</p>
                                <p className="text-3xl font-bold text-white mt-1">{severityData[0].value}</p>
                            </div>
                            <div className="p-3 bg-red-500/10 rounded-xl text-red-500">
                                <ShieldAlert size={24} />
                            </div>
                        </GlassPanel>

                        <GlassPanel className="p-6 flex items-center justify-between">
                            <div>
                                <p className="text-slate-400 text-sm">MTTR (Avg)</p>
                                <p className="text-3xl font-bold text-white mt-1">{stats.avgResolution}</p>
                            </div>
                            <div className="p-3 bg-emerald-500/10 rounded-xl text-emerald-500">
                                <Activity size={24} />
                            </div>
                        </GlassPanel>
                    </div>

                    {/* Charts Section */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <GlassPanel className="p-6 h-[350px]">
                            <h3 className="text-lg font-medium text-slate-200 mb-6 flex items-center gap-2">
                                <ShieldAlert size={18} className="text-slate-400" />
                                Incident Severity
                            </h3>
                            <ResponsiveContainer width="100%" height="80%">
                                <BarChart data={severityData}>
                                    <XAxis dataKey="name" stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                                    <YAxis stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                                    <RechartsTooltip
                                        contentStyle={{ backgroundColor: '#0f141e', borderColor: '#1e293b', borderRadius: '8px' }}
                                        itemStyle={{ color: '#e2e8f0' }}
                                        cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                                    />
                                    <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                                        {severityData.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={entry.color} />
                                        ))}
                                    </Bar>
                                </BarChart>
                            </ResponsiveContainer>
                        </GlassPanel>

                        <GlassPanel className="p-6 h-[350px]">
                            <h3 className="text-lg font-medium text-slate-200 mb-6 flex items-center gap-2">
                                <Server size={18} className="text-slate-400" />
                                Top Affected Services
                            </h3>
                            {serviceChartData.length > 0 ? (
                                <ResponsiveContainer width="100%" height="80%">
                                    <BarChart data={serviceChartData} layout="vertical">
                                        <XAxis type="number" stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                                        <YAxis dataKey="name" type="category" stroke="#64748b" fontSize={12} width={100} tickLine={false} axisLine={false} />
                                        <RechartsTooltip
                                            contentStyle={{ backgroundColor: '#0f141e', borderColor: '#1e293b', borderRadius: '8px' }}
                                            cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                                        />
                                        <Bar dataKey="count" fill="#818cf8" radius={[0, 4, 4, 0]} barSize={20} />
                                    </BarChart>
                                </ResponsiveContainer>
                            ) : (
                                <div className="flex h-full items-center justify-center text-slate-500 italic text-sm">
                                    No service data available
                                </div>
                            )}
                        </GlassPanel>
                    </div>

                    <div className="flex justify-start">
                        <button
                            onClick={() => navigate('/incidents')}
                            className="px-6 py-2.5 bg-indigo-500 hover:bg-indigo-600 text-white rounded-lg transition-all font-semibold text-sm shadow-lg shadow-indigo-500/20 active:scale-95"
                        >
                            Explore All Incidents
                        </button>
                    </div>
                </div>

                {/* Live Activity Sidebar */}
                <div className="lg:col-span-4 lg:border-l lg:border-white/5 lg:pl-8">
                    <RecentActivity />
                </div>
            </div>
        </div>
    );
};
