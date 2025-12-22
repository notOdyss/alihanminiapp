import React, { useState, useEffect } from 'react';
import './Referral.css';
import { useTelegram } from '../context/TelegramContext';

const API_URL = import.meta.env.VITE_API_URL || 'https://floy-effluvial-chaim.ngrok-free.dev/api';

const Referral = () => {
    const { user, tg } = useTelegram();
    const [referralCode, setReferralCode] = useState('');
    const [customCode, setCustomCode] = useState('');
    const [canCustomize, setCanCustomize] = useState(false);
    const [loading, setLoading] = useState(true);
    const [message, setMessage] = useState('');

    useEffect(() => {
        // Fetch referral code from access-status
        const fetchReferralInfo = async () => {
            try {
                const response = await fetch(`${API_URL}/access-status`, {
                    headers: {
                        'X-Telegram-Init-Data': tg?.initData || ''
                    }
                });

                if (response.ok) {
                    const data = await response.json();
                    setReferralCode(data.referral_code || 'Не установлен');
                    setCanCustomize(data.is_referral_custom || false);
                }
            } catch (e) {
                console.error('Failed to fetch referral info:', e);
            } finally {
                setLoading(false);
            }
        };

        if (tg?.initData) {
            fetchReferralInfo();
        } else {
            setLoading(false);
        }
    }, [tg?.initData]);

    const handleCopyLink = () => {
        const link = `https://t.me/exchangeali_bot?start=${referralCode || 'LOADING'}`;
        navigator.clipboard.writeText(link);
        if (tg?.showPopup) {
            tg.showPopup({ title: 'Ссылка скопирована', message: link, buttons: [{ type: 'ok' }] });
        }
    };

    const handleUpdateCode = async () => {
        if (!customCode) return;
        setMessage('');
        try {
            const response = await fetch(`${API_URL}/user/referral_code`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Telegram-Init-Data': tg?.initData || ''
                },
                body: JSON.stringify({ new_code: customCode })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Failed to update');
            }

            setReferralCode(data.new_code);
            setMessage("✅ Код обновлен!");
            setCustomCode('');
        } catch (e) {
            setMessage(`❌ Ошибка: ${e.message}`);
        }
    };

    return (
        <div className="referral-page">
            <h2>👥 Реферальная система</h2>

            <div className="card">
                <h3>Ваш код</h3>
                <div className="code-display" onClick={handleCopyLink}>
                    {referralCode || "Загрузка..."}
                </div>
                <p className="hint">Нажмите, чтобы скопировать ссылку</p>
            </div>

            <div className="card stats-card">
                <h3>Статистика</h3>
                {/* Placeholder stats */}
                <div className="stat-row">
                    <span>Приглашено:</span>
                    <span>--</span>
                </div>
            </div>

            <div className="card custom-code-card">
                <h3>Настроить код</h3>
                <p className="small-text">Доступно при обороте &gt; $300</p>

                <input
                    type="text"
                    placeholder="Новый код (3-20 символов)"
                    value={customCode}
                    onChange={(e) => setCustomCode(e.target.value.toUpperCase())}
                />
                <button onClick={handleUpdateCode}>Сохранить</button>
                {message && <p className="status-msg">{message}</p>}
            </div>
        </div>
    );
};

export default Referral;
