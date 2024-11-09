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

        # Calculate individual dimension matches if profiles exist
        if "wellbeing_profile" in user_profiles:
            matches["wellbeing_match"] = self._calculate_dimension_match(
                user_profiles["wellbeing_profile"],
                job_requirements.get("wellbeing_preferences", {}),
                company_profiles.get("wellbeing_profile", {}),
                "wellbeing",
            )
            logger.info(f"Wellbeing match score: {matches.get('wellbeing_match')}")

        if "skills_profile" in user_profiles:
            matches["skills_match"] = self._calculate_dimension_match(
                user_profiles["skills_profile"],
                job_requirements.get("skills_requirements", {}),
                company_profiles.get("skills_profile", {}),
                "skills",
            )
            logger.info(f"Skills match score: {matches.get('skills_match')}")

        if "values_profile" in user_profiles:
            matches["values_match"] = self._calculate_dimension_match(
                user_profiles["values_profile"],
                job_requirements.get("values_alignment", {}),
                company_profiles.get("values_profile", {}),
                "values",
            )
            logger.info(f"Values match score: {matches.get('values_match')}")

        # Calculate overall match score
        total_weight = 0
        weighted_sum = 0

        for match_type, weight in weights.items():
            match_key = f"{match_type}_match"
            if match_key in matches:
                weighted_sum += matches[match_key] * weight
                total_weight += weight

        matches["overall_match"] = (
            weighted_sum / total_weight if total_weight > 0 else 0.0
        )
        logger.info(f"Final matches: {matches}")

        return matches

    def _calculate_dimension_match(
        self,
        user_profile: Dict,
        job_requirements: Dict,
        company_profile: Dict,
        dimension_type: str,
    ) -> float:
        """Calculate match score for any dimension type"""
        logger.info(
            f"Starting {dimension_type} calculation with user profile: {user_profile}"
        )

        dimensions = list(
            set(user_profile.keys())
            | set(job_requirements.keys())
            | set(company_profile.keys())
        )

        dimension_scores = []

        for dimension in dimensions:
            if dimension not in user_profile:
                continue

            # Get scores (all are just simple scores now, no min/preferred)
            user_score = user_profile[dimension].get("score", 0)
            job_score = job_requirements.get(dimension, {}).get("score", 0)
            company_score = company_profile.get(dimension, {}).get("score", 0)

            # Normalize scores to 0-1 range
            user_score = user_score / 10.0
            job_score = job_score / 10.0
            company_score = company_score / 10.0

            logger.info(
                f"""
            Dimension {dimension}:
            User score: {user_score}
            Job score: {job_score}
            Company score: {company_score}
            """
            )

            # Calculate differences (with asymmetric penalties)
            job_diff = user_score - job_score
            company_diff = user_score - company_score

            # Calculate match scores with asymmetric penalties
            # Under = full penalty, Over = half penalty
            if job_diff < 0:
                job_match = 1.0 + job_diff  # Full penalty for being under
            else:
                job_match = 1.0 - (job_diff * 0.5)  # Half penalty for being over

            if company_diff < 0:
                company_match = 1.0 + company_diff
            else:
                company_match = 1.0 - (company_diff * 0.5)

            # Combine job (60%) and company (40%) matches
            dimension_match = (job_match * 0.6) + (company_match * 0.4)
            dimension_match = max(0.0, min(1.0, dimension_match))

            dimension_scores.append(dimension_match)

            logger.info(
                f"""
            Dimension {dimension} matches:
            Job match: {job_match}
            Company match: {company_match}
            Final dimension match: {dimension_match}
            """
            )

        if not dimension_scores:
            return 0.0

        final_score = sum(dimension_scores) / len(dimension_scores)
        logger.info(f"Final {dimension_type} match score: {final_score}")

        return final_score
