# 🎯 Relationship System - Implementation Roadmap

This guide will walk you through adding a complete relationship system to your city sim, enabling agents to meet, date, marry, have children, and potentially break up.

## Phase 1: Meeting & Attraction (2-3 hours)

### Step 1: Add Meeting Detection
Agents should notice each other when in the same location.

**In `agent.py`, add to Agent class:**
```python
# Add to dataclass fields
met_agents: Set[str] = field(default_factory=set)  # IDs of agents this person has met
relationship_scores: Dict[str, float] = field(default_factory=dict)  # agent_id -> score (0-100)

def meet_agent(self, other_agent: 'Agent'):
    """First meeting with another agent"""
    if other_agent.id not in self.met_agents:
        self.met_agents.add(other_agent.id)
        
        # Calculate initial attraction based on compatibility
        compatibility = self.personality.compatibility_score(other_agent.personality)
        
        # Modifiers
        if self.relationship_status != RelationshipStatus.SINGLE:
            compatibility *= 0.3  # Less interested if taken
        
        if abs(self.age - other_agent.age) > 15:
            compatibility *= 0.7  # Age gap penalty
        
        # Similar life goals boost
        shared_goals = set(self.life_goals) & set(other_agent.life_goals)
        if shared_goals:
            compatibility += 10 * len(shared_goals)
        
        self.relationship_scores[other_agent.id] = min(100, compatibility)
```

**In `city.py`, add to City class:**
```python
def process_social_interactions(self):
    """Check for agents at same location and process meetings"""
    for location in self.locations.values():
        if len(location.current_occupants) < 2:
            continue
        
        # Get agents at this location
        agents_here = [self.agents[aid] for aid in location.current_occupants 
                      if aid in self.agents]
        
        # Each agent can meet others here
        for i, agent1 in enumerate(agents_here):
            for agent2 in agents_here[i+1:]:
                # Meet if haven't met before
                if agent2.id not in agent1.met_agents:
                    agent1.meet_agent(agent2)
                    agent2.meet_agent(agent1)
```

**Call this in `simulate_hour()`:**
```python
def simulate_hour(self):
    self.current_time = (self.current_time + 1) % 24
    if self.current_time == 0:
        self.current_day += 1
    
    for agent in self.agents.values():
        self._update_agent_location(agent)
    
    # NEW: Process social interactions
    self.process_social_interactions()
```

### Step 2: Test It
Run the simulation and add a print statement to verify meetings:
```python
# In meet_agent() method
print(f"{self.name} met {other_agent.name}! Attraction: {compatibility:.1f}")
```

---

## Phase 2: Dating System (3-4 hours)

### Step 1: Add Dating Logic

**In `agent.py`, add new method:**
```python
def consider_dating(self, other_agent: 'Agent') -> bool:
    """Decide whether to ask someone out"""
    # Must be single
    if self.relationship_status != RelationshipStatus.SINGLE:
        return False
    if other_agent.relationship_status != RelationshipStatus.SINGLE:
        return False
    
    # Must have met and have good score
    if other_agent.id not in self.relationship_scores:
        return False
    
    score = self.relationship_scores[other_agent.id]
    
    # Threshold based on personality
    threshold = 70 - self.personality.extraversion * 0.2  # Extraverts less picky
    
    # Random element
    if score > threshold and random.random() < 0.1:  # 10% chance per interaction
        return True
    
    return False

def start_dating(self, other_agent: 'Agent'):
    """Start a relationship with another agent"""
    self.relationship_status = RelationshipStatus.DATING
    self.partner_id = other_agent.id
    
    other_agent.relationship_status = RelationshipStatus.DATING
    other_agent.partner_id = self.id
    
    # Happiness boost
    self.happiness = min(100, self.happiness + 10)
    other_agent.happiness = min(100, other_agent.happiness + 10)
    
    # Record in history
    self.relationship_history.append({
        'partner_id': other_agent.id,
        'started': self.current_day if hasattr(self, 'current_day') else 0,
        'type': 'dating'
    })
```

**In `city.py`, expand `process_social_interactions()`:**
```python
def process_social_interactions(self):
    """Check for agents at same location and process meetings/dating"""
    for location in self.locations.values():
        if len(location.current_occupants) < 2:
            continue
        
        agents_here = [self.agents[aid] for aid in location.current_occupants 
                      if aid in self.agents]
        
        for i, agent1 in enumerate(agents_here):
            for agent2 in agents_here[i+1:]:
                # Meet if haven't met before
                if agent2.id not in agent1.met_agents:
                    agent1.meet_agent(agent2)
                    agent2.meet_agent(agent1)
                
                # Consider dating
                elif agent1.consider_dating(agent2) and agent2.consider_dating(agent1):
                    agent1.start_dating(agent2)
                    print(f"💑 {agent1.name} and {agent2.name} started dating!")
```

