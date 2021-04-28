

def find_min(BV_times):
    min_time = 2856594574       # Time on 9th July, 2060 at 3:30pm
    min_time_idx = 0

    for i in range(len(BV_times)):
        if BV_times[i] == 0:
            pass
        else:
            if BV_times[i] < min_time:
                min_time = BV_times[i]
                min_time_idx = i
    return min_time_idx