# Compass AI — LangChain Agent Tools Specification


This document defines the tools available to the Compass AI LangChain agent. The agent uses these tools to answer student questions about UC Davis professors by querying the Supabase database.


---


## Agent Overview


The agent receives a natural language query from a student, decides which tools to call (and in what order), and synthesizes the results into a helpful recommendation. Tools are designed to be **composable** — the agent will often chain multiple tools together to answer a single question (e.g. look up a department, then find top professors in it, then fetch their recent reviews).


---


## Tools


---


### 1. `search_professors`


**Description:**
Search for professors by name, partial name, or fuzzy match. Use this when the student mentions a specific professor by name or when you need to resolve a name to a professor ID.


**Input:**
```json
{
 "name": "string — full or partial professor name (e.g. 'Sarah Chen', 'Johnson')"
}
```


**Pydantic Schema:**
```python
from pydantic import BaseModel, Field


class SearchProfessorsInput(BaseModel):
   name: str = Field(..., description="Full or partial professor name (e.g. 'Sarah Chen', 'Johnson')")
```


**Output:**
A list of matching professors with their `id`, `name`, `department`, `overall_rating`, `difficulty_rating`, `would_take_again_percentage`, and `profile_url`.


**Example triggers:**
- "Tell me about Professor Sarah Chen"
- "Compare Professor Johnson and Professor Martinez"
- "Who is Prof. Martinez?"


**SQL logic:**
```sql
SELECT p.id, p.name, d.name AS department,
      p.overall_rating, p.difficulty_rating,
      p.would_take_again_percentage, p.profile_url
FROM professors p
LEFT JOIN departments d ON p.department_id = d.id
WHERE p.name ILIKE '%<name>%';
```


---


### 2. `get_professor_details`


**Description:**
Fetch full details for a specific professor by their UUID, including aggregated review stats. Use this after resolving a professor's ID via `search_professors` or `find_professors_by_course`.


**Input:**
```json
{
 "professor_id": "string — UUID of the professor"
}
```


**Pydantic Schema:**
```python
from pydantic import BaseModel, Field


class GetProfessorDetailsInput(BaseModel):
   professor_id: str = Field(..., description="UUID of the professor")
```


**Output:**
Professor profile plus aggregated review stats: average rating, average difficulty, total review count, most common tags, and a sample of recent comments.


**Example triggers:**
- "Tell me about Professor Sarah Chen" (after resolving her ID)
- "What do students say about Johnson?"


**SQL logic:**
```sql
SELECT p.*, d.name AS department,
      COUNT(r.id) AS review_count,
      ROUND(AVG(r.rating), 1) AS avg_rating,
      ROUND(AVG(r.difficulty), 1) AS avg_difficulty
FROM professors p
LEFT JOIN departments d ON p.department_id = d.id
LEFT JOIN reviews r ON r.professor_id = p.id
WHERE p.id = '<professor_id>'
GROUP BY p.id, d.name;
```


---


### 3. `get_professor_reviews`


**Description:**
Fetch recent or filtered reviews for a specific professor. Use this when the student wants qualitative insight — teaching style, workload, clarity, engagement — not just numeric ratings.


**Input:**
```json
{
 "professor_id": "string — UUID of the professor",
 "limit": "integer — number of reviews to return (default 10)",
 "course": "string — optional, filter to reviews for a specific course"
}
```


**Pydantic Schema:**
```python
from pydantic import BaseModel, Field
from typing import Optional


class GetProfessorReviewsInput(BaseModel):
   professor_id: str = Field(..., description="UUID of the professor")
   limit: Optional[int] = Field(10, description="Number of reviews to return (default 10)")
   course: Optional[str] = Field(None, description="Optional filter to reviews for a specific course")
```


**Output:**
A list of reviews with `rating`, `difficulty`, `comment`, `course`, `tags`, and `review_date`.


**Example triggers:**
- "I learn best from professors who use real-world examples"
- "Are there any engaging lecturers in psychology?" (after finding candidates)
- "What do students say about his teaching style?"


**SQL logic:**
```sql
SELECT rating, difficulty, comment, course, tags, review_date
FROM reviews
WHERE professor_id = '<professor_id>'
 AND (<course> IS NULL OR course ILIKE '%<course>%')
ORDER BY review_date DESC
LIMIT <limit>;
```


---


### 4. `find_professors_by_course`


**Description:**
Find all professors who have taught a specific course, identified by course code or name. Use this when the student asks about a specific course (e.g. "ECS 36C", "MAT 21A").


