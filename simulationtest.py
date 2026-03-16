import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------
# DEFAULT CONFIG
# -----------------------------
DEFAULT_CONFIG = {
    "RANDOM_SEED": 42,
    "N_INCIDENTS": 400,
    "N_RUNS": 30,
    "INCIDENT_TYPES": ["Phishing", "Ransomware", "DDoS", "Insider", "Data_Exfil"],
    "TYPE_DIFFICULTY": {
        "Phishing": 0.30,
        "DDoS": 0.45,
        "Insider": 0.60,
        "Data_Exfil": 0.70,
        "Ransomware": 0.80,
    },
    "SEVERITIES": ["Low", "Medium", "High"],
    "SEVERITY_PROBS": [0.45, 0.35, 0.20],
    "GOV_REQUIRES_APPROVAL": {"High"},
}

# Global config variables
RANDOM_SEED = DEFAULT_CONFIG["RANDOM_SEED"]
N_INCIDENTS = DEFAULT_CONFIG["N_INCIDENTS"]
N_RUNS = DEFAULT_CONFIG["N_RUNS"]
INCIDENT_TYPES = DEFAULT_CONFIG["INCIDENT_TYPES"]
TYPE_DIFFICULTY = DEFAULT_CONFIG["TYPE_DIFFICULTY"]
SEVERITIES = DEFAULT_CONFIG["SEVERITIES"]
SEVERITY_PROBS = DEFAULT_CONFIG["SEVERITY_PROBS"]
GOV_REQUIRES_APPROVAL = DEFAULT_CONFIG["GOV_REQUIRES_APPROVAL"]

np.random.seed(RANDOM_SEED)


# -----------------------------
# SCENARIO DEFINITIONS
# -----------------------------
SCENARIOS = {
    "1": {
        "name": "Small Test",
        "description": "Quick test with 50 incidents, 5 runs",
        "N_INCIDENTS": 50,
        "N_RUNS": 5,
        "SEVERITY_PROBS": [0.60, 0.30, 0.10],
    },
    "2": {
        "name": "Standard",
        "description": "Default scenario with 400 incidents, 30 runs",
        "N_INCIDENTS": 400,
        "N_RUNS": 30,
        "SEVERITY_PROBS": [0.45, 0.35, 0.20],
    },
    "3": {
        "name": "High Severity",
        "description": "Challenging scenario with many high-severity incidents",
        "N_INCIDENTS": 400,
        "N_RUNS": 30,
        "SEVERITY_PROBS": [0.20, 0.35, 0.45],
    },
    "4": {
        "name": "Large Scale",
        "description": "Large-scale test with 1000 incidents, 50 runs",
        "N_INCIDENTS": 1000,
        "N_RUNS": 50,
        "SEVERITY_PROBS": [0.45, 0.35, 0.20],
    },
    "5": {
        "name": "Custom",
        "description": "Define your own scenario parameters",
        "custom": True,
    },
}


def display_scenarios():
    """Display available scenarios to user"""
    print("\n" + "="*60)
    print("SECURITY INCIDENT SIMULATION - SCENARIO SELECTION")
    print("="*60)
    for key, scenario in SCENARIOS.items():
        print(f"\n{key}. {scenario['name']}")
        print(f"   {scenario['description']}")
        if not scenario.get("custom"):
            print(f"   Incidents: {scenario['N_INCIDENTS']} | Runs: {scenario['N_RUNS']}")


def get_user_scenario():
    """Get scenario choice from user"""
    while True:
        display_scenarios()
        choice = input("\nSelect a scenario (1-5): ").strip()
        
        if choice in SCENARIOS:
            return choice
        else:
            print("Invalid choice. Please enter 1-5.")


