from uagents import Agent, Context  # Assuming this is the correct import for your agent setup

# Constants for reward values (can be adjusted)
REWARDS = {
    'win': 10.0,
    'kill': 5.0,
    'status': 3.0,
    'damage': 0.1  # Per 1% of damage dealt
}

# Dictionary to track battle state and rewards
battle_state = {
    'won': False,
    'killed_pkmn': 0,
    'status_inflicted': 0,
    'damage_done': 0.0
}

total_rewards = 0.0  # Track total rewards earned

# Function to handle adding rewards manually
def add_reward(amount):
    global total_rewards
    total_rewards += amount
    print(f"Reward of {amount} added. Total rewards: {total_rewards}")

# Function to parse the battle log and update battle state
def parse_battle_log(file_path, ctx: Context):
    global battle_state

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

    except FileNotFoundError:
        print(f"File {file_path} not found.")
    except Exception as e:
        print(f"An error occurred while parsing the log: {e}")

# Define your agent
agent = Agent(name="pokemon_agent")  # Removed agent_id as it's not supported

# This function runs your agent logic
@agent.on_interval(period=10.0)  # Run this function periodically (every 10 seconds in this case)
async def process_battle_logs(ctx: Context):
    # Assuming the battle log is generated by watch_replays.py
    log_file_path = 'battle_log.txt'
    parse_battle_log(log_file_path, ctx)
    print("Finished processing battle log.")

# Starting the agent
if __name__ == "__main__":
    agent.run()