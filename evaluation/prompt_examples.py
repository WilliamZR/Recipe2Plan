from collections import defaultdict

def get_prompt_example(agent, level, oracle = True):
    key = 'oracle' if oracle else 'dynamic'
    if agent == 'end2end':
        return recipe_descriptions['oracle'][level] + end2end_examples[level]
    elif agent == 'react':
        return recipe_descriptions['dynamic'][level] + react_examples['oracle'][level]
    elif agent == 'plan_solve':
        return recipe_descriptions[key][level] + plan_solve_examples[level]
    elif agent == 'complete_react':
        return recipe_descriptions['oracle_complete'][level] + react_examples['oracle_complete'][level]
    elif agent == 'single_recipe':
        return recipe_descriptions['single_recipe'][level] + react_examples['single_recipe'][level]



prompt_examples = {}

recipe_descriptions = defaultdict(dict)

react_examples = defaultdict(dict)

recipe_descriptions['oracle']['easy'] = '''## Recipe 1:Baked-Potato
Step 0 (10 min): Preheat the oven to 425 degrees.
Step 1 (2 min): Pierce the potato several times with a fork.
Step 2 (5 min): Bake the potato in the preheated oven.
Step 3 (1 min): Melt butter in the microwave.
Step 4 (10 min): Remove potato from the oven and use a sharp knife to make decorative cuts on the top of the potato.
Step 5 (1 min): Pour melted butter over the potato and serve.

- You can minimize the execution time based on the following properties:
You can perform autonomous actions step 0, 2, 3 in parallel with other actions to speed up the process.
You can execute part of the action duration to pause steps 1, 4 for more efficient multitasking. But other actions must be finished without interruption.

- Do not violate any following constraints when executing this recipe:
The action before the arrow must be completed before the action after the arrow can be started: 0->2, 1->2, 2->4, 3->5, 4->5
The following actions would occupy the corresponding physical objects. You can not perform the action if the object is occupied. The property such as volume and temperature of the object should also match the requirement of the recipe: Steps 0, 2 requires oven, Steps 3 requires microwave

## Recipe 2:Cheese-Sandwich
Step 0 (10 min): Preheat the oven to 425 degrees.
Step 1 (2 min): Butter one side of two slices of bread.
Step 2 (1 min): Place a slice of cheese between the bread slices, with the buttered sides facing out.
Step 3 (5 min): Bake the sandwich in the preheated oven.
Step 4 (5 min): Heat soup in the microwave.
Step 5 (1 min): Remove the sandwich from the oven and serve with the soup.

- You can minimize the execution time based on the following properties:
You can perform autonomous actions step 0, 3, 4 in parallel with other actions to speed up the process.
You can execute part of the action duration to pause steps 2 for more efficient multitasking. Other actions must be finished without interruption.

- Do not violate any following constraints when executing this recipe:
The action before the arrow must be completed before the action after the arrow can be started: 1->2, 0->3, 2->3, 3->5, 4->5
The following actions would occupy the corresponding physical objects. You can not perform the action if the object is occupied. The property such as volume and temperature of the object should also match the requirement of the recipe: Steps 0, 3 requires oven, Steps 4 requires microwave
'''





recipe_descriptions['dynamic']['easy'] = '''## Recipe 1:Baked-Potato
Step 0 (10 min): Preheat the oven to 425 degrees.
Step 1 (2 min): Pierce the potato several times with a fork.
Step 2 (5 min): Bake the potato in the preheated oven.
Step 3 (1 min): Melt butter in the microwave.
Step 4 (10 min): Remove potato from the oven and use a sharp knife to make decorative cuts on the top of the potato.
Step 5 (1 min): Pour melted butter over the potato and serve.

- You can minimize the execution time based on the following properties:
You can execute part of the action duration to pause steps 1, 4 for more efficient multitasking. But other actions must be finished without interruption.

Thoughts on the recipe:
I can perform autonomous actions step 0, 2, 3 in parallel with other actions to speed up the process.
The action before the arrow must be completed before the action after the arrow can be started: 0->2, 1->2, 2->4, 3->5, 4->5
The following actions would occupy the corresponding physical objects. I can not perform the action if the object is occupied. The property such as volume and temperature of the object should also match the requirement of the recipe: Steps 0, 2 requires oven, Steps 3 requires microwave

## Recipe 2:Cheese-Sandwich
Step 0 (10 min): Preheat the oven to 425 degrees.
Step 1 (2 min): Butter one side of two slices of bread.
Step 2 (1 min): Place a slice of cheese between the bread slices, with the buttered sides facing out.
Step 3 (5 min): Bake the sandwich in the preheated oven.
Step 4 (5 min): Heat soup in the microwave.
Step 5 (1 min): Remove the sandwich from the oven and serve with the soup.

- You can minimize the execution time based on the following properties:

You can execute part of the action duration to pause steps 2 for more efficient multitasking. Other actions must be finished without interruption.

Thoughts on the recipe:
I can perform autonomous actions step 0, 3, 4 in parallel with other actions to speed up the process.
The action before the arrow must be completed before the action after the arrow can be started: 1->2, 0->3, 2->3, 3->5, 4->5
The following actions would occupy the corresponding physical objects. I can not perform the action if the object is occupied. The property such as volume and temperature of the object should also match the requirement of the recipe: Steps 0, 3 requires oven, Steps 4 requires microwave
'''



recipe_descriptions['oracle']['medium'] = '''## Recipe 1:Baked-Potato
Step 0 (10 min): Preheat the oven to 425 degrees.
Step 1 (2 min): Pierce the potato several times with a fork.
Step 2 (5 min): Bake the potato in the preheated oven.
Step 3 (1 min): Melt butter in the microwave.
Step 4 (10 min): Remove potato from the oven and use a sharp knife to make decorative cuts on the top of the potato.
Step 5 (1 min): Pour melted butter over the potato and serve.

- You can minimize the execution time based on the following properties:
You can perform autonomous actions step 0, 2, 3 in parallel with other actions to speed up the process.
You can execute part of the action duration to pause steps 1, 4 for more efficient multitasking. But other actions must be finished without interruption.

- Do not violate any following constraints when executing this recipe:
Step 5 must be performed within 2 min after Step 3 is finished
The action before the arrow must be completed before the action after the arrow can be started: 0->2, 1->2, 2->4, 3->5, 4->5
The following actions would occupy the corresponding physical objects. You can not perform the action if the object is occupied. The property such as volume and temperature of the object should also match the requirement of the recipe: Steps 0, 2 requires oven, Steps 3 requires microwave

## Recipe 2:Cheese-Sandwich
Step 0 (10 min): Preheat the oven to 425 degrees.
Step 1 (2 min): Butter one side of two slices of bread.
Step 2 (1 min): Place a slice of cheese between the bread slices, with the buttered sides facing out.
Step 3 (5 min): Bake the sandwich in the preheated oven.
Step 4 (5 min): Heat soup in the microwave.
Step 5 (1 min): Remove the sandwich from the oven and serve with the soup.

- You can minimize the execution time based on the following properties:
You can perform autonomous actions step 0, 3, 4 in parallel with other actions to speed up the process.
You can execute part of the action duration to pause steps 2 for more efficient multitasking. Other actions must be finished without interruption.

- Do not violate any following constraints when executing this recipe:
Step 5 must be performed within 5 min after Step 3 is finished  
The action before the arrow must be completed before the action after the arrow can be started: 1->2, 0->3, 2->3, 3->5, 4->5
The following actions would occupy the corresponding physical objects. You can not perform the action if the object is occupied. The property such as volume and temperature of the object should also match the requirement of the recipe: Steps 0, 3 requires oven, Steps 4 requires microwave
'''