def apply_scenario(scenario_key):
    """Apply selected scenario configuration"""
    global RANDOM_SEED, N_INCIDENTS, N_RUNS, SEVERITY_PROBS
    
    scenario = SCENARIOS[scenario_key]
    
    if scenario.get("custom"):
        print("\n" + "="*60)
        print("CUSTOM SCENARIO SETUP")
        print("="*60)
        
        try:
            N_INCIDENTS = int(input(f"Number of incidents (default 400): ") or 400)
            N_RUNS = int(input(f"Number of Monte Carlo runs (default 30): ") or 30)
            
            print("\nSeverity distribution (must sum to 100):")
            low = float(input("Low severity percentage (default 45): ") or 45)
            med = float(input("Medium severity percentage (default 35): ") or 35)
            high = float(input("High severity percentage (default 20): ") or 20)
            
            total = low + med + high
            if total != 100:
                print(f"Warning: Distribution sums to {total}%. Normalizing...")
            
            SEVERITY_PROBS = [low/total, med/total, high/total]
            
        except ValueError:
            print("Invalid input. Using defaults.")
            N_INCIDENTS = DEFAULT_CONFIG["N_INCIDENTS"]
            N_RUNS = DEFAULT_CONFIG["N_RUNS"]
            SEVERITY_PROBS = DEFAULT_CONFIG["SEVERITY_PROBS"]
    else:
        N_INCIDENTS = scenario["N_INCIDENTS"]
        N_RUNS = scenario["N_RUNS"]
        SEVERITY_PROBS = scenario["SEVERITY_PROBS"]
    
    np.random.seed(RANDOM_SEED)
    
    print(f"\n✓ Scenario configured:")
    print(f"  Incidents: {N_INCIDENTS}")
    print(f"  Runs: {N_RUNS}")
    print(f"  Severity: Low={SEVERITY_PROBS[0]:.1%}, Medium={SEVERITY_PROBS[1]:.1%}, High={SEVERITY_PROBS[2]:.1%}")


# -----------------------------
# INCIDENT GENERATOR
# -----------------------------
def generate_incidents(n):
    incidents = []
    for i in range(n):
        itype = np.random.choice(INCIDENT_TYPES)
        severity = np.random.choice(SEVERITIES, p=SEVERITY_PROBS)

        # complexity influenced by type
        complexity = np.clip(np.random.normal(TYPE_DIFFICULTY[itype], 0.15), 0, 1)

        incidents.append({
            "incident_id": i,
            "type": itype,
            "severity": severity,
            "complexity": complexity
        })
    return pd.DataFrame(incidents)


# -----------------------------
# AI MODEL (probabilistic)
# -----------------------------
def ai_recommendation(incident):
    """
    AI returns:
    - confidence [0..1]
    - correct (bool)
    - explanation_quality [0..1]
    """
    complexity = incident["complexity"]

    # AI performance decreases with complexity
    base_acc = 0.82
    acc = np.clip(base_acc - 0.45 * complexity, 0.35, 0.90)

    correct = np.random.rand() < acc

    # confidence is correlated with correctness and inverse complexity
    confidence = np.clip(np.random.normal(0.75 - 0.35 * complexity + (0.10 if correct else -0.15), 0.10), 0, 1)

    # explanation quality is a separate factor
    explanation_quality = np.clip(np.random.normal(0.70 - 0.25 * complexity, 0.12), 0, 1)

    return confidence, correct, explanation_quality


# -----------------------------
# HUMAN MODEL
# -----------------------------
def human_decision(incident, cognitive_load, expertise=0.70):
    """
    Returns: (correct(bool), time_cost)
    expertise [0..1]
    cognitive_load >= 0
    """
    complexity = incident["complexity"]

    # human accuracy decreases with load and complexity
    base_acc = 0.78
    acc = np.clip(base_acc + 0.18 * expertise - 0.50 * complexity - 0.12 * cognitive_load, 0.30, 0.95)
    correct = np.random.rand() < acc

    # time cost increases with complexity and load
    time_cost = np.clip(np.random.normal(8 + 18 * complexity + 4 * cognitive_load, 2.0), 2, 60)
    return correct, time_cost


