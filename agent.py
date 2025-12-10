import random
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from enum import Enum
import uuid
from datetime import datetime, date

class PersonalityTrait(Enum):
    """Big Five personality traits (OCEAN model)"""
    OPENNESS = "openness"
    CONSCIENTIOUSNESS = "conscientiousness"
    EXTRAVERSION = "extraversion"
    AGREEABLENESS = "agreeableness"
    NEUROTICISM = "neuroticism"

class LifeGoal(Enum):
    # Career and Money Goals
    CAREER_FOCUSED = "career_focused"
    WEALTH_ACCUMULATION = "wealth_accumulation"
    ENTREPRENEURIAL = "entrepreneurial"
    
    # Family and Relationship Goals
    FAMILY_ORIENTED = "family_oriented"
    WANTS_CHILDREN = "wants_children"
    NO_CHILDREN = "no_children"
    MARRIAGE_FOCUSED = "marriage_focused"
    INDEPENDENCE = "independence"
    
    # Lifestyle Goals
    SOCIAL_BUTTERFLY = "social_butterfly"
    CREATIVE_PURSUITS = "creative_pursuits"
    KNOWLEDGE_SEEKER = "knowledge_seeker"
    TRAVEL_ENTHUSIAST = "travel_enthusiast"
    FITNESS_FOCUSED = "fitness_focused"
    STABILITY_SEEKER = "stability_seeker"

class EducationLevel(Enum):
    HIGH_SCHOOL = "high_school"
    SOME_COLLEGE = "some_college"
    BACHELORS = "bachelors"
    MASTERS = "masters"
    DOCTORATE = "doctorate"

class IncomeClass(Enum):
    LOWER = "lower"  # under $30k
    LOWER_MIDDLE = "lower_middle"  # $30k to $50k
    MIDDLE = "middle"  # $50k to $100k
    UPPER_MIDDLE = "upper_middle"  # $100k to $200k
    UPPER = "upper"  # over $200k

class RelationshipStatus(Enum):
    SINGLE = "single"
    DATING = "dating"
    ENGAGED = "engaged"
    MARRIED = "married"
    DIVORCED = "divorced"
    WIDOWED = "widowed"

class PregnancyStatus(Enum):
    NOT_PREGNANT = "not_pregnant"
    PREGNANT = "pregnant"
    RECENTLY_GAVE_BIRTH = "recently_gave_birth"

class SexualOrientation(Enum):
    STRAIGHT = "straight"
    GAY = "gay"
    LESBIAN = "lesbian"
    BISEXUAL = "bisexual"

@dataclass
class Personality:
    """Personality traits scored 0-100"""
    openness: int = 50
    conscientiousness: int = 50
    extraversion: int = 50
    agreeableness: int = 50
    neuroticism: int = 50
    
    def compatibility_score(self, other: 'Personality') -> float:
        """Calculate compatibility between two personalities (0-100)"""
        # Similar extraversion helps (both social or both introverted)
        # Opposite neuroticism helps (stable plus neurotic can work)
        # Similar openness helps (shared interests)
        # High agreeableness in both helps (less conflict)
        # Similar conscientiousness helps (shared values)
        
        scores = []
        scores.append(100 - abs(self.extraversion - other.extraversion))
        scores.append(abs(self.neuroticism - other.neuroticism))  # Opposites attract
        scores.append(100 - abs(self.openness - other.openness))
        scores.append(min(self.agreeableness, other.agreeableness))
        scores.append(100 - abs(self.conscientiousness - other.conscientiousness))
        
        return sum(scores) / len(scores)

