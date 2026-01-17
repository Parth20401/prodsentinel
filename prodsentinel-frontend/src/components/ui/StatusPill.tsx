import { cn } from '@/lib/utils';
import { IncidentStatus, IncidentSeverity } from '@/types';

const statusColors: Record<IncidentStatus, string> = {
    [IncidentStatus.OPEN]: 'bg-red-500/10 text-red-500 border-red-500/20',
    [IncidentStatus.INVESTIGATING]: 'bg-amber-500/10 text-amber-500 border-amber-500/20',
    [IncidentStatus.RESOLVED]: 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20',
    [IncidentStatus.CLOSED]: 'bg-slate-500/10 text-slate-500 border-slate-500/20',
};

const severityColors: Record<IncidentSeverity, string> = {
    [IncidentSeverity.CRITICAL]: 'text-red-500 font-bold',
    [IncidentSeverity.HIGH]: 'text-orange-500 font-semibold',
    [IncidentSeverity.MEDIUM]: 'text-yellow-500',
    [IncidentSeverity.LOW]: 'text-blue-500',
};

export const StatusPill = ({ status }: { status: IncidentStatus }) => {
    return (
        <span className={cn(
            "px-2 py-0.5 rounded-full text-xs font-medium border uppercase tracking-wide",
            statusColors[status]
        )}>
            {status}
        </span>
    );
};

export const SeverityBadge = ({ severity }: { severity: IncidentSeverity }) => {
    return (
        <div className="flex items-center gap-1.5">
            <span className={cn("h-1.5 w-1.5 rounded-full",
                severity === IncidentSeverity.CRITICAL ? "bg-red-500 animate-pulse" :
                    severity === IncidentSeverity.HIGH ? "bg-orange-500" :
                        severity === IncidentSeverity.MEDIUM ? "bg-yellow-500" : "bg-blue-500"
            )} />
            <span className={cn("text-xs uppercase tracking-wider", severityColors[severity])}>
                {severity}
            </span>
        </div>
    );
}
