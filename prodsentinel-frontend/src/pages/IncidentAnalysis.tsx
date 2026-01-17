import { useNavigate, useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { getIncidentAnalysis } from '@/services/api';
import { GlassPanel } from '@/components/ui/GlassPanel';
import { ArrowLeft, Bot, FileText, Activity } from 'lucide-react';


import ReactMarkdown from 'react-markdown';

export const IncidentAnalysis = () => {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();

    const { data: analysis, isLoading, error } = useQuery({
        queryKey: ['analysis', id],
        queryFn: () => getIncidentAnalysis(id!),
        enabled: !!id
    });

    if (isLoading) {
        return (
            <div className="p-8 max-w-5xl mx-auto animate-pulse space-y-8">
                <div className="h-8 w-1/3 bg-white/5 rounded" />
                <div className="h-64 bg-white/5 rounded-xl border border-white/5" />
                <div className="h-32 bg-white/5 rounded-xl border border-white/5" />
            </div>
        );
    }

    if (error || !analysis) {
        return (
            <div className="p-8 flex flex-col items-center justify-center h-[50vh] text-slate-400">
                <Bot size={48} className="mb-4 text-slate-600" />
                <h2 className="text-xl font-medium text-slate-300">Analysis Unavailable</h2>
                <p className="max-w-md text-center mt-2">
                    {error ? "Failed to load analysis data." : "AI analysis has not yet been generated for this incident."}
                </p>
                <button
                    onClick={() => navigate('/incidents')}
                    className="mt-6 px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg transition-colors"
                >
                    Return to Dashboard
                </button>
            </div>
        );
    }

    // Heuristic: If score > 1, assume it's 0-100. If <= 1, assume 0-1.
    const displayConfidence = analysis.confidence_score > 1
        ? analysis.confidence_score
        : analysis.confidence_score * 100;

    return (
        <div className="p-8 max-w-6xl mx-auto space-y-6 pb-20">
            {/* Header */}
            <div className="flex items-center gap-4">
                <button
                    onClick={() => navigate('/incidents')}
                    className="p-2 hover:bg-white/5 rounded-lg text-slate-400 hover:text-white transition-colors"
                >
                    <ArrowLeft size={20} />
                </button>
                <div>
                    <h1 className="text-xl font-bold text-white flex items-center gap-2">
                        Root Cause Analysis
                        <span className="text-slate-500 font-mono text-sm font-normal">#{id?.slice(0, 8)}</span>
                    </h1>
                </div>
                <div className="ml-auto flex items-center gap-3">
                    <div className="px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-sm font-medium">
                        Confidence: {displayConfidence.toFixed(0)}%
                    </div>
                </div>
            </div>

            {/* AI Insight Card */}
            <GlassPanel className="p-0 overflow-hidden border-indigo-500/20 shine-effect">
                <div className="bg-indigo-500/5 px-6 py-4 border-b border-indigo-500/10 flex items-center gap-3">
                    <Bot className="text-indigo-400" size={20} />
                    <h2 className="font-semibold text-indigo-100">AI Conclusion</h2>
                </div>
                <div className="p-6">
                    <div className="prose prose-invert max-w-none text-slate-300 prose-strong:text-indigo-300 prose-code:text-cyan-300 prose-code:bg-white/5 prose-code:px-1 prose-code:rounded prose-code:before:content-none prose-code:after:content-none">
                        <ReactMarkdown>{analysis.root_cause}</ReactMarkdown>


                        {analysis.ai_explanation && (
                            <div className="mt-6 bg-[#0f141e] rounded-lg p-4 border border-white/5 font-mono text-sm text-slate-400 whitespace-pre-wrap">
                                {typeof analysis.ai_explanation === 'string'
                                    ? analysis.ai_explanation
                                    : JSON.stringify(analysis.ai_explanation, null, 2)}
                            </div>
                        )}
                    </div>
                </div>
            </GlassPanel>

            {/* Evidence Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <GlassPanel className="p-6">
                    <h3 className="flex items-center gap-2 font-medium text-slate-200 mb-4">
                        <Activity size={18} className="text-emerald-400" />
                        Evidence Structure
                    </h3>
                    <div className="space-y-3">
                        {analysis.evidence_signals.map((sigId, idx) => (
                            <div key={sigId} className="flex items-center gap-3 p-3 rounded bg-white/5 border border-white/5">
                                <span className="text-xs font-mono text-slate-500 w-6">{idx + 1}</span>
                                <div className="flex-1">
                                    <div className="text-xs text-slate-400">Signal ID</div>
                                    <div className="text-sm font-mono text-indigo-300">{sigId}</div>
                                </div>
                            </div>
                        ))}
                        {analysis.evidence_signals.length === 0 && (
                            <p className="text-slate-500 italic">No specific signals cited.</p>
                        )}
                    </div>
                </GlassPanel>

                <GlassPanel className="p-6">
                    <h3 className="flex items-center gap-2 font-medium text-slate-200 mb-4">
                        <FileText size={18} className="text-amber-400" />
                        Metadata
                    </h3>
                    <dl className="space-y-4 text-sm">
                        <div className="flex justify-between py-1 border-b border-white/5">
                            <dt className="text-slate-500">Generated At</dt>
                            <dd className="font-mono text-slate-300">
                                {new Date(analysis.generated_at).toLocaleString()}
                            </dd>
                        </div>
                        <div className="flex justify-between py-1 border-b border-white/5">
                            <dt className="text-slate-500">Analysis Engine</dt>
                            <dd className="text-slate-300">AutoGen (Flash 2.5)</dd>
                        </div>
                    </dl>
                </GlassPanel>
            </div>
        </div>
    );
};