@dataclass
class Agent:
    """A simulated person in the city"""
    
    # Identity
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    age: int = 18
    birthday: date = field(default_factory=lambda: date(2000, 1, 1))  # Will be set properly in generation
    gender: str = "male"  # male, female, non binary
    
    # Personality and Goals
    personality: Personality = field(default_factory=Personality)
    life_goals: List[LifeGoal] = field(default_factory=list)
    hobbies: List[str] = field(default_factory=list)
    
    # Education and Career
    education_level: EducationLevel = EducationLevel.HIGH_SCHOOL
    job_title: Optional[str] = None
    income_class: IncomeClass = IncomeClass.LOWER
    annual_income: int = 25000
    
    # Relationships
    relationship_status: RelationshipStatus = RelationshipStatus.SINGLE
    sexual_orientation: SexualOrientation = SexualOrientation.STRAIGHT
    partner_id: Optional[str] = None
    friend_ids: List[str] = field(default_factory=list)
    children_ids: List[str] = field(default_factory=list)
    
    # Family
    mother_id: Optional[str] = None
    father_id: Optional[str] = None
    mother_name: str = ""  # For deceased parents not in simulation
    father_name: str = ""  # For deceased parents not in simulation
    
    # Pregnancy and Family
    pregnancy_status: PregnancyStatus = PregnancyStatus.NOT_PREGNANT
    pregnancy_days: int = 0  # Days into pregnancy (270 days equals 9 months equals full term)
    days_since_birth: int = 0  # Recovery period after birth
    
    # Relationship tracking
    relationship_start_date: Optional[date] = None  # When current relationship started
    days_in_relationship: int = 0  # Days with current partner
    
    # Life Stats
    happiness: int = 50  # 0 to 100
    health: int = 100  # 0 to 100
    energy: int = 100  # 0 to 100
    is_deceased: bool = False  # Death status
    date_of_death: Optional[date] = None  # When they died
    
    # Location and Schedule
    current_location: Optional[str] = None
    home_location: Optional[str] = None
    work_location: Optional[str] = None
    current_action: str = "relaxing"  # Cache current action to avoid recalculating every frame
    
    # History tracking
    relationship_history: List[Dict] = field(default_factory=list)
    job_history: List[Dict] = field(default_factory=list)
    
    def __str__(self):
        return (f"{self.name} ({self.age}y, {self.gender})\n"
                f"  Job: {self.job_title or 'Unemployed'} - ${self.annual_income:,}/yr\n"
                f"  Education: {self.education_level.value}\n"
                f"  Status: {self.relationship_status.value}\n"
                f"  Happiness: {self.happiness}/100, Health: {self.health}/100")
    
    def decide_action(self, current_time: int) -> str:
        """Decide what to do based on time of day and personality"""
        hour = current_time % 24
        
        # Sleep
        if hour < 6 or hour >= 23:
            return "sleeping"
        
        # Babies and toddlers stay home (unless with babysitter)
        if self.age < 4:
            if 6 <= hour < 22:
                return "at_home_with_care"
            else:
                return "sleeping"
        
        # Young children mostly stay home or at school
        if self.age < 13:
            if 8 <= hour < 15:  # School hours
                return "at_school"
            else:
                return "at_home"  # Home with family
        
        # Work hours (if employed)
        if self.job_title and 9 <= hour < 17:
            return "working"
        
        # School (if student and young)
        if self.age < 22 and 8 <= hour < 15:
            return "studying"
        
        # Morning routine
        if 6 <= hour < 9:
            if random.random() < 0.7:
                return "at_home"
            else:
                return "getting_coffee"
        
        # Lunch time
        if 12 <= hour < 14:
            return "having_lunch"
        
        # Evening activities based on personality
        if hour >= 17:
            if self.energy < 30:
                return "resting"
            elif self.personality.extraversion > 60 and random.random() < 0.4:
                return "socializing"
            elif random.random() < 0.3:
                return f"hobby: {random.choice(self.hobbies)}" if self.hobbies else "relaxing"
            else:
                return "relaxing"
        
        # Weekend behavior (simplified: treat as free time)
        return "relaxing"
    
    def hobby_compatibility(self, other_agent: 'Agent') -> float:
        """Calculate hobby compatibility (0-100)"""
        if not self.hobbies or not other_agent.hobbies:
            return 40  # Neutral compatibility if no hobbies
        
        shared_hobbies = set(self.hobbies) & set(other_agent.hobbies)
        total_unique_hobbies = len(set(self.hobbies) | set(other_agent.hobbies))
        
        if total_unique_hobbies == 0:
            return 50
        
        # More shared hobbies = higher compatibility, but not too penalizing
        shared_ratio = len(shared_hobbies) / total_unique_hobbies
        return min(100, 30 + (shared_ratio * 70))
    
    def goal_compatibility(self, other_agent: 'Agent') -> float:
        """Calculate life goal compatibility (0-100)"""
        my_goals = set(self.life_goals)
        their_goals = set(other_agent.life_goals)
        
        # Check for major incompatibilities
        major_conflicts = [
            (LifeGoal.WANTS_CHILDREN, LifeGoal.NO_CHILDREN),
            (LifeGoal.MARRIAGE_FOCUSED, LifeGoal.INDEPENDENCE),
            (LifeGoal.FAMILY_ORIENTED, LifeGoal.CAREER_FOCUSED),
            (LifeGoal.STABILITY_SEEKER, LifeGoal.TRAVEL_ENTHUSIAST)
        ]
        
        # Severe penalty for conflicting goals
        for goal_a, goal_b in major_conflicts:
            if (goal_a in my_goals and goal_b in their_goals) or (goal_b in my_goals and goal_a in their_goals):
                return 10  # Very low compatibility
        
        # Bonus for shared important goals
        important_shared_goals = my_goals & their_goals
        shared_bonus = len(important_shared_goals) * 15  # +15 for each shared goal
        
        # Base compatibility
        base_score = 50
        
        # Complementary goals (different but compatible)
        complementary_bonus = 0
        if LifeGoal.CAREER_FOCUSED in my_goals and LifeGoal.FAMILY_ORIENTED in their_goals:
            complementary_bonus += 10
        if LifeGoal.SOCIAL_BUTTERFLY in my_goals and LifeGoal.KNOWLEDGE_SEEKER in their_goals:
            complementary_bonus += 5
            
        return min(100, base_score + shared_bonus + complementary_bonus)
    
    def overall_compatibility(self, other_agent: 'Agent') -> float:
        """Calculate overall compatibility including personality, hobbies, and goals"""
        personality_comp = self.personality.compatibility_score(other_agent.personality)
        hobby_comp = self.hobby_compatibility(other_agent)
        goal_comp = self.goal_compatibility(other_agent)
        
        # Weight: 50% personality, 25% hobbies, 25% goals
        return (personality_comp * 0.5) + (hobby_comp * 0.25) + (goal_comp * 0.25)
    
    def is_sexually_compatible_with(self, other_agent: 'Agent') -> bool:
        """Check if two agents are sexually compatible based on orientation and gender"""
        # Check this agent's attraction to other agent
        my_attraction = False
        if self.sexual_orientation == SexualOrientation.STRAIGHT:
            my_attraction = (self.gender == "male" and other_agent.gender == "female") or \
                           (self.gender == "female" and other_agent.gender == "male")
        elif self.sexual_orientation == SexualOrientation.GAY:
            my_attraction = (self.gender == "male" and other_agent.gender == "male")
        elif self.sexual_orientation == SexualOrientation.LESBIAN:
            my_attraction = (self.gender == "female" and other_agent.gender == "female")
        elif self.sexual_orientation == SexualOrientation.BISEXUAL:
            my_attraction = True  # Attracted to all genders
        
        # Check other agent's attraction to this agent
        their_attraction = False
        if other_agent.sexual_orientation == SexualOrientation.STRAIGHT:
            their_attraction = (other_agent.gender == "male" and self.gender == "female") or \
                              (other_agent.gender == "female" and self.gender == "male")
        elif other_agent.sexual_orientation == SexualOrientation.GAY:
            their_attraction = (other_agent.gender == "male" and self.gender == "male")
        elif other_agent.sexual_orientation == SexualOrientation.LESBIAN:
            their_attraction = (other_agent.gender == "female" and self.gender == "female")
        elif other_agent.sexual_orientation == SexualOrientation.BISEXUAL:
            their_attraction = True  # Attracted to all genders
        
        return my_attraction and their_attraction

    def can_develop_relationship_with(self, other_agent: 'Agent') -> bool:
        """Check if this agent can develop a relationship with another agent"""
        # Must be single to start dating
        if self.relationship_status != RelationshipStatus.SINGLE or other_agent.relationship_status != RelationshipStatus.SINGLE:
            return False
        
        # Must be sexually compatible
        if not self.is_sexually_compatible_with(other_agent):
            return False
        
        # Age compatibility (within 15 years)
        age_diff = abs(self.age - other_agent.age)
        if age_diff > 15:
            return False
        
        # Not already family
        if other_agent.id in self.children_ids:
            return False
        
        # Must have minimum compatibility
        compatibility = self.overall_compatibility(other_agent)
        return compatibility > 30
    
    def develop_friendship(self, other_agent: 'Agent'):
        """Develop friendship with another agent"""
        if other_agent.id not in self.friend_ids:
            self.friend_ids.append(other_agent.id)
        if self.id not in other_agent.friend_ids:
            other_agent.friend_ids.append(self.id)
    
    def start_relationship(self, other_agent: 'Agent', current_date: date = None):
        """Start dating relationship with another agent"""
        if self.can_develop_relationship_with(other_agent):
            if current_date is None:
                current_date = date.today()
                
            self.relationship_status = RelationshipStatus.DATING
            self.partner_id = other_agent.id
            self.relationship_start_date = current_date
            self.days_in_relationship = 0
            
            other_agent.relationship_status = RelationshipStatus.DATING
            other_agent.partner_id = self.id
            other_agent.relationship_start_date = current_date
            other_agent.days_in_relationship = 0
            
            # Record relationship start
            self.relationship_history.append({
                'type': 'started_dating',
                'partner_id': other_agent.id,
                'partner_name': other_agent.name,
                'compatibility': self.overall_compatibility(other_agent),
                'start_date': current_date
            })
            return True
        return False
    
    def can_propose_to(self, other_agent: 'Agent') -> bool:
        """Check if this agent can propose to their dating partner"""
        if self.relationship_status != RelationshipStatus.DATING or self.partner_id != other_agent.id:
            return False
        
        # Need high compatibility and marriage focused goals for proposal
        compatibility = self.overall_compatibility(other_agent)
        wants_marriage = (LifeGoal.MARRIAGE_FOCUSED in self.life_goals or 
                         LifeGoal.FAMILY_ORIENTED in self.life_goals)
        
        return compatibility > 60 and wants_marriage
    
    def propose_to(self, other_agent: 'Agent') -> bool:
        """Propose marriage to partner"""
        if not self.can_propose_to(other_agent):
            return False
        
        # Calculate acceptance chance based on compatibility and goals
        compatibility = self.overall_compatibility(other_agent)
        goal_compatibility = self.goal_compatibility(other_agent)
        
        # Partner more likely to say yes if they also want marriage
        partner_wants_marriage = (LifeGoal.MARRIAGE_FOCUSED in other_agent.life_goals or 
                                 LifeGoal.FAMILY_ORIENTED in other_agent.life_goals)
        
        base_chance = 0.3  # 30% base chance
        compatibility_bonus = (compatibility - 60) / 100  # +0% to +40% based on compatibility
        goal_bonus = 0.3 if partner_wants_marriage else 0  # +30% if they want marriage
        goal_compatibility_bonus = (goal_compatibility - 50) / 200  # +0% to +25% based on goal compatibility
        
        acceptance_chance = min(0.95, base_chance + compatibility_bonus + goal_bonus + goal_compatibility_bonus)
        
        if random.random() < acceptance_chance:
            # Engagement!
            self.relationship_status = RelationshipStatus.ENGAGED
            other_agent.relationship_status = RelationshipStatus.ENGAGED
            
            # Record engagement
            self.relationship_history.append({
                'type': 'engaged',
                'partner_id': other_agent.id,
                'partner_name': other_agent.name,
                'compatibility': compatibility
            })
            
            # Happiness boost
            self.happiness = min(100, self.happiness + 10)
            other_agent.happiness = min(100, other_agent.happiness + 10)
            
            return True
        else:
            # Proposal rejected: relationship stress
            self.happiness = max(0, self.happiness - 10)
            other_agent.happiness = max(0, other_agent.happiness - 5)
            return False
    
    def get_married(self, other_agent: 'Agent'):
        """Progress from engagement to marriage"""
        if self.relationship_status != RelationshipStatus.ENGAGED or self.partner_id != other_agent.id:
            return False
            
        # Handle name change: woman takes man's last name
        if self.gender == "female" and other_agent.gender == "male":
            # Woman takes husband's last name
            husband_last_name = other_agent.name.split()[-1]
            wife_first_name = self.name.split()[0]
            old_name = self.name
            self.name = f"{wife_first_name} {husband_last_name}"
            print(f"💒 {old_name} is now {self.name}")
            
        elif self.gender == "male" and other_agent.gender == "female":
            # Woman takes husband's last name
            husband_last_name = self.name.split()[-1]
            wife_first_name = other_agent.name.split()[0]
            old_name = other_agent.name
            other_agent.name = f"{wife_first_name} {husband_last_name}"
            print(f"💒 {old_name} is now {other_agent.name}")
            
        self.relationship_status = RelationshipStatus.MARRIED
        other_agent.relationship_status = RelationshipStatus.MARRIED
        
        # Record marriage
        self.relationship_history.append({
            'type': 'married',
            'partner_id': other_agent.id,
            'partner_name': other_agent.name
        })
        
        # Happiness boost from wedding
        self.happiness = min(100, self.happiness + 15)
        other_agent.happiness = min(100, other_agent.happiness + 15)
        
        return True
    
    def should_breakup(self, other_agent: 'Agent') -> bool:
        """Determine if relationship should end based on compatibility"""
        if not self.partner_id or self.partner_id != other_agent.id:
            return False
        
        compatibility = self.overall_compatibility(other_agent)
        
        # Different breakup thresholds for different relationship stages
        if self.relationship_status == RelationshipStatus.DATING:
            return compatibility < 25  # Break up if very incompatible
        elif self.relationship_status == RelationshipStatus.MARRIED:
            return compatibility < 20  # Marriage is more stable, lower threshold
        
        return False
    
    def breakup(self, other_agent: 'Agent'):
        """End relationship with partner"""
        if self.partner_id == other_agent.id:
            # Record breakup
            self.relationship_history.append({
                'type': 'broke_up' if self.relationship_status == RelationshipStatus.DATING else 'divorced',
                'partner_id': other_agent.id,
                'partner_name': other_agent.name,
                'final_compatibility': self.overall_compatibility(other_agent)
            })
            
            # Update status
            self.relationship_status = RelationshipStatus.SINGLE if self.relationship_status == RelationshipStatus.DATING else RelationshipStatus.DIVORCED
            other_agent.relationship_status = RelationshipStatus.SINGLE if other_agent.relationship_status == RelationshipStatus.DATING else RelationshipStatus.DIVORCED
            
            # Clear partner references
            self.partner_id = None
            other_agent.partner_id = None
            
            # Reset relationship tracking
            self.relationship_start_date = None
            self.days_in_relationship = 0
            other_agent.relationship_start_date = None
            other_agent.days_in_relationship = 0
            
            # Happiness hit from breakup
            self.happiness = max(0, self.happiness - 15)
            other_agent.happiness = max(0, other_agent.happiness - 15)
            
            return True
        return False
    
    def update_relationship_duration(self, days_passed: int = 1):
        """Update how long agent has been in current relationship"""
        if self.partner_id and self.relationship_start_date:
            self.days_in_relationship += days_passed
    
    def celebrate_birthday(self, current_date: date):
        """Age the agent if it's their birthday"""
        if (current_date.month == self.birthday.month and 
            current_date.day == self.birthday.day):
            self.age += 1
            return True
        return False
    
    def can_get_pregnant(self, partner_agent: 'Agent') -> bool:
        """Check if this agent can get pregnant"""
        # Must be female, not already pregnant, and have a male partner
        if (self.gender != "female" or 
            self.pregnancy_status != PregnancyStatus.NOT_PREGNANT or
            not partner_agent or 
            partner_agent.gender != "male"):
            return False
        
        # Age factor (harder to get pregnant when older)
        if self.age < 16 or self.age > 45:
            return False
            
        # Recovery period after previous birth (180 days = ~6 months)
        if self.days_since_birth > 0 and self.days_since_birth < 180:
            return False
            
        return True
    
    def try_to_conceive(self, partner_agent: 'Agent', is_planned: bool = True) -> bool:
        """Attempt to get pregnant (planned or unplanned)"""
        if not self.can_get_pregnant(partner_agent):
            return False
        
        # For planned pregnancies, both partners must want children AND be in a relationship for 1+ year
        if is_planned:
            # Must be in any romantic relationship for planned pregnancy
            if self.relationship_status not in [RelationshipStatus.DATING, RelationshipStatus.ENGAGED, RelationshipStatus.MARRIED]:
                return False
            
            # Must have been together for at least 6 months (180 days) for planned pregnancy
            if self.days_in_relationship < 180:
                return False
                
            wants_children = LifeGoal.WANTS_CHILDREN in self.life_goals or LifeGoal.FAMILY_ORIENTED in self.life_goals
            partner_wants_children = LifeGoal.WANTS_CHILDREN in partner_agent.life_goals or LifeGoal.FAMILY_ORIENTED in partner_agent.life_goals
            
            if not (wants_children and partner_wants_children):
                return False
        
        # Age based fertility (peak fertility in 20s to early 30s): MUCH higher daily rates
        if self.age <= 25:
            base_chance = 0.15 if is_planned else 0.03  # 15% planned, 3% unplanned
        elif self.age <= 30:
            base_chance = 0.12 if is_planned else 0.025  # 12% planned, 2.5% unplanned  
        elif self.age <= 35:
            base_chance = 0.08 if is_planned else 0.02  # 8% planned, 2% unplanned
        elif self.age <= 40:
            base_chance = 0.05 if is_planned else 0.01  # 5% planned, 1% unplanned
        else:
            base_chance = 0.02 if is_planned else 0.005  # 2% planned, 0.5% unplanned
        
        # For unplanned pregnancies, personality affects chance
        if not is_planned:
            # Lower conscientiousness equals higher chance of unplanned pregnancy
            # Higher neuroticism equals higher chance (impulsive decisions)
            impulsiveness_factor = (100 - self.personality.conscientiousness) / 100  # 0 to 1
            neuroticism_factor = self.personality.neuroticism / 100  # 0 to 1
            personality_multiplier = 0.5 + (impulsiveness_factor * 0.5) + (neuroticism_factor * 0.3)  # 0.5 to 1.3
            base_chance *= personality_multiplier
        
        # Happiness and health factors
        health_factor = self.health / 100
        happiness_factor = min(1.0, self.happiness / 80) if is_planned else 1.0  # Happiness doesn't affect accidents
        
        conception_chance = base_chance * health_factor * happiness_factor
        
        if random.random() < conception_chance:
            self.pregnancy_status = PregnancyStatus.PREGNANT
            self.pregnancy_days = 0
            return True
        
        return False
    
    def progress_pregnancy(self, days_passed: int = 1):
        """Progress pregnancy by specified days"""
        if self.pregnancy_status != PregnancyStatus.PREGNANT:
            return False
        
        self.pregnancy_days += days_passed
        
        # Full term pregnancy is 270 days (9 months)
        if self.pregnancy_days >= 270:
            return self.give_birth()
        
        return False
    
    def give_birth(self) -> Optional[str]:
        """Give birth to a child"""
        if self.pregnancy_status != PregnancyStatus.PREGNANT:
            return None
        
        # Create child agent
        child_id = str(uuid.uuid4())[:8]
        
        # Reset pregnancy status
        self.pregnancy_status = PregnancyStatus.RECENTLY_GAVE_BIRTH
        self.pregnancy_days = 0
        self.days_since_birth = 0
        
        # Add child to parent's children list
        self.children_ids.append(child_id)
        
        # Happiness boost from childbirth
        self.happiness = min(100, self.happiness + 20)
        
        # Health impact from childbirth
        self.health = max(50, self.health - 10)
        
        return child_id
    
    def try_accidental_pregnancy(self, male_agent: 'Agent') -> bool:
        """Attempt accidental pregnancy during any interaction between male/female"""
        # Must be female interacting with male
        if self.gender != "female" or male_agent.gender != "male":
            return False
            
        # Both must be adults but not necessarily in a relationship
        if self.age < 16 or male_agent.age < 16:
            return False
            
        # Much higher chance of accidental pregnancy per interaction 
        # Higher chance if they know each other (friends or dating)
        base_chance = 0.001  # 0.1% base chance per interaction
        
        # Increase chance if they're friends or dating
        if (male_agent.id in self.friend_ids or 
            self.relationship_status == RelationshipStatus.DATING and self.partner_id == male_agent.id):
            base_chance *= 10  # 10x higher if they know each other (1.0%)
        
        # Use regular conception mechanics
        if random.random() < base_chance:
            return self.try_to_conceive(male_agent, is_planned=False)
            
        return False
    
    def can_adopt(self, partner_agent: 'Agent') -> bool:
        """Check if this couple can adopt a child"""
        # Must be in a committed relationship (engaged or married)
        if (self.relationship_status not in [RelationshipStatus.ENGAGED, RelationshipStatus.MARRIED] or
            not partner_agent or self.partner_id != partner_agent.id):
            return False
        
        # Must have been together for at least 2 years for adoption
        if self.days_in_relationship < 730:  # 2 years
            return False
        
        # At least one partner must want children
        wants_children = (LifeGoal.WANTS_CHILDREN in self.life_goals or 
                         LifeGoal.FAMILY_ORIENTED in self.life_goals or
                         LifeGoal.WANTS_CHILDREN in partner_agent.life_goals or 
                         LifeGoal.FAMILY_ORIENTED in partner_agent.life_goals)
        
        if not wants_children:
            return False
        
        # Age requirements (at least 21, under 60)
        if self.age < 21 or partner_agent.age < 21 or self.age > 60 or partner_agent.age > 60:
            return False
        
        return True
    
    def adopt_child(self, partner_agent: 'Agent', current_date: date) -> Optional[str]:
        """Adopt a child together"""
        if not self.can_adopt(partner_agent):
            return None
        
        # Create adopted child
        child_id = str(uuid.uuid4())[:8]
        
        # Create child using adoption logic
        child_agent = create_adopted_child(self, partner_agent, child_id, current_date)
        
        # Add child to both partners
        self.children_ids.append(child_id)
        partner_agent.children_ids.append(child_id)
        
        # Happiness boost from adoption
        self.happiness = min(100, self.happiness + 25)
        partner_agent.happiness = min(100, partner_agent.happiness + 25)
        
        return child_id, child_agent
    
    def update_postpartum(self, days_passed: int = 1):
        """Update postpartum recovery status"""
        if self.pregnancy_status == PregnancyStatus.RECENTLY_GAVE_BIRTH:
            self.days_since_birth += days_passed
            
            # Recovery period lasts 180 days (6 months)
            if self.days_since_birth >= 180:
                self.pregnancy_status = PregnancyStatus.NOT_PREGNANT
                self.days_since_birth = 0
    
    def calculate_death_probability(self) -> float:
        """Calculate the daily probability of death based on age and health"""
        # Base mortality rates by age (daily probability)
        if self.age < 1:
            base_rate = 0.00001  # Very low for babies
        elif self.age < 18:
            base_rate = 0.000005  # Very low for children
        elif self.age < 30:
            base_rate = 0.00001  # Low for young adults
        elif self.age < 50:
            base_rate = 0.00003  # Slightly higher for middle age
        elif self.age < 65:
            base_rate = 0.0001   # Higher for older adults
        elif self.age < 75:
            base_rate = 0.0005   # Much higher for seniors
        elif self.age < 85:
            base_rate = 0.002    # High for elderly
        else:
            base_rate = 0.01     # Very high for very elderly (85+)
        
        # Health factor (poor health = higher death rate)
        health_factor = (100 - self.health) / 100.0  # 0.0 (perfect health) to 1.0 (very poor health)
        health_multiplier = 1 + (health_factor * 2)   # 1.0x to 3.0x multiplier
        
        return min(0.05, base_rate * health_multiplier)  # Cap at 5% daily probability
    
    def check_for_death(self, current_date: date) -> bool:
        """Check if agent dies today, returns True if they die"""
        if self.is_deceased:
            return False  # Already dead
            
        death_probability = self.calculate_death_probability()
        
        if random.random() < death_probability:
            self.die(current_date)
            return True
        return False
    
    def die(self, current_date: date):
        """Handle agent death"""
        self.is_deceased = True
        self.date_of_death = current_date
        self.current_location = None
        self.current_action = "deceased"
        
        # Set health to 0 when they die
        self.health = 0