**Input:**
```json
{
 "course_code": "string — course identifier (e.g. 'ECS 36C', 'MAT 21A')"
}
```


**Pydantic Schema:**
```python
from pydantic import BaseModel, Field


class FindProfessorsByCourseInput(BaseModel):
   course_code: str = Field(..., description="Course identifier (e.g. 'ECS 36C', 'MAT 21A')")
```


**Output:**
A list of professors who have reviews mentioning that course, along with their ratings and the number of reviews for that course specifically.


**Example triggers:**
- "Who's the best professor for ECS 36C?"
- "Who teaches MAT 21A and how are they rated?"
- "Compare Johnson and Martinez for ECS 50"


**SQL logic:**
```sql
SELECT p.id, p.name, p.overall_rating, p.difficulty_rating,
      p.would_take_again_percentage,
      COUNT(r.id) AS course_review_count,
      ROUND(AVG(r.rating), 1) AS course_avg_rating
FROM reviews r
JOIN professors p ON r.professor_id = p.id
WHERE r.course ILIKE '%<course_code>%'
GROUP BY p.id
ORDER BY course_avg_rating DESC;
```


---


### 5. `get_top_professors_by_department`


**Description:**
Retrieve the highest-rated professors in a given department, optionally filtered by minimum review count to ensure statistical reliability. Use this for broad department-level questions.


**Input:**
```json
{
 "department_name": "string — full or partial department name (e.g. 'Computer Science', 'Biology', 'Mathematics')",
 "limit": "integer — number of professors to return (default 5)",
 "min_reviews": "integer — minimum review count to qualify (default 3)"
}
```


**Pydantic Schema:**
```python
from pydantic import BaseModel, Field
from typing import Optional


class GetTopProfessorsByDepartmentInput(BaseModel):
   department_name: str = Field(..., description="Full or partial department name (e.g. 'Computer Science', 'Biology', 'Mathematics')")
   limit: Optional[int] = Field(5, description="Number of professors to return (default 5)")
   min_reviews: Optional[int] = Field(3, description="Minimum review count to qualify (default 3)")
```


**Output:**
Ranked list of professors with ratings, difficulty, would-take-again percentage, and review count.


**Example triggers:**
- "Who are the top-rated biology professors?"
- "I need to take a CS elective, who should I take it with?"
- "Are there any engaging lecturers in psychology?"


**SQL logic:**
```sql
SELECT p.id, p.name, p.overall_rating, p.difficulty_rating,
      p.would_take_again_percentage, COUNT(r.id) AS review_count
FROM professors p
JOIN departments d ON p.department_id = d.id
LEFT JOIN reviews r ON r.professor_id = p.id
WHERE d.name ILIKE '%<department_name>%'
GROUP BY p.id
HAVING COUNT(r.id) >= <min_reviews>
ORDER BY p.overall_rating DESC
LIMIT <limit>;
```


---


### 6. `find_easy_professors`


**Description:**
Find professors known for lighter workloads and higher grades. Ranks by a combination of low difficulty rating and high would-take-again percentage. Use this when the student explicitly wants an easier course experience.


**Input:**
```json
{
 "department_name": "string — optional, filter by department",
 "course_code": "string — optional, filter by course",
 "limit": "integer — number of results (default 5)"
}
```


**Pydantic Schema:**
```python
from pydantic import BaseModel, Field
from typing import Optional


class FindEasyProfessorsInput(BaseModel):
   department_name: Optional[str] = Field(None, description="Optional filter by department")
   course_code: Optional[str] = Field(None, description="Optional filter by course")
   limit: Optional[int] = Field(5, description="Number of results (default 5)")
```


**Output:**
Ranked list of professors sorted by lowest difficulty and highest would-take-again percentage, with supporting review tags (e.g. "Easy A", "Light workload").


**Example triggers:**
- "I want an easy A for my GE requirement"
- "Which math professor has the lightest workload?"


**SQL logic:**
```sql
SELECT p.id, p.name, d.name AS department,
      p.difficulty_rating, p.would_take_again_percentage,
      p.overall_rating
FROM professors p
LEFT JOIN departments d ON p.department_id = d.id
WHERE (<department_name> IS NULL OR d.name ILIKE '%<department_name>%')
ORDER BY p.difficulty_rating ASC,
        p.would_take_again_percentage DESC
LIMIT <limit>;
```


---


### 7. `find_professors_by_teaching_style`


**Description:**
Search reviews semantically for professors matching a described teaching style or quality. This tool performs keyword/tag matching across review comments and tags. Use this for qualitative, preference-based queries.


