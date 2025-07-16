"""
Test code for testint ghe RCCModel and its agents.
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from model import RCCModel  
from agents import TCell, TumorCell, TReg, Androgens, ICI

class TestBasicRCCModel:

    def test_rcc_model(self):
        """
        Test the RCCModel initialization and basic functionality.
        """
        model = RCCModel(
            width=10,
            height=10,
            sex="male",
            nICI=0
        )

        assert model.width == 10
        assert model.height == 10
        assert len(model.agents.select(agent_type=ICI)) == 0

    def test_add_TReg(self):
        """
        Test the addition of TReg agents based on exhaustion.
        """
        model = RCCModel(
            width=10,
            height=10,
            sex="male",
            nICI=0
        )
        initial_TRegs = len(model.agents.select(agent_type=TReg))
        model._add_TReg()
        TRegs = model.agents.select(agent_type=TReg)
        assert len(TRegs) >= initial_TRegs
        for treg in TRegs:
            assert isinstance(treg, TReg)
            assert model.grid.is_cell_empty(treg.pos) is False

    def test_blood_vessel_density(self):
        """
        Test the blood vessel density calculation.
        """
        model = RCCModel(
            width=10,
            height=10
        )
        density = model.get_blood_vessles_density()
        assert 0 <= density <= 1, "Blood vessel density should be between 0 and 1"


class TestScenario:
    def test_more_TumorCells_than_TCells(self):
        """
        Test the scenario where there are more TumorCells than TCells.
        """
        model = RCCModel(
            width=10,
            height=10,
            sex="male",
            nTReg=0,
            nTCell=1,
            nTumorCells=11,
            nICI=0
        )

        assert len(model.agents.select(agent_type=TumorCell)) > len(model.agents.select(agent_type=TCell)), \
            "There should be more TumorCells than TCells in this scenario."

        for _ in range(10):
            model.step()
        
        assert len(model.agents.select(agent_type=TumorCell)) > 0, \
            "There should still be TumorCells present after several steps."
        assert len(model.agents.select(agent_type=TCell)) > 0, \
            "There should still be TCells present after several steps."
        assert len([t for t in model.agents.select(agent_type=TCell) if t.exhaustion > 0]) >= 0, \
            "TCell should be exhousted."
        
    def test_more_TCells_than_TumorCells(self):
        """
        Test the scenario where there are more TCells than TumorCells.
        """
        model = RCCModel(
            width=10,
            height=10,
            nTCell=90,
            nTumorCells=2,
        )

        assert len(model.agents.select(agent_type=TCell)) > len(model.agents.select(agent_type=TumorCell)), \
            "There should be more TCells than TumorCells in this scenario."
        for _ in range(100):
            model.step()
        for t in model.agents.select(agent_type=TumorCell):
            print(f"TumorCell at position {t.pos} with state {t.state}")
        assert len(model.agents.select(agent_type=TumorCell)) == 0, \
            "All TumorCells should be eliminated by TCells in this scenario."
        
    def test_sex_influence(self):
        """
        Test the influence of sex on the model.
        """
        model_male = RCCModel(
            width=15,
            height=15,
            nTCell=5,
            nTumorCells=50,
            nICI=12,
            sex="male",
            seed=42
        )     

        model_female = RCCModel(
            width=15,
            height=15,
            nTCell=5,
            nTumorCells=50,
            nICI=12,
            sex="female",
            seed=42
        )

        for _ in range(100):
            model_male.step()
            model_female.step()

        # Test if there are differences in the models
        assert len(model_male.agents.select(agent_type=TCell)) == len(model_female.agents.select(agent_type=TCell)), \
            "The number of TCells should be the same in both models."
        assert len(model_male.agents.select(agent_type=TReg)) < len(model_female.agents.select(agent_type=TReg)), \
            "The number of TReg agents should differ between"
        assert len(model_female.agents.select(agent_type=TumorCell)) < len(model_male.agents.select(agent_type=TumorCell)), \
            "There should be more TumorCells in the female model."
        
        print (len(model_female.agents.select(agent_type=TumorCell)))
        print (len(model_male.agents.select(agent_type=TumorCell)))

