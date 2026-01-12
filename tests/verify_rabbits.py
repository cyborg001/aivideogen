
import pandas as pd

def simulate_rabbits(months, maturity, lifespan):
    """
    Simulates rabbit population growth where:
    - maturity: months until a pair becomes fertile (1 means fertile at month 1)
    - lifespan: total months a pair lives before dying
    """
    # births[m] = number of pairs born in month m
    births = [0] * (months + 1)
    births[1] = 1 # Initial pair
    
    population = [0] * (months + 1)
    
    for m in range(1, months + 1):
        # Current population = sum of active births
        # A pair born at 'b' is alive in month 'm' if b <= m < b + lifespan
        alive = 0
        for b in range(1, m + 1):
            if b <= m < b + lifespan:
                alive += births[b]
        population[m] = alive
        
        # Calculate births for NEXT month (m+1)
        # A pair born at 'b' reproduces if month m >= b + maturity - 1
        # AND it is still alive (m < b + lifespan)
        if m + 1 <= months:
            new_births = 0
            for b in range(1, m + 1):
                if m >= b + maturity - 1 and m < b + lifespan:
                    new_births += births[b]
            births[m+1] = new_births
            
    return population[1:]

def recurrence_formula(months, f, d):
    """
    Calculates population based on the formula:
    P(n) = P(n-1) + P(n-f) - P(n-d-1)
    """
    p = [0] * (months + 1)
    p[1] = 1 # Month 1
    # Standard Fibonacci-like start before deaths kick in
    for n in range(2, months + 1):
        term1 = p[n-1]
        term2 = p[n-f] if n-f >= 1 else (1 if n-f == 0 else 0)
        term3 = p[n-d-1] if n-d-1 >= 1 else 0
        
        # Correction for the first pair that dies
        if n == d + 1:
            term3 = 1
            
        p[n] = term1 + term2 - term3
    return p[1:]

if __name__ == "__main__":
    n = 20
    f = 2 # Normal maturity
    d = 4 # Lifespan of 4 months
    
    sim = simulate_rabbits(n, f, d)
    rec = recurrence_formula(n, f, d)
    
    print(f"--- Verification (f={f}, d={d}) ---")
    print("Month | Simulation | Recurrence | Match?")
    print("-" * 40)
    for i in range(n):
        match = "✅" if sim[i] == rec[i] else "❌"
        print(f"{i+1:5} | {sim[i]:10} | {rec[i]:10} | {match}")
