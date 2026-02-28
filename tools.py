"""
Compass AI tools for querying professor and department data from Supabase.
Uses fuzzy matching (80% threshold) for professor name search.
"""

import json
import os
from typing import List, Optional

import logging
from dotenv import load_dotenv
from langchain.tools import tool
from rapidfuzz import fuzz

from supabase import create_client, Client

from input_schemas import (
    SearchProfessorsInput,
    GetProfessorDetailsInput,
    GetProfessorReviewsInput,
    FindProfessorsByCourseInput,
    GetTopProfessorsByDepartmentInput,
    FindEasyProfessorsInput,
    FindProfessorsByTeachingStyleInput,
    CompareProfessorsInput,
)

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Fuzzy match threshold: 80% similarity or above
FUZZY_MATCH_THRESHOLD = 80


def get_supabase() -> Client:
    """Return Supabase client instance."""
    url = os.getenv("SUPABASE_URL", "").strip()
    key = os.getenv("SUPABASE_SECRET_KEY", "").strip()
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_SECRET_KEY must be set in .env")
    return create_client(url, key)


@tool(
    "search_professors",
    description="Search for professors by name, partial name, or fuzzy match. Use this when the student mentions a specific professor by name or when you need to resolve a name to a professor ID. Fuzzy matching returns professors with 80% or higher name similarity.",
    args_schema=SearchProfessorsInput,
)
def search_professors(name: str) -> str:
    logger.info(f"[TOOL CALL] - search_professors(name={name})")
    try:
        sb = get_supabase()
        # Fetch all professors with department info for fuzzy matching
        resp = (
            sb.table("professors")
            .select("id, name, overall_rating, difficulty_rating, would_take_again_percentage, profile_url, department_id, departments(name)")
            .execute()
        )
        professors = resp.data or []

        # Apply fuzzy matching with 80% threshold
        name_lower = name.strip().lower()
        if not name_lower:
            return json.dumps({"error": "Empty search name"}, indent=2)

        matches = []
        for p in professors:
            prof_name = p.get("name") or ""
            # Use WRatio: handles partial matches, different lengths, and typos
            score = fuzz.WRatio(name_lower, prof_name.lower())
            if score >= FUZZY_MATCH_THRESHOLD:
                dept = p.get("departments")
                dept_name = (dept.get("name") or "") if isinstance(dept, dict) else ""
                matches.append(
                    {
                        "id": str(p["id"]),
                        "name": prof_name,
                        "department": dept_name,
                        "overall_rating": p.get("overall_rating"),
                        "difficulty_rating": p.get("difficulty_rating"),
                        "would_take_again_percentage": p.get("would_take_again_percentage"),
                        "profile_url": p.get("profile_url"),
                        "fuzzy_score": score,
                    }
                )

        matches.sort(key=lambda x: x["fuzzy_score"], reverse=True)
        return json.dumps(matches, indent=2) if matches else json.dumps({"message": "No professors found matching that name (fuzzy threshold: 80%)"}, indent=2)
    except Exception as e:
        logger.exception("search_professors failed")
        return json.dumps({"error": str(e)}, indent=2)


@tool(
    "get_professor_details",
    description="Fetch full details for a specific professor by their UUID, including aggregated review stats. Use this after resolving a professor's ID via `search_professors` or `find_professors_by_course`.",
    args_schema=GetProfessorDetailsInput,
)
def get_professor_details(professor_id: str) -> str:
    logger.info(f"[TOOL CALL] - get_professor_details(professor_id={professor_id})")
    try:
        sb = get_supabase()
        resp = (
            sb.table("professors")
            .select("*, departments(name, code)")
            .eq("id", professor_id)
            .maybe_single()
            .execute()
        )
        p = resp.data
        if not p:
            return json.dumps({"error": "Professor not found"}, indent=2)

        # Get review stats
        rev_resp = sb.table("reviews").select("rating, difficulty", count="exact").eq("professor_id", professor_id).execute()
        reviews = rev_resp.data or []
        count = getattr(rev_resp, "count", None) or len(reviews)

        avg_rating = round(sum(r.get("rating") or 0 for r in reviews) / len(reviews), 1) if reviews else None
        avg_difficulty = round(sum(r.get("difficulty") or 0 for r in reviews) / len(reviews), 1) if reviews else None

        dept = p.get("departments") or {}
        dept_name = dept.get("name") if isinstance(dept, dict) else ""

        out = {
            "id": str(p["id"]),
            "name": p.get("name"),
            "department": dept_name,
            "overall_rating": p.get("overall_rating"),
            "difficulty_rating": p.get("difficulty_rating"),
            "would_take_again_percentage": p.get("would_take_again_percentage"),
            "profile_url": p.get("profile_url"),
            "review_count": count,
            "avg_rating": avg_rating,
            "avg_difficulty": avg_difficulty,
        }
        return json.dumps(out, indent=2)
    except Exception as e:
        logger.exception("get_professor_details failed")
        return json.dumps({"error": str(e)}, indent=2)


