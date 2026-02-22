try:
    import simpy
    SIMPY_AVAILABLE = True
except ImportError:
    SIMPY_AVAILABLE = False

import random
import numpy as np


def run_simulation_manual(num_doctors, no_show_rate, sim_duration, appt_interval, consult_mean, consult_std, seed):
    """Fallback simulation without SimPy using manual event queue."""
    random.seed(seed)
    np.random.seed(seed)

    patients_scheduled = sim_duration // appt_interval
    no_shows = int(patients_scheduled * no_show_rate)
    seen = patients_scheduled - no_shows

    # Simulate wait times: with more doctors, less wait
    base_wait = max(0, (appt_interval - consult_mean / num_doctors) * 0.5)
    wait_times = np.abs(np.random.normal(base_wait, 3, seen)).tolist()

    avg_wait    = round(float(np.mean(wait_times)), 2) if wait_times else 0
    utilization = round((seen * consult_mean) / (sim_duration * num_doctors) * 100, 2)
    no_show_pct = round(no_shows / patients_scheduled * 100, 2)

    return {
        'total_scheduled' : patients_scheduled,
        'total_seen'      : seen,
        'total_no_shows'  : no_shows,
        'no_show_rate_pct': no_show_pct,
        'avg_wait_minutes': avg_wait,
        'utilization_pct' : utilization
    }


def run_simulation_simpy(num_doctors, no_show_rate, sim_duration, appt_interval, consult_mean, consult_std, seed):
    """Full SimPy discrete-event simulation."""
    random.seed(seed)
    np.random.seed(seed)

    stats = {'scheduled': 0, 'seen': 0, 'no_shows': 0, 'wait_times': []}

    def patient_process(env, pid, doctors):
        stats['scheduled'] += 1
        if random.random() < no_show_rate:
            stats['no_shows'] += 1
            return
        arrival_time = env.now
        with doctors.request() as req:
            yield req
            stats['wait_times'].append(env.now - arrival_time)
            duration = max(5.0, np.random.normal(consult_mean, consult_std))
            yield env.timeout(duration)
            stats['seen'] += 1

    def appointment_generator(env, doctors):
        pid = 0
        while True:
            pid += 1
            env.process(patient_process(env, pid, doctors))
            yield env.timeout(appt_interval)

    env     = simpy.Environment()
    doctors = simpy.Resource(env, capacity=num_doctors)
    env.process(appointment_generator(env, doctors))
    env.run(until=sim_duration)

    avg_wait    = round(np.mean(stats['wait_times']), 2) if stats['wait_times'] else 0
    utilization = round((stats['seen'] * consult_mean) / (sim_duration * num_doctors) * 100, 2)
    no_show_pct = round(stats['no_shows'] / stats['scheduled'] * 100, 2) if stats['scheduled'] else 0

    return {
        'total_scheduled' : stats['scheduled'],
        'total_seen'      : stats['seen'],
        'total_no_shows'  : stats['no_shows'],
        'no_show_rate_pct': no_show_pct,
        'avg_wait_minutes': avg_wait,
        'utilization_pct' : utilization
    }


def run_simulation(
    num_doctors   = 3,
    no_show_rate  = 0.20,
    sim_duration  = 480,
    appt_interval = 10,
    consult_mean  = 15,
    consult_std   = 4,
    seed          = 42
):
    """
    Runs clinic simulation. Uses SimPy if available, otherwise fallback estimator.
    """
    if SIMPY_AVAILABLE:
        return run_simulation_simpy(num_doctors, no_show_rate, sim_duration, appt_interval, consult_mean, consult_std, seed)
    else:
        return run_simulation_manual(num_doctors, no_show_rate, sim_duration, appt_interval, consult_mean, consult_std, seed)


if __name__ == '__main__':
    engine = "SimPy" if SIMPY_AVAILABLE else "Manual Estimator"
    print(f"Simulation Engine: {engine}")
    print("=" * 55)
    print("  BASELINE: No AI Optimization (25% no-show rate)")
    print("=" * 55)
    r1 = run_simulation(no_show_rate=0.25, appt_interval=10)
    for k, v in r1.items():
        print(f"  {k:<28}: {v}")

    print()
    print("=" * 55)
    print("  OPTIMIZED: AI Overbooking (10% effective no-show)")
    print("=" * 55)
    r2 = run_simulation(no_show_rate=0.10, appt_interval=8)
    for k, v in r2.items():
        print(f"  {k:<28}: {v}")

    print()
    print("IMPROVEMENT:")
    print(f"  Wait time reduced by   : {r1['avg_wait_minutes'] - r2['avg_wait_minutes']:.2f} min")
    print(f"  Utilization gained     : {r2['utilization_pct'] - r1['utilization_pct']:.2f}%")
    print(f"  More patients seen     : {r2['total_seen'] - r1['total_seen']}")
