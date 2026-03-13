import math

def calculate_organic_engagement(followers: int, aura: int, momentum_buff: bool = False, niche_bonus: float = 1.0) -> float:
    """
    Phase 24: Deep Calculus of Clout
    E(F,A) = F * (beta / ln(F + e)) * (1 + gamma * (A / 1000)) * niche_bonus
    beta: Baseline coefficient (0.05)
    gamma: Aura multiplier (1.0)
    
    If momentum_buff is True, beta is doubled (Phase 24.1).
    """
    beta = 0.05
    if momentum_buff:
        beta *= 2.0
        
    gamma = 1.0
    # e approx 2.71828
    engagement = followers * (beta / math.log(followers + 2.71828)) * (1 + gamma * (aura / 1000.0)) * niche_bonus
    return max(0.0, engagement)

def calculate_follower_change(current_followers: int, aura: int, virality_score: float = 0.0, base_momentum: float = 1.0) -> int:
    """
    Growth is now derived from Organic Engagement (E).
    """
    engagement = calculate_organic_engagement(current_followers, aura)
    
    # Growth scales with engagement and virality
    # If E is 50, and virality is 1.0, maybe they gain 10x E?
    growth = engagement * (1 + virality_score * 5.0) * base_momentum
    
    # Decay is higher for bigger accounts (churn)
    decay = current_followers * 0.001 # 0.1% daily churn baseline
    
    net_change = int(growth - decay)
    return net_change
