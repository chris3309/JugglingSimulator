import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# ----- Global Parameters -----
T_beat = 0.5          # time per beat (seconds)
g = 9.8               # gravitational acceleration (m/s^2)
throw_delay = 0.25
    # delay after scheduled throw time before releasing the ball

# Hand positions: right hand at (1,0) and left hand at (-1,0)
hand_positions = {"R": np.array([1.0, 0.0]), "L": np.array([-1.0, 0.0])}

# ----- Ball Class -----
class Ball:
    def __init__(self, ball_id, next_throw_time, hand):
        self.ball_id = ball_id
        self.next_throw_time = next_throw_time  # scheduled time for the next throw
        self.hand = hand                        # current hand ("R" or "L")
        self.state = "in_hand"                  # state: "in_hand" or "in_air"
        self.pos = hand_positions[hand].copy()  # current position
        # Attributes used during a throw:
        self.start_time = None
        self.flight_time = None
        self.catch_time = None
        self.start_pos = None
        self.vx = None
        self.vy = None
        self.dest_hand = None

    def throw(self, current_time, siteswap, period):
        """
        Initiate the throw of the ball.
        The throw value is determined by the beat corresponding to the scheduled throw time.
        The flight time is throw_value * T_beat.
        """
        # Determine beat using the scheduled throw time (not the delayed release)
        beat = int(round(self.next_throw_time / T_beat))
        throw_value = siteswap[beat % period]
        #print(f"Ball ID: {self.ball_id},  Throw Val: {throw_value}")
        self.flight_time = throw_value * T_beat
        self.catch_time = current_time + self.flight_time

        # The ball is thrown from the current hand's position:
        source_hand = self.hand
        source_pos = hand_positions[source_hand]
        # For odd throw values, the ball goes to the opposite hand; even throws stay in the same hand.
        if throw_value % 2 == 1:
            dest_hand = "L" if source_hand == "R" else "R"
        else:
            dest_hand = source_hand
        dest_pos = hand_positions[dest_hand]
        self.dest_hand = dest_hand

        # Compute projectile parameters:
        self.start_time = current_time
        self.start_pos = source_pos.copy()
        self.vx = (dest_pos[0] - source_pos[0]) / self.flight_time
        # To have the ball return to y = 0, we require:
        # 0 = vy*T - 0.5*g*T^2  ->  vy = 0.5*g*T
        self.vy = 0.5 * g * self.flight_time

        # Change state to in_air
        self.state = "in_air"
        # (Optional: print throw details for debugging)
        # print(f"Ball {self.ball_id} thrown from {source_hand} to {dest_hand} at time {current_time:.2f} with flight time {self.flight_time:.2f}")

    def update(self, current_time, siteswap, period):
        """Update the ball's position based on its current state."""
        if self.state == "in_air":
            t = current_time - self.start_time
            if t < self.flight_time:
                # Projectile motion equations:
                x = self.start_pos[0] + self.vx * t
                y = self.start_pos[1] + self.vy * t - 0.5 * g * t**2
                self.pos = np.array([x, y])
            else:
                # Ball is caught: update hand and state.
                self.state = "in_hand"
                self.hand = self.dest_hand
                self.pos = hand_positions[self.hand].copy()
                # Set the next scheduled throw time to the catch time.
                self.next_throw_time = self.catch_time
        elif self.state == "in_hand":
            # Delay the release slightly to ensure a ball remains visible in the hand.
            if current_time >= self.next_throw_time + throw_delay:
                self.throw(current_time, siteswap, period)
            else:
                # Remain at the hand's position.
                self.pos = hand_positions[self.hand].copy()

# ----- Main Program: Get Siteswap and Initialize Balls -----
siteswap_input = input("Enter a siteswap pattern (e.g., 333): ")
# Convert the string to a list of integers (ignoring non-digits)
siteswap = [int(ch) for ch in siteswap_input if ch.isdigit()]
period = len(siteswap)
# The average of the throw values equals the number of balls in play.
num_balls = int(sum(siteswap) / period)

# Create balls with staggered initial throw times.
balls = []
for i in range(num_balls):
    # Alternate starting hands: right hand for even-indexed balls, left for odd-indexed.
    hand = "R" if (i % 2 == 0) else "L"
    # Schedule initial throw times as multiples of T_beat.
    ball = Ball(ball_id=i, next_throw_time=i * T_beat, hand=hand)
    balls.append(ball)

# ----- Set Up Matplotlib Animation -----
fig, ax = plt.subplots(figsize=(6, 6))
ax.set_xlim(-2.5, 2.5)
ax.set_ylim(-0.5, 10)
ax.set_aspect('equal')
ax.set_title(f"Juggling Pattern: {siteswap_input}")
ax.set_xlabel("X")
ax.set_ylabel("Y")

# Plot static hand markers
hand_marker_style = dict(color='black', marker='s', markersize=10)
ax.plot(hand_positions["L"][0], hand_positions["L"][1], **hand_marker_style)
ax.plot(hand_positions["R"][0], hand_positions["R"][1], **hand_marker_style)

# Define a list of colors for the balls
colors = ['blue', 'red', 'green', 'orange', 'purple', 'cyan']

# Create circle patches for the balls, each with a different color.
ball_markers = []
for i in range(num_balls):
    color = colors[i % len(colors)]
    marker = plt.Circle((0, 0), 0.1, color=color, zorder=5)
    ball_markers.append(marker)
    ax.add_patch(marker)

sim_time = 0.0  # global simulation time
dt = 0.02       # time step (seconds)

def update_frame(frame):
    global sim_time
    sim_time += dt
    # Update each ball and its corresponding marker.
    for ball, marker in zip(balls, ball_markers):
        ball.update(sim_time, siteswap, period)
        marker.center = ball.pos
    return ball_markers

ani = FuncAnimation(fig, update_frame, interval=dt * 1000, blit=True)
plt.show()
