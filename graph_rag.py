import os
import logging
import tempfile
import requests
import zipfile
import json
from typing import Dict, List, Any
import subprocess
import shutil

logger = logging.getLogger(__name__)

class GraphRAGProcessor:
    """Process GitHub repositories using gitingest for content analysis"""
    
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp(prefix='repo2reel_graph_')
        logger.info(f"Initialized GraphRAG processor with temp dir: {self.temp_dir}")
    
    def analyze_repository(self, github_url: str) -> Dict[str, Any]:
        """
        Analyze a GitHub repository and extract structured information
        """
        try:
            logger.info(f"Starting repository analysis for: {github_url}")
            
            # Clone or download repository
            repo_path = self._download_repository(github_url)
            
            # Use gitingest for content analysis
            analysis = self._analyze_with_gitingest(repo_path)
            
            # Extract key information
            structured_data = self._extract_structured_info(analysis, github_url)
            
            logger.info("Repository analysis completed successfully")
            return structured_data
            
        except Exception as e:
            logger.error(f"Error analyzing repository: {e}")
            raise Exception(f"Failed to analyze repository: {str(e)}")
    
    def _download_repository(self, github_url: str) -> str:
        """Download repository content"""
        try:
            # Convert GitHub URL to download URL
            if github_url.endswith('.git'):
                github_url = github_url[:-4]
            
            # Extract owner and repo name
            parts = github_url.replace('https://github.com/', '').replace('http://github.com/', '').split('/')
            if len(parts) < 2:
                raise ValueError("Invalid GitHub URL format")
            
            owner, repo = parts[0], parts[1]
            logger.info(f"Downloading repository: {owner}/{repo}")
            
            # Try different branch names
            branches = ['main', 'master', 'dev', 'develop']
            download_url = None
            response = None
            
            for branch in branches:
                download_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/{branch}.zip"
                try:
                    response = requests.get(download_url, timeout=30, stream=True)
                    if response.status_code == 200:
                        logger.info(f"Successfully found branch: {branch}")
                        break
                except requests.RequestException:
                    continue
            
            if not response or response.status_code != 200:
                raise Exception(f"Failed to download repository: No accessible branches found")
            
            # Save and extract ZIP
            zip_path = os.path.join(self.temp_dir, f"{repo}.zip")
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Extract ZIP
            extract_path = os.path.join(self.temp_dir, repo)
            os.makedirs(extract_path, exist_ok=True)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
            
            # Find the actual repository directory (usually has branch name suffix)
            extracted_dirs = [d for d in os.listdir(extract_path) if os.path.isdir(os.path.join(extract_path, d))]
            if extracted_dirs:
                repo_path = os.path.join(extract_path, extracted_dirs[0])
            else:
                repo_path = extract_path
            
            logger.info(f"Repository downloaded to: {repo_path}")
            return repo_path
            
        except Exception as e:
            logger.error(f"Error downloading repository: {e}")
            raise
    
    def _analyze_with_gitingest(self, repo_path: str) -> str:
        """Use gitingest to analyze repository content"""
        try:
            # Try to use gitingest library
            try:
                import gitingest
                logger.info("Using gitingest library")
                result = gitingest.ingest(repo_path)
                return result
                
            except ImportError:
                logger.info("gitingest library not available, trying CLI")
                # Try command line gitingest
                try:
                    result = subprocess.run(
                        ['gitingest', repo_path],
                        capture_output=True,
                        text=True,
                        timeout=120
                    )
                    
                    if result.returncode == 0:
                        return result.stdout
                    else:
                        logger.warning(f"gitingest CLI failed: {result.stderr}")
                        return self._fallback_analysis(repo_path)
                        
                except (subprocess.CalledProcessError, FileNotFoundError):
                    logger.warning("gitingest CLI not available, using fallback analysis")
                    return self._fallback_analysis(repo_path)
                    
        except Exception as e:
            logger.error(f"Error in gitingest analysis: {e}")
            return self._fallback_analysis(repo_path)
    
    def _fallback_analysis(self, repo_path: str) -> str:
        """Fallback analysis when gitingest is not available"""
        try:
            logger.info("Starting fallback repository analysis")
            analysis = []
            
            # Analyze README files
            readme_files = ['README.md', 'README.txt', 'README.rst', 'readme.md', 'Readme.md', 'README']
            for readme in readme_files:
                readme_path = os.path.join(repo_path, readme)
                if os.path.exists(readme_path):
                    try:
                        with open(readme_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()[:4000]  # Limit content
                            analysis.append(f"=== README Content ({readme}) ===\n{content}\n")
                        break
                    except Exception as e:
                        logger.warning(f"Error reading {readme}: {e}")
                        continue
            
            # Analyze package files
            package_files = [
                'package.json', 'requirements.txt', 'Cargo.toml', 'go.mod', 
                'pom.xml', 'build.gradle', 'setup.py', 'pyproject.toml', 
                'composer.json', 'Gemfile', 'mix.exs'
            ]
            for package_file in package_files:
                package_path = os.path.join(repo_path, package_file)
                if os.path.exists(package_path):
                    try:
                        with open(package_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            analysis.append(f"=== Package File ({package_file}) ===\n{content}\n")
                    except Exception as e:
                        logger.warning(f"Error reading {package_file}: {e}")
                        continue
            
            # Analyze main code files
            code_extensions = ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs', '.php', '.rb', '.swift', '.kt']
            file_count = 0
            max_files = 20
            
            for root, dirs, files in os.walk(repo_path):
                # Skip hidden directories and common ignore patterns
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in [
                    'node_modules', '__pycache__', 'venv', 'env', 'dist', 'build', 
                    'target', 'vendor', '.git', '.github', '.vscode'
                ]]
                
                for file in files:
                    if file_count >= max_files:
                        break
                        
                    file_path = os.path.join(root, file)
                    _, ext = os.path.splitext(file)
                    
                    if ext.lower() in code_extensions or file in ['Dockerfile', 'docker-compose.yml', 'Makefile']:
                        try:
                            rel_path = os.path.relpath(file_path, repo_path)
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()[:2000]  # Limit content per file
                                analysis.append(f"=== File: {rel_path} ===\n{content}\n")
                                file_count += 1
                        except Exception as e:
                            logger.warning(f"Error reading {file}: {e}")
                            continue
                
                if file_count >= max_files:
                    break
            
            # Analyze configuration files
            config_files = [
                '.gitignore', 'LICENSE', 'CONTRIBUTING.md', 'CHANGELOG.md',
                'docker-compose.yml', 'Dockerfile', 'Makefile', '.env.example'
            ]
            for config_file in config_files:
                config_path = os.path.join(repo_path, config_file)
                if os.path.exists(config_path):
                    try:
                        with open(config_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()[:1000]
                            analysis.append(f"=== Config: {config_file} ===\n{content}\n")
                    except Exception as e:
                        logger.warning(f"Error reading {config_file}: {e}")
                        continue
            
            result = '\n'.join(analysis)
            logger.info(f"Fallback analysis completed, analyzed {len(analysis)} items")
            return result
            
        except Exception as e:
            logger.error(f"Error in fallback analysis: {e}")
            return "Error: Could not analyze repository content"
    
    def _extract_structured_info(self, analysis: str, github_url: str) -> Dict[str, Any]:
        """Extract structured information from analysis"""
        try:
            # Extract repository name
            repo_name = github_url.split('/')[-1].replace('.git', '')
            
            # Basic information extraction
            lines = analysis.split('\n')
            description = ""
            technologies = []
            main_features = []
            
            # Look for description in README
            in_readme = False
            readme_lines = []
            
            for i, line in enumerate(lines):
                if "=== README Content" in line:
                    in_readme = True
                    continue
                elif line.startswith("===") and in_readme:
                    break
                elif in_readme:
                    readme_lines.append(line)
            
            # Extract description from README
            if readme_lines:
                for i, line in enumerate(readme_lines[:20]):  # Check first 20 lines
                    line = line.strip()
                    if line.startswith('# ') and not description:
                        # Look for description in next few lines
                        for j in range(i+1, min(i+5, len(readme_lines))):
                            next_line = readme_lines[j].strip()
                            if next_line and not next_line.startswith('#') and not next_line.startswith('[!['):
                                description = next_line
                                break
                        break
            
            # Detect technologies
            tech_keywords = {
                'Python': ['python', '.py', 'pip', 'requirements.txt', 'django', 'flask', 'fastapi', 'import '],
                'JavaScript': ['javascript', '.js', 'npm', 'package.json', 'node', 'const ', 'let ', 'var '],
                'TypeScript': ['typescript', '.ts', '.tsx', 'tsconfig'],
                'React': ['react', 'jsx', 'create-react-app', 'useState', 'useEffect'],
                'Vue.js': ['vue', 'vuejs', 'vue.js', '<template>'],
                'Angular': ['angular', '@angular', '@Component'],
                'Flask': ['flask', 'from flask', 'Flask('],
                'Django': ['django', 'from django', 'Django'],
                'FastAPI': ['fastapi', 'from fastapi', 'FastAPI('],
                'Express': ['express', 'expressjs', 'app.get(', 'app.post('],
                'Node.js': ['nodejs', 'node.js', 'require(', 'module.exports'],
                'Java': ['.java', 'public class', 'import java'],
                'Go': ['.go', 'package main', 'func main', 'import "'],
                'Rust': ['.rs', 'fn main', 'use std::', 'cargo.toml'],
                'C++': ['.cpp', '.cc', '.cxx', '#include <', 'using namespace'],
                'C': ['.c', '#include <stdio.h>', 'int main('],
                'Docker': ['dockerfile', 'docker-compose', 'FROM ', 'RUN '],
                'Kubernetes': ['kubernetes', 'k8s', 'apiVersion:', 'kind:'],
                'MongoDB': ['mongodb', 'mongoose', 'db.collection'],
                'PostgreSQL': ['postgresql', 'postgres', 'psql'],
                'MySQL': ['mysql', 'mysqli'],
                'Redis': ['redis', 'redis-server'],
                'Next.js': ['next.js', 'nextjs', 'next/'],
                'Svelte': ['svelte', '.svelte'],
                'PHP': ['.php', '<?php', 'composer.json'],
                'Ruby': ['.rb', 'gemfile', 'require '],
                'Swift': ['.swift', 'import Foundation'],
                'Kotlin': ['.kt', 'fun main']
            }
            
            analysis_lower = analysis.lower()
            for tech, keywords in tech_keywords.items():
                if any(keyword.lower() in analysis_lower for keyword in keywords):
                    technologies.append(tech)
            
            # Extract features from README
            feature_sections = ['features:', 'functionality:', '## features', '## functionality', '### features', 'what it does']
            in_feature_section = False
            
            for i, line in enumerate(readme_lines):
                line_lower = line.lower().strip()
                
                # Check if we're entering a feature section
                if any(indicator in line_lower for indicator in feature_sections):
                    in_feature_section = True
                    continue
                elif line_lower.startswith('##') and in_feature_section:
                    # End of feature section
                    break
                elif in_feature_section:
                    # Look for bullet points
                    if line.strip().startswith(('-', '*', '+', '1.', '2.', '3.', '•')):
                        feature = line.strip()
                        # Clean up the feature text
                        for prefix in ['-', '*', '+', '1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '•']:
                            if feature.startswith(prefix):
                                feature = feature[len(prefix):].strip()
                                break
                        
                        if len(feature) > 10 and len(feature) < 150:
                            main_features.append(feature)
                        
                        if len(main_features) >= 8:
                            break
            
            # If no features found in dedicated section, extract from general content
            if not main_features:
                for line in readme_lines[:50]:  # Check first 50 lines
                    line = line.strip()
                    if line.startswith(('-', '*', '+', '1.', '2.', '3.')):
                        feature = line
                        for prefix in ['-', '*', '+', '1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.']:
                            if feature.startswith(prefix):
                                feature = feature[len(prefix):].strip()
                                break
                        
                        if len(feature) > 15 and len(feature) < 120:
                            main_features.append(feature)
                        
                        if len(main_features) >= 6:
                            break
            
            structured_info = {
                'repository_name': repo_name,
                'repository_url': github_url,
                'description': description or f"A comprehensive {repo_name} project",
                'technologies': technologies[:10],  # Limit to 10 technologies
                'main_features': main_features[:8],  # Limit to 8 features
                'content_summary': analysis[:2000] + "..." if len(analysis) > 2000 else analysis,
                'file_structure': self._extract_file_structure(analysis),
                'analysis_text': analysis
            }
            
            logger.info(f"Extracted structured info for {repo_name}: {len(technologies)} technologies, {len(main_features)} features")
            return structured_info
            
        except Exception as e:
            logger.error(f"Error extracting structured info: {e}")
            return {
                'repository_name': github_url.split('/')[-1].replace('.git', ''),
                'repository_url': github_url,
                'description': 'Repository analysis and overview',
                'technologies': [],
                'main_features': [],
                'content_summary': analysis[:1000] if analysis else 'Repository content analysis',
                'file_structure': [],
                'analysis_text': analysis
            }
    
    def _extract_file_structure(self, analysis: str) -> List[str]:
        """Extract file structure from analysis"""
        try:
            files = []
            lines = analysis.split('\n')
            
            for line in lines:
                # Look for file patterns
                if '=== File:' in line:
                    file_path = line.split('=== File:')[-1].replace('===', '').strip()
                    if file_path:
                        files.append(file_path)
                elif line.strip().endswith(('.py', '.js', '.java', '.cpp', '.c', '.go', '.rs', '.php', '.html', '.css', '.ts', '.jsx')):
                    files.append(line.strip())
            
            return files[:30]  # Limit to 30 files
            
        except Exception as e:
            logger.error(f"Error extracting file structure: {e}")
            return []
    
    def __del__(self):
        """Cleanup temporary directory"""
        try:
            if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                logger.info(f"Cleaned up temp directory: {self.temp_dir}")
        except Exception as e:
            logger.error(f"Error cleaning up temp directory: {e}")
