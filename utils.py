import os
import random
from PIL import Image, ImageEnhance, ImageFilter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.utils import ImageReader
import logging

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_image(filepath):
    """Process image for better scanning quality"""
    try:
        # Open image
        with Image.open(filepath) as img:
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize if too large (max 2000px on longest side)
            max_size = 2000
            if max(img.size) > max_size:
                img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            # Enhance contrast and sharpness for document scanning
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.2)  # Slight contrast boost
            
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(1.1)  # Slight sharpness boost
            
            # Save processed image
            processed_path = filepath.replace('.', '_processed.')
            img.save(processed_path, 'JPEG', quality=90)
            
            return processed_path
            
    except Exception as e:
        logger.error(f"Image processing error: {str(e)}")
        return filepath  # Return original if processing fails

def mock_ocr(image_path):
    """
    Mock OCR function that simulates text extraction
    In a real application, this would use OCR services like Tesseract, AWS Textract, etc.
    """
    try:
        # Open image to get basic info
        with Image.open(image_path) as img:
            width, height = img.size
            
        # Generate mock OCR text based on image characteristics
        mock_texts = [
            "INVOICE\n\nDate: 2024-01-15\nInvoice #: INV-2024-001\n\nBill To:\nJohn Smith\n123 Main Street\nAnytown, ST 12345\n\nDescription: Professional Services\nAmount: $1,250.00\n\nThank you for your business!",
            
            "RECEIPT\n\nStore: Quick Mart\nDate: 2024-01-15 14:30\nTransaction #: 789456123\n\nItems:\n- Milk 2% 1gal    $3.99\n- Bread Whole Wheat    $2.49\n- Bananas 2lbs    $1.98\n\nSubtotal: $8.46\nTax: $0.67\nTotal: $9.13\n\nPayment: Credit Card\nThank you!",
            
            "DOCUMENT SCANNER\n\nThis appears to be a scanned document.\nThe text recognition system has detected\nmultiple lines of text content.\n\nKey Information:\n• Date detected\n• Numbers and amounts visible\n• Multiple text regions identified\n• Document structure recognized\n\nProcessing complete.",
            
            "MEETING NOTES\n\nDate: January 15, 2024\nAttendees: Team Alpha\n\nAgenda Items:\n1. Project status update\n2. Budget review\n3. Timeline adjustments\n4. Next steps\n\nAction Items:\n- Review quarterly report\n- Schedule follow-up meeting\n- Update project documentation\n\nNext meeting: January 22, 2024",
            
            "BUSINESS CARD\n\nJohn Smith\nSenior Manager\n\nABC Corporation\n456 Business Ave\nSuite 100\nBusiness City, BC 12345\n\nPhone: (555) 123-4567\nEmail: john.smith@abc-corp.com\nWebsite: www.abc-corp.com"
        ]
        
        # Select random mock text
        selected_text = random.choice(mock_texts)
        
        # Add some variation based on image size
        if width > 1500 or height > 1500:
            selected_text += "\n\n[High resolution image - enhanced text extraction]"
        elif width < 800 and height < 800:
            selected_text += "\n\n[Low resolution image - basic text extraction]"
        
        return selected_text
        
    except Exception as e:
        logger.error(f"Mock OCR error: {str(e)}")
        return "Error: Unable to extract text from this image. Please ensure the image is clear and contains readable text."

def create_pdf(image_paths, output_path):
    """Create PDF from multiple images"""
    try:
        c = canvas.Canvas(output_path, pagesize=A4)
        page_width, page_height = A4
        
        for i, image_path in enumerate(image_paths):
            if i > 0:  # Add new page for subsequent images
                c.showPage()
                
            try:
                # Open image to get dimensions
                with Image.open(image_path) as img:
                    img_width, img_height = img.size
                    
                # Calculate scaling to fit page while maintaining aspect ratio
                width_scale = page_width / img_width
                height_scale = page_height / img_height
                scale = min(width_scale, height_scale)
                
                # Calculate centered position
                scaled_width = img_width * scale
                scaled_height = img_height * scale
                x = (page_width - scaled_width) / 2
                y = (page_height - scaled_height) / 2
                
                # Draw image
                c.drawImage(image_path, x, y, scaled_width, scaled_height)
                
            except Exception as img_error:
                logger.error(f"Error processing image {image_path}: {str(img_error)}")
                # Add error page
                c.drawString(100, page_height - 100, f"Error processing image: {os.path.basename(image_path)}")
        
        c.save()
        logger.info(f"PDF created successfully: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"PDF creation error: {str(e)}")
        return False
