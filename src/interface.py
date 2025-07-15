import mesa
import mesa.agent
import mesa.visualization
import solara

from mesa.visualization import SolaraViz, make_space_altair, make_plot_component

from model import RCCModel
from agents import TCell, TumorCell, TReg, Androgens, ICI

model_params = {
    "width": {
        "type": "SliderInt",
        "value": 50,
        "label": "Grid Width",
        "min": 10,
        "max": 200,
        "step": 1,
    },
    "height": {
        "type": "SliderInt", 
        "value": 50,
        "label": "Grid Height",
        "min": 10,
        "max": 200,
        "step": 1,
    },
    "sex": {
        "type": "Select", 
        "value": "male",
        "label": "Sex",
        "values": ["male", "female"]
    },
    "ICI": {
        "type": "SliderInt",
        "value": 0,
        "label": "ICI Agents",
        "min": 0,
        "max": 100,
        "step": 1,
    },
    "nTCell": {
        "type": "SliderInt",
        "value": 12,
        "label": "Number of T Cells",
        "min": 1,
        "max": 1000,
        "step": 1,
    },
    "nTReg": {
        "type": "SliderInt",
        "value": 2,
        "label": "Number of T Regulatory Cells",
        "min": 0,
        "max": 20,
        "step": 1,
    },
    "nAndrogens": {
        "type": "SliderInt",
        "value": 2,
        "label": "Number of Androgens",
        "min": 0,
        "max": 500,
        "step": 1,
    },
    "nTumorCells": {
        "type": "SliderInt",
        "value": 8,
        "label": "Number of Tumor Cells",
        "min": 1,
        "max": 1000,
        "step": 1,
    },
    "seed": {
        "type": "SliderFloat",
        "value": 42,
        "label": "Random Seed",
        "min": 0,
        "max": 1000,
        "step": 1,
    }
}

def agent_portrayal(agent: mesa.Agent) -> dict:
    """
    Function to extract parameters from an agent for visualization.
    
    :param agent: The agent from which to extract parameters.
    :return: A dictionary of parameters.
    """
    potrayal = {
        "color": "blue",
        "size": 5,
    }
    
    if isinstance(agent, TCell):
        if agent.state == "exhausted":
            potrayal["color"] = "gray"  
            potrayal["size"] = 1     
        elif hasattr(agent, 'exhaustion'):
            exhaustion_level = agent.exhaustion
            
            if exhaustion_level >= 0.8:
                potrayal["color"] = "#FF6B6B"  # light red - almost exhausted
            elif exhaustion_level >= 0.6:
                potrayal["color"] = "#FFE66D"  # light yellow - tired
            elif exhaustion_level >= 0.4:
                potrayal["color"] = "#4ECDC4"  # light teal - moderately active
            elif exhaustion_level >= 0.2:
                potrayal["color"] = "#45B7D1"  # light blue - moderately active
            else:
                potrayal["color"] = "#96CEB4"  # light green - very active
        else:
            potrayal["color"] = "green" 
        
        potrayal["size"] = 2
            
    elif isinstance(agent, TumorCell):
        potrayal["color"] = "red"
        potrayal["size"] = 2.3

    elif isinstance(agent, TReg):
        potrayal["color"] = "purple"
        potrayal["size"] = 2.5
        
    elif isinstance(agent, Androgens):
        potrayal["color"] = "orange"
        potrayal["size"] = 2.0
    elif isinstance(agent, ICI):
        potrayal["color"] = "pink"
        potrayal["size"] = 2.0

    return potrayal

@solara.component
def Page() -> SolaraViz:
    """
    Solara component to visualize the immune system model.
    """
    SpaceGraph = make_space_altair(agent_portrayal)

    AgentCountPlot = make_plot_component(
        ["T Cells", "Active T Cells", "Exhausted T Cells", "Tumor Cells", "T Regulatory Cells", "Androgens"]
    )
    
    ExhaustionPlot = make_plot_component(
        ["Average T Cell Exhaustion"]
    )

    model = RCCModel(
        width=model_params["width"]["value"],
        height=model_params["height"]["value"],
        sex=model_params["sex"]["value"],
        ICI=model_params["ICI"]["value"],
        nTCell=model_params["nTCell"]["value"],
        nTReg=model_params["nTReg"]["value"],
        nAndrogens=model_params["nAndrogens"]["value"],
        nTumorCells=model_params["nTumorCells"]["value"],
        seed=model_params["seed"]["value"]
    )
    solara_viz = SolaraViz(
        model,
        components=[SpaceGraph, AgentCountPlot, ExhaustionPlot],
        model_params=model_params,
        name="RCC",
    )
    return solara_viz

