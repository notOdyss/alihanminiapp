import React from 'react'
import './LoadingScreen.css'

export default function LoadingScreen() {
    return (
        <div className="loading-screen">
            <div className="loading-content">
                <div className="loading-spinner">
                    <div className="spinner-ring"></div>
                    <div className="spinner-ring"></div>
                    <div className="spinner-core"></div>
                </div>
                <h2 className="loading-title">AlihanBot</h2>
                <div className="loading-steps">
                    <div className="step active">Verifying secure access...</div>
                    <div className="step">Syncing latest transactions...</div>
                    <div className="step">Decrypting balances...</div>
                </div>
            </div>
        </div>
    )
}
