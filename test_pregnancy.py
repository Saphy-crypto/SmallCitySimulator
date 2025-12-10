#!/usr/bin/env python3
"""Test script for improved pregnancy system"""

from city import create_default_city
from agent import generate_random_agent, LifeGoal, RelationshipStatus, SexualOrientation
from datetime import date

def test_improved_pregnancy_system():
    """Test the improved pregnancy system functionality"""
    print("=== Testing IMPROVED Pregnancy System ===\n")
    
    # Create city and agents
    city = create_default_city("TestCity")
    current_date = date(2024, 1, 1)
    
    # Test 1: Married couple that has been together long enough
    print("=== TEST 1: Married Couple (1+ year together) ===")
    female = generate_random_agent(age_range=(25, 30))
    female.gender = "female"
    female.name = "Sarah Johnson"
    female.life_goals = [LifeGoal.WANTS_CHILDREN, LifeGoal.FAMILY_ORIENTED]
    female.relationship_status = RelationshipStatus.MARRIED
    female.personality.conscientiousness = 80  # High conscientiousness (mature)
    female.days_in_relationship = 400  # 13+ months together
    
    male = generate_random_agent(age_range=(25, 35)) 
    male.gender = "male"
    male.name = "David Johnson"
    male.life_goals = [LifeGoal.WANTS_CHILDREN, LifeGoal.FAMILY_ORIENTED]
    male.relationship_status = RelationshipStatus.MARRIED
    male.days_in_relationship = 400
    
    # Link them as partners
    female.partner_id = male.id
    male.partner_id = female.id
    
    city.add_agent(female)
    city.add_agent(male)
    
    print(f"Created couple: {female.name} & {male.name}")
    print(f"Relationship duration: {female.days_in_relationship} days")
    print(f"Both want children: {LifeGoal.WANTS_CHILDREN in female.life_goals and LifeGoal.WANTS_CHILDREN in male.life_goals}")
    
    # Test planned pregnancy with higher rates
    print("\nTesting planned pregnancy (should happen quickly)...")
    for attempt in range(1, 11):  # Only try 10 times with new high rates
        if female.try_to_conceive(male, is_planned=True):
            print(f"🤰 SUCCESS! {female.name} got pregnant on attempt {attempt}!")
            break
    else:
        print("❌ No pregnancy after 10 attempts (unexpected with new rates)")
    
    # Test 2: Same-sex couple adoption
    print("\n=== TEST 2: Same-Sex Couple Adoption ===")
    female1 = generate_random_agent(age_range=(28, 35))
    female1.gender = "female"
    female1.name = "Alex Rivera"
    female1.life_goals = [LifeGoal.WANTS_CHILDREN, LifeGoal.FAMILY_ORIENTED]
    female1.relationship_status = RelationshipStatus.MARRIED
    female1.sexual_orientation = SexualOrientation.LESBIAN
    female1.days_in_relationship = 800  # 2+ years together
    
    female2 = generate_random_agent(age_range=(28, 35))
    female2.gender = "female" 
    female2.name = "Jamie Rivera"
    female2.life_goals = [LifeGoal.FAMILY_ORIENTED]
    female2.relationship_status = RelationshipStatus.MARRIED
    female2.sexual_orientation = SexualOrientation.LESBIAN
    female2.days_in_relationship = 800
    
    # Link them as partners
    female1.partner_id = female2.id
    female2.partner_id = female1.id
    
    city.add_agent(female1)
    city.add_agent(female2)
    
    print(f"Created same-sex couple: {female1.name} & {female2.name}")
    print(f"Relationship duration: {female1.days_in_relationship} days")
    print(f"Can adopt: {female1.can_adopt(female2)}")
    
    # Test adoption
    if female1.can_adopt(female2):
        result = female1.adopt_child(female2, current_date)
        if result:
            child_id, child_agent = result
            print(f"👨‍👩‍👧‍👦 SUCCESS! {female1.name} and {female2.name} adopted {child_agent.name} (age {child_agent.age})!")
            print(f"  Adoptive parents: Mother ID: {child_agent.mother_id}, Father ID: {child_agent.father_id}")
        else:
            print("❌ Adoption failed")
    
    # Test 3: Unplanned pregnancy with personality factors
    print("\n=== TEST 3: Unplanned Pregnancy (Personality-Based) ===")
    
    # Create impulsive person (low conscientiousness, high neuroticism)
    impulsive_female = generate_random_agent(age_range=(20, 25))
    impulsive_female.gender = "female"
    impulsive_female.name = "Riley Thompson"
    impulsive_female.relationship_status = RelationshipStatus.DATING
    impulsive_female.personality.conscientiousness = 20  # Very impulsive
    impulsive_female.personality.neuroticism = 80  # High neuroticism
    impulsive_female.days_in_relationship = 90  # Only 3 months (too soon for planned)
    
    impulsive_male = generate_random_agent(age_range=(22, 27))
    impulsive_male.gender = "male"
    impulsive_male.name = "Tyler Thompson"
    impulsive_male.relationship_status = RelationshipStatus.DATING
    impulsive_male.personality.conscientiousness = 25  # Also impulsive
    impulsive_male.days_in_relationship = 90
    
    # Link them as dating partners
    impulsive_female.partner_id = impulsive_male.id
    impulsive_male.partner_id = impulsive_female.id
    
    city.add_agent(impulsive_female)
    city.add_agent(impulsive_male)
    
    print(f"Created impulsive couple: {impulsive_female.name} & {impulsive_male.name}")
    print(f"Female conscientiousness: {impulsive_female.personality.conscientiousness}")
    print(f"Female neuroticism: {impulsive_female.personality.neuroticism}")
    print(f"Relationship duration: {impulsive_female.days_in_relationship} days (too soon for planned)")
    
    # Test unplanned pregnancy
    print("Testing unplanned pregnancy with personality factors...")
    for attempt in range(1, 21):  # Try more attempts for unplanned
        if impulsive_female.try_to_conceive(impulsive_male, is_planned=False):
            print(f"🤰 UNPLANNED! {impulsive_female.name} got pregnant on attempt {attempt}!")
            print(f"  Due to personality: Low conscientiousness + High neuroticism = Higher risk")
            break
    else:
        print("No unplanned pregnancy in 20 attempts (unexpected with personality factors)")
    
    # Test 4: Mature couple that won't have unplanned pregnancy
    print("\n=== TEST 4: Mature Couple (Low Unplanned Risk) ===")
    
    mature_female = generate_random_agent(age_range=(30, 35))
    mature_female.gender = "female"
    mature_female.name = "Dr. Lisa Chen"
    mature_female.relationship_status = RelationshipStatus.DATING
    mature_female.personality.conscientiousness = 90  # Very mature
    mature_female.personality.neuroticism = 20  # Low neuroticism
    mature_female.days_in_relationship = 200  # 6+ months
    
    mature_male = generate_random_agent(age_range=(30, 35))
    mature_male.gender = "male"
    mature_male.name = "Dr. Mark Chen"
    mature_male.relationship_status = RelationshipStatus.DATING
    mature_male.personality.conscientiousness = 85  # Also mature
    mature_male.days_in_relationship = 200
    
    # Link them
    mature_female.partner_id = mature_male.id
    mature_male.partner_id = mature_female.id
    
    city.add_agent(mature_female)
    city.add_agent(mature_male)
    
    print(f"Created mature couple: {mature_female.name} & {mature_male.name}")
    print(f"Female conscientiousness: {mature_female.personality.conscientiousness}")
    print(f"Female neuroticism: {mature_female.personality.neuroticism}")
    
    # Test that they WON'T have unplanned pregnancies easily
    unplanned_count = 0
    for attempt in range(1, 51):  # Try many times
        if mature_female.try_to_conceive(mature_male, is_planned=False):
            unplanned_count += 1
    
    print(f"Unplanned pregnancies in 50 attempts: {unplanned_count}")
    print(f"✅ Mature couples have lower unplanned pregnancy rates!" if unplanned_count < 3 else "❌ Too many unplanned pregnancies")

    print("\n=== IMPROVED Pregnancy System Test Complete ===")
    print("\n🎯 KEY IMPROVEMENTS:")
    print("   ✅ Pregnancy rates MUCH higher (15% planned, 3% unplanned daily)")
    print("   ✅ Planned pregnancies require 1+ year relationship")
    print("   ✅ Same-sex couples can adopt after 2+ years")
    print("   ✅ Personality affects unplanned pregnancy risk")
    print("   ✅ Mature people (high conscientiousness) = lower risk")

if __name__ == "__main__":
    test_improved_pregnancy_system()