import math
import mesa
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from agents import TCell, TumorCell, TReg, Androgens

class RCCModel(mesa.Model):
    """
    Model class representing the immune system simulation.
    """
    def __init__(self,
            width=20,
            height=20, 
            sex: str = "male", 
            ICI: int = 0,
            nTCell: int = 12,
            nTReg: int = 2,
            nAndrogens: int = 2,
            nTumorCells: int = 8,
            seed: float | None = None
        ):
        """
        Initialize the model with a grid of specified dimensions.

        :param width: Width of the grid.
        :param height: Height of the grid.
        """
        super().__init__(seed=seed)
        self.space = MultiGrid(width, height, torus=True)
        self.grid = self.space
        self.width = width
        self.height = height
        self.sex = sex
        self.search_radius = 3  # Radius for searching agents

        # Create T cells
        for i in range(nTCell):
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            tcell = TCell(self)
            self.grid.place_agent(tcell, (x, y))

        for i in range(nTReg):
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            treg = TReg(self)
            self.grid.place_agent(treg, (x, y))
        for i in range(nAndrogens + 4 if self.sex == "male" else nAndrogens):
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            androgen = Androgens(self)
            self.grid.place_agent(androgen, (x, y))
        # Create tumor cells
        self._create_tumor_mass(num_cells=nTumorCells)
        self.datacollector = DataCollector(
            model_reporters={
                "T Cells": lambda m: len([a for a in m.space.agents if isinstance(a, TCell)]),
                "Active T Cells": lambda m: len([a for a in m.space.agents if isinstance(a, TCell) and a.state == "active"]),
                "Exhausted T Cells": lambda m: len([a for a in m.space.agents if isinstance(a, TCell) and a.state == "exhausted"]),
                "Tumor Cells": lambda m: len([a for a in m.space.agents if isinstance(a, TumorCell)]),
                "T Regulatory Cells": lambda m: len([a for a in m.space.agents if isinstance(a, TReg)]),
                "Androgens": lambda m: len([a for a in m.space.agents if isinstance(a, Androgens)]),
                "Average T Cell Exhaustion": lambda m: sum([a.exhaustion for a in m.space.agents if isinstance(a, TCell)]) / max(1, len([a for a in m.space.agents if isinstance(a, TCell)])),
            },
            agent_reporters={
                "Exhaustion": lambda a: getattr(a, 'exhaustion', 0) if isinstance(a, TCell) else None,
                "State": lambda a: getattr(a, 'state', None),
                "Type": lambda a: type(a).__name__,
            }
        )  

    def step(self):
        """
        Perform a step in the model, updating all agents.
        """
        self.datacollector.collect(self)

        self.agents.do("step")
        
        self._add_TReg()
        

    def _create_tumor_mass(self, num_cells=5):
        """
        Create a mass of tumor cells at a random position on the grid.
        of n cells are all placed between 
        """
        x = self.random.randrange(self.width)
        y = self.random.randrange(self.height)
        for _ in range(num_cells):
            tumor_cell = TumorCell(self)
            self.grid.place_agent(tumor_cell, (x, y))
            # Randomly spread the tumor cells around the initial position
            x_offset = self.random.choice([-1, 0, 1])
            y_offset = self.random.choice([-1, 0, 1])
            new_pos = (x + x_offset, y + y_offset)
            new_pos = (new_pos[0] % self.width, new_pos[1] % self.height)
            if self.grid.is_cell_empty(new_pos):
                self.grid.move_agent(tumor_cell, new_pos)
            (x, y) = new_pos

    def _add_TReg(self):
        """
        Add TReg agents based on the number of exhaustion of TCells.
        """
        TCells = self.agents.select(agent_type=TCell)
        TCells_active = [agent for agent in TCells if agent.state == "active"]
        exhaustions = [agent.exhaustion for agent in TCells_active]
        mean_exhaustion = sum(exhaustions) / len(exhaustions) if exhaustions else 0
        # Tregs grow based on the average exhaustion of TCells
        # When the mean is high, TRegs are less likely to spawn
        num_TReg = 10 - int(mean_exhaustion * 10)
        if num_TReg < 0:
            num_TReg = 0
        max_treg = len(TCells) if self.sex == "female" else len(TCells) // 1.3
        base_prob = 0.05
        TRegs_num = len(self.agents.select(agent_type=TReg))
        if TRegs_num > max_treg:
            num_TReg = 0
        
        for _ in range(num_TReg):
            prob = base_prob * (1 / (1 + math.exp((mean_exhaustion - 0.5) * 5)))
            # If female, the immune system is more active
            # so the probability of spawning TReg is increased
            if self.sex == "female":
                prob = min(prob * 1.5, 1)
            if prob < 0.01:
                prob = 0.01
            print(f"{self.sex}: Adding TReg with probability: {prob}")
            if self.random.random() < prob:
                x = self.random.randrange(self.width)
                y = self.random.randrange(self.height)
                treg = TReg(self)
                self.grid.place_agent(treg, (x, y))
                TRegs_num += 1

    def _add_androgens(self):
        """
        Add androgen agents based on sex and blood vessel density.
        """
        prob = self.get_blood_vessles_density()
        if self.sex == 'male':
            prob *= 1.5
        else:
            prob *= 0.5
        if self.random.random() < prob:
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            androgen = Androgens(self)
            self.grid.place_agent(androgen, (x, y))

    def _add_TCells(self):
        """
        Based on the number of active TCells and Blood Vessels, add TCells.
        """
        blood_vessles_density = self.get_blood_vessles_density()
        if blood_vessles_density > 0.1:  # Threshold for adding T
            num_TCells = int(blood_vessles_density * 5)
            for _ in range(num_TCells):
                x = self.random.randrange(self.width)
                y = self.random.randrange(self.height)
                tcell = TCell(self)
                self.grid.place_agent(tcell, (x, y))

    def get_blood_vessles_density(self):
        """
        Get the density of blood vessels in the model.
        """
        # Blood vessles is calculated with number of tumor cells
        tumor_cells = self.agents.select(agent_type=TumorCell)
        if tumor_cells:
            return len(tumor_cells) / (self.width * self.height)
        else:
            return 0.0
    
    def remove_agent(self, agent: mesa.Agent):
        """
        Remove an agent from the model and the grid.
        
        :param agent: The agent to remove.
        """
        self.grid.remove_agent(agent)
        self.agents.remove(agent)
        
    
      