"""
Input Validators
VJ-FILTER-BOT inspired validation utilities
"""

import re
from typing import Dict, List, Tuple

class Validators:
    """Input validation utilities (VJ pattern)"""
    
    # Email regex pattern
    EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    # Google Drive folder ID pattern
    FOLDER_ID_PATTERN = r'^[a-zA-Z0-9_-]{25,}$'
    
    @staticmethod
    def validate_email(email: str) -> Dict[str, any]:
        """
        Validate email format
        
        Args:
            email: Email address to validate
        
        Returns:
            dict: {
                'valid': bool,
                'email': str (cleaned),
                'error': str (if invalid)
            }
        """
        if not email:
            return {
                'valid': False,
                'error': "Email address is required"
            }
        
        # Clean email
        email = email.strip().lower()
        
        # Check format
        if not re.match(Validators.EMAIL_PATTERN, email):
            return {
                'valid': False,
                'error': "Invalid email format"
            }
        
        # Check length
        if len(email) > 254:
            return {
                'valid': False,
                'error': "Email address too long"
            }
        
        return {
            'valid': True,
            'email': email
        }
    
    @staticmethod
    def validate_multi_emails(emails_text: str, max_count: int = 50) -> Dict[str, any]:
        """
        Validate multiple email addresses
        
        Args:
            emails_text: Text containing emails (one per line)
            max_count: Maximum emails allowed
        
        Returns:
            dict: {
                'valid': bool,
                'emails': list (valid unique emails),
                'duplicates': list,
                'invalid': list,
                'error': str (if any)
            }
        """
        # Split by newlines
        lines = [line.strip() for line in emails_text.split('\n') if line.strip()]
        
        if not lines:
            return {
                'valid': False,
                'error': "No email addresses provided"
            }
        
        if len(lines) > max_count:
            return {
                'valid': False,
                'error': f"Maximum {max_count} emails allowed, you provided {len(lines)}"
            }
        
        valid_emails = []
        invalid_emails = []
        seen_emails = set()
        duplicates = []
        
        for email in lines:
            result = Validators.validate_email(email)
            
            if result['valid']:
                clean_email = result['email']
                
                if clean_email in seen_emails:
                    duplicates.append(clean_email)
                else:
                    valid_emails.append(clean_email)
                    seen_emails.add(clean_email)
            else:
                invalid_emails.append(email)
        
        if not valid_emails:
            return {
                'valid': False,
                'error': "No valid email addresses found",
                'invalid': invalid_emails
            }
        
        return {
            'valid': True,
            'emails': valid_emails,
            'duplicates': duplicates,
            'invalid': invalid_emails,
            'total': len(valid_emails)
        }
    
    @staticmethod
    def validate_folder_id(folder_id: str) -> Dict[str, any]:
        """
        Validate Google Drive folder ID
        
        Args:
            folder_id: Folder ID to validate
        
        Returns:
            dict: {
                'valid': bool,
                'folder_id': str (cleaned),
                'error': str (if invalid)
            }
        """
        if not folder_id:
            return {
                'valid': False,
                'error': "Folder ID is required"
            }
        
        # Clean folder ID
        folder_id = folder_id.strip()
        
        # Check format
        if not re.match(Validators.FOLDER_ID_PATTERN, folder_id):
            return {
                'valid': False,
                'error': "Invalid folder ID format"
            }
        
        return {
            'valid': True,
            'folder_id': folder_id
        }
    
    @staticmethod
    def sanitize_text(text: str) -> str:
        """
        Sanitize user input (VJ pattern)
        
        Removes potentially dangerous characters.
        
        Args:
            text: Text to sanitize
        
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&', '$', '`', '\x00']
        
        for char in dangerous_chars:
            text = text.replace(char, '')
        
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        return text.strip()
    
    @staticmethod
    def validate_duration(duration_str: str) -> Dict[str, any]:
        """
        Validate duration string
        
        Args:
            duration_str: Duration like "1h", "7d", "30d"
        
        Returns:
            dict: {
                'valid': bool,
                'hours': int (duration in hours),
                'days': int (duration in days),
                'error': str (if invalid)
            }
        """
        if not duration_str:
            return {
                'valid': False,
                'error': "Duration is required"
            }
        
        duration_str = duration_str.lower().strip()
        
        # Parse duration
        try:
            if duration_str.endswith('h'):
                hours = int(duration_str[:-1])
                return {
                    'valid': True,
                    'hours': hours,
                    'days': hours / 24
                }
            elif duration_str.endswith('d'):
                days = int(duration_str[:-1])
                return {
                    'valid': True,
                    'hours': days * 24,
                    'days': days
                }
            else:
                return {
                    'valid': False,
                    'error': "Duration must end with 'h' (hours) or 'd' (days)"
                }
        except ValueError:
            return {
                'valid': False,
                'error': "Invalid duration value"
            }
    
    @staticmethod
    def validate_role(role: str) -> Dict[str, any]:
        """
        Validate access role
        
        Args:
            role: Role string (reader/writer/viewer/editor)
        
        Returns:
            dict: {
                'valid': bool,
                'role': str (standardized),
                'error': str (if invalid)
            }
        """
        if not role:
            return {
                'valid': False,
                'error': "Role is required"
            }
        
        role = role.lower().strip()
        
        # Map to standard roles
        role_map = {
            'reader': 'reader',
            'viewer': 'reader',
            'read': 'reader',
            'writer': 'writer',
            'editor': 'writer',
            'edit': 'writer'
        }
        
        if role not in role_map:
            return {
                'valid': False,
                'error': "Invalid role. Use 'reader' or 'writer'"
            }
        
        return {
            'valid': True,
            'role': role_map[role]
        }
    
    @staticmethod
    def validate_page_size(page_size: any) -> Dict[str, any]:
        """
        Validate pagination page size
        
        Args:
            page_size: Page size value
        
        Returns:
            dict: {
                'valid': bool,
                'page_size': int,
                'error': str (if invalid)
            }
        """
        from config import Config
        
        try:
            page_size = int(page_size)
        except (ValueError, TypeError):
            return {
                'valid': False,
                'error': "Page size must be a number"
            }
        
        if page_size < Config.MIN_PAGE_SIZE:
            return {
                'valid': False,
                'error': f"Minimum page size is {Config.MIN_PAGE_SIZE}"
            }
        
        if page_size > Config.MAX_PAGE_SIZE:
            return {
                'valid': False,
                'error': f"Maximum page size is {Config.MAX_PAGE_SIZE}"
            }
        
        return {
            'valid': True,
            'page_size': page_size
        }
