## Acknowledgement: This code is adapted from the original codebase of the paper "AgentBoard: An Analytical Evaluation Board of Multi-turn LLM Agents"
## https://github.com/hkust-nlp/AgentBoard
import openai
import os
import time
import tiktoken
from openai import OpenAI
from google import genai
from google.genai import types
import anthropic


class VLLM:
    def __init__(self,
                 model='',
                 temperature=0,
                 max_tokens=1024,
                 top_p=1.0,
                 context_length=4096,
                 end = ['Observation:','*/'],
                 ngpu=4,
                 d_type='bfloat16'
                 ):
        from vllm import LLM, SamplingParams
        self.engine = model
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.end = end
        self.context_length = context_length
        self.sampling_params = SamplingParams(
            temperature=temperature,
            top_p=top_p,
            stop = end,
            max_tokens=max_tokens
        )

        self.llm = LLM(model=self.model, dtype=d_type, tensor_parallel_size=ngpu, gpu_memory_utilization=0.9)
        self.tokenizer = self.llm.get_tokenizer()
        

    def generate(self, system_message, prompt):
        prompt = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ]
        prompt = self.tokenizer.apply_chat_template(prompt, add_generation_prompt = True, tokenize = False)
        outputs = self.llm.generate([prompt], self.sampling_params)
        outputs = outputs[0].outputs[0].text

        return True, outputs 

    def num_tokens_from_messages(self, messages):
        prompt = messages[1]["content"]
        system_message = messages[0]["content"]
        full_prompt = self.make_prompt(system_message, prompt)
        tokens = self.tokenizer(full_prompt)
        num_tokens = len(tokens["input_ids"])
        #print(num_tokens)
        return num_tokens

    @classmethod
    def from_config(cls, config):

        engine = config.get("engine", "gpt-35-turbo")
        temperature = config.get("temperature", 0)
        max_tokens = config.get("max_tokens", 4096)
        end = config.get("end", ['Observation:', '*/'])
        top_p = config.get("top_p", 1)
        context_length = config.get("context_length", 16384)
        ngpu = config.get("ngpu", 4)
        dtype = config.get("dtype", 'bfloat16')
        return cls(model=engine,
                   temperature=temperature,
                   max_tokens=max_tokens,
                   end = end,
                   top_p=top_p,
                   context_length=context_length,
                   ngpu=ngpu,
                   d_type=dtype)
        