---

## Phase 3: Relationship Progression (2-3 hours)

### Step 1: Add Relationship Quality Tracking

**In `agent.py`, add to Agent class:**
```python
relationship_satisfaction: int = 50  # 0-100, how happy in current relationship
days_in_relationship: int = 0

def update_relationship(self, partner: 'Agent', city_day: int):
    """Update relationship quality over time"""
    if not self.partner_id or self.partner_id != partner.id:
        return
    
    self.days_in_relationship += 1
    
    # Compatibility affects satisfaction
    compatibility = self.personality.compatibility_score(partner.personality)
    
    # Trend toward compatibility score
    if self.relationship_satisfaction < compatibility:
        self.relationship_satisfaction += random.randint(1, 3)
    elif self.relationship_satisfaction > compatibility:
        self.relationship_satisfaction -= random.randint(1, 3)
    
    # Clamp
    self.relationship_satisfaction = max(0, min(100, self.relationship_satisfaction))
    
    # Affect happiness
    if self.relationship_satisfaction > 70:
        self.happiness = min(100, self.happiness + 1)
    elif self.relationship_satisfaction < 30:
        self.happiness = max(0, self.happiness - 1)

def consider_marriage(self, partner: 'Agent') -> bool:
    """Decide whether to propose marriage"""
    if self.relationship_status != RelationshipStatus.DATING:
        return False
    
    # Must be together for a while
    if self.days_in_relationship < 365:  # 1 year minimum
        return False
    
    # High satisfaction required
    if self.relationship_satisfaction < 75:
        return False
    
    # Life goals alignment
    if LifeGoal.FAMILY_ORIENTED in self.life_goals:
        chance = 0.01  # 1% per day after 1 year
    else:
        chance = 0.003  # 0.3% per day
    
    return random.random() < chance

def get_married(self, partner: 'Agent'):
    """Get married to partner"""
    self.relationship_status = RelationshipStatus.MARRIED
    partner.relationship_status = RelationshipStatus.MARRIED
    
    self.happiness = min(100, self.happiness + 20)
    partner.happiness = min(100, partner.happiness + 20)
    
    print(f"💒 {self.name} and {partner.name} got married!")
```

**In `city.py`, add daily relationship updates:**
```python
def simulate_day(self):
    """Simulate one full day (called when time hits 0)"""
    # Update all relationships
    processed_pairs = set()
    
    for agent in self.agents.values():
        if agent.partner_id and agent.partner_id in self.agents:
            pair = tuple(sorted([agent.id, agent.partner_id]))
            
            if pair not in processed_pairs:
                processed_pairs.add(pair)
                partner = self.agents[agent.partner_id]
                
                # Update relationship
                agent.update_relationship(partner, self.current_day)
                
                # Consider marriage
                if agent.consider_marriage(partner):
                    agent.get_married(partner)

# Modify simulate_hour to call simulate_day
def simulate_hour(self):
    self.current_time = (self.current_time + 1) % 24
    if self.current_time == 0:
        self.current_day += 1
        self.simulate_day()  # NEW
    
    for agent in self.agents.values():
        self._update_agent_location(agent)
    
    self.process_social_interactions()
```

---

## Phase 4: Breakups & Divorce (2 hours)

### Step 1: Add Breakup Logic

