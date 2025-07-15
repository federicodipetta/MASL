import mesa
from . import agents_utils as au
from .T_cell import TCell
class Androgens(mesa.Agent):
    """
    Androgens class representing androgen agents in the immune system simulation.
    """
    def __init__(self, model: mesa.Model):
        """
        Initialize an androgen agent.

        :param model: The model this agent belongs to.
        """
        super().__init__(model)
        self.type = "Androgen"
        self.exhaustion = 0.0  
        self.state = "active"

    def step(self):
        """
        Perform the step for the androgen agent.
        """
        # Androgens move randomly and can exhaust T cells
        self._move_randomly()
        self._exhaust_T_cells()

    def _move_randomly(self):
        """
        Move the androgen agent randomly within the model space.
        """
        possible_positions = self.model.grid.get_neighborhood(
            self.pos, 
            moore=True, 
            include_center=False
        )
        
        if possible_positions:
            new_pos = self.random.choice(possible_positions)
            self.model.grid.move_agent(self, new_pos)
    
    def _exhaust_T_cells(self):
        """
        Exhaust nearby T cells by increasing their exhaustion level.
        """
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=True)
        TCells: list[TCell] = [agent for agent in neighbors if isinstance(agent, TCell)]
        
        for tcell in TCells:
            tcell.receive_attack(attacker="Androgen")


    def _increase_exhaustion(self):
        self.exhaustion += 0.1
        if self.exhaustion >= 1.0:
            self.state = "exhausted"
        self.exhaustion = min(self.exhaustion, 1.0) 

    
        

                