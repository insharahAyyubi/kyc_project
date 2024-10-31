import pytesseract
from PIL import Image
import re
import cv2
import numpy as np

def preprocess_image(image_path):
    """Preprocess the image for basic grayscale and binarization, optimized for Tesseract OCR."""
    pil_image = Image.open(image_path)
    
    # Resize for higher DPI to improve OCR accuracy
    pil_image = pil_image.resize((pil_image.width * 2, pil_image.height * 2), Image.Resampling.LANCZOS)
    
    # Convert to grayscale
    gray_image = pil_image.convert("L")
    
    # Convert to OpenCV format
    image = np.array(gray_image)
    
    # Apply simple binary thresholding to enhance text visibility
    _, binary_image = cv2.threshold(image, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Save the preprocessed image
    preprocessed_image_path = "./uploads/preprocessed_image.jpg"
    cv2.imwrite(preprocessed_image_path, binary_image)
    
    return preprocessed_image_path

def correct_date_format(date_text):
    """Ensures the date format is dd/mm/yyyy."""
    # Remove any non-digit characters and reformat as dd/mm/yyyy
    digits_only = re.sub(r"[^\d]", "", date_text)  # Remove all non-digit characters

    # Check if the result has exactly 8 digits, e.g., '05031971'
    if len(digits_only) == 8:
        # Reformat to 'dd/mm/yyyy'
        date_text = f"{digits_only[:2]}/{digits_only[2:4]}/{digits_only[4:]}"
    else:
        return digits_only  # Return this if the date doesn't match the expected pattern
    
    # Final check to confirm the date is in the correct format
    match = re.match(r"(\d{2})/(\d{2})/(\d{4})", date_text)
    return date_text if match else "Invalid date format"

def extract_aadhaar_details(image_path):
    """Function to perform OCR on the Aadhaar image and extract details."""
    preprocessed_image_path = preprocess_image(image_path)
     
    text = pytesseract.image_to_string(preprocessed_image_path, lang='eng+hin', timeout=4)
    print("OCR Text Output:\n", text)  # Debugging line to inspect OCR text

    # Split the text by lines to process line-by-line
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # Initialize variables
    name = "Not found"
    dob = "Not found"
    
    # Iterate through lines to find DOB and extract the preceding line as the name
    for i, line in enumerate(lines):
        # Search for DOB in the format 'DOB:', 'जन्म तिथि:', or 'Date of Birth:'
        dob_match = re.search(r"(?:DOB|OOB|जन्म तिथि|Year of Birth)[:\s]*([\d/]+)", line, re.IGNORECASE)
        if dob_match:
            dob = correct_date_format(dob_match.group(1))
            # Capture the previous line as the name if it exists
            if i > 0:
                name = lines[i - 1].strip()
            break

    # Define regex pattern for gender and Aadhaar number
    gender_pattern = re.search(r"(Female|Male|महिला|पुरुष)", text, re.IGNORECASE)
    aadhaar_number_pattern = re.search(r"\b\d{4}\s\d{4}\s\d{4}\b", text)

    # Extract other details
    gender = gender_pattern.group(1).strip() if gender_pattern else "Not found"
    # Map gender to English if in Hindi
    gender = "Female" if gender in ["महिला", "Female"] else "Male" if gender in ["पुरुष", "Male"] else gender
    aadhaar_number = aadhaar_number_pattern.group(0).replace(" ", "") if aadhaar_number_pattern else "Not found"

    extracted_details = {
        "Name": name,
        "DOB": dob,
        "Gender": gender,
        "Aadhaar Number": aadhaar_number
    }
    
    return extracted_details


