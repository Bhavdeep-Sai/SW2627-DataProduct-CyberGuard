-- CyberGuard WHERE Filtering Query
-- Selects high severity alerts (CRITICAL or HIGH)
SELECT 
    timestamp,
    username,
    ip_address,
    country,
    threat_vector,
    risk_score,
    severity,
    primary_reason
FROM auth_events
WHERE severity IN ('CRITICAL', 'HIGH')
ORDER BY risk_score DESC;
