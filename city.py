from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import random
from datetime import datetime, date, timedelta

class LocationType(Enum):
    RESIDENTIAL = "residential"
    WORKPLACE = "workplace"
    SCHOOL = "school"
    RETAIL = "retail"
    RESTAURANT = "restaurant"
    PARK = "park"
    GYM = "gym"
    ENTERTAINMENT = "entertainment"
    HOSPITAL = "hospital"

@dataclass
class Location:
    """A place in the city"""
    id: str
    name: str
    location_type: LocationType
    position: Tuple[int, int]  # (x, y) coordinates
    capacity: int = 50
    current_occupants: List[str] = field(default_factory=list)  # Agent IDs
    
    def can_accommodate(self) -> bool:
        return len(self.current_occupants) < self.capacity
    
    def add_occupant(self, agent_id: str) -> bool:
        if self.can_accommodate():
            self.current_occupants.append(agent_id)
            return True
        return False
    
    def remove_occupant(self, agent_id: str):
        if agent_id in self.current_occupants:
            self.current_occupants.remove(agent_id)

@dataclass
class Job:
    """Job opening in the city"""
    id: str
    title: str
    location_id: str
    required_education: str
    salary_range: Tuple[int, int]
    openings: int = 1
    filled_by: List[str] = field(default_factory=list)  # Agent IDs