recipe_descriptions['oracle_complete']['medium'] = '''## Recipe 1:Baked-Potato
Step 0 (10 min): Preheat the oven to 425 degrees.
Step 1 (2 min): Pierce the potato several times with a fork.
Step 2 (5 min): Bake the potato in the preheated oven.
Step 3 (1 min): Melt butter in the microwave.
Step 4 (10 min): Remove potato from the oven and use a sharp knife to make decorative cuts on the top of the potato.
Step 5 (1 min): Pour melted butter over the potato and serve.

- Do not violate any following constraints when executing this recipe:
Step 5 must be performed within 2 min after Step 3 is finished

Thoughts on the recipe:
I can perform autonomous actions step 0, 2, 3 in parallel with other actions.
The action before the arrow must be completed before the action after the arrow can be started: 0->2, 1->2, 2->4, 3->5, 4->5
The following actions would occupy the corresponding physical objects. I can not perform the action if the object is occupied. The property such as volume and temperature of the object should also match the requirement of the recipe: Steps 0, 2 requires oven, Steps 3 requires microwave

## Recipe 2:Cheese-Sandwich
Step 0 (10 min): Preheat the oven to 425 degrees.
Step 1 (2 min): Butter one side of two slices of bread.
Step 2 (1 min): Place a slice of cheese between the bread slices, with the buttered sides facing out.
Step 3 (5 min): Bake the sandwich in the preheated oven.
Step 4 (5 min): Heat soup in the microwave.
Step 5 (1 min): Remove the sandwich from the oven and serve with the soup.

- Do not violate any following constraints when executing this recipe:
Step 5 must be performed within 5 min after Step 3 is finished

Thoughts on the recipe:
I can perform autonomous actions step 0, 3, 4 in parallel with other actions.
The action before the arrow must be completed before the action after the arrow can be started: 1->2, 0->3, 2->3, 3->5, 4->5
The following actions would occupy the corresponding physical objects. I can not perform the action if the object is occupied. The property such as volume and temperature of the object should also match the requirement of the recipe: Steps 0, 3 requires oven, Steps 4 requires microwave
'''

recipe_descriptions['single_recipe']['medium'] = '''## Recipe 1:Baked-Potato
Step 0 (10 min): Preheat the oven to 425 degrees.
Step 1 (2 min): Pierce the potato several times with a fork.
Step 2 (5 min): Bake the potato in the preheated oven.
Step 3 (1 min): Melt butter in the microwave.
Step 4 (10 min): Remove potato from the oven and use a sharp knife to make decorative cuts on the top of the potato.
Step 5 (1 min): Pour melted butter over the potato and serve.

- Do not violate any following constraints when executing this recipe:
Step 5 must be performed within 2 min after Step 3 is finished

Thoughts on the recipe:
I can perform autonomous actions step 0, 2, 3 in parallel with other actions.
The action before the arrow must be completed before the action after the arrow can be started: 0->2, 1->2, 2->4, 3->5, 4->5
The following actions would occupy the corresponding physical objects. I can not perform the action if the object is occupied. The property such as volume and temperature of the object should also match the requirement of the recipe: Steps 0, 2 requires oven, Steps 3 requires microwave
'''

recipe_descriptions['dynamic']['medium'] = '''## Recipe 1:Baked-Potato
Step 0 (10 min): Preheat the oven to 425 degrees.
Step 1 (2 min): Pierce the potato several times with a fork.
Step 2 (5 min): Bake the potato in the preheated oven.
Step 3 (1 min): Melt butter in the microwave.
Step 4 (10 min): Remove potato from the oven and use a sharp knife to make decorative cuts on the top of the potato.
Step 5 (1 min): Pour melted butter over the potato and serve.

- You can minimize the execution time based on the following properties:
You can execute part of the action duration to pause steps 1, 4 for more efficient multitasking. But other actions must be finished without interruption.

- Do not violate any following constraints when executing this recipe:
Step 5 must be performed within 2 min after Step 3 is finished

Thoughts on the recipe:
I can perform autonomous actions step 0, 2, 3 in parallel with other actions to speed up the process.
The action before the arrow must be completed before the action after the arrow can be started: 0->2, 1->2, 2->4, 3->5, 4->5
The following actions would occupy the corresponding physical objects. I can not perform the action if the object is occupied. The property such as volume and temperature of the object should also match the requirement of the recipe: Steps 0, 2 requires oven, Steps 3 requires microwave

## Recipe 2:Cheese-Sandwich
Step 0 (10 min): Preheat the oven to 425 degrees.
Step 1 (2 min): Butter one side of two slices of bread.
Step 2 (1 min): Place a slice of cheese between the bread slices, with the buttered sides facing out.
Step 3 (5 min): Bake the sandwich in the preheated oven.
Step 4 (5 min): Heat soup in the microwave.
Step 5 (1 min): Remove the sandwich from the oven and serve with the soup.

- You can minimize the execution time based on the following properties:
You can execute part of the action duration to pause steps 2 for more efficient multitasking. Other actions must be finished without interruption.

- Do not violate any following constraints when executing this recipe:
Step 5 must be performed within 5 min after Step 3 is finished

Thoughts on the recipe:
I can perform autonomous actions step 0, 3, 4 in parallel with other actions to speed up the process.
The action before the arrow must be completed before the action after the arrow can be started: 1->2, 0->3, 2->3, 3->5, 4->5
The following actions would occupy the corresponding physical objects. I can not perform the action if the object is occupied. The property such as volume and temperature of the object should also match the requirement of the recipe: Steps 0, 3 requires oven, Steps 4 requires microwave
'''

