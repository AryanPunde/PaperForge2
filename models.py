from app import db
from datetime import datetime

class ScanHistory(db.Model):
    """Model for storing scan history records"""
    __tablename__ = 'history'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    filename = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.String(50), nullable=False)
    pages = db.Column(db.Integer, nullable=False, default=1)
    
    def __init__(self, filename, pages=1):
        self.filename = filename
        self.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.pages = pages
    
    def to_dict(self):
        """Convert model instance to dictionary"""
        return {
            'id': self.id,
            'filename': self.filename,
            'timestamp': self.timestamp,
            'pages': self.pages
        }