class OPENAI_GPT:
    def __init__(self,
                 engine="gpt-3.5-turbo-0631",
                 temperature=0,
                 max_tokens=200,
                 use_azure=True,
                 top_p=1,
                 stop=["Observation:", '*/'],
                 retry_delays=60, # in seconds
                 max_retry_iters=5,
                 context_length=4096,
                 system_message='',
                 reasoning_effort='medium'
                 ):
        print(f"Using engine {engine}")
        #assert engine in ['gpt-4o-2024-08-06'] ## model we use in our study
        
        self.engine = engine
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.use_azure = use_azure
        self.top_p = top_p
        self.stop = stop
        self.retry_delays = retry_delays
        self.max_retry_iters = max_retry_iters
        self.context_length = context_length
        self.system_message = system_message
        self.reasoning_effort = reasoning_effort
        self.init_api_key()


        
    def init_api_key(self):
        if self.use_azure:
            openai.api_type = os.environ['OPENAI_API_TYPE']
            openai.api_version = os.environ['OPENAI_API_VERSION']
        else:
            if 'OPENAI_API_KEY' not in os.environ:
                raise Exception("OPENAI_API_KEY environment variable not set.")
            else:
                openai.api_key = os.environ['OPENAI_API_KEY']
            #openai.api_base = os.environ['OPENAI_API_BASE'] if 'OPENAI_API_BASE' in os.environ else openai.api_base

    def llm_inference(self, messages):
        client = OpenAI(
            base_url=os.environ['OPENAI_API_BASE'],
            api_key=os.environ['OPENAI_API_KEY']
        )
        if 'o1' in self.engine or 'qwen' in self.engine:
            ## o1 model does not support max tokens
            completion = client.chat.completions.create(
                model = self.engine,
                messages = messages,
                max_completion_tokens = 25000,
                seed=42
            )
        elif 'o4' in self.engine or 'gpt-5' in self.engine:
            completion = client.chat.completions.create(
                model = self.engine,
                messages = messages,
                reasoning_effort = self.reasoning_effort,
                seed=42
            )
        else:
            completion = client.chat.completions.create(
                model = self.engine,
                messages = messages,
                temperature = 0,
                stop = self.stop,
                max_tokens = self.max_tokens,
                seed=42
            )
        print(completion.usage.prompt_tokens)
        print(completion.usage.completion_tokens)
        return completion.choices[0].message.content

    def generate(self, system_message, prompt):
        if 'o' in self.engine or 'gpt-5' in self.engine:
            ## o1 model does not support system message
            prompt=[
                 {"role": "user", "content": prompt}
            ]
        else:
            prompt=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ]
        for attempt in range(self.max_retry_iters):
            try:
                return True, self.llm_inference(prompt) # return success, completion
            except Exception as e:
                print(f"Error on attempt {attempt + 1}, Error: {e}")
                if attempt < self.max_retry_iters - 1:  # If not the last attempt
                    time.sleep(self.retry_delays)  # Wait before retrying

                else:
                    print("Failed to get completion after multiple attempts.")
                    # raise e

        return False, None

    def num_tokens_from_messages(self, messages, model="gpt-3.5-turbo-0613"):
        """Return the number of tokens used by a list of messages."""
        model = self.engine
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            print("Warning: model not found. Using cl100k_base encoding.")
            encoding = tiktoken.get_encoding("cl100k_base")
        
        tokens_per_message = 0
        tokens_per_name = 0
        if model in {
            "gpt-3.5-turbo-0613",
            "gpt-3.5-turbo-16k-0613",
            "gpt-4-0314",
            "gpt-4-32k-0314",
            "gpt-4-0613",
            "gpt-4-32k-0613",
            }:
            tokens_per_message = 3
            tokens_per_name = 1
        
        num_tokens = 0
        for message in messages:
            num_tokens += tokens_per_message
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":
                    num_tokens += tokens_per_name
        num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
        return num_tokens

    @classmethod
    def from_config(cls, config):
        
        engine = config.get("engine", "gpt-35-turbo")
        temperature = config.get("temperature", 0)
        max_tokens = config.get("max_tokens", 32000)
        system_message = config.get("system_message", "You are a helpful assistant.")
        use_azure = config.get("use_azure", False)
        top_p = config.get("top_p", 1)
        stop = config.get("stop", ['Observation:', '*/'])
        retry_delays = config.get("retry_delays", 10)
        context_length = config.get("context_length", 16384)
        reasoning_effort = config.get("reasoning_effort", 'medium')
        return cls(engine=engine,
                   temperature=temperature,
                   max_tokens=max_tokens,
                   use_azure=use_azure,
                   top_p=top_p,
                   retry_delays=retry_delays,
                   system_message=system_message,
                   context_length=context_length,
                   reasoning_effort=reasoning_effort,)


class Google_Gemini:
    def __init__(self,
                 engine="gemini-1.5-flash",
                 temperature=0,
                 max_tokens=200,
                 top_p = 1,
                 stop = ['Observation:', '*/'],
                 retry_delays=60,
                 max_retry_iters=5,
                 context_length=4096,
                 system_message='',
                 thinking_budget=32000
                 ):
        print(f"Using engine {engine}")
        
        self.engine = engine
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.stop = stop
        self.retry_delays = retry_delays
        self.max_retry_iters = max_retry_iters
        self.context_length = context_length
        self.system_message = system_message
        self.thinking_budget = thinking_budget
        if 'flash' in self.engine:
            self.thinking_budget = min(self.thinking_budget, 24576)
        config = types.GenerationConfig(
            max_output_tokens=self.max_tokens,
            stop_sequences=self.stop,
        )
        

        
    def llm_inference(self, message):
        url = os.environ['GOOGLE_API_BASE']
        api_key = os.environ['GOOGLE_API_KEY'] 
        client = genai.Client(
            http_options=types.HttpOptions(base_url=url),
            api_key=api_key,
            )
        response = client.models.generate_content(
            model=self.engine,
            contents=message,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=self.thinking_budget)

            ),
        )
        return response.text
    
    def generate(self, system_message, prompt):
        for attempt in range(self.max_retry_iters):
            try:
                return True, self.llm_inference(prompt) # return success, completion
            except Exception as e:
                print(f"Error on attempt {attempt + 1}, Error: {e}")
                if attempt < self.max_retry_iters - 1:
                    time.sleep(self.retry_delays)
                else:
                    print("Failed to get completion after multiple attempts.")
        return False, None
    
    @classmethod
    def from_config(cls, config):
        engine = config.get("engine", "gemini-1.5-flash")
        temperature = config.get("temperature", 0)
        max_tokens = config.get("max_tokens", 4096)
        system_message = config.get("system_message", "You are a helpful assistant.")
        top_p = config.get("top_p", 1)
        stop = config.get("stop", ['Observation:', '*/'])
        retry_delays = config.get("retry_delays", 10)
        context_length = config.get("context_length", 16384)
        thinking_budget = config.get("thinking_budget", 32000)
        return cls(engine=engine,
                   temperature=temperature,
                   max_tokens=max_tokens,
                   top_p=top_p,
                   stop=stop,
                   retry_delays=retry_delays,
                   system_message=system_message,
                   context_length=context_length,
                   thinking_budget=thinking_budget)
        
