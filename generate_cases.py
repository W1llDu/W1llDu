"""
Objective: To generate the `case[1-5].txt` files for:

case1: <200 writes
case2: 100 operations, check if one can successfully read the value they write
case3: 100 operations, check if deletes actually delete a value
case4: 500 operations, check if kvstore still works properly when inserts more keys than 200 (the current limit)
case5: 1K increment operations to a single key, check correctness by something like running 500 +1 and 500 -1, which should end up with 0  
case6: 1K operations, check if the state numbers are correct.
"""

import string
import random

ALPHABET = list(string.ascii_letters)
KEY_LEN_BOUNDS = (5, 30) # inclusive
# INT_BOUNDS = (-sys.maxsize - 1, sys.maxsize)  # inclusive
INT_BOUNDS = (-(2**10), (2**10))
SET_OF_GENERATED_KEYS = set(["reserved"])
NUM_THREADS = 4
# a buffer between commands that should be happening sequentially
BUFFER_OPS = (NUM_THREADS*5)*["W,reserved,0"] 

random.seed(12345)

def main():
    fmap = {
        "case1": generate_case_1(),
        "case2": generate_case_2(),
        "case3": generate_case_3(),
        "case4": generate_case_4(),
        "case5": generate_case_5(),
        "case6": generate_case_6(),
    }
    for fname, loi in fmap.items():
        with open(f"{fname}.txt", 'w') as f:
            f.write("\n".join(loi))

def generate_case_1() -> list[str]:
    ops = []
    for _ in range(150):
        ops.append(f"W,{get_unique_key()},{rand_num()}")
    return ops


def generate_case_2() -> list[str]:
    ops = []
    keys = []
    for _ in range(50):
        key = get_unique_key()
        ops.append(f"W,{key},{rand_num()}")
        keys.append(key)
    ops.extend(BUFFER_OPS)
    for key in keys:
        ops.append(f"R,{key}")
    return ops

def generate_case_3() -> list[str]:
    ops = []
    keys = [get_unique_key() for _ in range(30)]
    for key in keys:
        ops.append(f"W,{key},0")
    ops.extend(BUFFER_OPS)
    for key in keys:
        ops.append(f"D,{key}")          # delete once
        if random.choice([True, False]): 
            ops.append(f"D,{key}")      # Randomly attempt to delete twice (second delete fails)
    return ops

def generate_case_4() -> list[str]:
    ops = []
    for _ in range(500):
        ops.append(f"W,{get_unique_key()},{rand_num()}")
    return ops


def generate_case_5() -> list[str]:
    ops = []
    key = get_unique_key()
    initial_num = 500
    ops.append(f"W,{key},{initial_num}")
    ops.extend(BUFFER_OPS)
    inc_ops = 500*[f"I,{key},1"] + 500*[f"I,{key},-1"]
    random.shuffle(inc_ops)
    ops.extend(inc_ops)
    ops.extend(BUFFER_OPS)
    ops.append(f"R,{key}")
    return ops

def generate_case_6() -> list[str]:
    ops = []
    keys = []

    def rand_key():
        if 0 < len(keys) and random.choice([True, False]):
            return random.choice(keys)
        else:
            return get_unique_key()

    for _ in range(1_000):
        opid = random.choice(['R','W','I','D'])
        if opid == 'R':
            ops.append(f"R,{rand_key()}")
        elif opid == 'W':
            new_key = rand_key()
            if new_key not in keys:
                keys.append(new_key)
            ops.append(f"W,{new_key},{rand_num()}")
        elif opid == 'I':
            ops.append(f"I,{rand_key()},{rand_num()}")
        elif opid == 'D':
            key = rand_key()
            #   Lets keep the key in the keys[] list so that we also test insert, 
            #   write, and read logic on deleted keys
            # if key in keys:
            #     keys.remove(key)
            ops.append(f"D,{key}")
    return ops

def get_unique_key(length_range=KEY_LEN_BOUNDS) -> str:
    for _ in range(10_000):
        n = random.randint(length_range[0], length_range[1])
        new_key = "".join(random.choice(ALPHABET) for _ in range(n))
        if new_key not in SET_OF_GENERATED_KEYS:
            SET_OF_GENERATED_KEYS.add(new_key)
            return new_key
    raise RuntimeError("Unique Key Timeout: Please report this error to the professors.")

def rand_num(bounds=INT_BOUNDS) -> int:
    return random.randint(bounds[0], bounds[1])

if __name__ == "__main__":
    main()