def get_job_for_workplace(workplace_name: str, education_level: EducationLevel) -> str:
    """Get appropriate job title based on workplace and education"""
    workplace_lower = workplace_name.lower()
    
    # Define job mappings based on workplace type and education
    job_mappings = {
        "tech corp": {
            EducationLevel.HIGH_SCHOOL: ["IT Support", "Junior Developer", "Technical Assistant"],
            EducationLevel.SOME_COLLEGE: ["Junior Developer", "QA Tester", "Systems Administrator"],
            EducationLevel.BACHELORS: ["Software Engineer", "Product Manager", "Data Analyst"],
            EducationLevel.MASTERS: ["Senior Engineer", "Engineering Manager", "Principal Developer"],
            EducationLevel.DOCTORATE: ["Research Scientist", "Chief Technology Officer", "Technical Director"]
        },
        "hospital": {
            EducationLevel.HIGH_SCHOOL: ["Medical Assistant", "Hospital Clerk", "Security Guard"],
            EducationLevel.SOME_COLLEGE: ["Nurse Assistant", "Medical Technician", "Administrative Coordinator"],
            EducationLevel.BACHELORS: ["Registered Nurse", "Physical Therapist", "Lab Technician"],
            EducationLevel.MASTERS: ["Nurse Practitioner", "Hospital Administrator", "Clinical Manager"],
            EducationLevel.DOCTORATE: ["Doctor", "Surgeon", "Medical Director"]
        },
        "law firm": {
            EducationLevel.HIGH_SCHOOL: ["Legal Secretary", "File Clerk", "Receptionist"],
            EducationLevel.SOME_COLLEGE: ["Paralegal", "Legal Assistant", "Court Reporter"],
            EducationLevel.BACHELORS: ["Junior Associate", "Legal Analyst", "Case Manager"],
            EducationLevel.MASTERS: ["Attorney", "Legal Counsel", "Senior Associate"],
            EducationLevel.DOCTORATE: ["Senior Partner", "Managing Partner", "Legal Director"]
        },
        "marketing": {
            EducationLevel.HIGH_SCHOOL: ["Marketing Assistant", "Social Media Coordinator", "Administrative Assistant"],
            EducationLevel.SOME_COLLEGE: ["Marketing Specialist", "Content Creator", "Campaign Coordinator"],
            EducationLevel.BACHELORS: ["Marketing Manager", "Brand Specialist", "Digital Marketing Manager"],
            EducationLevel.MASTERS: ["Marketing Director", "Brand Manager", "Strategic Marketing Lead"],
            EducationLevel.DOCTORATE: ["Chief Marketing Officer", "VP of Marketing", "Marketing Research Director"]
        },
        "finance": {
            EducationLevel.HIGH_SCHOOL: ["Bank Teller", "Administrative Assistant", "Data Entry Clerk"],
            EducationLevel.SOME_COLLEGE: ["Financial Assistant", "Loan Officer", "Accounting Clerk"],
            EducationLevel.BACHELORS: ["Financial Analyst", "Investment Advisor", "Account Manager"],
            EducationLevel.MASTERS: ["Financial Manager", "Portfolio Manager", "Senior Analyst"],
            EducationLevel.DOCTORATE: ["Chief Financial Officer", "Investment Director", "Risk Management Director"]
        },
        "manufacturing": {
            EducationLevel.HIGH_SCHOOL: ["Assembly Worker", "Machine Operator", "Quality Control"],
            EducationLevel.SOME_COLLEGE: ["Supervisor", "Quality Assurance", "Production Coordinator"],
            EducationLevel.BACHELORS: ["Production Manager", "Industrial Engineer", "Operations Manager"],
            EducationLevel.MASTERS: ["Plant Manager", "Manufacturing Director", "Operations Director"],
            EducationLevel.DOCTORATE: ["VP of Operations", "Chief Operations Officer", "Manufacturing Executive"]
        },
        "retail": {
            EducationLevel.HIGH_SCHOOL: ["Sales Associate", "Cashier", "Stock Clerk"],
            EducationLevel.SOME_COLLEGE: ["Shift Supervisor", "Customer Service Manager", "Sales Lead"],
            EducationLevel.BACHELORS: ["Store Manager", "District Manager", "Buyer"],
            EducationLevel.MASTERS: ["Regional Manager", "Operations Manager", "Retail Director"],
            EducationLevel.DOCTORATE: ["VP of Retail", "Chief Retail Officer", "Executive Director"]
        },
        "city hall": {
            EducationLevel.HIGH_SCHOOL: ["Administrative Clerk", "Receptionist", "File Clerk"],
            EducationLevel.SOME_COLLEGE: ["Administrative Assistant", "Permit Specialist", "Public Services Clerk"],
            EducationLevel.BACHELORS: ["Program Coordinator", "Policy Analyst", "Department Manager"],
            EducationLevel.MASTERS: ["Director", "Department Head", "City Manager"],
            EducationLevel.DOCTORATE: ["City Administrator", "Chief of Staff", "Executive Director"]
        },
        "daycare": {
            EducationLevel.HIGH_SCHOOL: ["Childcare Assistant", "Playground Monitor", "Kitchen Helper"],
            EducationLevel.SOME_COLLEGE: ["Childcare Worker", "Preschool Assistant", "Activity Coordinator"],
            EducationLevel.BACHELORS: ["Early Childhood Teacher", "Childcare Supervisor", "Program Director"],
            EducationLevel.MASTERS: ["Childcare Director", "Child Development Specialist", "Educational Coordinator"],
            EducationLevel.DOCTORATE: ["Child Psychology Expert", "Early Childhood Development Director", "Pediatric Consultant"]
        },
        "childcare": {
            EducationLevel.HIGH_SCHOOL: ["Nanny", "Babysitter", "Childcare Assistant"],
            EducationLevel.SOME_COLLEGE: ["Professional Nanny", "Childcare Provider", "Family Assistant"],
            EducationLevel.BACHELORS: ["Certified Childcare Professional", "Family Care Coordinator", "Child Development Specialist"],
            EducationLevel.MASTERS: ["Senior Childcare Director", "Family Support Specialist", "Child Welfare Coordinator"],
            EducationLevel.DOCTORATE: ["Child Development Expert", "Family Therapy Specialist", "Pediatric Care Consultant"]
        }
    }
    
    # Find matching workplace type
    for workplace_key in job_mappings:
        if workplace_key in workplace_lower:
            jobs = job_mappings[workplace_key].get(education_level, ["General Employee"])
            return random.choice(jobs)
    
    # Default jobs if no specific workplace match  
    default_jobs = {
        EducationLevel.HIGH_SCHOOL: ["Sales Associate", "Administrative Assistant", "Customer Service Rep", "Babysitter", "Nanny"],
        EducationLevel.SOME_COLLEGE: ["Coordinator", "Specialist", "Assistant Manager", "Childcare Worker", "Preschool Assistant"],
        EducationLevel.BACHELORS: ["Manager", "Analyst", "Professional", "Childcare Director", "Early Childhood Teacher"],
        EducationLevel.MASTERS: ["Senior Manager", "Director", "Consultant", "Child Development Specialist"],
        EducationLevel.DOCTORATE: ["Executive", "Senior Director", "Principal Consultant", "Child Psychology Expert"]
    }
    
    return random.choice(default_jobs[education_level])


