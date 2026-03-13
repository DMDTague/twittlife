import math
import numpy as np
from dictionaries import get_all_dict_keys

class FactionMath:
    """
    TwitLife Phase 24.1: Complex Multi-Agent Network Topology
    Calculates fandoms, beefs, cross-pollination, and algorithmic consequences.
    """

    @staticmethod
    def get_trait_vector(internal_truth: dict) -> list:
        """Converts internal_truth dict to a fixed-order trait vector."""
        all_keys = get_all_dict_keys()
        return [internal_truth.get(key, 0.0) for key in all_keys]

    @staticmethod
    def calculate_domain_similarity(vector_a: list, vector_b: list) -> float:
        """
        1. The Vector Space of Niches (Neutrality vs. Hostility)
        Uses Cosine Similarity to determine ideological distance.
        """
        vec_a = np.array(vector_a)
        vec_b = np.array(vector_b)
        
        dot_product = np.dot(vec_a, vec_b)
        norm_a = np.linalg.norm(vec_a)
        norm_b = np.linalg.norm(vec_b)

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return float(dot_product / (norm_a * norm_b))

    @staticmethod
    def calculate_stan_shield(f_total: int, a_current: int, a_peak: int, phi_fanaticism: float) -> int:
        """
        2. Audience Intersection & The "Stan" Shield
        Stans are immune to negative Aura. They will never unfollow you.
        """
        if a_peak <= 0:
            a_peak = 1500 # Default starting peek

        # Formula: F_stan = F_total * (A_current / A_peak)^phi
        # We ensure a_current doesn't drop below 1 for the math to work gracefully
        f_stan = f_total * math.pow((max(a_current, 1) / a_peak), phi_fanaticism)
        return int(f_stan)

    @staticmethod
    def calculate_viral_drama_multiplier(f_a: int, f_b: int, shared_audience: int, toxicity_coefficient: float) -> int:
        """
        3. The "Beef" Economy - Impressions Spike
        Initiating a public feud draws neutral eyes from outside both factions.
        """
        # Formula: I_beef = (F_A + F_B - |F_A intersect F_B|) * e^tau
        unique_audience = f_a + f_b - shared_audience
        i_beef = unique_audience * math.exp(toxicity_coefficient)
        return int(i_beef)

    @staticmethod
    def calculate_follower_migration(h_b: int, n_external: int, f_neutral_a: int, 
                                     rho: float, omega: float, sigma_actual: float) -> int:
        """
        3. The Migration Calculus (Follower Flow)
        Delta F_A = (rho * H_B) + (omega * N_external) - (sigma * F_neutral_A)
        """
        absorbed_haters = rho * h_b
        new_drama_fans = omega * n_external
        exhausted_moderates = sigma_actual * f_neutral_a

        delta_f_a = absorbed_haters + new_drama_fans - exhausted_moderates
        return int(delta_f_a)

    @staticmethod
    def calculate_net_conflict_score(likes: int, quote_tweets: int, ratios: int) -> int:
        """
        4. Winning or Losing the Beef (The Aura Tribunal)
        C_A = Sum(Likes * 1) + Sum(QTs * 2) - Sum(Ratios * 5)
        """
        c_a = (likes * 1) + (quote_tweets * 2) - (ratios * 5)
        return c_a

    @staticmethod
    def calculate_toxicity_fatigue(sigma_base: float, t_fatigue: int) -> float:
        """
        5. Advanced Metrics to Track (Toxicity Fatigue)
        sigma_actual = sigma_base * (1 + T_fatigue^2)
        """
        sigma_actual = sigma_base * (1 + math.pow(t_fatigue, 2))
        return sigma_actual
