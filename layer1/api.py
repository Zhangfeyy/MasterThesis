import asyncio
import pandas as pd
from tqdm.asyncio import tqdm
from dotenv import load_dotenv
from helper import AgentsLLM
from helper import agent_process
import os

load_dotenv()

PROMPT = """
You are a sentiment decision tool and please perform sentiment analysis on the following geopolitical text.
Directly output one of these three integers:
-1: Negative
 0: Neutral
 1: Positive
 
 The following text is:
 {text}

Rules:
- Strictly output the number ONLY. 
- No preamble, no explanation, no punctuation.
- If you are unsure, output 0.
"""

BATCH_SIZE = 100

OUTPUT = "../data/layer1/layer1_sentiment.csv"

if __name__ == "__main__":
    df = pd.read_csv("../data/layer1/layer1_sentence.csv")
    df["id"] = df.index

    llm = AgentsLLM()
    sem = asyncio.Semaphore(10)  # limit the concurrent

    start_idx = 0 # checkpoint
    if os.path.exists(OUTPUT):
        existing_df = pd.read_csv(OUTPUT)
        start_idx = len(existing_df)
        print(f"Found the record, starting from the {start_idx} record"+"-"*20)
    else:
        print(f"Starting processing {len(df)} records"+"-"*20)

    loop = asyncio.get_event_loop()
    for i in range(start_idx, len(df), BATCH_SIZE):
        batch_df = df.iloc[i:i+BATCH_SIZE]
        print(f"Processing the batch {i}-{i+BATCH_SIZE} records" + "-"*15)

        tasks = [
            agent_process(PROMPT,llm, idx, row["sentence"], sem=sem)
            for idx, row in batch_df.iterrows()  
        ]

        batch_results = loop.run_until_complete(tqdm.gather(*tasks))

        result_df = pd.DataFrame(batch_results)
        result_df.to_csv(OUTPUT, mode='a', index=False,
                         header=not os.path.exists(OUTPUT),
                         encoding="utf-8")

    print(f"\nALL DONE" + "-"*20)
