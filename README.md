# Recipe2Plan
While Large Language Model-based agents have demonstrated substantial progress in task completion, existing evaluation benchmarks tend to overemphasize **single-task** performance, with insufficient attention given to the crucial aspects of **multitask planning** and **execution efficiency** required in real-world scenarios. To bridge this gap, we present Recipe2Plan, a novel benchmark framework based on real-world cooking scenarios. Unlike conventional benchmarks, Recipe2Plan challenges agents to optimize cooking time through parallel task execution while respecting temporal constraints i.e. specific actions need to be performed within a particular time intervals following the preceding steps.

![here](assets/intro.png)

Overly aggressive local parallelization may disrupt this constraint, potentially compromising the entire cooking process.
This strict time constraint between actions raises a unique challenge for agents to balance between maximizing concurrent operations and adhering to critical timing constraints. Extensive experiments with state-of-the-art models reveal challenges in maintaining this balance between efficiency and feasibility. 

## Installation
```
pip install requirements.txt
```
And set your api keys in `.bashrc` as specified in `evaluation/model.py`

## Evaluation
```
python plan_solve_agent.py \
    --model_name claude-opus-4-20250514 \
    --verbose \
    --oracle \
    --level easy
```
Note: We use `level=easy` and `level=medium` to indicate planning `w/o time constraints` and `w/ time constraints`.

You can run a result summarizer as 
```
python result_summarizer.py --level easy
python result_summarizer.py --level medium
```
