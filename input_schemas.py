from pydantic import BaseModel, Field
from typing import Optional, List




class SearchProfessorsInput(BaseModel):
   name: str = Field(..., description="Full or partial professor name (e.g. 'Sarah Chen', 'Johnson')")




class GetProfessorDetailsInput(BaseModel):
   professor_id: str = Field(..., description="UUID of the professor")




class GetProfessorReviewsInput(BaseModel):
   professor_id: str = Field(..., description="UUID of the professor")
   limit: Optional[int] = Field(10, description="Number of reviews to return (default 10)")
   course: Optional[str] = Field(None, description="Optional filter to reviews for a specific course")




class FindProfessorsByCourseInput(BaseModel):
   course_code: str = Field(..., description="Course identifier (e.g. 'ECS 36C', 'MAT 21A')")




class GetTopProfessorsByDepartmentInput(BaseModel):
   department_name: str = Field(..., description="Full or partial department name (e.g. 'Computer Science', 'Biology', 'Mathematics')")
   limit: Optional[int] = Field(5, description="Number of professors to return (default 5)")
   min_reviews: Optional[int] = Field(3, description="Minimum review count to qualify (default 3)")




class FindEasyProfessorsInput(BaseModel):
   department_name: Optional[str] = Field(None, description="Optional filter by department")
   course_code: Optional[str] = Field(None, description="Optional filter by course")
   limit: Optional[int] = Field(5, description="Number of results (default 5)")




class FindProfessorsByTeachingStyleInput(BaseModel):
   keywords: str = Field(..., description="Teaching traits to search for (e.g. 'real-world examples', 'clear explanations', 'engaging', 'tough but fair')")
   department_name: Optional[str] = Field(None, description="Optional department filter")




class CompareProfessorsInput(BaseModel):
   professor_ids: List[str] = Field(..., description="List of 2–4 professor UUIDs to compare", min_length=2, max_length=4)


