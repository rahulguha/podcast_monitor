from typing import List, Optional
import re

class CharacterTextSplitter:
    def __init__(self, chunk_size=1000, chunk_overlap=200, separators=None):
        """
        Initialize the text splitter.

        :param chunk_size: The maximum size of each chunk.
        :param chunk_overlap: The number of overlapping characters between chunks.
        :param separators: List of preferred separators to split the text. Defaults to ["\n\n", "\n", " "].
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", " "]

    def _split_text(self, text, separator):
        """
        Split text using the specified separator.

        :param text: The text to split.
        :param separator: The separator to use for splitting.
        :return: A list of chunks.
        """
        if not separator:
            return list(text)  # Split into individual characters if no separator is provided
        return text.split(separator)

    def _merge_chunks(self, chunks, separator):
        """
        Merge chunks back into a larger text with a separator.

        :param chunks: List of smaller text pieces.
        :param separator: The separator to use for merging.
        :return: A string with chunks merged.
        """
        return separator.join(chunks)

    def split(self, text):
        """
        Split the input text into chunks.

        :param text: The input text to split.
        :return: List of text chunks.
        """
        final_chunks = []
        for separator in self.separators:
            if separator in text:
                break
        else:
            separator = ""

        splits = self._split_text(text, separator)

        current_chunk = []
        current_length = 0
        for split in splits:
            split_length = len(split)
            if current_length + split_length > self.chunk_size:
                if current_chunk:
                    final_chunks.append(self._merge_chunks(current_chunk, separator))
                current_chunk = [split]
                current_length = split_length
            else:
                current_chunk.append(split)
                current_length += split_length

            # Handle overlaps
            if final_chunks and self.chunk_overlap:
                overlap = self._merge_chunks(final_chunks[-1][-self.chunk_overlap:], separator)
                current_chunk.insert(0, overlap)

        if current_chunk:
            final_chunks.append(self._merge_chunks(current_chunk, separator))
        
        return final_chunks