import time

time.sleep(1.50315)
one = time.perf_counter()
time.sleep(0.001)
two = time.perf_counter()

print(one, two)
