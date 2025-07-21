import mesa

from .T_cell import TCell
from . import agents_utils as au
class TReg(mesa.Agent):

    def __init__(self, model):
        super().__init__(model)
        self.type = "TReg"
        self.state = "active"
        
    def step(self):
        if (not hasattr(self, 'pos')):
            return
        # moves to TCell
        self._move_to_TCell()

        # Attack TCell
        self._attack_TCell()

    def _move_to_TCell(self):
        new_pos = au.find_and_move_towards_agent_type(
            self.pos,
            self.model,
            TCell,
            self.model.search_radius
        )
        if new_pos:
            self.model.grid.move_agent(self, new_pos)
        
    def _attack_TCell(self):
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=True)
        neighbors_TCell = [n for n in neighbors if isinstance(n, TCell)]
        if neighbors_TCell:
            target: TCell = self.model.random.choice(neighbors_TCell)
            target.receive_attack(attacker="TReg")

        
