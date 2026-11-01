PROMPT_TEMPLATE = """You are a Senior Principal Engineer performing a deep forensic archaeology on a repository.

# REPOSITORY CONTEXT
Description: {description}
Lifespan: {first_commit_date} to {last_commit_date}
MANDATORY FOLDERS TO ANALYZE: {top_level_folders}
File Tree: {tree}
Recent Commits: {commits}
Evidence Files:
{key_files}

# TASK
Perform an exhaustive analysis. 

# CRITICAL CONSTRAINTS
- YOU MUST ANALYZE ONLY THE FOLDERS LISTED IN "MANDATORY FOLDERS TO ANALYZE". Do NOT hallucinate folders like "backend" or "frontend" if they are not in the list. If the list is "greenstep, inbox-sloth", your projects array MUST contain exactly those two.
- YOU ARE FORBIDDEN FROM USING WORDS LIKE "potentially", "likely", "appears to be". Deduce the tech stack accurately by reading the Evidence Files.
- For `ghost_commit`, return ONLY the commit message string (e.g., "chore: gave up"). Do NOT include the word "git commit -m".
- The `poetic_eulogy` must be strictly about CODE AND ARCHITECTURE (missing test coverage, unimplemented features), not vague poetry.
- RETURN ONLY VALID JSON. NO MARKDOWN.

# OUTPUT FORMAT
{{
  "repo_overview": "A detailed summary of the entire repository's purpose based on the files.",
  "global_tech_stack": "All languages and frameworks detected across the repo.",
  "projects": [
    {{
      "folder_name": "The name of the folder",
      "tech_stack": "Specific languages/frameworks for this folder.",
      "architecture_summary": "How is this specific project structured?",
      "core_components": "What are the main modules and how do they connect?",
      "entry_point": "Exact file path to start reading.",
      "critical_issues": "What is broken, missing, or outdated based on the files?",
      "resurrection_plan": ["Actionable step 1", "Actionable step 2"]
    }}
  ],
  "ghost_testimony": {{
    "poetic_eulogy": "A technical, melancholic 2-sentence summary of its death based on missing tests or unfinished code.",
    "abandonment_evidence": ["Technical evidence 1", "Technical evidence 2", "Technical evidence 3"],
    "ghost_commit": "A cynical commit message string only."
  }}
}}
"""