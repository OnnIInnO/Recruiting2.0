# app/core/matching.py
from typing import Dict, Any


class MatchingSystem:
    def calculate_match(
        self, user_profiles: Dict, job_requirements: Dict, company_profiles: Dict
    ) -> Dict[str, float]:
        """Calculate overall match score based on available profiles"""
        matches = {}
        weights = {"skills": 0.4, "wellbeing": 0.3, "values": 0.3}

        # Calculate individual dimension matches if profiles exist
        if (
            "skills_profile" in user_profiles
            and "skills_requirements" in job_requirements
        ):
            matches["skills_match"] = self._calculate_skills_match(
                user_profiles["skills_profile"], job_requirements["skills_requirements"]
            )

        if (
            "wellbeing_profile" in user_profiles
            and "wellbeing_preferences" in job_requirements
        ):
            matches["wellbeing_match"] = self._calculate_wellbeing_match(
                user_profiles["wellbeing_profile"],
                job_requirements["wellbeing_preferences"],
                company_profiles.get("wellbeing_profile", {}),
            )

        if "values_profile" in user_profiles and "values_alignment" in job_requirements:
            matches["values_match"] = self._calculate_values_match(
                user_profiles["values_profile"],
                job_requirements["values_alignment"],
                company_profiles.get("values_profile", {}),
            )

        # Calculate overall match score
        total_weight = 0
        weighted_sum = 0

        if "skills_match" in matches:
            weighted_sum += matches["skills_match"] * weights["skills"]
            total_weight += weights["skills"]

        if "wellbeing_match" in matches:
            weighted_sum += matches["wellbeing_match"] * weights["wellbeing"]
            total_weight += weights["wellbeing"]

        if "values_match" in matches:
            weighted_sum += matches["values_match"] * weights["values"]
            total_weight += weights["values"]

        # Normalize the overall score if we have any matches
        if total_weight > 0:
            matches["overall_match"] = weighted_sum / total_weight
        else:
            matches["overall_match"] = 0

        return matches

    def _calculate_wellbeing_match(
        self, user_profile: Dict, job_preferences: Dict, company_profile: Dict
    ) -> float:
        """Calculate match score for wellbeing dimensions"""
        dimensions = [
            "AUTONOMY",
            "MASTERY",
            "RELATEDNESS",
            "WORK_LIFE",
            "PURPOSE",
            "PSYCHOLOGICAL_SAFETY",
        ]
        total_score = 0
        counted_dimensions = 0

        for dimension in dimensions:
            user_score = 0
            dimension_count = 0

            # Calculate average score for the dimension from individual question scores
            for i in range(1, 4):  # Assuming 3 questions per dimension
                key = f"{dimension}_{i}"
                if key in user_profile:
                    user_score += user_profile[key]["score"]
                    dimension_count += 1

            if dimension_count > 0:
                avg_user_score = user_score / dimension_count
                # Compare with job preferences and company profile
                job_pref = job_preferences.get(dimension, {}).get("minimum", 0)
                company_score = company_profile.get(dimension, {}).get(
                    "score", avg_user_score
                )

                # Calculate match as percentage of meeting or exceeding requirements
                if job_pref > 0:
                    dimension_match = min(1.0, avg_user_score / job_pref)
                    total_score += dimension_match
                    counted_dimensions += 1

        if counted_dimensions > 0:
            return total_score / counted_dimensions
        return 0.0

    def _calculate_skills_match(
        self, user_profile: Dict, job_requirements: Dict
    ) -> float:
        """Calculate match score for skills"""
        if not job_requirements:
            return 1.0  # Perfect match if no requirements

        total_score = 0
        required_skills = len(job_requirements)

        for skill, required_level in job_requirements.items():
            user_level = user_profile.get(skill, {}).get("score", 0)
            if user_level >= required_level:
                total_score += 1
            else:
                total_score += user_level / required_level

        return total_score / required_skills if required_skills > 0 else 0.0

    def _calculate_values_match(
        self, user_profile: Dict, job_values: Dict, company_values: Dict
    ) -> float:
        """Calculate match score for values"""
        total_score = 0
        counted_values = 0

        # Compare user values with job and company values
        for value in (
            set(user_profile.keys())
            | set(job_values.keys())
            | set(company_values.keys())
        ):
            user_score = user_profile.get(value, {}).get("score", 0)
            job_importance = job_values.get(value, {}).get("importance", 0)
            company_score = company_values.get(value, {}).get("score", 0)

            if job_importance > 0:
                # Calculate match considering both job importance and company alignment
                value_match = min(
                    1.0, (user_score * 0.5 + company_score * 0.5) / job_importance
                )
                total_score += value_match
                counted_values += 1

        return total_score / counted_values if counted_values > 0 else 0.0