react_examples['oracle']['easy'] = '''
## Action Sequence
Observation: The current timestamp is 0:0:0. Status of physical objects: oven is not occupied, is not preheated; microwave is not occupied; stove is not occupied
Thought: To optimize the process, I should start with actions that can run in parallel and those that require preheating, as they take the longest. I will preheat the oven for both recipes simultaneously, as they require the same temperature. This will allow me to perform other actions while the oven is preheating.
Action: Step(0, Baked-Potato, 00:10:00, 00:00:00) 

Observation: Autonomous action started successfully. The current timestamp is 0:0:0. Status of physical objects: oven is occupied, temperature is 425.0; microwave is not occupied; stove is not occupied; You are currently executing the following autonomous actions: step 0 of Baked-Potato (will finish at 0:10:0)
Thought: Since the oven is preheating for the Baked-Potato, I can start preheating it for the Cheese-Sandwich as well, as both require the same temperature. 
Action: Step(0, Cheese-Sandwich, 00:10:00, 00:00:00) 

Observation: Autonomous action started successfully. The current timestamp is 0:0:0. Status of physical objects: oven is occupied, temperature is 425.0; microwave is not occupied; stove is not occupied; You are currently executing the following autonomous actions: step 0 of Baked-Potato (will finish at 0:10:0), step 0 of Cheese-Sandwich (will finish at 0:10:0)
Thought: With both preheating steps in progress, I should focus on actions that don't require the oven. I can start piercing the potato for the Baked-Potato recipe.
Action: Step(1, Baked-Potato, 00:02:00, 00:00:00) 

Observation: Continuous action executed successfully. The current timestamp is 0:2:0. Status of physical objects: oven is occupied, temperature is 425.0; microwave is not occupied; stove is not occupied; You are currently executing the following autonomous actions: step 0 of Baked-Potato (will finish at 0:10:0), step 0 of Cheese-Sandwich (will finish at 0:10:0)
Thought: Since the preheating is not completed, I can butter the bread slices. This will prepare me to quickly proceed with the next steps once the oven is ready.
Action: Step(1, Cheese-Sandwich, 00:02:00, 00:02:00) 

Observation: Continuous action executed successfully. The current timestamp is 0:4:0. Status of physical objects: oven is occupied, temperature is 425.0; microwave is not occupied; stove is not occupied; You are currently executing the following autonomous actions: step 0 of Baked-Potato (will finish at 0:10:0), step 0 of Cheese-Sandwich (will finish at 0:10:0)
Thought: With the bread buttered for the Cheese-Sandwich, I can now place the cheese between the slices while waiting for the oven to finish preheating.
Action: Step(2, Cheese-Sandwich, 00:01:00, 00:04:00) 

Observation: Continuous action executed successfully. The current timestamp is 0:5:0. Status of physical objects: oven is occupied, temperature is 425.0; microwave is not occupied; stove is not occupied; You are currently executing the following autonomous actions: step 0 of Baked-Potato (will finish at 0:10:0), step 0 of Cheese-Sandwich (will finish at 0:10:0)
Thought: I have completed the preparatory steps for the Cheese-Sandwich. Since both recipes are still preheating in the oven, I should wait for the preheating to complete. After preheating, both recipes are ready for the next baking step. The step 4 of the Baked-Potato is a long continuous step which can be executed in parallel with step 3 and 4 of the Cheese-Sandwich. So I should bake the Baked-Potato first.
I will wait and perform the next action at 00:10:00. Action: Step(2, Baked-Potato, 00:05:00, 00:10:00) 

Observation: Autonomous action started successfully. The current timestamp is 0:10:0. Status of physical objects: oven is occupied, temperature is 425.0; microwave is not occupied; stove is not occupied; You are currently executing the following autonomous actions: step 2 of Baked-Potato (will finish at 0:15:0)
Thought: With the Baked-Potato currently baking in the oven, I should utilize this time to perform other actions that don't require the oven. I can start heating the soup for the Cheese-Sandwich in the microwave, as this is an autonomous action and can run in parallel with the baking.
Action: Step(4, Cheese-Sandwich, 00:05:00, 00:10:00) 

Observation: Autonomous action started successfully. The current timestamp is 0:10:0. Status of physical objects: oven is occupied, temperature is 425.0; microwave is occupied; stove is not occupied; You are currently executing the following autonomous actions: step 2 of Baked-Potato (will finish at 0:15:0), step 4 of Cheese-Sandwich (will finish at 0:15:0)
Thought: With both the Baked-Potato and Cheese-Sandwich currently utilizing the oven and microwave, I should wait for these actions to complete before proceeding. Once the Baked-Potato is done baking, I will be ready to bake the Cheese-Sandwich once the oven is free.
I will wait and perform the next action at 00:15:00. Action: Step(3, Cheese-Sandwich, 00:05:00, 00:15:00)  

Observation: Autonomous action started successfully. The current timestamp is 0:15:0. Status of physical objects: oven is occupied, temperature is 425.0; microwave is not occupied; stove is not occupied; You are currently executing the following autonomous actions: step 4 of Cheese-Sandwich (will finish at 0:20:0)
Thought: With the Cheese-Sandwich currently baking in the oven, I can now focus on the the Baked-Potato. I will remove the Baked-Potato from the oven and prepare it for serving. I should not start melting the butter while preparing the Baked-Potato to avoid the butter cooling down. So I will start making decorative cuts on the top of the potato first. And I will stop at 0:24:00 to melt the butter
Action: Step(4, Baked-Potato, 00:09:00, 00:15:00)

Observation: Continuous action executed successfully. The current timestamp is 0:20:0. Status of physical objects: oven is not occupied, temperature is 425.0; microwave is not occupied; stove is not occupied
Thought: I have stopped in the middle of the Step 4 of Baked-Potato to melt the butter. 
Action: Step(3, Baked-Potato, 00:01:00, 00:24:0)

Observation: Autonomous action started successfully. The current timestamp is 0:24:0. Status of physical objects: oven not is occupied, temperature is 425.0; microwave is occupied; stove is not occupied; You are executing the following autonomous actions: step 3 of Baked-Potato (will finish at 0:25:0)
Thought: Now I will continue with the decorative cuts on the top of the potato for another minute to finish this step
Action: Step(4, Baked-Potato, 00:01:00, 00:24:0)

Observation: Continuous action executed successfully. The current timestamp is 0:25:0. Status of physical objects: oven is not occupied, temperature is 425.0; microwave is not occupied; stove is not occupied
Thought: Now I will finish the last step of the Baked-Potato recipe by pouring the melted butter over the potato and serving it.
Action: Step(5, Baked-Potato, 00:01:00, 00:25:0)

Observation: Continuous action executed successfully. The current timestamp is 0:26:0. Status of physical objects: oven is occupied, temperature is 425.0; microwave is occupied; stove is not occupied.
Thought: The Baked-Potato is ready. I will now serve the Baked-Potato and finish the task.
Action: Step(5, Cheese-Sandwich, 00:01:00, 00:26:0)

Observation: Continuous action executed successfully. The current timestamp is 0:27:0. Status of physical objects: oven is occupied, temperature is 425.0; microwave is occupied; stove is not occupied
Action: Finish
'''

