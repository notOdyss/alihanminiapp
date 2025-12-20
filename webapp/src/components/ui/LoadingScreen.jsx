import React from 'react'
import './LoadingScreen.css'

const LoadingScreen = () => {
    return (
        <div className="loading-screen">
            <div className="loading-content">
                <div className="logo-container">
                    <div className="logo-pulse"></div>
                    <img src="/vite.svg" alt="Logo" className="loading-logo" />
                </div>
                <h2 className="loading-title">Loading...</h2>
                <p className="loading-text">Getting User Data...</p>

                <div className="loading-bar-container">
                    <div className="loading-bar-fill"></div>
                </div>
            </div>
        </div>
    )
}

export default LoadingScreen
