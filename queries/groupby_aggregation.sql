-- CyberGuard Group By Aggregation Query
-- Groups authentication events by country and status with risk metrics
SELECT 
    country,
    status,
    COUNT(*) as attempt_count,
    ROUND(AVG(risk_score), 2) as avg_risk_score,
    MAX(risk_score) as peak_risk_score
FROM auth_events
GROUP BY country, status
ORDER BY attempt_count DESC;