@tool(
    "get_professor_reviews",
    description="Fetch recent or filtered reviews for a specific professor. Use this when the student wants qualitative insight — teaching style, workload, clarity, engagement — not just numeric ratings.",
    args_schema=GetProfessorReviewsInput,
)
def get_professor_reviews(professor_id: str, limit: int = 10, course: Optional[str] = None) -> str:
    logger.info(f"[TOOL CALL] - get_professor_reviews(professor_id={professor_id}, limit={limit}, course={course})")
    try:
        sb = get_supabase()
        q = sb.table("reviews").select("rating, difficulty, comment, course, tags, review_date").eq("professor_id", professor_id).order("review_date", desc=True).limit(limit)
        if course:
            q = q.ilike("course", f"%{course}%")
        resp = q.execute()
        reviews = resp.data or []
        return json.dumps(reviews, indent=2)
    except Exception as e:
        logger.exception("get_professor_reviews failed")
        return json.dumps({"error": str(e)}, indent=2)


@tool(
    "find_professors_by_course",
    description="Find all professors who have taught a specific course, identified by course code or name. Use this when the student asks about a specific course (e.g. 'ECS 36C', 'MAT 21A').",
    args_schema=FindProfessorsByCourseInput,
)
def find_professors_by_course(course_code: str) -> str:
    logger.info(f"[TOOL CALL] - find_professors_by_course(course_code={course_code})")
    try:
        sb = get_supabase()
        # Get reviews for this course, then fetch professor details
        rev_resp = sb.table("reviews").select("professor_id").ilike("course", f"%{course_code}%").execute()
        prof_ids = list({r["professor_id"] for r in (rev_resp.data or [])})
        if not prof_ids:
            return json.dumps({"message": f"No professors found for course {course_code}"}, indent=2)

        prof_resp = sb.table("professors").select("id, name, overall_rating, difficulty_rating, would_take_again_percentage, departments(name)").in_("id", prof_ids).execute()
        professors = prof_resp.data or []

        # Compute course-specific stats per professor
        results = []
        for p in professors:
            pid = p["id"]
            course_reviews = [r for r in (rev_resp.data or []) if r["professor_id"] == pid]
            ratings = [r.get("rating") for r in course_reviews if r.get("rating") is not None]
            avg = round(sum(ratings) / len(ratings), 1) if ratings else None
            dept = p.get("departments") or {}
            dept_name = dept.get("name") if isinstance(dept, dict) else ""
            results.append(
                {
                    "id": str(p["id"]),
                    "name": p.get("name"),
                    "department": dept_name,
                    "overall_rating": p.get("overall_rating"),
                    "difficulty_rating": p.get("difficulty_rating"),
                    "would_take_again_percentage": p.get("would_take_again_percentage"),
                    "course_review_count": len(course_reviews),
                    "course_avg_rating": avg,
                }
            )

        results.sort(key=lambda x: (x["course_avg_rating"] or 0), reverse=True)
        return json.dumps(results, indent=2)
    except Exception as e:
        logger.exception("find_professors_by_course failed")
        return json.dumps({"error": str(e)}, indent=2)