**In `agent.py`:**
```python
def consider_breakup(self, partner: 'Agent') -> bool:
    """Decide whether to end the relationship"""
    if not self.partner_id:
        return False
    
    # Very low satisfaction triggers breakup
    if self.relationship_satisfaction < 20:
        return random.random() < 0.1  # 10% chance per day
    
    # Moderate dissatisfaction
    if self.relationship_satisfaction < 40:
        return random.random() < 0.01  # 1% chance per day
    
    return False

def break_up(self, partner: 'Agent'):
    """End the relationship"""
    was_married = self.relationship_status == RelationshipStatus.MARRIED
    
    # Update status
    if was_married:
        self.relationship_status = RelationshipStatus.DIVORCED
        partner.relationship_status = RelationshipStatus.DIVORCED
        print(f"💔 {self.name} and {partner.name} got divorced")
    else:
        self.relationship_status = RelationshipStatus.SINGLE
        partner.relationship_status = RelationshipStatus.SINGLE
        print(f"💔 {self.name} and {partner.name} broke up")
    
    # Clear partners
    self.partner_id = None
    partner.partner_id = None
    
    # Happiness hit
    happiness_loss = 30 if was_married else 15
    self.happiness = max(0, self.happiness - happiness_loss)
    partner.happiness = max(0, partner.happiness - happiness_loss)
    
    # Record in history
    self.relationship_history.append({
        'partner_id': partner.id,
        'ended': self.current_day if hasattr(self, 'current_day') else 0,
        'reason': 'breakup',
        'type': 'divorced' if was_married else 'dating'
    })
```

**In `city.py`, add to `simulate_day()`:**
```python
def simulate_day(self):
    """Simulate one full day"""
    processed_pairs = set()
    breakups = []  # Track breakups to process after loop
    
    for agent in self.agents.values():
        if agent.partner_id and agent.partner_id in self.agents:
            pair = tuple(sorted([agent.id, agent.partner_id]))
            
            if pair not in processed_pairs:
                processed_pairs.add(pair)
                partner = self.agents[agent.partner_id]
                
                # Update relationship
                agent.update_relationship(partner, self.current_day)
                
                # Check for breakup (either can initiate)
                if agent.consider_breakup(partner) or partner.consider_breakup(agent):
                    breakups.append((agent, partner))
                
                # Consider marriage (if still together)
                elif agent.consider_marriage(partner):
                    agent.get_married(partner)
    
    # Process breakups
    for agent, partner in breakups:
        agent.break_up(partner)
```

---

## Phase 5: Children System (4-5 hours)

### Step 1: Add Pregnancy & Birth

**In `agent.py`:**
```python
# Add to imports
from datetime import datetime

# Add to Agent class
is_pregnant: bool = False
pregnancy_due_day: int = 0

def consider_having_child(self, partner: 'Agent') -> bool:
    """Decide whether to have a baby"""
    if self.relationship_status != RelationshipStatus.MARRIED:
        return False
    
    # Age restrictions
    if self.gender == "female" and not (20 <= self.age <= 42):
        return False
    
    # Already have children? Less likely
    num_children = len(self.children_ids)
    if num_children >= 3:
        return False
    
    # Life goals matter
    if LifeGoal.FAMILY_ORIENTED in self.life_goals:
        chance = 0.005  # 0.5% per day
    else:
        chance = 0.001  # 0.1% per day
    
    # Reduce chance with each child
    chance *= (0.5 ** num_children)
    
    return random.random() < chance

def start_pregnancy(self):
    """Begin pregnancy"""
    if self.gender == "female" and not self.is_pregnant:
        self.is_pregnant = True
        self.pregnancy_due_day = self.current_day + 270  # ~9 months
        print(f"👶 {self.name} is pregnant!")

def give_birth(self, partner: 'Agent', city: 'City') -> 'Agent':
    """Give birth to a baby"""
    self.is_pregnant = False
    
    # Create baby
    baby = Agent(
        name=f"Baby {self.name.split()[-1]}",
        age=0,
        gender=random.choice(["male", "female"]),
        personality=Personality(
            # Inherit some traits from parents
            openness=(self.personality.openness + partner.personality.openness) // 2 + random.randint(-10, 10),
            conscientiousness=(self.personality.conscientiousness + partner.personality.conscientiousness) // 2 + random.randint(-10, 10),
            extraversion=(self.personality.extraversion + partner.personality.extraversion) // 2 + random.randint(-10, 10),
            agreeableness=(self.personality.agreeableness + partner.personality.agreeableness) // 2 + random.randint(-10, 10),
            neuroticism=(self.personality.neuroticism + partner.personality.neuroticism) // 2 + random.randint(-10, 10)
        ),
        education_level=EducationLevel.HIGH_SCHOOL,
        relationship_status=RelationshipStatus.SINGLE,
        home_location=self.home_location
    )
    
    # Clamp personality values
    for trait in ['openness', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']:
        setattr(baby.personality, trait, max(0, min(100, getattr(baby.personality, trait))))
    
    # Update family relationships
    self.children_ids.append(baby.id)
    partner.children_ids.append(baby.id)
    
    # Add to city
    city.add_agent(baby)
    
    print(f"👶 {self.name} gave birth to {baby.name}!")
    
    return baby
```

