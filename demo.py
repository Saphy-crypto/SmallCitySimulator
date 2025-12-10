#!/usr/bin/env python3
"""
City Simulation Demo

This is your AI agent-based city simulator! Here's what's implemented:

AGENTS:
- Each agent has personality traits (Big Five: OCEAN model)
- Life goals (career-focused, family-oriented, etc.)
- Hobbies and interests
- Education level and income
- Relationship status
- Decision-making based on personality

CITY:
- Multiple location types (homes, workplaces, schools, parks, etc.)
- Grid-based layout with positions
- Capacity management for locations

SIMULATION:
- Time progression (24-hour cycle)
- Agents move between locations based on time and personality
- Real-time visualization
- Click agents to see their full details

NEXT STEPS TO BUILD:
1. Relationship system (meeting, dating, marriage)
2. Children/birth system
3. Job seeking and career progression
4. Social interaction between agents
5. Friendship formation
6. Breakups and divorces
7. Statistics tracking
8. More complex AI decision-making
"""

import sys
import os

def main():
    print(__doc__)
    print("\n" + "="*60)
    print("STARTING SIMULATION")
    print("="*60 + "\n")
    
    # Import and run the simulation
    from simulation import main as run_simulation
    run_simulation()

if __name__ == "__main__":
    main()
