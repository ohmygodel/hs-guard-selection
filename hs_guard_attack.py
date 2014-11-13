import random
import math

def check_for_compromise(sample_expiration_times, cur_time, adv_position,
    surveillance_time):
    """Checks if adversary in adv_position has surveillance_time left in each previous node
    before they expire. If so, the HS is compromised via repeated surveillance."""
    if (adv_position == 0):
        return True
    else:
        if (sample_expiration_times[adv_position-1] >=\
            cur_time + surveillance_time):
            return check_for_compromise(sample_expiration_times,
                cur_time + surveillance_time, adv_position-1, surveillance_time)
        else:
            return False


def simulate_guard_attacks(num_samples, node_expiration_times, num_guards, surveillance_time,
    adv_relay_probs, simulation_length):
    """Simulates HS compromise via guard surveillance or adversarial relay selection.
    Returns list of simulated times until compromise, where inf indicates no compromise."""
    compromise_times = []
    for sample in xrange(num_samples):
        if (sample % 1000 == 0):
            print('{} of {} samples finished.'.format(sample, num_samples))
        sample_expiration_times = [0]*len(node_expiration_times)
        compromise_time = float('inf')
        for cur_time in xrange(simulation_length):
            for i in xrange(len(sample_expiration_times)):
                if (sample_expiration_times[i] <= cur_time):
                    # relays expired, choose new ones
                    sample_expiration_times[i] = cur_time + node_expiration_times[i]
                    # check if surveillance toward the client would succeed
                    if (check_for_compromise(sample_expiration_times, cur_time, i,
                        surveillance_time)):
                        # check in any of the new relays are adversarial
                        for j in xrange(num_guards[i]):
                            p = random.random()
                            if (p <= adv_relay_probs[i]):
                                compromise_time = cur_time
                                break                            
                    if (compromise_time != float('inf')):
                        break
            # handle direct observation of last relay by RP
            if (compromise_time == float('inf')) and\
                (check_for_compromise(sample_expiration_times, cur_time,
                len(sample_expiration_times), surveillance_time)):
                compromise_time = cur_time
            if (compromise_time != float('inf')):
                break
        compromise_times.append(compromise_time)
    return compromise_times

def print_compromise_time_stats(compromise_times, simulation_length):
    compromise_times_sorted = sorted(compromise_times)
    try:
        first_uncomp_sample = compromise_times_sorted.index(float('inf'))
        prob_compromise = float(first_uncomp_sample) / len(compromise_times_sorted)
    except ValueError:
        prob_compromise = 1
    print('Probability of compromise over {} days: {}'.format(simulation_length/24.0,
        prob_compromise))
    print('Min time to compromise: {} days'.format(compromise_times_sorted[0]/24.0))
    print('Median time to compromise: {} days'.format(\
        compromise_times_sorted[(len(compromise_times_sorted)-1)/2]/24.0))
    print('Mean time tompromise: {} days'.format(\
        sum(compromise_times)/len(compromise_times)/24.0))
    print('Max time to compromise: {} days'.format(compromise_times_sorted[-1]/24.0))

num_samples = 10000
node_expiration_times = [90*24, 90*24, 12] # node expirations in order from HS (in hours)
surveillance_time = 1*24 # time for adversary to accomplish surveillance (in hours)
adv_relay_probs = [0.05, 0.01, 0.01] # node probability in each position, ordered from HS
num_guards = [1, 3, 3]
prob_compromise_during_simulation = 0.99999 # allowed prob of uncompromised sample (affects sim len)
simulation_length = min(node_expiration_times) *\
    int(math.ceil(math.log(1-prob_compromise_during_simulation) / math.log(1-min(adv_relay_probs))))
compromise_times = simulate_guard_attacks(num_samples, node_expiration_times, num_guards,
    surveillance_time, adv_relay_probs, simulation_length)
print_compromise_time_stats(compromise_times, simulation_length)