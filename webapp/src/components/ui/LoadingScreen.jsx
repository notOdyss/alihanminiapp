import React, { useState, useEffect } from 'react';
import './LoadingScreen.css';

const LoadingScreen = () => {
    const [progress, setProgress] = useState(0);
    const [currentStep, setCurrentStep] = useState(0);

    const steps = [
        { text: 'Проверка безопасности...', icon: '🔐' },
        { text: 'Синхронизация данных...', icon: '🔄' },
        { text: 'Загрузка транзакций...', icon: '💳' },
        { text: 'Подготовка интерфейса...', icon: '✨' },
    ];

    useEffect(() => {
        // Progress animation - complete in 5 seconds
        const progressInterval = setInterval(() => {
            setProgress(prev => {
                if (prev >= 100) return 100;
                // Ease out - faster at start, slower near end
                const increment = Math.max(0.5, (100 - prev) / 50);
                return Math.min(100, prev + increment);
            });
        }, 50);

        // Step animation - change step every ~1.2 seconds
        const stepInterval = setInterval(() => {
            setCurrentStep(prev => (prev < steps.length - 1 ? prev + 1 : prev));
        }, 1200);

        return () => {
            clearInterval(progressInterval);
            clearInterval(stepInterval);
        };
    }, []);

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

                {/* Progress Bar */}
                <div className="loading-progress-container">
                    <div className="loading-progress-bar">
                        <div
                            className="loading-progress-fill"
                            style={{ width: `${progress}%` }}
                        ></div>
                    </div>
                    <span className="loading-progress-text">{Math.round(progress)}%</span>
                </div>

                {/* Dynamic Steps */}
                <div className="loading-steps">
                    {steps.map((step, index) => (
                        <div
                            key={index}
                            className={`loading-step ${index === currentStep ? 'active' : ''} ${index < currentStep ? 'completed' : ''}`}
                        >
                            <span className="step-icon">{step.icon}</span>
                            <span className="step-text">{step.text}</span>
                            {index === currentStep && (
                                <span className="step-loader"></span>
                            )}
                            {index < currentStep && (
                                <span className="step-check">✓</span>
                            )}
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default LoadingScreen;
