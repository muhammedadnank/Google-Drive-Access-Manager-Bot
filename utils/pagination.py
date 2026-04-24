import re
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ButtonStyle


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


def create_pagination_keyboard(
    items,
    page,
    per_page,
    callback_prefix,
    item_callback_func,
    back_callback_data="main_menu",
    refresh_callback_data=None,
    item_style=ButtonStyle.PRIMARY,        # ← folder/item buttons color
    nav_style=ButtonStyle.PRIMARY,         # ← Prev / Next color
    refresh_style=ButtonStyle.PRIMARY,     # ← Refresh button color
    back_style=ButtonStyle.PRIMARY,        # ← Back button color
):
    """
    Creates an inline keyboard with pagination.

    :param items:               List of items to display.
    :param page:                Current page number (1-indexed).
    :param per_page:            Items per page.
    :param callback_prefix:     Prefix for pagination callbacks.
    :param item_callback_func:  Function(item) → (label, callback_data).
    :param back_callback_data:  Callback data for the Back button.
    :param refresh_callback_data: Optional callback data for a Refresh button.
    :param item_style:          ButtonStyle for item rows (default PRIMARY).
    :param nav_style:           ButtonStyle for Prev/Next buttons.
    :param refresh_style:       ButtonStyle for Refresh button.
    :param back_style:          ButtonStyle for Back button.
    """
    total_items = len(items)
    total_pages = max(1, (total_items + per_page - 1) // per_page)

    # Clamp page within bounds
    page = max(1, min(page, total_pages))

    start_index   = (page - 1) * per_page
    current_items = items[start_index:start_index + per_page]

    keyboard = []

    # ── Item buttons ──────────────────────────────────────────
    for item in current_items:
        text, callback_data = item_callback_func(item)
        keyboard.append([
            InlineKeyboardButton(text, callback_data=callback_data, style=item_style)
        ])

    # ── Pagination row ────────────────────────────────────────
    nav_row = []
    if page > 1:
        nav_row.append(InlineKeyboardButton(
            "⬅️ Prev",
            callback_data=f"{callback_prefix}_{page - 1}",
            style=nav_style
        ))
    nav_row.append(InlineKeyboardButton(
        f"{page}/{total_pages}",
        callback_data="noop",
        style=ButtonStyle.DANGER
    ))
    if page < total_pages:
        nav_row.append(InlineKeyboardButton(
            "Next ➡️",
            callback_data=f"{callback_prefix}_{page + 1}",
            style=nav_style
        ))
    keyboard.append(nav_row)

    # ── Bottom row: Refresh + Back ────────────────────────────
    bottom_row = []
    if refresh_callback_data:
        bottom_row.append(InlineKeyboardButton(
            "🔄 Refresh",
            callback_data=refresh_callback_data,
            style=refresh_style
        ))
    bottom_row.append(InlineKeyboardButton(
        "🏠 Back",
        callback_data=back_callback_data,
        style=back_style
    ))
    keyboard.append(bottom_row)

    return InlineKeyboardMarkup(keyboard)


def get_page_items(items, page, per_page):
    """Returns the subset of items for the current page."""
    start = (page - 1) * per_page
    return items[start:start + per_page]


def create_checkbox_keyboard(
    folders,
    selected_ids,
    page,
    per_page=15,
    callback_prefix="mf_page",
    toggle_prefix="tgl_",
    confirm_callback="confirm_multi_folders",
    selected_style=ButtonStyle.SUCCESS,    # ☑️ selected folder color
    unselected_style=ButtonStyle.PRIMARY,  # ☐ unselected folder color
    nav_style=ButtonStyle.PRIMARY,         # Prev / Next color
    confirm_style=ButtonStyle.SUCCESS,     # Confirm button color
    back_style=ButtonStyle.PRIMARY,        # Back button color
):
    """
    Creates a checkbox-style folder selector with ☑️/☐ toggles.

    :param folders:           List of folder dicts with 'id' and 'name'.
    :param selected_ids:      Set of currently selected folder IDs.
    :param page:              Current page (1-indexed).
    :param per_page:          Folders per page.
    :param callback_prefix:   Prefix for pagination callbacks.
    :param toggle_prefix:     Prefix for toggle callbacks.
    :param confirm_callback:  Callback data for the Confirm button.
    :param selected_style:    ButtonStyle for checked folders.
    :param unselected_style:  ButtonStyle for unchecked folders.
    :param nav_style:         ButtonStyle for Prev/Next buttons.
    :param confirm_style:     ButtonStyle for the Confirm button.
    :param back_style:        ButtonStyle for the Back button.
    """
    total       = len(folders)
    total_pages = max(1, (total + per_page - 1) // per_page)

    page = max(1, min(page, total_pages))

    start   = (page - 1) * per_page
    current = folders[start:start + per_page]

    keyboard = []

    # ── Folder toggle buttons ─────────────────────────────────
    for folder in current:
        is_selected = folder["id"] in selected_ids
        icon  = "☑️" if is_selected else "☐"
        style = selected_style if is_selected else unselected_style
        keyboard.append([
            InlineKeyboardButton(
                f"{icon} {folder['name']}",
                callback_data=f"{toggle_prefix}{folder['id']}",
                style=style
            )
        ])

    # ── Pagination row ────────────────────────────────────────
    nav = []
    if page > 1:
        nav.append(InlineKeyboardButton(
            "⬅️ Prev",
            callback_data=f"{callback_prefix}_{page - 1}",
            style=nav_style
        ))
    nav.append(InlineKeyboardButton(f"{page}/{total_pages}", callback_data="noop", style=ButtonStyle.DANGER))
    if page < total_pages:
        nav.append(InlineKeyboardButton(
            "Next ➡️",
            callback_data=f"{callback_prefix}_{page + 1}",
            style=nav_style
        ))
    keyboard.append(nav)

    # ── Confirm + Shortcuts + Back ────────────────────────────
    count = len(selected_ids)
    keyboard.append([
        InlineKeyboardButton(
            f"✅ Confirm ({count} selected)" if count > 0 else "⚠️ Select folders first",
            callback_data=confirm_callback if count > 0 else "noop",
            style=confirm_style if count > 0 else ButtonStyle.PRIMARY
        )
    ])
    keyboard.append([
        InlineKeyboardButton("📌 Favorites",      callback_data="favorites_menu",       style=ButtonStyle.SUCCESS),
        InlineKeyboardButton("🔍 Search",          callback_data="folder_search_start",  style=ButtonStyle.PRIMARY),
        InlineKeyboardButton("🔄 Refresh",         callback_data="mf_refresh",           style=ButtonStyle.PRIMARY),
    ])
    keyboard.append([
        InlineKeyboardButton("⬅️ Back", callback_data="grant_menu", style=back_style)
    ])

    return InlineKeyboardMarkup(keyboard)
