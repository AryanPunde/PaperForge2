# Document Scanner Application

## Overview

A Flask-based web application that provides document scanning capabilities through a browser interface. The application allows users to capture photos using their device camera or upload images from their gallery, processes them for better document readability, performs mock OCR text extraction, and converts the results to PDF format. It includes a complete scan history management system with SQLite database storage.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Web-based Interface**: Built with Flask templates using Jinja2 templating engine
- **Responsive Design**: Bootstrap 5 with dark theme for mobile-first responsive layout
- **Client-side JavaScript**: Vanilla JavaScript classes for camera management and application logic
- **Real-time Camera Access**: Uses HTML5 MediaDevices API for device camera integration
- **File Upload Support**: HTML5 file input with drag-and-drop capabilities

### Backend Architecture
- **Web Framework**: Flask application with modular structure separating routes, models, and utilities
- **Database ORM**: SQLAlchemy with declarative base for database operations
- **Image Processing Pipeline**: PIL (Pillow) for image enhancement, resizing, and format conversion
- **PDF Generation**: ReportLab library for creating multi-page PDF documents from processed images
- **Session Management**: Flask sessions for maintaining user state across requests
- **File Handling**: Secure file upload with UUID-based naming and organized directory structure

### Data Storage
- **Primary Database**: SQLite with configurable DATABASE_URL (defaults to local file)
- **File Storage**: Local filesystem with organized directories for uploads and PDFs
- **Session Storage**: Server-side Flask sessions with configurable secret key
- **Database Schema**: Single table design with scan history tracking (id, filename, timestamp, pages)

### Authentication and Authorization
- **Security Model**: Basic session-based security with CSRF protection via Flask secret key
- **File Security**: Werkzeug secure filename handling and file type validation
- **Upload Restrictions**: 16MB file size limit with allowed extensions whitelist

## External Dependencies

### Core Framework Dependencies
- **Flask**: Web application framework with SQLAlchemy integration
- **Werkzeug**: WSGI utilities including proxy fix for deployment environments
- **SQLAlchemy**: Database ORM with connection pooling and health checks

### Image Processing Libraries
- **Pillow (PIL)**: Image manipulation, enhancement, and format conversion
- **ReportLab**: PDF generation with support for image embedding and page layouts

### Frontend Libraries
- **Bootstrap 5**: CSS framework with dark theme support from Replit CDN
- **Feather Icons**: Lightweight icon library for consistent UI elements
- **HTML5 APIs**: MediaDevices for camera access, Canvas for image capture

### Development and Deployment
- **Buildozer**: Configured for Android packaging (mentioned in requirements)
- **ProxyFix**: Werkzeug middleware for proper header handling in production
- **Logging**: Python standard logging with debug level configuration