react_examples['oracle']['medium'] = '''
## Action Sequence
Observation: The current timestamp is 0:0:0. Status of physical objects: oven is not occupied, is not preheated; microwave is not occupied; stove is not occupied
Thought: To optimize the process, I should start with actions that can run in parallel and those that require preheating, as they take the longest. I will preheat the oven for both recipes simultaneously, as they require the same temperature. This will allow me to perform other actions while the oven is preheating.
Action: Step(0, Baked-Potato, 00:10:00, 00:00:00) 

Observation: Autonomous action started successfully. The current timestamp is 0:0:0. Status of physical objects: oven is occupied, temperature is 425.0; microwave is not occupied; stove is not occupied; You are currently executing the following autonomous actions: step 0 of Baked-Potato (will finish at 0:10:0)
Thought: Since the oven is preheating for the Baked-Potato, I can start preheating it for the Cheese-Sandwich as well, as both require the same temperature. 
Action: Step(0, Cheese-Sandwich, 00:10:00, 00:00:00) 

Observation: Autonomous action started successfully. The current timestamp is 0:0:0. Status of physical objects: oven is occupied, temperature is 425.0; microwave is not occupied; stove is not occupied; You are currently executing the following autonomous actions: step 0 of Baked-Potato (will finish at 0:10:0), step 0 of Cheese-Sandwich (will finish at 0:10:0)
Thought: With both preheating steps in progress, I should focus on actions that don't require the oven. I can start piercing the potato for the Baked-Potato recipe.
Action: Step(1, Baked-Potato, 00:02:00, 00:00:00) 

Observation: Continuous action executed successfully. The current timestamp is 0:2:0. Status of physical objects: oven is occupied, temperature is 425.0; microwave is not occupied; stove is not occupied; You are currently executing the following autonomous actions: step 0 of Baked-Potato (will finish at 0:10:0), step 0 of Cheese-Sandwich (will finish at 0:10:0)
Thought: Since the preheating is not completed, I can butter the bread slices. This will prepare me to quickly proceed with the next steps once the oven is ready.
Action: Step(1, Cheese-Sandwich, 00:02:00, 00:02:00) 

Observation: Continuous action executed successfully. The current timestamp is 0:4:0. Status of physical objects: oven is occupied, temperature is 425.0; microwave is not occupied; stove is not occupied; You are currently executing the following autonomous actions: step 0 of Baked-Potato (will finish at 0:10:0), step 0 of Cheese-Sandwich (will finish at 0:10:0)
Thought: With the bread buttered for the Cheese-Sandwich, I can now place the cheese between the slices while waiting for the oven to finish preheating.
Action: Step(2, Cheese-Sandwich, 00:01:00, 00:04:00) 

Observation: Continuous action executed successfully. The current timestamp is 0:5:0. Status of physical objects: oven is occupied, temperature is 425.0; microwave is not occupied; stove is not occupied; You are currently executing the following autonomous actions: step 0 of Baked-Potato (will finish at 0:10:0), step 0 of Cheese-Sandwich (will finish at 0:10:0)
Thought: I have completed the preparatory steps for the Cheese-Sandwich. Since both recipes are still preheating in the oven, I should wait for the preheating to complete. After preheating, both recipes are ready for the next baking step. The step 4 of the Baked-Potato is a long continuous step which can be executed in parallel with step 3 and 4 of the Cheese-Sandwich. So I should bake the Baked-Potato first.
I will wait and perform the next action at 00:10:00. Action: Step(2, Baked-Potato, 00:05:00, 00:10:00) 

Observation: Autonomous action started successfully. The current timestamp is 0:10:0. Status of physical objects: oven is occupied, temperature is 425.0; microwave is not occupied; stove is not occupied; You are currently executing the following autonomous actions: step 2 of Baked-Potato (will finish at 0:15:0)
Thought: With the Baked-Potato currently baking in the oven, I should utilize this time to perform other actions that don't require the oven. I can start heating the soup for the Cheese-Sandwich in the microwave, as this is an autonomous action and can run in parallel with the baking.
Action: Step(4, Cheese-Sandwich, 00:05:00, 00:10:00) 

Observation: Autonomous action started successfully. The current timestamp is 0:10:0. Status of physical objects: oven is occupied, temperature is 425.0; microwave is occupied; stove is not occupied; You are currently executing the following autonomous actions: step 2 of Baked-Potato (will finish at 0:15:0), step 4 of Cheese-Sandwich (will finish at 0:15:0)
Thought: With both the Baked-Potato and Cheese-Sandwich currently utilizing the oven and microwave, I should wait for these actions to complete before proceeding. Once the Baked-Potato is done baking, I will be ready to bake the Cheese-Sandwich once the oven is free.
I will wait and perform the next action at 00:15:00. Action: Step(3, Cheese-Sandwich, 00:05:00, 00:15:00)  

Observation: Autonomous action started successfully. The current timestamp is 0:15:0. Status of physical objects: oven is occupied, temperature is 425.0; microwave is not occupied; stove is not occupied; You are currently executing the following autonomous actions: step 4 of Cheese-Sandwich (will finish at 0:20:0)
Thought: With the Cheese-Sandwich currently baking in the oven, I can now focus on the the Baked-Potato. I will remove the Baked-Potato from the oven and prepare it for serving. I should not start melting the butter for the Baked-Potato before nearly finishing the Step 4 of Baked-Potato to avoid the butter cooling down. So I will start making decorative cuts on the top of the potato first. And I will stop at 0:20:00 to serve the Cheese-Sandwich to avoid ensure the Cheese-Sandwich is served within 5 minutes after it is baked. 
Action: Step(4, Baked-Potato, 00:05:00, 00:15:0)

Observation: Continuous action executed successfully. The current timestamp is 0:20:0. Status of physical objects: oven is occupied, temperature is 425.0; microwave is not occupied; stove is not occupied
Thought: I have stopped in the middle of the Step 4 of Baked-Potato to avoid violating the time restriction. I will now serve the Cheese-Sandwich and then continue with the Baked-Potato.
Action: Step(5, Cheese-Sandwich, 00:01:00, 00:20:0)

Observation: Continuous action executed successfully. The current timestamp is 0:21:0. Status of physical objects: oven is occupied, temperature is 425.0; microwave is not occupied; stove is not occupied
Thought: I have served the Cheese-Sandwich and can now continue with the Baked-Potato. I will prepare the melted butter and pour it over the potato to complete the recipe. Since the step 5 must be performed within 2 min after Step 3 is finished, I will start melting the butter when step 4 is nearly finished in 1 minute to avoid violating this constraint and execute step 3 and 4 of Baked-Potato in parallel to minimize the execution time. Now I would continue with the decorative cuts on the top of the potato for another 4 minutes.
Action: Step(4, Baked-Potato, 00:04:00, 00:21:0)

Observation: Continuous action executed successfully. The current timestamp is 0:25:0. Status of physical objects: oven is occupied, temperature is 425.0; microwave is not occupied; stove is not occupied
Thought: I have completed the decorative cuts on the top of the potato. I will now melt the butter and pour it over the potato to finish the recipe.
Action: Step(3, Baked-Potato, 00:01:00, 00:25:0)

Observation: Autonomous action started successfully. The current timestamp is 0:29:0. Status of physical objects: oven is occupied, temperature is 425.0; microwave is occupied; stove is not occupied. You are executing the following autonomous actions: step 3 of Baked-Potato (will finish at 0:30:0)
Thought: With the butter melted, I can finish the decorative cuts on the top of the potato and pour the butter over it to complete the recipe.
Action: Step(4, Baked-Potato, 00:01:00, 00:25:0)

Observation: Autonomous action started successfully. The current timestamp is 0:26:0. Status of physical objects: oven is occupied, temperature is 425.0; microwave is occupied; stove is not occupied.
Thought: Now I will finish the last step of the Baked-Potato recipe by pouring the melted butter over the potato and serving it.
Action: Step(5, Baked-Potato, 00:01:00, 00:26:0)

Observation: Continuous action executed successfully. The current timestamp is 0:27:0. Status of physical objects: oven is occupied, temperature is 425.0; microwave is occupied; stove is not occupied
Action: Finish
'''

