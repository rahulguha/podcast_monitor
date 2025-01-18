import os
import glob

from util import *
from transformers import BartTokenizer, BartForConditionalGeneration

def chunk_text_with_sliding_window(text, tokenizer_name="facebook/bart-large-cnn", max_tokens=1024, overlap=100):
    """
    Splits text into chunks with a sliding window to ensure token continuity.

    Parameters:
        text (str): The input text to be chunked.
        tokenizer_name (str): The name of the tokenizer to use.
        max_tokens (int): Maximum number of tokens per chunk.
        overlap (int): Number of overlapping tokens between consecutive chunks.

    Returns:
        list of str: List of text chunks.
    """
    if overlap >= max_tokens:
        raise ValueError("Overlap must be smaller than max_tokens.")

    # Load the tokenizer
    tokenizer = BartTokenizer.from_pretrained(tokenizer_name)

    # Tokenize the input text
    tokens = tokenizer.encode(text, return_tensors=None)

    # Split tokens into chunks with overlap
    chunks = []
    start = 0
    while start < len(tokens):
        end = min(start + max_tokens, len(tokens))
        chunk = tokens[start:end]
        chunks.append(tokenizer.decode(chunk, skip_special_tokens=True))
        start += max_tokens - overlap

    return chunks

def summarize_chunks(chunks, model_name="facebook/bart-large-cnn"):
    """
    Summarizes each chunk of text using a pre-trained BART model.

    Parameters:
        chunks (list of str): List of text chunks to summarize.
        model_name (str): The name of the model to use for summarization.

    Returns:
        str: The concatenated summary of all chunks.
    """
    # Load the model and tokenizer
    tokenizer = BartTokenizer.from_pretrained(model_name)
    model = BartForConditionalGeneration.from_pretrained(model_name)

    summaries = []
    for chunk in chunks:
        inputs = tokenizer(chunk, return_tensors="pt", max_length=1024, truncation=True)
        summary_ids = model.generate(inputs["input_ids"], max_length=70, min_length=20, length_penalty=2.0, num_beams=4, early_stopping=True)
        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        summaries.append(summary)

    return " ".join(summaries)


def summerize(source, destination):
    
    if not check_folder_exists(source):
        print (f"Source folder doesn't exist {source}")
        stop_program_if_condition(True)
    
    transcription_folder = source
    
    os.makedirs(destination, exist_ok=True)  # Create the folder if it doesn't exist
    destination_subfolders = get_subfolders(source)
    
    if len(destination_subfolders) > 0:
        for subfolder in destination_subfolders:
            source_subfolder_path = os.path.join(source, subfolder)
            destination_subfolder_path = os.path.join(destination, subfolder)
            os.makedirs(destination_subfolder_path, exist_ok=True)  # Create Subfolders
            source_files = glob.glob(source_subfolder_path + "/*.*") # read all files
            
            for source_file in source_files:
                file_name = "summ_" + strip_extension(strip_before_last_slash(source_file)) + ".txt"
                summery_file_name = os.path.join(destination, subfolder,  file_name)
                
                if not os.path.exists(summery_file_name):
                    with open(source_file, 'r') as file:
                        content = file.read()
                        print (f"***** start summarization for {source_file} - ({len(content)}) ")
                        chunks = chunk_text_with_sliding_window(content)
                        summ = summarize_chunks(chunks)
                        print (f"**** finish summarization for {source_file} - final size {len(summ)}")
                        create_file(summery_file_name, summ)
                        print(f"***** Summery created for {source_file} to {summery_file_name}")
                else:
                    print (f"{summery_file_name} already exists. Skipping ...")
    