def create_child_agent(parent1: 'Agent', parent2: 'Agent', child_id: str, current_date: date) -> 'Agent':
    """Create a child agent from two parents"""
    # Determine child's gender
    gender = random.choice(["male", "female"])
    
    # Generate name based on gender
    first_names_male = ["James", "John", "Michael", "William", "David", "Richard", "Joseph", "Daniel"]
    first_names_female = ["Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", "Jessica"]
    
    first_name = random.choice(first_names_male if gender == "male" else first_names_female)
    
    # Child takes one parent's last name (random choice)
    parent_for_surname = random.choice([parent1, parent2])
    last_name = parent_for_surname.name.split()[-1]
    name = f"{first_name} {last_name}"
    
    # Child is born today
    birthday = current_date
    
    # Inherit some personality traits from parents (with random variation)
    parent1_personality = parent1.personality
    parent2_personality = parent2.personality
    
    personality = Personality(
        openness=max(0, min(100, int((parent1_personality.openness + parent2_personality.openness) / 2 + random.randint(-20, 20)))),
        conscientiousness=max(0, min(100, int((parent1_personality.conscientiousness + parent2_personality.conscientiousness) / 2 + random.randint(-20, 20)))),
        extraversion=max(0, min(100, int((parent1_personality.extraversion + parent2_personality.extraversion) / 2 + random.randint(-20, 20)))),
        agreeableness=max(0, min(100, int((parent1_personality.agreeableness + parent2_personality.agreeableness) / 2 + random.randint(-20, 20)))),
        neuroticism=max(0, min(100, int((parent1_personality.neuroticism + parent2_personality.neuroticism) / 2 + random.randint(-20, 20))))
    )
    
    # Children start with basic goals, will develop more as they age
    life_goals = [LifeGoal.KNOWLEDGE_SEEKER]  # All children start curious
    
    # Basic hobbies appropriate for children
    child_hobbies = ["reading", "art", "music", "sports"]
    hobbies = random.sample(child_hobbies, 2)
    
    # Sexual orientation will be determined when they reach adolescence
    orientation = SexualOrientation.STRAIGHT  # Placeholder, will change later
    
    # Set up parent relationships
    mother_id = parent1.id if parent1.gender == "female" else parent2.id
    father_id = parent1.id if parent1.gender == "male" else parent2.id
    
    return Agent(
        id=child_id,
        name=name,
        age=0,
        birthday=birthday,
        gender=gender,
        personality=personality,
        life_goals=life_goals,
        hobbies=hobbies,
        education_level=EducationLevel.HIGH_SCHOOL,  # Will update as they grow
        job_title=None,
        income_class=IncomeClass.LOWER,
        annual_income=0,
        relationship_status=RelationshipStatus.SINGLE,
        sexual_orientation=orientation,
        mother_id=mother_id,
        father_id=father_id,
        happiness=random.randint(70, 90),  # Children generally happier
        health=random.randint(90, 100),    # Children generally healthier
        energy=random.randint(80, 100)
    )


