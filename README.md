# AI City Simulation

A city simulator with autonomous AI agents that have personalities, jobs, relationships, and daily routines based on real life statistics.


### Core Agent System
Each agent is a fully-featured individual with:

- **Demographics**: Name, age, gender
- **Personality Traits**: Based on the Big Five (OCEAN) model
  - Openness (creativity, curiosity)
  - Conscientiousness (organization, responsibility)
  - Extraversion (sociability, energy)
  - Agreeableness (friendliness, cooperation)
  - Neuroticism (emotional stability)
- **Life Goals**: Career-focused, family-oriented, social butterfly, creative pursuits, wealth accumulation, knowledge seeker
- **Hobbies**: Reading, gaming, sports, cooking, music, art, hiking, photography, gardening
- **Education**: High school through doctorate
- **Income**: Based on education level with realistic salary ranges
- **Relationships**: Status tracking (single, dating, married, divorced, widowed)
- **Stats**: Happiness, health, energy levels

### City Infrastructure
- **Multiple Location Types**: Residential, workplace, school, retail, restaurant, park, gym, entertainment, hospital
- **Grid-based Layout**: 50x50 grid with positioned locations
- **Capacity Management**: Each location has occupancy limits
- **Default City Setup**: Automatically creates apartments, offices, schools, parks, etc.

### Simulation Engine
- **Time System**: 24-hour day/night cycle with day counter
- **Agent Decision-Making**: Agents decide actions based on:
  - Current time
  - Personality traits
  - Energy levels
  - Employment status
  - Hobbies
- **Movement System**: Agents travel between locations realistically
- **Real-time Visualization**: See agents move around the city

## 🚀 How to Run

```bash
# Run the simulation
python simulation.py

# Or use the demo script
python demo.py
```

## 🎯 Controls

- **SPACE**: Pause/Resume simulation
- **UP/DOWN Arrows**: Adjust simulation speed (1x - 10x)
- **N**: Toggle location names on/off
- **A**: Add a random agent to the city
- **Click on agent**: Select and view full details

## 📊 Agent Generation Statistics

Agents are generated using real US demographic statistics:

### Education Distribution
- 12% - High school
- 30% - Some college
- 65% - Bachelor's degree
- 90% - Master's degree
- 10% - Doctorate

### Income Ranges by Education
- High school: $20,000 - $40,000
- Some college: $25,000 - $50,000
- Bachelor's: $40,000 - $90,000
- Master's: $60,000 - $130,000
- Doctorate: $80,000 - $180,000

### Personality Traits
Generated using normal distribution (mean=50, std=20) for realistic variation.

### Relationship Status (Age dependent)
- Under 25: Mostly single or dating
- 25 to 35: Mix of single, dating, married
- Over 35: Primarily married, some single or divorced

## 📁 Project Structure

```
├── agent.py          # Agent class with personality, stats, decision-making
├── city.py           # City infrastructure, locations, simulation logic
├── simulation.py     # Pygame visualization and main loop
├── demo.py          # Demo launcher with documentation
└── README.md        # This file
```

## 🔮 Next Features to Implement

### 1. Relationship System
- Meeting potential partners at social locations
- Compatibility checking based on personality traits
- Dating progression (single → dating → engaged → married)
- Breakup mechanics based on compatibility and life events

### 2. Social Network
- Friendship formation at work, school, hobbies
- Friend meetups and social activities
- Friendship decay over time without interaction
- Social satisfaction affecting happiness

### 3. Children & Family
- Pregnancy and childbirth system
- Child agents growing up
- Parenting effects on happiness and energy
- Family activities

### 4. Career System
- Job seeking and applications
- Promotions and raises
- Career changes based on goals
- Retirement at appropriate age

### 5. Life Events
- Random events (illness, accidents, windfalls)
- Major life decisions (relocating, career changes)
- Aging effects on health and energy
- Death system (natural causes, age-related)

### 6. Advanced AI
- Memory of past interactions
- Learning from experiences
- Goal-driven behavior (working toward life goals)
- Complex decision trees

### 7. Economics
- Housing market (buying/renting)
- Living expenses
- Savings and financial planning
- Economic class mobility

### 8. Statistics Dashboard
- Population demographics
- Average happiness/health
- Relationship statistics
- Economic indicators
- Birth/death rates

## 🎨 Visual Guide

### Location Colors
- 🔵 **Blue** - Residential (homes, apartments)
- 🔴 **Red** - Workplace (offices, businesses)
- 🟡 **Yellow** - School (education facilities)
- 🟠 **Orange** - Retail (stores, malls)
- 🌸 **Pink** - Restaurant (dining, cafes)
- 🟢 **Green** - Park (outdoor spaces)
- 🟣 **Purple** - Gym (fitness centers)
- 🔵 **Cyan** - Entertainment (theaters, venues)
- ⚪ **White** - Hospital (healthcare)

### Agent Indicators
- **Black dot** - Regular agent
- **Purple dot** - Selected agent
- Numbers on locations show current occupancy

## 🛠️ Technical Details

### Technologies Used
- **Python 3.12**
- **Pygame 2.6.1** - For visualization
- **Dataclasses** - For clean data structures
- **Enums** - For type-safe categories

### Performance
- Handles 50+ agents smoothly
- Real-time simulation at 60 FPS
- Adjustable time speed (1x-10x)

### Code Quality
- Type hints throughout
- Modular architecture
- Clean separation of concerns:
  - `agent.py` - Agent logic only
  - `city.py` - City/location logic only
  - `simulation.py` - Visualization only

## 💡 Example Use Cases

### Research
- Study emergence of social patterns
- Test urban planning concepts
- Analyze relationship dynamics

### Game Development
- Prototype for city-building game
- NPC behavior system
- Dynamic population simulation

### Education
- Demonstrate complex systems
- Teach agent-based modeling
- Explore sociological concepts

## 🤝 How to Extend

### Adding New Location Types
```python
# In city.py
class LocationType(Enum):
    YOUR_TYPE = "your_type"

# Add to LOCATION_COLORS in simulation.py
LOCATION_COLORS[LocationType.YOUR_TYPE] = (r, g, b)
```

### Adding New Personality Traits
```python
# In agent.py: Personality class
@dataclass
class Personality:
    your_trait: int = 50
```

### Adding New Agent Behaviors
```python
# In agent.py: Agent.decide_action()
def decide_action(self, current_time: int) -> str:
    # Add your logic here
    if some_condition:
        return "new_action"
```

## 📈 Current Limitations

1. **No persistent relationships**: Agents don't form lasting bonds yet
2. **Simple pathfinding**: Direct teleportation between locations
3. **No resource management**: Money doesn't affect behavior yet
4. **Static jobs**: No job changes or unemployment
5. **No reproduction**: Population is fixed
6. **No death**: Agents live forever currently

## 🎯 Immediate Next Steps

If you want to continue developing this, I recommend:

1. **Add relationship formation** - Agents can meet and start dating
2. **Implement friendship system** - Agents build social networks
3. **Add basic conversations** - Agents can interact when at same location
4. **Create life events** - Trigger random events that affect agents
5. **Build statistics tracking** - Dashboard showing population metrics

## 📝 Notes

- All statistics based on real US demographics (as of 2024)
- Personality compatibility uses the Big Five model
- Agent decision-making is deterministic but personality-driven
- Time scale is flexible (can be sped up/slowed down)

---

**Ready to see it in action?** Run `python simulation.py` and start exploring!
