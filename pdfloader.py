import re
from io import StringIO
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage
from pdfminer.high_level import extract_text


from pathlib import Path

def pdf2txt_page_split(pdf_path: Path) -> list[str]:

    # Create a resource manager
    rsrcmgr = PDFResourceManager()
    # Create an object to store the text
    retstr = StringIO()
    # Create a text converter
    codec = "utf-8"
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    # Create a PDF interpreter
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    # Open the PDF file
    fp = open(pdf_path, "rb")
    # Create a list to store the text of each page
    text_list = []
    # Extract text from each page
    for page in PDFPage.get_pages(fp):
        interpreter.process_page(page)
        # Get the text
        text = retstr.getvalue()
        # Clean the text(delete \n, \u, \\...)
        cleaned_text = re.sub(r'[\u2002\u3000\u200c\n\x0c\ufeff\\]', '', text)
        # Add the text to the list
        text_list.append(cleaned_text)
        # Clear the text
        retstr.truncate(0)
        retstr.seek(0)
    # Close the file
    fp.close()
    # Close the device
    device.close()
    # Return the text list
    return text_list


def pdf2txt_all(pdf_path: Path) -> str:
    text = extract_text(pdf_path)
    print(text)



if __name__ == "__main__":
    pdf_path = Path("/Users/nagashimadaichi/Downloads/法定健診_demo (3).pdf")
    #text_list = pdf2txt_all(pdf_path)
    #print(f"pages: {len(text_list)}")
    text_list = pdf2txt_page_split(pdf_path)
    print(text_list)