class City:
    """The simulated city containing all locations and infrastructure"""
    
    def __init__(self, name: str, grid_size: int = 50, start_date: date = None):
        self.name = name
        self.grid_size = grid_size
        self.locations: Dict[str, Location] = {}
        self.jobs: Dict[str, Job] = {}
        self.agents: Dict[str, 'Agent'] = {}  # Will store all agents
        self.graveyard: Dict[str, 'Agent'] = {}  # Deceased agents
        self.current_time: int = 0  # Hour of simulation (0 to 23)
        self.current_day: int = 0
        self.current_date: date = start_date or date(2024, 1, 1)  # Start date of simulation
        
    def add_location(self, location: Location):
        """Add a location to the city"""
        self.locations[location.id] = location
    
    def add_job(self, job: Job):
        """Add a job opening to the city"""
        self.jobs[job.id] = job
    
    def add_agent(self, agent):
        """Add an agent to the city"""
        self.agents[agent.id] = agent
        
        # Assign home if not set
        if not agent.home_location:
            residential = [loc for loc in self.locations.values() 
                          if loc.location_type == LocationType.RESIDENTIAL and loc.can_accommodate()]
            if residential:
                home = random.choice(residential)
                agent.home_location = home.id
                agent.current_location = home.id
                home.add_occupant(agent.id)
        
        # Assign work if not unemployed and no work location
        if agent.age >= 18 and not agent.work_location:
            workplaces = [loc for loc in self.locations.values() 
                         if loc.location_type == LocationType.WORKPLACE and loc.can_accommodate()]
            if workplaces:
                work = random.choice(workplaces)
                agent.work_location = work.id
                
                # Assign job title based on workplace and education
                from agent import get_job_for_workplace
                agent.job_title = get_job_for_workplace(work.name, agent.education_level)
    
    def move_agent(self, agent_id: str, target_location_id: str):
        """Move an agent from their current location to a new one"""
        if agent_id not in self.agents:
            return False
        
        agent = self.agents[agent_id]
        
        # Remove from current location
        if agent.current_location and agent.current_location in self.locations:
            self.locations[agent.current_location].remove_occupant(agent_id)
        
        # Add to new location
        if target_location_id in self.locations:
            location = self.locations[target_location_id]
            if location.add_occupant(agent_id):
                agent.current_location = target_location_id
                return True
        
        return False
    
    def simulate_hour(self):
        """Simulate one hour passing"""
        self.current_time = (self.current_time + 1) % 24
        
        # New day
        if self.current_time == 0:
            self.current_day += 1
            self.current_date += timedelta(days=1)
            
            # Create a list copy to avoid "dictionary changed size during iteration" error
            agents_list = list(self.agents.values())
            
            # Update relationship durations for all agents (once per day)
            for agent in agents_list:
                agent.update_relationship_duration(1)
            
            # Check for birthdays and age agents
            for agent in agents_list:
                if agent.celebrate_birthday(self.current_date):
                    print(f"🎂 {agent.name} turned {agent.age} today!")
            
            # Check for deaths (daily)
            agents_to_remove = []
            for agent in agents_list:
                if not agent.is_deceased and agent.check_for_death(self.current_date):
                    print(f"💀 {agent.name} (age {agent.age}) has passed away.")
                    agents_to_remove.append(agent.id)
            
            # Move deceased agents to graveyard and handle cleanup
            for agent_id in agents_to_remove:
                self._handle_agent_death(agent_id)
        
        # Each agent decides what to do
        # Create a list copy to avoid "dictionary changed size during iteration" error
        agents_list = list(self.agents.values())
        for agent in agents_list:
            # Update agent's current action
            agent.current_action = agent.decide_action(self.current_time)
            self._update_agent_location(agent)
        
        # Handle social interactions at each location
        self._handle_social_interactions()
        
        # Daily pregnancy progression and accidental pregnancies
        if self.current_time == 12:  # Check daily at noon
            self._handle_pregnancies()
            self._handle_accidental_pregnancies()
        
        # Monthly checks
        if self.current_day % 30 == 0 and self.current_time == 12:  # Check at noon every 30 days
            self._check_relationship_health()
            self._handle_family_planning()
    
    def _update_agent_location(self, agent):
        """Update agent location based on their decision"""
        action = agent.current_action
        target_location = None
        
        if action == "sleeping":
            target_location = agent.home_location
        elif action == "at_home_with_care" or action == "at_home":
            target_location = agent.home_location
        elif action == "at_school":
            # Find a school appropriate for age
            schools = [loc for loc in self.locations.values() 
                      if loc.location_type == LocationType.SCHOOL]
            if schools:
                target_location = random.choice(schools).id
            else:
                target_location = agent.home_location  # Stay home if no school
        elif action == "working":
            target_location = agent.work_location
        elif action == "studying":
            # Find a school
            schools = [loc for loc in self.locations.values() 
                      if loc.location_type == LocationType.SCHOOL]
            if schools:
                target_location = random.choice(schools).id
        elif action == "socializing":
            # Go to restaurant, park, or entertainment
            social_places = [loc for loc in self.locations.values() 
                           if loc.location_type in [LocationType.RESTAURANT, 
                                                    LocationType.PARK, 
                                                    LocationType.ENTERTAINMENT]]
            if social_places:
                target_location = random.choice(social_places).id
        elif "hobby" in action:
            # Go to relevant location or stay home
            if random.random() < 0.5:
                target_location = agent.home_location
            else:
                target_location = random.choice(list(self.locations.keys()))
        else:
            # Default to home
            target_location = agent.home_location
        
        if target_location and target_location != agent.current_location:
            self.move_agent(agent.id, target_location)
    
    def _handle_social_interactions(self):
        """Handle social interactions between agents at the same locations"""
        import random
        
        # Create a snapshot to avoid iteration issues
        locations_list = list(self.locations.values())
        for location in locations_list:
            occupants = location.current_occupants[:]  # Copy the list
            
            # Need at least 2 people for interactions
            if len(occupants) < 2:
                continue
            
            # Check for interactions based on location type
            interaction_chance = self._get_interaction_chance(location.location_type)
            
            # Try interactions between random pairs
            for i in range(len(occupants)):
                for j in range(i + 1, len(occupants)):
                    agent1_id = occupants[i]
                    agent2_id = occupants[j]
                    
                    if agent1_id not in self.agents or agent2_id not in self.agents:
                        continue
                        
                    agent1 = self.agents[agent1_id]
                    agent2 = self.agents[agent2_id]
                    
                    # Check if they should interact
                    if random.random() < interaction_chance:
                        self._process_interaction(agent1, agent2, location)
    
    def _get_interaction_chance(self, location_type: LocationType) -> float:
        """Get the chance of interaction based on location type"""
        interaction_chances = {
            LocationType.RESTAURANT: 0.5,
            LocationType.PARK: 0.4,
            LocationType.ENTERTAINMENT: 0.6,
            LocationType.GYM: 0.35,
            LocationType.RETAIL: 0.25,
            LocationType.WORKPLACE: 0.2,
            LocationType.RESIDENTIAL: 0.1,
            LocationType.SCHOOL: 0.3,
            LocationType.HOSPITAL: 0.1
        }
        return interaction_chances.get(location_type, 0.1)
    
    def _process_interaction(self, agent1, agent2, location):
        """Process interaction between two agents"""
        import random
        
        # Calculate overall compatibility (personality + hobbies)
        compatibility = agent1.overall_compatibility(agent2)
        
        # Higher compatibility = better chance of positive interaction
        interaction_success = compatibility > 30 and random.random() < 0.6
        
        if interaction_success:
            # Develop friendship if not already friends and compatible
            if agent2.id not in agent1.friend_ids and compatibility > 35:
                # Higher compatibility equals better chance of friendship
                friendship_chance = min(0.15, (compatibility - 30) / 300)  # 0% to 15% chance
                if random.random() < friendship_chance:
                    agent1.develop_friendship(agent2)
                    # Debug: Print when friendship forms (remove this in production)
                    print(f"👥 {agent1.name} and {agent2.name} became friends! (Compatibility: {compatibility:.1f}%)")
            
            # If both single and already friends, chance to start dating
            elif (agent2.id in agent1.friend_ids and 
                  agent1.can_develop_relationship_with(agent2)):
                # High compatibility required for dating
                dating_chance = min(0.20, max(0, (compatibility - 40) / 300))  # 0% to 20% based on compatibility
                if random.random() < dating_chance:
                    success = agent1.start_relationship(agent2, self.current_date)
                    # Debug: Print when dating starts (remove this in production)
                    if success:
                        print(f"🥰 {agent1.name} and {agent2.name} started dating! (Compatibility: {compatibility:.1f}%)")
            
            # If dating, chance to propose (high compatibility + marriage goals needed)
            elif (agent1.partner_id == agent2.id and 
                  agent1.relationship_status.value == 'dating'):
                if agent1.can_propose_to(agent2) and random.random() < 0.03:  # 3% chance per interaction
                    success = agent1.propose_to(agent2)
                    if success:
                        print(f"💍 {agent1.name} proposed to {agent2.name} and they said YES!")
                    else:
                        print(f"💔 {agent1.name} proposed to {agent2.name} but they said no...")
                        
            # If engaged, chance to get married
            elif (agent1.partner_id == agent2.id and 
                  agent1.relationship_status.value == 'engaged'):
                if random.random() < 0.05:  # 5% chance per interaction to get married
                    agent1.get_married(agent2)
                    print(f"👰🤵 {agent1.name} and {agent2.name} got married!")
            
            # Small happiness boost from positive social interaction
            happiness_boost = int(compatibility / 50)  # 1 to 2 points based on compatibility
            agent1.happiness = min(100, agent1.happiness + happiness_boost)
            agent2.happiness = min(100, agent2.happiness + happiness_boost)
        
        # Check for relationship problems (even if no interaction this time)
        if agent1.partner_id == agent2.id:
            if agent1.should_breakup(agent2) and random.random() < 0.05:  # 5% chance to break up per interaction
                agent1.breakup(agent2)
                print(f"💔 {agent1.name} and {agent2.name} broke up due to incompatibility...")
    
    def _check_relationship_health(self):
        """Monthly check for relationship problems based on goal compatibility"""
        from agent import LifeGoal
        
        couples = []
        # Create a list copy to avoid "dictionary changed size during iteration" error
        agents_list = list(self.agents.values())
        for agent in agents_list:
            if agent.partner_id and agent.partner_id in self.agents:
                partner = self.agents[agent.partner_id]
                # Avoid checking the same couple twice
                if (agent.id, partner.id) not in [(p[1].id, p[0].id) for p in couples]:
                    couples.append((agent, partner))
        
        for agent1, agent2 in couples:
            goal_compatibility = agent1.goal_compatibility(agent2)
            overall_compatibility = agent1.overall_compatibility(agent2)
            
            # Major goal conflicts cause relationship stress
            if goal_compatibility < 20:
                # High chance of breakup for major goal conflicts
                if random.random() < 0.3:  # 30% chance per month for severely incompatible goals
                    agent1.breakup(agent2)
                    print(f"💔 {agent1.name} and {agent2.name} broke up due to incompatible life goals...")
                else:
                    # Happiness decreases due to ongoing conflicts
                    agent1.happiness = max(0, agent1.happiness - 5)
                    agent2.happiness = max(0, agent2.happiness - 5)
                    print(f"😔 {agent1.name} and {agent2.name} are having relationship difficulties...")
            
            elif overall_compatibility < 25:
                # General incompatibility 
                if random.random() < 0.15:  # 15% chance per month
                    agent1.breakup(agent2)
                    print(f"💔 {agent1.name} and {agent2.name} broke up due to overall incompatibility...")
    
    def _handle_pregnancies(self):
        """Handle pregnancy progression and births"""
        from agent import PregnancyStatus, create_child_agent
        
        # Create a list copy to avoid "dictionary changed size during iteration" error
        agents_list = list(self.agents.values())
        for agent in agents_list:
            if agent.pregnancy_status == PregnancyStatus.PREGNANT:
                # Progress pregnancy by 1 day
                gave_birth = agent.progress_pregnancy(1)
                
                if gave_birth:
                    child_id = agent.children_ids[-1]  # Get the newly added child ID
                    
                    # Find the father (could be partner or someone else for accidental pregnancy)
                    father = None
                    if agent.partner_id and agent.partner_id in self.agents:
                        father = self.agents[agent.partner_id]
                        father.children_ids.append(child_id)
                    else:
                        # For accidental pregnancies, try to find the father among friends/recent interactions
                        # For now, just assign a random male agent as father
                        male_agents = [a for a in self.agents.values() if a.gender == "male" and a.age >= 16]
                        if male_agents:
                            father = random.choice(male_agents)
                            father.children_ids.append(child_id)
                    
                    if father:
                        # Create child agent
                        child_agent = create_child_agent(agent, father, child_id, self.current_date)
                        self.add_agent(child_agent)
                        
                        print(f"👶 {agent.name} and {father.name} had a baby: {child_agent.name}!")
                    else:
                        print(f"👶 {agent.name} had a baby (father unknown)!")
                        
            elif agent.pregnancy_status == PregnancyStatus.RECENTLY_GAVE_BIRTH:
                # Update postpartum recovery daily
                agent.update_postpartum(1)
    
    def _handle_accidental_pregnancies(self):
        """Handle accidental pregnancies during social interactions"""
        # Create a snapshot of locations to avoid iteration issues
        locations_list = list(self.locations.values())
        for location in locations_list:
            occupants = location.current_occupants[:]  # Copy the list
            
            # Check for accidental pregnancies between males and females
            for i in range(len(occupants)):
                for j in range(i + 1, len(occupants)):
                    agent1_id = occupants[i]
                    agent2_id = occupants[j]
                    
                    if agent1_id not in self.agents or agent2_id not in self.agents:
                        continue
                        
                    agent1 = self.agents[agent1_id]
                    agent2 = self.agents[agent2_id]
                    
                    # Check for female and male pairs
                    if agent1.gender == "female" and agent2.gender == "male":
                        if agent1.try_accidental_pregnancy(agent2):
                            print(f"🤰 {agent1.name} accidentally got pregnant!")
                    elif agent2.gender == "female" and agent1.gender == "male":
                        if agent2.try_accidental_pregnancy(agent1):
                            print(f"🤰 {agent2.name} accidentally got pregnant!")
    
    def _handle_family_planning(self):
        """Handle couples trying to conceive"""
        from agent import LifeGoal
        
        # Create a list copy to avoid "dictionary changed size during iteration" error
        agents_list = list(self.agents.values())
        for agent in agents_list:
            if (agent.partner_id and 
                agent.partner_id in self.agents and
                agent.relationship_status.value in ['married', 'engaged']):
                
                partner = self.agents[agent.partner_id]
                
                # Check for pregnancy (heterosexual couples)
                if (agent.gender == "female" and partner.gender == "male"):
                    if agent.try_to_conceive(partner):
                        print(f"🤰 {agent.name} is pregnant!")
                
                # Check for adoption (any couple, especially same sex)
                elif agent.can_adopt(partner) and random.random() < 0.01:  # 1% chance per month
                    result = agent.adopt_child(partner, self.current_date)
                    if result:
                        child_id, child_agent = result
                        self.add_agent(child_agent)
                        print(f"👨‍👩‍👧‍👦 {agent.name} and {partner.name} adopted {child_agent.name}!")
    
    def get_location_name(self, location_id: str) -> str:
        """Get location name from ID"""
        if location_id in self.locations:
            return self.locations[location_id].name
        return "Unknown"
    
    def get_agent_status(self, agent_id: str) -> Dict:
        """Get current status of an agent"""
        if agent_id not in self.agents:
            return {}
        
        agent = self.agents[agent_id]
        return {
            "name": agent.name,
            "age": agent.age,
            "location": self.get_location_name(agent.current_location),
            "action": agent.decide_action(self.current_time),
            "happiness": agent.happiness,
            "energy": agent.energy,
            "time": f"Day {self.current_day}, {self.current_time:02d}:00"
        }
    
    def _handle_agent_death(self, agent_id: str):
        """Handle when an agent dies - move to graveyard and clean up relationships"""
        if agent_id not in self.agents:
            return
        
        deceased_agent = self.agents[agent_id]
        
        # Move to graveyard
        self.graveyard[agent_id] = deceased_agent
        
        # Remove from active agents
        del self.agents[agent_id]
        
        # Clean up relationships
        self._cleanup_deceased_relationships(deceased_agent)
        
        # Remove from all locations
        for location in self.locations.values():
            if agent_id in location.current_occupants:
                location.remove_occupant(agent_id)
    
    def _cleanup_deceased_relationships(self, deceased_agent):
        """Clean up relationships when an agent dies"""
        from agent import RelationshipStatus
        
        # Break up with partner if they have one
        if deceased_agent.partner_id and deceased_agent.partner_id in self.agents:
            partner = self.agents[deceased_agent.partner_id]
            partner.relationship_status = RelationshipStatus.SINGLE
            partner.partner_id = None
            partner.happiness = max(0, partner.happiness - 30)  # Grief reduces happiness
            print(f"💔 {partner.name} is grieving the loss of {deceased_agent.name}")
        
        # Remove from all friends' lists
        for friend_id in deceased_agent.friend_ids:
            if friend_id in self.agents:
                friend = self.agents[friend_id]
                if deceased_agent.id in friend.friend_ids:
                    friend.friend_ids.remove(deceased_agent.id)
                    friend.happiness = max(0, friend.happiness - 15)  # Grief
        
        # Handle children: they become orphans or go to other parent
        for child_id in deceased_agent.children_ids:
            if child_id in self.agents:
                child = self.agents[child_id]
                
                # Update the child's parent references
                if child.mother_id == deceased_agent.id:
                    child.mother_name = deceased_agent.name  # Store name for deceased parent
                    child.mother_id = None
                elif child.father_id == deceased_agent.id:
                    child.father_name = deceased_agent.name  # Store name for deceased parent
                    child.father_id = None
                
                # Reduce happiness due to loss of parent
                child.happiness = max(0, child.happiness - 25)
                print(f"😢 {child.name} has lost their parent {deceased_agent.name}")
    
    def get_graveyard_count(self) -> int:
        """Get total number of deceased agents"""
        return len(self.graveyard)


