import math
import mesa
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from agents import ICI, TCell, TumorCell, TReg, Androgens

class RCCModel(mesa.Model):
    """
    Model class representing the immune system simulation.
    """
    def __init__(self,
            width=150,
            height=150, 
            sex: str = "male", 
            nICI: int = 2,
            nTCell: int = 373,
            nTReg: int = 0,
            nAndrogens: int = 371,
            nTumorCells: int = 394,
            seed: float | None = None,
            p_TReg_add: float = 0.24287156301254542,
            TCell_exhaustion_Tumor: float = 0.04001731201879627,
            TCell_exhaustion_TReg: float = 0.16934907608400246,
            TCell_exhaustion_Androgens: float = 0.1666884991199096,
            TCell_activation_ICI: float = 0.15767026596715517,
            p_TumorCell_add: float = 0.031642094522462534,
            ICI_exhaustion: float = 0.5098813436502578
        ):
        """
        Initialize the model with a grid of specified dimensions.

        :param width: Width of the grid.
        :param height: Height of the grid.
        """
        super().__init__(seed=seed)
        self.last_tcell_count_step = None

        self.space = MultiGrid(width, height, torus=True)
        self.grid = self.space
        self.width = width
        self.height = height
        self.sex = sex
        self.search_radius = 3  # Radius for searching agents

        self.p_TReg_add = p_TReg_add
        self.TCell_exhaustion_Tumor = TCell_exhaustion_Tumor
        self.TCell_exhaustion_TReg = TCell_exhaustion_TReg
        self.TCell_exhaustion_Androgens = TCell_exhaustion_Androgens
        self.TCell_activation_ICI = TCell_activation_ICI
        self.p_TumorCell_add = p_TumorCell_add
        self.ICI_exhaustion = ICI_exhaustion
        # Create T cells
        for _ in range(nTCell):
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            tcell = TCell(self)
            self.grid.place_agent(tcell, (x, y))

        for _ in range(nTReg if sex == 'male' else int(nTReg + nTReg * 0.1)):
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            treg = TReg(self)
            self.grid.place_agent(treg, (x, y))
        for i in range(nAndrogens + 4 if self.sex == "male" else nAndrogens):
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            androgen = Androgens(self)
            self.grid.place_agent(androgen, (x, y))

        for _ in range(nICI):
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            icer = ICI(self)
            self.grid.place_agent(icer, (x, y))
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
                "Dead": lambda m: not m.is_patient_alive(),
                "Tumor Defeated": lambda m: len(m.agents.select(agent_type=TumorCell)) == 0,
                "Step": lambda m: m.steps
            },
            agent_reporters={
                "Exhaustion": lambda a: getattr(a, 'exhaustion', 0) if isinstance(a, TCell) else None,
                "State": lambda a: getattr(a, 'state', None),
                "Type": lambda a: type(a).__name__,
            }
        )

        self.running = True
        self.datacollector.collect(self)


    def run_model(self, max_steps=2000):
        """
        Run the model until patient dies, tumor is defeated, or max steps reached.
        
        :param max_steps: Maximum number of steps to run
        """
        
        while (self.running and 
            self.is_patient_alive() and 
            len(self.agents.select(agent_type=TumorCell)) > 0 and
            self.steps < max_steps):
            self.step()
        
        # Set running to False when simulation ends
        self.running = False
        
        # Optional: log why the simulation ended
        if not self.is_patient_alive():
            print(f"Simulation ended: Patient died at step {self.steps}")
        elif len(self.agents.select(agent_type=TumorCell)) == 0:
            print(f"Simulation ended: Tumor defeated at step {self.steps}")
        elif self.steps >= max_steps:
            print(f"Simulation ended: Max steps ({max_steps}) reached")
                

    def step(self):
        """
        Perform a step in the model, updating all agents.
        """
        super().step()
        self.agents.do("step")
        
        self._add_TReg()

        self.datacollector.collect(self)
        
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
        TCells_active = [agent for agent in TCells]
        exhaustions = [agent.exhaustion for agent in TCells_active]
        mean_exhaustion = sum(exhaustions) / len(exhaustions) if exhaustions else 0
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
                prob = min(prob * 2, 1)
            if prob < 0.01:
                prob = 0.01
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
        self.deregister_agent(agent)
        self.grid.remove_agent(agent)

    def get_tumor_coverage_percentage(self):
        """
        Calculate the percentage of grid cells occupied by tumor cells.
        """
        tumor_cells = self.agents.select(agent_type=TumorCell)
        total_cells = self.width * self.height
        return len(tumor_cells) / total_cells * 100

    def is_patient_alive(self, death_threshold=40):
        """
        Check if patient is still alive based on tumor coverage.
        
        :param death_threshold: Percentage of tumor coverage that causes death
        :return: True if patient is alive, False otherwise
        """
        n_tcells = len(self.agents.select(agent_type=TCell, filter_func=lambda a: a.state == "active"))
        if n_tcells and self.last_tcell_count_step is None:
            self.last_tcell_count_step = self.steps
        elif n_tcells > 0:
            self.last_tcell_count_step = None
        
        if self.last_tcell_count_step is not None and self.steps - (self.last_tcell_count_step or 0) > 100:
            return False
        
        return self.get_tumor_coverage_percentage() < death_threshold
        
    
      