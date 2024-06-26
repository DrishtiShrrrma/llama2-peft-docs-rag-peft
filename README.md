 
![image](https://github.com/DrishtiShrrrma/llama2-peft-docs-rag-peft/assets/129742046/c82c9437-cccb-49d6-8455-7d693e97ae6e)


pip install pandas pyarrow




import scrapy
from bs4 import BeautifulSoup
import hashlib
import os

class HuggingFaceDocsSpider(scrapy.Spider):
    name = 'huggingface_docs'
    allowed_domains = ['huggingface.co']
    start_urls = [
        'https://huggingface.co/docs/peft',
        'https://huggingface.co/docs/trl',
        'https://huggingface.co/docs/evaluate',
        'https://huggingface.co/docs/optimum',
        'https://huggingface.co/docs/accelerate',
        'https://huggingface.co/docs/transformers',
        'https://huggingface.co/docs/tokenizers',
        'https://huggingface.co/docs/text-generation-inference',
        'https://huggingface.co/docs/text-embeddings-inference'
    ]

    def __init__(self, *args, **kwargs):
        super(HuggingFaceDocsSpider, self).__init__(*args, **kwargs)
        # Create the output directory if it doesn't exist
        os.makedirs('output', exist_ok=True)

    def parse(self, response):
        soup = BeautifulSoup(response.body, 'html.parser')

        # Find specific <div> elements and extract text
        target_divs = soup.find_all('div', class_='z-1 min-w-0 flex-1')
        text_content = ' '.join(div.get_text(separator=' ', strip=True) for div in target_divs)

        # Save the text content to a file in the output folder
        file_name = 'output/' + hashlib.md5(response.url.encode()).hexdigest() + '.txt'
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(text_content)

        # Follow links to next pages within the /docs subdirectory
        for link in soup.find_all('a', href=True):
            next_page = response.urljoin(link['href'])
            if 'https://huggingface.co/docs' in next_page:
                yield scrapy.Request(next_page, callback=self.parse)





import os
import argparse
import pandas as pd

def chunk_text(text, chunk_length, chunk_overlap):
    if chunk_length <= chunk_overlap:
        raise ValueError("Chunk length must be greater than the chunk overlap.")

    return [text[i:i + chunk_length] for i in range(0, len(text), chunk_length - chunk_overlap)]

def process_folder(folder_path, chunk_length, chunk_overlap):
    chunks_data = []
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
                chunks = chunk_text(text, chunk_length, chunk_overlap)
                for i, chunk in enumerate(chunks):
                    chunk_id = f"{filename}_chunk_{i+1}"
                    chunks_data.append({'chunk_id': chunk_id, 'chunk_content': chunk, 'filename': filename})

    return pd.DataFrame(chunks_data)

def main():
    parser = argparse.ArgumentParser(description="Chunk files in a folder and save the output to a Parquet file.")
    parser.add_argument("chunk_length", type=int, help="Length of each chunk")
    parser.add_argument("chunk_overlap", type=int, help="Overlap between consecutive chunks")
    parser.add_argument("folder_path", type=str, help="Path to the folder containing files to be chunked")
    parser.add_argument("output_path", type=str, help="Path to save the output Parquet file")

    args = parser.parse_args()

    df = process_folder(args.folder_path, args.chunk_length, args.chunk_overlap)
    df.to_parquet(args.output_path)

if __name__ == "__main__":
    main()

Save this script in a file, for example, chunk_to_parquet.py.
Run the script from the command line by providing the necessary arguments. For instance:

!python chunk_to_parquet.py 100 20 /path/to/your/folder /path/to/output.parquet

