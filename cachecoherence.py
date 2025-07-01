# -*- coding: utf-8 -*-

from collections import defaultdict

# Start with all caches in Invalid state
def start_state():
    return {'P1': 'I', 'P2': 'I', 'P3': 'I', 'P4': 'I'}

# MESI protocol logic
def mesi_step(cache, proc, op, bus_activity):
    other_procs = [p for p in cache if p != proc]
    current = cache[proc]
    any_shared = False
    for p in other_procs:
        if cache[p] != 'I':
            any_shared = True
            break

    if op == 'read':
        if current == 'I':
            bus_activity['BusRd'] += 1
            if any_shared:
                cache[proc] = 'S'
                for p in other_procs:
                    if cache[p] == 'E':
                        cache[p] = 'S'
            else:
                cache[proc] = 'E'

    elif op == 'write':
        if current == 'M':
            return
        elif current == 'E':
            cache[proc] = 'M'
        elif current == 'S':
            bus_activity['BusUpgr'] += 1
            cache[proc] = 'M'
            for p in other_procs:
                if cache[p] == 'S':
                    cache[p] = 'I'
        elif current == 'I':
            bus_activity['BusRdX'] += 1
            cache[proc] = 'M'
            for p in other_procs:
                if cache[p] != 'I':
                    cache[p] = 'I'

# Dragon logic
def dragon_step(cache, proc, op, bus_activity):
    other_procs = [p for p in cache if p != proc]
    current = cache[proc]
    found_shared = False
    for p in other_procs:
        if cache[p] in ['Sc', 'Sm', 'E', 'M']:
            found_shared = True
            break

    if op == 'read':
        if current == 'I':
            bus_activity['BusRd'] += 1
            if found_shared:
                cache[proc] = 'Sc'
            else:
                cache[proc] = 'E'

    elif op == 'write':
        if current == 'M':
            return
        elif current == 'E':
            cache[proc] = 'M'
        elif current in ['Sc', 'Sm']:
            bus_activity['BusUpdate'] += 1
            cache[proc] = 'Sm'
        elif current == 'I':
            bus_activity['BusRd'] += 1
            if found_shared:
                bus_activity['BusUpdate'] += 1
                cache[proc] = 'Sm'
            else:
                cache[proc] = 'M'

# Main logic
def run_simulation(input_file):
    mesi_cache = start_state()
    dragon_cache = start_state()
    mesi_bus = defaultdict(int)
    dragon_bus = defaultdict(int)

    try:
        f = open(input_file, 'r')
        lines = f.readlines()
        f.close()
    except:
        print("Input file not found!")
        return

    for entry in lines:
        entry = entry.strip()
        if entry == '':
            continue
        parts = entry.split()
        if len(parts) != 2:
            continue
        p, action = parts[0], parts[1].lower()

        mesi_step(mesi_cache, p, action, mesi_bus)
        dragon_step(dragon_cache, p, action, dragon_bus)

    print("\n--- MESI Protocol Bus Activity ---")
    for item in mesi_bus:
        print(item, ":", mesi_bus[item])

    print("\n--- Dragon Protocol Bus Activity ---")
    for item in dragon_bus:
        print(item, ":", dragon_bus[item])

run_simulation("cache_coherence_sequence_2_10000 (1).txt")
