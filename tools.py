from langchain.tools import tool
from typing import List
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




@tool(
   "search_professors",
   description="Search for professors by name, partial name, or fuzzy match. Use this when the student mentions a specific professor by name or when you need to resolve a name to a professor ID.",
   args_schema=SearchProfessorsInput
)
def search_professors(name: str) -> str:
   return "success"




@tool(
   "get_professor_details",
   description="Fetch full details for a specific professor by their UUID, including aggregated review stats. Use this after resolving a professor's ID via `search_professors` or `find_professors_by_course`.",
   args_schema=GetProfessorDetailsInput
)
def get_professor_details(professor_id: str) -> str:
   return "success"




@tool(
   "get_professor_reviews",
   description="Fetch recent or filtered reviews for a specific professor. Use this when the student wants qualitative insight — teaching style, workload, clarity, engagement — not just numeric ratings.",
   args_schema=GetProfessorReviewsInput
)
def get_professor_reviews(professor_id: str, limit: int = 10, course: str = None) -> str:
   return "success"




@tool(
   "find_professors_by_course",
   description="Find all professors who have taught a specific course, identified by course code or name. Use this when the student asks about a specific course (e.g. \"ECS 36C\", \"MAT 21A\").",
   args_schema=FindProfessorsByCourseInput
)
def find_professors_by_course(course_code: str) -> str:
   return "success"




@tool(
   "get_top_professors_by_department",
   description="Retrieve the highest-rated professors in a given department, optionally filtered by minimum review count to ensure statistical reliability. Use this for broad department-level questions.",
   args_schema=GetTopProfessorsByDepartmentInput
)
def get_top_professors_by_department(department_name: str, limit: int = 5, min_reviews: int = 3) -> str:
   return "success"




@tool(
   "find_easy_professors",
   description="Find professors known for lighter workloads and higher grades. Ranks by a combination of low difficulty rating and high would-take-again percentage. Use this when the student explicitly wants an easier course experience.",
   args_schema=FindEasyProfessorsInput
)
def find_easy_professors(department_name: str = None, course_code: str = None, limit: int = 5) -> str:
   return "success"




@tool(
   "find_professors_by_teaching_style",
   description="Search reviews semantically for professors matching a described teaching style or quality. This tool performs keyword/tag matching across review comments and tags. Use this for qualitative, preference-based queries.",
   args_schema=FindProfessorsByTeachingStyleInput
)
def find_professors_by_teaching_style(keywords: str, department_name: str = None) -> str:
   return "success"




@tool(
   "compare_professors",
   description="Generate a side-by-side comparison of two or more professors. Pulls full stats and a summary of review sentiment for each. Use this when the student explicitly wants to compare options.",
   args_schema=CompareProfessorsInput
)
def compare_professors(professor_ids: List[str]) -> str:
   return "success"




@tool(
   "list_departments",
   description="Return all available departments. Use this to resolve ambiguous department names or when the student asks a broad question without specifying a department."
)
def list_departments() -> str:
   return "success"
