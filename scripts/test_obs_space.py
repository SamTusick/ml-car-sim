import numpy as np
from car_sim.env import CarEnv
from car_sim.car import SENSOR_ANGLES

N_STEPS = 500


def main():
    env = CarEnv()

    # 1: reset and inspect the observation
    # Expected (written down before running):
    #   shape  (6,)      -> 5 rays + 1 velocity
    #   dtype  float32
    #   min    0.0       -> velocity is 0 at spawn (and rays are never negative)
    #   max    <= 1.0    -> rays are distance / MAX_SENSOR_DIST, velocity is vel / max_vel
    obs, info = env.reset(seed=0)
    print("expected: shape=(6,) dtype=float32 min=0.0 max=1.0")
    print(f"actual:   shape={obs.shape} dtype={obs.dtype} min={obs.min()} max={obs.max()}")
    assert obs.shape == (len(SENSOR_ANGLES) + 1,)
    assert obs.dtype == np.float32

    # 2: random steps must always stay inside the observation space
    obs, info = env.reset(seed=0)
    resets = 0
    for i in range(N_STEPS):
        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)
        assert env.observation_space.contains(obs), (
            f"step {i}: obs outside observation_space: {obs} (dtype={obs.dtype}, shape={obs.shape})"
        )
        if terminated or truncated:
            resets += 1
            obs, info = env.reset()
            assert env.observation_space.contains(obs), f"reset obs outside space: {obs}"
    print(f"{N_STEPS} random steps OK ({resets} episode resets)")

    # 3: spawn observation
    # Velocity is 0.0 because PlayerCar starts with vel = 0 and reset() applies no
    # action, so nothing has accelerated the car yet. The last obs entry is vel / max_vel.
    obs, info = env.reset()
    print("spawn obs (rays at -60, -30, 0, +30, +60 deg, then velocity):")
    print(obs)
    
    assert obs[-1] == 0.0, f"expected spawn velocity 0.0, got {obs[-1]}"

    env.close()


if __name__ == "__main__":
    main()
