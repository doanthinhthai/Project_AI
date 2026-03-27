from .features import FeatureExtractor
from .weights import FEATURE_WEIGHTS, CHECK_BONUS
from core.constants import RED, BLACK


class Evaluation:
    @staticmethod
    def get_check_bonus(game_manager=None):
        if game_manager is None:
            return 0

        bonus = 0

        try:
            if game_manager.is_in_check(BLACK):
                bonus += CHECK_BONUS
            if game_manager.is_in_check(RED):
                bonus -= CHECK_BONUS
        except Exception:
            pass

        return bonus

    @staticmethod
    def combine(features, game_manager=None):
        score = 0

        for name, value in features.items():
            weight = FEATURE_WEIGHTS.get(name, 1.0)
            score += weight * value

        score += FEATURE_WEIGHTS["check_bonus"] * Evaluation.get_check_bonus(game_manager)
        return int(score)

    @staticmethod
    def evaluate(board, game_manager=None):
        features = FeatureExtractor.extract_all(board)
        return Evaluation.combine(features, game_manager)