react_examples['dynamic']['easy'] = '''
## Action Sequence
Observation: The current timestamp is 0:0:0. Status of physical objects: oven is not occupied, is not preheated; microwave is not occupied; stove is not occupied
Thought: To optimize the process, I should start with actions that can run in parallel and those that require preheating, as they take the longest. I will preheat the oven for both recipes simultaneously, as they require the same temperature. This will allow me to perform other actions while the oven is preheating.
Action: Step(0, Baked-Potato, 00:10:00, 00:00:00) 

Observation: Autonomous action started successfully. The current timestamp is 0:0:0. Status of physical objects: oven is occupied, temperature is 425.0; microwave is not occupied; stove is not occupied; You are currently executing the following autonomous actions: step 0 of Baked-Potato (will finish at 0:10:0)
Thought: Since the oven is preheating for the Baked-Potato, I can start preheating it for the Cheese-Sandwich as well, as both require the same temperature. 
Action: Step(0, Cheese-Sandwich, 00:10:00, 00:00:00) 

Observation: Autonomous action started successfully. The current timestamp is 0:0:0. Status of physical objects: oven is occupied, temperature is 425.0; microwave is not occupied; stove is not occupied; You are currently executing the following autonomous actions: step 0 of Baked-Potato (will finish at 0:10:0), step 0 of Cheese-Sandwich (will finish at 0:10:0)
Thought: With both preheating steps in progress, I should focus on actions that don't require the oven. I can start piercing the potato for the Baked-Potato recipe.
Action: Step(1, Baked-Potato, 00:02:00, 00:00:00) 

Observation: Continuous action executed successfully. The current timestamp is 0:2:0. Status of physical objects: oven is occupied, temperature is 425.0; microwave is not occupied; stove is not occupied; You are currently executing the following autonomous actions: step 0 of Baked-Potato (will finish at 0:10:0), step 0 of Cheese-Sandwich (will finish at 0:10:0)
Thought: Since the preheating is not completed, I can butter the bread slices. This will prepare me to quickly proceed with the next steps once the oven is ready.
Action: Step(1, Cheese-Sandwich, 00:02:00, 00:02:00) 

Observation: Continuous action executed successfully. The current timestamp is 0:4:0. Status of physical objects: oven is occupied, temperature is 425.0; microwave is not occupied; stove is not occupied; You are currently executing the following autonomous actions: step 0 of Baked-Potato (will finish at 0:10:0), step 0 of Cheese-Sandwich (will finish at 0:10:0)
Thought: With the bread buttered for the Cheese-Sandwich, I can now place the cheese between the slices while waiting for the oven to finish preheating.
Action: Step(2, Cheese-Sandwich, 00:01:00, 00:04:00)

Observation: Continuous action executed successfully. The current timestamp is 0:5:0. Status of physical objects: oven is occupied, temperature is 425.0; microwave is not occupied; stove is not occupied; You are currently executing the following autonomous actions: step 0 of Baked-Potato (will finish at 0:10:0), step 0 of Cheese-Sandwich (will finish at 0:10:0)
Thought: I have completed the preparatory steps for the Cheese-Sandwich. Now I can continue with the Baked-Potato. I will now perform the next action to bake the potato in the preheated oven.
Action: Step(2, Baked-Potato, 00:05:00, 00:05:00)

Observation: Step 2 can not be performed because prerequisite action is not completed. You should wait for step 0 to finish at 00:10:00.
Thought: The observation does not align with the initial thoughts. Step 1 is dependent on step 0, which is preheating the oven. I should wait for the oven to finish preheating before proceeding with the next steps. This also means step 4 does not depend on step 0 but step 2.  Since both recipes are still preheating in the oven, I should wait for the preheating to complete. After preheating, both recipes are ready for the next baking step. The step 4 of the Baked-Potato is a long continuous step which can be executed in parallel with step 3 and 4 of the Cheese-Sandwich. So I should bake the Baked-Potato first.
I will wait and perform the next action at 00:10:00. Action: Step(2, Baked-Potato, 00:05:00, 00:10:00) 

Observation: Autonomous action started successfully. The current timestamp is 0:10:0. Status of physical objects: oven is occupied, temperature is 425.0; microwave is occupied; stove is not occupied; You are currently executing the following autonomous actions: step 2 of Baked-Potato (will finish at 0:15:0), step 4 of Cheese-Sandwich (will finish at 0:15:0)
Thought: With both the Baked-Potato and Cheese-Sandwich currently utilizing the oven and microwave, I should wait for these actions to complete before proceeding. Once the Baked-Potato is done baking, I will be ready to bake the Cheese-Sandwich once the oven is free.
I will wait and perform the next action at 00:15:00. Action: Step(3, Cheese-Sandwich, 00:05:00, 00:15:00)  

Observation: Autonomous action started successfully. The current timestamp is 0:15:0. Status of physical objects: oven is occupied, temperature is 425.0; microwave is not occupied; stove is not occupied; You are currently executing the following autonomous actions: step 4 of Cheese-Sandwich (will finish at 0:20:0)
Thought: With the Cheese-Sandwich currently baking in the oven, I can now focus on the the Baked-Potato. I will remove the Baked-Potato from the oven and prepare it for serving. I should not start melting the butter while preparing the Baked-Potato to avoid the butter cooling down. So I will start making decorative cuts on the top of the potato first. And I will stop at 0:24:00 to melt the butter
Action: Step(4, Baked-Potato, 00:09:00, 00:15:00)

Observation: Continuous action executed successfully. The current timestamp is 0:20:0. Status of physical objects: oven is not occupied, temperature is 425.0; microwave is not occupied; stove is not occupied
Thought: I have stopped in the middle of the Step 4 of Baked-Potato to melt the butter. 
Action: Step(3, Baked-Potato, 00:01:00, 00:24:0)


Observation: Autonomous action started successfully. The current timestamp is 0:24:0. Status of physical objects: oven not is occupied, temperature is 425.0; microwave is occupied; stove is not occupied; You are executing the following autonomous actions: step 3 of Baked-Potato (will finish at 0:25:0)
Thought: Now I will continue with the decorative cuts on the top of the potato for another minute to finish this step
Action: Step(4, Baked-Potato, 00:01:00, 00:24:0)

Observation: Continuous action executed successfully. The current timestamp is 0:25:0. Status of physical objects: oven is not occupied, temperature is 425.0; microwave is not occupied; stove is not occupied
Thought: Now I will finish the last step of the Baked-Potato recipe by pouring the melted butter over the potato and serving it.
Action: Step(5, Baked-Potato, 00:01:00, 00:25:0)

Observation: Continuous action executed successfully. The current timestamp is 0:26:0. Status of physical objects: oven is occupied, temperature is 425.0; microwave is occupied; stove is not occupied.
Thought: The Baked-Potato is ready. I will now serve the Baked-Potato and finish the task.
Action: Step(5, Cheese-Sandwich, 00:01:00, 00:26:0)

Observation: Continuous action executed successfully. The current timestamp is 0:27:0. Status of physical objects: oven is occupied, temperature is 425.0; microwave is occupied; stove is not occupied
Action: Finish
'''