**In `city.py`, expand `simulate_day()`:**
```python
def simulate_day(self):
    """Simulate one full day"""
    processed_pairs = set()
    breakups = []
    births = []  # Track births
    
    for agent in self.agents.values():
        # Check pregnancy due date
        if agent.is_pregnant and self.current_day >= agent.pregnancy_due_day:
            if agent.partner_id and agent.partner_id in self.agents:
                partner = self.agents[agent.partner_id]
                births.append((agent, partner))
        
        # Existing relationship code...
        if agent.partner_id and agent.partner_id in self.agents:
            pair = tuple(sorted([agent.id, agent.partner_id]))
            
            if pair not in processed_pairs:
                processed_pairs.add(pair)
                partner = self.agents[agent.partner_id]
                
                agent.update_relationship(partner, self.current_day)
                
                if agent.consider_breakup(partner) or partner.consider_breakup(agent):
                    breakups.append((agent, partner))
                elif agent.consider_marriage(partner):
                    agent.get_married(partner)
                elif agent.relationship_status == RelationshipStatus.MARRIED:
                    # Consider having children
                    if agent.gender == "female" and agent.consider_having_child(partner):
                        agent.start_pregnancy()
    
    # Process breakups
    for agent, partner in breakups:
        agent.break_up(partner)
    
    # Process births
    for mother, father in births:
        mother.give_birth(father, self)
```

---

## Phase 6: Visualization Updates (1-2 hours)

**In `simulation.py`, update the info panel to show relationship info:**

```python
def draw_info_panel(self):
    # ... existing code ...
    
    if self.selected_agent and self.selected_agent in self.city.agents:
        agent = self.city.agents[self.selected_agent]
        
        # ... existing info ...
        
        # ADD RELATIONSHIP INFO
        info_lines.extend([
            "",
            "=== Relationships ===",
            f"Status: {agent.relationship_status.value}",
        ])
        
        if agent.partner_id and agent.partner_id in self.city.agents:
            partner = self.city.agents[agent.partner_id]
            info_lines.extend([
                f"Partner: {partner.name}",
                f"Satisfaction: {agent.relationship_satisfaction}/100",
                f"Days together: {agent.days_in_relationship}",
            ])
            
            if agent.is_pregnant:
                days_left = agent.pregnancy_due_day - self.city.current_day
                info_lines.append(f"Pregnant! Due in {days_left} days")
        
        if agent.children_ids:
            info_lines.append(f"Children: {len(agent.children_ids)}")
        
        info_lines.append(f"Met: {len(agent.met_agents)} people")
```

---

## Testing Checklist

✅ **Phase 1**: Agents meet when at same location  
✅ **Phase 2**: Compatible agents start dating  
✅ **Phase 3**: Dating couples can get married  
✅ **Phase 4**: Unhappy couples can break up/divorce  
✅ **Phase 5**: Married couples can have children  
✅ **Phase 6**: UI shows relationship details

---

## Statistics to Track

Add these to a new statistics dashboard:

```python
class CityStatistics:
    def __init__(self, city: City):
        self.city = city
    
    def get_relationship_stats(self) -> Dict:
        single = sum(1 for a in self.city.agents.values() 
                    if a.relationship_status == RelationshipStatus.SINGLE)
        dating = sum(1 for a in self.city.agents.values() 
                    if a.relationship_status == RelationshipStatus.DATING)
        married = sum(1 for a in self.city.agents.values() 
                     if a.relationship_status == RelationshipStatus.MARRIED)
        divorced = sum(1 for a in self.city.agents.values() 
                      if a.relationship_status == RelationshipStatus.DIVORCED)
        
        total_children = sum(len(a.children_ids) for a in self.city.agents.values())
        
        return {
            'single': single,
            'dating': dating // 2,  # Count couples, not individuals
            'married': married // 2,
            'divorced': divorced,
            'total_children': total_children,
            'birth_rate': total_children / len(self.city.agents) if self.city.agents else 0
        }
```

---

## Next Steps After Relationships

Once relationships are working:
1. **Friendship networks** - Similar system but non-romantic
2. **Aging system** - Children grow up, adults age
3. **Death system** - Natural causes, becoming widowed
4. **Life events** - Random events affecting relationships
5. **Economic effects** - Money impacts relationship stress

This roadmap gives you everything you need to build a complete relationship system. Start with Phase 1 and work your way through!
