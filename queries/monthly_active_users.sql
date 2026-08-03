-- CyberGuard Monthly Active Authenticated Users Query
-- Groups authentications by year-month and counts active users
SELECT 
    STRFTIME('%Y-%m', timestamp) as activity_month,
    COUNT(DISTINCT username) as distinct_users,
    COUNT(*) as total_authentications,
    SUM(CASE WHEN status = 'Failed' THEN 1 ELSE 0 END) as total_failures
FROM auth_events
GROUP BY activity_month
ORDER BY activity_month DESC;
