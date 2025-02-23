import json
import random
import numpy as np


# Load data from JSON
with open("data/names.json", "r") as file:
    data = json.load(file)

# Access lists from the JSON file
first_names = data["first_names"]
last_names = data["last_names"]
talents = data["talents"]
negative_traits = data["negative_traits"]
backgrounds = data["backgrounds"]
secret_bodies = data["secret_bodies"]
affiliations = data["affiliations"]
trait_stat_relationships = data["trait_stat_relationships"]
negative_trait_stat_relationships = data["negative_trait_stat_relationships"]

# Helper function to determine traits with probabilities
def get_traits(trait_list, max_traits=5):
    if random.random() < 0.4:  # 40% chance of no traits
        return []

    traits = [random.choice(trait_list)]  # Always at least one trait
    probability = 0.5  # Start with 50% chance for a second trait

    while len(traits) < max_traits and random.random() < probability:
        new_trait = random.choice(trait_list)
        if new_trait not in traits:  # Avoid duplicates
            traits.append(new_trait)
        probability /= 2  # Halve the chance for the next trait

    return traits

# Helper function to generate a skewed age distribution
def generate_age():
    while True:
        # Generate a normal distribution with mean 20 and standard deviation 5
        age = np.random.normal(loc=20, scale=8)
        # Apply positive skewness (higher chance of lower ages)
        if random.random() < 0.8:  # 80% chance to favor younger ages
            age = min(age, np.random.uniform(18, 30))
        if 16 <= age <= 60:  # Ensure age is within the desired range
            return int(round(age))

# Helper function to generate normally distributed stats
def generate_stat():
    while True:
        stat = np.random.normal(loc=4, scale=2)  # Mean 4, standard deviation 2
        if 0 <= stat <= 10:  # Ensure stats are between 0 and 10
            return int(round(stat))

def apply_trait_boosts(character, trait_stat_relationships, negative_trait_stat_relationships):
    # Apply positive boosts
    for trait in character["Secret Talents (Native)"] + character["Acquired Talents"]:
        if trait in trait_stat_relationships:
            for stat, boost in trait_stat_relationships[trait].items():
                if stat in character:  # For primary stats
                    character[stat] += boost
                elif stat in character["Secondary Stats"]:  # For secondary stats
                    if isinstance(character["Secondary Stats"][stat], dict):  # Nested dictionary
                        for sub_stat, sub_boost in boost.items():
                            character["Secondary Stats"][stat][sub_stat] += sub_boost
                    else:  # Regular secondary stat
                        character["Secondary Stats"][stat] += boost

    # Apply negative penalties
    for trait in character["Negative Traits (Native)"] + character["Acquired Negative Traits"]:
        if trait in negative_trait_stat_relationships:
            for stat, penalty in negative_trait_stat_relationships[trait].items():
                if stat in character:  # For primary stats
                    character[stat] += penalty
                elif stat in character["Secondary Stats"]:  # For secondary stats
                    if isinstance(character["Secondary Stats"][stat], dict):  # Nested dictionary
                        for sub_stat, sub_penalty in penalty.items():
                            character["Secondary Stats"][stat][sub_stat] += sub_penalty
                    else:  # Regular secondary stat
                        character["Secondary Stats"][stat] += penalty

    # Apply buffs from the secret body
    if character["Secret Body"] != "None":
        secret_body_buffs = secret_bodies[character["Secret Body"]]
        for stat, boost in secret_body_buffs.items():
            if stat in character:  # For primary stats
                character[stat] += boost
            elif stat in character["Secondary Stats"]:  # For secondary stats
                if isinstance(character["Secondary Stats"][stat], dict):  # Nested dictionary
                    for sub_stat, sub_boost in boost.items():
                        character["Secondary Stats"][stat][sub_stat] += sub_boost
                else:  # Regular secondary stat
                    character["Secondary Stats"][stat] += boost

def get_acquired_traits(trait_list, age, max_traits=5):
    # Calculate the probability based on age
    probability = min(0.02 * (age - 16), 1.0)  # 2% per year, capped at 100%

    if random.random() > probability:  # Check if no acquired traits
        return []

    traits = [random.choice(trait_list)]  # Always at least one trait if eligible
    while len(traits) < max_traits and random.random() < probability:
        new_trait = random.choice(trait_list)
        if new_trait not in traits:  # Avoid duplicates
            traits.append(new_trait)

    return traits


def create_random_character():
    age = generate_age()

    base_stats = {
        "Strength": generate_stat(),
        "Dexterity": generate_stat(),
        "Intellect": generate_stat(),
        "Perception": generate_stat(),
        "Luck": generate_stat(),
        "Agility": generate_stat(),
        "Resilience": generate_stat(),
        "Social": generate_stat(),
    }

    character = {
        "Name": f"{random.choice(first_names)} {random.choice(last_names)}",
        "Sex": random.choice(["Male", "Female"]),
        "Age": age,
        "Secret Talents (Native)": get_traits(talents["native"]),
        "Acquired Talents": get_acquired_traits(talents["acquired"], age),
        "Negative Traits (Native)": get_traits(negative_traits["native"]),
        "Acquired Negative Traits": get_acquired_traits(negative_traits["acquired"], age),
        "Background": random.choice(backgrounds),
        "Secret Body": random.choice(list(secret_bodies.keys())) if random.random() < 0.05 else "None",
        "Affiliation": random.choice(affiliations),
        "QI": random.choice([0] + [random.randint(1, 100)] * 2 if random.random() >= 0.8 else [0]),
        "Lifespan": random.randint(50, 200),
        "Base Stats": base_stats,
        "Strength": base_stats["Strength"],
        "Dexterity": base_stats["Dexterity"],
        "Intellect": base_stats["Intellect"],
        "Perception": base_stats["Perception"],
        "Luck": base_stats["Luck"],
        "Agility": base_stats["Agility"],
        "Resilience": base_stats["Resilience"],
        "Social": base_stats["Social"],
        "Secondary Stats": {
            "Fighting": 0,
            "Running": 0,
            "Speaking": 0,
            "Negotiation": 0,
            "Stealth": 0,
            "Studying": 0,
            "Fishing": 0,
            "QI Control": 0,
            "Weapon Control": {
                "Sword": 0,
                "Blade": 0,
                "Lance": 0,
                "Palm": 0,
                "Kick": 0,
                "Hammer": 0,
                "Club": 0,
                "Bow": 0
            },
            "Spell": 0,
            "Artisanal Skill": {
                "Forging Weapon": 0,
                "Forging Armor": 0,
                "Crafting": 0,
                "Manual Labor": 0
            },
            "Alchemist Skill": 0,
            "Formation Skill": 0,
            "Beauty": 0,
            "Renown": 0,
            "Beast Taming": 0
        }
    }

    apply_trait_boosts(character, trait_stat_relationships, negative_trait_stat_relationships)
    return character





