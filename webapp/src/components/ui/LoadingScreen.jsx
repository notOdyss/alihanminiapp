import React from 'react';
import './LoadingScreen.css';

const LoadingScreen = () => {
    return (
        <div className="loading-screen">
            {/* Background orbs */}
            <div className="loading-bg-orb loading-bg-orb-1"></div>
            <div className="loading-bg-orb loading-bg-orb-2"></div>
            <div className="loading-bg-orb loading-bg-orb-3"></div>

            <div className="loading-content">
                {/* Logo Section */}
                <div className="loading-logo-section">
                    <div className="logo-ring">
                        <div className="logo-ring-inner"></div>
                    </div>
                    <div className="logo-icon">
                        <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <defs>
                                <linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                                    <stop offset="0%" stopColor="#a855f7" />
                                    <stop offset="100%" stopColor="#6366f1" />
                                </linearGradient>
                            </defs>
                            <circle cx="24" cy="24" r="20" stroke="url(#logoGradient)" strokeWidth="2.5" fill="none" />
                            <path
                                d="M15 24L21 30L33 18"
                                stroke="url(#logoGradient)"
                                strokeWidth="3"
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                fill="none"
                            />
                        </svg>
                    </div>
                </div>

                {/* Brand Name */}
                <div className="loading-brand">
                    <h1 className="loading-title">Обменник</h1>
                    <span className="loading-subtitle">by Ali</span>
                </div>

                {/* Loading Spinner */}
                <div className="loading-spinner">
                    <div className="spinner-circle"></div>
                    <div className="spinner-circle"></div>
                    <div className="spinner-circle"></div>
                </div>

                {/* Loading Text */}
                <p className="loading-text">
                    Загрузка<span className="loading-dots"><span>.</span><span>.</span><span>.</span></span>
                </p>
            </div>
        </div>
    );
};

export default LoadingScreen;
