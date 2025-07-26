import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class PromptGenerator:
    """Generate prompts for various LLM tasks"""
    
    def __init__(self):
        logger.info("Initialized PromptGenerator")
    
    def generate_video_script_prompt(self, repo_analysis: Dict[str, Any]) -> str:
        """Generate a prompt for creating a video script about the repository"""
        try:
            repo_name = repo_analysis.get('repository_name', 'Unknown Repository')
            description = repo_analysis.get('description', 'A software repository')
            technologies = repo_analysis.get('technologies', [])
            features = repo_analysis.get('main_features', [])
            content_summary = repo_analysis.get('content_summary', '')
            
            # Format technologies and features for better prompt context
            tech_list = ', '.join(technologies[:6]) if technologies else 'Various modern technologies'
            feature_list = '\n'.join([f"- {feature}" for feature in features[:6]]) if features else "- Multiple innovative features"
            
            prompt = f"""Create a comprehensive and engaging video script for a repository overview video about '{repo_name}'.

Repository Information:
- Name: {repo_name}
- Description: {description}
- Technologies Used: {tech_list}
- Key Features:
{feature_list}

Repository Content Summary:
{content_summary[:1200]}

Requirements for the Video Script:
1. Create a 2-3 minute video script (approximately 300-450 words)
2. Use an engaging, professional tone suitable for developers and tech enthusiasts
3. Structure the script with clear timing sections:
   - Introduction (30 seconds) - Hook the audience and introduce the project
   - Main features and functionality (90 seconds) - Detailed overview of capabilities
   - Technical highlights (60 seconds) - Architecture, technologies, and implementation details
   - Conclusion (30 seconds) - Summary and call-to-action

4. Include natural transitions between sections
5. Make it informative yet accessible to both technical and non-technical audiences
6. Focus on practical benefits, use cases, and real-world applications
7. End with a compelling call-to-action encouraging exploration or contribution
8. Include timing cues in brackets like [0:00 - 0:30] for each section

Style Guidelines:
- Use conversational, engaging language
- Include specific details about the project's functionality
- Highlight what makes this repository unique or valuable
- Keep sentences clear and well-paced for narration
- Include enthusiasm and excitement about the project
- Mention specific technologies and their benefits when relevant

Write a complete video script that effectively communicates the value and functionality of this repository:

Video Script:"""

            return prompt
            
        except Exception as e:
            logger.error(f"Error generating video script prompt: {e}")
            return self._fallback_video_script_prompt(repo_analysis)
    
    def generate_summary_prompt(self, repo_analysis: Dict[str, Any]) -> str:
        """Generate a prompt for creating a repository summary"""
        try:
            repo_name = repo_analysis.get('repository_name', 'Unknown Repository')
            content = repo_analysis.get('analysis_text', '')
            technologies = repo_analysis.get('technologies', [])
            features = repo_analysis.get('main_features', [])
            
            prompt = f"""Create a comprehensive technical summary for the '{repo_name}' repository based on the following analysis:

Repository Content Analysis:
{content[:1500]}

Technologies Identified: {', '.join(technologies) if technologies else 'Various technologies'}

Key Features:
{chr(10).join([f"- {feature}" for feature in features[:5]]) if features else "- Various features"}

Instructions:
1. Write a detailed 3-4 paragraph technical summary
2. Focus on the project's purpose, functionality, and technical implementation
3. Highlight key features, technologies used, and architectural decisions
4. Mention any notable design patterns, frameworks, or methodologies
5. Include information about the project's potential use cases and target audience
6. Keep the tone professional and informative
7. Target audience: software developers, technical leads, and project stakeholders

Structure:
- Paragraph 1: Project overview and primary purpose
- Paragraph 2: Key features and functionality
- Paragraph 3: Technical implementation and technologies
- Paragraph 4: Value proposition and potential applications

Technical Summary:"""

            return prompt
            
        except Exception as e:
            logger.error(f"Error generating summary prompt: {e}")
            return f"Provide a comprehensive technical summary and analysis of the {repo_analysis.get('repository_name', 'repository')} project, including its features, technologies, and implementation details."
    
    def generate_feature_extraction_prompt(self, content: str) -> str:
        """Generate a prompt for extracting features from repository content"""
        prompt = f"""Analyze the following repository content and extract the main features and functionality:

Repository Content:
{content[:2000]}

Instructions:
1. Identify and list the main user-facing features and functionality
2. Focus on what the software actually does for users
3. Include technical capabilities and APIs if present
4. Mention any integrations with external services or systems
5. Note automation, workflow, or process improvements provided
6. Keep each feature description concise but informative (1-2 sentences)
7. Organize features by category if applicable (e.g., Core Features, API Features, etc.)
8. Prioritize the most important and distinctive features

Output Format:
Main Features:
- [Feature 1]: [Brief description]
- [Feature 2]: [Brief description]
...

Feature Analysis:"""

        return prompt
    
    def generate_technology_analysis_prompt(self, content: str) -> str:
        """Generate a prompt for analyzing technologies used"""
        prompt = f"""Analyze the following repository content and provide a comprehensive technology analysis:

Repository Content:
{content[:2000]}

Instructions:
1. Identify programming languages used (with confidence level)
2. List frameworks, libraries, and dependencies
3. Note development tools, build systems, and CI/CD setup
4. Identify database technologies and data storage solutions
5. Mention deployment technologies, containerization, and cloud services
6. Note testing frameworks and quality assurance tools
7. Identify any AI/ML technologies, APIs, or specialized tools
8. Group technologies by category for better organization

Output Format:
Technology Stack Analysis:

Programming Languages:
- [Language]: [Usage context and prevalence]

Frameworks & Libraries:
- [Framework/Library]: [Purpose and implementation]

Development Tools:
- [Tool]: [Role in development process]

Data & Storage:
- [Technology]: [Data handling approach]

Deployment & Infrastructure:
- [Technology]: [Deployment and scaling approach]

Technology Analysis:"""

        return prompt
    
    def _fallback_video_script_prompt(self, repo_analysis: Dict[str, Any]) -> str:
        """Fallback prompt when main generation fails"""
        repo_name = repo_analysis.get('repository_name', 'Repository')
        
        return f"""Create a professional and engaging video script about the '{repo_name}' software repository. 

The script should be 2-3 minutes long (300-450 words) and cover:

[0:00 - 0:30] Introduction
- Welcome viewers and introduce the project
- Hook them with what makes this repository interesting

[0:30 - 2:00] Main Content  
- Overview of the project's functionality and features
- Technical implementation and architecture highlights
- Benefits for users and developers

[2:00 - 2:30] Technical Details
- Key technologies and frameworks used
- Notable code quality and development practices

[2:30 - 3:00] Conclusion
- Summary of key points
- Call-to-action encouraging exploration or contribution

Write in a conversational, engaging tone suitable for a developer audience. Include timing markers and natural transitions between sections.

Video Script:"""
    
    def generate_visual_description_prompt(self, repo_analysis: Dict[str, Any]) -> str:
        """Generate a prompt for describing visual elements for video generation"""
        try:
            repo_name = repo_analysis.get('repository_name', 'Repository')
            technologies = repo_analysis.get('technologies', [])
            features = repo_analysis.get('main_features', [])
            
            prompt = f"""Describe visual elements and scenes for a video about the '{repo_name}' repository.

Project Context:
- Repository: {repo_name}
- Technologies: {', '.join(technologies[:4]) if technologies else 'Software development'}
- Key Features: {', '.join(features[:3]) if features else 'Various features'}

Instructions:
1. Suggest 6-8 distinct visual scenes that would work well for a repository overview video
2. Each scene should be 20-40 seconds long and complement the narration
3. Focus on abstract, code-related, technology-themed, or conceptual visuals
4. Consider backgrounds, colors, animations, and visual metaphors
5. Make suggestions suitable for automated video generation
6. Avoid showing specific faces, copyrighted content, or real screenshots
7. Include smooth transitions between scenes
8. Ensure visuals enhance the educational and professional nature of the content

Visual Scene Descriptions:

Scene 1 (Introduction): [Description]
Scene 2 (Overview): [Description]
Scene 3 (Features): [Description]
Scene 4 (Technology): [Description]
Scene 5 (Implementation): [Description]
Scene 6 (Conclusion): [Description]

Additional Visual Elements:
- Suggested color palette
- Animation styles
- Text overlay recommendations
- Transition effects

Visual Description:"""

            return prompt
            
        except Exception as e:
            logger.error(f"Error generating visual description prompt: {e}")
            return "Describe visual elements suitable for a professional software repository overview video, including code-themed backgrounds, technology-related graphics, and smooth transitions between informational scenes."
    
    def generate_script_enhancement_prompt(self, base_script: str, repo_analysis: Dict[str, Any]) -> str:
        """Generate a prompt to enhance and improve an existing script"""
        try:
            repo_name = repo_analysis.get('repository_name', 'Repository')
            technologies = repo_analysis.get('technologies', [])
            
            prompt = f"""Enhance and improve the following video script for the '{repo_name}' repository:

Current Script:
{base_script}

Repository Context:
- Technologies: {', '.join(technologies[:5]) if technologies else 'Various technologies'}
- Repository: {repo_name}

Enhancement Instructions:
1. Improve the flow and readability while maintaining the original structure
2. Add more specific technical details where appropriate
3. Enhance the introduction to be more engaging and hook the audience
4. Strengthen the conclusion with a compelling call-to-action
5. Ensure smooth transitions between sections
6. Add more personality and enthusiasm while keeping it professional
7. Include specific benefits and use cases where possible
8. Maintain the timing structure (2-3 minutes total)
9. Keep the language accessible to both technical and non-technical audiences
10. Ensure the script sounds natural when spoken aloud

Enhanced Video Script:"""

            return prompt
            
        except Exception as e:
            logger.error(f"Error generating script enhancement prompt: {e}")
            return f"Enhance and improve the following video script to make it more engaging, informative, and professional:\n\n{base_script}"