def create_adopted_child(parent1: 'Agent', parent2: 'Agent', child_id: str, current_date: date) -> 'Agent':
    """Create an adopted child agent for a couple"""
    # Determine child's gender
    gender = random.choice(["male", "female"])
    
    # Generate name based on gender
    first_names_male = ["James", "John", "Michael", "William", "David", "Richard", "Joseph", "Daniel", "Luke", "Noah"]
    first_names_female = ["Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", "Jessica", "Emma", "Grace"]
    
    first_name = random.choice(first_names_male if gender == "male" else first_names_female)
    
    # Child takes one parent's last name (random choice)
    parent_for_surname = random.choice([parent1, parent2])
    last_name = parent_for_surname.name.split()[-1]
    name = f"{first_name} {last_name}"
    
    # Adopted children can be various ages (0 to 10 years old)
    child_age = random.randint(0, 10)
    birth_year = current_date.year - child_age
    birthday = date(birth_year, random.randint(1, 12), random.randint(1, 28))
    
    # Random personality (not inherited since adopted)
    personality = Personality(
        openness=random.randint(20, 80),
        conscientiousness=random.randint(20, 80),
        extraversion=random.randint(20, 80),
        agreeableness=random.randint(40, 90),  # Generally well adjusted
        neuroticism=random.randint(10, 60)  # Less neurotic on average
    )
    
    # Children start with basic goals
    life_goals = [LifeGoal.KNOWLEDGE_SEEKER]
    
    # Age appropriate hobbies
    if child_age < 5:
        child_hobbies = ["art", "music", "reading"]
    else:
        child_hobbies = ["reading", "art", "music", "sports", "gaming"]
    hobbies = random.sample(child_hobbies, random.randint(1, 3))
    
    # Sexual orientation placeholder
    orientation = SexualOrientation.STRAIGHT
    
    # Adoptive parents become the child's family
    mother_id = parent1.id if parent1.gender == "female" else parent2.id
    father_id = parent1.id if parent1.gender == "male" else parent2.id
    
    # Handle same sex couples
    if parent1.gender == parent2.gender:
        # For same sex couples, assign one as "mother" and one as "father" for tracking
        if parent1.gender == "female":
            mother_id = parent1.id
            father_id = parent2.id  # Second parent takes father role for tracking
        else:
            father_id = parent1.id
            mother_id = parent2.id  # Second parent takes mother role for tracking
    
    return Agent(
        id=child_id,
        name=name,
        age=child_age,
        birthday=birthday,
        gender=gender,
        personality=personality,
        life_goals=life_goals,
        hobbies=hobbies,
        education_level=EducationLevel.HIGH_SCHOOL,
        job_title=None,
        income_class=IncomeClass.LOWER,
        annual_income=0,
        relationship_status=RelationshipStatus.SINGLE,
        sexual_orientation=orientation,
        mother_id=mother_id,
        father_id=father_id,
        happiness=random.randint(60, 85),  # Adopted children may have some adjustment issues
        health=random.randint(85, 100),
        energy=random.randint(70, 100)
    )


