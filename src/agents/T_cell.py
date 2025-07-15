import mesa

from .tumor_cell import TumorCell
from . import agents_utils as au

class TCell(mesa.Agent):
    """
    TCell class representing a T cell in the immune system.
    """
    def __init__(self, model: mesa.Model):
        """
        Initialize a T cell agent.

        :param model: The model this agent belongs to.
        """
        super().__init__(model)
        self.type = "TCell"
        self.state = "active"
        self.exhaustion = 0.0
        
        

    def step(self):
        """
        Perform the step for the T cell agent.
        """
        # Example behavior: T cells can become exhausted over time
        if self.state == "active":
            self._move_to_tumor()
            self.attack()
        elif self.state == "exhausted":
            #When exhausted it stay incative until Androgen or ICI activate it
            pass

    def attack(self):
        """
        T cells can attack tumor cells.
        """
        # Find neighboring tumor cells
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=True)
        tumor_cells = [agent for agent in neighbors if isinstance(agent, TumorCell)]
        # Attack the first tumor cell found
        if tumor_cells:
            target = self.model.random.choice(tumor_cells)
            target.receive_attack()
            # add exhaustion to T cell, influenced by androgen or ICI
            self.exhaustion += 0.1 

    def receive_attack(self, attacker: str = "TReg"):
        """
        Handle receiving an attack from TReg or Androgen.
        """
        if attacker == "TReg":
            self.exhaustion += 0.2
        elif attacker == "Androgen":
            self.exhaustion += 0.4
        
        self.exhaustion = min(self.exhaustion, 1.0)  # Cap exhaustion at 1.0    
        if self.exhaustion >= 1:
            self.state = "exhausted"
        else:
            self.state = "active"
        
    
    def _move_to_tumor(self):
        """
        Move towards the nearest tumor cell.
        """
        # Find neighboring tumor cells
        next_pos = au.find_and_move_towards_agent_type(
            self.pos, 
            self.model, 
            TumorCell, 
            self.model.search_radius,
            moore=True
        )
        if next_pos:
            self.model.grid.move_agent(self, next_pos)  
        else:
            random_move = au.get_random_empty_neighbor(self.pos, self.model, moore=True)
            if random_move:
                self.model.grid.move_agent(self, random_move)

    def ICI_activation(self):
        """
        Activate T cell by ICI, reducing exhaustion.
        """
        self.exhaustion -= 0.2
        if self.exhaustion < 0:
            self.exhaustion = 0
        if self.exhaustion < 1.0:
            self.state = "active"