@tool(
    "get_top_professors_by_department",
    description="Retrieve the highest-rated professors in a given department, optionally filtered by minimum review count. Use this for broad department-level questions.",
    args_schema=GetTopProfessorsByDepartmentInput,
)
def get_top_professors_by_department(department_name: str, limit: int = 5, min_reviews: int = 3) -> str:
    logger.info(f"[TOOL CALL] - get_top_professors_by_department(department_name={department_name}, limit={limit}, min_reviews={min_reviews})")
    try:
        sb = get_supabase()
        # Resolve department by name
        dept_resp = sb.table("departments").select("id").ilike("name", f"%{department_name}%").execute()
        depts = dept_resp.data or []
        if not depts:
            return json.dumps({"message": f"No department found matching '{department_name}'"}, indent=2)
        dept_ids = [d["id"] for d in depts]

        prof_resp = sb.table("professors").select("id, name, overall_rating, difficulty_rating, would_take_again_percentage, departments(name)").in_("department_id", dept_ids).execute()
        professors = prof_resp.data or []

        results = []
        for p in professors:
            rev_resp = sb.table("reviews").select("professor_id").eq("professor_id", p["id"]).execute()
            count = len(rev_resp.data or [])
            if count < min_reviews:
                continue
            dept = p.get("departments") or {}
            dept_name = dept.get("name") if isinstance(dept, dict) else ""
            results.append(
                {
                    "id": str(p["id"]),
                    "name": p.get("name"),
                    "department": dept_name,
                    "overall_rating": p.get("overall_rating"),
                    "difficulty_rating": p.get("difficulty_rating"),
                    "would_take_again_percentage": p.get("would_take_again_percentage"),
                    "review_count": count,
                }
            )

        results.sort(key=lambda x: (x["overall_rating"] or 0), reverse=True)
        return json.dumps(results[:limit], indent=2)
    except Exception as e:
        logger.exception("get_top_professors_by_department failed")
        return json.dumps({"error": str(e)}, indent=2)


@tool(
    "find_easy_professors",
    description="Find professors known for lighter workloads and higher grades. Ranks by low difficulty and high would-take-again percentage. Use when the student wants an easier course experience.",
    args_schema=FindEasyProfessorsInput,
)
def find_easy_professors(department_name: Optional[str] = None, course_code: Optional[str] = None, limit: int = 5) -> str:
    logger.info(f"[TOOL CALL] - find_easy_professors(department_name={department_name}, course_code={course_code}, limit={limit})")
    try:
        sb = get_supabase()
        q = sb.table("professors").select("id, name, overall_rating, difficulty_rating, would_take_again_percentage, departments(name)")
        if department_name:
            dept_resp = sb.table("departments").select("id").ilike("name", f"%{department_name}%").execute()
            dept_ids = [d["id"] for d in (dept_resp.data or [])]
            if dept_ids:
                q = q.in_("department_id", dept_ids)
            else:
                return json.dumps({"message": f"No department found matching '{department_name}'"}, indent=2)
        resp = q.order("difficulty_rating").limit(limit * 3).execute()
        professors = resp.data or []

        if course_code:
            rev_resp = sb.table("reviews").select("professor_id").ilike("course", f"%{course_code}%").execute()
            course_prof_ids = {r["professor_id"] for r in (rev_resp.data or [])}
            professors = [p for p in professors if p["id"] in course_prof_ids]

        # Sort by difficulty asc, then would_take_again desc
        professors.sort(key=lambda x: (x.get("difficulty_rating") or 99, -(x.get("would_take_again_percentage") or 0)))

        out = []
        for p in professors[:limit]:
            dept = p.get("departments") or {}
            dept_name = dept.get("name") if isinstance(dept, dict) else ""
            out.append(
                {
                    "id": str(p["id"]),
                    "name": p.get("name"),
                    "department": dept_name,
                    "difficulty_rating": p.get("difficulty_rating"),
                    "would_take_again_percentage": p.get("would_take_again_percentage"),
                    "overall_rating": p.get("overall_rating"),
                }
            )
        return json.dumps(out, indent=2)
    except Exception as e:
        logger.exception("find_easy_professors failed")
        return json.dumps({"error": str(e)}, indent=2)


