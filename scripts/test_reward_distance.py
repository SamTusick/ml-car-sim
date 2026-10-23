import math
from car_sim.env import CarEnv, Actions, DISTANCE_REWARD, STEPS_REWARD
from car_sim.track import cp1_cord, cp2_cord, cp3_cord, cp4_cord, cp5_cord, FINISH_CENTER

N_ACCEL_STEPS = 50
MAX_FOLLOW_STEPS = 3000
GATES = [cp1_cord, cp2_cord, cp3_cord, cp4_cord, cp5_cord]


def hand_distance(env):
    """Distance from the car's center to the current target, computed without env helpers."""
    car = env.car
    cx = car.x + car.img.get_width() / 2
    cy = car.y + car.img.get_height() / 2
    tx, ty = GATES[env.next_gate] if env.next_gate < len(GATES) else FINISH_CENTER
    return math.sqrt((tx - cx) ** 2 + (ty - cy) ** 2)


def check_distance(env, info, label):
    expected = hand_distance(env)
    assert math.isclose(info["distance_to_next_gate"], expected, abs_tol=1e-9), (
        f"{label}: info={info['distance_to_next_gate']} hand={expected} next_gate={env.next_gate}"
    )


# Hand-picked centerline (clockwise from the start); the gate/finish centroids are on it.
# Only used to drive the car; the distance assertions do not depend on it.
WAYPOINTS = [
    (60, 500), (60, 250), (90, 170), (148, 121), (240, 105), (242, 200), (240, 290), (300, 290),
    (360, 230), (400, 150), (445, 116), (520, 80), (620, 60), (720, 75), (800, 70), (845, 130),
    (848, 250), (900, 290), (966, 221), (1000, 120), (1050, 80), (1110, 85), (1160, 150),
    (1170, 300), (1170, 450), (1140, 540), (1050, 560), (964, 560), (900, 590), (830, 630),
    (780, 615), (735, 540), (730, 490), (650, 470), (560, 490), (500, 540), (440, 570),
    (411, 605), (330, 640), (250, 610), (150, 640), (54, 640), (54, 620),
]
WAYPOINT_RADIUS = 35


def steer_action(env, state):
    """Follow WAYPOINTS: turn toward the next one, coasting through sharp turns."""
    car = env.car
    cx, cy = car.get_center()
    while state["i"] < len(WAYPOINTS) - 1 and math.hypot(WAYPOINTS[state["i"]][0] - cx,
                                                         WAYPOINTS[state["i"]][1] - cy) < WAYPOINT_RADIUS:
        state["i"] += 1
    tx, ty = WAYPOINTS[state["i"]]
    # heading vector is (-sin a, -cos a), so a = atan2(-dx, -dy)
    want = math.degrees(math.atan2(-(tx - cx), -(ty - cy)))
    diff = (want - car.angle + 180) % 360 - 180
    slow = abs(diff) > 25 and car.vel > 1.5
    if diff > 4:
        return Actions.COAST_LEFT.value if slow else Actions.ACCELERATE_LEFT.value
    if diff < -4:
        return Actions.COAST_RIGHT.value if slow else Actions.ACCELERATE_RIGHT.value
    return Actions.ACCELERATE.value


def main():
    env = CarEnv()

    # 1: ACCELERATE for 50 steps, print the reward each step
    # Expected (written down before running): reward ~= DISTANCE_REWARD * (progress toward gate 1) - 0.01.
    # Speed ramps 0.1 -> 3.0 (+0.1/step), so reward should grow with speed, not sit flat at -0.01.
    # (The env rewards distance closed toward the gate, so it equals DISTANCE_REWARD * speed only
    # while driving straight at the gate.)
    env.reset(seed=0)
    print(f"--- {N_ACCEL_STEPS} x ACCELERATE (DISTANCE_REWARD={DISTANCE_REWARD}, STEPS_REWARD={STEPS_REWARD}) ---")
    print("step  speed   reward      DR*speed-0.01  gate dist")
    for i in range(1, N_ACCEL_STEPS + 1):
        _, reward, terminated, truncated, info = env.step(Actions.ACCELERATE.value)
        speed = env.car.vel
        print(f"{i:>4}  {speed:5.2f}  {reward:10.4f}  {DISTANCE_REWARD * speed - STEPS_REWARD:12.4f}  "
              f"{info['distance_to_next_gate']:9.2f}")
        check_distance(env, info, f"accelerate step {i}")
        if terminated or truncated:
            print(f"episode ended at step {i} (terminated={terminated}, truncated={truncated})")
            break

    # 2: assert distance_to_next_gate against a hand computation every step, past the 5th gate
    env.reset(seed=0)
    check_distance(env, env._get_info(), "reset")
    checked = 0
    max_gate = 0
    state = {"i": 0}
    for i in range(1, MAX_FOLLOW_STEPS + 1):
        prev_gate = env.next_gate
        _, reward, terminated, truncated, info = env.step(steer_action(env, state))
        check_distance(env, info, f"follow step {i}")
        checked += 1
        if env.next_gate != prev_gate:
            print(f"step {i}: gate {prev_gate + 1} passed, next target distance {info['distance_to_next_gate']:.2f}")
        max_gate = max(max_gate, env.next_gate)
        if terminated or truncated:
            print(f"episode ended at step {i}: terminated={terminated} truncated={truncated} "
                  f"finished={info['finished']} gates_passed={info['gates_passed']}")
            break
    print(f"{checked} steps asserted, max gates passed = {max_gate}")
    assert max_gate >= len(GATES), f"never got past the 5th gate (max_gate={max_gate})"
    print("distance assertions OK, including after the 5th gate (target = finish line)")

    env.close()


if __name__ == "__main__":
    main()