class Claude_Anthropic:
    def __init__(self,
                 engine="claude-sonnet-4-20250514",
                 temperature=0,
                 max_tokens=200,
                 top_p=1,
                 top_k=40,
                 stop_sequences=None,
                 retry_delays=60,
                 max_retry_iters=5,
                 system_message='',
                 thinking_budget=10000
                 ):
        print(f"Using engine {engine}")
        
        self.engine = engine
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.top_k = top_k
        self.stop_sequences = stop_sequences or []
        self.retry_delays = retry_delays
        self.max_retry_iters = max_retry_iters
        self.system_message = system_message
        self.thinking_budget = thinking_budget
        
        # Initialize the Anthropic client
        self.client = anthropic.Anthropic(
            api_key=os.environ.get('CLAUDE_API_KEY'),
            base_url=os.environ.get('CLAUDE_API_BASE')  # Optional custom base URL
        )



    def llm_inference(self, message):
        """Perform inference using Claude API with thinking enabled"""
        # Convert message to Claude format if it's a string
        if isinstance(message, str):
            messages = [{"role": "user", "content": message}]
        else:
            # Assuming message is already in the right format
            messages = message
        
        # Make API call with thinking enabled
        response = self.client.messages.create(
            model=self.engine,
            messages=messages,
            stream=True,# Streaming is required for operations that may take longer than 10 minutes. See https://github.com/anthropics/anthropic-sdk-python#long-requests for more details
            max_tokens=self.max_tokens,
            stop_sequences=self.stop_sequences,
            thinking={
                "type": "enabled",
                "budget_tokens": self.thinking_budget
            }
        )
        
        # Process response content (both thinking and text blocks)
        full_response = ""
        for event in response:
            if event.type == "content_block_delta" and hasattr(event.delta, 'text'):
                # Print the text as it's generated
                #print(event.delta.text, end="", flush=True)
                # Also collect it in a variable
                full_response += event.delta.text
            elif event.type == "message_stop":
                # Stream has ended
                break
        
        return full_response

    def generate(self, system_message, prompt):
        """Generate a response with retry logic"""
        # Update system message if provided
        if system_message:
            original_system = self.system_message
            self.system_message = system_message
            
        for attempt in range(self.max_retry_iters):
            try:
                result = self.llm_inference(prompt)
                # Restore original system message if we changed it
                if system_message:
                    self.system_message = original_system
                return True, result  # return success, completion
            except Exception as e:
                print(f"Error on attempt {attempt + 1}, Error: {e}")
                if attempt < self.max_retry_iters - 1:
                    time.sleep(self.retry_delays)
                else:
                    print("Failed to get completion after multiple attempts.")
        
        # Restore original system message if we changed it
        if system_message:
            self.system_message = original_system
        return False, None

    @classmethod
    def from_config(cls, config):
        """Create instance from configuration dictionary"""
        engine = config.get("engine", "claude-sonnet-4-20250514")
        temperature = config.get("temperature", 0)
        max_tokens = config.get("max_tokens", 32000)
        system_message = config.get("system_message", "You are a helpful assistant.")
        top_p = config.get("top_p", 1)
        top_k = config.get("top_k", 40)
        stop_sequences = config.get("stop_sequences", [])
        retry_delays = config.get("retry_delays", 10)
        thinking_budget = config.get("thinking_budget", 30000)
        
        return cls(
            engine=engine,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            top_k=top_k,
            stop_sequences=stop_sequences,
            retry_delays=retry_delays,
            system_message=system_message,
            thinking_budget=thinking_budget
        )
