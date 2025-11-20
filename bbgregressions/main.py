import os 

os.makedirs(output_dir, exist_ok = True)

# read data
os.makedirs(os.path.join(output_dir, "input"), exist_ok = True)
readers()

# regressions

# plot