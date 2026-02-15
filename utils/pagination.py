import re
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def natural_sort_key(text):
    """
    Universal natural sort key:
    - Splits text into (string, number) chunks
    - Strings sorted A-Z (case-insensitive)
    - Numbers sorted numerically (1, 2, 10 instead of 1, 10, 2)
    Works for folder names, emails, any text.
    """
    parts = re.split(r'(\d+)', str(text).lower().strip())
    return [int(p) if p.isdigit() else p for p in parts]


def folder_sort_key(folder):
    """Natural sort key for folder dicts with 'name' field."""
    return natural_sort_key(folder.get("name", ""))


def sort_folders(folders):
    """Sort folders with natural A-Z + numeric sort."""
    return sorted(folders, key=folder_sort_key)


def sort_grants(grants, key="folder_name"):
    """Sort grants list naturally by any string field (folder_name, email, etc.)."""
    return sorted(grants, key=lambda g: natural_sort_key(g.get(key, "")))


def create_pagination_keyboard(items, page, per_page, callback_prefix, item_callback_func, back_callback_data="main_menu", refresh_callback_data=None):
    """
    Creates an inline keyboard with pagination.
    
    :param items: List of items to display.
    :param page: Current page number (1-indexed).
    :param per_page: Items per page.
    :param callback_prefix: Prefix for pagination callbacks (e.g., 'folder_page_').
    :param item_callback_func: Function that takes an item and returns (text, callback_data).
    :param back_callback_data: Callback data for the 'Back' button.
    :param refresh_callback_data: Optional callback data for a 'Refresh' button.
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
    
    # Bottom row: Refresh + Back
    bottom_row = []
    if refresh_callback_data:
        bottom_row.append(InlineKeyboardButton("🔄 Refresh", callback_data=refresh_callback_data))
    bottom_row.append(InlineKeyboardButton("🏠 Back", callback_data=back_callback_data))
    keyboard.append(bottom_row)
    
    return InlineKeyboardMarkup(keyboard)

def get_page_items(items, page, per_page):
    """Returns the subset of items for the current page."""
    start = (page - 1) * per_page
    end = start + per_page
    return items[start:end]


def create_checkbox_keyboard(folders, selected_ids, page, per_page=15, callback_prefix="mf_page", toggle_prefix="tgl_", confirm_callback="confirm_multi_folders"):
    """
    Creates a checkbox-style folder selector with ☑️/☐ toggles.
    
    :param folders: List of folder dicts with 'id' and 'name'.
    :param selected_ids: Set of currently selected folder IDs.
    :param page: Current page (1-indexed).
    :param per_page: Folders per page.
    :param callback_prefix: Prefix for pagination callbacks.
    :param toggle_prefix: Prefix for toggle callbacks.
    :param confirm_callback: Callback data for the confirm button.
    """
    total = len(folders)
    total_pages = (total + per_page - 1) // per_page
    
    if page < 1: page = 1
    if page > total_pages and total_pages > 0: page = total_pages
    
    start = (page - 1) * per_page
    end = start + per_page
    current = folders[start:end]
    
    keyboard = []
    
    for folder in current:
        is_selected = folder["id"] in selected_ids
        icon = "☑️" if is_selected else "☐"
        keyboard.append([
            InlineKeyboardButton(
                f"{icon} {folder['name']}",
                callback_data=f"{toggle_prefix}{folder['id']}"
            )
        ])
    
    # Pagination
    nav = []
    if page > 1:
        nav.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"{callback_prefix}_{page - 1}"))
    nav.append(InlineKeyboardButton(f"{page}/{total_pages}", callback_data="noop"))
    if page < total_pages:
        nav.append(InlineKeyboardButton("Next ➡️", callback_data=f"{callback_prefix}_{page + 1}"))
    keyboard.append(nav)
    
    # Confirm + Back
    count = len(selected_ids)
    keyboard.append([
        InlineKeyboardButton(
            f"✅ Confirm ({count} selected)" if count > 0 else "⚠️ Select folders first",
            callback_data=confirm_callback if count > 0 else "noop"
        )
    ])
    keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="grant_menu")])
    
    return InlineKeyboardMarkup(keyboard)
