import React, { useState, useEffect } from 'react';
import './Referral.css';
import { useTelegram } from '../hooks/useTelegram';

const Referral = () => {
    const { user, tg } = useTelegram();
    const [referralCode, setReferralCode] = useState('');
    const [customCode, setCustomCode] = useState('');
    const [stats, setStats] = useState({ totalTurnover: 0, referralCount: 0 }); // Placeholder for counts if API provided them
    const [loading, setLoading] = useState(true);
    const [message, setMessage] = useState('');

    // Fetch user data (logic to be added to DataContext or fetched directly)
    // For now, we reuse the /api/access-status or similar to get turnover, but code needs to be fetched.
    // We might need to update DataContext to return referral_code. 
    // For MVP, let's assume we can get it or we fetch it from a new endpoint.
    // Actually, let's update DataContext to include referral info if possible, or fetch separate.

    // Let's create a specialized fetch here or rely on props. 
    // Since we didn't add GET /api/referral, we might need to. 
    // Wait, let's add GET /api/user/profile to get this info or attach to access-status.

    // Pivot: I will add `referral_code` to the `/api/access-status` response in backend first.

    useEffect(() => {
        // Placeholder logic until backend is updated to return code
        // Assuming DataContext could provide this, but strict mode now.
        // I will write the frontend assuming the data exists, then go back update backend if missed.
        // Actually, I missed adding `referral_code` to the response in api/main.py. I should fix that.
        setLoading(false);
    }, []);

    const handleCopyLink = () => {
        const link = `https://t.me/AlihanBot?start=${referralCode || 'LOADING'}`;
        navigator.clipboard.writeText(link);
        tg.showPopup({ title: 'Ссылка скопирована', message: link, buttons: [{ type: 'ok' }] });
    };

    const handleUpdateCode = async () => {
        if (!customCode) return;
        try {
            const response = await fetch(`${import.meta.env.VITE_API_URL}/api/user/referral_code`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Telegram-Init-Data': tg.initData
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
