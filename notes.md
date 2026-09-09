# Building a Self-Driving car sim from scratch using Neural Networks and Genetic Algorithms.

With no help from AI tools. No machine learning libraries or LLM help. I got this idea when I discovered CommonLuke on Youtube who did something similar where he created his own model and put it against models made by Claude, ChatGPT, and Gemini. I dont want to compete against other models like that, instead I want to build this one from scratch and then build one with ML libraries and maybe eventually compare different algorithm metrics.

Just trying to learn as much as I can

## Inital Plan (No research)

1. Create game env.
2. Create neural network to start learning
3. Begin training model
4. Test model on brand new env.

## Creating Game Envirnoment

- Creating using Pygame. I found this is the most commonly used and seems the most staright forward.
- Need to integrate 360 degree physics instead of just 2-D so we can get realistic car mechanics. Right now moving right moves the car right directly instead of 'steering' right.

### Moving the object 360 deg

We want the car to act like a real car, so it should only be able to move forward(gas) and make turns using the left and right movement. Instead of when changing the x coordinate moving the whole object directly that direction we want to pair it with the forward movement to create a 'turn'.
