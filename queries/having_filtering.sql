-- CyberGuard HAVING Filtering Query
-- Filters IP addresses with 5 or more failed login attempts
SELECT 
    ip_address,
    country,
    COUNT(*) as total_failed_attempts,
    MIN(timestamp) as first_failure,
    MAX(timestamp) as last_failure
FROM auth_events
WHERE status = 'Failed'
GROUP BY ip_address, country
HAVING COUNT(*) >= 5
ORDER BY total_failed_attempts DESC;
