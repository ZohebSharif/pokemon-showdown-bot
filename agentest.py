import asyncio
import re
import numpy as np
import os
import sys
from bs4 import BeautifulSoup
from uagents import Agent, Context  # Ensure this is the correct import for your agent setup

# Debugging output
print("Current directory:", os.path.dirname(os.path.abspath(__file__)))
print("Contents of the current directory:", os.listdir(os.path.dirname(os.path.abspath(__file__))))
print("Python path:", sys.path)

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Constants for reward values (can be adjusted)
REWARDS = {
    'win': 10.0,
    'kill': 5.0,
    'status': 3.0,
    'damage': 0.1  # Per 1% of damage dealt
}

# Q-learning parameters
ALPHA = 0.1  # Learning rate
GAMMA = 0.9  # Discount factor
EPSILON = 0.1  # Exploration rate

# Dictionary to track battle state and rewards
battle_state = {
    'won': False,
    'killed_pkmn': 0,
    'status_inflicted': 0,
    'damage_done': 0.0
}

total_rewards = 0.0  # Track total rewards earned for the current battle
total_game_score = 0.0  # Track total game score across battles

# Initialize Q-table
q_table = {}

# Function to handle adding rewards manually
def add_reward(amount):
    global total_rewards
    total_rewards += amount
    print(f"Reward of {amount} added. Total rewards this battle: {total_rewards}")

# Function to parse the battle log and update battle state
def parse_battle_log(file_path, ctx: Context):
    global battle_state, total_rewards

    # Reset battle state and rewards at the beginning of parsing
    battle_state = {
        'won': False,
        'killed_pkmn': 0,
        'status_inflicted': 0,
        'damage_done': 0.0
    }
    total_rewards = 0.0  # Reset battle rewards for a new battle

    try:
        with open(file_path, 'r') as file:
            battle_log = file.read()
        
        # Split the battle log into lines for processing
        lines = battle_log.splitlines()
        for line in lines:
            line_lower = line.lower()  # Convert line to lowercase for case-insensitive matching

            # Check for a win
            if "won the battle!" in line_lower:
                battle_state['won'] = True
                add_reward(REWARDS['win'])
                print("Win detected, reward added.")

            # Check for Pokémon fainted
            if "fainted" in line_lower:
                battle_state['killed_pkmn'] += 1
                add_reward(REWARDS['kill'])
                print("Pokemon faint detected, reward added.")
            
            # Check for status inflicted
            if "paralyzed" in line_lower or "asleep" in line_lower:
                battle_state['status_inflicted'] += 1
                add_reward(REWARDS['status'])
                print("Status inflicted, reward added.")
            
            # Check for damage done (assuming percentages of health)
            if "%" in line_lower and "lost" in line_lower:
                try:
                    # Example: '(Exeggcute lost 71.0% of its health!)'
                    percentage_str = re.search(r'(\d+\.\d+)%', line_lower).group(1)
                    damage = float(percentage_str)
                    battle_state['damage_done'] += damage
                    add_reward(damage * REWARDS['damage'])
                    print(f"Damage detected: {damage}%, reward added.")
                except (IndexError, ValueError, AttributeError) as e:
                    print(f"Error parsing damage from line: '{line}'. Error: {e}")

        # Update Q-values based on the current battle state and rewards
        update_q_values(battle_state)

        # After processing the battle log, add the total rewards to the total game score
        global total_game_score
        total_game_score += total_rewards
        print(f"Total game score updated: {total_game_score}")

    except FileNotFoundError:
        print(f"File {file_path} not found.")
    except Exception as e:
        print(f"An error occurred while parsing the log: {e}")

# Function to update Q-values
def update_q_values(state):
    global q_table, total_rewards

    state_tuple = (state['won'], state['killed_pkmn'], state['status_inflicted'], state['damage_done'])

    # Initialize Q-values for the state if not already done
    if state_tuple not in q_table:
        q_table[state_tuple] = np.zeros(4)  # Assume 4 possible actions for simplification

    # Choose an action (for now, we can randomly choose an action)
    action = np.random.choice([0, 1, 2, 3])  # Choose one of the 4 actions (this needs a proper action definition)

    # Simulate a reward for the chosen action
    reward = total_rewards  # You can modify this to get the reward specific to the action taken

    # Update Q-value for the chosen action using the Q-learning formula
    best_future_q = np.max(q_table[state_tuple])  # Get the maximum Q-value for the next state
    current_q = q_table[state_tuple][action]
    
    # Q-learning formula
    new_q = (1 - ALPHA) * current_q + ALPHA * (reward + GAMMA * best_future_q)
    q_table[state_tuple][action] = new_q

    print(f"Updated Q-table for state {state_tuple}: {q_table[state_tuple]}")