**Input:**
```json
{
 "keywords": "string — teaching traits to search for (e.g. 'real-world examples', 'clear explanations', 'engaging', 'tough but fair')",
 "department_name": "string — optional department filter"
}
```


**Pydantic Schema:**
```python
from pydantic import BaseModel, Field
from typing import Optional


class FindProfessorsByTeachingStyleInput(BaseModel):
   keywords: str = Field(..., description="Teaching traits to search for (e.g. 'real-world examples', 'clear explanations', 'engaging', 'tough but fair')")
   department_name: Optional[str] = Field(None, description="Optional department filter")
```


**Output:**
Professors whose reviews frequently mention the requested traits, with example matching comments and a match score (count of matching reviews).


**Example triggers:**
- "I learn best from professors who use lots of real-world examples"
- "I need a professor who's good at explaining complex topics clearly"
- "I want a challenging upper-division course, who should I look for?"
- "Are there any really engaging lecturers in psychology?"


**SQL logic:**
```sql
SELECT p.id, p.name, d.name AS department,
      p.overall_rating, COUNT(r.id) AS match_count,
      array_agg(r.comment ORDER BY r.review_date DESC) AS sample_comments
FROM reviews r
JOIN professors p ON r.professor_id = p.id
LEFT JOIN departments d ON p.department_id = d.id
WHERE r.comment ILIKE '%<keyword>%'
  OR '<keyword>' = ANY(r.tags)
 AND (<department_name> IS NULL OR d.name ILIKE '%<department_name>%')
GROUP BY p.id, d.name
ORDER BY match_count DESC
LIMIT 5;
```


---


### 8. `compare_professors`


**Description:**
Generate a side-by-side comparison of two or more professors. Pulls full stats and a summary of review sentiment for each. Use this when the student explicitly wants to compare options.


**Input:**
```json
{
 "professor_ids": "string[] — list of 2–4 professor UUIDs to compare"
}
```


**Pydantic Schema:**
```python
from pydantic import BaseModel, Field
from typing import List


class CompareProfessorsInput(BaseModel):
   professor_ids: List[str] = Field(..., description="List of 2–4 professor UUIDs to compare", min_items=2, max_items=4)
```


**Output:**
A structured comparison table with `name`, `department`, `overall_rating`, `difficulty_rating`, `would_take_again_percentage`, `review_count`, top tags, and a sample positive and negative comment for each professor.


**Example triggers:**
- "Compare Professor Johnson and Professor Martinez for ECS 50"


**Implementation note:** Calls `get_professor_details` and `get_professor_reviews` internally for each ID and formats results comparatively.


---


### 9. `list_departments`


**Description:**
Return all available departments. Use this to resolve ambiguous department names or when the student asks a broad question without specifying a department.


**Input:** None


**Pydantic Schema:**
```python
# No input schema needed - this tool takes no parameters
```


**Output:**
Full list of department names and codes.


**Example triggers:**
- Used internally when department name is ambiguous
- "What departments are available?"


**SQL logic:**
```sql
SELECT name, code FROM departments ORDER BY name;
```


---


## Tool Chaining Examples


| Student Query | Tool Chain |
|---|---|
| "Who's the best professor for ECS 36C?" | `find_professors_by_course` → `get_professor_details` |
| "I need a CS elective, who should I take?" | `get_top_professors_by_department(CS)` → `get_professor_reviews` |
| "Compare Johnson and Martinez for ECS 50" | `search_professors` x2 → `find_professors_by_course` → `compare_professors` |
| "I want an easy A for my GE" | `list_departments` → `find_easy_professors` |
| "I learn best with real-world examples" | `find_professors_by_teaching_style` → `get_professor_details` |
| "Tell me about Professor Sarah Chen" | `search_professors` → `get_professor_details` → `get_professor_reviews` |
| "Best biology professors?" | `get_top_professors_by_department(Biology)` → `get_professor_details` |


---


## Notes for Implementation


- All tools should be implemented as LangChain `Tool` or `StructuredTool` objects with Pydantic input schemas for reliable argument parsing.
- The agent should use **ReAct** or **OpenAI Functions** agent type for best tool-chaining behavior.
- `find_professors_by_teaching_style` is the most expensive query — consider adding a `LIMIT` on the subquery and caching frequent keyword searches.
- For semantic search improvements, consider embedding review comments with `pgvector` and replacing keyword matching in `find_professors_by_teaching_style` with a vector similarity search.
- Always resolve professor names to UUIDs before calling detail/review tools — never pass raw name strings to tools that expect an ID.2

