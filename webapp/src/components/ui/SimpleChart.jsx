import React from 'react';

export default function SimpleChart({ data, height = 100, color = '#6366f1', showArea = true }) {
    if (!data || data.length < 2) return null;

    const width = 100; // SVG coordinate system
    const max = Math.max(...data);
    const min = Math.min(...data);
    const range = max - min || 1;

    // Points for the line
    const points = data.map((val, i) => {
        const x = (i / (data.length - 1)) * width;
        const y = height - ((val - min) / range) * (height - 10) - 5; // padding
        return `${x},${y}`;
    }).join(' ');

    // Path for the area
    const areaPath = `
    M 0,${height}
    L ${points}
    L ${width},${height}
    Z
  `;

    return (
        <div style={{ width: '100%', height: '100%', overflow: 'hidden' }}>
            <svg
                viewBox={`0 0 ${width} ${height}`}
                preserveAspectRatio="none"
                style={{ width: '100%', height: '100%', display: 'block' }}
            >
                <defs>
                    <linearGradient id={`gradient-${color}`} x1="0" x2="0" y1="0" y2="1">
                        <stop offset="0%" stopColor={color} stopOpacity="0.4" />
                        <stop offset="100%" stopColor={color} stopOpacity="0" />
                    </linearGradient>
                </defs>

                {showArea && (
                    <path
                        d={areaPath}
                        fill={`url(#gradient-${color})`}
                        stroke="none"
                    />
                )}

                <polyline
                    points={points}
                    fill="none"
                    stroke={color}
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    vectorEffect="non-scaling-stroke"
                />
            </svg>
        </div>
    );
}
