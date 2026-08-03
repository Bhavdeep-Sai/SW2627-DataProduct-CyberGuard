"""
CyberGuard Analytical SQL Queries with Window Functions
"""

WINDOW_VELOCITY_QUERY = """
SELECT 
    event_id,
    timestamp,
    username,
    ip_address,
    country,
    status,
    LAG(timestamp, 1) OVER (PARTITION BY username ORDER BY timestamp) as prev_login_time,
    LAG(country, 1) OVER (PARTITION BY username ORDER BY timestamp) as prev_country,
    LAG(ip_address, 1) OVER (PARTITION BY username ORDER BY timestamp) as prev_ip,
    COUNT(*) OVER (PARTITION BY username ORDER BY timestamp RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) as cumulative_logins_per_user
FROM auth_events
ORDER BY timestamp DESC;
"""

BRUTE_FORCE_SQL = """
SELECT 
    username,
    ip_address,
    COUNT(*) as failed_attempts,
    MIN(timestamp) as burst_start,
    MAX(timestamp) as burst_end
FROM auth_events
WHERE status = 'Failed'
GROUP BY username, ip_address
HAVING COUNT(*) >= 5
ORDER BY failed_attempts DESC;
"""

USER_RISK_RANKING_SQL = """
SELECT 
    username,
    COUNT(*) as total_events,
    SUM(CASE WHEN status = 'Failed' THEN 1 ELSE 0 END) as total_failures,
    MAX(risk_score) as peak_risk_score,
    ROUND(AVG(risk_score), 2) as mean_risk_score,
    RANK() OVER (ORDER BY MAX(risk_score) DESC, COUNT(*) DESC) as risk_rank
FROM auth_events
GROUP BY username
ORDER BY risk_rank ASC;
"""
