import optuna
from optuna.samplers import TPESampler
from model import RCCModel
def objective_optuna(trial):
    """
    Objective function for Optuna optimization.
    """
    target_survival_time = 1024
    
    # Define parameter space - Optuna gestisce automaticamente i tipi
    width = 150
    height = 150
    nTCell = trial.suggest_int('nTCell', 100, 500)
    nTumorCells = trial.suggest_int('nTumorCells', 200, 400)
    nTReg = trial.suggest_int('nTReg', 0, 20)
    nAndrogens = trial.suggest_int('nAndrogens', 0, 500)
    nICI = trial.suggest_int('nICI', 0, 100)

    p_TReg_add = trial.suggest_float('p_TReg_add', 0.01, 1.0)
    TCell_exhaustion_Tumor = trial.suggest_float('TCell_exhaustion_Tumor', 0.01, 1.0)
    TCell_exhaustion_TReg = trial.suggest_float('TCell_exhaustion_TReg', 0.01, 1.0)
    TCell_exhaustion_Androgens = trial.suggest_float('TCell_exhaustion_Androgens', 0.01, 1.0)
    TCell_activation_ICI = trial.suggest_float('TCell_activation_ICI', 0.01, 1.0)
    p_TumorCell_add = trial.suggest_float('p_TumorCell_add', 0.01, 1.0)
    ICI_exhaustion = trial.suggest_float('ICI_exhaustion', 0.01, 1.0)
    
    # Create and run model
    model = RCCModel(
        width=width,
        height=height,
        nTCell=nTCell,
        nTumorCells=nTumorCells,
        nTReg=nTReg,
        nAndrogens=nAndrogens,
        nICI=5,
        p_TReg_add=p_TReg_add,
        TCell_exhaustion_Tumor=TCell_exhaustion_Tumor,
        TCell_exhaustion_TReg=TCell_exhaustion_TReg,
        TCell_exhaustion_Androgens=TCell_exhaustion_Androgens,
        TCell_activation_ICI=TCell_activation_ICI,
        p_TumorCell_add=p_TumorCell_add,
        ICI_exhaustion=ICI_exhaustion,
        seed=42
    )
    
    model.run_model(max_steps=1500)
    
    # Get survival time
    data = model.datacollector.get_model_vars_dataframe()
    survival_time = data['Step'].iloc[-1] if not data.empty and 'Step' in data.columns else 0
    
    deviation = abs(target_survival_time - survival_time)
    
    # Optuna minimizza automaticamente
    return deviation

def optimize_with_optuna():
    """
    Optimize using Optuna.
    """
    study = optuna.create_study(
        study_name='rcc_optimization',
        storage='sqlite:///optuna_study.db',
        load_if_exists=True,  
        direction='minimize',
        sampler=optuna.samplers.TPESampler(seed=42),
        
    )
    
    study.optimize(objective_optuna, n_trials=100, show_progress_bar=True, n_jobs=2)

    print("Best trial:")
    print(f"Objective value: {study.best_value}")
    print("Best params:")
    for key, value in study.best_params.items():
        print(f"  {key}: {value}")
    
    return study.best_params

if __name__ == '__main__':
    best_params = optimize_with_optuna()