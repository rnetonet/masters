fixations_times_starts = [1,2702,3055,3271,3514,3728,4037,4435,4989,5219,5567,5864,6157]
fixations_times_ends = [2643,3005,3221,3471,3685,3996,4400,4938,5176,5523,5819,6119,6198]

fixations_times = []
for start, end in zip(fixations_times_starts, fixations_times_ends):
    period = list(range(start, end + 1))
    fixations_times.extend(period)
fixations_times = set(sorted(fixations_times))