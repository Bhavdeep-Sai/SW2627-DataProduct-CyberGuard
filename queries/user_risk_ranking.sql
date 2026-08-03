-- CyberGuard User Risk Ranking Query
-- Uses DENSE_RANK() window function to rank risky users based on peak risk scores and failure counts
SELECT 
    username,
    COUNT(*) as total_attempts,
    SUM(CASE WHEN status = 'Failed' THEN 1 ELSE 0 END) as failed_attempts,
    MAX(risk_score) as max_risk_score,
    ROUND(AVG(risk_score), 2) as avg_risk_score,
    DENSE_RANK() OVER (ORDER BY MAX(risk_score) DESC, COUNT(*) DESC) as security_risk_rank
FROM auth_events
GROUP BY username
ORDER BY security_risk_rank ASC;
