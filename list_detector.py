"""
List Detection Module for BabelDOC
Fixes Issue #5: Bullet Points and Numbered Lists Converted to Paragraphs
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List as TypingList

class ListType(Enum):
    """Types of lists."""
    NONE = "none"
    BULLET = "bullet"
    NUMBERED = "numbered"
    LETTERED = "lettered"
    ROMAN = "roman"

@dataclass
class ListItemInfo:
    """Information about a list item."""
    item_type: ListType
    marker: str  # Original marker like "•", "1.", "a."
    content: str  # Text without marker
    level: int = 0  # Indentation level
    index: int = 0  # For numbered lists: 1, 2, 3...
    is_continuation: bool = False  # If this is wrapped text

class ListDetector:
    """Detects and processes list items in text."""
    
    # Regex patterns for list detection
    PATTERNS = {
        ListType.BULLET: re.compile(r'^[\s]*?([•\-*●○■▪▫‣⁃⁌⁍⦾⦿\+])\s+'),
        ListType.NUMBERED: re.compile(r'^[\s]*?(\d+)[\.\)]\s+'),
        ListType.LETTERED: re.compile(r'^[\s]*?([a-zA-Z])[\.\)]\s+'),
        ListType.ROMAN: re.compile(r'^[\s]*?(?=[MDCLXVI])(M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3}))[\.\)]\s+'),
    }
    
    # Common bullet characters
    BULLET_CHARS = {'•', '●', '○', '■', '▪', '▫', '‣', '⁃', '⁌', '⁍', '⦾', '⦿', '-', '*', '+'}
    
    @classmethod
    def detect_list_item(cls, text: str, x_coord: float = 0) -> Optional[ListItemInfo]:
        """
        Detect if text is a list item.
        
        Args:
            text: Text to analyze
            x_coord: X-coordinate for indentation level calculation
            
        Returns:
            ListItemInfo if list item detected, None otherwise
        """
        if not text or not text.strip():
            return None
        
        # Calculate indentation level based on x-coordinate
        # Assuming 40 pixels per indentation level
        level = int(x_coord // 40) if x_coord else 0
        
        # Try each pattern
        for list_type, pattern in cls.PATTERNS.items():
            match = pattern.match(text)
            if match:
                marker = match.group(0).strip()
                content = text[match.end():].strip()
                
                # Determine index for numbered lists
                index = 0
                if list_type == ListType.NUMBERED:
                    index = int(match.group(1))
                elif list_type == ListType.LETTERED:
                    index = ord(match.group(1).lower()) - ord('a') + 1
                elif list_type == ListType.ROMAN:
                    index = cls._roman_to_int(match.group(1).upper())
                
                return ListItemInfo(
                    item_type=list_type,
                    marker=marker,
                    content=content,
                    level=level,
                    index=index
                )
        
        # Check for bullet characters anywhere
        first_non_space = text.lstrip()[:10]
        for bullet in cls.BULLET_CHARS:
            if bullet in first_non_space:
                bullet_pos = text.find(bullet)
                if bullet_pos >= 0:
                    marker = text[:bullet_pos + len(bullet)]
                    content = text[bullet_pos + len(bullet):].strip()
                    return ListItemInfo(
                        item_type=ListType.BULLET,
                        marker=marker,
                        content=content,
                        level=level,
                        index=0
                    )
        
        return None
    
    @staticmethod
    def _roman_to_int(roman: str) -> int:
        """Convert Roman numeral to integer."""
        roman_numerals = {
            'I': 1, 'V': 5, 'X': 10, 'L': 50,
            'C': 100, 'D': 500, 'M': 1000
        }
        result = 0
        prev_value = 0
        
        for char in reversed(roman.upper()):
            value = roman_numerals.get(char, 0)
            if value < prev_value:
                result -= value
            else:
                result += value
            prev_value = value
        
        return result
    
    @staticmethod
    def _int_to_roman(num: int) -> str:
        """Convert integer to Roman numeral."""
        val = [
            1000, 900, 500, 400,
            100, 90, 50, 40,
            10, 9, 5, 4,
            1
        ]
        syb = [
            "M", "CM", "D", "CD",
            "C", "XC", "L", "XL",
            "X", "IX", "V", "IV",
            "I"
        ]
        roman_num = ''
        i = 0
        while num > 0:
            for _ in range(num // val[i]):
                roman_num += syb[i]
                num -= val[i]
            i += 1
        return roman_num
    
    @classmethod
    def reconstruct_list_text(cls, list_info: ListItemInfo, translated_content: str, 
                            target_lang: str = "en") -> str:
        """
        Reconstruct list item with proper formatting.
        
        Args:
            list_info: Original list metadata
            translated_content: Translated text content
            target_lang: Target language code
        
        Returns:
            Formatted list item text
        """
        # Add indentation
        indent = '    ' * list_info.level
        
        if list_info.item_type == ListType.BULLET:
            return f"{indent}• {translated_content}"
        
        elif list_info.item_type == ListType.NUMBERED:
            index = list_info.index
            return f"{indent}{index}. {translated_content}"
        
        elif list_info.item_type == ListType.LETTERED:
            index = list_info.index
            letter = chr(ord('a') + index - 1)
            return f"{indent}{letter}. {translated_content}"
        
        elif list_info.item_type == ListType.ROMAN:
            index = list_info.index
            roman = cls._int_to_roman(index)
            return f"{indent}{roman}. {translated_content}"
        
        return f"{indent}{translated_content}"

@dataclass
class ListGroup:
    """Represents a group of consecutive list items."""
    items: TypingList[ListItemInfo]
    list_type: ListType
    level: int
    
    def add_item(self, item: ListItemInfo) -> None:
        """Add an item to the list group."""
        self.items.append(item)
    
    def is_continuation(self, item: ListItemInfo) -> bool:
        """Check if item continues this list group."""
        return (item.item_type == self.list_type and 
                item.level == self.level)
