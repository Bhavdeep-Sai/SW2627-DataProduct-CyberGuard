-- CyberGuard Window Analytics Query
-- Computes lagged timestamp, lagged country, and running login counts per user
SELECT 
    event_id,
    timestamp,
    username,
    ip_address,
    country,
    status,
    LAG(timestamp, 1) OVER (PARTITION BY username ORDER BY timestamp) as prev_login_time,
    LAG(country, 1) OVER (PARTITION BY username ORDER BY timestamp) as prev_country,
    COUNT(*) OVER (PARTITION BY username ORDER BY timestamp RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) as running_user_logins
FROM auth_events
ORDER BY timestamp DESC;
