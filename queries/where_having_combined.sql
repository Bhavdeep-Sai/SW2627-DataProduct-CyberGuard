-- CyberGuard Combined WHERE and HAVING Filtering Query
-- Filters failed events originating from high-risk countries and groups by IP address
SELECT 
    ip_address,
    country,
    COUNT(*) as failed_attempts,
    AVG(risk_score) as avg_risk_score
FROM auth_events
WHERE status = 'Failed' AND country IN ('RU', 'CN', 'BR')
GROUP BY ip_address, country
HAVING COUNT(*) >= 3
ORDER BY avg_risk_score DESC;
