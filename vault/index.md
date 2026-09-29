# Index

Personal wiki of my coding-class projects. Start with a project, follow its topic links,
and use each note's **Sources** list to open the original README section it came from.

## Projects

*What I built*

- [[Custom LLM]]: This project involves training a custom Large Language Model (LLM) from scratch using a small word-token corpus and extending its knowledge base through targeted corpus additions.
- [[Networking Tracker]]: A small, secure contacts tracker for keeping up with your professional network: create, view, edit, delete, sort, and filter contacts, each visible only to the account that created it.
- [[Pac-Man DQN]]: This project trains a Deep Q-Network (DQN) agent to play Ms. Pac-Man using a convolutional network.

## Concepts

*Ideas and techniques*

- [[Corpus Extension]]: The process involved iteratively adding eight distinct categories of text to the original corpus to improve the model's performance on specific evaluation tasks.
- [[Deep Q-Network]]: The agent uses a convolutional DQN that processes four stacked game screens to infer motion and select the best joystick move.
- [[Experience Replay]]: The agent learns from a replay buffer, which stores past experiences to stabilize learning.
- [[Learning Rate]]: The learning rate was set to 0.0001, matching the reference Adam learning rate for the classroom-scale setup.
- [[Model Evaluation]]: The agent's performance is measured by the raw, unclipped game score across five fixed evaluation seeds. Shared by [[Pac-Man DQN]], [[Custom LLM]].
- [[Model Training]]: The training process used the nanoGPT architecture with specific hyperparameters like learning rate and training steps to build the model.
- [[Node Backend Architecture]]: A Node backend is used to perform trusted, non-bypassable validation steps before forwarding requests to the Data API.
- [[Row Level Security]]: Postgres Row Level Security enforces cross-user data access control for all CRUD operations.
- [[Token Embeddings]]: The model's internal representation of words is stored in 64-number vectors that are updated during training.

## Tools

*Software and services*

- [[Neon Postgres]]: Neon Postgres is used as the database, utilizing Row Level Security for authorization boundaries.
- [[Vercel Deployment]]: The project is deployed as a single Vercel project using static build and serverless functions.

## Original sources

*Unchanged copies in `raw/`. These are the evidence the wiki is built from.*

- [[Networking Tracker README]]: original of [[Networking Tracker]] (from `Assignment1/README.md`)
- [[Pac-Man DQN README]]: original of [[Pac-Man DQN]] (from `pacman-dqn/README.md`)
- [[Custom LLM README]]: original of [[Custom LLM]] (from `Assignment 3/custom-llm/README.md`)
