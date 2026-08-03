-- CyberGuard Brute Force Threat Detection Query
-- Identifies users and IPs with 5+ failed login attempts
SELECT 
    username,
    ip_address,
    country,
    COUNT(*) as failed_attempts,
    MIN(timestamp) as attack_start,
    MAX(timestamp) as attack_end
FROM auth_events
WHERE status = 'Failed'
GROUP BY username, ip_address, country
HAVING COUNT(*) >= 5
ORDER BY failed_attempts DESC;
