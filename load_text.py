
from fileloader import *
from text_splitter import *




def get_text(data_source):
    loader = FileLoader()
    files = loader.load_directory(data_source, file_extensions=['.txt'])
    docs = []
    for f in files:
        text = loader.load_file( data_source + "/" + f)
        splitter = CharacterTextSplitter(chunk_size=200, chunk_overlap=20)
        chunks = splitter.split(text)
        docs.append(chunks)
    return docs

