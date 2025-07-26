import os
import logging
import tempfile
import json
import random
import subprocess
from typing import Dict, Any, List, Tuple
from PIL import Image, ImageDraw, ImageFont
import math

logger = logging.getLogger(__name__)

class VideoGenerator:
    """Generate video content using CPU-optimized processing"""
    
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
        self.width = 1920
        self.height = 1080
        self.fps = 25  # Reduced FPS for better CPU performance
        logger.info("Initialized VideoGenerator")
    
    def generate_video(self, script: str, repo_analysis: Dict[str, Any], session_id: str) -> str:
        """Generate video from script and repository analysis"""
        try:
            output_file = os.path.join(self.temp_dir, f'repo2reel_{session_id}_video.mp4')
            
            # Estimate video duration from script
            words = len(script.split())
            duration = max(words * 0.4, 30)  # ~2.5 words per second, minimum 30 seconds
            duration = min(duration, 300)  # Maximum 5 minutes
            
            logger.info(f"Generating video with duration: {duration} seconds")
            
            # Generate visual scenes
            scenes = self._create_scenes(script, repo_analysis, duration)
            
            # Create video frames (reduced frame count for CPU optimization)
            frame_files = self._generate_frames(scenes, duration, session_id)
            
            # Compile frames into video
            video_file = self._compile_video(frame_files, output_file, duration)
            
            # Clean up frame files
            self._cleanup_frames(frame_files)
            
            logger.info(f"Generated video: {video_file}")
            return video_file
            
        except Exception as e:
            logger.error(f"Error generating video: {e}")
            # Try to generate a simple fallback video
            return self._generate_fallback_video(session_id, script, repo_analysis)
    
    def _create_scenes(self, script: str, repo_analysis: Dict[str, Any], duration: float) -> List[Dict[str, Any]]:
        """Create visual scenes based on script and repository content"""
        try:
            scenes = []
            repo_name = repo_analysis.get('repository_name', 'Repository')
            technologies = repo_analysis.get('technologies', [])
            features = repo_analysis.get('main_features', [])
            
            # Split script into sections for different scenes
            script_sections = self._split_script_into_sections(script)
            scene_duration = duration / len(script_sections)
            
            colors = [
                '#2563eb',  # Blue
                '#7c3aed',  # Purple  
                '#059669',  # Green
                '#dc2626',  # Red
                '#ea580c',  # Orange
                '#0891b2',  # Cyan
                '#6366f1',  # Indigo
                '#8b5cf6',  # Violet
            ]
            
            for i, section in enumerate(script_sections):
                scene = {
                    'type': self._determine_scene_type(section, technologies),
                    'duration': scene_duration,
                    'text': section[:150] + '...' if len(section) > 150 else section,
                    'title': self._extract_title_from_section(section, repo_name),
                    'color': colors[i % len(colors)],
                    'start_time': i * scene_duration,
                    'repo_name': repo_name,
                    'technologies': technologies[:6],  # Limit technologies shown
                    'features': features[:5]  # Limit features shown
                }
                scenes.append(scene)
            
            return scenes
            
        except Exception as e:
            logger.error(f"Error creating scenes: {e}")
            # Return a simple default scene
            return [{
                'type': 'title',
                'duration': duration,
                'text': script[:200],
                'title': repo_analysis.get('repository_name', 'Repository Overview'),
                'color': '#2563eb',
                'start_time': 0,
                'repo_name': repo_analysis.get('repository_name', 'Repository'),
                'technologies': repo_analysis.get('technologies', [])[:6],
                'features': repo_analysis.get('main_features', [])[:5]
            }]
    
    def _split_script_into_sections(self, script: str) -> List[str]:
        """Split script into logical sections"""
        # Split by timing markers first
        if '[' in script and ']' in script:
            sections = []
            current_section = ""
            
            lines = script.split('\n')
            for line in lines:
                if '[' in line and ']' in line and any(char.isdigit() for char in line):
                    if current_section.strip():
                        sections.append(current_section.strip())
                    current_section = line + '\n'
                else:
                    current_section += line + '\n'
            
            if current_section.strip():
                sections.append(current_section.strip())
            
            if len(sections) >= 2:
                return sections
        
        # Fallback: split by paragraphs
        paragraphs = script.split('\n\n')
        if len(paragraphs) > 1:
            return [p.strip() for p in paragraphs if p.strip()]
        
        # If no paragraphs, split by sentences
        sentences = script.split('. ')
        if len(sentences) > 4:
            # Group sentences into sections
            section_size = max(len(sentences) // 4, 1)
            sections = []
            for i in range(0, len(sentences), section_size):
                section = '. '.join(sentences[i:i+section_size])
                if section:
                    sections.append(section)
            return sections
        
        # If too few sentences, split by words
        words = script.split()
        if len(words) > 40:
            section_size = max(len(words) // 4, 20)
            sections = []
            for i in range(0, len(words), section_size):
                section = ' '.join(words[i:i+section_size])
                if section:
                    sections.append(section)
            return sections
        
        return [script] if script else ["Repository Overview"]
    
    def _determine_scene_type(self, section: str, technologies: List[str]) -> str:
        """Determine the type of scene based on content"""
        section_lower = section.lower()
        
        if any(word in section_lower for word in ['welcome', 'introduction', 'hello', 'today', 'overview']):
            return 'title'
        elif any(word in section_lower for word in ['feature', 'functionality', 'capability', 'includes']):
            return 'features'
        elif any(tech.lower() in section_lower for tech in technologies):
            return 'technology'
        elif any(word in section_lower for word in ['code', 'implementation', 'architecture', 'technical']):
            return 'code'
        elif any(word in section_lower for word in ['conclusion', 'summary', 'thank', 'explore']):
            return 'conclusion'
        else:
            return 'content'
    
    def _extract_title_from_section(self, section: str, repo_name: str) -> str:
        """Extract a title from the section content"""
        # Remove timing markers
        section = section.split(']')[-1] if ']' in section else section
        
        # Look for the first sentence or meaningful phrase
        sentences = section.split('.')
        if sentences:
            title = sentences[0].strip()
            # Clean up common prefixes
            title = title.replace('Welcome to', '').replace('Today', '').strip()
            if len(title) > 60:
                title = title[:57] + '...'
            if title:
                return title
        
        return repo_name
    
    def _generate_frames(self, scenes: List[Dict[str, Any]], total_duration: float, session_id: str) -> List[str]:
        """Generate video frames for all scenes"""
        try:
            frame_files = []
            frame_rate = 3  # Generate every 3rd frame to reduce processing
            total_frames = int(total_duration * self.fps / frame_rate)
            
            logger.info(f"Generating {total_frames} frames (optimized for CPU)")
            
            for frame_num in range(total_frames):
                time_pos = (frame_num * frame_rate) / self.fps
                
                # Determine which scene this frame belongs to
                current_scene = None
                for scene in scenes:
                    if scene['start_time'] <= time_pos < scene['start_time'] + scene['duration']:
                        current_scene = scene
                        break
                
                if not current_scene:
                    current_scene = scenes[-1]  # Use last scene if time exceeds
                
                # Generate frame
                frame_file = self._generate_single_frame(current_scene, time_pos, frame_num, session_id)
                frame_files.append(frame_file)
                
                if frame_num % 20 == 0:
                    logger.info(f"Generated {frame_num}/{total_frames} frames")
            
            return frame_files
            
        except Exception as e:
            logger.error(f"Error generating frames: {e}")
            raise
    
    def _generate_single_frame(self, scene: Dict[str, Any], time_pos: float, frame_num: int, session_id: str) -> str:
        """Generate a single video frame"""
        try:
            # Create image
            image = Image.new('RGB', (self.width, self.height), color='#000000')
            draw = ImageDraw.Draw(image)
            
            # Draw background
            self._draw_background(draw, scene, time_pos)
            
            # Draw content based on scene type
            if scene['type'] == 'title':
                self._draw_title_scene(draw, scene)
            elif scene['type'] == 'features':
                self._draw_features_scene(draw, scene)
            elif scene['type'] == 'technology':
                self._draw_technology_scene(draw, scene)
            elif scene['type'] == 'code':
                self._draw_code_scene(draw, scene)
            elif scene['type'] == 'conclusion':
                self._draw_conclusion_scene(draw, scene)
            else:
                self._draw_content_scene(draw, scene)
            
            # Save frame
            frame_file = os.path.join(self.temp_dir, f'repo2reel_{session_id}_frame_{frame_num:06d}.png')
            image.save(frame_file, 'PNG')
            
            return frame_file
            
        except Exception as e:
            logger.error(f"Error generating frame {frame_num}: {e}")
            # Return a simple black frame
            image = Image.new('RGB', (self.width, self.height), color='#111111')
            frame_file = os.path.join(self.temp_dir, f'repo2reel_{session_id}_frame_{frame_num:06d}.png')
            image.save(frame_file, 'PNG')
            return frame_file
    
    def _draw_background(self, draw: ImageDraw.Draw, scene: Dict[str, Any], time_pos: float):
        """Draw animated background"""
        try:
            color = scene['color']
            
            # Create gradient background
            for y in range(0, self.height, 4):  # Step by 4 for performance
                # Create vertical gradient
                intensity = int(255 * (1 - y / self.height) * 0.3)
                gradient_color = self._adjust_color_brightness(color, intensity)
                draw.rectangle([(0, y), (self.width, y+4)], fill=gradient_color)
            
            # Add animated elements (simplified for CPU)
            self._draw_animated_elements(draw, scene, time_pos)
            
        except Exception as e:
            logger.error(f"Error drawing background: {e}")
    
    def _draw_animated_elements(self, draw: ImageDraw.Draw, scene: Dict[str, Any], time_pos: float):
        """Draw animated background elements"""
        try:
            # Draw floating geometric shapes (reduced count for performance)
            num_shapes = 6
            for i in range(num_shapes):
                # Calculate position with animation
                base_x = (i * self.width / num_shapes) + (time_pos * 15) % self.width
                base_y = (i * self.height / num_shapes) + math.sin(time_pos + i) * 40
                
                # Ensure shapes wrap around
                x = base_x % self.width
                y = base_y % self.height
                
                size = 25 + math.sin(time_pos * 1.5 + i) * 8
                
                # Draw semi-transparent circles
                alpha_color = self._adjust_color_brightness(scene['color'], 25)
                draw.ellipse([
                    x - size/2, y - size/2,
                    x + size/2, y + size/2
                ], fill=alpha_color)
                
        except Exception as e:
            logger.error(f"Error drawing animated elements: {e}")
    
    def _draw_title_scene(self, draw: ImageDraw.Draw, scene: Dict[str, Any]):
        """Draw title scene content"""
        try:
            # Try to load better fonts with fallbacks
            try:
                title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 84)
                subtitle_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 42)
                tech_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 28)
            except OSError:
                try:
                    title_font = ImageFont.truetype("arial.ttf", 84)
                    subtitle_font = ImageFont.truetype("arial.ttf", 42)
                    tech_font = ImageFont.truetype("arial.ttf", 28)
                except OSError:
                    try:
                        title_font = ImageFont.load_default()
                        subtitle_font = ImageFont.load_default()
                        tech_font = ImageFont.load_default()
                    except:
                        # Use PIL's basic font as absolute fallback
                        title_font = subtitle_font = tech_font = None
            
            title = scene['repo_name']
            
            # Draw enhanced title with multiple shadow layers for better visibility
            if title_font:
                try:
                    title_bbox = draw.textbbox((0, 0), title, font=title_font)
                    title_width = title_bbox[2] - title_bbox[0]
                except:
                    title_width = len(title) * 50  # Estimate
            else:
                title_width = len(title) * 50
                
            title_x = (self.width - title_width) // 2
            title_y = self.height // 2 - 150
            
            # Draw multiple shadow layers for better contrast
            if title_font:
                # Dark outer shadow
                draw.text((title_x + 6, title_y + 6), title, fill='#000000', font=title_font)
                draw.text((title_x + 4, title_y + 4), title, fill='#333333', font=title_font)
                # Bright main text
                draw.text((title_x, title_y), title, fill='#ffffff', font=title_font)
                # Add subtle glow effect
                draw.text((title_x - 1, title_y - 1), title, fill='#f0f0f0', font=title_font)
            else:
                draw.text((title_x + 4, title_y + 4), title, fill='#000000')
                draw.text((title_x, title_y), title, fill='#ffffff')
            
            # Draw enhanced subtitle with background box
            subtitle = "Repository Overview"
            if subtitle_font:
                try:
                    subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
                    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
                    subtitle_height = subtitle_bbox[3] - subtitle_bbox[1]
                except:
                    subtitle_width = len(subtitle) * 24
                    subtitle_height = 42
            else:
                subtitle_width = len(subtitle) * 24
                subtitle_height = 42
                
            subtitle_x = (self.width - subtitle_width) // 2
            subtitle_y = title_y + 140
            
            # Draw background box for subtitle
            padding = 20
            box_x1 = subtitle_x - padding
            box_y1 = subtitle_y - padding//2
            box_x2 = subtitle_x + subtitle_width + padding
            box_y2 = subtitle_y + subtitle_height + padding//2
            
            # Draw rounded rectangle background
            draw.rectangle([box_x1, box_y1, box_x2, box_y2], fill='#2563eb', outline='#1d4ed8', width=2)
            
            if subtitle_font:
                draw.text((subtitle_x + 2, subtitle_y + 2), subtitle, fill='#000066', font=subtitle_font)
                draw.text((subtitle_x, subtitle_y), subtitle, fill='#ffffff', font=subtitle_font)
            else:
                draw.text((subtitle_x + 2, subtitle_y + 2), subtitle, fill='#000066')
                draw.text((subtitle_x, subtitle_y), subtitle, fill='#ffffff')
            
            # Draw technologies as enhanced badges with better layout
            if scene['technologies']:
                tech_y = subtitle_y + 120
                
                # Calculate optimal layout for tech badges
                tech_per_row = min(3, len(scene['technologies']))
                rows_needed = (len(scene['technologies'][:6]) + tech_per_row - 1) // tech_per_row
                badge_width = 200
                badge_height = 45
                badge_spacing = 20
                
                total_width = tech_per_row * badge_width + (tech_per_row - 1) * badge_spacing
                tech_x_start = (self.width - total_width) // 2
                
                for i, tech in enumerate(scene['technologies'][:6]):
                    row = i // tech_per_row
                    col = i % tech_per_row
                    
                    tech_x = tech_x_start + col * (badge_width + badge_spacing)
                    current_tech_y = tech_y + row * (badge_height + 15)
                    
                    # Draw enhanced tech badge with gradient effect
                    # Outer shadow
                    draw.rectangle([
                        tech_x + 4, current_tech_y + 4,
                        tech_x + badge_width + 4, current_tech_y + badge_height + 4
                    ], fill='#000000aa')
                    
                    # Main badge
                    draw.rectangle([
                        tech_x, current_tech_y,
                        tech_x + badge_width, current_tech_y + badge_height
                    ], fill=scene['color'], outline='#ffffff', width=3)
                    
                    # Inner highlight
                    draw.rectangle([
                        tech_x + 2, current_tech_y + 2,
                        tech_x + badge_width - 2, current_tech_y + badge_height - 2
                    ], fill=None, outline=self._adjust_color_brightness(scene['color'], 40), width=1)
                    
                    # Center the tech text in badge
                    if tech_font:
                        try:
                            tech_bbox = draw.textbbox((0, 0), tech, font=tech_font)
                            tech_text_width = tech_bbox[2] - tech_bbox[0]
                        except:
                            tech_text_width = len(tech) * 16
                    else:
                        tech_text_width = len(tech) * 16
                    
                    tech_text_x = tech_x + (badge_width - tech_text_width) // 2
                    tech_text_y = current_tech_y + (badge_height - 28) // 2
                    
                    if tech_font:
                        draw.text((tech_text_x + 2, tech_text_y + 2), tech, fill='#000000', font=tech_font)
                        draw.text((tech_text_x, tech_text_y), tech, fill='#ffffff', font=tech_font)
                    else:
                        draw.text((tech_text_x + 2, tech_text_y + 2), tech, fill='#000000')
                        draw.text((tech_text_x, tech_text_y), tech, fill='#ffffff')
            
        except Exception as e:
            logger.error(f"Error drawing title scene: {e}")
    
    def _draw_features_scene(self, draw: ImageDraw.Draw, scene: Dict[str, Any]):
        """Draw features scene with table-like layout"""
        try:
            try:
                title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 56)
                text_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
                bullet_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
            except OSError:
                try:
                    title_font = ImageFont.truetype("arial.ttf", 56)
                    text_font = ImageFont.truetype("arial.ttf", 24)
                    bullet_font = ImageFont.truetype("arial.ttf", 28)
                except OSError:
                    title_font = text_font = bullet_font = None
            
            # Draw "Features" title
            title = "Key Features"
            if title_font:
                try:
                    title_bbox = draw.textbbox((0, 0), title, font=title_font)
                    title_width = title_bbox[2] - title_bbox[0]
                except:
                    title_width = len(title) * 30
            else:
                title_width = len(title) * 30
                
            title_x = (self.width - title_width) // 2
            title_y = 200
            
            if title_font:
                draw.text((title_x + 2, title_y + 2), title, fill='#000000', font=title_font)
                draw.text((title_x, title_y), title, fill='#ffffff', font=title_font)
            else:
                draw.text((title_x + 2, title_y + 2), title, fill='#000000')
                draw.text((title_x, title_y), title, fill='#ffffff')
            
            # Draw features in table format
            if scene.get('features'):
                # Draw table background
                table_x = 100
                table_y = title_y + 120
                table_width = self.width - 200
                table_height = min(len(scene['features'][:5]) * 80 + 40, 450)
                
                # Table background with border
                draw.rectangle([table_x, table_y, table_x + table_width, table_y + table_height], 
                              fill='#1a1a1a', outline='#4a90e2', width=3)
                
                # Table header
                header_height = 60
                draw.rectangle([table_x, table_y, table_x + table_width, table_y + header_height], 
                              fill='#4a90e2', outline='#ffffff', width=2)
                
                header_text = "Key Features"
                if title_font:
                    try:
                        header_bbox = draw.textbbox((0, 0), header_text, font=title_font)
                        header_width = header_bbox[2] - header_bbox[0]
                    except:
                        header_width = len(header_text) * 32
                else:
                    header_width = len(header_text) * 32
                
                header_x = table_x + (table_width - header_width) // 2
                header_y = table_y + 15
                
                if title_font:
                    draw.text((header_x + 2, header_y + 2), header_text, fill='#000066', font=title_font)
                    draw.text((header_x, header_y), header_text, fill='#ffffff', font=title_font)
                else:
                    draw.text((header_x + 2, header_y + 2), header_text, fill='#000066')
                    draw.text((header_x, header_y), header_text, fill='#ffffff')
                
                # Draw feature rows
                row_height = 75
                for i, feature in enumerate(scene['features'][:5]):  # Max 5 features
                    row_y = table_y + header_height + i * row_height
                    
                    # Alternate row colors
                    row_color = '#2a2a2a' if i % 2 == 0 else '#1f1f1f'
                    draw.rectangle([table_x + 3, row_y, table_x + table_width - 3, row_y + row_height], 
                                  fill=row_color)
                    
                    # Feature number circle
                    circle_x = table_x + 40
                    circle_y = row_y + row_height // 2
                    circle_radius = 18
                    
                    draw.ellipse([circle_x - circle_radius, circle_y - circle_radius,
                                 circle_x + circle_radius, circle_y + circle_radius], 
                                fill='#4a90e2', outline='#ffffff', width=2)
                    
                    # Feature number
                    number_text = str(i + 1)
                    if bullet_font:
                        try:
                            num_bbox = draw.textbbox((0, 0), number_text, font=bullet_font)
                            num_width = num_bbox[2] - num_bbox[0]
                        except:
                            num_width = len(number_text) * 16
                    else:
                        num_width = len(number_text) * 16
                    
                    num_x = circle_x - num_width // 2
                    num_y = circle_y - 14
                    
                    if bullet_font:
                        draw.text((num_x, num_y), number_text, fill='#ffffff', font=bullet_font)
                    else:
                        draw.text((num_x, num_y), number_text, fill='#ffffff')
                    
                    # Feature text
                    feature_text = feature[:60] + '...' if len(feature) > 60 else feature
                    feature_x = table_x + 90
                    feature_y_pos = row_y + (row_height - 24) // 2
                    
                    if text_font:
                        draw.text((feature_x + 2, feature_y_pos + 2), feature_text, fill='#000000', font=text_font)
                        draw.text((feature_x, feature_y_pos), feature_text, fill='#ffffff', font=text_font)
                    else:
                        draw.text((feature_x + 2, feature_y_pos + 2), feature_text, fill='#000000')
                        draw.text((feature_x, feature_y_pos), feature_text, fill='#ffffff')
            else:
                # Draw general feature text
                text = self._wrap_text(scene['text'], 60)
                text_y = title_y + 120
                
                for line in text.split('\n')[:6]:  # Max 6 lines
                    if line.strip():
                        if text_font:
                            try:
                                line_bbox = draw.textbbox((0, 0), line, font=text_font)
                                line_width = line_bbox[2] - line_bbox[0]
                            except:
                                line_width = len(line) * 12
                        else:
                            line_width = len(line) * 12
                        
                        line_x = (self.width - line_width) // 2
                        
                        if text_font:
                            draw.text((line_x + 1, text_y + 1), line, fill='#000000', font=text_font)
                            draw.text((line_x, text_y), line, fill='#ffffff', font=text_font)
                        else:
                            draw.text((line_x + 1, text_y + 1), line, fill='#000000')
                            draw.text((line_x, text_y), line, fill='#ffffff')
                        
                        text_y += 35
            
        except Exception as e:
            logger.error(f"Error drawing features scene: {e}")
    
    def _draw_technology_scene(self, draw: ImageDraw.Draw, scene: Dict[str, Any]):
        """Draw technology scene with flowchart-style layout"""
        try:
            try:
                title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 52)
                text_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
                tech_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 26)
            except OSError:
                try:
                    title_font = ImageFont.truetype("arial.ttf", 52)
                    text_font = ImageFont.truetype("arial.ttf", 22)
                    tech_font = ImageFont.truetype("arial.ttf", 26)
                except OSError:
                    title_font = text_font = tech_font = None
            
            # Draw "Technology" title
            title = "Technology Stack"
            if title_font:
                try:
                    title_bbox = draw.textbbox((0, 0), title, font=title_font)
                    title_width = title_bbox[2] - title_bbox[0]
                except:
                    title_width = len(title) * 30
            else:
                title_width = len(title) * 30
                
            title_x = (self.width - title_width) // 2
            title_y = 200
            
            if title_font:
                draw.text((title_x + 2, title_y + 2), title, fill='#000000', font=title_font)
                draw.text((title_x, title_y), title, fill='#ffffff', font=title_font)
            else:
                draw.text((title_x + 2, title_y + 2), title, fill='#000000')
                draw.text((title_x, title_y), title, fill='#ffffff')
            
            # Draw technology badges
            if scene.get('technologies'):
                tech_y = title_y + 120
                tech_x_start = 300
                
                for i, tech in enumerate(scene['technologies'][:6]):
                    # Calculate position (2 columns)
                    col = i % 2
                    row = i // 2
                    
                    badge_x = tech_x_start + col * 700
                    badge_y = tech_y + row * 80
                    
                    # Draw badge background
                    badge_width = 250
                    badge_height = 50
                    
                    draw.rectangle([
                        badge_x, badge_y,
                        badge_x + badge_width, badge_y + badge_height
                    ], fill=self._adjust_color_brightness(scene['color'], 50))
                    
                    # Draw tech name
                    if text_font:
                        try:
                            tech_bbox = draw.textbbox((0, 0), tech, font=text_font)
                            tech_text_width = tech_bbox[2] - tech_bbox[0]
                        except:
                            tech_text_width = len(tech) * 12
                    else:
                        tech_text_width = len(tech) * 12
                    
                    tech_text_x = badge_x + (badge_width - tech_text_width) // 2
                    tech_text_y = badge_y + (badge_height - 20) // 2
                    
                    if text_font:
                        draw.text((tech_text_x, tech_text_y), tech, fill='#ffffff', font=text_font)
                    else:
                        draw.text((tech_text_x, tech_text_y), tech, fill='#ffffff')
            
        except Exception as e:
            logger.error(f"Error drawing technology scene: {e}")
    
    def _draw_code_scene(self, draw: ImageDraw.Draw, scene: Dict[str, Any]):
        """Draw code scene with syntax highlighting effect"""
        try:
            try:
                title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 52)
                code_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 20)
            except OSError:
                try:
                    title_font = ImageFont.truetype("arial.ttf", 52)
                    code_font = ImageFont.truetype("courier.ttf", 20)
                except OSError:
                    title_font = code_font = None
            
            # Draw "Code" title
            title = "Implementation"
            if title_font:
                try:
                    title_bbox = draw.textbbox((0, 0), title, font=title_font)
                    title_width = title_bbox[2] - title_bbox[0]
                except:
                    title_width = len(title) * 30
            else:
                title_width = len(title) * 30
                
            title_x = (self.width - title_width) // 2
            title_y = 150
            
            if title_font:
                draw.text((title_x + 2, title_y + 2), title, fill='#000000', font=title_font)
                draw.text((title_x, title_y), title, fill='#ffffff', font=title_font)
            else:
                draw.text((title_x + 2, title_y + 2), title, fill='#000000')
                draw.text((title_x, title_y), title, fill='#ffffff')
            
            # Draw IDE-style code editor
            editor_x, editor_y = 150, title_y + 80
            editor_width, editor_height = self.width - 300, 550
            
            # Editor background (dark theme)
            draw.rectangle([editor_x, editor_y, editor_x + editor_width, editor_y + editor_height], 
                          fill='#282c34', outline='#61dafb', width=3)
            
            # Editor header bar
            header_height = 40
            draw.rectangle([editor_x, editor_y, editor_x + editor_width, editor_y + header_height], 
                          fill='#21252b', outline='#61dafb', width=2)
            
            # File tab
            tab_width = 200
            draw.rectangle([editor_x + 10, editor_y + 5, editor_x + 10 + tab_width, editor_y + header_height - 5], 
                          fill='#282c34', outline='#61dafb', width=1)
            
            if code_font:
                draw.text((editor_x + 20, editor_y + 12), f"{scene['repo_name']}.py", fill='#ffffff', font=code_font)
            else:
                draw.text((editor_x + 20, editor_y + 12), f"{scene['repo_name']}.py", fill='#ffffff')
            
            # Enhanced code with syntax highlighting colors
            code_lines = [
                ("# Repository Analysis and Video Generation", '#5c6370'),  # Comment
                ("", ''),
                ("class Repository:", '#c678dd'),  # Keyword
                ("    def __init__(self, url: str):", '#61dafb'),  # Function
                ("        self.url = url", '#e06c75'),  # Variable
                ("        self.technologies = []", '#e06c75'),
                ("        self.features = []", '#e06c75'),
                ("        self.analysis_complete = False", '#e06c75'),
                ("", ''),
                ("    def analyze_codebase(self):", '#61dafb'),
                ("        \"\"\"Analyze repository structure\"\"\"", '#98c379'),  # String
                ("        return self.extract_insights()", '#e5c07b'),  # Method call
                ("", ''),
                ("    def generate_presentation(self):", '#61dafb'),
                ("        if self.analysis_complete:", '#c678dd'),
                ("            return create_video_content()", '#e5c07b'),
                ("        else:", '#c678dd'),
                ("            raise ValueError('Analysis required')", '#d19a66'),  # Error
            ]
            
            # Draw line numbers and code
            line_num_x = editor_x + 15
            code_start_x = editor_x + 60
            code_start_y = editor_y + header_height + 20
            line_height = 28
            
            for i, (line, color) in enumerate(code_lines):
                if i >= 16:  # Limit lines to fit in editor
                    break
                    
                current_y = code_start_y + i * line_height
                
                # Line number
                line_num = str(i + 1).rjust(2)
                if code_font:
                    draw.text((line_num_x, current_y), line_num, fill='#5c6370', font=code_font)
                else:
                    draw.text((line_num_x, current_y), line_num, fill='#5c6370')
                
                # Code line with syntax coloring
                if line.strip():
                    if code_font:
                        draw.text((code_start_x, current_y), line, fill=color or '#abb2bf', font=code_font)
                    else:
                        draw.text((code_start_x, current_y), line, fill=color or '#abb2bf')
            
            # Draw cursor (blinking effect simulation)
            cursor_x = code_start_x + 300
            cursor_y = code_start_y + 17 * line_height
            draw.rectangle([cursor_x, cursor_y, cursor_x + 2, cursor_y + 20], fill='#61dafb')
            
        except Exception as e:
            logger.error(f"Error drawing code scene: {e}")
    
    def _draw_conclusion_scene(self, draw: ImageDraw.Draw, scene: Dict[str, Any]):
        """Draw conclusion scene content"""
        try:
            try:
                title_font = ImageFont.truetype("arial.ttf", 48)
                text_font = ImageFont.truetype("arial.ttf", 24)
            except OSError:
                title_font = text_font = None
            
            # Draw "Thank You" title
            title = "Thank You!"
            if title_font:
                try:
                    title_bbox = draw.textbbox((0, 0), title, font=title_font)
                    title_width = title_bbox[2] - title_bbox[0]
                except:
                    title_width = len(title) * 30
            else:
                title_width = len(title) * 30
                
            title_x = (self.width - title_width) // 2
            title_y = self.height // 2 - 150
            
            if title_font:
                draw.text((title_x + 2, title_y + 2), title, fill='#000000', font=title_font)
                draw.text((title_x, title_y), title, fill='#ffffff', font=title_font)
            else:
                draw.text((title_x + 2, title_y + 2), title, fill='#000000')
                draw.text((title_x, title_y), title, fill='#ffffff')
            
            # Draw call to action
            cta_text = f"Explore {scene['repo_name']}"
            if text_font:
                try:
                    cta_bbox = draw.textbbox((0, 0), cta_text, font=text_font)
                    cta_width = cta_bbox[2] - cta_bbox[0]
                except:
                    cta_width = len(cta_text) * 16
            else:
                cta_width = len(cta_text) * 16
                
            cta_x = (self.width - cta_width) // 2
            cta_y = title_y + 100
            
            if text_font:
                draw.text((cta_x + 1, cta_y + 1), cta_text, fill='#000000', font=text_font)
                draw.text((cta_x, cta_y), cta_text, fill='#cccccc', font=text_font)
            else:
                draw.text((cta_x + 1, cta_y + 1), cta_text, fill='#000000')
                draw.text((cta_x, cta_y), cta_text, fill='#cccccc')
            
        except Exception as e:
            logger.error(f"Error drawing conclusion scene: {e}")
    
    def _draw_content_scene(self, draw: ImageDraw.Draw, scene: Dict[str, Any]):
        """Draw general content scene with enhanced formatting"""
        try:
            try:
                title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
                text_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
            except OSError:
                try:
                    title_font = ImageFont.truetype("arial.ttf", 48)
                    text_font = ImageFont.truetype("arial.ttf", 32)
                except OSError:
                    title_font = text_font = None
            
            # Create content box with enhanced styling
            content_box_x = 150
            content_box_y = 200
            content_box_width = self.width - 300
            content_box_height = 500
            
            # Draw content box background
            draw.rectangle([content_box_x, content_box_y, content_box_x + content_box_width, content_box_y + content_box_height], 
                          fill='#1a202c', outline='#4a90e2', width=4)
            
            # Content title
            content_title = scene.get('title', 'Repository Details')
            if title_font:
                try:
                    title_bbox = draw.textbbox((0, 0), content_title, font=title_font)
                    title_width = title_bbox[2] - title_bbox[0]
                except:
                    title_width = len(content_title) * 28
            else:
                title_width = len(content_title) * 28
            
            title_x = content_box_x + (content_box_width - title_width) // 2
            title_y = content_box_y + 20
            
            if title_font:
                draw.text((title_x + 3, title_y + 3), content_title, fill='#000000', font=title_font)
                draw.text((title_x, title_y), content_title, fill='#4a90e2', font=title_font)
            else:
                draw.text((title_x + 3, title_y + 3), content_title, fill='#000000')
                draw.text((title_x, title_y), content_title, fill='#4a90e2')
            
            # Draw wrapped text with better formatting
            text = self._wrap_text(scene['text'], 65)
            text_lines = text.split('\n')[:12]  # Max 12 lines
            line_height = 35
            text_start_y = content_box_y + 80
            
            for i, line in enumerate(text_lines):
                if line.strip():
                    # Add bullet points for better readability
                    if i > 0 and len(line.strip()) > 3:
                        line = "• " + line.strip()
                    
                    line_x = content_box_x + 30
                    line_y = text_start_y + i * line_height
                    
                    # Ensure text doesn't go beyond box
                    if line_y + line_height > content_box_y + content_box_height - 20:
                        break
                    
                    if text_font:
                        draw.text((line_x + 2, line_y + 2), line, fill='#000000', font=text_font)
                        draw.text((line_x, line_y), line, fill='#ffffff', font=text_font)
                    else:
                        draw.text((line_x + 2, line_y + 2), line, fill='#000000')
                        draw.text((line_x, line_y), line, fill='#ffffff')
            
        except Exception as e:
            logger.error(f"Error drawing content scene: {e}")
    
    def _wrap_text(self, text: str, width: int) -> str:
        """Wrap text to specified width"""
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 <= width:
                current_line.append(word)
                current_length += len(word) + 1
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return '\n'.join(lines)
    
    def _adjust_color_brightness(self, hex_color: str, brightness: int) -> str:
        """Adjust color brightness"""
        try:
            # Remove # if present
            hex_color = hex_color.lstrip('#')
            
            # Convert to RGB
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            
            # Adjust brightness
            r = min(255, max(0, r + brightness))
            g = min(255, max(0, g + brightness))
            b = min(255, max(0, b + brightness))
            
            return f'#{r:02x}{g:02x}{b:02x}'
            
        except Exception:
            return hex_color  # Return original if conversion fails
    
    def _compile_video(self, frame_files: List[str], output_file: str, duration: float) -> str:
        """Compile frames into video using ffmpeg"""
        try:
            if not frame_files:
                raise Exception("No frames to compile")
            
            # Create a text file listing all frames
            frame_list_file = os.path.join(self.temp_dir, f'frames_{os.path.basename(output_file)}.txt')
            frame_duration = duration / len(frame_files)
            
            with open(frame_list_file, 'w') as f:
                for frame_file in frame_files:
                    f.write(f"file '{frame_file}'\n")
                    f.write(f"duration {frame_duration}\n")
                # Add last frame again to ensure proper duration
                if frame_files:
                    f.write(f"file '{frame_files[-1]}'\n")
            
            # Use ffmpeg to create video with CPU-optimized settings
            cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', frame_list_file,
                '-vf', f'fps={self.fps},scale={self.width}:{self.height}',
                '-c:v', 'libx264',
                '-preset', 'ultrafast',  # Faster encoding
                '-crf', '25',            # Slightly lower quality for speed
                '-pix_fmt', 'yuv420p',
                '-threads', '0',         # Use all CPU cores
                '-y',                    # Overwrite output file
                output_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode != 0:
                logger.error(f"ffmpeg error: {result.stderr}")
                raise Exception(f"Video compilation failed: {result.stderr}")
            
            # Clean up frame list file
            os.remove(frame_list_file)
            
            return output_file
            
        except Exception as e:
            logger.error(f"Error compiling video: {e}")
            raise
    
    def _cleanup_frames(self, frame_files: List[str]):
        """Clean up temporary frame files"""
        try:
            for frame_file in frame_files:
                if os.path.exists(frame_file):
                    os.remove(frame_file)
            logger.info(f"Cleaned up {len(frame_files)} frame files")
        except Exception as e:
            logger.error(f"Error cleaning up frames: {e}")
    
    def _generate_fallback_video(self, session_id: str, script: str, repo_analysis: Dict[str, Any]) -> str:
        """Generate a simple fallback video"""
        try:
            output_file = os.path.join(self.temp_dir, f'repo2reel_{session_id}_video_fallback.mp4')
            
            # Create a simple video using ffmpeg
            duration = min(len(script.split()) * 0.4, 180)
            repo_name = repo_analysis.get('repository_name', 'Repository')
            
            cmd = [
                'ffmpeg',
                '-f', 'lavfi',
                '-i', f'color=c=blue:size={self.width}x{self.height}:duration={duration}',
                '-vf', f'drawtext=text="{repo_name}":fontsize=60:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2',
                '-c:v', 'libx264',
                '-preset', 'ultrafast',
                '-y',
                output_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                logger.info(f"Generated fallback video: {output_file}")
                return output_file
            else:
                raise Exception("Fallback video generation failed")
                
        except Exception as e:
            logger.error(f"Error generating fallback video: {e}")
            raise Exception("Could not generate video")

def generate_video_from_script(script: str, repo_analysis: Dict[str, Any], session_id: str) -> str:
    """Main function to generate video from script"""
    try:
        generator = VideoGenerator()
        return generator.generate_video(script, repo_analysis, session_id)
    except Exception as e:
        logger.error(f"Failed to generate video: {e}")
        raise
