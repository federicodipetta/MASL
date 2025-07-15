
import mesa
from . import agents_utils as au
from .T_cell import TCell
class ICI(mesa.Agent):
    """
    ICI class representing an immune checkpoint inhibitor agent in the immune system simulation.
    """
    def __init__(self, model: mesa.Model):
        """
        Initialize an ICI agent.

        :param model: The model this agent belongs to.
        """
        super().__init__(model)
        self.type = "ICI"
        self.state = "active"
    
    def step(self):
        """
        Perform the step for the ICI agent.
        """
        # Example behavior: ICI agents can enhance T cell activity
        self._enhance_T_cells()

    def _enhance_T_cells(self):
        """
        Enhance nearby T cells by reducing their exhaustion level.
        """
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=True)
        TCells = [agent for agent in neighbors if isinstance(agent, TCell)]
        
        for tcell in TCells:
            if tcell.state == "exhausted":
                tcell.exhaustion -= 0.1  # Reduce exhaustion level
                if tcell.exhaustion < 0:
                    tcell.exhaustion = 0

    def move(self):
        """
        Move the ICI agent randomly within the model space.
        """
        next_pos = au.find_and_move_towards_agent_type(
            self.pos, 
            self.model, 
            TCell, 
            self.model.search_radius,
            moore=True
        )
        if next_pos:
            self.model.grid.move_agent(self, next_pos)  
        else:
            random_move = au.get_random_empty_neighbor(self.pos, self.model, moore=True)
            if random_move:
                self.model.grid.move_agent(self, random_move)