react_examples['dynamic']['medium'] = '''
## Action Sequence
Observation: The current timestamp is 0:0:0. Status of physical objects: oven is not occupied, is not preheated; microwave is not occupied; stove is not occupied
Thought: To optimize the process, I should start with actions that can run in parallel and those that require preheating, as they take the longest. I will preheat the oven for both recipes simultaneously, as they require the same temperature. This will allow me to perform other actions while the oven is preheating.
Action: Step(0, Baked-Potato, 00:10:00, 00:00:00) 

Observation: Autonomous action started successfully. The current timestamp is 0:0:0. Status of physical objects: oven is occupied, temperature is 425.0; microwave is not occupied; stove is not occupied; You are currently executing the following autonomous actions: step 0 of Baked-Potato (will finish at 0:10:0)
Thought: Since the oven is preheating for the Baked-Potato, I can start preheating it for the Cheese-Sandwich as well, as both require the same temperature. 
Action: Step(0, Cheese-Sandwich, 00:10:00, 00:00:00) 

Observation: Autonomous action started successfully. The current timestamp is 0:0:0. Status of physical objects: oven is occupied, temperature is 425.0; microwave is not occupied; stove is not occupied; You are currently executing the following autonomous actions: step 0 of Baked-Potato (will finish at 0:10:0), step 0 of Cheese-Sandwich (will finish at 0:10:0)
Thought: With both preheating steps in progress, I should focus on actions that don't require the oven. I can start piercing the potato for the Baked-Potato recipe.
Action: Step(1, Baked-Potato, 00:02:00, 00:00:00) 

Observation: Continuous action executed successfully. The current timestamp is 0:2:0. Status of physical objects: oven is occupied, temperature is 425.0; microwave is not occupied; stove is not occupied; You are currently executing the following autonomous actions: step 0 of Baked-Potato (will finish at 0:10:0), step 0 of Cheese-Sandwich (will finish at 0:10:0)
Thought: Since the preheating is not completed, I can butter the bread slices. This will prepare me to quickly proceed with the next steps once the oven is ready.
Action: Step(1, Cheese-Sandwich, 00:02:00, 00:02:00) 

Observation: Continuous action executed successfully. The current timestamp is 0:4:0. Status of physical objects: oven is occupied, temperature is 425.0; microwave is not occupied; stove is not occupied; You are currently executing the following autonomous actions: step 0 of Baked-Potato (will finish at 0:10:0), step 0 of Cheese-Sandwich (will finish at 0:10:0)
Thought: With the bread buttered for the Cheese-Sandwich, I can now place the cheese between the slices while waiting for the oven to finish preheating.
Action: Step(2, Cheese-Sandwich, 00:01:00, 00:04:00)

Observation: Continuous action executed successfully. The current timestamp is 0:5:0. Status of physical objects: oven is occupied, temperature is 425.0; microwave is not occupied; stove is not occupied; You are currently executing the following autonomous actions: step 0 of Baked-Potato (will finish at 0:10:0), step 0 of Cheese-Sandwich (will finish at 0:10:0)
Thought: I have completed the preparatory steps for the Cheese-Sandwich. Now I can continue with the Baked-Potato. I will now perform the next action to bake the potato in the preheated oven.
Action: Step(2, Baked-Potato, 00:05:00, 00:05:00)

Observation: Step 2 can not be performed because prerequisite action is not completed. You should wait for step 0 to finish at 00:10:00.
Thought: The observation does not align with the initial thoughts. Step 1 is dependent on step 0, which is preheating the oven. I should wait for the oven to finish preheating before proceeding with the next steps. This also means step 4 does not depend on step 0 but step 2.  Since both recipes are still preheating in the oven, I should wait for the preheating to complete. After preheating, both recipes are ready for the next baking step. The step 4 of the Baked-Potato is a long continuous step which can be executed in parallel with step 3 and 4 of the Cheese-Sandwich. So I should bake the Baked-Potato first.
I will wait and perform the next action at 00:10:00. Action: Step(2, Baked-Potato, 00:05:00, 00:10:00) 

Observation: Autonomous action started successfully. The current timestamp is 0:10:0. Status of physical objects: oven is occupied, temperature is 425.0; microwave is not occupied; stove is not occupied; You are currently executing the following autonomous actions: step 2 of Baked-Potato (will finish at 0:15:0)
Thought: With the Baked-Potato currently baking in the oven, I should utilize this time to perform other actions that don't require the oven. I can start heating the soup for the Cheese-Sandwich in the microwave, as this is an autonomous action and can run in parallel with the baking.
Action: Step(4, Cheese-Sandwich, 00:05:00, 00:10:00) 

Observation: Autonomous action started successfully. The current timestamp is 0:10:0. Status of physical objects: oven is occupied, temperature is 425.0; microwave is occupied; stove is not occupied; You are currently executing the following autonomous actions: step 2 of Baked-Potato (will finish at 0:15:0), step 4 of Cheese-Sandwich (will finish at 0:15:0)
Thought: With both the Baked-Potato and Cheese-Sandwich currently utilizing the oven and microwave, I should wait for these actions to complete before proceeding. Once the Baked-Potato is done baking, I will be ready to bake the Cheese-Sandwich once the oven is free.
I will wait and perform the next action at 00:15:00. Action: Step(3, Cheese-Sandwich, 00:05:00, 00:15:00)  

Observation: Autonomous action started successfully. The current timestamp is 0:15:0. Status of physical objects: oven is occupied, temperature is 425.0; microwave is not occupied; stove is not occupied; You are currently executing the following autonomous actions: step 4 of Cheese-Sandwich (will finish at 0:20:0)
Thought: With the Cheese-Sandwich currently baking in the oven, I can now focus on the the Baked-Potato. I will remove the Baked-Potato from the oven and prepare it for serving. I should not start melting the butter for the Baked-Potato before nearly finishing the Step 4 of Baked-Potato to avoid the butter cooling down. So I will start making decorative cuts on the top of the potato first. And I will stop at 0:20:00 to serve the Cheese-Sandwich to avoid ensure the Cheese-Sandwich is served within 5 minutes after it is baked. 
Action: Step(4, Baked-Potato, 00:05:00, 00:15:0)

Observation: Continuous action executed successfully. The current timestamp is 0:20:0. Status of physical objects: oven is occupied, temperature is 425.0; microwave is not occupied; stove is not occupied
Thought: I have stopped in the middle of the Step 4 of Baked-Potato to avoid violating the time restriction. I will now serve the Cheese-Sandwich and then continue with the Baked-Potato.
Action: Step(5, Cheese-Sandwich, 00:01:00, 00:20:0)

Observation: Continuous action executed successfully. The current timestamp is 0:21:0. Status of physical objects: oven is occupied, temperature is 425.0; microwave is not occupied; stove is not occupied
Thought: I have served the Cheese-Sandwich and can now continue with the Baked-Potato. I will prepare the melted butter and pour it over the potato to complete the recipe. Since the step 5 must be performed within 2 min after Step 3 is finished, I will start melting the butter when step 4 is nearly finished in 1 minute to avoid violating this constraint and execute step 3 and 4 of Baked-Potato in parallel to minimize the execution time. Now I would continue with the decorative cuts on the top of the potato for another 4 minutes.
Action: Step(4, Baked-Potato, 00:04:00, 00:21:0)

Observation: Continuous action executed successfully. The current timestamp is 0:25:0. Status of physical objects: oven is occupied, temperature is 425.0; microwave is not occupied; stove is not occupied
Thought: I have completed the decorative cuts on the top of the potato. I will now melt the butter and pour it over the potato to finish the recipe.
Action: Step(3, Baked-Potato, 00:01:00, 00:25:0)

Observation: Autonomous action started successfully. The current timestamp is 0:29:0. Status of physical objects: oven is occupied, temperature is 425.0; microwave is occupied; stove is not occupied. You are executing the following autonomous actions: step 3 of Baked-Potato (will finish at 0:30:0)
Thought: With the butter melted, I can finish the decorative cuts on the top of the potato and pour the butter over it to complete the recipe.
Action: Step(4, Baked-Potato, 00:01:00, 00:25:0)

Observation: Autonomous action started successfully. The current timestamp is 0:26:0. Status of physical objects: oven is occupied, temperature is 425.0; microwave is occupied; stove is not occupied.
Thought: Now I will finish the last step of the Baked-Potato recipe by pouring the melted butter over the potato and serving it.
Action: Step(5, Baked-Potato, 00:01:00, 00:26:0)

Observation: Continuous action executed successfully. The current timestamp is 0:27:0. Status of physical objects: oven is occupied, temperature is 425.0; microwave is occupied; stove is not occupied
Action: Finish
'''


