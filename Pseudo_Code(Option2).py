for volume in volumes:
    state = check_snapmirror_state(volume)
    lag = check_transfer_lag(volume)
    snapshot = check_last_snapshot(volume)

    if state == "healthy" and lag < 15min and snapshot == "success":
        status = "Green"
    elif lag < 60min:
        status = "Amber"
    else:
        status = "Red"

output_dashboard(status_per_volume)

if any Red:
    decision = "No-Go"
else:
    decision = "Go"