# Define your agent
agent = Agent(name="pokemon_agent")  # Removed agent_id as it's not supported

# Function to extract active Pokémon from HTML
def extract_active_pokemon(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find the active Pokémon (opponent's and your Pokémon)
    opponent_pokemon = soup.find_all('span', class_='picon has-tooltip')[0]  # Assuming opponent's Pokémon is first
    your_pokemon = soup.find_all('span', class_='picon has-tooltip')[1]  # Your Pokémon is second

    # Extract Pokémon names from the 'aria-label' attribute
    opponent_name = opponent_pokemon['aria-label'].split(' ')[0]  # Get only the Pokémon name
    your_name = your_pokemon['aria-label'].split(' ')[0]

    return opponent_name, your_name

# Example type advantage and disadvantage dictionaries
type_advantages = {
    'Fire': ['Grass', 'Bug', 'Ice', 'Steel'],
    'Water': ['Fire', 'Ground', 'Rock'],
    'Grass': ['Water', 'Ground', 'Rock'],
    # Add other types and their advantages here...
}

type_disadvantages = {
    'Fire': ['Water', 'Rock', 'Ground'],
    'Water': ['Electric', 'Grass'],
    'Grass': ['Fire', 'Bug', 'Flying', 'Ice'],
    # Add other types and their disadvantages here...
}

# Function to get Pokémon type
def get_pokemon_type(pokemon_name):
    # This should return the type of the Pokémon based on its name
    # You can implement a dictionary lookup or API call here
    # Example:
    types = {
        'Charmander': 'Fire',
        'Squirtle': 'Water',
        # Add more Pokémon and their types here...
    }
    return types.get(pokemon_name, None)  # Return None if Pokémon type not found

# Suggest moves based on active Pokémon
def suggest_move(opponent_name, your_name):
    opponent_type = get_pokemon_type(opponent_name)
    your_type = get_pokemon_type(your_name)

    suggestions = []

    # Check for super effective move
    if opponent_type in type_advantages.get(your_type, []):
        suggestions.append(f"{your_name} should use a move against {opponent_name} for a super effective hit!")

    # Check for not very effective move
    if opponent_type in type_disadvantages.get(your_type, []):
        suggestions.append(f"{your_name} should avoid using moves against {opponent_name} because they're not very effective.")

    return suggestions

# This function runs your agent logic
@agent.on_interval(period=10.0)  # Run this function periodically (every 10 seconds in this case)
async def process_battle_logs(ctx: Context):
    # Assuming the battle log is generated by watch_replays.py
    log_file_path = 'battle_log.txt'
    parse_battle_log(log_file_path, ctx)
    print("Finished processing battle log.")

    # Sample HTML content for active Pokémon (this should be obtained dynamically during a battle)
    html_content = """<span class="picon has-tooltip" data-tooltip="pokemon|0|0" style="background:transparent url(https://play.pokemonshowdown.com/sprites/pokemonicons-sheet.png?v16) no-repeat scroll -160px -0px" aria-label="Charmander (active)"></span>
    <span class="picon has-tooltip" data-tooltip="pokemon|0|0" style="background:transparent url(https://play.pokemonshowdown.com/sprites/pokemonicons-sheet.png?v16) no-repeat scroll -160px -0px" aria-label="Squirtle (active)"></span>"""

    # Extract active Pokémon names from the HTML content
    opponent_name, your_name = extract_active_pokemon(html_content)

    # Get suggestions for moves based on the active Pokémon
    move_suggestions = suggest_move(opponent_name, your_name)
    print(f"Move suggestions based on active Pokémon: {move_suggestions}")

# Start the agent loop (this will keep the agent running and processing)
async def main():
    await agent.start()

# If this script is the main program, run the main function
if __name__ == "__main__":
    asyncio.run(main())