
import mesa

class TumorCell(mesa.Agent):
    """
    TumorCell class representing a tumor cell in the immune system.
    """
    def __init__(self, model: mesa.Model):
        """
        Initialize a tumor cell agent.

        :param model: The model this agent belongs to.
        """
        super().__init__(model)
        self.type = "TumorCell"
        self.state = "active"
    
    def step(self):
        """
        Perform the step for the tumor cell agent.
        """
        # Example behavior: Tumor cells can proliferate over time
        if self.state == "active":
            self.proliferate()


    def proliferate(self):
        """
        Tumor cells can proliferate, creating new tumor cells.
        """
        # Find empty neighboring cells
        possible_positions = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
        empty_positions = []
        
        for pos in possible_positions:
            if self.model.grid.is_cell_empty(pos):
                empty_positions.append(pos)
        
        # Create new tumor cell if there's space
        # It can proliferate with a probability of 0.1
        if empty_positions and self.model.random.random() < 0.05:
            new_pos = self.model.random.choice(empty_positions)
            new_tumor_cell = TumorCell(self.model)
            self.model.grid.place_agent(new_tumor_cell, new_pos)

    def receive_attack(self):
        """
        Handle an attack on the tumor cell.
        """
        self.state = "dead"
        self.model.remove_agent(self)