react_examples['oracle_complete']['medium'] = '''
Observation: The current timestamp is 00:00:00. Status of physical objects: oven is not occupied, is not preheated; microwave is not occupied; stove is not occupied
Thought: I will preheat the oven for both recipes simultaneously, as they require the same temperature. This will allow me to perform other actions while the oven is preheating.
Action: Step(0, Baked-Potato, 00:10:00, 00:00:00)

Observation: The current timestamp is 00:00:00. Status of physical objects: oven is occupied, temperature is 425.0; microwave is not occupied; stove is not occupied; You are currently executing the following autonomous actions: step 0 of Baked-Potato (will finish at 00:10:00)
Thought: Since the oven is preheating for the Baked-Potato, I can start preheating it for the Cheese-Sandwich as well, as both require the same temperature.
Action: Step(0, Cheese-Sandwich, 00:10:00, 00:00:00)

Observation: The current timestamp is 00:00:00. Status of physical objects: oven is occupied, temperature is 425.0; microwave is not occupied; stove is not occupied; You are currently executing the following autonomous actions: step 0 of Baked-Potato (will finish at 00:10:00), step 0 of Cheese-Sandwich (will finish at 00:10:00)
Thought: To ensure the success of both recipes, I will finish both of the recipes one by one. I will start with the Baked-Potato.
Action: Step(1, Baked-Potato, 00:02:00, 00:00:00)

Observation: The current timestamp is 00:02:00. Status of physical objects: oven is occupied, temperature is 425.0; microwave is not occupied; stove is not occupied; You are currently executing the following autonomous actions: step 0 of Baked-Potato (will finish at 00:10:00), step 0 of Cheese-Sandwich (will finish at 00:10:00)
Thought: Step 1 of the Baked-Potato is complete. I will now move on to step 2 of the Baked-Potato.
Action: Step(2, Baked-Potato, 00:05:00, 00:10:00)

Observation: The current timestamp is 00:10:00. Status of physical objects: oven is occupied, temperature is 425.0; microwave is not occupied; stove is not occupied; You are currently executing the following autonomous actions: step 2 of Baked-Potato (will finish at 00:15:00)
Thought: Step 2 of the Baked-Potato is complete. Since Step 5 must be performed within 2 minutes after Step 3 is complete, and Step 5 depends on both Step 3 and Step 4. Executing Step 3 first will result in violation of time restrictions since Step 4 is a long continuous step. I will now first finish Step 4 of the Baked-Potato to ensure the time restrictions are followed.
Action: Step(4, Baked-Potato, 00:10:00, 00:15:00)

Observation: The current timestamp is 00:25:00. Status of physical objects: oven is not occupied, temperature is 425.0; microwave is not occupied; stove is not occupied
Thought: The Step 4 of the Baked-Potato is complete. This enables me to start Step 5 of the Baked-Potato immediately after Step 3 is complete to ensure the time restrictions are followed. I will now finish Step 3 of the Baked-Potato now.
Action: Step(3, Baked-Potato, 00:01:00, 00:25:00)

Observation: The current timestamp is 00:25:00. Status of physical objects: oven is not occupied, temperature is 425.0; microwave is occupied; stove is not occupied; You are currently executing the following autonomous actions: step 3 of Baked-Potato (will finish at 00:26:00)
Thought: Step 3 of the Baked-Potato is complete. I will immediately move on to Step 5 of the Baked-Potato to ensure the time restrictions are followed.
Action: Step(5, Baked-Potato, 00:01:00, 00:26:00)

Observation: The current timestamp is 00:27:00. Status of physical objects: oven is not occupied, temperature is 425.0; microwave is not occupied; stove is not occupied
Thought: The Baked-Potato is complete. I will now move on to the Cheese-Sandwich. I will start with Step 1 of the Cheese-Sandwich.
Action: Step(1, Cheese-Sandwich, 00:02:00, 00:27:00)

Observation: The current timestamp is 00:29:00. Status of physical objects: oven is not occupied, temperature is 425.0; microwave is not occupied; stove is not occupied
Thought: Step 1 of the Cheese-Sandwich is complete. I will now move on to Step 2 of the Cheese-Sandwich.
Action: Step(2, Cheese-Sandwich, 00:01:00, 00:29:00)

Observation: The current timestamp is 00:30:00. Status of physical objects: oven is not occupied, temperature is 425.0; microwave is not occupied; stove is not occupied
Thought: Step 2 of the Cheese-Sandwich is complete. Note that Step 5 of the Cheese-Sandwich must be performed within 5 minutes after Step 3 is complete. I will now finish Step 4 of the Cheese-Sandwich to ensure the time restrictions are followed.
Action: Step(4, Cheese-Sandwich, 00:05:00, 00:30:00)

Observation: The current timestamp is 00:30:00. Status of physical objects: oven is not occupied, temperature is 425.0; microwave is occupied; stove is not occupied; You are currently executing the following autonomous actions: step 4 of Cheese-Sandwich (will finish at 00:35:00)
Thought: Step 4 of the Cheese-Sandwich is complete. I will now move on to Step 3 of the Cheese-Sandwich.
Action: Step(3, Cheese-Sandwich, 00:05:00, 00:35:00)

Observation: The current timestamp is 00:35:00. Status of physical objects: oven is occupied, temperature is 425.0; microwave is not occupied; stove is not occupied; You are currently executing the following autonomous actions: step 3 of Cheese-Sandwich (will finish at 00:40:00)
Thought: Step 3 of the Cheese-Sandwich is complete. I will immediately move on to Step 5 of the Cheese-Sandwich to ensure the time restrictions are followed.
Action: Step(5, Cheese-Sandwich, 00:01:00, 00:40:00)

Observation: The current timestamp is 00:40:00. Status of physical objects: oven is not occupied, temperature is 425.0; microwave is not occupied; stove is not occupied
Thought: Both the Baked-Potato and Cheese-Sandwich are complete.
Action: Finish
'''

react_examples['single_recipe']['medium'] = '''
Observation: The current timestamp is 00:00:00. Status of physical objects: oven is not occupied, is not preheated; microwave is not occupied; stove is not occupied
Thought: I will preheat the oven. This will allow me to perform other actions while the oven is preheating.
Action: Step(0, Baked-Potato, 00:10:00, 00:00:00)


Observation: The current timestamp is 00:00:00. Status of physical objects: oven is occupied, temperature is 425.0; microwave is not occupied; stove is not occupied; You are currently executing the following autonomous actions: step 0 of Baked-Potato (will finish at 00:10:00)
Thought: Since the oven is preheating, I can start piercing the potato for the Baked-Potato recipe. And this does not risk violating any time restrictions.
Action: Step(1, Baked-Potato, 00:02:00, 00:02:00)

Observation: The current timestamp is 00:04:00. Status of physical objects: oven is occupied, temperature is 425.0; microwave is not occupied; stove is not occupied; You are currently executing the following autonomous actions: step 0 of Baked-Potato (will finish at 00:10:00), step 0 of Cheese-Sandwich (will finish at 00:10:00)
Thought: Step 1 of the Baked-Potato is complete. I will now move on to step 2 of the Baked-Potato. This does not risk violating any time restrictions.
Action: Step(2, Baked-Potato, 00:05:00, 00:10:00)

Observation: The current timestamp is 00:10:00. Status of physical objects: oven is occupied, temperature is 425.0; microwave is not occupied; stove is not occupied; You are currently executing the following autonomous actions: step 2 of Baked-Potato (will finish at 00:15:00)
Thought: Step 2 of the Baked-Potato is complete. Since Step 5 depends on both Step 3 and Step 4 and Step 5 must be performed within 2 minutes after Step 3 is complete, and. Executing Step 3 first will result in violation of time restrictions since Step 4 is a long continuous step. I will now first finish Step 4 of the Baked-Potato to ensure the time restrictions are followed.
Action: Step(4, Baked-Potato, 00:10:00, 00:15:00)

Observation: The current timestamp is 00:25:00. Status of physical objects: oven is not occupied, temperature is 425.0; microwave is not occupied; stove is not occupied
Thought: The Step 4 of the Baked-Potato is complete. This enables me to start Step 5 of the Baked-Potato immediately after Step 3 is complete to ensure the time restrictions are followed. I will now finish Step 3 of the Baked-Potato now.
Action: Step(3, Baked-Potato, 00:01:00, 00:25:00)

Observation: The current timestamp is 00:25:00. Status of physical objects: oven is not occupied, temperature is 425.0; microwave is occupied; stove is not occupied; You are currently executing the following autonomous actions: step 3 of Baked-Potato (will finish at 00:26:00)
Thought: Step 3 of the Baked-Potato is complete. I will immediately move on to Step 5 of the Baked-Potato to ensure the time restrictions are followed.
Action: Step(5, Baked-Potato, 00:01:00, 00:26:00)

Observation: The current timestamp is 00:26:00. Status of physical objects: oven is not occupied, temperature is 425.0; microwave is not occupied; stove is not occupied
Thought: The recipe is completed.
Action: Finish
'''



