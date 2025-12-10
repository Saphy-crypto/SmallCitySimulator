import pygame
import sys
from typing import Dict, Tuple
from datetime import date
from city import City, Location, LocationType, create_default_city
from agent import Agent, generate_random_agent

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (160, 32, 240)
PINK = (255, 192, 203)
BROWN = (139, 69, 19)
CYAN = (0, 255, 255)

# Location type colors
LOCATION_COLORS = {
    LocationType.RESIDENTIAL: BLUE,
    LocationType.WORKPLACE: RED,
    LocationType.SCHOOL: YELLOW,
    LocationType.RETAIL: ORANGE,
    LocationType.RESTAURANT: PINK,
    LocationType.PARK: GREEN,
    LocationType.GYM: PURPLE,
    LocationType.ENTERTAINMENT: CYAN,
    LocationType.HOSPITAL: WHITE
}

class CitySimulation:
    def __init__(self, city: City, width=1200, height=800):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(f"{city.name} - Agent Simulation")
        
        self.city = city
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # Scaling factors
        self.grid_margin = 50
        self.grid_width = width - 400  # Leave room for info panel
        self.grid_height = height - 100
        self.scale_x = self.grid_width / city.grid_size
        self.scale_y = self.grid_height / city.grid_size
        
        self.selected_agent = None
        self.paused = False
        self.speed = 1  # Simulation speed multiplier
        self.show_names = True
        self.info_scroll_offset = 0  # For scrolling in info panel
        self.show_family_tree = False  # Toggle family tree view
        self.family_tree_clickable_areas = []  # Store clickable areas for family tree
        self.show_help_menu = False  # Toggle help menu
        self.show_agent_list = False  # Toggle agent list view
        self.agent_list_filter = "all"  # Current age filter: all, babies, toddlers, children, preteens, teens, young_adults, adults, elders
        self.agent_list_scroll_offset = 0  # Scroll offset for agent list
        self.agent_list_clickable_areas = []  # Store clickable areas for agent list
        
    def grid_to_screen(self, grid_pos: Tuple[int, int]) -> Tuple[int, int]:
        """Convert grid coordinates to screen coordinates"""
        x, y = grid_pos
        screen_x = self.grid_margin + x * self.scale_x
        screen_y = self.grid_margin + y * self.scale_y
        return (int(screen_x), int(screen_y))
    
    def draw_location(self, location: Location):
        """Draw a location on the map"""
        pos = self.grid_to_screen(location.position)
        color = LOCATION_COLORS.get(location.location_type, GRAY)
        
        # Draw location as a rectangle
        size = max(8, min(30, location.capacity // 5))
        rect = pygame.Rect(pos[0] - size//2, pos[1] - size//2, size, size)
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, BLACK, rect, 1)
        
        # Draw name if show_names is True
        if self.show_names:
            name_text = self.small_font.render(location.name[:15], True, BLACK)
            self.screen.blit(name_text, (pos[0] - name_text.get_width()//2, pos[1] + size//2 + 2))
        
        # Draw occupancy count
        count_text = self.small_font.render(str(len(location.current_occupants)), True, WHITE)
        self.screen.blit(count_text, (pos[0] - count_text.get_width()//2, pos[1] - count_text.get_height()//2))
    
    def draw_agent(self, agent: Agent):
        """Draw an agent on the map"""
        if agent.current_location not in self.city.locations:
            return
        
        location = self.city.locations[agent.current_location]
        pos = self.grid_to_screen(location.position)
        
        # Offset agents within same location slightly
        occupants = location.current_occupants
        if agent.id in occupants:
            index = occupants.index(agent.id)
            offset_x = (index % 3 - 1) * 8
            offset_y = (index // 3 - 1) * 8
            pos = (pos[0] + offset_x, pos[1] + offset_y)
        
        # Draw agent as a circle
        color = PURPLE if agent.id == self.selected_agent else BLACK
        radius = 10 if agent.id == self.selected_agent else 7
        pygame.draw.circle(self.screen, color, pos, radius)
        
        # Draw name if selected
        if agent.id == self.selected_agent:
            name_text = self.small_font.render(agent.name.split()[0], True, PURPLE)
            self.screen.blit(name_text, (pos[0] + 8, pos[1] - 8))
    
    def draw_info_panel(self):
        """Draw the information panel on the right side"""
        panel_x = self.width - 350
        panel_y = 10
        
        # Background
        pygame.draw.rect(self.screen, LIGHT_GRAY, (panel_x, panel_y, 340, self.height - 20))
        pygame.draw.rect(self.screen, BLACK, (panel_x, panel_y, 340, self.height - 20), 2)
        
        # Time info
        y_offset = panel_y + 10
        date_text = self.font.render(f"{self.city.current_date.strftime('%Y-%m-%d')}", True, BLACK)
        self.screen.blit(date_text, (panel_x + 10, y_offset))
        y_offset += 25
        
        time_text = self.font.render(f"Day {self.city.current_day}, {self.city.current_time:02d}:00", True, BLACK)
        self.screen.blit(time_text, (panel_x + 10, y_offset))
        y_offset += 30
        
        # Format speed display nicely for high speeds
        if self.speed >= 1000000:
            speed_display = f"{self.speed//1000000}M"
        elif self.speed >= 10000:
            speed_display = f"{self.speed//1000}k"
        elif self.speed >= 1000:
            speed_display = f"{self.speed//1000}.{(self.speed%1000)//100}k"
        else:
            speed_display = f"{self.speed}"
        
        status_text = self.small_font.render(f"{'PAUSED' if self.paused else 'RUNNING'} (Speed: {speed_display}x)", True, RED if self.paused else GREEN)
        self.screen.blit(status_text, (panel_x + 10, y_offset))
        y_offset += 30
        
        # Agent count
        agent_count_text = self.small_font.render(f"Agents: {len(self.city.agents)}", True, BLACK)
        self.screen.blit(agent_count_text, (panel_x + 10, y_offset))
        y_offset += 25
        
        # Locations count
        loc_count_text = self.small_font.render(f"Locations: {len(self.city.locations)}", True, BLACK)
        self.screen.blit(loc_count_text, (panel_x + 10, y_offset))
        y_offset += 25
        
        # Graveyard count
        graveyard_count_text = self.small_font.render(f"💀 Deceased: {len(self.city.graveyard)}", True, (100, 100, 100))
        self.screen.blit(graveyard_count_text, (panel_x + 10, y_offset))
        y_offset += 35
        
        # Agent list button (when no agent is selected)
        if not self.selected_agent:
            pygame.draw.line(self.screen, BLACK, (panel_x + 10, y_offset), (panel_x + 330, y_offset), 1)
            y_offset += 15
            
            agent_list_button_text = self.font.render("👥 Agent Browser", True, BLUE)
            self.screen.blit(agent_list_button_text, (panel_x + 10, y_offset))
            # Store button area for clicking
            self.agent_list_button_area = (panel_x + 10, y_offset, agent_list_button_text.get_width(), agent_list_button_text.get_height())
            y_offset += 30
        
        # Selected agent info
        if self.selected_agent and (self.selected_agent in self.city.agents or self.selected_agent in self.city.graveyard):
            agent = self.city.agents.get(self.selected_agent) or self.city.graveyard.get(self.selected_agent)
            is_deceased = agent.is_deceased
            
            pygame.draw.line(self.screen, BLACK, (panel_x + 10, y_offset), (panel_x + 330, y_offset), 1)
            y_offset += 10
            
            title = "💀 Deceased Agent" if is_deceased else "Selected Agent"
            title_color = (100, 100, 100) if is_deceased else BLACK
            title_text = self.font.render(title, True, title_color)
            self.screen.blit(title_text, (panel_x + 10, y_offset))
            y_offset += 25
            
            # Family tree button
            tree_button_text = self.small_font.render("🌳 Family Tree", True, BLUE)
            self.screen.blit(tree_button_text, (panel_x + 10, y_offset))
            # Store button area for clicking
            self.family_tree_button_area = (panel_x + 10, y_offset, tree_button_text.get_width(), tree_button_text.get_height())
            y_offset += 30
            
            # Get current action and separate hobbies (use cached action)
            if is_deceased:
                action_text = "deceased"
                hobby_text = ""
            else:
                current_action = agent.current_action
                action_text = current_action
                hobby_text = ""
                
                if current_action.startswith("hobby: "):
                    action_text = "pursuing hobby"
                    hobby_text = current_action[7:]  # Remove "hobby: " prefix
            
            # Get detailed relationship info
            partner_info = "None"
            relationship_duration = ""
            if agent.partner_id and agent.partner_id in self.city.agents:
                partner = self.city.agents[agent.partner_id]
                partner_info = f"{partner.name} (ID: {partner.id})"
                if agent.days_in_relationship > 0:
                    days = agent.days_in_relationship
                    if days < 30:
                        # Show days for first month
                        relationship_duration = f" ({days}d together)"
                    elif days < 365:
                        # Show months after 30 days
                        months = days // 30
                        remaining_days = days % 30
                        if remaining_days > 0:
                            relationship_duration = f" ({months}m {remaining_days}d together)"
                        else:
                            relationship_duration = f" ({months}m together)"
                    else:
                        # Show years and months after 365 days
                        years = days // 365
                        months = (days % 365) // 30
                        remaining_days = days % 30
                        if months > 0:
                            relationship_duration = f" ({years}y {months}m together)"
                        else:
                            relationship_duration = f" ({years}y together)"
            
            # Build detailed friends list
            friends_info = []
            for friend_id in agent.friend_ids:
                if friend_id in self.city.agents:
                    friend = self.city.agents[friend_id]
                    friends_info.append(f"{friend.name} (ID: {friend.id})")
            
            info_lines = [
                f"ID: {agent.id}",
                f"Name: {agent.name}",
                f"Age: {agent.age} years old",
                f"Birthday: {agent.birthday.strftime('%m-%d')}",
                f"Gender: {agent.gender}",
                f"Orientation: {agent.sexual_orientation.value}",
            ]
            
            # Add death information if deceased
            if is_deceased:
                info_lines.extend([
                    f"",
                    f"💀 STATUS: DECEASED",
                    f"Date of Death: {agent.date_of_death.strftime('%Y-%m-%d') if agent.date_of_death else 'Unknown'}",
                    f"Age at Death: {agent.age} years",
                    f"",
                ])
            else:
                info_lines.extend([
                    f"",
                    f"Job: {agent.job_title or 'Unemployed'}",
                    f"Income: ${agent.annual_income:,}/year",
                    f"Education: {agent.education_level.value}",
                    f"",
                    f"Status: {agent.relationship_status.value}",
                    f"Partner: {partner_info}{relationship_duration}",
                ])
            
            # Add pregnancy status for female agents
            if agent.gender == "female":
                if agent.pregnancy_status.value == "pregnant":
                    weeks = agent.pregnancy_days // 7
                    info_lines.append(f"🤰 Pregnant ({weeks} weeks, {agent.pregnancy_days} days)")
                elif agent.pregnancy_status.value == "recently_gave_birth":
                    recovery_days = agent.days_since_birth
                    info_lines.append(f"👶 Recently gave birth ({recovery_days} days ago)")
            
            # Add children information
            if agent.children_ids:
                info_lines.extend([
                    f"",
                    f"Children ({len(agent.children_ids)}):",
                ])
                for child_id in agent.children_ids:
                    if child_id in self.city.agents:
                        child = self.city.agents[child_id]
                        info_lines.append(f"  • {child.name} (Age {child.age})")
                    else:
                        info_lines.append(f"  • Child ID: {child_id}")
            
            info_lines.extend([
                f"",
                f"Parents:",
                f"  Father: {self.get_parent_name(agent, 'father')}",
                f"  Mother: {self.get_parent_name(agent, 'mother')}",
                f"",
                f"Friends ({len(friends_info)}):",
            ])
            
            # Add each friend on a separate line
            if friends_info:
                for friend_info in friends_info:
                    info_lines.append(f"  • {friend_info}")
            else:
                info_lines.append("  None")
            
            info_lines.extend([
                f"",
                f"Happiness: {agent.happiness}/100",
                f"Health: {agent.health}/100",
                f"Energy: {agent.energy}/100",
                f"",
                f"Location: {self.city.get_location_name(agent.current_location)}",
                f"Action: {action_text}",
            ])
            
            # Add hobbies section if agent has hobbies
            if agent.hobbies:
                info_lines.extend([
                    f"",
                    f"Hobbies: {', '.join(agent.hobbies)}",
                    f"Current hobby: {hobby_text}" if hobby_text else "",
                ])
            
            info_lines.extend([
                f"",
                f"Life Goals:",
            ])
            
            # Add each life goal
            if agent.life_goals:
                for goal in agent.life_goals:
                    info_lines.append(f"  • {goal.value.replace('_', ' ').title()}")
            else:
                info_lines.append("  None")
            
            info_lines.extend([
                f"",
                f"Personality:",
                f"  Openness: {agent.personality.openness}",
                f"  Conscientious: {agent.personality.conscientiousness}",
                f"  Extraversion: {agent.personality.extraversion}",
                f"  Agreeableness: {agent.personality.agreeableness}",
                f"  Neuroticism: {agent.personality.neuroticism}",
            ])
            
            # Apply scroll offset and draw visible lines
            start_line = max(0, self.info_scroll_offset)
            visible_lines = (self.height - y_offset - 30) // 20  # How many lines fit
            end_line = min(len(info_lines), start_line + visible_lines)
            
            for i in range(start_line, end_line):
                line = info_lines[i]
                text = self.small_font.render(line, True, BLACK)
                self.screen.blit(text, (panel_x + 15, y_offset))
                y_offset += 20
            
            # Scroll indicators
            if self.info_scroll_offset > 0:
                up_indicator = self.small_font.render("↑ More above", True, BLUE)
                self.screen.blit(up_indicator, (panel_x + 15, panel_y + 40))
            
            if end_line < len(info_lines):
                down_indicator = self.small_font.render("↓ More below", True, BLUE)
                self.screen.blit(down_indicator, (panel_x + 15, self.height - 50))
    
    def draw_help_menu(self):
        """Draw help menu overlay"""
        # Semi-transparent background
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Help menu box
        menu_width = 400
        menu_height = 300
        menu_x = (self.width - menu_width) // 2
        menu_y = (self.height - menu_height) // 2
        
        pygame.draw.rect(self.screen, WHITE, (menu_x, menu_y, menu_width, menu_height))
        pygame.draw.rect(self.screen, BLACK, (menu_x, menu_y, menu_width, menu_height), 3)
        
        # Title
        title = self.font.render("Controls & Help", True, BLACK)
        self.screen.blit(title, (menu_x + 20, menu_y + 20))
        
        # Help text
        help_text = [
            "",
            "SIMULATION CONTROLS:",
            "  SPACE - Pause/Resume simulation",
            "  UP/DOWN Arrow - Adjust speed (1-100M x)",
            "  Speed presets:",
            "    1=1x, 2=10x, 3=50x, 4=200x, 5=500x",
            "    6=1k, 7=2k, 8=5k, 9=10k, 0=50k",
            "    Q=1M, W=10M, E=100M (MEGA SPEEDS!)",
            "  N - Toggle location names",
            "  A - Add random agent",
            "",
            "AGENT INTERACTION:",
            "  Click agent - Select and view info",
            "  Mouse wheel - Scroll panels",
            "  F - Open family tree view",
            "  L - Open agent browser",
            "  ESC - Close overlays",
            "",
            "Click anywhere to close this menu"
        ]
        
        y_offset = menu_y + 60
        for line in help_text:
            text = self.small_font.render(line, True, BLACK)
            self.screen.blit(text, (menu_x + 20, y_offset))
            y_offset += 18
    
    def draw_help_button(self):
        """Draw help button in top left corner"""
        button_text = self.small_font.render("❓ Help", True, WHITE)
        button_bg = pygame.Rect(10, 10, button_text.get_width() + 10, button_text.get_height() + 6)
        
        pygame.draw.rect(self.screen, BLUE, button_bg)
        pygame.draw.rect(self.screen, BLACK, button_bg, 2)
        self.screen.blit(button_text, (15, 13))
        
        # Store button area for clicking
        self.help_button_area = (10, 10, button_bg.width, button_bg.height)
    
    def draw_legend(self):
        """Draw the legend for location types"""
        legend_x = 10
        legend_y = self.height - 40
        
        x_offset = legend_x
        for loc_type, color in LOCATION_COLORS.items():
            pygame.draw.rect(self.screen, color, (x_offset, legend_y, 15, 15))
            pygame.draw.rect(self.screen, BLACK, (x_offset, legend_y, 15, 15), 1)
            
            text = self.small_font.render(loc_type.value, True, BLACK)
            self.screen.blit(text, (x_offset + 18, legend_y))
            x_offset += 100
            
            if x_offset > self.width - 500:
                break
    
    def handle_click(self, pos: Tuple[int, int]):
        """Handle mouse click to select agents"""
        # Check if click is on an agent
        for agent in self.city.agents.values():
            if agent.current_location not in self.city.locations:
                continue
            
            location = self.city.locations[agent.current_location]
            base_pos = self.grid_to_screen(location.position)
            
            # Calculate agent position with offset (same logic as in draw_agent)
            occupants = location.current_occupants
            agent_pos = base_pos
            if agent.id in occupants:
                index = occupants.index(agent.id)
                offset_x = (index % 3 - 1) * 8
                offset_y = (index // 3 - 1) * 8
                agent_pos = (base_pos[0] + offset_x, base_pos[1] + offset_y)
            
            # Check distance (increased to account for larger agent size)
            dist = ((pos[0] - agent_pos[0])**2 + (pos[1] - agent_pos[1])**2)**0.5
            if dist < 15:  # Increased from 10 to 15 to match larger agent radius
                self.selected_agent = agent.id
                return
        
        # Deselect if clicked elsewhere (but not in info panel area)
        info_panel_x = self.width - 350
        if pos[0] < info_panel_x:  # Only deselect if click is not in info panel
            self.selected_agent = None
    
    def get_info_lines(self):
        """Get all info lines for the selected agent (for scroll calculation)"""
        if not self.selected_agent or (self.selected_agent not in self.city.agents and self.selected_agent not in self.city.graveyard):
            return []
        
        agent = self.city.agents.get(self.selected_agent) or self.city.graveyard.get(self.selected_agent)
        
        # Build the same info lines as in draw_info_panel
        current_action = agent.current_action
        action_text = current_action
        hobby_text = ""
        
        if current_action.startswith("hobby: "):
            action_text = "pursuing hobby"
            hobby_text = current_action[7:]
        
        # Get detailed relationship info
        partner_info = "None"
        if agent.partner_id and agent.partner_id in self.city.agents:
            partner = self.city.agents[agent.partner_id]
            partner_info = f"{partner.name} (ID: {partner.id})"
        
        # Build detailed friends list
        friends_info = []
        for friend_id in agent.friend_ids:
            if friend_id in self.city.agents:
                friend = self.city.agents[friend_id]
                friends_info.append(f"{friend.name} (ID: {friend.id})")
        
        info_lines = [
            f"ID: {agent.id}",
            f"Name: {agent.name}",
            f"Age: {agent.age} years old",
            f"Birthday: {agent.birthday.strftime('%m-%d')}",
            f"Gender: {agent.gender}",
            f"Orientation: {agent.sexual_orientation.value}",
            f"",
            f"Job: {agent.job_title or 'Unemployed'}",
            f"Income: ${agent.annual_income:,}/year",
            f"Education: {agent.education_level.value}",
            f"",
            f"Status: {agent.relationship_status.value}",
            f"Partner: {partner_info}",
        ]
        
        # Add pregnancy status for female agents
        if agent.gender == "female":
            if agent.pregnancy_status.value == "pregnant":
                weeks = agent.pregnancy_days // 7
                info_lines.append(f"🤰 Pregnant ({weeks} weeks, {agent.pregnancy_days} days)")
            elif agent.pregnancy_status.value == "recently_gave_birth":
                recovery_days = agent.days_since_birth
                info_lines.append(f"👶 Recently gave birth ({recovery_days} days ago)")
        
        # Add children information
        if agent.children_ids:
            info_lines.extend([
                f"",
                f"Children ({len(agent.children_ids)}):",
            ])
            for child_id in agent.children_ids:
                if child_id in self.city.agents:
                    child = self.city.agents[child_id]
                    info_lines.append(f"  • {child.name} (Age {child.age})")
                else:
                    info_lines.append(f"  • Child ID: {child_id}")
        
        info_lines.extend([
            f"",
            f"Parents:",
            f"  Father: {self.get_parent_name(agent, 'father')}",
            f"  Mother: {self.get_parent_name(agent, 'mother')}",
            f"",
            f"Friends ({len(friends_info)}):",
        ])
        
        # Add each friend
        if friends_info:
            for friend_info in friends_info:
                info_lines.append(f"  • {friend_info}")
        else:
            info_lines.append("  None")
        
        info_lines.extend([
            f"",
            f"Happiness: {agent.happiness}/100",
            f"Health: {agent.health}/100",
            f"Energy: {agent.energy}/100",
            f"",
            f"Location: {self.city.get_location_name(agent.current_location)}",
            f"Action: {action_text}",
        ])
        
        # Add hobbies section if agent has hobbies
        if agent.hobbies:
            info_lines.extend([
                f"",
                f"Hobbies: {', '.join(agent.hobbies)}",
                f"Current hobby: {hobby_text}" if hobby_text else "",
            ])
        
        info_lines.extend([
            f"",
            f"Life Goals:",
        ])
        
        # Add each life goal
        if agent.life_goals:
            for goal in agent.life_goals:
                info_lines.append(f"  • {goal.value.replace('_', ' ').title()}")
        else:
            info_lines.append("  None")
        
        info_lines.extend([
            f"",
            f"Personality:",
            f"  Openness: {agent.personality.openness}",
            f"  Conscientious: {agent.personality.conscientiousness}",
            f"  Extraversion: {agent.personality.extraversion}",
            f"  Agreeableness: {agent.personality.agreeableness}",
            f"  Neuroticism: {agent.personality.neuroticism}",
        ])
        
        return info_lines
    
    def get_parent_name(self, agent, parent_type):
        """Get parent name, checking if parent is alive in simulation or deceased"""
        if parent_type == 'father':
            parent_id = agent.father_id
            deceased_name = agent.father_name
        else:  # mother
            parent_id = agent.mother_id
            deceased_name = agent.mother_name
        
        # Check if parent is alive in the simulation
        if parent_id and parent_id in self.city.agents:
            parent = self.city.agents[parent_id]
            return f"{parent.name} (ID: {parent.id})"
        elif deceased_name:
            return f"{deceased_name} (deceased)"
        else:
            return "Unknown"
    
    def get_age_category(self, age):
        """Get age category for agent filtering"""
        if age < 2:
            return "babies"
        elif age < 4:
            return "toddlers" 
        elif age < 10:
            return "children"
        elif age < 13:
            return "preteens"
        elif age < 18:
            return "teens"
        elif age < 30:
            return "young_adults"
        elif age < 60:
            return "adults"
        else:
            return "elders"
    
    def get_filtered_agents(self):
        """Get agents filtered by current age category"""
        if self.agent_list_filter == "graveyard":
            # Show deceased agents from graveyard
            deceased_agents = list(self.city.graveyard.values())
            return sorted(deceased_agents, key=lambda a: a.date_of_death if a.date_of_death else date(1900, 1, 1), reverse=True)
        
        # Show living agents
        agents = list(self.city.agents.values())
        
        if self.agent_list_filter == "all":
            return sorted(agents, key=lambda a: a.age)
        else:
            filtered = [a for a in agents if self.get_age_category(a.age) == self.agent_list_filter]
            return sorted(filtered, key=lambda a: a.age)
    
    def draw_agent_list(self):
        """Draw agent list view with age filtering"""
        panel_x = self.width - 350
        panel_y = 10
        
        # Background
        pygame.draw.rect(self.screen, LIGHT_GRAY, (panel_x, panel_y, 340, self.height - 20))
        pygame.draw.rect(self.screen, BLACK, (panel_x, panel_y, 340, self.height - 20), 2)
        
        # Clear clickable areas
        self.agent_list_clickable_areas = []
        
        y_offset = panel_y + 10
        
        # Title
        title_text = self.font.render("Agent Browser", True, BLACK)
        self.screen.blit(title_text, (panel_x + 10, y_offset))
        y_offset += 35
        
        # Back button
        back_text = self.small_font.render("← Back", True, BLUE)
        self.screen.blit(back_text, (panel_x + 10, y_offset))
        self.agent_list_clickable_areas.append(("back", panel_x + 10, y_offset, back_text.get_width(), back_text.get_height()))
        y_offset += 25
        
        # Age filter buttons
        filters = [
            ("all", "All"), ("babies", "Babies"), ("toddlers", "Toddlers"), 
            ("children", "Children"), ("preteens", "Preteens"), ("teens", "Teens"),
            ("young_adults", "Young Adults"), ("adults", "Adults"), ("elders", "Elders"),
            ("graveyard", "💀 Graveyard")
        ]
        
        filter_y = y_offset
        for i, (filter_key, filter_name) in enumerate(filters):
            if i == 3:  # Start new row after 3 filters
                y_offset = filter_y + 20
                filter_x = panel_x + 10
            elif i == 6:  # Start third row
                y_offset = filter_y + 40 
                filter_x = panel_x + 10
            elif i == 9:  # Start fourth row for graveyard
                y_offset = filter_y + 60
                filter_x = panel_x + 10
            else:
                filter_x = panel_x + 10 + (i % 3) * 110
            
            # Highlight current filter
            color = RED if filter_key == self.agent_list_filter else BLUE
            filter_text = self.small_font.render(filter_name, True, color)
            self.screen.blit(filter_text, (filter_x, y_offset))
            self.agent_list_clickable_areas.append((f"filter_{filter_key}", filter_x, y_offset, filter_text.get_width(), filter_text.get_height()))
        
        y_offset = filter_y + 85  # More space for 4 rows of filters
        
        # Agent count for current filter
        filtered_agents = self.get_filtered_agents()
        if self.agent_list_filter == "graveyard":
            count_label = "deceased souls" if len(filtered_agents) != 1 else "deceased soul"
            count_text = self.small_font.render(f"{len(filtered_agents)} {count_label}", True, BLACK)
        else:
            count_label = "agents" if len(filtered_agents) != 1 else "agent"
            count_text = self.small_font.render(f"{len(filtered_agents)} {count_label}", True, BLACK)
        self.screen.blit(count_text, (panel_x + 10, y_offset))
        y_offset += 25
        
        # Agent list
        pygame.draw.line(self.screen, BLACK, (panel_x + 10, y_offset), (panel_x + 330, y_offset), 1)
        y_offset += 10
        
        # Calculate visible agents
        max_visible = (self.height - y_offset - 50) // 20
        start_index = self.agent_list_scroll_offset
        end_index = min(len(filtered_agents), start_index + max_visible)
        
        for i in range(start_index, end_index):
            agent = filtered_agents[i]
            
            # Agent info line
            age_cat = self.get_age_category(agent.age)
            status_icon = ""
            
            if self.agent_list_filter == "graveyard":
                # Special display for deceased agents
                status_icon = "💀"
                death_info = f" (died on {agent.date_of_death})" if agent.date_of_death else " (deceased)"
                agent_line = f"{status_icon} {agent.name} ({agent.age}y){death_info}"
                agent_text = self.small_font.render(agent_line, True, (100, 100, 100))  # Gray text for deceased
            else:
                # Normal display for living agents
                if agent.relationship_status.value == "married":
                    status_icon = "💑"
                elif agent.relationship_status.value == "dating":
                    status_icon = "💕"
                elif agent.pregnancy_status.value == "pregnant":
                    status_icon = "🤰"
                
                agent_line = f"{status_icon} {agent.name} ({agent.age}y)"
                agent_text = self.small_font.render(agent_line, True, BLUE)
            self.screen.blit(agent_text, (panel_x + 15, y_offset))
            
            # Store clickable area
            self.agent_list_clickable_areas.append((f"agent_{agent.id}", panel_x + 15, y_offset, agent_text.get_width(), agent_text.get_height()))
            
            y_offset += 20
        
        # Scroll indicators
        if self.agent_list_scroll_offset > 0:
            up_indicator = self.small_font.render("↑ More above", True, BLUE)
            self.screen.blit(up_indicator, (panel_x + 15, panel_y + 50))
        
        if end_index < len(filtered_agents):
            down_indicator = self.small_font.render("↓ More below", True, BLUE)
            self.screen.blit(down_indicator, (panel_x + 15, self.height - 40))
    
    def handle_agent_list_click(self, pos: Tuple[int, int]):
        """Handle clicks in agent list view"""
        for area in self.agent_list_clickable_areas:
            area_type = area[0]
            x, y, w, h = area[1], area[2], area[3], area[4]
            
            if x <= pos[0] <= x + w and y <= pos[1] <= y + h:
                if area_type == "back":
                    self.show_agent_list = False
                    return
                elif area_type.startswith("filter_"):
                    filter_key = area_type[7:]  # Remove "filter_" prefix
                    self.agent_list_filter = filter_key
                    self.agent_list_scroll_offset = 0  # Reset scroll
                    return
                elif area_type.startswith("agent_"):
                    agent_id = area_type[6:]  # Remove "agent_" prefix
                    if agent_id in self.city.agents:
                        self.selected_agent = agent_id
                        self.show_agent_list = False
                        self.info_scroll_offset = 0
                    return
    
    def draw_family_tree(self):
        """Draw family tree view for selected agent"""
        if not self.selected_agent or (self.selected_agent not in self.city.agents and self.selected_agent not in self.city.graveyard):
            return
            
        agent = self.city.agents.get(self.selected_agent) or self.city.graveyard.get(self.selected_agent)
        panel_x = self.width - 350
        panel_y = 10
        
        # Background
        pygame.draw.rect(self.screen, LIGHT_GRAY, (panel_x, panel_y, 340, self.height - 20))
        pygame.draw.rect(self.screen, BLACK, (panel_x, panel_y, 340, self.height - 20), 2)
        
        # Clear clickable areas
        self.family_tree_clickable_areas = []
        
        y_offset = panel_y + 10
        
        # Title
        title_text = self.font.render(f"Family Tree: {agent.name}", True, BLACK)
        self.screen.blit(title_text, (panel_x + 10, y_offset))
        y_offset += 40
        
        # Back button
        back_text = self.small_font.render("← Back to Profile", True, BLUE)
        self.screen.blit(back_text, (panel_x + 10, y_offset))
        self.family_tree_clickable_areas.append(("back", panel_x + 10, y_offset, back_text.get_width(), back_text.get_height()))
        y_offset += 30
        
        # Parents section
        parents_title = self.font.render("Parents:", True, BLACK)
        self.screen.blit(parents_title, (panel_x + 10, y_offset))
        y_offset += 25
        
        # Father
        if agent.father_id and agent.father_id in self.city.agents:
            father = self.city.agents[agent.father_id]
            father_text = self.small_font.render(f"Father: {father.name}", True, BLUE)
            self.screen.blit(father_text, (panel_x + 20, y_offset))
            self.family_tree_clickable_areas.append(("agent", agent.father_id, panel_x + 20, y_offset, father_text.get_width(), father_text.get_height()))
        else:
            father_name = self.get_parent_name(agent, 'father')
            father_text = self.small_font.render(f"Father: {father_name}", True, GRAY)
            self.screen.blit(father_text, (panel_x + 20, y_offset))
        y_offset += 20
        
        # Mother
        if agent.mother_id and agent.mother_id in self.city.agents:
            mother = self.city.agents[agent.mother_id]
            mother_text = self.small_font.render(f"Mother: {mother.name}", True, BLUE)
            self.screen.blit(mother_text, (panel_x + 20, y_offset))
            self.family_tree_clickable_areas.append(("agent", agent.mother_id, panel_x + 20, y_offset, mother_text.get_width(), mother_text.get_height()))
        else:
            mother_name = self.get_parent_name(agent, 'mother')
            mother_text = self.small_font.render(f"Mother: {mother_name}", True, GRAY)
            self.screen.blit(mother_text, (panel_x + 20, y_offset))
        y_offset += 30
        
        # Partner section
        partner_title = self.font.render("Partner:", True, BLACK)
        self.screen.blit(partner_title, (panel_x + 10, y_offset))
        y_offset += 25
        
        if agent.partner_id and agent.partner_id in self.city.agents:
            partner = self.city.agents[agent.partner_id]
            partner_text = self.small_font.render(f"{agent.relationship_status.value.title()}: {partner.name}", True, BLUE)
            self.screen.blit(partner_text, (panel_x + 20, y_offset))
            self.family_tree_clickable_areas.append(("agent", agent.partner_id, panel_x + 20, y_offset, partner_text.get_width(), partner_text.get_height()))
        else:
            partner_text = self.small_font.render("None", True, GRAY)
            self.screen.blit(partner_text, (panel_x + 20, y_offset))
        y_offset += 30
        
        # Children section
        children_title = self.font.render(f"Children ({len(agent.children_ids)}):", True, BLACK)
        self.screen.blit(children_title, (panel_x + 10, y_offset))
        y_offset += 25
        
        if agent.children_ids:
            for child_id in agent.children_ids:
                if child_id in self.city.agents:
                    child = self.city.agents[child_id]
                    child_text = self.small_font.render(f"• {child.name} (Age {child.age})", True, BLUE)
                    self.screen.blit(child_text, (panel_x + 20, y_offset))
                    self.family_tree_clickable_areas.append(("agent", child_id, panel_x + 20, y_offset, child_text.get_width(), child_text.get_height()))
                    y_offset += 20
        else:
            no_children_text = self.small_font.render("None", True, GRAY)
            self.screen.blit(no_children_text, (panel_x + 20, y_offset))
    
    def handle_family_tree_click(self, pos: Tuple[int, int]):
        """Handle clicks in family tree view"""
        for area in self.family_tree_clickable_areas:
            if area[0] == "back":
                _, x, y, w, h = area
                if x <= pos[0] <= x + w and y <= pos[1] <= y + h:
                    self.show_family_tree = False
                    return
            elif area[0] == "agent":
                _, agent_id, x, y, w, h = area
                if x <= pos[0] <= x + w and y <= pos[1] <= y + h:
                    self.selected_agent = agent_id
                    self.show_family_tree = False
                    return
    
    def run(self):
        """Main simulation loop"""
        running = True
        frames_per_hour = 30  # Simulate one hour every 30 frames
        frame_count = 0
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Check for help menu close (click anywhere when help is open)
                    if self.show_help_menu:
                        self.show_help_menu = False
                    # Check for help button click
                    elif (hasattr(self, 'help_button_area') and
                          self.help_button_area[0] <= event.pos[0] <= self.help_button_area[0] + self.help_button_area[2] and
                          self.help_button_area[1] <= event.pos[1] <= self.help_button_area[1] + self.help_button_area[3]):
                        self.show_help_menu = True
                    elif self.show_family_tree:
                        self.handle_family_tree_click(event.pos)
                    elif self.show_agent_list:
                        self.handle_agent_list_click(event.pos)
                    else:
                        # Check for family tree button click
                        if (self.selected_agent and hasattr(self, 'family_tree_button_area') and
                            self.family_tree_button_area[0] <= event.pos[0] <= self.family_tree_button_area[0] + self.family_tree_button_area[2] and
                            self.family_tree_button_area[1] <= event.pos[1] <= self.family_tree_button_area[1] + self.family_tree_button_area[3]):
                            self.show_family_tree = True
                            self.info_scroll_offset = 0  # Reset scroll
                        # Check for agent list button click
                        elif (not self.selected_agent and hasattr(self, 'agent_list_button_area') and
                            self.agent_list_button_area[0] <= event.pos[0] <= self.agent_list_button_area[0] + self.agent_list_button_area[2] and
                            self.agent_list_button_area[1] <= event.pos[1] <= self.agent_list_button_area[1] + self.agent_list_button_area[3]):
                            self.show_agent_list = True
                            self.agent_list_scroll_offset = 0  # Reset scroll
                        else:
                            self.handle_click(event.pos)
                elif event.type == pygame.MOUSEWHEEL:
                    # Handle scrolling in various panels
                    mouse_pos = pygame.mouse.get_pos()
                    info_panel_x = self.width - 350
                    
                    if mouse_pos[0] >= info_panel_x and not self.show_help_menu:
                        if self.show_agent_list:
                            # Scroll agent list
                            filtered_agents = self.get_filtered_agents()
                            max_scroll = max(0, len(filtered_agents) - 15)  # Rough estimate
                            self.agent_list_scroll_offset = max(0, min(max_scroll, self.agent_list_scroll_offset - event.y * 3))
                        elif self.selected_agent and not self.show_family_tree:
                            # Scroll info panel
                            max_scroll = max(0, len(self.get_info_lines()) - 15)  # Rough estimate
                            self.info_scroll_offset = max(0, min(max_scroll, self.info_scroll_offset - event.y * 3))
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.paused = not self.paused
                    elif event.key == pygame.K_UP:
                        if self.speed < 10:
                            self.speed += 1
                        elif self.speed < 50:
                            self.speed += 10  # Jump by 10 for medium speeds
                        elif self.speed < 1000:
                            self.speed = min(1000, self.speed + 100)  # Jump by 100 for high speeds
                        elif self.speed < 50000:
                            self.speed = min(50000, self.speed + 5000)  # Jump by 5000 for ultra speeds
                        elif self.speed < 500000:
                            self.speed = min(500000, self.speed + 50000)  # Jump by 50k for extreme speeds
                        elif self.speed < 1000000:
                            self.speed = min(1000000, self.speed + 100000)  # Jump by 100k for insane speeds
                        elif self.speed < 10000000:
                            self.speed = min(10000000, self.speed + 1000000)  # Jump by 1M for ultra insane speeds
                        else:
                            self.speed = min(100000000, self.speed + 10000000)  # Jump by 10M for mega insane speeds
                    elif event.key == pygame.K_DOWN:
                        if self.speed > 10000000:
                            self.speed = max(10000000, self.speed - 10000000)  # Jump by 10M for mega insane speeds
                        elif self.speed > 1000000:
                            self.speed = max(1000000, self.speed - 1000000)  # Jump by 1M for ultra insane speeds
                        elif self.speed > 500000:
                            self.speed = max(500000, self.speed - 100000)  # Jump by 100k for insane speeds
                        elif self.speed > 50000:
                            self.speed = max(50000, self.speed - 50000)    # Jump by 50k for extreme speeds
                        elif self.speed > 1000:
                            self.speed = max(1000, self.speed - 5000)      # Jump by 5k for ultra speeds
                        elif self.speed > 50:
                            self.speed = max(50, self.speed - 100)         # Jump by 100 for high speeds
                        elif self.speed > 10:
                            self.speed = max(10, self.speed - 10)          # Jump by 10 for medium speeds
                        else:
                            self.speed = max(1, self.speed - 1)            # Single steps for low speeds
                    elif event.key == pygame.K_n:
                        self.show_names = not self.show_names
                    elif event.key == pygame.K_a:
                        # Add a new random agent
                        new_agent = generate_random_agent()
                        self.city.add_agent(new_agent)
                        self.selected_agent = new_agent.id
                    elif event.key == pygame.K_f:
                        # Toggle family tree view
                        if self.selected_agent:
                            self.show_family_tree = not self.show_family_tree
                            self.info_scroll_offset = 0
                    elif event.key == pygame.K_ESCAPE:
                        # Close any open overlays
                        if self.show_help_menu:
                            self.show_help_menu = False
                        elif self.show_family_tree:
                            self.show_family_tree = False
                        elif self.show_agent_list:
                            self.show_agent_list = False
                    elif event.key == pygame.K_h:
                        # Toggle help menu
                        self.show_help_menu = not self.show_help_menu
                    elif event.key == pygame.K_l:
                        # Toggle agent list
                        self.show_agent_list = not self.show_agent_list
                        self.agent_list_scroll_offset = 0
                    elif event.key == pygame.K_1:
                        # Set speed to 1x
                        self.speed = 1
                    elif event.key == pygame.K_2:
                        # Set speed to 10x
                        self.speed = 10
                    elif event.key == pygame.K_3:
                        # Set speed to 50x
                        self.speed = 50
                    elif event.key == pygame.K_4:
                        # Set speed to 200x
                        self.speed = 200
                    elif event.key == pygame.K_5:
                        # Set speed to 500x (fast forward)
                        self.speed = 500
                    elif event.key == pygame.K_6:
                        # Set speed to 1000x (ultra fast)
                        self.speed = 1000
                    elif event.key == pygame.K_7:
                        # Set speed to 2000x
                        self.speed = 2000
                    elif event.key == pygame.K_8:
                        # Set speed to 5000x (extreme)
                        self.speed = 5000
                    elif event.key == pygame.K_9:
                        # Set speed to 10000x (ultra extreme)
                        self.speed = 10000
                    elif event.key == pygame.K_0:
                        # Set speed to 50000x (extreme)
                        self.speed = 50000
                    elif event.key == pygame.K_q:
                        # Set speed to 1,000,000x (mega)
                        self.speed = 1000000
                    elif event.key == pygame.K_w:
                        # Set speed to 10,000,000x (ultra mega)
                        self.speed = 10000000
                    elif event.key == pygame.K_e:
                        # Set speed to 100,000,000x (insane mega)
                        self.speed = 100000000
            
            # Update simulation
            if not self.paused:
                frame_count += self.speed
                if frame_count >= frames_per_hour:
                    frame_count = 0
                    self.city.simulate_hour()
            
            # Draw everything
            self.screen.fill(WHITE)
            
            # Draw grid
            for i in range(0, self.city.grid_size + 1, 5):
                x_pos = self.grid_margin + i * self.scale_x
                y_pos = self.grid_margin + i * self.scale_y
                pygame.draw.line(self.screen, LIGHT_GRAY, (x_pos, self.grid_margin), 
                               (x_pos, self.grid_margin + self.grid_height), 1)
                pygame.draw.line(self.screen, LIGHT_GRAY, (self.grid_margin, y_pos), 
                               (self.grid_margin + self.grid_width, y_pos), 1)
            
            # Draw locations
            for location in self.city.locations.values():
                self.draw_location(location)
            
            # Draw agents
            for agent in self.city.agents.values():
                self.draw_agent(agent)
            
            # Draw UI
            if self.show_family_tree:
                self.draw_family_tree()
            elif self.show_agent_list:
                self.draw_agent_list()
            else:
                self.draw_info_panel()
            self.draw_legend()
            
            # Draw help button
            self.draw_help_button()
            
            # Draw help menu overlay if open
            if self.show_help_menu:
                self.draw_help_menu()
            
            pygame.display.flip()
            self.clock.tick(60)  # 60 FPS
        
        pygame.quit()


def main():
    """Main entry point"""
    print("Creating city...")
    city = create_default_city("SimCity")
    
    print("Generating initial agents...")
    for i in range(5):  # Start with 5 agents
        agent = generate_random_agent(age_range=(22, 45))
        city.add_agent(agent)
        print(f"  Added: {agent.name} ({agent.age}y, {agent.job_title})")
    
    print("\nStarting simulation...")
    print("Controls:")
    print("  SPACE - Pause/Resume")
    print("  UP/DOWN Arrow - Adjust speed (1-100Mx)")
    print("  1/2/3/4/5/6/7/8/9/0 - Speed presets (1x to 50000x)")
    print("  Q/W/E - MEGA speed presets (1M/10M/100M x)")
    print("  N - Toggle location names")
    print("  A - Add random agent")
    print("  L - Agent browser")
    print("  H - Help menu")
    print("  Click on an agent to view details")
    print("\nTIP: Use speed 1000x+ to quickly see generations develop!")
    print("EXTREME: Press '0' for 50000x speed  watch decades pass!")
    print("MEGA INSANE: Press 'Q/W/E' for 1M/10M/100M x speed - watch centuries fly by!")
    
    sim = CitySimulation(city)
    sim.run()


if __name__ == "__main__":
    main()