@tool(
    "find_professors_by_teaching_style",
    description="Search reviews for professors matching teaching style keywords. Use for qualitative, preference-based queries.",
    args_schema=FindProfessorsByTeachingStyleInput,
)
def find_professors_by_teaching_style(keywords: str, department_name: Optional[str] = None) -> str:
    logger.info(f"[TOOL CALL] - find_professors_by_teaching_style(keywords={keywords}, department_name={department_name})")
    try:
        sb = get_supabase()
        kw_list = [k.strip() for k in keywords.split(",") if k.strip()]
        if not kw_list:
            return json.dumps({"message": "Please provide at least one keyword"}, indent=2)

        # Query for each keyword and merge professor_ids
        all_reviews = []
        for kw in kw_list:
            resp = sb.table("reviews").select("professor_id, comment, tags").ilike("comment", f"%{kw}%").execute()
            all_reviews.extend(resp.data or [])
            # Also check tags array (contains)
            resp2 = sb.table("reviews").select("professor_id, comment, tags").contains("tags", [kw]).execute()
            all_reviews.extend(resp2.data or [])
        prof_ids = list({r["professor_id"] for r in all_reviews})
        if not prof_ids:
            return json.dumps({"message": "No professors found matching those teaching style keywords"}, indent=2)

        prof_q = sb.table("professors").select("id, name, overall_rating, departments(name)").in_("id", prof_ids)
        if department_name:
            dept_resp = sb.table("departments").select("id").ilike("name", f"%{department_name}%").execute()
            dept_ids = [d["id"] for d in (dept_resp.data or [])]
            if dept_ids:
                prof_q = prof_q.in_("department_id", dept_ids)
        prof_resp = prof_q.execute()
        professors = prof_resp.data or []

        # Count matches per professor
        match_counts = {}
        for r in all_reviews:
            pid = r["professor_id"]
            match_counts[pid] = match_counts.get(pid, 0) + 1

        results = []
        for p in professors:
            dept = p.get("departments") or {}
            dept_name = dept.get("name") if isinstance(dept, dict) else ""
            results.append(
                {
                    "id": str(p["id"]),
                    "name": p.get("name"),
                    "department": dept_name,
                    "overall_rating": p.get("overall_rating"),
                    "match_count": match_counts.get(p["id"], 0),
                }
            )
        results.sort(key=lambda x: x["match_count"], reverse=True)
        return json.dumps(results[:5], indent=2)
    except Exception as e:
        logger.exception("find_professors_by_teaching_style failed")
        return json.dumps({"error": str(e)}, indent=2)


@tool(
    "compare_professors",
    description="Generate a side-by-side comparison of two or more professors. Use when the student explicitly wants to compare options.",
    args_schema=CompareProfessorsInput,
)
def compare_professors(professor_ids: List[str]) -> str:
    logger.info(f"[TOOL CALL] - compare_professors(professor_ids={professor_ids})")
    try:
        comparisons = []
        for pid in professor_ids[:4]:  # cap at 4
            detail_str = get_professor_details.invoke({"professor_id": pid})
            reviews_str = get_professor_reviews.invoke({"professor_id": pid, "limit": 3})
            try:
                detail = json.loads(detail_str)
                reviews = json.loads(reviews_str)
            except json.JSONDecodeError:
                detail = {"raw": detail_str}
                reviews = []
            comparisons.append({"details": detail, "reviews": reviews})
        return json.dumps(comparisons, indent=2)
    except Exception as e:
        logger.exception("compare_professors failed")
        return json.dumps({"error": str(e)}, indent=2)


@tool(
    "list_departments",
    description="Return all available departments. Use to resolve ambiguous department names or when the student asks a broad question.",
)
def list_departments() -> str:
    logger.info("[TOOL CALL] - list_departments()")
    try:
        sb = get_supabase()
        resp = sb.table("departments").select("name, code").order("name").execute()
        depts = resp.data or []
        return json.dumps(depts, indent=2)
    except Exception as e:
        logger.exception("list_departments failed")
        return json.dumps({"error": str(e)}, indent=2)
