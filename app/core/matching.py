# app/core/matching.py
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class MatchingSystem:
    def calculate_match(
        self, user_profiles: Dict, job_requirements: Dict, company_profiles: Dict
    ) -> Dict[str, float]:
        """Calculate overall match score based on available profiles"""
        logger.info(f"Starting match calculation with user_profiles: {user_profiles}")
        matches = {}
        weights = {"skills": 0.4, "wellbeing": 0.3, "values": 0.3}

        # Calculate wellbeing match if profile exists
        if "wellbeing_profile" in user_profiles:
            logger.info(f"Raw wellbeing profile: {user_profiles['wellbeing_profile']}")
            matches["wellbeing_match"] = self._calculate_wellbeing_match(
                user_profiles["wellbeing_profile"],
                job_requirements.get("wellbeing_preferences", {}),
                company_profiles.get("wellbeing_profile", {}),
            )
            logger.info(f"Wellbeing match score: {matches.get('wellbeing_match')}")

        matches["overall_match"] = matches.get("wellbeing_match", 0.0)
        return matches

    def _calculate_wellbeing_match(
        self, user_profile: Dict, job_preferences: Dict, company_profile: Dict
    ) -> float:
        """Calculate match score for wellbeing dimensions"""
        logger.info(f"Starting wellbeing calculation with user profile: {user_profile}")

        dimensions = [
            "AUTONOMY",
            "MASTERY",
            "RELATEDNESS",
            "WORK_LIFE",
            "PURPOSE",
            "PSYCHOLOGICAL_SAFETY",
        ]
        dimension_scores = {}

        # Handle the profile structure
        for dimension in dimensions:
            if dimension in user_profile:
                dimension_data = user_profile[dimension]
                if isinstance(dimension_data, dict) and "score" in dimension_data:
                    score = float(dimension_data["score"])
                    normalized_score = min(
                        max(score / 10.0, 0.0), 1.0
                    )  # Ensure score is between 0 and 1
                    dimension_scores[dimension] = normalized_score
                    logger.info(
                        f"Processed {dimension} score: {score} (normalized: {normalized_score})"
                    )

        logger.info(f"Calculated dimension scores: {dimension_scores}")

        # If we have no dimension scores, return 0
        if not dimension_scores:
            logger.info("No dimension scores calculated, returning 0")
            return 0.0

        # Calculate match score considering job preferences if they exist
        if job_preferences:
            match_scores = []
            for dimension, score in dimension_scores.items():
                job_min = job_preferences.get(dimension, {}).get("minimum", 0.5)
                company_score = company_profile.get(dimension, {}).get(
                    "score", score
                )  # Default to user score if no company score

                # Normalize company score
                company_score = min(max(company_score / 10.0, 0.0), 1.0)

                # Calculate base match score
                if score >= job_min:
                    # Full points for meeting minimum plus bonus for company alignment
                    company_alignment = 1.0 - abs(
                        score - company_score
                    )  # Simplified alignment calculation
                    dimension_match = 0.7 + (
                        0.3 * company_alignment
                    )  # 70% for meeting minimum, 30% for alignment
                else:
                    # Partial credit for being close to minimum
                    dimension_match = max(
                        0.0, min(1.0, score / job_min * 0.7)
                    )  # Cap at 70% if below minimum

                match_scores.append(dimension_match)
                logger.info(f"Dimension {dimension} match: {dimension_match}")

            final_score = sum(match_scores) / len(match_scores)
        else:
            # If no job preferences, use normalized dimension scores directly
            final_score = sum(dimension_scores.values()) / len(dimension_scores)

        # Ensure final score is between 0 and 1
        final_score = min(max(final_score, 0.0), 1.0)

        logger.info(f"Final wellbeing match score: {final_score}")
        return final_score
