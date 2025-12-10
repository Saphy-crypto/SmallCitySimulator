# 🎮 Quick Start Guide - City Simulation

## What You Have

A fully working AI city simulator with autonomous agents! Here's what's ready:

### ✅ Working Features
- **5 Agents** spawn automatically with unique personalities
- **27 Locations** including homes, offices, schools, parks, restaurants
- **24-hour simulation** with day/night cycles
- **Real-time visualization** showing agent movement
- **Personality-driven AI** - agents make decisions based on their traits
- **Click-to-inspect** any agent to see full details

## 🚀 How to Run (3 Easy Steps)

### Step 1: Download Files
You have these files ready to use:
- `agent.py` - Agent AI system
- `city.py` - City infrastructure
- `simulation.py` - Visual interface
- `demo.py` - Launch script
- `README.md` - Full documentation

### Step 2: Install Requirements
```bash
pip install pygame
```

### Step 3: Run!
```bash
python simulation.py
```

That's it! The simulation window will open.

## 🎮 What You'll See

```
┌─────────────────────────────────────────────────────┐
│                   City Grid (50x50)                  │
│                                                      │
│  🔵 = Homes        🟡 = Schools     🟢 = Parks       │
│  🔴 = Offices      🌸 = Restaurants 🟣 = Gyms        │
│  ⚫ = Agents (move around automatically)             │
│                                                      │
│  [Right side shows selected agent details]          │
└─────────────────────────────────────────────────────┘
```

## 🎯 Try These Things

1. **Watch agents go to work** - Press SPACE to resume, agents move to offices at 9am
2. **See lunch rush** - Around noon, agents visit restaurants
3. **Evening socializing** - Extraverted agents hit bars and parks after 5pm
4. **Click any agent** - See their full personality, job, income, stats
5. **Press A** - Add more agents dynamically
6. **UP/DOWN arrows** - Speed up time (up to 10x)

## 🔍 Understanding Agent Behavior

### Agent Decision Logic
```
6am to 9am   → Wake up, at home
9am to 5pm   → Work (if employed) or School (if student)
5pm to 10pm  → Social activities (based on personality)
              - High extraversion? → Restaurant or bar
              - Has hobbies? → Related location
              - Low energy? → Stay home
10pm to 6am  → Sleep at home
```

### Personality Effects
- **High Extraversion** → More likely to socialize evenings
- **High Conscientiousness** → Reliable work schedule
- **High Openness** → Diverse hobbies and activities
- **High Agreeableness** → (Will affect relationships later)
- **Low Energy** → Go home earlier

## 📊 Sample Agent

When you click an agent, you'll see:
```
Name: Jennifer Martinez
Age: 32 years old
Gender: female

Job: Masters Professional
Income: $87,450/year
Education: masters

Status: married
Happiness: 72/100
Health: 88/100
Energy: 65/100

Location: Tech Corp HQ
Action: working

Personality:
  Openness: 68
  Conscientiousness: 54
  Extraversion: 73
  Agreeableness: 61
  Neuroticism: 42
```

## 🎨 Customization Ideas

Want to modify the simulation? Here's what's easy to change:

### Add More Starting Agents
```python
# In simulation.py, line ~252
for i in range(10):  # Change 5 to 10
    agent = generate_random_agent()
```

### Change Time Speed
```python
# In simulation.py, line ~234
frames_per_hour = 15  # Lower means faster (default: 30)
```

### Add Custom Locations
```python
# In city.py, after line ~150
city.add_location(Location(
    id="my_location",
    name="Your Place Name",
    location_type=LocationType.ENTERTAINMENT,
    position=(25, 25),
    capacity=50
))
```

## 🔮 What's Next?

The foundation is built! Here's what you could add:

### Easy Additions (1 to 2 hours each)
1. **More agents** - Change the starting count
2. **More locations** - Copy existing location code
3. **Different city layouts** - Modify positions
4. **Color themes** - Change the color scheme

### Medium Additions (4 to 8 hours each)
1. **Relationship system** - Agents can meet and date
2. **Job changes** - Agents can get promoted or fired
3. **Friendship networks** - Track who knows who
4. **Statistics panel** - Show city wide metrics

### Advanced Additions (1 to 2 days each)
1. **Children and families** - Birth, aging, parenting
2. **Economic system** - Money management, expenses
3. **Life events** - Random occurrences affecting agents
4. **Memory system** - Agents remember past interactions

## 🐛 Troubleshooting

### "No module named pygame"
```bash
pip install pygame
```

### Window doesn't open
Make sure you're running Python 3.8+:
```bash
python --version
```

### Simulation too fast or slow
Press UP or DOWN arrows to adjust speed in real time

### Can't see agent names
Press N to toggle name display

## 💡 Pro Tips

1. **Start small** - Begin with 5 agents, add more with A key
2. **Speed up time** - Use UP arrow to see full day cycles quickly
3. **Follow one agent** - Click someone and watch their routine
4. **Pause to inspect** - Hit SPACE to freeze and examine details
5. **Look for patterns** - Notice how personality affects behavior

## 📚 Full Documentation

See `README.md` for:
- Complete technical details
- Architecture explanation
- Extension guide
- Statistics documentation

## 🎉 You're Ready!

Everything is set up. Just run:
```bash
python simulation.py
```

And watch your city come alive!

**Questions?** Check README.md for detailed documentation.
**Want to extend it?** Start with the relationship system. It's outlined and ready to implement!
