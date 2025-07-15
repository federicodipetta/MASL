
"""
Movement utilities for agents
"""

def find_and_move_towards_agent_type(current_pos, model, target_agent_type, search_radius=3, moore=True):
    """
    Find the nearest agent of a specific type and return the best move towards it.
    
    :param current_pos: Current position tuple (x, y)
    :param model: The model instance
    :param target_agent_type: Class type to search for (e.g., TumorCell, TCell)
    :param search_radius: How far to search for targets
    :param moore: Use Moore neighborhood (8 directions) vs Von Neumann (4)
    :return: Next position tuple (x, y) or None if no target found or can't move
    """
    # Search for agents of target type in radius
    nearby_agents = model.grid.get_neighbors(
        current_pos,
        moore=moore,
        include_center=False,
        radius=search_radius
    )
    
    # Filter for target agent type
    target_agents = [agent for agent in nearby_agents 
                    if isinstance(agent, target_agent_type)]
    
    if not target_agents:
        return None  # No targets found
    
    # Find closest target
    closest_target = min(target_agents, 
                        key=lambda agent: manhattan_distance(current_pos, agent.pos))
    
    # If adjacent (distance 1), don't move
    if manhattan_distance(current_pos, closest_target.pos) == 1:
        return None  # Already adjacent, don't move
    
    # Calculate and return best move towards target
    return calculate_best_move_towards(current_pos, closest_target.pos, model, moore)

def calculate_best_move_towards(current_pos, target_pos, model, moore=True):
    """
    Calculate the best next position to move towards a target.
    
    :param current_pos: Current position tuple (x, y)
    :param target_pos: Target position tuple (x, y)
    :param model: The model instance
    :param moore: Use Moore neighborhood (8 directions) vs Von Neumann (4)
    :return: Best next position tuple (x, y) or None if can't move
    """
    possible_positions = model.grid.get_neighborhood(
        current_pos,
        moore=moore,
        include_center=False
    )
    
    # Filter only empty positions
    empty_positions = [pos for pos in possible_positions 
                      if model.grid.is_cell_empty(pos)]
    
    if not empty_positions:
        return None  # Can't move anywhere
    
    # Find position that minimizes distance to target
    best_position = min(empty_positions, 
                       key=lambda pos: manhattan_distance(pos, target_pos))
    
    return best_position

def get_random_empty_neighbor(current_pos, model, moore=True):
    """
    Get a random empty neighboring position.
    """
    possible_positions = model.grid.get_neighborhood(
        current_pos,
        moore=moore,
        include_center=False
    )
    
    empty_positions = [pos for pos in possible_positions 
                      if model.grid.is_cell_empty(pos)]
    
    if empty_positions:
        return model.random.choice(empty_positions)
    return None

def manhattan_distance(pos1, pos2):
    """
    Calculate the Manhattan distance between two positions.
    
    :param pos1: First position tuple (x, y)
    :param pos2: Second position tuple (x, y)
    :return: Manhattan distance as an integer
    """
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])