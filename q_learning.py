import random
import pickle
from collections import defaultdict
from env_2048 import Game2048Env, ACTIONS, encode_state

def epsilon_greedy(Q, state, epsilon, env):
    """Choose action using epsilon greedy."""
    if random.random() < epsilon:
        # optionally filter only valid actions
        valid_actions = env.get_valid_actions()
        if len(valid_actions) == 0:
            return random.choice(ACTIONS)
        return random.choice(valid_actions)

    # exploit best Q value
    q_vals = Q[state]
    max_q = max(q_vals)
    best_actions = [a for a, q in enumerate(q_vals) if q == max_q]
    return random.choice(best_actions)

def train_q_learning(
    num_episodes=50000,
    alpha=0.1,
    gamma=0.99,
    epsilon_start=1.0,
    epsilon_min=0.1,
    epsilon_decay=0.9999,
    report_every=500
):
    env = Game2048Env()
    Q = defaultdict(lambda: [0.0 for _ in ACTIONS])

    epsilon = epsilon_start
    scores = []

    for episode in range(num_episodes):
        state = env.reset()
        done = False
        episode_reward = 0

        while not done:
            action = epsilon_greedy(Q, state, epsilon, env)

            next_state, reward, done = env.step(action)
            episode_reward += reward

            # Q learning update:
            # Q[s][a] = Q[s][a] + alpha * (reward + gamma * max_a' Q[s'][a'] - Q[s][a])
            best_next_q = 0.0 if done else max(Q[next_state])
            td_target = reward + gamma * best_next_q
            td_error = td_target - Q[state][action]
            Q[state][action] += alpha * td_error

            state = next_state

        # decay epsilon
        if epsilon > epsilon_min:
            epsilon *= epsilon_decay

        scores.append(episode_reward)

        if (episode + 1) % report_every == 0:
            avg_reward = sum(scores[-report_every:]) / report_every
            print(f"Episode {episode+1}: avg reward {avg_reward:.2f}, epsilon {epsilon:.3f}")

    return Q

if __name__ == "__main__":
    Q = train_q_learning()

    with open("q_table.pkl", "wb") as f:
        pickle.dump(dict(Q), f)

    print("Saved Q table to q_table.pkl")