def create_default_city(name: str = "SimCity") -> City:
    """Create a city with default locations"""
    city = City(name)
    
    # Residential areas (houses/apartments)
    residential_names = [
        "Maple Street Apartments", "Oak Avenue Houses", "Pine District",
        "Riverside Homes", "Downtown Lofts", "Suburb Heights",
        "Garden View Apartments", "Hillside Residences"
    ]
    
    for i, name in enumerate(residential_names):
        x = (i % 4) * 12 + random.randint(0, 5)
        y = (i // 4) * 12 + random.randint(0, 5)
        city.add_location(Location(
            id=f"res_{i}",
            name=name,
            location_type=LocationType.RESIDENTIAL,
            position=(x, y),
            capacity=20
        ))
    
    # Workplaces
    workplace_names = [
        "Tech Corp HQ", "City Hospital", "Law Firm Associates",
        "Marketing Agency", "Finance Center", "Manufacturing Plant",
        "Retail Store", "City Hall", "Little Angels Daycare", "Bright Futures Childcare"
    ]
    
    for i, name in enumerate(workplace_names):
        x = 20 + (i % 3) * 10 + random.randint(0, 5)
        y = 5 + (i // 3) * 10 + random.randint(0, 5)
        city.add_location(Location(
            id=f"work_{i}",
            name=name,
            location_type=LocationType.WORKPLACE,
            position=(x, y),
            capacity=30
        ))
    
    # Schools
    schools = ["Elementary School", "High School", "Community College", "University"]
    for i, name in enumerate(schools):
        city.add_location(Location(
            id=f"school_{i}",
            name=name,
            location_type=LocationType.SCHOOL,
            position=(5 + i * 12, 35),
            capacity=100
        ))
    
    # Social venues
    social_venues = [
        ("Central Park", LocationType.PARK),
        ("City Gym", LocationType.GYM),
        ("Movie Theater", LocationType.ENTERTAINMENT),
        ("Mall", LocationType.RETAIL),
        ("Pizza Place", LocationType.RESTAURANT),
        ("Coffee Shop", LocationType.RESTAURANT),
        ("Sports Bar", LocationType.RESTAURANT),
    ]
    
    for i, (name, loc_type) in enumerate(social_venues):
        x = 30 + (i % 3) * 8 + random.randint(0, 3)
        y = 30 + (i // 3) * 8 + random.randint(0, 3)
        city.add_location(Location(
            id=f"social_{i}",
            name=name,
            location_type=loc_type,
            position=(x, y),
            capacity=50
        ))
    
    return city


# Test city creation
if __name__ == "__main__":
    city = create_default_city("TestCity")
    print(f"=== {city.name} ===")
    print(f"Locations: {len(city.locations)}")
    print(f"Grid size: {city.grid_size}x{city.grid_size}\n")
    
    print("Residential areas:")
    for loc in city.locations.values():
        if loc.location_type == LocationType.RESIDENTIAL:
            print(f"  - {loc.name} at {loc.position}")
    
    print("\nWorkplaces:")
    for loc in city.locations.values():
        if loc.location_type == LocationType.WORKPLACE:
            print(f"  - {loc.name} at {loc.position}")
