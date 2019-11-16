fixations_times_starts = [1,2297,2800,3030,3249,3612,3707,3888,4086,4500]
fixations_times_ends = [2251,2743,2974,3193,3567,3676,3833,4043,4473,4698]

fixations_times = []
for start, end in zip(fixations_times_starts, fixations_times_ends):
    period = list(range(start, end + 1))
    fixations_times.extend(period)
fixations_times = set(sorted(fixations_times))