class DeepseekAliyun:
    ## Not Supported Parameters：temperature、top_p、presence_penalty、frequency_penalty、logprobs、top_logprobs. Please note that to ensure compatibility with existing software, setting temperature、top_p、presence_penalty、frequency_penalty will not trigger an error but will also have no effect. Setting logprobs、top_logprobs will trigger an error.
    def __init__(self,
                 engine='deepseek-r1',
                 max_tokens = 1024,
                 stop = ['Observation:', '*'],
                 retry_delays = 60,
                 max_retry_iters=10,
                 context_length=4096,
                 system_message = ''):
        self.engine = engine
        self.max_tokens = max_tokens
        self.stop = stop
        self.retry_delays = retry_delays
        self.max_retry_iters = max_retry_iters
        self.context_length = context_length
        self.system_message = system_message

        self.client = OpenAI(
            api_key = os.environ.get('DEEPSEEK_API_KEY'),
            base_url = os.environ.get('DEEPSEEK_API_BASE')
        )
              
        
    def llm_inference(self, user_prompt):
        completion = self.client.chat.completions.create(
            model="deepseek-reasoner",  # 此处以 deepseek-r1-distill-qwen-7b 为例，可按需更换模型名称。
            timeout=120000,
            stream=False,
            messages=user_prompt
        )
        reasoning_content = completion.choices[0].message.reasoning_content
        answer_content = completion.choices[0].message.content
        return '<think>\n' + reasoning_content + '</think>' + answer_content
    
    def generate(self, system_message, prompt):
        prompt=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ]

        for attempt in range(self.max_retry_iters):
            try:
                return True, self.llm_inference(prompt)
            except Exception as e:
                print(f"Error on attempt {attempt + 1}, Error: {e}")
                if attempt < self.max_retry_iters - 1:
                    time.sleep(self.retry_delays)
                else:
                    print("Failed to get completion after multiple attempts.")
        return False, ''
    
    @classmethod
    def from_config(cls, config):
        engine = config.get("engine", "deepseek-r1")
        max_tokens = config.get("max_tokens", 4096)
        system_message = config.get("system_message", "You are a helpful assistant.")
        stop = config.get("stop", ['Observation:', '*/'])
        retry_delays = config.get("retry_delays", 10)
        context_length = config.get("context_length", 16384)
        return cls(engine=engine,
                   max_tokens=max_tokens,
                   stop=stop,
                   retry_delays=retry_delays,
                   system_message=system_message,
                   context_length=context_length)

class Model:
    def __init__(self, config):
        if 'gpt' in config['engine'] or 'o1' in config['engine'] or 'qwen' in config['engine']:
            self.llm = OPENAI_GPT.from_config(config)
        elif 'llama' in config['engine'].lower():
            if config['engine'].startswith('/'): ## Use Local Models
                if '8b' in config['engine'].lower() or '7b' in config['engine'].lower():
                    config['ngpu'] = 1
                elif '70b' in config['engine'].lower():
                    config['ngpu'] = 4
                self.llm = VLLM.from_config(config)
            else: ## Use Llama API
                raise NotImplementedError
        elif 'gemini' in config['engine'].lower():
            self.llm = Google_Gemini.from_config(config)
        elif config['engine'].lower().startswith('qw'):
            self.llm = VLLM.from_config(config)
        elif 'deepseek' in config['engine'].lower():
            self.llm = DeepseekAliyun.from_config(config)
        elif 'claude' in config['engine'].lower():
            self.llm = Claude_Anthropic.from_config(config)
        else:
            raise NotImplementedError
        
    def generate(self, system_message, prompt):
        return self.llm.generate(system_message, prompt)
    
    
if __name__ == "__main__":
    test_config = {
        "engine": "qwen3-235b-a22b-instruct-2507",
    }
    #llm = OPENAI_GPT.from_config(test_config)
    llm = Model(test_config)
    print(llm.generate('You are a helpful assistant.', 'Let $N$ be the greatest four-digit positive integer with the property that whenever one of its digits is changed to $1$, the resulting number is divisible by $7$. Let $Q$ and $R$ be the quotient and remainder, respectively, when $N$ is divided by $1000$. Find $Q+R$.'))