def generate_random_agent(age_range=(18, 65), city=None) -> Agent:
    """Generate an agent with realistic statistics"""
    
    first_names_male = ["James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph"]
    first_names_female = ["Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", "Jessica"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
    
    gender = random.choice(["male", "female"])
    first_name = random.choice(first_names_male if gender == "male" else first_names_female)
    last_name = random.choice(last_names)
    name = f"{first_name} {last_name}"
    
    age = random.randint(*age_range)
    
    # Generate birthday (assume current year is 2024)
    current_year = 2024
    birth_year = current_year - age
    birthday = date(birth_year, random.randint(1, 12), random.randint(1, 28))  # Use day 1 to 28 to avoid month issues
    
    # Education distribution (US stats)
    edu_roll = random.random()
    if edu_roll < 0.12:
        education = EducationLevel.HIGH_SCHOOL
    elif edu_roll < 0.30:
        education = EducationLevel.SOME_COLLEGE
    elif edu_roll < 0.65:
        education = EducationLevel.BACHELORS
    elif edu_roll < 0.90:
        education = EducationLevel.MASTERS
    else:
        education = EducationLevel.DOCTORATE
    
    # Income based on education
    income_ranges = {
        EducationLevel.HIGH_SCHOOL: (20000, 40000),
        EducationLevel.SOME_COLLEGE: (25000, 50000),
        EducationLevel.BACHELORS: (40000, 90000),
        EducationLevel.MASTERS: (60000, 130000),
        EducationLevel.DOCTORATE: (80000, 180000)
    }
    
    income = random.randint(*income_ranges[education])
    
    # Income class
    if income < 30000:
        income_class = IncomeClass.LOWER
    elif income < 50000:
        income_class = IncomeClass.LOWER_MIDDLE
    elif income < 100000:
        income_class = IncomeClass.MIDDLE
    elif income < 200000:
        income_class = IncomeClass.UPPER_MIDDLE
    else:
        income_class = IncomeClass.UPPER
    
    # Personality (normal distribution around 50)
    personality = Personality(
        openness=max(0, min(100, int(random.gauss(50, 20)))),
        conscientiousness=max(0, min(100, int(random.gauss(50, 20)))),
        extraversion=max(0, min(100, int(random.gauss(50, 20)))),
        agreeableness=max(0, min(100, int(random.gauss(50, 20)))),
        neuroticism=max(0, min(100, int(random.gauss(50, 20))))
    )
    
    # Life goals (pick 2 to 4 based on age and personality)
    available_goals = list(LifeGoal)
    life_goals = []
    
    # Age based goal tendencies
    if age < 25:
        # Young people more likely to have career and education goals
        if random.random() < 0.6:
            life_goals.append(LifeGoal.CAREER_FOCUSED)
        if random.random() < 0.3:
            life_goals.append(LifeGoal.TRAVEL_ENTHUSIAST)
    elif age < 35:
        # Mid age more family and relationship focused
        if random.random() < 0.4:
            life_goals.append(LifeGoal.WANTS_CHILDREN if random.random() < 0.7 else LifeGoal.NO_CHILDREN)
        if random.random() < 0.5:
            life_goals.append(LifeGoal.MARRIAGE_FOCUSED)
        if random.random() < 0.4:
            life_goals.append(LifeGoal.WEALTH_ACCUMULATION)
    else:
        # Older people more stability and family focused
        if random.random() < 0.6:
            life_goals.append(LifeGoal.STABILITY_SEEKER)
        if random.random() < 0.3:
            life_goals.append(LifeGoal.FAMILY_ORIENTED)
    
    # Add random additional goals
    remaining_goals = [g for g in available_goals if g not in life_goals]
    additional_goals = random.randint(1, 3)
    life_goals.extend(random.sample(remaining_goals, min(additional_goals, len(remaining_goals))))
    
    # Hobbies based on personality
    all_hobbies = ["reading", "gaming", "sports", "cooking", "music", "art", "hiking", "photography", "gardening"]
    num_hobbies = random.randint(2, 5)
    hobbies = random.sample(all_hobbies, num_hobbies)
    
    # All agents start single: relationships develop through simulation
    status = RelationshipStatus.SINGLE
    
    # Generate deceased parent names
    father_first_names = ["Robert", "James", "John", "Michael", "William", "David", "Richard", "Joseph"]
    mother_first_names = ["Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", "Jessica"]
    
    # Use same last name as agent for father, random maiden name for mother
    agent_last_name = last_name
    mother_maiden_names = ["Miller", "Wilson", "Moore", "Taylor", "Anderson", "Thomas", "Jackson", "White"]
    
    father_name = f"{random.choice(father_first_names)} {agent_last_name}"
    mother_maiden = random.choice(mother_maiden_names)
    mother_name = f"{random.choice(mother_first_names)} {mother_maiden} {agent_last_name}"
    
    # Assign sexual orientation (realistic distribution)
    orientation_roll = random.random()
    if orientation_roll < 0.80:  # ~80% straight
        orientation = SexualOrientation.STRAIGHT
    elif orientation_roll < 0.90:  # ~10% gay/lesbian
        if gender == "male":
            orientation = SexualOrientation.GAY
        else:
            orientation = SexualOrientation.LESBIAN
    else:  # ~10% bisexual
        orientation = SexualOrientation.BISEXUAL
    
    return Agent(
        name=name,
        age=age,
        birthday=birthday,
        gender=gender,
        personality=personality,
        life_goals=life_goals,
        hobbies=hobbies,
        education_level=education,
        job_title=None,  # Will be assigned when workplace is assigned
        income_class=income_class,
        annual_income=income,
        relationship_status=status,
        sexual_orientation=orientation,
        mother_name=mother_name,
        father_name=father_name,
        happiness=random.randint(40, 80),
        health=random.randint(70, 100),
        energy=random.randint(50, 100)
    )


# Test the agent generation
if __name__ == "__main__":
    print("=== Generating Random Agents ===\n")
    for i in range(3):
        agent = generate_random_agent()
        print(agent)
        print(f"  Personality: O={agent.personality.openness}, C={agent.personality.conscientiousness}, "
              f"E={agent.personality.extraversion}, A={agent.personality.agreeableness}, N={agent.personality.neuroticism}")
        print(f"  Goals: {[g.value for g in agent.life_goals]}")
        print(f"  Hobbies: {agent.hobbies}")
        print()