# -----------------------------
# TRUST UPDATE
# -----------------------------
def update_trust(trust, ai_correct, explanation_quality):
    """
    trust in [0..1]
    trust increases if AI correct + good explanation
    decreases if wrong
    """
    if ai_correct:
        trust += 0.04 + 0.03 * explanation_quality
    else:
        trust -= 0.08
    return float(np.clip(trust, 0, 1))


# -----------------------------
# POLICY / GOVERNANCE CHECK
# -----------------------------
def requires_human_approval(severity):
    return severity in GOV_REQUIRES_APPROVAL


# -----------------------------
# SIMULATION MODES
# -----------------------------
def simulate_mode(df_incidents, mode="COLLAB"):
    """
    mode in {"HUMAN_ONLY", "AI_ONLY", "COLLAB"}
    Returns metrics dict + per-incident logs
    """
    trust = 0.55  # starting trust in AI
    cognitive_load = 0.0

    total_time = 0.0
    correct_count = 0
    policy_blocks = 0
    overrides = 0

    trust_series = []
    time_series = []

    logs = []

    for _, inc in df_incidents.iterrows():
        severity = inc["severity"]

        # cognitive load rises when incidents come in
        cognitive_load = np.clip(cognitive_load + np.random.uniform(0.00, 0.06), 0, 1)

        if mode == "HUMAN_ONLY":
            correct, t = human_decision(inc, cognitive_load)
            total_time += t
            correct_count += int(correct)

        elif mode == "AI_ONLY":
            conf, ai_correct, expq = ai_recommendation(inc)

            # Governance: AI cannot act alone on high severity
            if requires_human_approval(severity):
                policy_blocks += 1
                # AI-only fails here because no approval is possible
                # (counts as incorrect response)
                t = np.random.uniform(1, 3)
                total_time += t
            else:
                t = np.clip(np.random.normal(3 + 8 * inc["complexity"], 1.0), 1, 25)
                total_time += t
                correct_count += int(ai_correct)

            trust = update_trust(trust, ai_correct, expq)

        elif mode == "COLLAB":
            conf, ai_correct, expq = ai_recommendation(inc)

            # Decision acceptance probability depends on trust, confidence, explainability, and load
            accept_prob = (
                0.25
                + 0.35 * trust
                + 0.25 * conf
                + 0.15 * expq
                - 0.10 * cognitive_load
            )
            accept_prob = float(np.clip(accept_prob, 0.05, 0.95))
            accept_ai = (np.random.rand() < accept_prob)

            # Governance: high severity requires human approval
            if requires_human_approval(severity):
                # AI can recommend, but human must approve/execute
                human_correct, human_time = human_decision(inc, cognitive_load, expertise=0.75)

                # If human accepts AI, outcome leans towards AI correctness; otherwise human judgment
                if accept_ai:
                    # human follows AI, but still must implement => time slightly reduced
                    overrides += 0  # not overridden
                    t = max(2, human_time * 0.75)
                    outcome_correct = ai_correct
                else:
                    overrides += 1
                    t = human_time
                    outcome_correct = human_correct

                total_time += t
                correct_count += int(outcome_correct)

            else:
                # For lower severities AI can act quickly if accepted
                if accept_ai:
                    t = np.clip(np.random.normal(2.5 + 7 * inc["complexity"], 1.0), 1, 25)
                    total_time += t
                    correct_count += int(ai_correct)
                else:
                    overrides += 1
                    human_correct, human_time = human_decision(inc, cognitive_load, expertise=0.72)
                    total_time += human_time
                    correct_count += int(human_correct)

            trust = update_trust(trust, ai_correct, expq)

        else:
            raise ValueError("Unknown mode")

        # cognitive load reduces with time (more time clears queue)
        cognitive_load = np.clip(cognitive_load - (0.02 + 0.0015 * total_time / 100), 0, 1)

        trust_series.append(trust)
        time_series.append(total_time)

        logs.append({
            "severity": severity,
            "type": inc["type"],
            "complexity": inc["complexity"],
            "trust": trust,
            "cognitive_load": cognitive_load
        })

    accuracy = correct_count / len(df_incidents)
    avg_time_per_incident = total_time / len(df_incidents)

    return {
        "mode": mode,
        "accuracy": accuracy,
        "avg_time_per_incident": avg_time_per_incident,
        "total_time": total_time,
        "policy_blocks": policy_blocks,
        "overrides": overrides,
        "trust_series": trust_series,
        "time_series": time_series,
        "logs": pd.DataFrame(logs)
    }


