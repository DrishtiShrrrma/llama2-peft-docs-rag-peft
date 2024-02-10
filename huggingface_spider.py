import scrapy
import hashlib
import os
from bs4 import BeautifulSoup

class HuggingFaceSpider(scrapy.Spider):
    name = 'huggingface'
    allowed_domains = ['huggingface.co']
    start_urls = [
        'https://huggingface.co/docs/api-inference',
        'https://huggingface.co/docs/inference-endpoints',
        'https://huggingface.co/docs/peft',
        'https://huggingface.co/docs/accelerate',
        'https://huggingface.co/docs/optimum',
        'https://huggingface.co/docs/optimum-neuron',  # Listed twice in your request, included once
        'https://huggingface.co/docs/evaluate',
        'https://huggingface.co/docs/trl',
        'https://huggingface.co/docs/sagemaker',
    ]

    def __init__(self, *args, **kwargs):
        super(HuggingFaceSpider, self).__init__(*args, **kwargs)
        self.output_folder = 'output'
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

    def is_valid_sublink(self, url):
        return url.startswith('https://huggingface.co/docs')

    def is_multimedia_content(self, response):
        content_type = response.headers.get('content-type', '').decode('utf-8').lower()
        return any(content_type.startswith(t) for t in ['image/', 'video/', 'audio/'])

    def parse(self, response):
        if self.is_multimedia_content(response):
            self.logger.info(f"Skipping multimedia content for URL: {response.url}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        text_content = ""

        # Filter only the text from <div> elements with the specified class
        div_elements = soup.select('div.z-1.min-w-0.flex-1')
        for div_element in div_elements:
            text = div_element.get_text()
            text_content += text.strip() + '\n'

        # Calculate the MD5 hash of the URL to use as the filename
        url_hash = hashlib.md5(response.url.encode('utf-8')).hexdigest()

        # Save the text content to a file in the 'output' folder
        file_path = os.path.join(self.output_folder, f"{url_hash}.txt")
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(text_content)

        # Follow all sublinks within the allowed domain and from 'https://huggingface.co/docs'
        for link in soup.find_all('a', href=True):
            sublink = response.urljoin(link['href'])
            if self.allowed_domains[0] in sublink and self.is_valid_sublink(sublink):
                yield scrapy.Request(sublink, callback=self.parse)
