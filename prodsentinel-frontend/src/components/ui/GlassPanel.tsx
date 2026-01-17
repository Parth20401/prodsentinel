import React from 'react';

interface GlassPanelProps extends React.HTMLAttributes<HTMLDivElement> {
    children: React.ReactNode;
    hoverEffect?: boolean;
}


export const GlassPanel = ({
    children,
    className,
    hoverEffect = false,
    ...props
}: GlassPanelProps) => {
    return (
        <div
            className={`
        glass-panel rounded-xl border border-white/10 overflow-hidden
        transition-all duration-300 ease-in-out
        ${hoverEffect ? 'hover:bg-[rgba(30,35,45,0.7)] hover:border-white/20 hover:shadow-lg hover:-translate-y-[1px]' : ''}
        ${className}
      `}
            {...props}
        >
            {children}
        </div>
    );
};