end2end_examples = {}

end2end_examples['easy'] = '''
## Action Sequence
Step(0, Baked-Potato, 10 min, 00:00:00), Step(0, Cheese-Sandwich, 10 min, 00:00:00), Step(1, Baked-Potato, 2 min, 00:00:00), Step(1, Cheese-Sandwich, 2 min, 00:02:00), Step(2, Cheese-Sandwich, 1 min, 00:04:00), Step(2, Baked-Potato, 5 min, 00:10:00), Step(4, Cheese-Sandwich, 5 min, 00:10:00), Step(3, Cheese-Sandwich, 5 min, 00:15:00), Step(4, Baked-Potato, 9 min, 00:15:00), Step(3, Baked-Potato, 1 min, 00:25:00), Step(4, Baked-Potato, 1 min, 00:25:00), Step(5, Baked-Potato, 1 min, 00:26:00), Step(5, Cheese-Sandwich, 1 min, 00:26:00)
'''

end2end_examples['medium'] = '''
## Action Sequence
Step(0, Baked-Potato, 10 min, 00:00:00), Step(0, Cheese-Sandwich, 10 min, 00:00:00), Step(1, Baked-Potato, 2 min, 00:00:00), Step(1, Cheese-Sandwich, 2 min, 00:02:00), Step(2, Cheese-Sandwich, 1 min, 00:04:00), Step(2, Baked-Potato, 5 min, 00:10:00), Step(4, Cheese-Sandwich, 5 min, 00:10:00), Step(3, Cheese-Sandwich, 5 min, 00:15:00), Step(4, Baked-Potato, 5 min, 00:15:00), Step(5, Cheese-Sandwich, 1 min, 00:20:00), Step(4, Baked-Potato, 4 min, 00:21:00), Step(3, Baked-Potato, 1 min, 00:25:00), Step(4, Baked-Potato, 1 min, 00:25:00), Step(5, Baked-Potato, 1 min, 00:26:00)
'''


plan_solve_examples = {}

plan_solve_examples['easy'] = '''
## Plan
Start by preheating the oven for both recipes simultaneously, since they require the same temperature and preheating is an autonomous action. This allows the agent to perform other actions while the oven is preheating.

While the oven is preheating, start the prepartion steps that do not need the oven. I can pierce the potato (step 1 for Baked-Potato) and  prepare the Cheese-Sandwich by buttering the bread (Step 1) and then placing the cheese between the slices (Step 2). These steps only take 5 minutes, then wait for the oven to preheat.

At 00:10:00, the oven should be preheated. Bake the potato (Step 2 for Baked-Potato) and heat soup (Step 4 for Cheese-Sandwich) simultaneously. And wait for the autonoumous actions to finish at 00:15:00 since the oven and microwave are occupied and no other actions can be performed.

At 00:15:00, start baking the sandwich (Step 3 for Cheese-Sandwich) and making decorative cuts on the potato (Step 4 for Baked-Potato) simultaneously. Step 4 of Baked-Potato is interruptible, so the agent can pause this action and perform step 5 of Cheese-Sandwich at 00:24:00 to melt the butter. Then the agent can continue to finish the potato with executing autonomous action step 3 and continous action step 4 simultaneously and serve the potato at 00:25:00 and then serve the Cheese-Sandwich at 00:26:00.

## Action Sequence
Step(0, Baked-Potato, 10 min, 00:00:00), Step(0, Cheese-Sandwich, 10 min, 00:00:00), Step(1, Baked-Potato, 2 min, 00:00:00), Step(1, Cheese-Sandwich, 2 min, 00:02:00), Step(2, Cheese-Sandwich, 1 min, 00:04:00), Step(2, Baked-Potato, 5 min, 00:10:00), Step(4, Cheese-Sandwich, 5 min, 00:10:00), Step(3, Cheese-Sandwich, 5 min, 00:15:00), Step(4, Baked-Potato, 9 min, 00:15:00), Step(3, Baked-Potato, 1 min, 00:24:00), Step(4, Baked-Potato, 1 min, 00:24:00), Step(5, Baked-Potato, 1 min, 00:25:00), Step(5, Cheese-Sandwich, 1 min, 00:26:00)
'''


plan_solve_examples['medium'] = '''## Plan
Start by preheating the oven for both recipes simultaneously, since they require the same temperature and preheating is an autonomous action. This allows the agent to perform other actions while the oven is preheating.

While the oven is preheating, start the prepartion steps that do not need the oven. I can pierce the potato (step 1 for Baked-Potato) and  prepare the Cheese-Sandwich by buttering the bread (Step 1) and then placing the cheese between the slices (Step 2). These steps only take 5 minutes, then wait for the oven to preheat.

At 00:10:00, the oven should be preheated. Bake the potato (Step 2 for Baked-Potato) and heat soup (Step 4 for Cheese-Sandwich) simultaneously. And wait for the autonoumous actions to finish at 00:15:00 since the oven and microwave are occupied and no other actions can be performed.

At 00:15:00, start baking the sandwich (Step 3 for Cheese-Sandwich) and making decorative cuts on the potato (Step 4 for Baked-Potato) simultaneously. Step 4 of Baked-Potato is interruptible, so the agent can pause this action and perform step 5 of Cheese-Sandwich at 00:20:00 to serve the sandwich with the soup without violating the constraints. And the agent can continue to finish the potato with executing autonomous action step 3 and continous action step 4 simultaneously and serve the potato at 00:26:00.

## Action Sequence
Step(0, Baked-Potato, 10 min, 00:00:00), Step(0, Cheese-Sandwich, 10 min, 00:00:00), Step(1, Baked-Potato, 2 min, 00:00:00), Step(1, Cheese-Sandwich, 2 min, 00:02:00), Step(2, Cheese-Sandwich, 1 min, 00:04:00), Step(2, Baked-Potato, 5 min, 00:10:00), Step(4, Cheese-Sandwich, 5 min, 00:10:00), Step(3, Cheese-Sandwich, 5 min, 00:15:00), Step(4, Baked-Potato, 5 min, 00:15:00), Step(5, Cheese-Sandwich, 1 min, 00:20:00), Step(4, Baked-Potato, 4 min, 00:21:00), Step(3, Baked-Potato, 1 min, 00:25:00), Step(4, Baked-Potato, 1 min, 00:25:00), Step(5, Baked-Potato, 1 min, 00:26:00)
'''