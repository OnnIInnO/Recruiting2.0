from typing import Dict, List, Tuple
import numpy as np
from .dimensions import AssessmentType, AssessmentDimensions


class MatchingSystem:
    """
    Handles matching logic between candidates and jobs/companies
    """

    def __init__(self):
        self.dimensions = AssessmentDimensions()

    def calculate_match(self, completed_profiles, job_requirements, company_profiles):
        matches = {}
        total_weight = 0

        # Calculate skills match if available
        if (
            "skills_profile" in completed_profiles
            and "skills_requirements" in job_requirements
        ):
            matches["skills_match"] = self._calculate_skills_match(
                completed_profiles["skills_profile"],
                job_requirements["skills_requirements"],
            )
            total_weight += 0.4

        # Calculate wellbeing match if available
        if (
            "wellbeing_profile" in completed_profiles
            and "wellbeing_preferences" in job_requirements
        ):
            matches["wellbeing_match"] = self._calculate_wellbeing_match(
                completed_profiles["wellbeing_profile"],
                job_requirements["wellbeing_preferences"],
            )
            total_weight += 0.3

        # Calculate values match if available
        if (
            "values_profile" in completed_profiles
            and "values_profile" in company_profiles
        ):
            matches["values_match"] = self._calculate_values_match(
                completed_profiles["values_profile"], company_profiles["values_profile"]
            )
            total_weight += 0.3

        # Calculate normalized overall match
        if total_weight > 0:
            overall_match = (
                sum(
                    score * weight
                    for score, weight in [
                        (matches.get("skills_match", 0), 0.4),
                        (matches.get("wellbeing_match", 0), 0.3),
                        (matches.get("values_match", 0), 0.3),
                    ]
                    if score > 0
                )
                / total_weight
            )
        else:
            overall_match = 0

        return {
            "overall_match": overall_match,
            **matches,
            "dimensions_matched": list(matches.keys()),
        }

    def _calculate_profile_match(
        self, profile1: Dict, profile2: Dict, profile_type: AssessmentType
    ) -> Dict:
        """Calculate match between two profiles of same type"""
        dimensions = self.dimensions.get_dimensions(profile_type)
        dimension_matches = {}
        dimension_scores = []

        for dim_key, dimension in dimensions.items():
            score1 = profile1.get(dim_key, {}).get("score", 0)
            score2 = profile2.get(dim_key, {}).get("score", 0)

            # Calculate match score
            if profile_type == AssessmentType.SKILLS:
                # For skills, only penalize if candidate scores lower than requirement
                match = max(0, 1 - max(0, score2 - score1) / 10)
            else:
                # For wellbeing and values, look for alignment within tolerance
                match = 1 - abs(score1 - score2) / 10

            dimension_matches[dim_key] = {
                "match": match,
                "title": dimension["title"],
                "description": dimension["description"],
            }
            dimension_scores.append(match)

        return {"overall": np.mean(dimension_scores), "dimensions": dimension_matches}

    def _generate_insights(
        self, wellbeing_match: Dict, skills_match: Dict, values_match: Dict
    ) -> List[str]:
        """Generate insights based on match scores"""
        insights = []

        # Add specific insights based on strong matches or gaps
        for match_type, match_data in [
            ("Skills", skills_match),
            ("Wellbeing", wellbeing_match),
            ("Values", values_match),
        ]:
            for dim, data in match_data["dimensions"].items():
                if data["match"] > 0.8:
                    insights.append(
                        f"Strong {match_type.lower()} match in {data['title']}"
                    )
                elif data["match"] < 0.6:
                    insights.append(
                        f"Consider alignment in {data['title']} "
                        f"({data['description']})"
                    )

        return insights

    def get_recommendations(
        self, candidate_profiles: Dict, available_jobs: List[Dict]
    ) -> List[Tuple[Dict, float]]:
        """Get job recommendations sorted by match score"""
        job_matches = []

        for job in available_jobs:
            match_score = self.calculate_match(
                candidate_profiles, job["requirements"], job["company_profile"]
            )
            job_matches.append((job, match_score["overall_match"]))

        # Sort by match score
        job_matches.sort(key=lambda x: x[1], reverse=True)
        return job_matches
