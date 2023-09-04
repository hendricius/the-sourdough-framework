import openai
import os
import re
import sys

from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv('OPENAI_KEY')

lang = "french"
model = "gpt-4"
system = f"""
You are a translating assistant. 
You translate in {lang}. 
You directly translate messages your receive, without saying anything else than the translation of the messages. 
The content you take as input are LaTeX document. 
You need to only translate the text that is rendered on the output. Do not translate comments, labels, references, file paths, or anything that is syntax-related or that would break the LaTex compilation.
"""
max_chunk_length = 1000*4

def read_file(filepath):
    file = open(filepath, 'r')
    file_content = file.read()
    return file_content

def write_file(filepath, content):
    file = open(filepath, 'w')
    file.write(str(content))

def translate(content):
    chat_completion = openai.ChatCompletion.create(
        model=model, 
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": content},
        ]
    )

    translation = chat_completion.choices[0].message.content

    return translation

def translate_big(big_content):
    content_paragraphs = big_content.split('\n\n') # maybe take lines instead of paragraphs

    chunks = []
    chunk = ""

    for index, paragraph in enumerate(content_paragraphs):
        if len(chunk + paragraph) > max_chunk_length:
            if len(chunk) == 0:
                raise Exception("Paragraph length exceeded maximum chunk size")
            chunks.append(chunk)
            chunk = ""
        chunk += paragraph
        if index == len(content_paragraphs)-1:
            chunks.append(chunk)
            break;
        else:
            chunk += "\n\n"

    translated_chunks = []
    for index, chunk in enumerate(chunks):
        print(f'PENDING - Translating chunk {index+1}/{len(chunks)}')

        translated_chunk = translate(chunk)
        # translated_chunk = chunk

        print(f'OK - Done translating chunk {index+1}/{len(chunks)}')
        translated_chunks.append(translated_chunk)

    translated = "".join(translated_chunks)
    
    return translated

def list_files():
    book_root = './book'
    tex_string = read_file(os.path.join(book_root, 'book.original.tex'))

    pattern = r'\\input\{(.*?)\}'
    matches = re.findall(pattern, tex_string)

    files_to_translate = [os.path.join(book_root, match) for match in matches]
    
    return files_to_translate


def translate_one_file(input_path, output_path):
    if os.path.exists(output_path):
        print(f'SKIP - File already translated')
        return

    content = read_file(input_path)
    translated_content = translate_big(content)
    write_file(output_path, translated_content)

def translate_all_files():
    print(f'Translating book to {lang}')
    
    files_to_translate = list_files()

    #files_to_translate = [files_to_translate[1]]
    #print(files_to_translate)

    for file_to_translate in files_to_translate:
        print(f'PENDING - Translating {file_to_translate}')
        input_file = file_to_translate + '.tex'
        output_file = file_to_translate + f'.{lang}.tex'
        translate_one_file(input_file, output_file)
        print(f'OK - Done translating {file_to_translate}')

    print(f'Done translating book')

def copy_translations():
    files_to_translate = list_files()
    for file_to_translate in files_to_translate:
        filename = file_to_translate + f'.{lang}.tex'
        if not os.path.exists(filename):
            filename = file_to_translate + '.tex'
        content = read_file(filename)
        write_file(file_to_translate + '-translated.tex', content)
        
if __name__ == "__main__":
    if "--copy" in sys.argv:
        copy_translations()
    else:
        translate_all_files()
        copy_translations()