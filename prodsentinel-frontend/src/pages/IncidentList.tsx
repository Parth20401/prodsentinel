import { useQuery } from '@tanstack/react-query';
import { getIncidents } from '@/services/api';
import { GlassPanel } from '@/components/ui/GlassPanel';
import { StatusPill, SeverityBadge } from '@/components/ui/StatusPill';
import { AlertCircle, CheckCircle2 } from 'lucide-react';
import { Link } from 'react-router-dom';

export const IncidentList = () => {
    const { data, isLoading } = useQuery({
        queryKey: ['incidents'],
        queryFn: () => getIncidents()
    });

    return (
        <div className="p-8 max-w-7xl mx-auto space-y-8">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
                        Incident Command
                    </h1>
                    <p className="text-slate-400 text-sm mt-1">Real-time production monitoring</p>
                </div>
                <div className="flex gap-4">
                    {/* Summary Stats (Mock for visuals) */}
                    <GlassPanel className="px-4 py-2 flex items-center gap-3">
                        <div className="p-1.5 bg-red-500/10 rounded-lg text-red-500"><AlertCircle size={16} /></div>
                        <div>
                            <p className="text-xs text-slate-400">Open</p>
                            <p className="text-lg font-mono leading-none">3</p>
                        </div>
                    </GlassPanel>
                </div>
            </div>

            {/* Grid */}
            <GlassPanel className="min-h-[600px] relative">
                <div className="absolute inset-0 overflow-auto">
                    <table className="w-full text-left text-sm">
                        <thead className="sticky top-0 bg-[#0f141e]/90 backdrop-blur-md z-10 border-b border-white/5">
                            <tr className="text-slate-400 font-medium">
                                <th className="px-6 py-4 w-[120px]">Status</th>
                                <th className="px-6 py-4 w-[120px]">Severity</th>
                                <th className="px-6 py-4 font-mono">Trace ID / Impact</th>
                                <th className="px-6 py-4">Services</th>
                                <th className="px-6 py-4 text-right">Detected</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                            {isLoading ? (
                                // Skeleton Loader
                                [...Array(5)].map((_, i) => (
                                    <tr key={i} className="animate-pulse">
                                        <td className="px-6 py-4"><div className="h-4 w-16 bg-white/5 rounded" /></td>
                                        <td className="px-6 py-4"><div className="h-4 w-16 bg-white/5 rounded" /></td>
                                        <td className="px-6 py-4"><div className="h-4 w-32 bg-white/5 rounded" /></td>
                                        <td className="px-6 py-4"><div className="h-4 w-24 bg-white/5 rounded" /></td>
                                        <td className="px-6 py-4"><div className="h-4 w-20 bg-white/5 rounded ml-auto" /></td>
                                    </tr>
                                ))
                            ) : data?.items.map((incident) => (
                                <tr
                                    key={incident.id}
                                    className="group hover:bg-white/[0.02] transition-colors cursor-pointer"
                                >
                                    <td className="px-6 py-4">
                                        <StatusPill status={incident.status} />
                                    </td>
                                    <td className="px-6 py-4">
                                        <SeverityBadge severity={incident.severity} />
                                    </td>
                                    <td className="px-6 py-4 font-mono text-slate-300 group-hover:text-cyan-400 transition-colors">
                                        <Link to={`/incidents/${incident.id}`} className="block" title={`Trace ID: ${incident.trace_id}`}>
                                            {incident.trace_id.slice(0, 8)}...
                                            <div className="text-xs text-slate-500 mt-1">Error Count: {incident.error_count}</div>
                                        </Link>
                                    </td>
                                    <td className="px-6 py-4 text-slate-300">
                                        <div className="flex gap-2">
                                            {incident.affected_services.map(svc => (
                                                <span key={svc} className="text-xs bg-white/5 px-1.5 py-0.5 rounded border border-white/5">
                                                    {svc}
                                                </span>
                                            ))}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 text-right text-slate-400 font-mono text-xs">
                                        {new Date(incident.detected_at).toLocaleString()}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>

                    {!isLoading && data?.items.length === 0 && (
                        <div className="flex flex-col items-center justify-center py-20 text-slate-500">
                            <CheckCircle2 size={48} className="mb-4 text-emerald-500/50" />
                            <p className="text-lg font-medium text-slate-300">All Systems Operational</p>
                            <p className="text-sm">No active incidents detected.</p>
                        </div>
                    )}
                </div>
            </GlassPanel>
        </div>
    );
};
