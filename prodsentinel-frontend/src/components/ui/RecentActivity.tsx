import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import { Activity, Terminal, Database, Cpu } from 'lucide-react';
import { cn } from '@/lib/utils';
import { formatDistanceToNow } from 'date-fns';

const API_URL = 'http://localhost:8000';

interface RawSignal {
    id: string;
    signal_type: 'log' | 'trace' | 'metric';
    service_name: string;
    timestamp: string;
    payload: any;
}

export const RecentActivity = () => {
    const { data, isLoading } = useQuery({
        queryKey: ['raw_signals'],
        queryFn: async () => {
            const res = await axios.get(`${API_URL}/query/signals?limit=10`);
            return res.data;
        },
        refetchInterval: 5000 // Poll every 5s for "live" feel
    });

    if (isLoading) return <div className="text-slate-500 text-sm p-4">Streaming signals...</div>;

    return (
        <div className="space-y-3">
            <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-2 px-1">
                <Activity size={14} className="text-indigo-400" />
                Live Signal Feed
            </h3>

            <div className="space-y-2">
                {data?.items?.map((signal: RawSignal) => (
                    <div
                        key={signal.id}
                        className="group flex items-start gap-3 p-3 rounded-lg bg-white/[0.02] border border-white/[0.05] hover:bg-white/[0.04] transition-all"
                    >
                        <div className={cn(
                            "mt-1 p-1.5 rounded-md",
                            signal.signal_type === 'log' ? "bg-blue-500/10 text-blue-400" :
                                signal.signal_type === 'trace' ? "bg-purple-500/10 text-purple-400" :
                                    "bg-amber-500/10 text-amber-400"
                        )}>
                            {signal.signal_type === 'log' && <Terminal size={14} />}
                            {signal.signal_type === 'trace' && <Database size={14} />}
                            {signal.signal_type === 'metric' && <Cpu size={14} />}
                        </div>

                        <div className="flex-1 min-w-0">
                            <div className="flex items-center justify-between gap-2">
                                <span className="text-xs font-bold text-slate-200 truncate font-mono">
                                    {signal.service_name}
                                </span>
                                <span className="text-[10px] text-slate-500 whitespace-nowrap">
                                    {formatDistanceToNow(new Date(signal.timestamp), { addSuffix: true })}
                                </span>
                            </div>
                            <p className="text-[11px] text-slate-400 truncate mt-0.5 font-mono">
                                {signal.signal_type === 'log' ? signal.payload.message :
                                    signal.signal_type === 'metric' ? `${signal.payload.metric_name}: ${signal.payload.value}${signal.payload.unit || ''}` :
                                        `Span: ${signal.payload.span_id || 'unnamed'}`}
                            </p>
                        </div>
                    </div>
                ))}

                {(!data?.items || data.items.length === 0) && (
                    <div className="text-center py-8 text-slate-500 text-sm italic">
                        Listening for incoming signals...
                    </div>
                )}
            </div>
        </div>
    );
};
