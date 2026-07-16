import React from 'react';

const LoadingSpinner = ({ label = 'Loading…' }) => (
    <div className="flex items-center justify-center min-h-[40vh]">
        <div className="flex flex-col items-center gap-3">
            <div className="w-10 h-10 border-2 border-brand-600 border-t-transparent rounded-full animate-spin" />
            <p className="text-sm text-slate-500">{label}</p>
        </div>
    </div>
);

export default LoadingSpinner;
