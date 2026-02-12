import re
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def folder_sort_key(folder):
    """
    Smart sort key for folders like 'Leo AD 2500 [001 - 050]'.
    Sorts alphabetically by base name, then numerically by range start.
    """
    name = folder["name"]
    
    # Extract base name before bracket
    base = name.split("[")[0].strip()
    
    # Extract starting number from bracket range
    match = re.search(r"\[\s*(\d+)", name)
    start_num = int(match.group(1)) if match else -1
    
    return (base.lower(), start_num)


def sort_folders(folders):
    """Sort folders with smart numeric range sorting."""
    return sorted(folders, key=folder_sort_key)


def create_pagination_keyboard(items, page, per_page, callback_prefix, item_callback_func, back_callback_data="main_menu"):
    """
    Creates an inline keyboard with pagination.
    
    :param items: List of items to display.
    :param page: Current page number (1-indexed).
    :param per_page: Items per page.
    :param callback_prefix: Prefix for pagination callbacks (e.g., 'folder_page_').
    :param item_callback_func: Function that takes an item and returns (text, callback_data).
    :param back_callback_data: Callback data for the 'Back' button.
    """
    total_items = len(items)
    total_pages = (total_items + per_page - 1) // per_page
    
    # Ensure page is within bounds
    if page < 1: page = 1
    if page > total_pages and total_pages > 0: page = total_pages
    
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    current_items = items[start_index:end_index]
    
    keyboard = []
    
    # Item Buttons
    for item in current_items:
        text, callback_data = item_callback_func(item)
        keyboard.append([InlineKeyboardButton(text, callback_data=callback_data)])
    
    # Pagination Buttons
    pagination_buttons = []
    if page > 1:
        pagination_buttons.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"{callback_prefix}_{page - 1}"))
    
    pagination_buttons.append(InlineKeyboardButton(f"{page}/{total_pages}", callback_data="noop"))
    
    if page < total_pages:
        pagination_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"{callback_prefix}_{page + 1}"))
    
    keyboard.append(pagination_buttons)
    
    # Back Button
    keyboard.append([InlineKeyboardButton("🏠 Back", callback_data=back_callback_data)])
    
    return InlineKeyboardMarkup(keyboard)

def get_page_items(items, page, per_page):
    """Returns the subset of items for the current page."""
    start = (page - 1) * per_page
    end = start + per_page
    return items[start:end]