# -----------------------------
# RUN EXPERIMENT
# -----------------------------
def run_experiment():
    results = []
    trust_curves = {"HUMAN_ONLY": [], "AI_ONLY": [], "COLLAB": []}

    for run in range(N_RUNS):
        df = generate_incidents(N_INCIDENTS)

        for mode in ["HUMAN_ONLY", "AI_ONLY", "COLLAB"]:
            sim = simulate_mode(df, mode=mode)
            results.append({
                "run": run,
                "mode": mode,
                "accuracy": sim["accuracy"],
                "avg_time_per_incident": sim["avg_time_per_incident"],
                "policy_blocks": sim["policy_blocks"],
                "overrides": sim["overrides"],
            })
            trust_curves[mode].append(sim["trust_series"])

    df_results = pd.DataFrame(results)
    return df_results, trust_curves


def plot_results(df_results, trust_curves):
    # Summary stats
    summary = df_results.groupby("mode").agg({
        "accuracy": ["mean", "std"],
        "avg_time_per_incident": ["mean", "std"],
        "policy_blocks": ["mean"],
        "overrides": ["mean"],
    })
    print("\n===== SUMMARY (Mean ± Std) =====\n")
    print(summary)

    # Accuracy bar chart
    plt.figure()
    means = df_results.groupby("mode")["accuracy"].mean()
    plt.bar(means.index, means.values)
    plt.title("Mean Accuracy by Mode")
    plt.ylabel("Accuracy")
    plt.ylim(0, 1)
    plt.xticks(rotation=15)
    plt.tight_layout()

    # Avg time bar chart
    plt.figure()
    means_t = df_results.groupby("mode")["avg_time_per_incident"].mean()
    plt.bar(means_t.index, means_t.values)
    plt.title("Mean Avg Time per Incident by Mode")
    plt.ylabel("Time (simulated units)")
    plt.xticks(rotation=15)
    plt.tight_layout()

    # Trust curve plot (only AI modes)
    plt.figure()
    for mode in ["AI_ONLY", "COLLAB"]:
        # average trust at each incident index
        curves = np.array(trust_curves[mode])
        mean_curve = curves.mean(axis=0)
        plt.plot(mean_curve, label=mode)

    plt.title("Trust Evolution Over Incidents")
    plt.xlabel("Incident Index")
    plt.ylabel("Trust (0-1)")
    plt.ylim(0, 1)
    plt.legend()
    plt.tight_layout()

    plt.show()


if __name__ == "__main__":
    # Get user scenario
    scenario_key = get_user_scenario()
    apply_scenario(scenario_key)
    
    print("\n" + "="*60)
    print("RUNNING SIMULATION...")
    print("="*60)
    
    df_results, trust_curves = run_experiment()
    plot_results(df_results, trust_curves)
    
    # Ask if user wants to run another scenario
    while True:
        again = input("\nRun another scenario? (y/n): ").strip().lower()
        if again == 'y':
            scenario_key = get_user_scenario()
            apply_scenario(scenario_key)
            print("\n" + "="*60)
            print("RUNNING SIMULATION...")
            print("="*60)
            df_results, trust_curves = run_experiment()
            plot_results(df_results, trust_curves)
        else:
            print("Exiting simulation. Goodbye!")
            break